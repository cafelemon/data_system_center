from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session
from starlette import status

from app.api.deps import get_db, require_admin_user
from app.core.responses import ApiResponse, ok
from app.models import Archive, ArchiveType, OperationLog, RetentionPeriod, User
from app.schemas.settings import (
    ArchiveTypeListResponse,
    ArchiveTypePayload,
    ArchiveTypeRead,
    EnabledUpdate,
    RetentionPeriodListResponse,
    RetentionPeriodPayload,
    RetentionPeriodRead,
)

router = APIRouter(prefix="/settings", tags=["settings"])


def normalize_required_text(value: str, label: str) -> str:
    stripped = value.strip()
    if not stripped:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{label}不能为空",
        )
    return stripped


def next_sort_order(db: Session, model: type[Any]) -> int:
    current_max = db.scalar(select(func.max(model.sort_order)))
    return (current_max or 0) + 10


def write_settings_log(
    db: Session,
    *,
    operator: User,
    operation_type: str,
    target_id: int,
    target_name: str,
    detail: str,
    request: Request,
) -> None:
    db.add(
        OperationLog(
            user_id=operator.id,
            module="系统设置",
            operation_type=operation_type,
            target_id=str(target_id),
            target_name=target_name,
            operation_detail=detail,
            ip_address=request.client.host if request.client else None,
        )
    )


def ensure_unique_archive_type(
    db: Session,
    *,
    name: str,
    code: str,
    exclude_id: int | None = None,
) -> None:
    query = select(ArchiveType).where(
        or_(ArchiveType.name == name, ArchiveType.code == code)
    )
    if exclude_id is not None:
        query = query.where(ArchiveType.id != exclude_id)

    duplicate = db.scalar(query)
    if duplicate is not None:
        field = "类型名称" if duplicate.name == name else "编码值"
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{field}已存在",
        )


def ensure_unique_retention_period(
    db: Session,
    *,
    name: str,
    exclude_id: int | None = None,
) -> None:
    query = select(RetentionPeriod).where(RetentionPeriod.name == name)
    if exclude_id is not None:
        query = query.where(RetentionPeriod.id != exclude_id)

    duplicate = db.scalar(query)
    if duplicate is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="期限名称已存在",
        )


def get_archive_type_or_404(db: Session, archive_type_id: int) -> ArchiveType:
    item = db.get(ArchiveType, archive_type_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="档案类型不存在",
        )
    return item


def get_retention_period_or_404(
    db: Session,
    retention_period_id: int,
) -> RetentionPeriod:
    item = db.get(RetentionPeriod, retention_period_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="保管期限不存在",
        )
    return item


@router.get("/archive-types", response_model=ApiResponse[ArchiveTypeListResponse])
def list_archive_types(
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin_user),
) -> ApiResponse[ArchiveTypeListResponse]:
    items = db.scalars(
        select(ArchiveType).order_by(ArchiveType.sort_order.asc(), ArchiveType.id.asc())
    ).all()
    return ok(
        ArchiveTypeListResponse(
            items=[ArchiveTypeRead.model_validate(item) for item in items]
        )
    )


@router.post("/archive-types", response_model=ApiResponse[ArchiveTypeRead])
def create_archive_type(
    payload: ArchiveTypePayload,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_user),
) -> ApiResponse[ArchiveTypeRead]:
    name = normalize_required_text(payload.name, "类型名称")
    code = normalize_required_text(payload.code, "编码值")
    ensure_unique_archive_type(db, name=name, code=code)

    item = ArchiveType(
        name=name,
        code=code,
        enabled=payload.enabled,
        sort_order=payload.sort_order
        if payload.sort_order is not None
        else next_sort_order(db, ArchiveType),
    )
    db.add(item)
    db.flush()
    write_settings_log(
        db,
        operator=current_user,
        operation_type="新增档案类型",
        target_id=item.id,
        target_name=item.name,
        detail=f"新增档案类型 {item.name}",
        request=request,
    )
    db.commit()
    db.refresh(item)
    return ok(ArchiveTypeRead.model_validate(item))


@router.put("/archive-types/{archive_type_id}", response_model=ApiResponse[ArchiveTypeRead])
def update_archive_type(
    archive_type_id: int,
    payload: ArchiveTypePayload,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_user),
) -> ApiResponse[ArchiveTypeRead]:
    item = get_archive_type_or_404(db, archive_type_id)
    name = normalize_required_text(payload.name, "类型名称")
    code = normalize_required_text(payload.code, "编码值")
    ensure_unique_archive_type(db, name=name, code=code, exclude_id=item.id)

    item.name = name
    item.code = code
    item.enabled = payload.enabled
    if payload.sort_order is not None:
        item.sort_order = payload.sort_order
    write_settings_log(
        db,
        operator=current_user,
        operation_type="编辑档案类型",
        target_id=item.id,
        target_name=item.name,
        detail=f"编辑档案类型 {item.name}",
        request=request,
    )
    db.commit()
    db.refresh(item)
    return ok(ArchiveTypeRead.model_validate(item))


