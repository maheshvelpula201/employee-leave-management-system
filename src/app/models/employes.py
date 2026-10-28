# src/app/models/employes.py

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.app.db.database import Base
# CRITICAL FIX: Import EmployeeHistory so SQLAlchemy registry can resolve the relationship string target
from src.app.models.employee_history import EmployeeHistory  # noqa: F401


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    department = Column(String, nullable=True)
    designation = Column(String, nullable=True)
    employment_status = Column(String, default="ACTIVE", nullable=False)
    phone = Column(String, nullable=True)
    joining_date = Column(DateTime, nullable=True, server_default=func.now())
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # Relationship back to history if defined in your model
    history = relationship("EmployeeHistory", back_populates="employee", cascade="all, delete-orphan")
    leaves = relationship("Leave", back_populates="employee")
    attendance = relationship("Attendance", back_populates="employee")