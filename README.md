# create-flask

![Python](https://img.shields.io/badge/python-3.13-3776AB?style=flat&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-pure-000000?style=flat&logo=flask&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=flat&logo=sqlalchemy&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-2-E92063?style=flat&logo=pydantic&logoColor=white)
![uv](https://img.shields.io/badge/uv-managed-DE5FE9?style=flat&logo=uv&logoColor=white)
![Ruff](https://img.shields.io/badge/lint-ruff-D7FF64?style=flat&logo=ruff&logoColor=black)
![Typer](https://img.shields.io/badge/CLI-Typer-009485?style=flat&logo=typer&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-blue?style=flat)

现代化 Flask 项目脚手架，内置最佳实践。

基于 **Typer** 的命令行工具，一条命令生成生产可用的 Flask 项目骨架。

## 核心技术栈（生成项目）

- **运行时**：Python 3.13、uv
- **Web**：纯 Flask（蓝图 + 视图函数）
- **数据**：SQLAlchemy 2.0、Flask-SQLAlchemy、Flask-Migrate
- **校验/配置**：Pydantic、pydantic-settings
- **代码质量**：ruff、mypy
- **生产**：gunicorn + supervisor + nginx

> 不依赖 Flask-RESTful / Flask-Smorest / Marshmallow。

可选模块（按需开启，不计入核心栈）：Redis（`--redis`，使用官方 redis 客户端）、Celery（`--celery`，强制依赖 Redis）、Docker（`--docker`）。

## 安装与使用

```bash
# 在本仓库内
uv sync

# 生成项目
uv run create-flask my-api
uv run create-flask my-api --redis --celery --docker
uv run create-flask my-api --path ./services --force

# 帮助 / 版本
uv run create-flask --help
uv run create-flask --version
```

> 本工具只负责生成文件，不会代为执行 `uv sync`、数据库迁移或启动服务；后续步骤见生成项目的 `README.md`。

## 命令

`create-flask <name>`

| 参数 | 说明 |
|------|------|
| `<name>` | 项目名（小写，可用中划线分隔；不得含下划线/空格/特殊字符） |
| `--path` | 目标目录，默认当前目录下与项目名同名文件夹 |
| `--redis / --no-redis` | 集成 Redis 客户端 |
| `--celery` | 集成 Celery（自动启用 Redis；与 `--no-redis` 冲突时报错） |
| `--docker` | 生成 Dockerfile / docker-compose / .dockerignore |
| `--force` | 覆盖已存在文件（默认跳过） |
| `--yes`, `-y` | 跳过交互 |
| `--template`, `-t` | 模板来源：缺省用内置；可传本地目录或 git 地址 |
| `--template-ref` | git 模板的分支或标签（仅 git 来源） |
| `--template-subdir` | 模板根所在子目录 |

## 自定义模板

`-t` 支持三种来源：

```bash
# 1) 内置模板（默认）
uv run create-flask my-api

# 2) 本地目录
uv run create-flask my-api -t ./my-template

# 3) git 仓库（自动 git clone，结束后清理；可指定分支/子目录）
uv run create-flask my-api -t https://github.com/user/flask-template
uv run create-flask my-api -t git@github.com:user/repo.git --template-ref main --template-subdir templates/api
```

git 来源依赖系统已安装 `git`。`http(s)://`、`git@`、`ssh://`、`git://` 开头或以 `.git` 结尾的来源按 git 处理，其余按本地路径。克隆出的 `.git/` 不会进入生成结果。

**模板约定**（外部模板需遵循，与内置一致）：

- 使用 Jinja2，占位变量：`{{ project_name }}`、`{{ package_name }}`（中划线转下划线），及布尔量 `use_redis` / `use_celery` / `use_docker`。
- 点文件用无点文件名占位：`gitignore`、`dockerignore`、`python-version`、`env.example`（生成时自动加点）。
- 可选模块按路径门控：`celeryconfig.py`、`app/tasks/__init__.py` 仅 `--celery` 生成；`Dockerfile`、`docker-compose.yml`、`dockerignore` 仅 `--docker` 生成。
- `deploy/supervisor/supervisor.conf` 生成时按项目名重命名为 `<name>.conf`。
- 空目录用 `.gitkeep` 占位；非文本文件原样复制不渲染。

## 开发

```bash
uv sync
uv run pytest
uv run ruff check .
uv run mypy
```
