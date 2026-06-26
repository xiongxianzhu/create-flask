<h1 align="center">create-flask</h1>

<p align="center">
  <sub>一条命令，生成生产可用的现代 Flask 项目骨架</sub>
</p>

<p align="center">
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.13"/></a>
  <a href="https://github.com/astral-sh/uv"><img src="https://img.shields.io/badge/uv-managed-DE5FE9?style=for-the-badge&logo=uv&logoColor=white" alt="uv"/></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-2EA043?style=for-the-badge" alt="MIT License"/></a>
</p>

<p align="center">
  <a href="https://flask.palletsprojects.com/"><img src="https://img.shields.io/badge/Flask-pure-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask"/></a>
  <a href="https://www.sqlalchemy.org/"><img src="https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white" alt="SQLAlchemy 2.0"/></a>
  <a href="https://docs.pydantic.dev/"><img src="https://img.shields.io/badge/Pydantic-2-E92063?style=for-the-badge&logo=pydantic&logoColor=white" alt="Pydantic 2"/></a>
  <a href="https://docs.gunicorn.org/"><img src="https://img.shields.io/badge/gunicorn-WSGI-499848?style=for-the-badge" alt="gunicorn"/></a>
</p>

<p align="center">
  <a href="https://docs.astral.sh/ruff/"><img src="https://img.shields.io/badge/Ruff-lint%20%2B%20format-D7FF64?style=for-the-badge&logo=ruff&logoColor=000000" alt="Ruff"/></a>
  <a href="https://mypy-lang.org/"><img src="https://img.shields.io/badge/mypy-typed-2B5B84?style=for-the-badge&logo=mypy&logoColor=white" alt="mypy"/></a>
  <a href="https://typer.tiangolo.com/"><img src="https://img.shields.io/badge/CLI-Typer-009485?style=for-the-badge&logo=typer&logoColor=white" alt="Typer"/></a>
  <img src="https://img.shields.io/badge/no_REST_framework-✓-4A4A4A?style=for-the-badge&logo=flask&logoColor=white" alt="No Flask-RESTful / Smorest / Marshmallow"/>
</p>

---

基于 **Typer** 的 CLI 脚手架。生成文件后由你自行 `uv sync`、迁移与启动——工具不代跑任何初始化命令。

```bash
uv tool install git+https://github.com/xiongxianzhu/create-flask.git
create-flask my-api
cd my-api && uv sync && cp .env.example .env && uv run flask run
```

## 技术栈

create-flask **工具本身**与**生成项目**使用不同技术栈，职责分离：

### 工具本身（create-flask CLI）

