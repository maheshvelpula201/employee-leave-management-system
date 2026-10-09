from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict


class InvitationCreate(BaseModel):
    email: EmailStr
    role: str


class InvitationResponse(BaseModel):
    id: int
    company_id: int
    email: EmailStr
    role: str
    status: str
    expires_at: datetime
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class InvitationAccept(BaseModel):
    token: str
    name: str
    password: str