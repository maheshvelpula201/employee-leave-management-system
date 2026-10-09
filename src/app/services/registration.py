import secrets

from sqlalchemy.orm import Session

from src.app.models.company import Company
from src.app.models.user import User
from src.app.schemas.registration import CompanyRegistration
from src.app.core.security import hash_password


def register_company(
    db: Session,
    data: CompanyRegistration
):
    # 1. Check whether the company already exists
    existing_company = (
        db.query(Company)
        .filter(Company.email == data.company_email)
        .first()
    )

    if existing_company:
        raise ValueError("Company already exists")

    # 2. Check whether the admin email is already registered
    existing_user = (
        db.query(User)
        .filter(User.email == data.admin_email)
        .first()
    )

    if existing_user:
        raise ValueError("An account with this admin email already exists")

    # 3. Generate a unique company code
    while True:
        company_code = secrets.token_hex(4).upper()

        existing_code = (
            db.query(Company)
            .filter(Company.company_code == company_code)
            .first()
        )

        if not existing_code:
            break

    # 4. Create the company as pending approval
    company = Company(
        name=data.company_name,
        email=data.company_email,
        phone=data.company_phone,
        address=data.address,
        city=data.city,
        state=data.state,
        country=data.country,
        website=data.website,
        description=data.description,
        company_code=company_code,
        status="PENDING",
        is_active=False
    )

    # 5. Add the company and flush to obtain its database ID
    db.add(company)
    db.flush()

    # 6. Create the initial Company Admin
    admin = User(
        name=data.admin_name,
        email=data.admin_email,
        password_hash=hash_password(data.admin_password),
        role="COMPANY_ADMIN",
        company_id=company.id,
        is_active=True
    )

    db.add(admin)

    # 7. Save both records in one transaction
    db.commit()

    # 8. Refresh the saved records
    db.refresh(company)
    db.refresh(admin)

    return {
        "message": "Company registration submitted successfully. Awaiting approval.",
        "company": {
            "company_id": company.id,
            "company_name": company.name,
            "company_email": company.email,
            "company_code": company.company_code,
            "status": company.status,
            "is_active": company.is_active
        },
        "admin": {
            "user_id": admin.id,
            "name": admin.name,
            "email": admin.email,
            "role": admin.role,
            "company_id": admin.company_id,
            "is_active": admin.is_active
        }
    }
