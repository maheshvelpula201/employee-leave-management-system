from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship

from src.app.db.database import Base


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)

    email = Column(
        String,
        unique=True,
        nullable=False,
        index=True
    )

    department = Column(
        String,
        nullable=False
    )

    designation = Column(
        String,
        nullable=True
    )

    joining_date = Column(
        Date,
        nullable=True
    )

    leaving_date = Column(
        Date,
        nullable=True
    )

    termination_reason = Column(
        String,
        nullable=True
    )

    employment_status = Column(
        String,
        nullable=False,
        default="ACTIVE"
    )

    phone = Column(
        String,
        nullable=True
    )

    emergency_contact_name = Column(
        String,
        nullable=True
    )

    emergency_contact_phone = Column(
        String,
        nullable=True
    )

    manager_id = Column(
        Integer,
        ForeignKey("employees.id"),
        nullable=True
    )

    hr_id = Column(
        Integer,
        ForeignKey("hrs.id"),
        nullable=True
    )

    company_id = Column(
        Integer,
        ForeignKey("companies.id"),
        nullable=False
    )

    leaves = relationship(
        "Leave",
        back_populates="employee"
    )

    manager = relationship(
        "Employee",
        remote_side=[id],
        back_populates="team_members"
    )

    team_members = relationship(
        "Employee",
        back_populates="manager"
    )

    hr = relationship(
        "HR",
        back_populates="employees"
    )

    history = relationship(
        "EmployeeHistory",
        back_populates="employee"
    )

    company = relationship(
        "Company"
    )