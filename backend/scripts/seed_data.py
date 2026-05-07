from __future__ import annotations

import os
import sys
from datetime import date
from pathlib import Path
from typing import Any, TypeVar

from passlib.context import CryptContext
from sqlalchemy import func, select
from sqlalchemy.orm import Session

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.db.session import SessionLocal  # noqa: E402
from app.models import (  # noqa: E402
    Archive,
    ArchiveStatus,
    ArchiveType,
    Department,
    OperationLog,
    RetentionPeriod,
    Role,
    User,
)

ModelT = TypeVar("ModelT")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ROLES = [
    {"name": "管理员", "code": "admin", "enabled": True, "sort_order": 10},
    {"name": "普通用户", "code": "user", "enabled": True, "sort_order": 20},
    {"name": "管理层用户", "code": "manager", "enabled": True, "sort_order": 30},
]

DEPARTMENTS = [
    {"name": "信息中心", "code": "XXZX", "enabled": True, "sort_order": 10},
    {"name": "综合管理部", "code": "ZHGL", "enabled": True, "sort_order": 20},
    {"name": "技术研发部", "code": "JSYF", "enabled": True, "sort_order": 30},
    {"name": "质量体系部", "code": "ZLTX", "enabled": True, "sort_order": 40},
    {"name": "人力资源部", "code": "RLZY", "enabled": True, "sort_order": 50},
    {"name": "财务部", "code": "CWB", "enabled": True, "sort_order": 60},
    {"name": "财务管理部", "code": "CWGL", "enabled": True, "sort_order": 70},
    {"name": "市场营销部", "code": "SCYX", "enabled": True, "sort_order": 80},
    {"name": "行政部", "code": "XZB", "enabled": True, "sort_order": 90},
    {"name": "法务部", "code": "FWB", "enabled": True, "sort_order": 100},
    {"name": "生产部门", "code": "SCBM", "enabled": True, "sort_order": 110},
]

ARCHIVE_TYPES = [
    {"name": "文书档案", "code": "WS", "enabled": True, "sort_order": 10},
    {"name": "科技档案", "code": "KJ", "enabled": True, "sort_order": 20},
    {"name": "会计档案", "code": "KUAI", "enabled": True, "sort_order": 30},
    {"name": "财务档案", "code": "CW", "enabled": True, "sort_order": 40},
    {"name": "人事档案", "code": "RS", "enabled": False, "sort_order": 50},
    {"name": "声像档案", "code": "SX", "enabled": True, "sort_order": 60},
    {"name": "实物档案", "code": "SW", "enabled": True, "sort_order": 70},
    {"name": "合同档案", "code": "HT", "enabled": True, "sort_order": 80},
    {"name": "其他档案", "code": "QT", "enabled": True, "sort_order": 90},
]

ARCHIVE_STATUSES = [
    {"name": "在库", "code": "ZK", "enabled": True, "sort_order": 10},
    {"name": "借出", "code": "JC", "enabled": True, "sort_order": 20},
    {"name": "待归档", "code": "DGD", "enabled": True, "sort_order": 30},
    {"name": "待审核", "code": "DSH", "enabled": True, "sort_order": 40},
    {"name": "已归档", "code": "YGD", "enabled": True, "sort_order": 50},
    {"name": "已销毁", "code": "YXH", "enabled": True, "sort_order": 60},
]

RETENTION_PERIODS = [
    {"name": "永久", "years": 0, "enabled": True, "sort_order": 10},
    {"name": "30年", "years": 30, "enabled": True, "sort_order": 20},
    {"name": "10年", "years": 10, "enabled": True, "sort_order": 30},
    {"name": "5年", "years": 5, "enabled": True, "sort_order": 40},
    {"name": "其他", "years": -1, "enabled": True, "sort_order": 50},
]

USERS = [
    {
        "username": "admin",
        "real_name": "admin",
        "email": "admin@company.com",
        "role_code": "admin",
        "department_code": "XXZX",
        "status": "enabled",
        "is_admin": True,
    },
    {
        "username": "zhangsan",
        "real_name": "张三",
        "email": "zhangsan@company.com",
        "role_code": "user",
        "department_code": "ZLTX",
        "status": "enabled",
        "is_admin": False,
    },
    {
        "username": "lisi",
        "real_name": "李四",
        "email": "lisi@company.com",
        "role_code": "user",
        "department_code": "RLZY",
        "status": "enabled",
        "is_admin": False,
    },
    {
        "username": "wangwu",
        "real_name": "王五",
        "email": "wangwu@company.com",
        "role_code": "user",
        "department_code": "CWB",
        "status": "disabled",
        "is_admin": False,
    },
    {
        "username": "zhaoliu",
        "real_name": "赵六",
        "email": "zhaoliu@company.com",
        "role_code": "admin",
        "department_code": "XXZX",
        "status": "enabled",
        "is_admin": False,
    },
    {
        "username": "qianqi",
        "real_name": "钱七",
        "email": "qianqi@company.com",
        "role_code": "user",
        "department_code": "ZLTX",
        "status": "enabled",
        "is_admin": False,
    },
]

