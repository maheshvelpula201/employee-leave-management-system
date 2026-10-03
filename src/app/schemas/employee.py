from datetime import date

from pydantic import BaseModel, EmailStr


class EmployeeCreate(BaseModel):

    name: str

    email: EmailStr

    department: str

    designation: str | None = None

    joining_date: date | None = None

    leaving_date: date | None = None

    termination_reason: str | None = None

    employment_status: str = "ACTIVE"

    phone: str | None = None

    emergency_contact_name: str | None = None

    emergency_contact_phone: str | None = None

    manager_id: int | None = None


class EmployeeUpdate(BaseModel):

    name: str | None = None

    email: EmailStr | None = None

    department: str | None = None

    designation: str | None = None

    joining_date: date | None = None

    leaving_date: date | None = None

    termination_reason: str | None = None

    phone: str | None = None

    emergency_contact_name: str | None = None

    emergency_contact_phone: str | None = None


class EmployeeExit(BaseModel):

    leaving_date: date

    termination_reason: str