@router.patch(
    "/archive-types/{archive_type_id}/status",
    response_model=ApiResponse[ArchiveTypeRead],
)
def update_archive_type_status(
    archive_type_id: int,
    payload: EnabledUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_user),
) -> ApiResponse[ArchiveTypeRead]:
    item = get_archive_type_or_404(db, archive_type_id)
    item.enabled = payload.enabled
    write_settings_log(
        db,
        operator=current_user,
        operation_type="调整档案类型状态",
        target_id=item.id,
        target_name=item.name,
        detail=f"将档案类型 {item.name} 状态调整为 {payload.enabled}",
        request=request,
    )
    db.commit()
    db.refresh(item)
    return ok(ArchiveTypeRead.model_validate(item))


@router.delete("/archive-types/{archive_type_id}", response_model=ApiResponse[ArchiveTypeRead])
def delete_archive_type(
    archive_type_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_user),
) -> ApiResponse[ArchiveTypeRead]:
    item = get_archive_type_or_404(db, archive_type_id)
    referenced = db.scalar(
        select(func.count()).select_from(Archive).where(Archive.archive_type_id == item.id)
    )
    if referenced:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="该档案类型已被档案引用，不能删除",
        )

    item_read = ArchiveTypeRead.model_validate(item)
    write_settings_log(
        db,
        operator=current_user,
        operation_type="删除档案类型",
        target_id=item.id,
        target_name=item.name,
        detail=f"删除档案类型 {item.name}",
        request=request,
    )
    db.delete(item)
    db.commit()
    return ok(item_read)


@router.get(
    "/retention-periods",
    response_model=ApiResponse[RetentionPeriodListResponse],
)
def list_retention_periods(
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin_user),
) -> ApiResponse[RetentionPeriodListResponse]:
    items = db.scalars(
        select(RetentionPeriod).order_by(
            RetentionPeriod.sort_order.asc(),
            RetentionPeriod.id.asc(),
        )
    ).all()
    return ok(
        RetentionPeriodListResponse(
            items=[RetentionPeriodRead.model_validate(item) for item in items]
        )
    )


@router.post("/retention-periods", response_model=ApiResponse[RetentionPeriodRead])
def create_retention_period(
    payload: RetentionPeriodPayload,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_user),
) -> ApiResponse[RetentionPeriodRead]:
    name = normalize_required_text(payload.name, "期限名称")
    ensure_unique_retention_period(db, name=name)

    item = RetentionPeriod(
        name=name,
        years=payload.years,
        enabled=payload.enabled,
        sort_order=payload.sort_order
        if payload.sort_order is not None
        else next_sort_order(db, RetentionPeriod),
    )
    db.add(item)
    db.flush()
    write_settings_log(
        db,
        operator=current_user,
        operation_type="新增保管期限",
        target_id=item.id,
        target_name=item.name,
        detail=f"新增保管期限 {item.name}",
        request=request,
    )
    db.commit()
    db.refresh(item)
    return ok(RetentionPeriodRead.model_validate(item))


@router.put(
    "/retention-periods/{retention_period_id}",
    response_model=ApiResponse[RetentionPeriodRead],
)
def update_retention_period(
    retention_period_id: int,
    payload: RetentionPeriodPayload,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_user),
) -> ApiResponse[RetentionPeriodRead]:
    item = get_retention_period_or_404(db, retention_period_id)
    name = normalize_required_text(payload.name, "期限名称")
    ensure_unique_retention_period(db, name=name, exclude_id=item.id)

    item.name = name
    item.years = payload.years
    item.enabled = payload.enabled
    if payload.sort_order is not None:
        item.sort_order = payload.sort_order
    write_settings_log(
        db,
        operator=current_user,
        operation_type="编辑保管期限",
        target_id=item.id,
        target_name=item.name,
        detail=f"编辑保管期限 {item.name}",
        request=request,
    )
    db.commit()
    db.refresh(item)
    return ok(RetentionPeriodRead.model_validate(item))


@router.patch(
    "/retention-periods/{retention_period_id}/status",
    response_model=ApiResponse[RetentionPeriodRead],
)
def update_retention_period_status(
    retention_period_id: int,
    payload: EnabledUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_user),
) -> ApiResponse[RetentionPeriodRead]:
    item = get_retention_period_or_404(db, retention_period_id)
    item.enabled = payload.enabled
    write_settings_log(
        db,
        operator=current_user,
        operation_type="调整保管期限状态",
        target_id=item.id,
        target_name=item.name,
        detail=f"将保管期限 {item.name} 状态调整为 {payload.enabled}",
        request=request,
    )
    db.commit()
    db.refresh(item)
    return ok(RetentionPeriodRead.model_validate(item))


@router.delete(
    "/retention-periods/{retention_period_id}",
    response_model=ApiResponse[RetentionPeriodRead],
)
def delete_retention_period(
    retention_period_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_user),
) -> ApiResponse[RetentionPeriodRead]:
    item = get_retention_period_or_404(db, retention_period_id)
    referenced = db.scalar(
        select(func.count())
        .select_from(Archive)
        .where(Archive.retention_period_id == item.id)
    )
    if referenced:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="该保管期限已被档案引用，不能删除",
        )

    item_read = RetentionPeriodRead.model_validate(item)
    write_settings_log(
        db,
        operator=current_user,
        operation_type="删除保管期限",
        target_id=item.id,
        target_name=item.name,
        detail=f"删除保管期限 {item.name}",
        request=request,
    )
    db.delete(item)
    db.commit()
    return ok(item_read)
