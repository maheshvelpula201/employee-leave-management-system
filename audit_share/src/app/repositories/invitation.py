from datetime import datetime

from sqlalchemy.orm import Session

from src.app.models.invitation import Invitation


def create_invitation(
    db: Session,
    company_id: int,
    role: str,
    token_hash: str,
    expires_at: datetime,
    max_uses: int | None,
    created_by: int | None,
):
    invitation = Invitation(
        company_id=company_id,
        email=None,
        role=role,
        token_hash=token_hash,
        status="PENDING",
        expires_at=expires_at,
        max_uses=max_uses,
        uses_count=0,
        created_by=created_by,
    )

    db.add(invitation)
    db.flush()

    return invitation


def get_invitation_by_token_hash(
    db: Session,
    token_hash: str,
    for_update: bool = False,
):
    query = db.query(Invitation).filter(
        Invitation.token_hash == token_hash
    )

    if for_update:
        query = query.with_for_update()

    return query.first()


def get_all_invitations(
    db: Session,
    company_id: int,
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


def revoke_invitation(
    db: Session,
    invitation: Invitation,
):
    invitation.status = "REVOKED"
    invitation.revoked_at = datetime.utcnow()

    db.flush()

    return invitation
