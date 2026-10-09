"""replace invitation code with token hash

Revision ID: 71ff49a3865b
Revises: 484b71336201
Create Date: 2026-10-08

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "71ff49a3865b"

down_revision: Union[str, Sequence[str], None] = "484b71336201"

branch_labels: Union[str, Sequence[str], None] = None

depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column(
        "invitations",
        "invitation_code"
    )

    op.add_column(
        "invitations",
        sa.Column(
            "token_hash",
            sa.String(),
            nullable=False
        )
    )

    op.create_index(
        "ix_invitations_token_hash",
        "invitations",
        ["token_hash"],
        unique=True
    )


def downgrade() -> None:
    op.drop_index(
        "ix_invitations_token_hash",
        table_name="invitations"
    )

    op.drop_column(
        "invitations",
        "token_hash"
    )

    op.add_column(
        "invitations",
        sa.Column(
            "invitation_code",
            sa.String(),
            nullable=False
        )
    )