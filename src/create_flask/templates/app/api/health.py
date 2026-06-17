"""健康检查端点。"""

from __future__ import annotations

from flask import Blueprint

health_bp = Blueprint("health", __name__)


@health_bp.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
