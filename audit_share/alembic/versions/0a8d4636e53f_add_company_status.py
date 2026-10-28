"""add company status

Revision ID: 0a8d4636e53f
Revises: 5a8edf5606d0
Create Date: 2026-10-04 23:09:48.458235

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0a8d4636e53f"
down_revision: Union[str, Sequence[str], None] = "5a8edf5606d0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "companies",
        sa.Column(
            "status",
            sa.String(),
            nullable=False,
            server_default="PENDING"
        )
    )


def downgrade() -> None:
    op.drop_column(
        "companies",
        "status"
    )