from datetime import datetime

from pydantic import BaseModel, ConfigDict


class OperationLogUserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    real_name: str


class OperationLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user: OperationLogUserRead | None
    module: str
    operation_type: str
    target_id: str | None
    target_name: str | None
    operation_detail: str | None
    ip_address: str | None
    created_at: datetime


class OperationLogListResponse(BaseModel):
    items: list[OperationLogRead]
    total: int
    page: int
    page_size: int
