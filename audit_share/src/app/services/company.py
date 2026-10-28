from sqlalchemy.orm import Session

from src.app.models.company import Company
from src.app.models.user import User


def update_company_status(
    db: Session,
    company_id: int,
    new_status: str
):
    # 1. Find the company

    company = (
        db.query(Company)
        .filter(Company.id == company_id)
        .first()
    )

    if not company:
        raise ValueError("Company not found")

    # 2. Validate the new status

    allowed_statuses = {
        "APPROVED",
        "REJECTED",
        "SUSPENDED"
    }

    if new_status not in allowed_statuses:
        raise ValueError("Invalid company status")

    # 3. Company must currently be PENDING

    if company.status != "PENDING":
        raise ValueError(
            "Only PENDING companies can have their status changed"
        )

    # 4. Update the status

    company.status = new_status

    # 5. Company remains inactive after approval
    #    until at least one active Company Admin exists

    company.is_active = False

    # 6. Save changes

    db.commit()

    # 7. Refresh company

    db.refresh(company)

    return {
        "company_id": company.id,
        "company_name": company.name,
        "company_email": company.email,
        "status": company.status,
        "is_active": company.is_active
    }


def activate_company(
    db: Session,
    company_id: int
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
            "Company must be approved before activation"
        )

    # 3. Check whether the company has
    #    at least one active Company Admin

    active_admin = (
        db.query(User)
        .filter(
            User.company_id == company_id,
            User.role == "COMPANY_ADMIN",
            User.is_active == True
        )
        .first()
    )

    if not active_admin:
        raise ValueError(
            "Company must have at least one active Company Admin"
        )

    # 4. Activate the company

    company.is_active = True

    # 5. Save changes

    db.commit()

    # 6. Refresh company

    db.refresh(company)

    return {
        "company_id": company.id,
        "company_name": company.name,
        "company_email": company.email,
        "status": company.status,
        "is_active": company.is_active
    }