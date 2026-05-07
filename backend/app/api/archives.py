from datetime import UTC, datetime
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload
from starlette import status

from app.api.deps import get_current_user, get_db, require_admin_user
from app.core.responses import ApiResponse, ok
from app.models import (
    Archive,
    ArchiveStatus,
    ArchiveType,
    Department,
    OperationLog,
    RetentionPeriod,
    User,
)
from app.schemas.archive import (
    ArchiveListResponse,
    ArchiveOptionsResponse,
    ArchivePayload,
    ArchiveRead,
    RetentionPeriodOption,
    SelectOption,
)

router = APIRouter(prefix="/archives", tags=["archives"])


def archive_query():
    return select(Archive).options(
        selectinload(Archive.archive_type),
        selectinload(Archive.status),
        selectinload(Archive.retention_period),
        selectinload(Archive.department),
    )


def normalize_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def archive_values(payload: ArchivePayload) -> dict[str, Any]:
    archive_year = payload.archive_year
    if archive_year is None and payload.archive_date is not None:
        archive_year = payload.archive_date.year

    return {
        "archive_no": payload.archive_no.strip(),
        "title": payload.title.strip(),
        "archive_type_id": payload.archive_type_id,
        "status_id": payload.status_id,
        "retention_period_id": payload.retention_period_id,
        "department_id": payload.department_id,
        "archive_date": payload.archive_date,
        "storage_location": normalize_optional_text(payload.storage_location),
        "owner_name": normalize_optional_text(payload.owner_name),
        "archive_year": archive_year,
        "security_level": normalize_optional_text(payload.security_level),
        "importance_level": normalize_optional_text(payload.importance_level),
        "project_name": normalize_optional_text(payload.project_name),
        "related_party": normalize_optional_text(payload.related_party),
        "contract_no": normalize_optional_text(payload.contract_no),
        "keywords": normalize_optional_text(payload.keywords),
        "remarks": normalize_optional_text(payload.remarks),
    }


def get_archive_or_404(db: Session, archive_id: int) -> Archive:
    archive = db.scalar(
        archive_query().where(
            Archive.id == archive_id,
            Archive.deleted_at.is_(None),
        )
    )
    if archive is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="档案不存在",
        )
    return archive


def ensure_archive_no_unique(
    db: Session,
    archive_no: str,
    exclude_archive_id: int | None = None,
) -> None:
    query = select(Archive).where(Archive.archive_no == archive_no.strip())
    if exclude_archive_id is not None:
        query = query.where(Archive.id != exclude_archive_id)

    duplicate = db.scalar(query)
    if duplicate is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="档案编号已存在",
        )


def ensure_lookup_exists(
    db: Session,
    model: type[Any],
    item_id: int,
    label: str,
    *,
    require_enabled: bool = False,
    allowed_disabled_id: int | None = None,
) -> None:
    item = db.get(model, item_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{label}不存在",
        )
    if (
        require_enabled
        and not item.enabled
        and item_id != allowed_disabled_id
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{label}已停用",
        )


def validate_archive_lookups(
    db: Session,
    payload: ArchivePayload,
    archive: Archive | None = None,
) -> None:
    ensure_lookup_exists(
        db,
        ArchiveType,
        payload.archive_type_id,
        "档案类型",
        require_enabled=True,
        allowed_disabled_id=archive.archive_type_id if archive else None,
    )
    ensure_lookup_exists(db, ArchiveStatus, payload.status_id, "档案状态")
    ensure_lookup_exists(
        db,
        RetentionPeriod,
        payload.retention_period_id,
        "保管期限",
        require_enabled=True,
        allowed_disabled_id=archive.retention_period_id if archive else None,
    )
    ensure_lookup_exists(db, Department, payload.department_id, "所属部门")


def write_archive_log(
    db: Session,
    *,
    operator: User,
    operation_type: str,
    archive: Archive,
    detail: str,
    request: Request,
) -> None:
    db.add(
        OperationLog(
            user_id=operator.id,
            module="档案管理",
            operation_type=operation_type,
            target_id=str(archive.id),
            target_name=archive.title,
            operation_detail=detail,
            ip_address=request.client.host if request.client else None,
        )
    )


