from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

ArchiveMedium = Literal["paper", "electronic"]


class ArchiveTypeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    code: str
    enabled: bool


class ArchiveStatusRead(BaseModel):
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


class RetentionPeriodRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    years: int
    enabled: bool


class ArchiveRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    archive_no: str
    title: str
    archive_type: ArchiveTypeRead
    internal_archive_type: str
    status: ArchiveStatusRead
    retention_period: RetentionPeriodRead
    department: DepartmentRead
    archive_medium: ArchiveMedium
    paper_copies: int
    archive_date: date | None
    paper_storage_location: str | None
    electronic_storage_path: str | None
    archiver_name: str | None
    owner_name: str | None
    archive_year: int | None
    security_level: str | None
    importance_level: str | None
    project_name: str | None
    related_party: str | None
    contract_no: str | None
    keywords: str | None
    remarks: str | None
    created_at: datetime
    updated_at: datetime


class ArchiveListResponse(BaseModel):
    items: list[ArchiveRead]
    total: int
    page: int
    page_size: int


class ArchivePayload(BaseModel):
    archive_no: str = Field(min_length=1, max_length=50)
    title: str = Field(min_length=1, max_length=255)
    archive_medium: ArchiveMedium = Field(pattern="^(paper|electronic)$")
    archive_type_id: int
    internal_archive_type: str = Field(min_length=1, max_length=100)
    status_id: int
    retention_period_id: int
    department_id: int
    paper_copies: int = Field(default=1, ge=0)
    archive_date: date | None = None
    paper_storage_location: str | None = Field(default=None, max_length=100)
    electronic_storage_path: str | None = Field(default=None, max_length=255)
    archiver_name: str | None = Field(default=None, max_length=100)
    owner_name: str | None = Field(default=None, max_length=100)
    archive_year: int | None = Field(default=None, ge=1900, le=2100)
    security_level: str | None = Field(default=None, max_length=50)
    importance_level: str | None = Field(default=None, max_length=50)
    project_name: str | None = Field(default=None, max_length=255)
    related_party: str | None = Field(default=None, max_length=255)
    contract_no: str | None = Field(default=None, max_length=100)
    keywords: str | None = Field(default=None, max_length=255)
    remarks: str | None = None

    @field_validator("internal_archive_type", mode="before")
    @classmethod
    def validate_internal_archive_type(cls, value: Any) -> str:
        if not isinstance(value, str):
            raise ValueError("内部档案类型不能为空")
        stripped = value.strip()
        if not stripped:
            raise ValueError("内部档案类型不能为空")
        return stripped


class SelectOption(BaseModel):
    id: int
    name: str
    code: str
    enabled: bool


class RetentionPeriodOption(BaseModel):
    id: int
    name: str
    years: int
    enabled: bool


class ArchiveOptionsResponse(BaseModel):
    archive_types: list[SelectOption]
    statuses: list[SelectOption]
    departments: list[SelectOption]
    retention_periods: list[RetentionPeriodOption]


class ArchiveBatchDeletePayload(BaseModel):
    archive_ids: list[int] = Field(min_length=1, max_length=100)
