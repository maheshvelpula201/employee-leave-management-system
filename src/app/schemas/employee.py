# src/app/schemas/employee.py

from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict, Field, model_validator


class StaffMemberResponse(BaseModel):
    id: int
    user_id: int | None = None
    name: str
    email: EmailStr
    employee_id: str | None = None
    department: str | None = None
    designation: str | None = None
    phone: str | None = None
    category: str  # 'Employee', 'Manager', or 'HR'
    employment_status: str | None = None
    joining_date: datetime | None = None
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class ProfileUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    phone: str | None = Field(default=None, max_length=50)
    department: str | None = Field(default=None, max_length=100)
    designation: str | None = Field(default=None, max_length=100)

    @model_validator(mode="after")
    def validate_fields(self):
        self.name = self.name.strip()
        if not self.name:
            raise ValueError("Name cannot be empty")
        if self.phone:
            self.phone = self.phone.strip()
        if self.department:
            self.department = self.department.strip()
        if self.designation:
            self.designation = self.designation.strip()
        return self


class UserProfileResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    company_id: int
    phone: str | None = None
    department: str | None = None
    designation: str | None = None
    employment_status: str | None = None
    joining_date: datetime | None = None

    model_config = ConfigDict(from_attributes=True)