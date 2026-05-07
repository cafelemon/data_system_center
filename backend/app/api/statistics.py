from datetime import UTC, date, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.responses import ApiResponse, ok
from app.models import (
    Archive,
    ArchiveStatus,
    ArchiveType,
    Department,
    RetentionPeriod,
    User,
)
from app.schemas.statistics import (
    DepartmentRankingItem,
    DepartmentRankingResponse,
    DistributionItem,
    DistributionResponse,
    MonthlyTrendItem,
    MonthlyTrendResponse,
    StatisticsOverviewResponse,
)

router = APIRouter(prefix="/statistics", tags=["statistics"])


def add_years(value: date, years: int) -> date:
    try:
        return value.replace(year=value.year + years)
    except ValueError:
        return value.replace(month=2, day=28, year=value.year + years)


def add_months(value: date, months: int) -> date:
    month_index = value.month - 1 + months
    year = value.year + month_index // 12
    month = month_index % 12 + 1
    return date(year, month, 1)


def month_start(value: date) -> date:
    return date(value.year, value.month, 1)


def percentage(count: int, total: int) -> float:
    if total == 0:
        return 0.0
    return round(count * 100 / total, 1)


def total_archive_count(db: Session) -> int:
    return db.scalar(
        select(func.count()).select_from(Archive).where(Archive.deleted_at.is_(None))
    ) or 0


def count_by_archive_field(db: Session, field) -> dict[int, int]:
    rows = db.execute(
        select(field, func.count(Archive.id))
        .where(Archive.deleted_at.is_(None))
        .group_by(field)
    ).all()
    return {item_id: count for item_id, count in rows if item_id is not None}


def count_expiring_soon(db: Session, today: date, days: int = 90) -> int:
    deadline = today + timedelta(days=days)
    rows = db.execute(
        select(Archive.archive_date, RetentionPeriod.years)
        .join(RetentionPeriod, Archive.retention_period_id == RetentionPeriod.id)
        .where(
            Archive.deleted_at.is_(None),
            Archive.archive_date.is_not(None),
            RetentionPeriod.years > 0,
        )
    ).all()

    count = 0
    for archive_date, years in rows:
        expiry_date = add_years(archive_date, years)
        if today <= expiry_date <= deadline:
            count += 1
    return count


@router.get("/overview", response_model=ApiResponse[StatisticsOverviewResponse])
def get_statistics_overview(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> ApiResponse[StatisticsOverviewResponse]:
    today = date.today()
    current_month_start = datetime(today.year, today.month, 1, tzinfo=UTC)
    next_month_start = (
        datetime(today.year + 1, 1, 1, tzinfo=UTC)
        if today.month == 12
        else datetime(today.year, today.month + 1, 1, tzinfo=UTC)
    )

    total = total_archive_count(db)
    monthly_new = db.scalar(
        select(func.count())
        .select_from(Archive)
        .where(
            Archive.deleted_at.is_(None),
            Archive.created_at >= current_month_start,
            Archive.created_at < next_month_start,
        )
    ) or 0
    department_count = db.scalar(
        select(func.count(func.distinct(Archive.department_id))).where(
            Archive.deleted_at.is_(None)
        )
    ) or 0

    return ok(
        StatisticsOverviewResponse(
            total_archives=total,
            monthly_new=monthly_new,
            expiring_soon=count_expiring_soon(db, today),
            department_count=department_count,
        )
    )


@router.get("/status-distribution", response_model=ApiResponse[DistributionResponse])
def get_status_distribution(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> ApiResponse[DistributionResponse]:
    total = total_archive_count(db)
    counts = count_by_archive_field(db, Archive.status_id)
    statuses = db.scalars(
        select(ArchiveStatus).order_by(
            ArchiveStatus.sort_order.asc(),
            ArchiveStatus.id.asc(),
        )
    ).all()

    return ok(
        DistributionResponse(
            total=total,
            items=[
                DistributionItem(
                    id=item.id,
                    name=item.name,
                    code=item.code,
                    count=counts.get(item.id, 0),
                    percentage=percentage(counts.get(item.id, 0), total),
                )
                for item in statuses
            ],
        )
    )


@router.get("/type-distribution", response_model=ApiResponse[DistributionResponse])
def get_type_distribution(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> ApiResponse[DistributionResponse]:
    total = total_archive_count(db)
    counts = count_by_archive_field(db, Archive.archive_type_id)
    archive_types = db.scalars(
        select(ArchiveType).order_by(ArchiveType.sort_order.asc(), ArchiveType.id.asc())
    ).all()

    return ok(
        DistributionResponse(
            total=total,
            items=[
                DistributionItem(
                    id=item.id,
                    name=item.name,
                    code=item.code,
                    count=counts.get(item.id, 0),
                    percentage=percentage(counts.get(item.id, 0), total),
                )
                for item in archive_types
            ],
        )
    )


@router.get("/department-ranking", response_model=ApiResponse[DepartmentRankingResponse])
def get_department_ranking(
    limit: Annotated[int, Query(ge=1, le=20)] = 8,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> ApiResponse[DepartmentRankingResponse]:
    archive_count = func.count(Archive.id).label("archive_count")
    rows = db.execute(
        select(Department.id, Department.name, Department.code, archive_count)
        .join(Archive, Archive.department_id == Department.id)
        .where(Archive.deleted_at.is_(None))
        .group_by(Department.id, Department.name, Department.code, Department.sort_order)
        .order_by(archive_count.desc(), Department.sort_order.asc(), Department.id.asc())
        .limit(limit)
    ).all()

    return ok(
        DepartmentRankingResponse(
            items=[
                DepartmentRankingItem(
                    id=item.id,
                    name=item.name,
                    code=item.code,
                    count=item.archive_count,
                )
                for item in rows
            ]
        )
    )


@router.get("/monthly-trend", response_model=ApiResponse[MonthlyTrendResponse])
def get_monthly_trend(
    months: Annotated[int, Query(ge=1, le=36)] = 12,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> ApiResponse[MonthlyTrendResponse]:
    max_archive_date = db.scalar(
        select(func.max(Archive.archive_date)).where(
            Archive.deleted_at.is_(None),
            Archive.archive_date.is_not(None),
        )
    )
    end_month = month_start(max_archive_date or date.today())
    start_month = add_months(end_month, -(months - 1))
    end_exclusive = add_months(end_month, 1)

    rows = db.execute(
        select(Archive.archive_date)
        .where(
            Archive.deleted_at.is_(None),
            Archive.archive_date >= start_month,
            Archive.archive_date < end_exclusive,
        )
    ).all()
    counts: dict[str, int] = {}
    for (archive_date,) in rows:
        key = archive_date.strftime("%Y-%m")
        counts[key] = counts.get(key, 0) + 1

    items = []
    for index in range(months):
        month = add_months(start_month, index).strftime("%Y-%m")
        items.append(MonthlyTrendItem(month=month, count=counts.get(month, 0)))

    return ok(MonthlyTrendResponse(items=items))
