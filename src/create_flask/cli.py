"""create-flask 命令行入口。"""

from __future__ import annotations

import sys
from pathlib import Path

import typer

from create_flask import __version__
from create_flask.generator import (
    GenerationError,
    GenerationResult,
    ProjectOptions,
    generate_project,
    resolve_template,
    validate_name,
)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"create-flask {__version__}")
        raise typer.Exit()


def main(
    name: str | None = typer.Argument(None, help="项目名（小写，可用中划线分隔）。"),
    path: Path | None = typer.Option(
        None, "--path", help="目标目录，默认在当前目录下创建与项目名同名文件夹。"
    ),
    redis: bool | None = typer.Option(
        None, "--redis/--no-redis", help="集成 Redis 客户端（可选模块）。"
    ),
    celery: bool = typer.Option(False, "--celery", help="集成 Celery（强制依赖 Redis）。"),
    docker: bool = typer.Option(False, "--docker", help="生成 Docker 容器化文件（可选模块）。"),
    force: bool = typer.Option(False, "--force", help="覆盖目标目录下已存在的文件。"),
    yes: bool = typer.Option(False, "--yes", "-y", help="跳过交互，使用默认值。"),
    template: str | None = typer.Option(
        None,
        "--template",
        "-t",
        help="模板来源：缺省用内置模板；可传本地目录路径或 git 地址。",
    ),
    template_ref: str | None = typer.Option(
        None, "--template-ref", help="git 模板的分支或标签（仅 git 来源）。"
    ),
    template_subdir: str | None = typer.Option(
        None, "--template-subdir", help="模板根所在的子目录。"
    ),
    version: bool | None = typer.Option(
        None,
        "--version",
        callback=_version_callback,
        is_eager=True,
        help="输出版本并退出。",
    ),
) -> None:
    """生成一个新的 Flask 项目骨架：``create-flask <name>``。"""
    interactive = sys.stdin.isatty() and not yes

    # 1) 项目名
    if name is None:
        if not interactive:
            typer.secho("错误：缺少项目名，且当前为非交互环境。", fg=typer.colors.RED, err=True)
            raise typer.Exit(code=2)
        name = typer.prompt("项目名")

    try:
        validate_name(name)
    except GenerationError as exc:
        typer.secho(f"错误：{exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=2) from exc

    # 2) 可选模块：Celery 强制依赖 Redis
    use_celery = celery
    if use_celery:
        if redis is False:
            typer.secho(
                "错误：--celery 必须依赖 Redis，不能与 --no-redis 同时使用。",
                fg=typer.colors.RED,
                err=True,
            )
            raise typer.Exit(code=2)
        use_redis = True
        if redis is None:
            typer.secho(
                "提示：已启用 --celery，自动启用 Redis 作为 broker。",
                fg=typer.colors.YELLOW,
            )
    else:
        use_redis = bool(redis)

    # 3) 目标目录
    target_dir = (path / name) if path is not None else (Path.cwd() / name)
    target_dir = target_dir.resolve()

    # 4) 解析模板来源并生成
    try:
        with resolve_template(template, template_ref, template_subdir) as template_dir:
            opts = ProjectOptions(
                name=name,
                target_dir=target_dir,
                use_redis=use_redis,
                use_celery=use_celery,
                use_docker=docker,
                force=force,
                template_dir=template_dir,
            )
            result = generate_project(opts)
    except GenerationError as exc:
        typer.secho(f"错误：{exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from exc

    _print_summary(opts, result, template)


def _print_summary(opts: ProjectOptions, result: GenerationResult, template: str | None) -> None:
    modules = []
    if opts.use_redis:
        modules.append("Redis")
    if opts.use_celery:
        modules.append("Celery")
    if opts.use_docker:
        modules.append("Docker")
    modules_text = "、".join(modules) if modules else "无"

    typer.secho("\n✓ 项目生成完成", fg=typer.colors.GREEN, bold=True)
    typer.echo(f"  路径：{result.target_dir}")
    typer.echo(f"  生成文件数：{result.file_count}")
    typer.echo(f"  模板来源：{template or '内置'}")
    typer.echo(f"  可选模块：{modules_text}")

    if result.skipped:
        typer.secho(
            f"\n已跳过 {len(result.skipped)} 个已存在文件（未加 --force）：",
            fg=typer.colors.YELLOW,
        )
        for rel in result.skipped:
            typer.echo(f"  - {rel}")

    typer.echo("\n下一步（请自行执行）：")
    typer.echo(f"  cd {result.target_dir}")
    typer.echo("  uv sync")
    typer.echo("  cp .env.example .env   # 修改 SECRET_KEY 等")
    typer.echo("  uv run flask db init")
    typer.echo("  uv run flask db migrate -m 'init' && uv run flask db upgrade")
    typer.echo("  uv run flask run")
    if opts.use_celery:
        typer.echo("  uv run celery -A wsgi:celery_app worker -l info   # 需本地 Redis")
    if opts.use_docker:
        typer.echo("  docker compose up --build")


def run() -> None:
    typer.run(main)


if __name__ == "__main__":
    run()
