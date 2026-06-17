"""路由注册。"""

from __future__ import annotations

from flask import Flask

from app.api.health import health_bp


def register_routes(app: Flask) -> None:
    app.register_blueprint(health_bp)
