.DEFAULT_GOAL := help

UV  ?= uv
RUN := $(UV) run
MSG ?= init

.PHONY: help install env run db-init db-migrate db-upgrade db-setup \
	lint format format-check typecheck test check gunicorn prod-sync{% if use_celery %} celery{% endif %}{% if use_docker %} docker-up docker-down{% endif %}

help: ## 显示可用命令
	@grep -E '^[a-zA-Z0-9_-]+:.*?##' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

install: ## 安装依赖 (uv sync)
	$(UV) sync

env: ## 复制 .env.example → .env（已存在则跳过）
	@test -f .env || cp .env.example .env
	@echo ".env 已就绪"

run: ## 启动开发服务器 (flask run)
	$(RUN) flask run

db-init: ## 初始化迁移目录
	$(RUN) flask db init

db-migrate: ## 生成迁移脚本 (make db-migrate MSG="描述")
	$(RUN) flask db migrate -m "$(MSG)"

db-upgrade: ## 应用迁移
	$(RUN) flask db upgrade

db-setup: db-init db-migrate db-upgrade ## 首次初始化数据库（init → migrate → upgrade）

lint: ## ruff 检查
	$(RUN) ruff check .

format: ## ruff 格式化
	$(RUN) ruff format .

format-check: ## 检查格式（CI 用）
	$(RUN) ruff format --check .

typecheck: ## mypy 类型检查
	$(RUN) mypy

test: ## 运行测试
	$(RUN) pytest

check: lint format-check typecheck test ## 全部质量检查

gunicorn: ## 生产模式启动 (gunicorn)
	$(RUN) gunicorn -c gunicorn.conf.py wsgi:app

prod-sync: ## 生产依赖安装 (--frozen --no-dev)
	$(UV) sync --frozen --no-dev
{% if use_celery %}

celery: ## 启动 Celery worker
	$(RUN) celery -A wsgi:celery_app worker -l info
{% endif %}{% if use_docker %}

docker-up: ## 构建并启动容器
	docker compose up --build

docker-down: ## 停止并移除容器
	docker compose down
{% endif %}
