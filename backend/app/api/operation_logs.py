from datetime import UTC, date, datetime, time, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_db, require_admin_user
from app.core.responses import ApiResponse, ok
from app.models import OperationLog, User
from app.schemas.operation_log import OperationLogListResponse, OperationLogRead

router = APIRouter(prefix="/operation-logs", tags=["operation-logs"])


@router.get("", response_model=ApiResponse[OperationLogListResponse])
def list_operation_logs(
    keyword: str | None = Query(default=None, max_length=100),
    module: str | None = Query(default=None, max_length=100),
    operation_type: str | None = Query(default=None, max_length=100),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 10,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin_user),
) -> ApiResponse[OperationLogListResponse]:
    conditions = []
    if keyword and keyword.strip():
        keyword_like = f"%{keyword.strip()}%"
        conditions.append(
            or_(
                OperationLog.module.ilike(keyword_like),
                OperationLog.operation_type.ilike(keyword_like),
                OperationLog.target_id.ilike(keyword_like),
                OperationLog.target_name.ilike(keyword_like),
                OperationLog.operation_detail.ilike(keyword_like),
                OperationLog.ip_address.ilike(keyword_like),
                User.username.ilike(keyword_like),
                User.real_name.ilike(keyword_like),
            )
        )
    if module and module.strip():
        conditions.append(OperationLog.module == module.strip())
    if operation_type and operation_type.strip():
        conditions.append(OperationLog.operation_type == operation_type.strip())
    if date_from is not None:
        conditions.append(
            OperationLog.created_at
            >= datetime.combine(date_from, time.min, tzinfo=UTC)
        )
    if date_to is not None:
        end_date = datetime.combine(date_to, time.min, tzinfo=UTC) + timedelta(days=1)
        conditions.append(OperationLog.created_at < end_date)

    total = db.scalar(
        select(func.count())
        .select_from(OperationLog)
        .outerjoin(OperationLog.user)
        .where(*conditions)
    )
    logs = db.scalars(
        select(OperationLog)
        .outerjoin(OperationLog.user)
        .options(selectinload(OperationLog.user))
        .where(*conditions)
        .order_by(OperationLog.created_at.desc(), OperationLog.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    return ok(
        OperationLogListResponse(
            items=[OperationLogRead.model_validate(log) for log in logs],
            total=total or 0,
            page=page,
            page_size=page_size,
        )
    )
