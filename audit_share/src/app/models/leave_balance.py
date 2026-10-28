from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from src.app.db.database import Base


class LeaveBalance(Base):
    __tablename__ = "leave_balances"

    id = Column(Integer, primary_key=True, index=True)

    employee_id = Column(
        Integer,
        ForeignKey("employees.id"),
        nullable=False
    )

    leave_type = Column(String, nullable=False)

    total_days = Column(Integer, nullable=False)

    used_days = Column(Integer, default=0, nullable=False)

    remaining_days = Column(Integer, nullable=False)

    employee = relationship("Employee")