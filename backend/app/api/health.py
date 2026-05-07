from datetime import UTC, datetime

from fastapi import APIRouter
from sqlalchemy import text

from app.core.config import settings
from app.core.responses import ApiResponse, ok
from app.db.session import engine

router = APIRouter(tags=["health"])


@router.get("/health", response_model=ApiResponse[dict[str, str]])
def health_check() -> ApiResponse[dict[str, str]]:
    database_status = "ok"

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception:
        database_status = "error"

    status = "ok" if database_status == "ok" else "degraded"

    return ok(
        {
            "service": settings.app_name,
            "status": status,
            "database": database_status,
            "version": settings.app_version,
            "timestamp": datetime.now(UTC).isoformat(),
        }
    )
