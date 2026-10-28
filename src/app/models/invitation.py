# src/app/models/invitation.py

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

    # Optional targeted email binding. Nullable for reusable open links.
    email = Column(
        String,
        nullable=True,
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

    max_uses = Column(
        Integer,
        nullable=True
    )

    uses_count = Column(
        Integer,
        nullable=False,
        default=0,
        server_default="0"
    )

    created_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    revoked_at = Column(
        DateTime,
        nullable=True
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