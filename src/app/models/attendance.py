
from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    CheckConstraint,
)
from sqlalchemy.orm import relationship

from src.app.db.database import Base


class Attendance(Base):
    __tablename__ = "attendance"

    __table_args__ = (
        UniqueConstraint(
            "employee_id",
            "attendance_date",
            name="uq_attendance_employee_date",
        ),
        CheckConstraint(
            "status IN ('PRESENT', 'ABSENT', 'HALF_DAY', 'ON_LEAVE')",
            name="ck_attendance_status",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)

    employee_id = Column(
        Integer,
        ForeignKey("employees.id"),
        nullable=False,
        index=True,
    )

    attendance_date = Column(Date, nullable=False, index=True)

    check_in = Column(DateTime(timezone=True), nullable=True)

    check_out = Column(DateTime(timezone=True), nullable=True)

    status = Column(
        String,
        nullable=False,
        default="PRESENT",
    )

    notes = Column(String, nullable=True)

    employee = relationship("Employee", back_populates="attendance")
