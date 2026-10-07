import secrets

from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.app.schemas.invitation import InvitationCreate

from src.app.repositories.invitation import (
    create_invitation,
    get_pending_invitation
)


ALLOWED_INVITATION_ROLES = {
    "COMPANY_ADMIN",
    "HR",
    "MANAGER",
    "EMPLOYEE"
}


INVITATION_EXPIRE_HOURS = 72


def create_invitation_service(
    db: Session,
    data: InvitationCreate,
    company_id: int
):
    role = data.role.upper()
    email = str(data.email).lower()

    if role not in ALLOWED_INVITATION_ROLES:
        raise HTTPException(
            status_code=400,
            detail="Invalid invitation role"
        )

    existing_invitation = get_pending_invitation(
        db,
        company_id,
        email,
        role
    )

    if existing_invitation:
        raise HTTPException(
            status_code=400,
            detail="A pending invitation already exists for this email and role"
        )

    invitation_code = secrets.token_urlsafe(48)

    expires_at = (
        datetime.now(timezone.utc)
        + timedelta(
            hours=INVITATION_EXPIRE_HOURS
        )
    )

    invitation = create_invitation(
        db=db,
        company_id=company_id,
        email=email,
        role=role,
        invitation_code=invitation_code,
        expires_at=expires_at
    )

    return {
        "invitation_id": invitation.id,
        "company_id": invitation.company_id,
        "email": invitation.email,
        "role": invitation.role,
        "status": invitation.status,
        "expires_at": invitation.expires_at,
        "invitation_token": invitation_code
    }