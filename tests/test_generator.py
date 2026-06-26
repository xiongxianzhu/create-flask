"""generator 单元测试。"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from create_flask.generator import (
    GenerationError,
    ProjectOptions,
    _is_git_url,
    generate_project,
    resolve_template,
    validate_name,
)

PLACEHOLDER_RE = re.compile(r"\{\{|\{%")


def _read_all_text(root: Path) -> dict[Path, str]:
    out: dict[Path, str] = {}
    for p in root.rglob("*"):
        if p.is_file():
            try:
                out[p.relative_to(root)] = p.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                pass
    return out


def test_validate_name_rejects_invalid() -> None:
    for bad in ["My-App", "my_app", "1app", "my app", "my.app", ""]:
        with pytest.raises(GenerationError):
            validate_name(bad)


def test_validate_name_accepts_valid() -> None:
    for ok in ["myapp", "my-app", "my-api-backend", "app2"]:
        validate_name(ok)


def test_base_generation(tmp_path: Path) -> None:
    target = tmp_path / "my-api"
    result = generate_project(ProjectOptions(name="my-api", target_dir=target))

    assert result.file_count > 0
    assert (target / "app" / "__init__.py").exists()
    assert (target / "wsgi.py").exists()
    assert (target / "pyproject.toml").exists()
    assert (target / "Makefile").exists()
    assert (target / ".env.example").exists()
    assert (target / ".python-version").exists()
    assert (target / ".gitignore").exists()
    assert (target / "deploy" / "supervisor" / "my-api.conf").exists()
    assert (target / "logs" / ".gitkeep").exists()

    # 可选模块默认不生成
    assert not (target / "celeryconfig.py").exists()
    assert not (target / "app" / "tasks").exists()
    assert not (target / "Dockerfile").exists()

    # 不残留占位符
    for rel, text in _read_all_text(target).items():
        assert not PLACEHOLDER_RE.search(text), f"占位符残留：{rel}"


def test_pyproject_name_substituted(tmp_path: Path) -> None:
    target = tmp_path / "my-api"
    generate_project(ProjectOptions(name="my-api", target_dir=target))
    content = (target / "pyproject.toml").read_text(encoding="utf-8")
    assert 'name = "my-api"' in content
    # 默认不含可选依赖，且不依赖 flask-restful
    assert "flask-restful" not in content
    assert "redis" not in content
    assert "celery" not in content


def test_no_rest_framework_deps(tmp_path: Path) -> None:
    target = tmp_path / "pureflask"
    generate_project(ProjectOptions(name="pureflask", target_dir=target))
    files = _read_all_text(target)
    joined = "\n".join(files.values())
    for forbidden in ["flask_restful", "flask-restful", "flask_smorest", "marshmallow"]:
        assert forbidden not in joined, f"不应依赖 {forbidden}"
    # 健康端点应为纯 Flask 蓝图
    health = (target / "app" / "api" / "health.py").read_text(encoding="utf-8")
    assert "Blueprint" in health


def test_redis_module(tmp_path: Path) -> None:
    target = tmp_path / "app1"
    generate_project(ProjectOptions(name="app1", target_dir=target, use_redis=True))
    ext = (target / "app" / "extensions.py").read_text(encoding="utf-8")
    assert "from redis import Redis" in ext
    assert "get_redis" in ext
    assert "FlaskRedis" not in ext
    assert "REDIS_URL" in (target / ".env.example").read_text(encoding="utf-8")
    pyproject = (target / "pyproject.toml").read_text(encoding="utf-8")
    assert "redis>=" in pyproject
    assert "flask-redis" not in pyproject
    # redis 不新增独立目录/文件
    assert not (target / "celeryconfig.py").exists()


def test_celery_module(tmp_path: Path) -> None:
    target = tmp_path / "app2"
    generate_project(
        ProjectOptions(name="app2", target_dir=target, use_redis=True, use_celery=True)
    )
    assert (target / "celeryconfig.py").exists()
    assert (target / "app" / "tasks" / "__init__.py").exists()
    assert "celery_init_app" in (target / "app" / "extensions.py").read_text(encoding="utf-8")
    assert "celery_app" in (target / "wsgi.py").read_text(encoding="utf-8")
    pyproject = (target / "pyproject.toml").read_text(encoding="utf-8")
    assert "celery[redis]" in pyproject


def test_docker_module(tmp_path: Path) -> None:
    target = tmp_path / "app3"
    generate_project(ProjectOptions(name="app3", target_dir=target, use_docker=True))
    assert (target / "Dockerfile").exists()
    assert (target / "docker-compose.yml").exists()
    assert (target / ".dockerignore").exists()


def test_docker_compose_includes_services_when_celery(tmp_path: Path) -> None:
    target = tmp_path / "app4"
    generate_project(
        ProjectOptions(
            name="app4",
            target_dir=target,
            use_redis=True,
            use_celery=True,
            use_docker=True,
        )
    )
    compose = (target / "docker-compose.yml").read_text(encoding="utf-8")
    assert "redis:" in compose
    assert "worker:" in compose


def test_is_git_url() -> None:
    for url in [
        "https://github.com/u/repo",
        "http://example.com/x",
        "git@github.com:u/repo.git",
        "ssh://git@host/u/repo",
        "git://host/u/repo",
        "./local.git",
    ]:
        assert _is_git_url(url)
    for path in ["./my-template", "/abs/path", "templates", "~/t"]:
        assert not _is_git_url(path)


def test_resolve_builtin_template() -> None:
    with resolve_template(None) as tdir:
        assert (tdir / "wsgi.py").exists()


def test_resolve_local_template_missing() -> None:
    with pytest.raises(GenerationError):
        with resolve_template("/no/such/template/dir"):
            pass


def test_custom_local_template(tmp_path: Path) -> None:
    tpl = tmp_path / "tpl"
    (tpl / "app").mkdir(parents=True)
    (tpl / "README.md").write_text(
        "# {{ project_name }}\npkg={{ package_name }}\n", encoding="utf-8"
    )
    (tpl / "app" / "main.py").write_text(
        "NAME = '{{ project_name }}'\n{% if use_redis %}REDIS = True\n{% endif %}",
        encoding="utf-8",
    )
    (tpl / "Dockerfile").write_text("FROM python:3.13\n", encoding="utf-8")

    target = tmp_path / "out"
    with resolve_template(str(tpl)) as tdir:
        result = generate_project(
            ProjectOptions(name="cool-app", target_dir=target, template_dir=tdir)
        )

    assert result.file_count > 0
    readme = (target / "README.md").read_text(encoding="utf-8")
    assert "# cool-app" in readme
    assert "pkg=cool_app" in readme
    assert not (target / "Dockerfile").exists()
    assert "REDIS" not in (target / "app" / "main.py").read_text(encoding="utf-8")


def test_path_placeholder_in_filename(tmp_path: Path) -> None:
    tpl = tmp_path / "tpl"
    conf_dir = tpl / "deploy" / "supervisor"
    conf_dir.mkdir(parents=True)
    conf_path = conf_dir / "{{ project_name }}.conf"
    conf_path.write_text("[program:{{ project_name }}]\n", encoding="utf-8")

    target = tmp_path / "out"
    generate_project(ProjectOptions(name="my-api", target_dir=target, template_dir=tpl))

    assert (target / "deploy" / "supervisor" / "my-api.conf").exists()
    content = (target / "deploy" / "supervisor" / "my-api.conf").read_text(encoding="utf-8")
    assert "[program:my-api]" in content


def test_custom_local_template_skips_git_dir(tmp_path: Path) -> None:
    tpl = tmp_path / "tpl"
    (tpl / ".git").mkdir(parents=True)
    (tpl / ".git" / "config").write_text("[core]\n", encoding="utf-8")
    (tpl / "file.txt").write_text("{{ project_name }}\n", encoding="utf-8")

    target = tmp_path / "out"
    generate_project(ProjectOptions(name="x", target_dir=target, template_dir=tpl))
    assert (target / "file.txt").exists()
    assert not (target / ".git").exists()


def test_overwrite_protection(tmp_path: Path) -> None:
    target = tmp_path / "app5"
    generate_project(ProjectOptions(name="app5", target_dir=target))
    marker = target / "wsgi.py"
    marker.write_text("# user edit\n", encoding="utf-8")

    # 不加 force：跳过已存在文件，不覆盖
    result = generate_project(ProjectOptions(name="app5", target_dir=target))
    assert any(p.name == "wsgi.py" for p in result.skipped)
    assert marker.read_text(encoding="utf-8") == "# user edit\n"

    # 加 force：覆盖
    result2 = generate_project(ProjectOptions(name="app5", target_dir=target, force=True))
    assert any(p.name == "wsgi.py" for p in result2.created)
    assert "create_app" in marker.read_text(encoding="utf-8")
