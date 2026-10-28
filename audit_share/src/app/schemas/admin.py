from pydantic import BaseModel, EmailStr


class CompanyAdminCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


class AdminUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None


class AdminStatusUpdate(BaseModel):
    is_active: bool


class AdminResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    company_id: int
    is_active: bool