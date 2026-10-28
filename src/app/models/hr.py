# src/app/models/hr.py

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from src.app.db.database import Base


class HR(Base):
    __tablename__ = "hrs"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    company_id = Column(
        Integer,
        ForeignKey("companies.id"),
        nullable=False
    )

    name = Column(
        String,
        nullable=False
    )

    email = Column(
        String,
        unique=True,
        index=True,
        nullable=False
    )

    phone = Column(
        String,
        nullable=True
    )

    joining_date = Column(
        DateTime,
        nullable=True,
        server_default=func.now()
    )

    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now()
    )