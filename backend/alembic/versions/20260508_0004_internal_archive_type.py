"""add internal archive type

Revision ID: 20260508_0004
Revises: 20260508_0003
Create Date: 2026-05-08 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260508_0004"
down_revision: str | None = "20260508_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "archives",
        sa.Column("internal_archive_type", sa.String(length=100), nullable=True),
    )

    connection = op.get_bind()
    connection.execute(
        sa.text(
            """
            update archives
            set internal_archive_type = archive_types.name
            from archive_types
            where archives.archive_type_id = archive_types.id
              and archives.internal_archive_type is null
            """
        )
    )
    connection.execute(
        sa.text(
            """
            update archives
            set internal_archive_type = '未分类'
            where internal_archive_type is null
               or btrim(internal_archive_type) = ''
            """
        )
    )

    op.alter_column("archives", "internal_archive_type", nullable=False)
    op.create_index(
        "ix_archives_internal_archive_type",
        "archives",
        ["internal_archive_type"],
    )
    op.create_check_constraint(
        "ck_archives_internal_archive_type_not_blank",
        "archives",
        "btrim(internal_archive_type) <> ''",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_archives_internal_archive_type_not_blank",
        "archives",
        type_="check",
    )
    op.drop_index("ix_archives_internal_archive_type", table_name="archives")
    op.drop_column("archives", "internal_archive_type")
