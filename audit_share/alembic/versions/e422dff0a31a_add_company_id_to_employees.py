"""Add company_id to employees

Revision ID: e422dff0a31a
Revises: 92b54de7fe68
Create Date: 2026-10-06 15:15:20.308371

"""
from alembic import op
import sqlalchemy as sa


revision = "e422dff0a31a"
down_revision = "92b54de7fe68"
branch_labels = None
depends_on = None


def upgrade():
    # 1. Add the column temporarily as nullable
    op.add_column(
        "employees",
        sa.Column(
            "company_id",
            sa.Integer(),
            nullable=True
        )
    )

    # 2. Assign existing employees to Company 2
    #    Company 2 is the TechNova company we created earlier.
    op.execute(
        """
        UPDATE employees
        SET company_id = 2
        WHERE company_id IS NULL
        """
    )

    # 3. Make the column required
    op.alter_column(
        "employees",
        "company_id",
        existing_type=sa.Integer(),
        nullable=False
    )

    # 4. Add the foreign key
    op.create_foreign_key(
        "fk_employees_company_id",
        "employees",
        "companies",
        ["company_id"],
        ["id"]
    )


def downgrade():
    op.drop_constraint(
        "fk_employees_company_id",
        "employees",
        type_="foreignkey"
    )

    op.drop_column(
        "employees",
        "company_id"
    )