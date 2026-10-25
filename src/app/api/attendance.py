
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.app.db.database import get_db
from src.app.core.dependencies import get_current_user
from src.app.core.rbac import Permission
from src.app.core.rbac_dependencies import require_permission
from src.app.models.user import User
from src.app.schemas.attendance import (
    AttendanceUpload,
    AttendanceResponse,
    AttendanceCorrectionRequest,
    AttendanceReopenRequest,
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


@router.post("/mark", response_model=AttendanceResponse)
def mark_attendance_endpoint(
    data: AttendanceUpload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Retained for compatibility with the existing /attendance/mark route.
    # This endpoint now uses the validated batch-upload workflow.
    batch = upload_attendance(db, current_user, data)

    record = (
        db.query(__import__(
            "src.app.models.attendance",
            fromlist=["Attendance"],
        ).Attendance)
        .filter(
            __import__(
                "src.app.models.attendance",
                fromlist=["Attendance"],
            ).Attendance.employee_id == data.entries[0].employee_id,
            __import__(
                "src.app.models.attendance",
                fromlist=["Attendance"],
            ).Attendance.attendance_date == data.attendance_date,
        )
        .first()
    )

    if not record:
        raise HTTPException(500, "Attendance was uploaded but the record could not be retrieved")

    return record


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
        return get_employee_attendance(
            db=db,
            company_id=current_user.company_id,
            employee_id=employee.id,
        )

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
            raise HTTPException(403, "No employee profile is linked to this manager")
        records = [
            record for record in records
            if record.employee.manager_id == manager.id
        ]

    if role == "HR":
        from src.app.models.hr import HR

        hr = (
            db.query(HR)
            .filter(
                HR.company_id == current_user.company_id,
                HR.email == current_user.email,
            )
            .first()
        )

        if not hr:
            raise HTTPException(403, "No HR profile is linked to this account")

        records = [
            record for record in records
            if record.employee.hr_id == hr.id
        ]

    return records


@router.get(
    "/employee/{employee_id}",
    response_model=list[AttendanceResponse],
)
def get_employee_attendance_endpoint(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    role = current_user.role.upper()

    if role == "EMPLOYEE":
        employee = employee_for_user(db, current_user)
        if not employee or employee.id != employee_id:
            raise HTTPException(403, "Employees can only view their own attendance")

    elif role == "MANAGER":
        manager = employee_for_user(db, current_user)
        employee = (
            __import__(
                "src.app.models.employes",
                fromlist=["Employee"],
            ).Employee
        )
        target = (
            db.query(employee)
            .filter(
                employee.id == employee_id,
                employee.company_id == current_user.company_id,
                employee.manager_id == manager.id if manager else False,
            )
            .first()
        )
        if not target:
            raise HTTPException(403, "You can only view your team's attendance")

    elif role == "HR":
        from src.app.models.hr import HR
        from src.app.models.employes import Employee

        hr = (
            db.query(HR)
            .filter(
                HR.company_id == current_user.company_id,
                HR.email == current_user.email,
            )
            .first()
        )
        target = (
            db.query(Employee)
            .filter(
                Employee.id == employee_id,
                Employee.company_id == current_user.company_id,
                Employee.hr_id == hr.id if hr else False,
            )
            .first()
        )
        if not target:
            raise HTTPException(403, "You can only view assigned employees")

    elif role != "COMPANY_ADMIN":
        raise HTTPException(403, "You cannot view this attendance")

    return get_employee_attendance(
        db=db,
        company_id=current_user.company_id,
        employee_id=employee_id,
    )


@router.patch("/{attendance_id}/correct", response_model=AttendanceResponse)
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
