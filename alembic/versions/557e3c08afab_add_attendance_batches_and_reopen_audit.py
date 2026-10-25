
"""add attendance batches and reopen audit

Revision ID: 557e3c08afab
Revises: b723a73bf755
Create Date: 2026-10-25 20:57:06.957741
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "557e3c08afab"
down_revision: Union[str, Sequence[str], None] = "b723a73bf755"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


attendance_status = postgresql.ENUM(
    "PRESENT",
    "ABSENT",
    "LATE",
    "HALF_DAY",
    "ON_LEAVE",
    "WORK_FROM_HOME",
    "HOLIDAY",
    "WEEK_OFF",
    name="attendance_status",
    create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()

    # Create the PostgreSQL enum if it does not already exist.
    attendance_status.create(bind, checkfirst=True)

    # Create upload batches.
    op.create_table(
        "attendance_batches",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("attendance_date", sa.Date(), nullable=False),
        sa.Column("scope_key", sa.String(length=255), nullable=False),
        sa.Column("department", sa.String(length=255), nullable=True),
        sa.Column("manager_employee_id", sa.Integer(), nullable=True),
        sa.Column("uploaded_by", sa.Integer(), nullable=False),
        sa.Column(
            "uploaded_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("closes_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reopened_by", sa.Integer(), nullable=True),
        sa.Column("reopened_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reopen_reason", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.ForeignKeyConstraint(["manager_employee_id"], ["employees.id"]),
        sa.ForeignKeyConstraint(["reopened_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["uploaded_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "company_id",
            "attendance_date",
            "scope_key",
            name="uq_attendance_batch_company_date_scope",
        ),
    )
    op.create_index(
        "ix_attendance_batch_date",
        "attendance_batches",
        ["attendance_date"],
    )
    op.create_index(
        "ix_attendance_batches_company_id",
        "attendance_batches",
        ["company_id"],
    )

    # Create correction history.
    op.create_table(
        "attendance_corrections",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("attendance_id", sa.Integer(), nullable=False),
        sa.Column("previous_status", attendance_status, nullable=False),
        sa.Column("new_status", attendance_status, nullable=False),
        sa.Column("changed_by", sa.Integer(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["attendance_id"],
            ["attendance.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["changed_by"], ["users.id"]),
    )
    op.create_index(
        "ix_attendance_corrections_attendance_id",
        "attendance_corrections",
        ["attendance_id"],
    )

    # Create reopen audit history.
    op.create_table(
        "attendance_reopen_audits",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("batch_id", sa.Integer(), nullable=False),
        sa.Column("authorized_by", sa.Integer(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["authorized_by"], ["users.id"]),
        sa.ForeignKeyConstraint(
            ["batch_id"],
            ["attendance_batches.id"],
            ondelete="CASCADE",
        ),
    )
    op.create_index(
        "ix_attendance_reopen_audits_batch_id",
        "attendance_reopen_audits",
        ["batch_id"],
    )

    # Remove the old status check before changing the status column type.
    op.drop_constraint(
        "ck_attendance_status",
        "attendance",
        type_="check",
    )

    # Add the new attendance columns.
    op.add_column(
        "attendance",
        sa.Column(
            "team_id",
            sa.Integer(),
            server_default="0",
            nullable=False,
        ),
    )
    op.add_column(
        "attendance",
        sa.Column("marked_by", sa.Integer(), nullable=True),
    )
    op.add_column(
        "attendance",
        sa.Column(
            "uploaded_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )
    op.add_column(
        "attendance",
        sa.Column(
            "closes_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )
    op.add_column(
        "attendance",
        sa.Column("last_updated_by", sa.Integer(), nullable=True),
    )
    op.add_column(
        "attendance",
        sa.Column("last_updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "attendance",
        sa.Column("correction_reason", sa.Text(), nullable=True),
    )
    op.add_column(
        "attendance",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.add_column(
        "attendance",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    # Convert status strings to the enum.
    op.alter_column(
        "attendance",
        "status",
        existing_type=sa.VARCHAR(),
        type_=attendance_status,
        postgresql_using="upper(status)::attendance_status",
        existing_nullable=False,
    )

    # Preserve the time portion of the existing timestamp columns.
    op.alter_column(
        "attendance",
        "check_in",
        existing_type=postgresql.TIMESTAMP(timezone=True),
        type_=sa.Time(),
        postgresql_using="check_in::time",
        existing_nullable=True,
    )
    op.alter_column(
        "attendance",
        "check_out",
        existing_type=postgresql.TIMESTAMP(timezone=True),
        type_=sa.Time(),
        postgresql_using="check_out::time",
        existing_nullable=True,
    )
    op.alter_column(
        "attendance",
        "notes",
        existing_type=sa.VARCHAR(),
        type_=sa.Text(),
        existing_nullable=True,
    )

    # Add foreign keys for the new audit columns.
    op.create_foreign_key(
        "fk_attendance_last_updated_by_users",
        "attendance",
        "users",
        ["last_updated_by"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_attendance_marked_by_users",
        "attendance",
        "users",
        ["marked_by"],
        ["id"],
    )

    # Replace attendance indexes without dropping the table.
    op.drop_index("ix_attendance_attendance_date", table_name="attendance")
    op.drop_index("ix_attendance_employee_id", table_name="attendance")

    op.create_index(
        "ix_attendance_date",
        "attendance",
        ["attendance_date"],
    )
    op.create_index(
        "ix_attendance_team_date",
        "attendance",
        ["team_id", "attendance_date"],
    )
    op.create_index(
        "ix_attendance_team_id",
        "attendance",
        ["team_id"],
    )

    # The table was verified empty. Make required upload metadata non-nullable.
    op.alter_column(
        "attendance",
        "marked_by",
        existing_type=sa.Integer(),
        nullable=False,
    )
    op.alter_column(
        "attendance",
        "uploaded_at",
        existing_type=sa.DateTime(timezone=True),
        nullable=False,
    )
    op.alter_column(
        "attendance",
        "closes_at",
        existing_type=sa.DateTime(timezone=True),
        nullable=False,
    )


def downgrade() -> None:
    # Restore the previous attendance indexes.
    op.drop_index("ix_attendance_team_id", table_name="attendance")
    op.drop_index("ix_attendance_team_date", table_name="attendance")
    op.drop_index("ix_attendance_date", table_name="attendance")

    op.create_index(
        "ix_attendance_employee_id",
        "attendance",
        ["employee_id"],
    )
    op.create_index(
        "ix_attendance_attendance_date",
        "attendance",
        ["attendance_date"],
    )

    # Remove new audit foreign keys.
    op.drop_constraint(
        "fk_attendance_marked_by_users",
        "attendance",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_attendance_last_updated_by_users",
        "attendance",
        type_="foreignkey",
    )

    # Restore the old column types.
    op.alter_column(
        "attendance",
        "notes",
        existing_type=sa.Text(),
        type_=sa.VARCHAR(),
        existing_nullable=True,
    )
    op.alter_column(
        "attendance",
        "check_out",
        existing_type=sa.Time(),
        type_=postgresql.TIMESTAMP(timezone=True),
        postgresql_using="(CURRENT_DATE + check_out)::timestamp AT TIME ZONE 'UTC'",
        existing_nullable=True,
    )
    op.alter_column(
        "attendance",
        "check_in",
        existing_type=sa.Time(),
        type_=postgresql.TIMESTAMP(timezone=True),
        postgresql_using="(CURRENT_DATE + check_in)::timestamp AT TIME ZONE 'UTC'",
        existing_nullable=True,
    )
    op.alter_column(
        "attendance",
        "status",
        existing_type=attendance_status,
        type_=sa.VARCHAR(),
        postgresql_using="status::text",
        existing_nullable=False,
    )

    # Restore the original status check.
    op.create_check_constraint(
        "ck_attendance_status",
        "attendance",
        "status IN ('PRESENT', 'ABSENT', 'HALF_DAY', 'ON_LEAVE')",
    )

    # Remove the columns added by this revision.
    op.drop_column("attendance", "updated_at")
    op.drop_column("attendance", "created_at")
    op.drop_column("attendance", "correction_reason")
    op.drop_column("attendance", "last_updated_at")
    op.drop_column("attendance", "last_updated_by")
    op.drop_column("attendance", "closes_at")
    op.drop_column("attendance", "uploaded_at")
    op.drop_column("attendance", "marked_by")
    op.drop_column("attendance", "team_id")

    # Remove new audit tables.
    op.drop_index(
        "ix_attendance_reopen_audits_batch_id",
        table_name="attendance_reopen_audits",
    )
    op.drop_table("attendance_reopen_audits")

    op.drop_index(
        "ix_attendance_corrections_attendance_id",
        table_name="attendance_corrections",
    )
    op.drop_table("attendance_corrections")

    op.drop_index(
        "ix_attendance_batches_company_id",
        table_name="attendance_batches",
    )
    op.drop_index(
        "ix_attendance_batch_date",
        table_name="attendance_batches",
    )
    op.drop_table("attendance_batches")

    # Remove the enum type after dependent tables and columns are gone.
    attendance_status.drop(op.get_bind(), checkfirst=True)
