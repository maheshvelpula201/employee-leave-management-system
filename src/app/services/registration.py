import secrets

from sqlalchemy.orm import Session

from src.app.models.company import Company
from src.app.schemas.registration import CompanyRegistration


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

    # 2. Generate a unique company code

    while True:
        company_code = secrets.token_hex(4).upper()

        existing_code = (
            db.query(Company)
            .filter(Company.company_code == company_code)
            .first()
        )

        if not existing_code:
            break

    # 3. Create the company

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

    db.add(company)

    # 4. Save the company

    db.commit()

    # 5. Refresh company data

    db.refresh(company)

    return {
        "company_id": company.id,
        "company_name": company.name,
        "company_email": company.email,
        "company_code": company.company_code,
        "status": company.status,
        "is_active": company.is_active
    }