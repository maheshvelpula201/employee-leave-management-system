from pydantic import BaseModel, Field
from typing import Literal


class LeavePolicyCreate(BaseModel):
    leave_type: Literal["Sick", "Casual", "Earned"]
    annual_days: int = Field(gt=0)
    year: int = Field(gt=2000)


class LeavePolicyResponse(BaseModel):
    id: int
    leave_type: str
    annual_days: int
    year: int

    class Config:
        from_attributes = True