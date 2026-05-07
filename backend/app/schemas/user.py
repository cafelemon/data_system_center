from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

UserStatus = Literal["enabled", "disabled"]


class RoleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    code: str
    enabled: bool


class DepartmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    code: str
    enabled: bool


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    real_name: str
    email: str
    status: UserStatus
    role: RoleRead
    department: DepartmentRead
    created_at: datetime
    updated_at: datetime


class UserListResponse(BaseModel):
    items: list[UserRead]
    total: int
    page: int
    page_size: int


class UserCreate(BaseModel):
    username: str = Field(min_length=2, max_length=50)
    real_name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=3, max_length=255)
    role_id: int
    department_id: int
    status: UserStatus = "enabled"
    password: str | None = Field(default=None, min_length=8, max_length=100)


class UserUpdate(BaseModel):
    real_name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=3, max_length=255)
    role_id: int
    department_id: int
    status: UserStatus
    password: str | None = Field(default=None, min_length=8, max_length=100)


class UserStatusUpdate(BaseModel):
    status: UserStatus


class SelectOption(BaseModel):
    id: int
    name: str
    code: str


class StatusOption(BaseModel):
    label: str
    value: UserStatus


class UserOptionsResponse(BaseModel):
    roles: list[SelectOption]
    departments: list[SelectOption]
    statuses: list[StatusOption]
