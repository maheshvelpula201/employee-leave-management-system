from pydantic import BaseModel, EmailStr


class CompanyAdminCreate(BaseModel):

    name: str
    email: EmailStr
    password: str
    