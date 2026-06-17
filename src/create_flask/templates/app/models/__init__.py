"""SQLAlchemy 2.0 模型。

在此定义业务模型，继承 ``app.core.base.BaseModel``，例如::

    from sqlalchemy.orm import Mapped, mapped_column
    from app.core.base import BaseModel

    class User(BaseModel):
        __tablename__ = "users"
        name: Mapped[str] = mapped_column(index=True)
"""
