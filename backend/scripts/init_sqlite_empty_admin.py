from __future__ import annotations

import os
import sys
from pathlib import Path

SQLITE_DB_PATH = Path(__file__).resolve().parents[1] / "data" / "archive_system.sqlite3"
SQLITE_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("DATABASE_URL", f"sqlite:///{SQLITE_DB_PATH.as_posix()}")

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from sqlalchemy import delete, select  # noqa: E402

from app.db.base import Base  # noqa: E402
from app.db.session import engine, SessionLocal  # noqa: E402
from app.models import Archive, Department, OperationLog, Role, User  # noqa: E402
from scripts.seed_data import pwd_context, seed_lookup_tables  # noqa: E402


def init_sqlite_empty_admin() -> None:
    admin_password = os.getenv("DEFAULT_ADMIN_PASSWORD", "Admin@123456")

    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        seed_lookup_tables(session)

        admin_role = session.scalar(select(Role).where(Role.code == "admin"))
        general_department = session.scalar(
            select(Department).where(Department.code == "ZHGL")
        )
        if admin_role is None:
            raise RuntimeError("管理员角色不存在，请检查基础字典初始化")
        if general_department is None:
            raise RuntimeError("综合管理部不存在，请检查部门字典初始化")

        session.execute(delete(OperationLog))
        session.execute(delete(Archive))
        session.execute(delete(User).where(User.username != "admin"))

        admin = session.scalar(select(User).where(User.username == "admin"))
        admin_values = {
            "username": "admin",
            "password_hash": pwd_context.hash(admin_password),
            "real_name": "admin",
            "email": "admin@company.com",
            "role_id": admin_role.id,
            "department_id": general_department.id,
            "status": "enabled",
        }
        if admin is None:
            session.add(User(**admin_values))
        else:
            for field, value in admin_values.items():
                setattr(admin, field, value)

        session.commit()

    print(f"SQLite 数据库：{SQLITE_DB_PATH}")
    print("数据库已初始化为空业务数据，仅保留 admin 管理员账号。")
    print("登录账号：admin")
    print(f"登录密码：{admin_password}")


if __name__ == "__main__":
    init_sqlite_empty_admin()
