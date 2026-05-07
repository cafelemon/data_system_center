from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    code: int
    message: str
    data: T | None = None


def ok(data: T | None = None, message: str = "ok") -> ApiResponse[T]:
    return ApiResponse(code=0, message=message, data=data)


def fail(
    message: str,
    code: int = 1,
    data: T | None = None,
) -> ApiResponse[T]:
    return ApiResponse(code=code, message=message, data=data)
