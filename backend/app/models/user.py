from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    real_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False)
    department_id: Mapped[int] = mapped_column(
        ForeignKey("departments.id"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="enabled")

    role = relationship("Role", back_populates="users")
    department = relationship("Department", back_populates="users")
    created_archives = relationship(
        "Archive",
        foreign_keys="Archive.created_by",
        back_populates="creator",
    )
    updated_archives = relationship(
        "Archive",
        foreign_keys="Archive.updated_by",
        back_populates="updater",
    )
    operation_logs = relationship("OperationLog", back_populates="user")
