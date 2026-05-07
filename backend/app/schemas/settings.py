from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ArchiveTypeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    code: str
    enabled: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime


class ArchiveTypeListResponse(BaseModel):
    items: list[ArchiveTypeRead]


class ArchiveTypePayload(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    code: str = Field(min_length=1, max_length=50)
    enabled: bool = True
    sort_order: int | None = None


class RetentionPeriodRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    years: int
    enabled: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime


class RetentionPeriodListResponse(BaseModel):
    items: list[RetentionPeriodRead]


class RetentionPeriodPayload(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    years: int = Field(ge=-1)
    enabled: bool = True
    sort_order: int | None = None


class EnabledUpdate(BaseModel):
    enabled: bool
