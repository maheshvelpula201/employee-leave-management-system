from pydantic import BaseModel, EmailStr


class CompanyRegistration(BaseModel):

    company_name: str
    company_email: EmailStr
    company_phone: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    website: str | None = None
    description: str | None = None