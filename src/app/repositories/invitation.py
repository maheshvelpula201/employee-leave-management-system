from sqlalchemy.orm import Session

from src.app.models.invitation import Invitation


def create_invitation(
    db: Session,
    company_id: int,
    email: str,
    role: str,
    token_hash: str,
    expires_at
):
    invitation = Invitation(
        company_id=company_id,
        email=email,
        role=role,
        token_hash=token_hash,
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


def get_invitation_by_token_hash(
    db: Session,
    token_hash: str
):
    return (
        db.query(Invitation)
        .filter(
            Invitation.token_hash == token_hash
        )
        .first()
    )


def get_all_invitations(
    db: Session,
    company_id: int
):
    return (
        db.query(Invitation)
        .filter(
            Invitation.company_id == company_id
        )
        .order_by(
            Invitation.created_at.desc()
        )
        .all()
    )