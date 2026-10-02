from sqlalchemy import Column, Integer, String, ForeignKey
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

    department = Column(String, nullable=False)

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