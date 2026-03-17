"""normalize machine codes for raw import

Revision ID: 20260317_0005
Revises: 20260317_0004
Create Date: 2026-03-17 13:10:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260317_0005"
down_revision = "20260317_0004"
branch_labels = None
depends_on = None


def _machine_exists(connection, code: str) -> bool:
    return connection.execute(
        sa.text("SELECT id FROM machine WHERE code = :code LIMIT 1"),
        {"code": code},
    ).fetchone() is not None


def upgrade() -> None:
    connection = op.get_bind()

    if _machine_exists(connection, "N530") and not _machine_exists(connection, "530C"):
        connection.execute(
            sa.text("UPDATE machine SET code = '530C', name = '530C' WHERE code = 'N530'")
        )
    elif _machine_exists(connection, "N530") and _machine_exists(connection, "530C"):
        connection.execute(sa.text("DELETE FROM machine WHERE code = 'N530'"))

    if _machine_exists(connection, "MANUAL_BAGGING") and not _machine_exists(connection, "MANUAL"):
        connection.execute(
            sa.text(
                "UPDATE machine SET code = 'MANUAL', name = 'Manual Keluli' "
                "WHERE code = 'MANUAL_BAGGING'"
            )
        )
    elif _machine_exists(connection, "MANUAL_BAGGING") and _machine_exists(connection, "MANUAL"):
        connection.execute(sa.text("DELETE FROM machine WHERE code = 'MANUAL_BAGGING'"))


def downgrade() -> None:
    connection = op.get_bind()

    if _machine_exists(connection, "530C") and not _machine_exists(connection, "N530"):
        connection.execute(
            sa.text("UPDATE machine SET code = 'N530', name = 'N530' WHERE code = '530C'")
        )

    if _machine_exists(connection, "MANUAL") and not _machine_exists(connection, "MANUAL_BAGGING"):
        connection.execute(
            sa.text(
                "UPDATE machine SET code = 'MANUAL_BAGGING', name = 'Manual bagging' "
                "WHERE code = 'MANUAL'"
            )
        )
