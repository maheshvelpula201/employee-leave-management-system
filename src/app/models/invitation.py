from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func

from src.app.db.database import Base


class Invitation(Base):
    __tablename__ = "invitations"

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

    email = Column(
        String,
        nullable=False,
        index=True
    )

    role = Column(
        String,
        nullable=False
    )

    token_hash = Column(
        String,
        unique=True,
        nullable=False,
        index=True
    )

    status = Column(
        String,
        nullable=False,
        default="PENDING"
    )

    expires_at = Column(
        DateTime,
        nullable=False
    )

    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now()
    )