SCREENSHOT_ARCHIVES = [
    ("DA-2020-0001", "2024年度财务报表", "文书档案", "在库", "永久", "综合管理部", "2020-01-15", "A区-01柜", "张三"),
    ("DA-2020-0002", "产品研发技术文档", "科技档案", "已归档", "30年", "技术研发部", "2020-02-15", "B区-03柜", "李四"),
    ("DA-2020-0003", "员工入职档案-张三", "人事档案", "已销毁", "10年", "市场营销部", "2020-03-15", "C区-02柜", "王五"),
    ("DA-2020-0004", "采购合同-办公用品", "财务档案", "待审核", "永久", "财务管理部", "2020-04-15", "D区-05柜", "赵六"),
    ("DA-2020-0005", "会议纪要-2024Q1", "合同档案", "在库", "30年", "人力资源部", "2020-05-15", "E区-01柜", "钱七"),
    ("DA-2020-0006", "项目验收报告-A项目", "文书档案", "已归档", "10年", "综合管理部", "2020-06-15", "A区-01柜", "张三"),
    ("DA-2020-0007", "专利申请文件", "科技档案", "已销毁", "永久", "技术研发部", "2020-07-15", "B区-03柜", "李四"),
    ("DA-2020-0008", "年度审计报告", "人事档案", "待审核", "30年", "市场营销部", "2020-08-15", "C区-02柜", "王五"),
    ("DA-2020-0009", "客户合作协议", "财务档案", "在库", "10年", "财务管理部", "2020-09-15", "D区-05柜", "赵六"),
    ("DA-2020-0010", "设备采购清单", "合同档案", "已归档", "永久", "人力资源部", "2020-10-15", "E区-01柜", "钱七"),
]


def upsert_by_key(
    session: Session,
    model: type[ModelT],
    key_field: str,
    values: dict[str, Any],
) -> ModelT:
    key_value = values[key_field]
    instance = session.scalar(
        select(model).where(getattr(model, key_field) == key_value)
    )
    if instance is None:
        instance = model(**values)
        session.add(instance)
    else:
        for field, value in values.items():
            setattr(instance, field, value)
    return instance


def seed_lookup_tables(session: Session) -> None:
    for values in ROLES:
        upsert_by_key(session, Role, "code", values)
    for values in DEPARTMENTS:
        upsert_by_key(session, Department, "code", values)
    for values in ARCHIVE_TYPES:
        upsert_by_key(session, ArchiveType, "code", values)
    for values in ARCHIVE_STATUSES:
        upsert_by_key(session, ArchiveStatus, "code", values)
    for values in RETENTION_PERIODS:
        upsert_by_key(session, RetentionPeriod, "name", values)
    session.flush()


def seed_users(session: Session) -> None:
    admin_password = os.getenv("DEFAULT_ADMIN_PASSWORD", "Admin@123456")
    user_password = os.getenv("DEFAULT_USER_PASSWORD", "User@123456")

    role_by_code = {role.code: role for role in session.scalars(select(Role))}
    department_by_code = {
        department.code: department for department in session.scalars(select(Department))
    }

    for user in USERS:
        password = admin_password if user["is_admin"] else user_password
        values = {
            "username": user["username"],
            "password_hash": pwd_context.hash(password),
            "real_name": user["real_name"],
            "email": user["email"],
            "role_id": role_by_code[user["role_code"]].id,
            "department_id": department_by_code[user["department_code"]].id,
            "status": user["status"],
        }
        upsert_by_key(session, User, "username", values)
    session.flush()


def screenshot_archive_values(
    archive: tuple[str, str, str, str, str, str, str, str, str],
    lookups: dict[str, dict[str, Any]],
    admin_user: User,
) -> dict[str, Any]:
    (
        archive_no,
        title,
        archive_type,
        status,
        retention_period,
        department,
        archive_date,
        storage_location,
        owner_name,
    ) = archive
    parsed_date = date.fromisoformat(archive_date)
    return {
        "archive_no": archive_no,
        "title": title,
        "archive_type_id": lookups["archive_types"][archive_type].id,
        "status_id": lookups["statuses"][status].id,
        "retention_period_id": lookups["retention_periods"][retention_period].id,
        "department_id": lookups["departments"][department].id,
        "archive_date": parsed_date,
        "storage_location": storage_location,
        "owner_name": owner_name,
        "archive_year": parsed_date.year,
        "security_level": "内部",
        "importance_level": "普通",
        "project_name": None,
        "related_party": None,
        "contract_no": None,
        "keywords": title,
        "remarks": "截图示例数据",
        "created_by": admin_user.id,
        "updated_by": admin_user.id,
    }


