
from datetime import date, datetime, time
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


AttendanceStatusInput = Literal[
    "PRESENT",
    "ABSENT",
    "LATE",
    "HALF_DAY",
    "ON_LEAVE",
    "WORK_FROM_HOME",
    "HOLIDAY",
    "WEEK_OFF",
]

StatusDisplay = {
    "PRESENT": "Present",
    "ABSENT": "Absent",
    "LATE": "Late",
    "HALF_DAY": "Half-day",
    "ON_LEAVE": "On leave",
    "WORK_FROM_HOME": "Work from home",
    "HOLIDAY": "Holiday",
    "WEEK_OFF": "Week off",
}


class AttendanceEntry(BaseModel):
    employee_id: int = Field(gt=0)
    status: AttendanceStatusInput
    check_in: time | None = None
    check_out: time | None = None
    notes: str | None = Field(default=None, max_length=2000)

    @model_validator(mode="after")
    def validate_times(self):
        if (
            self.check_in is not None
            and self.check_out is not None
            and self.check_out < self.check_in
        ):
            raise ValueError(
                "Check-out cannot be earlier than check-in on the same day"
            )
        return self


class AttendanceUpload(BaseModel):
    attendance_date: date
    department: str | None = Field(default=None, max_length=255)
    manager_employee_id: int | None = Field(default=None, gt=0)
    entries: list[AttendanceEntry] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_entries(self):
        ids = [entry.employee_id for entry in self.entries]
        if len(ids) != len(set(ids)):
            raise ValueError("An employee can appear only once per upload")
        return self


class AttendanceMark(BaseModel):
    employee_id: int
    attendance_date: date
    status: AttendanceStatusInput
    notes: str | None = None
    check_in: time | None = None
    check_out: time | None = None


class AttendanceCorrectionRequest(BaseModel):
    requested_status: AttendanceStatusInput
    reason: str = Field(min_length=3, max_length=2000)


class AttendanceReopenRequest(BaseModel):
    reason: str = Field(min_length=3, max_length=2000)


class AttendanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_id: int
    attendance_date: date
    status: str
    check_in: time | None = None
    check_out: time | None = None
    notes: str | None = None
    marked_by: int
    uploaded_at: datetime
    closes_at: datetime
    last_updated_by: int | None = None
    last_updated_at: datetime | None = None
    correction_reason: str | None = None


class AttendanceBatchResponse(BaseModel):
    id: int
    attendance_date: date
    scope_key: str
    department: str | None = None
    manager_employee_id: int | None = None
    uploaded_by: int
    uploaded_at: datetime
    closes_at: datetime
