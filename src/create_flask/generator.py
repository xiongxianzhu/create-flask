"""项目生成核心逻辑：模板渲染、可选模块门控、覆盖保护与结果汇总。"""

from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path

from jinja2 import Environment, StrictUndefined

BUILTIN_TEMPLATES_DIR = Path(__file__).parent / "templates"

GIT_URL_PREFIXES = ("git@", "ssh://", "git://", "http://", "https://")

NAME_PATTERN = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")

# 模板文件名 -> 实际落盘文件名（处理点文件，避免点文件在打包/版本库中被忽略）
DOTFILE_MAP = {
    "gitignore": ".gitignore",
    "dockerignore": ".dockerignore",
    "python-version": ".python-version",
    "env.example": ".env.example",
}

# 仅在启用 Celery 时生成
CELERY_PATHS = {"celeryconfig.py", "app/tasks/__init__.py"}

# 仅在启用 Docker 时生成
DOCKER_PATHS = {"Dockerfile", "docker-compose.yml", "dockerignore"}


class GenerationError(Exception):
    """生成过程中的可预期错误（参数非法、目标冲突等）。"""


@dataclass
class ProjectOptions:
    name: str
    target_dir: Path
    use_redis: bool = False
    use_celery: bool = False
    use_docker: bool = False
    force: bool = False
    template_dir: Path | None = None

    @property
    def package_name(self) -> str:
        return self.name.replace("-", "_")


@dataclass
class GenerationResult:
    target_dir: Path
    created: list[Path] = field(default_factory=list)
    skipped: list[Path] = field(default_factory=list)

    @property
    def file_count(self) -> int:
        return len(self.created)


def validate_name(name: str) -> None:
    if not NAME_PATTERN.match(name):
        raise GenerationError(
            f"项目名 {name!r} 不合法：必须为小写字母开头，仅含小写字母、数字与中划线（-），"
            "不得包含下划线、空格或其他特殊字符。"
        )


def _is_git_url(spec: str) -> bool:
    return spec.startswith(GIT_URL_PREFIXES) or spec.endswith(".git")


def _with_subdir(base: Path, subdir: str | None) -> Path:
    target = base / subdir if subdir else base
    if not target.is_dir():
        raise GenerationError(f"模板目录不存在：{target}")
    return target


@contextmanager
def resolve_template(
    spec: str | None,
    ref: str | None = None,
    subdir: str | None = None,
) -> Iterator[Path]:
    """将模板来源解析为本地目录：内置（spec=None）/ 本地路径 / git 地址。

    git 来源会被浅克隆到临时目录，退出上下文时清理。
    """
    if spec is None:
        yield _with_subdir(BUILTIN_TEMPLATES_DIR, subdir)
        return

    if _is_git_url(spec):
        tmp = Path(tempfile.mkdtemp(prefix="create-flask-tpl-"))
        try:
            cmd = ["git", "clone", "--depth", "1"]
            if ref:
                cmd += ["--branch", ref]
            cmd += [spec, str(tmp / "repo")]
            try:
                subprocess.run(cmd, check=True, capture_output=True, text=True)
            except FileNotFoundError as exc:
                raise GenerationError(
                    "未找到 git 命令，请先安装 git，或改用本地模板路径。"
                ) from exc
            except subprocess.CalledProcessError as exc:
                detail = (exc.stderr or "").strip()
                raise GenerationError(f"克隆模板仓库失败：{spec}\n{detail}") from exc
            yield _with_subdir(tmp / "repo", subdir)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        return

    yield _with_subdir(Path(spec).expanduser().resolve(), subdir)


def _should_skip_source(rel: Path) -> bool:
    # 跳过 VCS 元数据（外部 git 模板克隆后会带 .git/）
    return ".git" in rel.parts


def _is_included(rel_posix: str, opts: ProjectOptions) -> bool:
    if rel_posix in CELERY_PATHS and not opts.use_celery:
        return False
    if rel_posix in DOCKER_PATHS and not opts.use_docker:
        return False
    return True


def _output_relpath(rel: Path, opts: ProjectOptions) -> Path:
    rel_posix = rel.as_posix()
    # supervisor 配置按项目名重命名
    if rel_posix == "deploy/supervisor/supervisor.conf":
        return Path("deploy/supervisor") / f"{opts.name}.conf"
    # 点文件名映射
    mapped = DOTFILE_MAP.get(rel.name)
    if mapped is not None:
        return rel.with_name(mapped)
    return rel


def _build_context(opts: ProjectOptions) -> dict[str, object]:
    return {
        "project_name": opts.name,
        "package_name": opts.package_name,
        "use_redis": opts.use_redis,
        "use_celery": opts.use_celery,
        "use_docker": opts.use_docker,
    }


def _render(text: str, context: dict[str, object]) -> str:
    env = Environment(
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
        undefined=StrictUndefined,
    )
    return env.from_string(text).render(**context)


def generate_project(opts: ProjectOptions) -> GenerationResult:
    """按选项生成项目；失败时不会在目标目录留下半成品。"""
    validate_name(opts.name)

    template_dir = opts.template_dir or BUILTIN_TEMPLATES_DIR
    if not template_dir.is_dir():
        raise GenerationError(f"模板目录不存在：{template_dir}")

    context = _build_context(opts)
    target = opts.target_dir

    # 先在临时目录完整渲染，成功后再合并到目标目录，保证原子性。
    staging_root = Path(tempfile.mkdtemp(prefix="create-flask-"))
    try:
        staging = staging_root / "project"
        staging.mkdir(parents=True)

        for src in sorted(template_dir.rglob("*")):
            if src.is_dir():
                continue
            rel = src.relative_to(template_dir)
            if _should_skip_source(rel):
                continue
            if not _is_included(rel.as_posix(), opts):
                continue
            out_rel = _output_relpath(rel, opts)
            out_path = staging / out_rel
            out_path.parent.mkdir(parents=True, exist_ok=True)
            if src.name == ".gitkeep":
                out_path.write_bytes(b"")
                continue
            try:
                text = src.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                # 非文本文件（如图片）原样复制，不做模板渲染
                shutil.copy2(src, out_path)
                continue
            rendered = _render(text, context)
            out_path.write_text(rendered, encoding="utf-8")

        result = GenerationResult(target_dir=target)
        target.mkdir(parents=True, exist_ok=True)

        for staged in sorted(staging.rglob("*")):
            if staged.is_dir():
                continue
            rel = staged.relative_to(staging)
            dest = target / rel
            if dest.exists() and not opts.force:
                result.skipped.append(rel)
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(staged, dest)
            result.created.append(rel)

        return result
    finally:
        shutil.rmtree(staging_root, ignore_errors=True)
