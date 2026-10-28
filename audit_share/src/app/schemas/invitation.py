from datetime import datetime

from pydantic import (
    BaseModel,
    EmailStr,
    ConfigDict,
    Field,
    model_validator,
)


class InvitationCreate(BaseModel):
    role: str = Field(min_length=1, max_length=50)

    # None means unlimited uses.
    max_uses: int | None = Field(
        default=None,
        ge=1,
    )

    # Number of days until the invitation expires.
    expires_in_days: int = Field(
        default=3,
        ge=1,
        le=90,
    )


class InvitationResponse(BaseModel):
    id: int
    company_id: int
    email: EmailStr | None
    role: str
    status: str
    max_uses: int | None
    uses_count: int
    created_by: int | None
    revoked_at: datetime | None
    expires_at: datetime
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class InvitationAccept(BaseModel):
    token: str = Field(min_length=1)
    email: EmailStr
    name: str = Field(min_length=1, max_length=150)
    password: str = Field(min_length=8, max_length=128)

    @model_validator(mode="after")
    def validate_name(self):
        self.name = self.name.strip()

        if not self.name:
            raise ValueError("Name cannot be empty")

        return self
