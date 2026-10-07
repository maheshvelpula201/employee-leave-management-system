from sqlalchemy.orm import Session

from src.app.models.invitation import Invitation


def create_invitation(
    db: Session,
    company_id: int,
    email: str,
    role: str,
    invitation_code: str,
    expires_at
):
    invitation = Invitation(
        company_id=company_id,
        email=email,
        role=role,
        invitation_code=invitation_code,
        status="PENDING",
        expires_at=expires_at
    )

    db.add(invitation)
    db.commit()
    db.refresh(invitation)

    return invitation


def get_pending_invitation(
    db: Session,
    company_id: int,
    email: str,
    role: str
):
    return (
        db.query(Invitation)
        .filter(
            Invitation.company_id == company_id,
            Invitation.email == email,
            Invitation.role == role,
            Invitation.status == "PENDING"
        )
        .first()
    )


def get_invitation_by_code(
    db: Session,
    invitation_code: str
):
    return (
        db.query(Invitation)
        .filter(
            Invitation.invitation_code == invitation_code
        )
        .first()
    )