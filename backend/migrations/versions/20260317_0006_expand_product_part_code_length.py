"""expand product part code length

Revision ID: 20260317_0006
Revises: 20260317_0005
Create Date: 2026-03-17 13:32:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260317_0006"
down_revision = "20260317_0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "product",
        "part_code",
        existing_type=sa.String(length=40),
        type_=sa.String(length=120),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "product",
        "part_code",
        existing_type=sa.String(length=120),
        type_=sa.String(length=40),
        existing_nullable=False,
    )
