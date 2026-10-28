from sqlalchemy.orm import Session

from src.app.models.user import User


def get_all_admins(
    db: Session,
    company_id: int
):
    return (
        db.query(User)
        .filter(
            User.company_id == company_id,
            User.role == "COMPANY_ADMIN"
        )
        .all()
    )


def get_admin_by_id(
    db: Session,
    admin_id: int,
    company_id: int
):
    return (
        db.query(User)
        .filter(
            User.id == admin_id,
            User.company_id == company_id,
            User.role == "COMPANY_ADMIN"
        )
        .first()
    )


def get_admin_by_email(
    db: Session,
    email: str,
    company_id: int
):
    return (
        db.query(User)
        .filter(
            User.email == email,
            User.company_id == company_id,
            User.role == "COMPANY_ADMIN"
        )
        .first()
    )


def update_admin(
    db: Session,
    admin: User,
    name: str | None = None,
    email: str | None = None
):
    if name is not None:
        admin.name = name

    if email is not None:
        admin.email = email

    db.commit()
    db.refresh(admin)

    return admin


def update_admin_status(
    db: Session,
    admin: User,
    is_active: bool
):
    admin.is_active = is_active

    db.commit()
    db.refresh(admin)

    return admin