from pydantic import BaseModel, EmailStr, Field


class CompanyRegistration(BaseModel):
    # Company details
    company_name: str = Field(min_length=2, max_length=200)
    company_email: EmailStr
    company_phone: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    website: str | None = None
    description: str | None = None

    # Initial Company Admin details
    admin_name: str = Field(min_length=2, max_length=200)
    admin_email: EmailStr
    admin_password: str = Field(min_length=8, max_length=128)
