import hashlib
import secrets

from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.app.schemas.invitation import (
    InvitationCreate,
    InvitationAccept
)

from src.app.repositories.invitation import (
    create_invitation,
    get_pending_invitation,
    get_all_invitations,
    get_invitation_by_token_hash
)

from src.app.models.user import User

from src.app.core.security import hash_password


ALLOWED_INVITATION_ROLES = {
    "COMPANY_ADMIN",
    "HR",
    "MANAGER",
    "EMPLOYEE",
    "OWNER"
}


INVITATION_EXPIRE_HOURS = 72


def hash_invitation_token(
    token: str
) -> str:
    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()


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

    # Generate the raw token.
    invitation_token = secrets.token_urlsafe(48)

    # Store only the SHA-256 hash in the database.
    token_hash = hash_invitation_token(
        invitation_token
    )

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
        token_hash=token_hash,
        expires_at=expires_at
    )

    return {
        "invitation_id": invitation.id,
        "company_id": invitation.company_id,
        "email": invitation.email,
        "role": invitation.role,
        "status": invitation.status,
        "expires_at": invitation.expires_at,
        "invitation_token": invitation_token
    }


def get_all_invitations_service(
    db: Session,
    company_id: int
):
    return get_all_invitations(
        db,
        company_id
    )


def accept_invitation_service(
    db: Session,
    data: InvitationAccept
):
    # Hash the token received from the invited user.
    token_hash = hash_invitation_token(
        data.token
    )

    # Find the invitation using only the hash.
    invitation = get_invitation_by_token_hash(
        db,
        token_hash
    )

    if not invitation:
        raise HTTPException(
            status_code=400,
            detail="Invalid invitation token"
        )

    # An invitation can only be accepted once.
    if invitation.status != "PENDING":
        raise HTTPException(
            status_code=400,
            detail="Invitation is no longer valid"
        )

    # Database DateTime is stored without timezone information.
    current_time = datetime.now(
        timezone.utc
    ).replace(
        tzinfo=None
    )

    if invitation.expires_at <= current_time:
        invitation.status = "EXPIRED"

        db.commit()

        raise HTTPException(
            status_code=400,
            detail="Invitation has expired"
        )

    # Make sure this email does not already belong
    # to another user.
    existing_user = (
        db.query(User)
        .filter(
            User.email == invitation.email
        )
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="A user with this email already exists"
        )

    # Create the user's account using the
    # trusted information from the invitation.
    new_user = User(
        name=data.name,
        email=invitation.email,
        password_hash=hash_password(
            data.password
        ),
        role=invitation.role,
        company_id=invitation.company_id,
        is_active=True
    )

    db.add(new_user)

    # Mark invitation as used.
    invitation.status = "ACCEPTED"

    db.commit()
    db.refresh(new_user)

    return {
        "message": "Invitation accepted successfully",
        "user_id": new_user.id,
        "name": new_user.name,
        "email": new_user.email,
        "role": new_user.role,
        "company_id": new_user.company_id,
        "is_active": new_user.is_active
    }