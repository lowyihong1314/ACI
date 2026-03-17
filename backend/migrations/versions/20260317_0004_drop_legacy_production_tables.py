"""drop legacy production tables

Revision ID: 20260317_0004
Revises: 20260317_0003
Create Date: 2026-03-17 12:10:00
"""

from alembic import op
import sqlalchemy as sa
from datetime import datetime


revision = "20260317_0004"
down_revision = "20260317_0003"
branch_labels = None
depends_on = None


breakdown_reason_table = sa.table(
    "breakdown_reason",
    sa.column("name", sa.String()),
    sa.column("code", sa.String()),
    sa.column("is_active", sa.Boolean()),
    sa.column("display_order", sa.Integer()),
    sa.column("created_at", sa.DateTime()),
    sa.column("updated_at", sa.DateTime()),
)


def upgrade() -> None:
    op.drop_table("annual_machine_target")

    op.drop_table("daily_breakdown_record")

    op.drop_table("daily_production_record")

    op.drop_table("breakdown_reason")


def downgrade() -> None:
    op.create_table(
        "breakdown_reason",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("code", sa.String(length=40), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
    )
    op.create_index("ix_breakdown_reason_code", "breakdown_reason", ["code"], unique=False)

    op.create_table(
        "daily_production_record",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("record_date", sa.Date(), nullable=False),
        sa.Column("machine_id", sa.Integer(), nullable=False),
        sa.Column("actual_output_mt", sa.Numeric(12, 3), nullable=False, server_default="0"),
        sa.Column("target_output_mt", sa.Numeric(12, 3), nullable=False, server_default="0"),
        sa.Column("reject_qty_mt", sa.Numeric(12, 3), nullable=False, server_default="0"),
        sa.Column("available_hours", sa.Numeric(8, 2), nullable=False, server_default="0"),
        sa.Column("remarks", sa.Text(), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=False),
        sa.Column("updated_by", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["user_data.id"]),
        sa.ForeignKeyConstraint(["machine_id"], ["machine.id"]),
        sa.ForeignKeyConstraint(["updated_by"], ["user_data.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("record_date", "machine_id", name="uq_daily_production_record"),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
    )
    op.create_index("ix_daily_production_record_record_date", "daily_production_record", ["record_date"], unique=False)
    op.create_index("ix_daily_production_record_machine_id", "daily_production_record", ["machine_id"], unique=False)

    op.create_table(
        "daily_breakdown_record",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("record_date", sa.Date(), nullable=False),
        sa.Column("machine_id", sa.Integer(), nullable=False),
        sa.Column("breakdown_reason_id", sa.Integer(), nullable=False),
        sa.Column("downtime_hours", sa.Numeric(8, 2), nullable=False),
        sa.Column("remarks", sa.Text(), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=False),
        sa.Column("updated_by", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["breakdown_reason_id"], ["breakdown_reason.id"]),
        sa.ForeignKeyConstraint(["created_by"], ["user_data.id"]),
        sa.ForeignKeyConstraint(["machine_id"], ["machine.id"]),
        sa.ForeignKeyConstraint(["updated_by"], ["user_data.id"]),
        sa.PrimaryKeyConstraint("id"),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
    )
    op.create_index("ix_daily_breakdown_record_record_date", "daily_breakdown_record", ["record_date"], unique=False)
    op.create_index("ix_daily_breakdown_record_machine_id", "daily_breakdown_record", ["machine_id"], unique=False)
    op.create_index("ix_daily_breakdown_record_breakdown_reason_id", "daily_breakdown_record", ["breakdown_reason_id"], unique=False)

    op.create_table(
        "annual_machine_target",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("machine_id", sa.Integer(), nullable=False),
        sa.Column("annual_target_mt", sa.Numeric(12, 3), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["machine_id"], ["machine.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("year", "machine_id", name="uq_annual_machine_target"),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
    )
    op.create_index("ix_annual_machine_target_year", "annual_machine_target", ["year"], unique=False)
    op.create_index("ix_annual_machine_target_machine_id", "annual_machine_target", ["machine_id"], unique=False)

    now = datetime.utcnow()
    op.bulk_insert(
        breakdown_reason_table,
        [
            {"name": "Electric problem", "code": "ELECTRIC_PROBLEM", "is_active": True, "display_order": 10, "created_at": now, "updated_at": now},
            {"name": "Change raw material", "code": "CHANGE_RAW_MATERIAL", "is_active": True, "display_order": 20, "created_at": now, "updated_at": now},
            {"name": "Change die", "code": "CHANGE_DIE", "is_active": True, "display_order": 30, "created_at": now, "updated_at": now},
            {"name": "Machine breakdown", "code": "MACHINE_BREAKDOWN", "is_active": True, "display_order": 40, "created_at": now, "updated_at": now},
            {"name": "Management", "code": "MANAGEMENT", "is_active": True, "display_order": 50, "created_at": now, "updated_at": now},
            {"name": "External factor", "code": "EXTERNAL_FACTOR", "is_active": True, "display_order": 60, "created_at": now, "updated_at": now},
        ],
    )
