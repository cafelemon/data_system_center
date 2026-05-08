"""archive dual ledger fields

Revision ID: 20260508_0003
Revises: 20260505_0002
Create Date: 2026-05-08 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260508_0003"
down_revision: str | None = "20260505_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

NEW_DEPARTMENTS = [
    ("董事会办公室", "DSHBGS"),
    ("综合管理部", "ZHGL"),
    ("北京公司", "BJGS"),
    ("投资者关系部", "TZZGX"),
    ("财务与资产管理部", "CWZC"),
    ("组织与人才发展中心", "ZZRC"),
    ("研发中心", "YFZX"),
    ("生产中心", "SCZX"),
    ("客户服务中心", "KHFW"),
    ("数字与信息中心", "SZXX"),
    ("质量体系部", "ZLTX"),
    ("临床与注册事务部", "LCZC"),
    ("工程管理部", "GCGL"),
    ("发展规划部", "FZGH"),
    ("监察审计室", "JCSJ"),
]
NEW_DEPARTMENT_NAMES = [name for name, _code in NEW_DEPARTMENTS]
NEW_DEPARTMENT_CODES = [code for _name, code in NEW_DEPARTMENTS]


def upgrade() -> None:
    op.add_column(
        "archives",
        sa.Column(
            "archive_medium",
            sa.String(length=20),
            nullable=False,
            server_default="paper",
        ),
    )
    op.add_column(
        "archives",
        sa.Column("paper_copies", sa.Integer(), nullable=False, server_default="1"),
    )
    op.add_column("archives", sa.Column("archiver_name", sa.String(length=100)))
    op.create_check_constraint(
        "ck_archives_archive_medium",
        "archives",
        "archive_medium in ('paper', 'electronic')",
    )
    op.create_check_constraint(
        "ck_archives_paper_copies_non_negative",
        "archives",
        "paper_copies >= 0",
    )
    op.drop_index("ix_archives_storage_location", table_name="archives")
    op.alter_column(
        "archives",
        "storage_location",
        new_column_name="paper_storage_location",
        existing_type=sa.String(length=100),
        existing_nullable=True,
    )
    op.add_column("archives", sa.Column("electronic_storage_path", sa.String(length=255)))
    op.create_index("ix_archives_archive_medium", "archives", ["archive_medium"])
    op.create_index(
        "ix_archives_paper_storage_location",
        "archives",
        ["paper_storage_location"],
    )
    op.create_index(
        "ix_archives_electronic_storage_path",
        "archives",
        ["electronic_storage_path"],
    )

    connection = op.get_bind()
    connection.execute(
        sa.text(
            """
            update departments
            set code = concat(code, '_OLD_', id), updated_at = now()
            where name not in :new_names and code in :new_codes
            """
        ).bindparams(
            sa.bindparam("new_names", expanding=True),
            sa.bindparam("new_codes", expanding=True),
        ),
        {"new_names": NEW_DEPARTMENT_NAMES, "new_codes": NEW_DEPARTMENT_CODES},
    )
    for index, (name, code) in enumerate(NEW_DEPARTMENTS, start=1):
        existing = connection.execute(
            sa.text("select id from departments where name = :name"),
            {"name": name},
        ).first()
        if existing:
            connection.execute(
                sa.text(
                    """
                    update departments
                    set code = :code,
                        enabled = true,
                        sort_order = :sort_order,
                        updated_at = now()
                    where id = :id
                    """
                ),
                {"id": existing.id, "code": code, "sort_order": index * 10},
            )
        else:
            connection.execute(
                sa.text(
                    """
                    insert into departments
                        (name, code, enabled, sort_order, created_at, updated_at)
                    values
                        (:name, :code, true, :sort_order, now(), now())
                    """
                ),
                {"name": name, "code": code, "sort_order": index * 10},
            )

    general_department_id = connection.execute(
        sa.text("select id from departments where name = '综合管理部'")
    ).scalar_one()
    connection.execute(
        sa.text("update users set department_id = :department_id"),
        {"department_id": general_department_id},
    )
    connection.execute(
        sa.text("update archives set department_id = :department_id"),
        {"department_id": general_department_id},
    )
    connection.execute(
        sa.text(
            """
            update departments
            set enabled = false
            """
        )
    )
    for name, _code in NEW_DEPARTMENTS:
        connection.execute(
            sa.text(
                """
                update departments
                set enabled = true, updated_at = now()
                where name = :name
                """
            ),
            {"name": name},
        )

    op.alter_column("archives", "archive_medium", server_default=None)
    op.alter_column("archives", "paper_copies", server_default=None)


def downgrade() -> None:
    op.drop_index("ix_archives_electronic_storage_path", table_name="archives")
    op.drop_index("ix_archives_paper_storage_location", table_name="archives")
    op.drop_index("ix_archives_archive_medium", table_name="archives")
    op.drop_column("archives", "electronic_storage_path")
    op.alter_column(
        "archives",
        "paper_storage_location",
        new_column_name="storage_location",
        existing_type=sa.String(length=100),
        existing_nullable=True,
    )
    op.create_index("ix_archives_storage_location", "archives", ["storage_location"])
    op.drop_constraint(
        "ck_archives_paper_copies_non_negative",
        "archives",
        type_="check",
    )
    op.drop_constraint("ck_archives_archive_medium", "archives", type_="check")
    op.drop_column("archives", "archiver_name")
    op.drop_column("archives", "paper_copies")
    op.drop_column("archives", "archive_medium")
