from pydantic import BaseModel
from typing import Literal


class LeaveBalanceCreate(BaseModel):
    employee_id: int
    leave_type: Literal["Sick", "Casual", "Earned"]
    year: int


class LeaveBalanceResponse(BaseModel):
    id: int
    employee_id: int
    leave_type: str
    total_days: int
    used_days: int
    remaining_days: int

    class Config:
        from_attributes = True