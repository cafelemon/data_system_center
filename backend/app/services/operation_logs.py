from fastapi import Request
from sqlalchemy.orm import Session

from app.models import OperationLog, User


def write_operation_log(
    db: Session,
    *,
    module: str,
    operation_type: str,
    operator: User | None = None,
    target_id: str | None = None,
    target_name: str | None = None,
    detail: str | None = None,
    request: Request | None = None,
) -> None:
    db.add(
        OperationLog(
            user_id=operator.id if operator else None,
            module=module,
            operation_type=operation_type,
            target_id=target_id,
            target_name=target_name,
            operation_detail=detail,
            ip_address=request.client.host if request and request.client else None,
        )
    )
