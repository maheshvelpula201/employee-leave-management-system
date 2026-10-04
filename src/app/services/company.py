from sqlalchemy.orm import Session

from src.app.models.company import Company


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

    # 5. Keep company inactive until operator onboarding

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