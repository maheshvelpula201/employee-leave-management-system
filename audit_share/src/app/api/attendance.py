
from calendar import monthrange
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.app.db.database import get_db
from src.app.core.dependencies import get_current_user
from src.app.models.attendance import Attendance
from src.app.models.employes import Employee
from src.app.models.hr import HR
from src.app.models.user import User
from src.app.schemas.attendance import (
    AttendanceUpload,
    AttendanceResponse,
    AttendanceCorrectionRequest,
    AttendanceReopenRequest,
    AttendanceMonthlySummaryResponse,
)
from src.app.services.attendance import (
    upload_attendance,
    correct_attendance,
    reopen_attendance_batch,
    get_company_attendance,
    get_employee_attendance,
    employee_for_user,
)


router = APIRouter(
    prefix="/attendance",
    tags=["Attendance"],
)


def get_authorized_employee(
    db: Session,
    user: User,
    employee_id: int,
) -> Employee:
    """Return an employee only when the current user may access that profile."""

    role = user.role.upper()

    employee = (
        db.query(Employee)
        .filter(
            Employee.id == employee_id,
            Employee.company_id == user.company_id,
        )
        .first()
    )

    if not employee:
        raise HTTPException(404, "Employee not found")

    if role == "COMPANY_ADMIN":
        return employee

    if role == "EMPLOYEE":
        own_profile = employee_for_user(db, user)

        if not own_profile or own_profile.id != employee.id:
            raise HTTPException(
                403,
                "Employees can only view their own attendance",
            )

        return employee

    if role == "MANAGER":
        manager = employee_for_user(db, user)

        if not manager or employee.manager_id != manager.id:
            raise HTTPException(
                403,
                "You can only view your team's attendance",
            )

        return employee

    if role == "HR":
        hr = (
            db.query(HR)
            .filter(
                HR.company_id == user.company_id,
                HR.email == user.email,
            )
            .first()
        )

        if not hr or employee.hr_id != hr.id:
            raise HTTPException(
                403,
                "You can only view attendance for assigned employees",
            )

        return employee

    raise HTTPException(403, "You cannot view this attendance")


