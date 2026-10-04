from sqlalchemy.orm import Session

from src.app.models.company import Company
from src.app.models.user import User
from src.app.core.security import hash_password
from src.app.schemas.admin import CompanyAdminCreate


def create_company_admin(
    db: Session,
    company_id: int,
    data: CompanyAdminCreate
):
    # 1. Find the company

    company = (
        db.query(Company)
        .filter(Company.id == company_id)
        .first()
    )

    if not company:
        raise ValueError("Company not found")

    # 2. Company must be approved

    if company.status != "APPROVED":
        raise ValueError(
            "Company must be approved before creating an admin"
        )

    # 3. Check whether this email is already registered

    existing_user = (
        db.query(User)
        .filter(User.email == data.email)
        .first()
    )

    if existing_user:
        raise ValueError("User with this email already exists")

    # 4. Hash the password

    password_hash = hash_password(data.password)

    # 5. Create the Company Admin

    admin = User(
        name=data.name,
        email=data.email,
        password_hash=password_hash,
        role="COMPANY_ADMIN",
        company_id=company.id,
        is_active=True
    )

    db.add(admin)

    # 6. Save the admin

    db.commit()

    # 7. Refresh admin

    db.refresh(admin)

    return {
        "user_id": admin.id,
        "name": admin.name,
        "email": admin.email,
        "role": admin.role,
        "company_id": admin.company_id,
        "is_active": admin.is_active
    }