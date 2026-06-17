"""健康检查冒烟测试。"""

from __future__ import annotations

from app import create_app


def test_health_ok() -> None:
    app = create_app()
    client = app.test_client()
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}
