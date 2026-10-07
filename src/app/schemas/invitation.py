from pydantic import BaseModel, EmailStr


class InvitationCreate(BaseModel):
    email: EmailStr
    role: str


class InvitationResponse(BaseModel):
    id: int
    company_id: int
    email: EmailStr
    role: str
    status: str