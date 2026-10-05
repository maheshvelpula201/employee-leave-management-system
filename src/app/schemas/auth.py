from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    role: str
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str
