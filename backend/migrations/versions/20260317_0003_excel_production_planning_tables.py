"""add excel production planning tables

Revision ID: 20260317_0003
Revises: 20260310_0002
Create Date: 2026-03-17 11:30:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260317_0003"
down_revision = "20260310_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "product",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("plant_id", sa.Integer(), nullable=True),
        sa.Column("part_code", sa.String(length=40), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=False),
        sa.Column("product_class", sa.String(length=40), nullable=True),
        sa.Column("warehouse_code", sa.String(length=40), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["plant_id"], ["plant.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("part_code"),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
    )
    op.create_index("ix_product_plant_id", "product", ["plant_id"], unique=False)
    op.create_index("ix_product_part_code", "product", ["part_code"], unique=False)
    op.create_index("ix_product_product_class", "product", ["product_class"], unique=False)
    op.create_index("ix_product_warehouse_code", "product", ["warehouse_code"], unique=False)

    op.create_table(
        "daily_product_tonnage",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("record_date", sa.Date(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("output_mt", sa.Numeric(12, 3), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["product.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("record_date", "product_id", name="uq_daily_product_tonnage"),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
    )
    op.create_index("ix_daily_product_tonnage_record_date", "daily_product_tonnage", ["record_date"], unique=False)
    op.create_index("ix_daily_product_tonnage_product_id", "daily_product_tonnage", ["product_id"], unique=False)

    op.create_table(
        "monthly_product_tonnage",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("month_start", sa.Date(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("output_mt", sa.Numeric(12, 3), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["product.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("month_start", "product_id", name="uq_monthly_product_tonnage"),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
    )
    op.create_index("ix_monthly_product_tonnage_month_start", "monthly_product_tonnage", ["month_start"], unique=False)
    op.create_index("ix_monthly_product_tonnage_product_id", "monthly_product_tonnage", ["product_id"], unique=False)

    op.create_table(
        "daily_machine_plan",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("plan_date", sa.Date(), nullable=False),
        sa.Column("machine_id", sa.Integer(), nullable=False),
        sa.Column("planned_output_mt", sa.Numeric(12, 3), nullable=False, server_default="0"),
        sa.Column("standard_output_mt", sa.Numeric(12, 3), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["machine_id"], ["machine.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("plan_date", "machine_id", name="uq_daily_machine_plan"),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
    )
    op.create_index("ix_daily_machine_plan_plan_date", "daily_machine_plan", ["plan_date"], unique=False)
    op.create_index("ix_daily_machine_plan_machine_id", "daily_machine_plan", ["machine_id"], unique=False)

    op.create_table(
        "monthly_machine_summary",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("month_start", sa.Date(), nullable=False),
        sa.Column("machine_id", sa.Integer(), nullable=False),
        sa.Column("actual_output_mt", sa.Numeric(12, 3), nullable=False, server_default="0"),
        sa.Column("rejected_output_mt", sa.Numeric(12, 3), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["machine_id"], ["machine.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("month_start", "machine_id", name="uq_monthly_machine_summary"),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
    )
    op.create_index("ix_monthly_machine_summary_month_start", "monthly_machine_summary", ["month_start"], unique=False)
    op.create_index("ix_monthly_machine_summary_machine_id", "monthly_machine_summary", ["machine_id"], unique=False)

    op.create_table(
        "monthly_efficiency_summary",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("scope_code", sa.String(length=40), nullable=False, server_default="OVERALL"),
        sa.Column("month_start", sa.Date(), nullable=False),
        sa.Column("planned_output_mt", sa.Numeric(12, 3), nullable=False, server_default="0"),
        sa.Column("actual_output_mt", sa.Numeric(12, 3), nullable=False, server_default="0"),
        sa.Column("efficiency_ratio", sa.Numeric(10, 6), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("scope_code", "month_start", name="uq_monthly_efficiency_summary"),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
    )
    op.create_index("ix_monthly_efficiency_summary_scope_code", "monthly_efficiency_summary", ["scope_code"], unique=False)
    op.create_index("ix_monthly_efficiency_summary_month_start", "monthly_efficiency_summary", ["month_start"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_monthly_efficiency_summary_month_start", table_name="monthly_efficiency_summary")
    op.drop_index("ix_monthly_efficiency_summary_scope_code", table_name="monthly_efficiency_summary")
    op.drop_table("monthly_efficiency_summary")

    op.drop_index("ix_monthly_machine_summary_machine_id", table_name="monthly_machine_summary")
    op.drop_index("ix_monthly_machine_summary_month_start", table_name="monthly_machine_summary")
    op.drop_table("monthly_machine_summary")

    op.drop_index("ix_daily_machine_plan_machine_id", table_name="daily_machine_plan")
    op.drop_index("ix_daily_machine_plan_plan_date", table_name="daily_machine_plan")
    op.drop_table("daily_machine_plan")

    op.drop_index("ix_monthly_product_tonnage_product_id", table_name="monthly_product_tonnage")
    op.drop_index("ix_monthly_product_tonnage_month_start", table_name="monthly_product_tonnage")
    op.drop_table("monthly_product_tonnage")

    op.drop_index("ix_daily_product_tonnage_product_id", table_name="daily_product_tonnage")
    op.drop_index("ix_daily_product_tonnage_record_date", table_name="daily_product_tonnage")
    op.drop_table("daily_product_tonnage")

    op.drop_index("ix_product_warehouse_code", table_name="product")
    op.drop_index("ix_product_product_class", table_name="product")
    op.drop_index("ix_product_part_code", table_name="product")
    op.drop_index("ix_product_plant_id", table_name="product")
    op.drop_table("product")
