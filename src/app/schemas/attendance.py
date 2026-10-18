
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, model_validator


AttendanceStatus = Literal[
    "PRESENT",
    "ABSENT",
    "HALF_DAY",
    "ON_LEAVE",
]


class AttendanceMark(BaseModel):
    employee_id: int
    attendance_date: date
    status: AttendanceStatus
    notes: str | None = None


class AttendanceCorrectionRequest(BaseModel):
    requested_status: AttendanceStatus
    reason: str


class AttendanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_id: int
    attendance_date: date
    check_in: datetime | None = None
    check_out: datetime | None = None
    status: AttendanceStatus
    notes: str | None = None
