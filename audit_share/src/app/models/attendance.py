
import enum
from datetime import date, datetime, time

from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Text,
    Time,
    UniqueConstraint,
    Index,
    func,
)
from sqlalchemy.orm import relationship

from src.app.db.database import Base


class AttendanceStatus(str, enum.Enum):
    PRESENT = "Present"
    ABSENT = "Absent"
    LATE = "Late"
    HALF_DAY = "Half-day"
    ON_LEAVE = "On leave"
    WORK_FROM_HOME = "Work from home"
    HOLIDAY = "Holiday"
    WEEK_OFF = "Week off"


class AttendanceBatch(Base):
    __tablename__ = "attendance_batches"

    __table_args__ = (
        UniqueConstraint(
            "company_id",
            "attendance_date",
            "scope_key",
            name="uq_attendance_batch_company_date_scope",
        ),
        Index("ix_attendance_batch_date", "attendance_date"),
    )

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(
        Integer,
        ForeignKey("companies.id"),
        nullable=False,
        index=True,
    )
    attendance_date = Column(Date, nullable=False)
    scope_key = Column(String(255), nullable=False)
    department = Column(String(255), nullable=True)
    manager_employee_id = Column(
        Integer,
        ForeignKey("employees.id"),
        nullable=True,
    )
    uploaded_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )
    uploaded_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    closes_at = Column(DateTime(timezone=True), nullable=False)
    reopened_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
    )
    reopened_at = Column(DateTime(timezone=True), nullable=True)
    reopen_reason = Column(Text, nullable=True)

    company = relationship("Company")
    manager = relationship("Employee", foreign_keys=[manager_employee_id])
    uploader = relationship("User", foreign_keys=[uploaded_by])


class Attendance(Base):
    __tablename__ = "attendance"

    __table_args__ = (
        UniqueConstraint(
            "employee_id",
            "attendance_date",
            name="uq_attendance_employee_date",
        ),
        Index("ix_attendance_date", "attendance_date"),
        Index("ix_attendance_team_date", "team_id", "attendance_date"),
    )

    id = Column(Integer, primary_key=True, index=True)

    employee_id = Column(
        Integer,
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Manager employee ID for a manager-led team; 0 for a department batch.
    team_id = Column(Integer, nullable=False, default=0, server_default="0")

    attendance_date = Column(Date, nullable=False)

    status = Column(
        Enum(AttendanceStatus, name="attendance_status"),
        nullable=False,
    )

    check_in = Column(Time, nullable=True)
    check_out = Column(Time, nullable=True)
    notes = Column(Text, nullable=True)

    marked_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    uploaded_at = Column(DateTime(timezone=True), nullable=False)
    closes_at = Column(DateTime(timezone=True), nullable=False)

    last_updated_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
    )
    last_updated_at = Column(DateTime(timezone=True), nullable=True)
    correction_reason = Column(Text, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    employee = relationship("Employee", back_populates="attendance")
    corrections = relationship(
        "AttendanceCorrection",
        back_populates="attendance",
        cascade="all, delete-orphan",
        order_by="AttendanceCorrection.created_at",
    )


class AttendanceCorrection(Base):
    __tablename__ = "attendance_corrections"

    id = Column(Integer, primary_key=True, index=True)
    attendance_id = Column(
        Integer,
        ForeignKey("attendance.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    previous_status = Column(
        Enum(AttendanceStatus, name="attendance_status", create_type=False),
        nullable=False,
    )
    new_status = Column(
        Enum(AttendanceStatus, name="attendance_status", create_type=False),
        nullable=False,
    )
    changed_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )
    reason = Column(Text, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    attendance = relationship("Attendance", back_populates="corrections")


class AttendanceReopenAudit(Base):
    __tablename__ = "attendance_reopen_audits"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(
        Integer,
        ForeignKey("attendance_batches.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    authorized_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )
    reason = Column(Text, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    batch = relationship("AttendanceBatch")
