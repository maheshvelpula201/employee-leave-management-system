# src/app/services/invitation.py

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
from src.app.models.employes import Employee
from src.app.models.hr import HR
from src.app.models.company import Company

from src.app.core.security import hash_password
from src.app.services.email import send_invitation_email_async


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
    return datetime.now(timezone.utc).replace(tzinfo=None)


def compute_invitation_details(invitation: Invitation) -> dict:
    """
    Computes human-readable status, remaining time, and remaining usage display
    dynamically from current backend timestamps and counts.
    """
    now = utc_now_naive()
    
    # 1. Determine Revoked status
    if invitation.revoked_at is not None or invitation.status == "REVOKED":
        return {
            "human_status": "Revoked",
            "remaining_time_display": "Revoked",
            "remaining_uses_display": (
                "Unlimited" if invitation.max_uses is None 
                else f"{max(0, invitation.max_uses - invitation.uses_count)} registrations remaining"
            )
        }

    # 2. Determine Expired status (strict 24h or expiration timestamp reached)
    if invitation.expires_at <= now or invitation.status == "EXPIRED":
        return {
            "human_status": "Expired",
            "remaining_time_display": "Expired",
            "remaining_uses_display": (
                "Unlimited" if invitation.max_uses is None 
                else f"{max(0, invitation.max_uses - invitation.uses_count)} registrations remaining"
            )
        }

    # 3. Determine Fully Used / Exhausted status
    if invitation.max_uses is not None and invitation.uses_count >= invitation.max_uses:
        return {
            "human_status": "Fully Used",
            "remaining_time_display": "Completed",
            "remaining_uses_display": "0 registrations remaining"
        }

    # 4. Otherwise Active - Calculate remaining time
    delta = invitation.expires_at - now
    total_seconds = int(delta.total_seconds())
    
    if total_seconds <= 0:
        human_status = "Expired"
        remaining_time_display = "Expired"
    else:
        human_status = "Active"
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        if hours > 0:
            remaining_time_display = f"{hours} hour{'s' if hours > 1 else ''} left"
        else:
            remaining_time_display = f"{max(1, minutes)} minute{'s' if minutes > 1 else ''} left"

    # Remaining uses display
    if invitation.max_uses is None:
        remaining_uses_display = "Unlimited"
    else:
        remaining = max(0, invitation.max_uses - invitation.uses_count)
        remaining_uses_display = f"{remaining} registration{'s' if remaining != 1 else ''} remaining"

    return {
        "human_status": human_status,
        "remaining_time_display": remaining_time_display,
        "remaining_uses_display": remaining_uses_display,
    }


def enrich_invitation_response(invitation: Invitation) -> dict:
    details = compute_invitation_details(invitation)
    return {
        "id": invitation.id,
        "company_id": invitation.company_id,
        "email": invitation.email,
        "role": invitation.role,
        "status": invitation.status,
        "max_uses": invitation.max_uses,
        "uses_count": invitation.uses_count,
        "created_by": invitation.created_by,
        "revoked_at": invitation.revoked_at,
        "expires_at": invitation.expires_at,
        "created_at": invitation.created_at,
        "human_status": details["human_status"],
        "remaining_time_display": details["remaining_time_display"],
        "remaining_uses_display": details["remaining_uses_display"],
    }


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

    if role in {"OWNER", "COMPANY_ADMIN"}:
        raise HTTPException(
            status_code=403,
            detail="Creating invitations for this role is not allowed here",
        )

    target_email = str(data.email).strip().lower() if data.email else None
    invitation_token = secrets.token_urlsafe(48)
    token_hash = hash_invitation_token(invitation_token)

    # STRICT 24-HOUR EXPIRATION ENFORCEMENT
    expires_at = utc_now_naive() + timedelta(hours=24)

    try:
        invitation = Invitation(
            company_id=company_id,
            email=target_email,
            role=role,
            token_hash=token_hash,
            status="PENDING",
            expires_at=expires_at,
            max_uses=data.max_uses,
            uses_count=0,
            created_by=created_by,
        )
        db.add(invitation)
        db.flush()

        db.commit()
        db.refresh(invitation)

        if target_email:
            company = db.query(Company).filter(Company.id == company_id).first()
            company_name = company.name if company else "PeopleSphere"
            invite_url = f"/invite?token={invitation_token}"
            send_invitation_email_async(
                to_email=target_email,
                invite_url=invite_url,
                role=role,
                company_name=company_name,
            )

    except Exception:
        db.rollback()
        raise

    response_data = enrich_invitation_response(invitation)
    response_data["invitation_token"] = invitation_token
    return response_data


def get_all_invitations_service(
    db: Session,
    company_id: int,
):
    invitations = get_all_invitations(db, company_id)
    return [enrich_invitation_response(inv) for inv in invitations]


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

    if invitation.status != "PENDING":
        raise HTTPException(
            status_code=400,
            detail="Only pending invitations can be revoked",
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

    if invitation.status == "REVOKED" or invitation.revoked_at is not None:
        raise HTTPException(
            status_code=400,
            detail="This invitation has been revoked.",
        )

    # STRICT 24-HOUR EXPIRY & TIMESTAMPS CHECK
    if invitation.expires_at <= utc_now_naive() or invitation.status == "EXPIRED":
        invitation.status = "EXPIRED"
        db.commit()
        raise HTTPException(
            status_code=400,
            detail="This invitation link has expired. Please contact your Company Admin for a new invitation.",
        )

    if (
        invitation.max_uses is not None
        and invitation.uses_count >= invitation.max_uses
    ) or invitation.status == "EXHAUSTED":
        invitation.status = "EXHAUSTED"
        db.commit()
        raise HTTPException(
            status_code=400,
            detail="Invitation usage limit has been reached",
        )

    registering_email = str(data.email).strip().lower()

    if invitation.email and invitation.email.strip().lower() != registering_email:
        raise HTTPException(
            status_code=400,
            detail="This invitation link is restricted to a different email address",
        )

    existing_user = (
        db.query(User)
        .filter(User.email == registering_email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="A user with this email already exists",
        )

    role = invitation.role.strip().upper()

    new_user = User(
        name=data.name.strip(),
        email=registering_email,
        password_hash=hash_password(data.password),
        role=role,
        company_id=invitation.company_id,
        is_active=True,
    )

    try:
        db.add(new_user)
        db.flush()

        if role == "HR":
            new_hr = HR(
                name=new_user.name,
                email=new_user.email,
                company_id=new_user.company_id,
            )
            db.add(new_hr)

        elif role in {"EMPLOYEE", "MANAGER"}:
            new_employee = Employee(
                name=new_user.name,
                email=new_user.email,
                department="Unassigned",
                designation="Manager" if role == "MANAGER" else None,
                employment_status="ACTIVE",
                company_id=new_user.company_id,
            )
            db.add(new_employee)

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