# create-flask 现代 Flask 项目生成器需求

时间：20260617

## 工具定位

- `create-flask` 是基于 Typer 的命令行脚手架工具，一条命令生成生产可用的现代 Flask 项目骨架。
- 工具本身只负责生成文件，不得代为执行 `uv sync`、数据库迁移、启动服务等命令，仅生成后文字提示后续步骤。
- 生成项目核心技术栈固定为：纯 Flask + Pydantic + uv + ruff + pydantic-settings + SQLAlchemy 2.0 + gunicorn + 类型检查（mypy 或 pyright）。
- 不得依赖 Flask-RESTful、Flask-Smorest、Marshmallow；API 采用纯 Flask（蓝图 + 视图函数），入/出参用 Pydantic。
- Redis、Celery、Docker 均为可选模块，通过开关按需加入，不计入核心技术栈。
- 默认生产部署形态为 gunicorn + supervisor + nginx（传统方式）；Docker 为可选的容器化替代方案。
- CLI 与生成项目均基于 Python 3.13。

## CLI 命令

- 应提供 `create-flask <name>` 直接生成项目骨架（单命令，无 `new` 子命令）。
- 应支持 `--path` 指定目标目录，默认在当前目录下创建与项目名同名文件夹。
- 项目名必须为小写、可用中划线分隔单词；不得含下划线、空格或特殊字符，非法时应拒绝并提示原因。
- 应支持非交互（参数化）模式便于 CI 调用，缺参且为交互终端时可进入问答模式；非交互环境缺参应报错而非挂起。
- 应提供 `--yes` 跳过交互、`--force` 允许覆盖、`--version` 输出版本、`--help` 显示帮助。
- 应支持可选模块开关 `--redis`、`--celery`、`--docker`；未指定时不生成对应模块文件，也不引入相关依赖。
- 应支持 `--template / -t` 指定模板来源：缺省用内置模板，可传本地目录路径或 git 地址；并提供 `--template-ref`（git 分支/标签）与 `--template-subdir`（模板子目录）。

## 项目生成

- 模板应使用统一占位符（如 `{{project_name}}`、`{{package_name}}`），生成时同时替换文件内容与文件/目录路径。
- 生成产物中不得残留任何未替换占位符；包名由项目名规范化得到（中划线转下划线）。
- 默认应跳过目标路径下已存在文件，加 `--force` 时才覆盖。
- 生成完成后应输出结构化摘要：项目路径、文件数、技术栈、后续命令；有跳过文件时应明确列出。
- 单次生成（不含依赖安装）应在 2 秒内完成；生成失败不得留下不可用的半成品目录。

## 生成项目结构与特性

- 应采用应用工厂模式：暴露 `create_app(config)`，扩展实例集中管理以避免循环导入。
- 应采用分层目录结构（core / models / schemas / services / api / routes），空目录以 `.gitkeep` 占位。
- API 应使用纯 Flask 蓝图 + 视图函数；`routes/` 集中注册蓝图；`schemas/` 用 Pydantic。
- 应提供示例健康检查端点（如 `GET /health`）用于冒烟验证，启动后访问应返回 HTTP 200。
- 应提供 WSGI 入口与 `README.md`（含本地开发与生产部署说明）。

## 生成项目目录结构

生成的项目应符合下述结构（标注 `[可选]` 的文件/目录仅在对应开关启用时生成）：

```text
<project-name>/
├── app/                          # 应用包（包名由项目名规范化得到）
│   ├── __init__.py               # 应用工厂 create_app(config)
│   ├── extensions.py             # 扩展实例集中管理（db、migrate 等）
│   ├── settings.py               # pydantic-settings 配置（分环境）
│   ├── core/                     # 框架级公共能力
│   │   ├── __init__.py
│   │   ├── base.py               # BaseModel（id/时间戳）
│   │   ├── exceptions.py         # 统一异常
│   │   └── constants.py
│   ├── models/                   # SQLAlchemy 2.0 模型
│   │   └── __init__.py
│   ├── schemas/                  # Pydantic 入/出参模型
│   │   └── __init__.py
│   ├── services/                 # 业务逻辑
│   │   └── __init__.py
│   ├── api/                      # 接口（Flask 蓝图 + 视图函数）
│   │   ├── __init__.py
│   │   └── health.py             # 示例健康检查端点（蓝图）
│   ├── routes/                   # 蓝图注册 register_routes(app)
│   │   └── __init__.py
│   └── tasks/                    # [可选 --celery] Celery 任务
│       └── __init__.py
├── deploy/
│   └── supervisor/
│       └── <project-name>.conf   # supervisor 进程配置
├── logs/
│   └── .gitkeep
├── tests/                        # pytest 测试
│   └── __init__.py
├── wsgi.py                       # WSGI 入口，暴露 app
├── celeryconfig.py               # [可选 --celery] Celery broker/result 配置
├── gunicorn.conf.py              # gunicorn 配置
├── pyproject.toml                # 项目元数据、依赖、ruff/类型检查配置
├── .python-version               # 固定 3.13
├── .env.example                  # 配置示例（不含真实密钥）
├── .gitignore
├── Dockerfile                    # [可选 --docker]
├── docker-compose.yml            # [可选 --docker]
├── .dockerignore                 # [可选 --docker]
└── README.md                     # 本地开发与生产部署说明
```

