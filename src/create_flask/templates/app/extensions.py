"""扩展实例集中管理，避免循环导入。"""

from __future__ import annotations

{% if use_celery %}from celery import Celery, Task
from flask import Flask, current_app
{% elif use_redis %}from flask import current_app
{% endif %}from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
{% if use_redis %}from redis import Redis
{% endif %}from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """SQLAlchemy 2.0 声明式基类。"""


db = SQLAlchemy(model_class=Base)
migrate = Migrate()
{% if use_redis %}


def get_redis() -> Redis:
    """获取当前应用绑定的 Redis 客户端。"""
    return current_app.extensions["redis"]
{% endif %}
{% if use_celery %}


def celery_init_app(app: Flask) -> Celery:
    """创建并绑定 Flask 应用上下文的 Celery 实例。"""

    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object("celeryconfig")
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app
{% endif %}
