from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.app.models.company import Company
from src.app.models.user import User

from src.app.core.security import hash_password

from src.app.schemas.admin import (
    CompanyAdminCreate,
    AdminUpdate,
    AdminStatusUpdate
)

from src.app.repositories.admin import (
    get_all_admins,
    get_admin_by_id,
    get_admin_by_email,
    update_admin,
    update_admin_status
)


# ==========================================
# CREATE FIRST COMPANY ADMIN
# ==========================================

def create_company_admin(
    db: Session,
    company_id: int,
    data: CompanyAdminCreate
):
    company = (
        db.query(Company)
        .filter(
            Company.id == company_id
        )
        .first()
    )

    if not company:
        raise ValueError(
            "Company not found"
        )

    if company.status != "APPROVED":
        raise ValueError(
            "Company must be approved before creating an admin"
        )

    existing_admin = (
        db.query(User)
        .filter(
            User.company_id == company_id,
            User.role == "COMPANY_ADMIN"
        )
        .first()
    )

    if existing_admin:
        raise ValueError(
            "Company already has a Company Admin"
        )

    existing_user = (
        db.query(User)
        .filter(
            User.email == data.email
        )
        .first()
    )

    if existing_user:
        raise ValueError(
            "User with this email already exists"
        )

    password_hash = hash_password(
        data.password
    )

    admin = User(
        name=data.name,
        email=data.email,
        password_hash=password_hash,
        role="COMPANY_ADMIN",
        company_id=company.id,
        is_active=True
    )

    db.add(admin)
    db.commit()
    db.refresh(admin)

    return {
        "user_id": admin.id,
        "name": admin.name,
        "email": admin.email,
        "role": admin.role,
        "company_id": admin.company_id,
        "is_active": admin.is_active
    }


# ==========================================
# GET ALL ADMINS
# ==========================================

def get_all_admins_service(
    db: Session,
    company_id: int
):
    return get_all_admins(
        db,
        company_id
    )


# ==========================================
# GET ADMIN BY ID
# ==========================================

def get_admin_by_id_service(
    db: Session,
    admin_id: int,
    company_id: int
):
    admin = get_admin_by_id(
        db,
        admin_id,
        company_id
    )

    if not admin:
        raise HTTPException(
            status_code=404,
            detail="Admin not found"
        )

    return admin


# ==========================================
# UPDATE ADMIN
# ==========================================

def update_admin_service(
    db: Session,
    admin_id: int,
    data: AdminUpdate,
    company_id: int
):
    admin = get_admin_by_id(
        db,
        admin_id,
        company_id
    )

    if not admin:
        raise HTTPException(
            status_code=404,
            detail="Admin not found"
        )

    if data.email is not None:

        existing_admin = get_admin_by_email(
            db,
            data.email,
            company_id
        )

        if (
            existing_admin
            and existing_admin.id != admin.id
        ):
            raise HTTPException(
                status_code=400,
                detail="Admin with this email already exists"
            )

        existing_user = (
            db.query(User)
            .filter(
                User.email == data.email,
                User.id != admin.id
            )
            .first()
        )

        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="User with this email already exists"
            )

    return update_admin(
        db,
        admin,
        data.name,
        data.email
    )


# ==========================================
# UPDATE ADMIN STATUS
# ==========================================

def update_admin_status_service(
    db: Session,
    admin_id: int,
    data: AdminStatusUpdate,
    company_id: int,
    current_admin_id: int
):
    admin = get_admin_by_id(
        db,
        admin_id,
        company_id
    )

    if not admin:
        raise HTTPException(
            status_code=404,
            detail="Admin not found"
        )

    if (
        admin.id == current_admin_id
        and not data.is_active
    ):
        raise HTTPException(
            status_code=400,
            detail="You cannot deactivate your own account"
        )

    return update_admin_status(
        db,
        admin,
        data.is_active
    )