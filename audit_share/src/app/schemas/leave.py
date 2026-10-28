from pydantic import BaseModel, model_validator
from datetime import date
from typing import Literal


class LeaveCreate(BaseModel):
    employee_id: int
    leave_type: Literal["Sick", "Casual", "Earned", "Unpaid"]
    start_date: date
    end_date: date
    reason: str | None = None

    @model_validator(mode="after")
    def validate_dates(self):
        if self.start_date > self.end_date:
            raise ValueError("start_date cannot be after end_date")

        if self.start_date < date.today():
            raise ValueError("start_date cannot be in the past")

        return self


class LeaveStatusUpdate(BaseModel):
    status: Literal["Pending", "Approved", "Rejected"]


class LeaveResponse(BaseModel):
    id: int
    employee_id: int
    leave_type: str
    start_date: date
    end_date: date
    reason: str | None
    status: str

    class Config:
        from_attributes = True