- 包名应由项目名规范化得到（中划线转下划线），目录与配置内引用应保持一致。
- 空目录（如 `logs`）应以 `.gitkeep` 占位以便 git 跟踪；`migrations/` 由用户执行 `flask db init` 时生成，不预置占位。
- 启用 `--docker` 时应生成 Docker 相关文件；启用 `--celery` 时应生成 `app/tasks/` 与 `celeryconfig.py`；未启用的可选文件不得出现在产物中。
- 启用 `--redis` 时不新增独立目录，使用官方 `redis` 客户端：在应用工厂内 `Redis.from_url(...)` 创建并存入 `app.extensions["redis"]`，`app/extensions.py` 提供 `get_redis()` 辅助，`app/settings.py` 与 `.env.example` 增加 `REDIS_URL` 配置项。不得使用 flask-redis。

## 模板来源（--template）

- 应支持三种模板来源：内置（默认）、本地目录路径、git 地址。
- git 来源应使用系统 `git clone`（浅克隆）拉取到临时目录，生成结束后清理；未安装 git 或克隆失败应给出明确错误。
- 来源判定：以 `http(s)://`、`git@`、`ssh://`、`git://` 开头或以 `.git` 结尾按 git 处理，其余按本地路径。
- 克隆产物中的 `.git/` 等 VCS 元数据不得进入生成结果；非文本文件应原样复制、不做模板渲染。
- 外部模板应遵循与内置一致的约定：Jinja2 占位（`project_name` / `package_name` / `use_redis` / `use_celery` / `use_docker`）、点文件无点占位名、可选模块按约定路径门控、supervisor 配置按项目名重命名、空目录 `.gitkeep` 占位。
- 来源目录不存在或子目录不存在时应报错并终止。

## 依赖管理（uv）

- 生成项目应使用 uv 管理依赖与虚拟环境，并提供 `pyproject.toml`（声明运行时依赖与 dev 依赖）。
- 应提供 `.python-version` 固定为 3.13；运行时不得强依赖 uv（可用标准 venv + pip 安装）。
- 在生成目录执行 `uv sync` 应能成功安装并生成 `uv.lock`（由用户执行，本工具不代跑）。

## 配置系统（pydantic-settings）

- 配置应基于 pydantic-settings，支持类型校验与默认值，从 `.env` 与环境变量读取，并提供 `.env.example`。
- 应区分多环境（development / production / testing），可通过环境变量切换。
- 敏感配置（`SECRET_KEY`、`DATABASE_URL`）不得在代码硬编码明文，应由 `.env` 提供；缺必填项时应在启动阶段抛出明确校验错误。
- `.env.example` 仅含占位/示例值，不得写入真实密钥。

## ORM（SQLAlchemy 2.0）

- 应采用 SQLAlchemy 2.0 风格：`DeclarativeBase` + `Mapped` / `mapped_column` 类型化声明。
- 应提供模型基类（含 `id`、创建/更新时间戳等公共字段）及会话管理与数据库初始化逻辑。
- 数据库连接应经配置系统读取；默认数据库为 SQLite，可切换至 PostgreSQL / MySQL。

## 代码质量（ruff + 类型检查）

- 应在 `pyproject.toml` 提供 ruff 的 lint 与 format 规则，生成代码应默认通过 `ruff check .` 与 `ruff format --check .`。
- 应集成类型检查（mypy 或 pyright）并提供配置，生成代码应默认无类型告警。

## 生产部署（默认：gunicorn + supervisor + nginx）

- 应将 gunicorn 作为生产 WSGI server 写入依赖，并提供其配置（如 `gunicorn.conf.py`）。
- 应提供 supervisor 配置模板（如 `deploy/supervisor/<name>.conf`）用于进程管理，默认拉起 `.venv/bin/gunicorn`。
- nginx 作为反向代理，模板可不内置具体配置，但 `README.md` 应说明如何反代至 gunicorn（默认 `127.0.0.1:8000`）。
- supervisor 配置中的目录、命令路径、运行用户、日志路径等应使用占位/约定路径，由用户部署前修改。

## 可选模块

- **Redis（`--redis`）**：应使用官方 `redis` 客户端集成（不得用 flask-redis），含配置项（如 `REDIS_URL`），由配置系统读取；未启用时产物中不得包含相关依赖。
- **Celery（`--celery`）**：应生成 Celery 配置（broker / result 默认指向 Redis）、worker 入口与示例任务目录，并绑定 Flask 应用上下文。
- Celery 必须依赖 Redis 作为 broker / result backend：启用 `--celery` 时必须同时启用 Redis，未显式指定 `--redis` 时应自动启用并在摘要中提示；若用户显式传入与之冲突的开关（如 `--no-redis`），应直接报错并终止生成。
- **Docker（`--docker`）**：应生成 `Dockerfile`（基于精简 Python 镜像，使用 uv 安装依赖）、`docker-compose.yml` 与 `.dockerignore`；作为 gunicorn+supervisor+nginx 之外的容器化部署替代方案。
  - 启用时容器应以 gunicorn 作为入口，业务进程不得以 root 身份运行，生成项目应可 `docker build` 成功（由用户执行）。
  - 同时启用 `--redis` / `--celery` 时，`docker-compose.yml` 应一并加入对应服务（如 redis、worker）。
- 可选模块的依赖应仅在启用时写入 `pyproject.toml`，`.env.example` 相应补充其配置占位项。

## 约束与假设

- CLI 基于 Typer，生成逻辑尽量零额外重依赖（优先标准库）。
- 假设用户本机已安装 Python 3.13 与 uv，或愿意按 README 安装。
- CLI 应可在 macOS、Linux 运行，Windows 为可选支持。

## 变更记录

- 20260617 v1.0：初版（简化版）创建。
