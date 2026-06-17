<h1 align="center">create-flask</h1>

<p align="center">
  <sub>一条命令，生成生产可用的现代 Flask 项目骨架</sub>
</p>

<p align="center">
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/Python-3.13-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.13"/></a>
  <a href="https://github.com/astral-sh/uv"><img src="https://img.shields.io/badge/uv-managed-DE5FE9?style=flat-square&logo=uv&logoColor=white" alt="uv"/></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-2EA043?style=flat-square" alt="MIT License"/></a>
</p>

<p align="center">
  <a href="https://flask.palletsprojects.com/"><img src="https://img.shields.io/badge/Flask-pure-000000?style=flat-square&logo=flask&logoColor=white" alt="Flask"/></a>
  <a href="https://www.sqlalchemy.org/"><img src="https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=flat-square&logo=sqlalchemy&logoColor=white" alt="SQLAlchemy 2.0"/></a>
  <a href="https://docs.pydantic.dev/"><img src="https://img.shields.io/badge/Pydantic-2-E92063?style=flat-square&logo=pydantic&logoColor=white" alt="Pydantic 2"/></a>
  <a href="https://docs.gunicorn.org/"><img src="https://img.shields.io/badge/gunicorn-WSGI-499848?style=flat-square" alt="gunicorn"/></a>
</p>

<p align="center">
  <a href="https://docs.astral.sh/ruff/"><img src="https://img.shields.io/badge/Ruff-lint%20%2B%20format-D7FF64?style=flat-square&logo=ruff&logoColor=000000" alt="Ruff"/></a>
  <a href="https://mypy-lang.org/"><img src="https://img.shields.io/badge/mypy-typed-2B5B84?style=flat-square&logo=mypy&logoColor=white" alt="mypy"/></a>
  <a href="https://typer.tiangolo.com/"><img src="https://img.shields.io/badge/CLI-Typer-009485?style=flat-square&logo=typer&logoColor=white" alt="Typer"/></a>
  <img src="https://img.shields.io/badge/no_REST_framework-✓-4A4A4A?style=flat-square&logo=flask&logoColor=white" alt="No Flask-RESTful / Smorest / Marshmallow"/>
</p>

---

基于 **Typer** 的 CLI 脚手架。生成文件后由你自行 `uv sync`、迁移与启动——工具不代跑任何初始化命令。

```bash
uv sync
uv run create-flask my-api
cd my-api && uv sync && cp .env.example .env && uv run flask run
```

## 特性

| | |
|---|---|
| **纯 Flask + Pydantic** | 蓝图 + 视图函数，入/出参用 Pydantic；不依赖 Flask-RESTful / Smorest / Marshmallow |
| **现代工具链** | uv 依赖管理 · ruff lint/format · mypy 类型检查 · pydantic-settings 配置 |
| **SQLAlchemy 2.0** | `Mapped` / `mapped_column` 类型化模型 · Flask-Migrate 迁移 |
| **生产就绪** | gunicorn + supervisor + nginx 模板 · 可选 Docker 容器化 |
| **可选模块** | `--redis`（官方 redis 客户端）· `--celery`（强制依赖 Redis）· `--docker` |
| **自定义模板** | 内置 / 本地目录 / git 仓库，同一套 Jinja 约定与模块门控 |

## 快速开始

```bash
# 安装（本仓库）
uv sync

# 生成项目
uv run create-flask my-api
uv run create-flask my-api --redis --celery --docker
uv run create-flask my-api --path ./services --force

# 查看帮助
uv run create-flask --help
uv run create-flask --version
```

生成完成后，进入项目目录按 `README.md` 执行 `uv sync`、数据库迁移与启动。

## 命令参考

```text
create-flask <name> [OPTIONS]
```

| 参数 | 说明 |
|------|------|
| `<name>` | 项目名：小写，可用 `-` 分隔；不得含 `_`、空格或特殊字符 |
| `--path` | 目标目录，默认在当前目录创建 `<name>/` |
| `--redis` / `--no-redis` | 集成 Redis 客户端（可选） |
| `--celery` | 集成 Celery；自动启用 Redis，与 `--no-redis` 冲突时报错 |
| `--docker` | 生成 Dockerfile / docker-compose / .dockerignore |
| `--template`, `-t` | 模板来源：内置（默认）/ 本地路径 / git 地址 |
| `--template-ref` | git 模板的分支或标签 |
| `--template-subdir` | 模板根所在子目录 |
| `--force` | 覆盖已存在文件（默认跳过） |
| `--yes`, `-y` | 跳过交互 |

## 自定义模板

`-t` 支持三种来源，渲染规则与内置模板一致（Jinja2 + 可选模块门控）：

```bash
# 内置（默认）
uv run create-flask my-api

# 本地目录
uv run create-flask my-api -t ./my-template

# git 仓库（浅克隆，结束后清理）
uv run create-flask my-api -t https://github.com/user/flask-template
uv run create-flask my-api -t git@github.com:user/repo.git \
  --template-ref main --template-subdir templates/api
```

<details>
<summary><strong>外部模板约定</strong></summary>

- **占位变量**：`{{ project_name }}`、`{{ package_name }}`（`-` → `_`），及 `use_redis` / `use_celery` / `use_docker`
- **点文件占位名**：`gitignore`、`dockerignore`、`python-version`、`env.example`（生成时自动加点）
- **模块门控**：`celeryconfig.py`、`app/tasks/` 仅 `--celery`；Docker 三件套仅 `--docker`
- **supervisor**：`deploy/supervisor/supervisor.conf` → `<name>.conf`
- **其他**：空目录用 `.gitkeep`；非文本文件原样复制；克隆的 `.git/` 不进入产物

git 来源需系统已安装 `git`。`http(s)://`、`git@`、`ssh://`、`git://` 或 `.git` 结尾按 git 处理，其余为本地路径。

</details>

## 生成项目结构

```text
my-api/
├── app/
│   ├── core/          # 基类、异常、常量
│   ├── models/        # SQLAlchemy 2.0 模型
│   ├── schemas/       # Pydantic 入/出参
│   ├── services/      # 业务逻辑
│   ├── api/           # 蓝图 + 视图函数
│   ├── routes/        # 蓝图注册
│   ├── extensions.py  # db、migrate 等扩展实例
│   └── settings.py    # pydantic-settings
├── deploy/supervisor/ # 进程配置模板
├── tests/
├── wsgi.py
├── gunicorn.conf.py
└── pyproject.toml
```

## 开发

```bash
uv sync
uv run pytest
uv run ruff check .
uv run mypy
```

---

<p align="center">
  <sub>MIT · 只生成文件，不代跑 <code>uv sync</code> / 迁移 / 启动</sub>
</p>
