"""统一异常。"""

from __future__ import annotations


class APIException(Exception):
    """业务异常基类。"""

    status_code: int = 400
    message: str = "请求错误"

    def __init__(self, message: str | None = None, status_code: int | None = None) -> None:
        super().__init__(message or self.message)
        if message is not None:
            self.message = message
        if status_code is not None:
            self.status_code = status_code

    def to_dict(self) -> dict[str, object]:
        return {"message": self.message}