@router.get("/options", response_model=ApiResponse[ArchiveOptionsResponse])
def get_archive_options(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> ApiResponse[ArchiveOptionsResponse]:
    archive_types = db.scalars(
        select(ArchiveType).order_by(ArchiveType.sort_order.asc(), ArchiveType.id.asc())
    ).all()
    statuses = db.scalars(
        select(ArchiveStatus).order_by(
            ArchiveStatus.sort_order.asc(),
            ArchiveStatus.id.asc(),
        )
    ).all()
    departments = db.scalars(
        select(Department).order_by(Department.sort_order.asc(), Department.id.asc())
    ).all()
    retention_periods = db.scalars(
        select(RetentionPeriod).order_by(
            RetentionPeriod.sort_order.asc(),
            RetentionPeriod.id.asc(),
        )
    ).all()

    return ok(
        ArchiveOptionsResponse(
            archive_types=[
                SelectOption(
                    id=item.id,
                    name=item.name,
                    code=item.code,
                    enabled=item.enabled,
                )
                for item in archive_types
            ],
            statuses=[
                SelectOption(
                    id=item.id,
                    name=item.name,
                    code=item.code,
                    enabled=item.enabled,
                )
                for item in statuses
            ],
            departments=[
                SelectOption(
                    id=item.id,
                    name=item.name,
                    code=item.code,
                    enabled=item.enabled,
                )
                for item in departments
            ],
            retention_periods=[
                RetentionPeriodOption(
                    id=item.id,
                    name=item.name,
                    years=item.years,
                    enabled=item.enabled,
                )
                for item in retention_periods
            ],
        )
    )


@router.get("", response_model=ApiResponse[ArchiveListResponse])
def list_archives(
    keyword: str | None = Query(default=None, max_length=100),
    archive_type_id: int | None = Query(default=None),
    department_id: int | None = Query(default=None),
    status_id: int | None = Query(default=None),
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 10,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> ApiResponse[ArchiveListResponse]:
    conditions = [Archive.deleted_at.is_(None)]
    if keyword and keyword.strip():
        keyword_like = f"%{keyword.strip()}%"
        conditions.append(
            or_(
                Archive.archive_no.ilike(keyword_like),
                Archive.title.ilike(keyword_like),
            )
        )
    if archive_type_id is not None:
        conditions.append(Archive.archive_type_id == archive_type_id)
    if department_id is not None:
        conditions.append(Archive.department_id == department_id)
    if status_id is not None:
        conditions.append(Archive.status_id == status_id)

    total = db.scalar(select(func.count()).select_from(Archive).where(*conditions))
    archives = db.scalars(
        archive_query()
        .where(*conditions)
        .order_by(Archive.archive_no.asc(), Archive.id.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    return ok(
        ArchiveListResponse(
            items=[ArchiveRead.model_validate(archive) for archive in archives],
            total=total or 0,
            page=page,
            page_size=page_size,
        )
    )


@router.get("/{archive_id}", response_model=ApiResponse[ArchiveRead])
def get_archive(
    archive_id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> ApiResponse[ArchiveRead]:
    return ok(ArchiveRead.model_validate(get_archive_or_404(db, archive_id)))


@router.post("", response_model=ApiResponse[ArchiveRead])
def create_archive(
    payload: ArchivePayload,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_user),
) -> ApiResponse[ArchiveRead]:
    values = archive_values(payload)
    ensure_archive_no_unique(db, values["archive_no"])
    validate_archive_lookups(db, payload)

    archive = Archive(
        **values,
        created_by=current_user.id,
        updated_by=current_user.id,
    )
    db.add(archive)
    db.flush()
    write_archive_log(
        db,
        operator=current_user,
        operation_type="新增档案",
        archive=archive,
        detail=f"新增档案 {archive.archive_no}",
        request=request,
    )
    db.commit()
    return ok(ArchiveRead.model_validate(get_archive_or_404(db, archive.id)))


@router.put("/{archive_id}", response_model=ApiResponse[ArchiveRead])
def update_archive(
    archive_id: int,
    payload: ArchivePayload,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_user),
) -> ApiResponse[ArchiveRead]:
    archive = get_archive_or_404(db, archive_id)
    values = archive_values(payload)
    ensure_archive_no_unique(db, values["archive_no"], exclude_archive_id=archive.id)
    validate_archive_lookups(db, payload, archive)

    for field, value in values.items():
        setattr(archive, field, value)
    archive.updated_by = current_user.id
    write_archive_log(
        db,
        operator=current_user,
        operation_type="编辑档案",
        archive=archive,
        detail=f"编辑档案 {archive.archive_no}",
        request=request,
    )
    db.commit()
    return ok(ArchiveRead.model_validate(get_archive_or_404(db, archive.id)))


@router.delete("/{archive_id}", response_model=ApiResponse[ArchiveRead])
def delete_archive(
    archive_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_user),
) -> ApiResponse[ArchiveRead]:
    archive = get_archive_or_404(db, archive_id)
    archive.deleted_at = datetime.now(UTC)
    archive.updated_by = current_user.id
    write_archive_log(
        db,
        operator=current_user,
        operation_type="软删除档案",
        archive=archive,
        detail=f"软删除档案 {archive.archive_no}",
        request=request,
    )
    archive_read = ArchiveRead.model_validate(archive)
    db.commit()
    return ok(archive_read)
