"""Pydantic 入/出参模型。

定义请求/响应 schema，例如::

    from app.schemas import BaseSchema

    class UserOut(BaseSchema):
        id: int
        name: str
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """基础 schema：支持从 ORM 对象属性读取。"""

    model_config = ConfigDict(from_attributes=True)
