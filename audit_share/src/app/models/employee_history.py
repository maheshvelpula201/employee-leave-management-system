from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from src.app.db.database import Base


class EmployeeHistory(Base):
    __tablename__ = "employee_history"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    employee_id = Column(
        Integer,
        ForeignKey("employees.id"),
        nullable=False
    )

    action = Column(
        String,
        nullable=False
    )

    old_value = Column(
        String,
        nullable=True
    )

    new_value = Column(
        String,
        nullable=True
    )

    changed_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now()
    )

    employee = relationship(
        "Employee",
        back_populates="history"
    )