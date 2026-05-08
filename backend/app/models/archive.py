from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin


class Archive(TimestampMixin, Base):
    __tablename__ = "archives"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    archive_no: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    archive_type_id: Mapped[int] = mapped_column(
        ForeignKey("archive_types.id"),
        nullable=False,
    )
    internal_archive_type: Mapped[str] = mapped_column(String(100), nullable=False)
    status_id: Mapped[int] = mapped_column(
        ForeignKey("archive_statuses.id"),
        nullable=False,
    )
    retention_period_id: Mapped[int] = mapped_column(
        ForeignKey("retention_periods.id"),
        nullable=False,
    )
    department_id: Mapped[int] = mapped_column(
        ForeignKey("departments.id"),
        nullable=False,
    )
    archive_medium: Mapped[str] = mapped_column(String(20), nullable=False, default="paper")
    paper_copies: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    archive_date: Mapped[date | None] = mapped_column(Date)
    paper_storage_location: Mapped[str | None] = mapped_column(String(100))
    electronic_storage_path: Mapped[str | None] = mapped_column(String(255))
    archiver_name: Mapped[str | None] = mapped_column(String(100))
    owner_name: Mapped[str | None] = mapped_column(String(100))
    archive_year: Mapped[int | None] = mapped_column(Integer)
    security_level: Mapped[str | None] = mapped_column(String(50))
    importance_level: Mapped[str | None] = mapped_column(String(50))
    project_name: Mapped[str | None] = mapped_column(String(255))
    related_party: Mapped[str | None] = mapped_column(String(255))
    contract_no: Mapped[str | None] = mapped_column(String(100))
    keywords: Mapped[str | None] = mapped_column(String(255))
    remarks: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    updated_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    archive_type = relationship("ArchiveType", back_populates="archives")
    status = relationship("ArchiveStatus", back_populates="archives")
    retention_period = relationship("RetentionPeriod", back_populates="archives")
    department = relationship("Department", back_populates="archives")
    creator = relationship(
        "User",
        foreign_keys=[created_by],
        back_populates="created_archives",
    )
    updater = relationship(
        "User",
        foreign_keys=[updated_by],
        back_populates="updated_archives",
    )
