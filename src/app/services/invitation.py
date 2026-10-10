import hashlib
import secrets

from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.app.schemas.invitation import (
    InvitationCreate,
    InvitationAccept,
)

from src.app.repositories.invitation import (
    create_invitation,
    get_all_invitations,
    get_invitation_by_token_hash,
)

from src.app.models.invitation import Invitation
from src.app.models.user import User

from src.app.core.security import hash_password


ALLOWED_INVITATION_ROLES = {
    "COMPANY_ADMIN",
    "HR",
    "MANAGER",
    "EMPLOYEE",
    "OWNER",
}


def hash_invitation_token(token: str) -> str:
    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()


def utc_now_naive() -> datetime:
    # Database columns currently use timezone-naive DateTime.
    return datetime.now(timezone.utc).replace(tzinfo=None)


def create_invitation_service(
    db: Session,
    data: InvitationCreate,
    company_id: int,
    created_by: int | None = None,
):
    role = data.role.strip().upper()

    if role not in ALLOWED_INVITATION_ROLES:
        raise HTTPException(
            status_code=400,
            detail="Invalid invitation role",
        )

    # Don't allow privileged roles to be granted by ordinary operators.
    # Additional creator-role authorization must also be enforced by RBAC.
    if role in {"OWNER", "COMPANY_ADMIN"}:
        raise HTTPException(
            status_code=403,
            detail="Creating invitations for this role is not allowed here",
        )

    invitation_token = secrets.token_urlsafe(48)
    token_hash = hash_invitation_token(invitation_token)

    expires_at = utc_now_naive() + timedelta(
        days=data.expires_in_days
    )

    try:
        invitation = create_invitation(
            db=db,
            company_id=company_id,
            role=role,
            token_hash=token_hash,
            expires_at=expires_at,
            max_uses=data.max_uses,
            created_by=created_by,
        )

        db.commit()
        db.refresh(invitation)

    except Exception:
        db.rollback()
        raise

    return {
        "invitation_id": invitation.id,
        "company_id": invitation.company_id,
        "role": invitation.role,
        "status": invitation.status,
        "max_uses": invitation.max_uses,
        "uses_count": invitation.uses_count,
        "expires_at": invitation.expires_at,
        "invitation_token": invitation_token,
    }


def get_all_invitations_service(
    db: Session,
    company_id: int,
):
    return get_all_invitations(
        db,
        company_id,
    )


def revoke_invitation_service(
    db: Session,
    invitation_id: int,
    company_id: int,
):
    invitation = (
        db.query(Invitation)
        .filter(
            Invitation.id == invitation_id,
            Invitation.company_id == company_id,
        )
        .with_for_update()
        .first()
    )

    if not invitation:
        raise HTTPException(
            status_code=404,
            detail="Invitation not found",
        )

    if invitation.status == "REVOKED":
        raise HTTPException(
            status_code=400,
            detail="Invitation is already revoked",
        )

    invitation.status = "REVOKED"
    invitation.revoked_at = utc_now_naive()

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    return {
        "message": "Invitation revoked successfully",
        "invitation_id": invitation.id,
        "status": invitation.status,
    }


def accept_invitation_service(
    db: Session,
    data: InvitationAccept,
):
    token_hash = hash_invitation_token(data.token)

    # Lock the invitation row to serialize concurrent registrations.
    invitation = get_invitation_by_token_hash(
        db,
        token_hash,
        for_update=True,
    )

    if not invitation:
        raise HTTPException(
            status_code=400,
            detail="Invalid invitation token",
        )

    if invitation.status != "PENDING":
        raise HTTPException(
            status_code=400,
            detail="Invitation is no longer valid",
        )

    if invitation.revoked_at is not None:
        raise HTTPException(
            status_code=400,
            detail="Invitation has been revoked",
        )

    if invitation.expires_at <= utc_now_naive():
        invitation.status = "EXPIRED"
        db.commit()

        raise HTTPException(
            status_code=400,
            detail="Invitation has expired",
        )

    if (
        invitation.max_uses is not None
        and invitation.uses_count >= invitation.max_uses
    ):
        invitation.status = "EXHAUSTED"
        db.commit()

        raise HTTPException(
            status_code=400,
            detail="Invitation usage limit has been reached",
        )

    email = str(data.email).strip().lower()

    existing_user = (
        db.query(User)
        .filter(
            User.email == email
        )
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="A user with this email already exists",
        )

    new_user = User(
        name=data.name.strip(),
        email=email,
        password_hash=hash_password(data.password),
        role=invitation.role,
        company_id=invitation.company_id,
        is_active=True,
    )

    try:
        db.add(new_user)

        invitation.uses_count += 1

        if (
            invitation.max_uses is not None
            and invitation.uses_count >= invitation.max_uses
        ):
            invitation.status = "EXHAUSTED"

        db.commit()
        db.refresh(new_user)

    except Exception:
        db.rollback()
        raise

    return {
        "message": "Invitation accepted successfully",
        "user_id": new_user.id,
        "name": new_user.name,
        "email": new_user.email,
        "role": new_user.role,
        "company_id": new_user.company_id,
        "is_active": new_user.is_active,
    }
