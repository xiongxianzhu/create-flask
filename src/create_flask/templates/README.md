# {{ project_name }}

由 [create-flask](https://github.com/) 生成的现代 Flask 项目。

## 技术栈

- **运行时**：Python 3.13、uv
- **Web**：纯 Flask（蓝图 + 视图函数）
- **数据**：SQLAlchemy 2.0、Flask-SQLAlchemy、Flask-Migrate
- **校验/序列化**：Pydantic、pydantic-settings（读取 `.env`）
- **代码质量**：ruff（lint/format）、mypy（类型检查）
- **生产**：gunicorn + supervisor + nginx
{% if use_redis %}- **缓存**：Redis（redis 官方客户端）
{% endif %}{% if use_celery %}- **任务队列**：Celery（broker/result = Redis）
{% endif %}{% if use_docker %}- **容器化**：Docker、docker compose
{% endif %}

## 目录结构

```text
app/                应用包（应用工厂 create_app）
├── core/           基类、异常、常量
├── models/         SQLAlchemy 模型
├── schemas/        Pydantic 入/出参
├── services/       业务逻辑
├── api/            接口（蓝图 + 视图函数）
├── routes/         蓝图注册
{% if use_celery %}├── tasks/          Celery 任务
{% endif %}├── extensions.py   扩展实例
└── settings.py     配置
wsgi.py             WSGI 入口（暴露 app）
gunicorn.conf.py    gunicorn 配置
deploy/supervisor/  supervisor 配置
tests/              测试
```

## 本地开发

```bash
uv sync
cp .env.example .env       # 修改 SECRET_KEY、DATABASE_URL 等

uv run flask db init
uv run flask db migrate -m "init"
uv run flask db upgrade
uv run flask run
```

健康检查：`GET http://127.0.0.1:5000/health` 应返回 `{"status": "ok"}`。

## 代码质量

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest
```
{% if use_celery %}
## Celery

需本地或远程 Redis 可用，启动 worker：

```bash
uv run celery -A wsgi:celery_app worker -l info
```
{% endif %}
## 生产部署（gunicorn + supervisor + nginx）

```bash
uv python install 3.13
uv sync --frozen --no-dev
uv run flask db upgrade
```

- 使用 `deploy/supervisor/{{ project_name }}.conf` 配置 supervisor（部署前修改 `directory`、`user`、日志路径）。
- 由 gunicorn 监听 `127.0.0.1:8000`（见 `gunicorn.conf.py`）。
- 用 nginx 反向代理至 gunicorn，例如：

```nginx
server {
    listen 80;
    server_name example.com;
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```
{% if use_docker %}
## 容器化部署

```bash
docker compose up --build
```

应用监听容器内 `0.0.0.0:8000`，映射到宿主机 `8000` 端口。
{% endif %}