| 类别 | 技术 |
|------|------|
| 语言 | Python 3.13 |
| CLI | [Typer](https://typer.tiangolo.com/) |
| 模板引擎 | [Jinja2](https://jinja.palletsprojects.com/) |
| 打包 | [hatchling](https://hatch.pypa.io/) |
| 开发 | uv · pytest · ruff · mypy |

运行时依赖仅 **Typer + Jinja2**；模板渲染、可选模块门控、git 浅克隆均在此层完成。

### 生成项目（`create-flask my-api` 产物）

| 类别 | 技术 |
|------|------|
| 运行时 | Python 3.13 · [uv](https://github.com/astral-sh/uv) |
| Web | 纯 [Flask](https://flask.palletsprojects.com/)（蓝图 + 视图函数） |
| 校验 / 配置 | [Pydantic](https://docs.pydantic.dev/) · pydantic-settings |
| 数据 | [SQLAlchemy](https://www.sqlalchemy.org/) 2.0 · Flask-SQLAlchemy · Flask-Migrate |
| 代码质量 | [ruff](https://docs.astral.sh/ruff/) · [mypy](https://mypy-lang.org/) |
| 生产 | [gunicorn](https://docs.gunicorn.org/) + supervisor + nginx |

> 不依赖 Flask-RESTful / Flask-Smorest / Marshmallow。

**可选模块**（`--redis` / `--celery` / `--docker`，不计入核心栈）：

| 开关 | 技术 |
|------|------|
| `--redis` | 官方 [redis](https://redis.io/docs/latest/develop/clients/redis-py/) 客户端 |
| `--celery` | [Celery](https://docs.celeryq.dev/)（强制依赖 Redis） |
| `--docker` | Dockerfile · docker compose |

## 特性

| | |
|---|---|
| **纯 Flask + Pydantic** | 蓝图 + 视图函数，入/出参用 Pydantic；不依赖 Flask-RESTful / Smorest / Marshmallow |
| **现代工具链** | uv 依赖管理 · ruff lint/format · mypy 类型检查 · pydantic-settings 配置 |
| **SQLAlchemy 2.0** | `Mapped` / `mapped_column` 类型化模型 · Flask-Migrate 迁移 |
| **生产就绪** | gunicorn + supervisor + nginx 模板 · 可选 Docker 容器化 |
| **可选模块** | `--redis`（官方 redis 客户端）· `--celery`（强制依赖 Redis）· `--docker` |
| **自定义模板** | 内置 / 本地目录 / git 仓库，同一套 Jinja 约定与模块门控 |

## 安装

**要求**：Python 3.13+；推荐 [uv](https://github.com/astral-sh/uv)。使用 git 模板时需系统已安装 `git`。

### PyPI（发布后）

```bash
# 推荐：全局 CLI，任意目录可用
uv tool install create-flask

# 或 pip
pip install create-flask
pipx install create-flask
```

### 从 GitHub 安装（当前）

```bash
uv tool install git+https://github.com/xiongxianzhu/create-flask.git

# 更新或重装（上游有变更、安装失败或命中旧缓存时）
uv tool install --reinstall git+https://github.com/xiongxianzhu/create-flask.git

# 或 pip / pipx
pip install git+https://github.com/xiongxianzhu/create-flask.git
pipx install git+https://github.com/xiongxianzhu/create-flask.git
```

### 本地开发（贡献 / 调试）

```bash
git clone https://github.com/xiongxianzhu/create-flask.git
cd create-flask
uv sync

# 仓库内直接运行（无需全局安装）
uv run create-flask my-api
```

### 验证

```bash
create-flask --version
create-flask --help
```

### 卸载

按安装方式对应卸载全局 CLI（**不会**删除已生成的项目目录）：

```bash
# uv tool 安装时
uv tool uninstall create-flask

# pip 安装时
pip uninstall create-flask

# pipx 安装时
pipx uninstall create-flask
```

本地开发（clone 仓库 + `uv sync`）无需卸载命令，删除 clone 目录即可。

## 快速开始

```bash
# 生成项目（已全局安装时）
create-flask my-api
create-flask my-api --redis --celery --docker
create-flask my-api --path ./services --force

# 未全局安装、在仓库内开发时
uv run create-flask my-api
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
create-flask my-api

# 本地目录
create-flask my-api -t ./my-template

# git 仓库（浅克隆，结束后清理）
create-flask my-api -t https://github.com/user/flask-template
create-flask my-api -t git@github.com:user/repo.git \
  --template-ref main --template-subdir templates/api
```

<details>
<summary><strong>外部模板约定</strong></summary>

- **占位变量**：`{{ project_name }}`、`{{ package_name }}`（`-` → `_`），及 `use_redis` / `use_celery` / `use_docker`；可用于**文件内容**与**文件/目录名**
- **点文件占位名**：`gitignore`、`dockerignore`、`python-version`、`env.example`（生成时自动加点）
- **模块门控**：`celeryconfig.py`、`app/tasks/` 仅 `--celery`；Docker 三件套仅 `--docker`
- **路径示例**：`deploy/supervisor/{{ project_name }}.conf` → `deploy/supervisor/my-api.conf`
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
├── Makefile           # 常用开发命令
└── pyproject.toml
```

## PyPI 镜像源

本仓库与生成项目的 `pyproject.toml` 均默认使用腾讯 PyPI 镜像：

```toml
[tool.uv]
index-url = "https://mirrors.tencent.com/pypi/simple/"
```

若 `uv sync` 仍从其他镜像或官方 PyPI 拉包，常见原因如下。

### 优先级

uv 解析依赖时的镜像来源（高 → 低）：

1. 命令行 `--index-url`
2. 环境变量 `UV_INDEX_URL`
3. 项目 `pyproject.toml` 中的 `[tool.uv] index-url`
4. 官方 PyPI

因此 shell 里若设置了 `UV_INDEX_URL`（例如清华源），会**覆盖**项目内的腾讯源配置。uv 读取的是 `UV_INDEX_URL`，不是 `PIP_INDEX_URL`。

### `uv.lock` 会固定下载地址

`uv lock` 会把当时使用的 registry 和包 URL 写入 `uv.lock`。仅修改 `pyproject.toml` 不会自动换源；需重新锁依赖：

```bash
# 若希望本项目严格走 pyproject.toml 中的腾讯源，可先取消全局覆盖
unset UV_INDEX_URL

uv lock
uv sync
```

### 推荐做法

| 场景 | 做法 |
|------|------|
| 仅本项目用腾讯源 | 不设 `UV_INDEX_URL`，保留 `pyproject.toml` 中的 `index-url` |
| 所有项目统一镜像 | 在 `~/.zshrc` 等设置 `UV_INDEX_URL`，与项目配置保持一致 |
| 切换镜像后 | 执行 `uv lock` 再 `uv sync`，并提交更新后的 `uv.lock` |

## llms.txt · AI 导航

> 仓库根目录的 [`llms.txt`](llms.txt) 遵循 [llms.txt 规范](https://llmstxt.org/)，为 LLM / AI 助手提供**精简索引**——指向 README、PRD、核心源码与模板，避免通读全库。

| 文件 | 面向 |
|------|------|
| [`llms.txt`](llms.txt) | LLM 快速定位文档与关键路径 |
| [`AGENT.md`](AGENT.md) | Agent 协作约定、生成边界与开发命令 |

在 Cursor / Claude 等环境中，可将 `llms.txt` 作为上下文入口；`Optional` 小节内的链接可在上下文紧张时跳过。

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

<p align="center">
  <sub>姊妹项目 → <a href="https://github.com/xiongxianzhu/create-fastapi">create-fastapi</a></sub>
</p>
