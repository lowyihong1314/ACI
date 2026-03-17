"""product unique by part code and warehouse

Revision ID: 20260317_0007
Revises: 20260317_0006
Create Date: 2026-03-17 13:48:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260317_0007"
down_revision = "20260317_0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("part_code", "product", type_="unique")
    op.create_unique_constraint(
        "uq_product_part_code_warehouse",
        "product",
        ["part_code", "warehouse_code"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_product_part_code_warehouse", "product", type_="unique")
    op.create_unique_constraint("part_code", "product", ["part_code"])
