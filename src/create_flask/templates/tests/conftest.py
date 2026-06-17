"""测试夹具：提供启动所需的最小环境变量。"""

from __future__ import annotations

import os

os.environ.setdefault("SECRET_KEY", "testing-secret")
os.environ.setdefault("DATABASE_URL", "sqlite://")
