"""Add company_id to HRs

Revision ID: 6078fb6149c4
Revises: e422dff0a31a
Create Date: 2026-10-06 15:20:31.361118

"""
from alembic import op
import sqlalchemy as sa


revision = "6078fb6149c4"
down_revision = "e422dff0a31a"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "hrs",
        sa.Column(
            "company_id",
            sa.Integer(),
            nullable=True
        )
    )

    # Existing HR belongs to TechNova (company_id = 2)
    op.execute(
        """
        UPDATE hrs
        SET company_id = 2
        WHERE company_id IS NULL
        """
    )

    op.alter_column(
        "hrs",
        "company_id",
        existing_type=sa.Integer(),
        nullable=False
    )

    op.create_foreign_key(
        "fk_hrs_company_id",
        "hrs",
        "companies",
        ["company_id"],
        ["id"]
    )


def downgrade():
    op.drop_constraint(
        "fk_hrs_company_id",
        "hrs",
        type_="foreignkey"
    )

    op.drop_column(
        "hrs",
        "company_id"
    )