@router.post("/upload")
def upload_attendance_endpoint(
    data: AttendanceUpload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.upper() not in {
        "COMPANY_ADMIN",
        "HR",
        "MANAGER",
    }:
        raise HTTPException(403, "You cannot upload attendance")

    batch = upload_attendance(db, current_user, data)

    return {
        "message": "Attendance uploaded successfully",
        "batch_id": batch.id,
        "attendance_date": batch.attendance_date,
        "scope_key": batch.scope_key,
        "uploaded_at": batch.uploaded_at,
        "closes_at": batch.closes_at,
    }


@router.get("/", response_model=list[AttendanceResponse])
def get_attendance_endpoint(
    attendance_date: date | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    role = current_user.role.upper()

    if role == "EMPLOYEE":
        employee = employee_for_user(db, current_user)

        if not employee:
            raise HTTPException(404, "Employee profile not found")

        query = db.query(Attendance).filter(
            Attendance.employee_id == employee.id,
        )

        if attendance_date is not None:
            query = query.filter(
                Attendance.attendance_date == attendance_date,
            )

        return query.order_by(
            Attendance.attendance_date.desc(),
        ).all()

    if role not in {"COMPANY_ADMIN", "HR", "MANAGER"}:
        raise HTTPException(403, "You cannot view attendance")

    records = get_company_attendance(
        db=db,
        company_id=current_user.company_id,
        attendance_date=attendance_date,
    )

    if role == "MANAGER":
        manager = employee_for_user(db, current_user)

        if not manager:
            raise HTTPException(
                403,
                "No employee profile is linked to this manager",
            )

        records = [
            record
            for record in records
            if record.employee.manager_id == manager.id
        ]

    elif role == "HR":
        hr = (
            db.query(HR)
            .filter(
                HR.company_id == current_user.company_id,
                HR.email == current_user.email,
            )
            .first()
        )

        if not hr:
            raise HTTPException(
                403,
                "No HR profile is linked to this account",
            )

        records = [
            record
            for record in records
            if record.employee.hr_id == hr.id
        ]

    return records


@router.get(
    "/me/history",
    response_model=list[AttendanceResponse],
)
def get_my_attendance_history(
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return the signed-in employee's own saved attendance records."""

    if current_user.role.upper() != "EMPLOYEE":
        raise HTTPException(
            403,
            "This endpoint is only for employee accounts",
        )

    if (
        start_date is not None
        and end_date is not None
        and start_date > end_date
    ):
        raise HTTPException(
            400,
            "start_date cannot be after end_date",
        )

    employee = employee_for_user(db, current_user)

    if not employee:
        raise HTTPException(404, "Employee profile not found")

    query = db.query(Attendance).filter(
        Attendance.employee_id == employee.id,
    )

    if start_date is not None:
        query = query.filter(
            Attendance.attendance_date >= start_date,
        )

    if end_date is not None:
        query = query.filter(
            Attendance.attendance_date <= end_date,
        )

    return query.order_by(
        Attendance.attendance_date.desc(),
    ).all()


@router.get(
    "/me/monthly-summary",
    response_model=AttendanceMonthlySummaryResponse,
)
def get_my_monthly_attendance_summary(
    year: int | None = Query(default=None, ge=2000, le=2100),
    month: int | None = Query(default=None, ge=1, le=12),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Summarize actual saved records for the signed-in employee."""

    if current_user.role.upper() != "EMPLOYEE":
        raise HTTPException(
            403,
            "This endpoint is only for employee accounts",
        )

    employee = employee_for_user(db, current_user)

    if not employee:
        raise HTTPException(404, "Employee profile not found")

    today = date.today()

    year = year if year is not None else today.year
    month = month if month is not None else today.month

    first_day = date(year, month, 1)
    last_day = date(
        year,
        month,
        monthrange(year, month)[1],
    )

    records = (
        db.query(Attendance)
        .filter(
            Attendance.employee_id == employee.id,
            Attendance.attendance_date >= first_day,
            Attendance.attendance_date <= last_day,
        )
        .order_by(Attendance.attendance_date.asc())
        .all()
    )

    counts = {
        "PRESENT": 0,
        "ABSENT": 0,
        "LATE": 0,
        "HALF_DAY": 0,
        "ON_LEAVE": 0,
        "WORK_FROM_HOME": 0,
        "HOLIDAY": 0,
        "WEEK_OFF": 0,
    }

    for record in records:
        status_name = (
            record.status.name
            if hasattr(record.status, "name")
            else str(record.status).upper()
        )

        if status_name in counts:
            counts[status_name] += 1

    return {
        "employee_id": employee.id,
        "year": year,
        "month": month,
        "period_start": first_day,
        "period_end": last_day,
        "total_marked_days": len(records),
        "present": counts["PRESENT"],
        "absent": counts["ABSENT"],
        "late": counts["LATE"],
        "half_day": counts["HALF_DAY"],
        "on_leave": counts["ON_LEAVE"],
        "work_from_home": counts["WORK_FROM_HOME"],
        "holidays": counts["HOLIDAY"],
        "week_offs": counts["WEEK_OFF"],
        "records": records,
    }


@router.get(
    "/employee/{employee_id}",
    response_model=list[AttendanceResponse],
)
def get_employee_attendance_endpoint(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_authorized_employee(
        db=db,
        user=current_user,
        employee_id=employee_id,
    )

    return get_employee_attendance(
        db=db,
        company_id=current_user.company_id,
        employee_id=employee_id,
    )


@router.patch(
    "/{attendance_id}/correct",
    response_model=AttendanceResponse,
)
def correct_attendance_endpoint(
    attendance_id: int,
    data: AttendanceCorrectionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return correct_attendance(
        db=db,
        user=current_user,
        attendance_id=attendance_id,
        requested_status=data.requested_status,
        reason=data.reason,
    )


@router.post("/batches/{batch_id}/reopen")
def reopen_attendance_endpoint(
    batch_id: int,
    data: AttendanceReopenRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    batch = reopen_attendance_batch(
        db=db,
        user=current_user,
        batch_id=batch_id,
        reason=data.reason,
    )

    return {
        "message": "Attendance batch reopened",
        "batch_id": batch.id,
        "reopened_at": batch.reopened_at,
        "reopen_reason": batch.reopen_reason,
    }
