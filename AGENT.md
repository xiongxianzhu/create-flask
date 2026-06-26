# create-flask · Agent 指南

> **Typer CLI 脚手架** — 生成现代 Flask 项目骨架。  
> 本仓库维护**工具本身**；`templates/` 是生成产物的唯一真相源。

---

## 定位

| | |
|---|---|
| **做什么** | `create-flask <name>` → 渲染 Jinja 模板 → 落盘 Flask 项目 |
| **不做什么** | 不代跑 `uv sync`、迁移、启动服务；不实现业务 API |
| **姊妹项目** | [create-fastapi](https://github.com/xiongxianzhu/create-fastapi) |

---

## 仓库地图

```text
src/create_flask/
├── cli.py          # Typer 入口（create-flask <name>）
├── generator.py    # 渲染、门控、路径占位符、git 克隆
└── templates/      # ★ 改生成结果，只改这里

tests/              # 工具单测（不测生成项目的运行时）
docs/prd-create-flask.md
```

**改生成项目** → 编辑 `templates/`  
**改 CLI 行为** → 编辑 `cli.py` / `generator.py`

---

## 生成约定

```
占位符   {{ project_name }}  {{ package_name }}  use_redis / use_celery / use_docker
路径     文件名、目录名均支持 Jinja（如 deploy/supervisor/{{ project_name }}.conf）
点文件   gitignore → .gitignore   env.example → .env.example  …
门控     celery / docker 相关文件仅在对应开关启用时生成
应用包   固定为 app（import 稳定，与 wsgi:app 一致）
```

生成项目栈：**纯 Flask + Pydantic + SQLAlchemy 2.0 + uv + ruff + mypy + gunicorn**  
禁止引入 Flask-RESTful / Smorest / Marshmallow；Redis 用官方 `redis`，不用 flask-redis。

---

## 开发命令

```bash
uv sync
uv run pytest
uv run ruff check .
uv run ruff format .
uv run mypy
uv run create-flask demo --path /tmp
```

`templates/` 含 Jinja 语法，**ruff/mypy 已排除**，勿对模板跑 lint。

---

## 提交规范

- 语言：**简体中文**
- 格式：Conventional Commits — `feat:` `fix:` `docs:` `refactor:` `test:` `chore:` …
- 分支：`feat/<名>` · `fix/<名>` · `docs/<名>`

---

## 边界

- 最小 diff；不重构无关代码
- 不提交 `.env`、密钥、`uv.lock` 除非任务明确要求
- 模板变更后跑 `pytest`；必要时本地 `create-flask` 冒烟生成
- README / PRD 与模板行为不一致时，以 **generator + templates 实际逻辑** 为准并同步文档
