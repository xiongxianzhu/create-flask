"""WSGI 入口。"""

from __future__ import annotations

from app import create_app

app = create_app()
{% if use_celery %}

from app.extensions import celery_init_app  # noqa: E402

celery_app = celery_init_app(app)

from app import tasks  # noqa: E402, F401
{% endif %}