def generated_archive_values(
    number: int,
    lookups: dict[str, dict[str, Any]],
    admin_user: User,
) -> dict[str, Any]:
    type_names = list(lookups["archive_types"].keys())
    status_names = list(lookups["statuses"].keys())
    retention_names = list(lookups["retention_periods"].keys())
    department_names = list(lookups["departments"].keys())
    storage_locations = ["A区-01柜", "B区-03柜", "C区-02柜", "D区-05柜", "E区-01柜"]
    owners = ["张三", "李四", "王五", "赵六", "钱七"]
    security_levels = ["公开", "内部", "秘密"]
    importance_levels = ["普通", "重要", "核心"]

    archive_type = type_names[number % len(type_names)]
    status = status_names[number % len(status_names)]
    retention_period = retention_names[number % len(retention_names)]
    department = department_names[number % len(department_names)]
    archive_date = date(2021 + number % 4, number % 12 + 1, number % 27 + 1)
    archive_no = f"DA-{archive_date.year}-{number:04d}"

    return {
        "archive_no": archive_no,
        "title": f"{archive_date.year}年度{department}档案资料-{number:04d}",
        "archive_type_id": lookups["archive_types"][archive_type].id,
        "status_id": lookups["statuses"][status].id,
        "retention_period_id": lookups["retention_periods"][retention_period].id,
        "department_id": lookups["departments"][department].id,
        "archive_date": archive_date,
        "storage_location": storage_locations[number % len(storage_locations)],
        "owner_name": owners[number % len(owners)],
        "archive_year": archive_date.year,
        "security_level": security_levels[number % len(security_levels)],
        "importance_level": importance_levels[number % len(importance_levels)],
        "project_name": f"演示项目-{number % 12 + 1:02d}",
        "related_party": f"合作单位-{number % 8 + 1:02d}",
        "contract_no": f"HT-{archive_date.year}-{number:04d}",
        "keywords": f"{department},{archive_type},{status}",
        "remarks": "P2 初始化演示数据",
        "created_by": admin_user.id,
        "updated_by": admin_user.id,
    }


def seed_archives(session: Session) -> None:
    lookups = {
        "archive_types": {item.name: item for item in session.scalars(select(ArchiveType))},
        "statuses": {item.name: item for item in session.scalars(select(ArchiveStatus))},
        "retention_periods": {
            item.name: item for item in session.scalars(select(RetentionPeriod))
        },
        "departments": {item.name: item for item in session.scalars(select(Department))},
    }
    admin_user = session.scalar(select(User).where(User.username == "admin"))
    if admin_user is None:
        raise RuntimeError("admin user is required before seeding archives")

    for archive in SCREENSHOT_ARCHIVES:
        upsert_by_key(
            session,
            Archive,
            "archive_no",
            screenshot_archive_values(archive, lookups, admin_user),
        )

    for number in range(11, 121):
        upsert_by_key(
            session,
            Archive,
            "archive_no",
            generated_archive_values(number, lookups, admin_user),
        )

    seed_log_exists = session.scalar(
        select(OperationLog.id).where(
            OperationLog.module == "seed",
            OperationLog.operation_type == "p2_seed_data",
        )
    )
    if seed_log_exists is None:
        session.add(
            OperationLog(
                user_id=admin_user.id,
                module="seed",
                operation_type="p2_seed_data",
                target_id="P2",
                target_name="核心数据初始化",
                operation_detail="初始化角色、部门、字典、用户和档案演示数据",
                ip_address="127.0.0.1",
            )
        )


def print_counts(session: Session) -> None:
    counts = {
        "roles": session.scalar(select(func.count()).select_from(Role)),
        "departments": session.scalar(select(func.count()).select_from(Department)),
        "users": session.scalar(select(func.count()).select_from(User)),
        "archive_types": session.scalar(select(func.count()).select_from(ArchiveType)),
        "archive_statuses": session.scalar(
            select(func.count()).select_from(ArchiveStatus)
        ),
        "retention_periods": session.scalar(
            select(func.count()).select_from(RetentionPeriod)
        ),
        "archives": session.scalar(select(func.count()).select_from(Archive)),
        "operation_logs": session.scalar(select(func.count()).select_from(OperationLog)),
    }

    for name, count in counts.items():
        print(f"{name}: {count}")


def main() -> None:
    with SessionLocal() as session:
        seed_lookup_tables(session)
        seed_users(session)
        seed_archives(session)
        session.commit()
        print_counts(session)


if __name__ == "__main__":
    main()
