"""replace invitation code with token hash

Revision ID: 484b71336201
Revises: 6078fb6149c4
Create Date: 2026-10-07 20:28:07.021277

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '484b71336201'
down_revision: Union[str, Sequence[str], None] = '6078fb6149c4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
