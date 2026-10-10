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

    # Reusable invitation links do not require a predefined email.
    email = Column(
        String,
        nullable=True,
        index=True
    )

    # The role is fixed when the invitation is created.
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

    # NULL means unlimited uses.
    max_uses = Column(
        Integer,
        nullable=True
    )

    # Number of successful registrations through this link.
    uses_count = Column(
        Integer,
        nullable=False,
        default=0,
        server_default="0"
    )

    # User who generated the invitation.
    created_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    # Set when an administrator revokes the invitation.
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
