"""应用工厂。"""

from __future__ import annotations

from flask import Flask
{% if use_redis %}
from redis import Redis
{% endif %}

from app.extensions import db, migrate
from app.routes import register_routes
from app.settings import get_settings


def create_app() -> Flask:
    app = Flask(__name__, static_folder=None)
    settings = get_settings()

    app.config["SECRET_KEY"] = settings.secret_key
    app.config["SQLALCHEMY_DATABASE_URI"] = settings.database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    migrate.init_app(app, db)
{% if use_redis %}    app.extensions["redis"] = Redis.from_url(settings.redis_url, decode_responses=True)
{% endif %}
    # 导入模型，确保 Flask-Migrate 能侦测到表结构
    from app import models  # noqa: F401

    register_routes(app)
    return app
