from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from src.app.db.database import Base


class HR(Base):
    __tablename__ = "hrs"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String,
        nullable=False
    )

    email = Column(
        String,
        unique=True,
        nullable=False,
        index=True
    )

    company_id = Column(
        Integer,
        ForeignKey("companies.id"),
        nullable=False
    )

    employees = relationship(
        "Employee",
        back_populates="hr"
    )

    company = relationship(
        "Company"
    )