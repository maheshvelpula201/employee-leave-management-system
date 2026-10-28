
from datetime import date, datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.app.models.attendance import (
    Attendance,
    AttendanceBatch,
    AttendanceCorrection,
    AttendanceReopenAudit,
    AttendanceStatus,
)
from src.app.models.employes import Employee
from src.app.models.leave import Leave
from src.app.models.hr import HR
from src.app.models.user import User
from src.app.schemas.attendance import AttendanceUpload


def utc_now():
    return datetime.now(timezone.utc)


def status_from_input(value: str) -> AttendanceStatus:
    try:
        return AttendanceStatus[value]
    except KeyError:
        raise HTTPException(status_code=422, detail="Invalid attendance status")


def employee_for_user(db: Session, user: User):
    return (
        db.query(Employee)
        .filter(
            Employee.company_id == user.company_id,
            Employee.email == user.email,
        )
        .first()
    )


def get_scoped_employees(
    db: Session,
    user: User,
    department: str | None = None,
    manager_employee_id: int | None = None,
):
    query = db.query(Employee).filter(
        Employee.company_id == user.company_id,
        Employee.employment_status == "ACTIVE",
    )

    role = user.role.upper()

    if role == "COMPANY_ADMIN":
        if manager_employee_id is not None:
            query = query.filter(Employee.manager_id == manager_employee_id)
        elif department:
            query = query.filter(Employee.department == department)
        return query.all()

    if role == "HR":
        hr = (
            db.query(HR)
            .filter(
                HR.company_id == user.company_id,
                HR.email == user.email,
            )
            .first()
        )
        if not hr:
            raise HTTPException(403, "No HR profile is linked to this account")

        query = query.filter(Employee.hr_id == hr.id)

        if manager_employee_id is not None:
            query = query.filter(Employee.manager_id == manager_employee_id)
        if department:
            query = query.filter(Employee.department == department)

        return query.all()

    if role == "MANAGER":
        manager = employee_for_user(db, user)
        if not manager:
            raise HTTPException(403, "No employee profile is linked to this manager")

        if manager_employee_id is not None and manager_employee_id != manager.id:
            raise HTTPException(403, "Managers can only manage their own team")

        query = query.filter(Employee.manager_id == manager.id)

        if department:
            query = query.filter(Employee.department == department)

        return query.all()

    raise HTTPException(403, "You cannot manage attendance")


def scope_key_for_upload(
    user: User,
    department: str | None,
    manager_employee_id: int | None,
):
    if manager_employee_id is not None:
        return f"manager:{manager_employee_id}"
    if department:
        return f"department:{department.strip().casefold()}"
    return f"company:{user.company_id}"


def ensure_not_on_approved_leave(
    db: Session,
    employee_id: int,
    attendance_date: date,
):
    leave = (
        db.query(Leave)
        .filter(
            Leave.employee_id == employee_id,
            Leave.status.ilike("approved"),
            Leave.start_date <= attendance_date,
            Leave.end_date >= attendance_date,
        )
        .first()
    )

    if leave:
        return True
    return False


def upload_attendance(
    db: Session,
    user: User,
    data: AttendanceUpload,
):
    today = utc_now().date()

    if data.attendance_date != today:
        raise HTTPException(
            400,
            "Normal attendance uploads are allowed for today only",
        )

    employees = get_scoped_employees(
        db,
        user,
        department=data.department,
        manager_employee_id=data.manager_employee_id,
    )

    if not employees:
        raise HTTPException(400, "No eligible employees were found in this scope")

    employee_ids = {employee.id for employee in employees}
    submitted_ids = {entry.employee_id for entry in data.entries}

    if submitted_ids != employee_ids:
        missing = sorted(employee_ids - submitted_ids)
        extra = sorted(submitted_ids - employee_ids)

        raise HTTPException(
            400,
            {
                "message": (
                    "Upload blocked. Every eligible employee must have "
                    "an explicit attendance status."
                ),
                "missing_employee_ids": missing,
                "ineligible_employee_ids": extra,
            },
        )

    for entry in data.entries:
        if ensure_not_on_approved_leave(
            db, entry.employee_id, data.attendance_date
        ):
            if entry.status != "ON_LEAVE":
                raise HTTPException(
                    400,
                    f"Employee {entry.employee_id} has approved leave. "
                    "Their status must be ON_LEAVE.",
                )

    scope_key = scope_key_for_upload(
        user,
        data.department,
        data.manager_employee_id,
    )

    existing_batch = (
        db.query(AttendanceBatch)
        .filter(
            AttendanceBatch.company_id == user.company_id,
            AttendanceBatch.attendance_date == data.attendance_date,
            AttendanceBatch.scope_key == scope_key,
        )
        .first()
    )

    if existing_batch:
        raise HTTPException(
            409,
            "Attendance for this scope and date has already been uploaded. "
            "Use the correction workflow.",
        )

    now = utc_now()
    closes_at = now + timedelta(hours=24)

    batch = AttendanceBatch(
        company_id=user.company_id,
        attendance_date=data.attendance_date,
        scope_key=scope_key,
        department=data.department,
        manager_employee_id=data.manager_employee_id,
        uploaded_by=user.id,
        uploaded_at=now,
        closes_at=closes_at,
    )

    try:
        db.add(batch)
        db.flush()

        manager_team_id = data.manager_employee_id or 0

        for entry in data.entries:
            record = Attendance(
                employee_id=entry.employee_id,
                team_id=manager_team_id,
                attendance_date=data.attendance_date,
                status=status_from_input(entry.status),
                check_in=entry.check_in,
                check_out=entry.check_out,
                notes=entry.notes,
                marked_by=user.id,
                uploaded_at=now,
                closes_at=closes_at,
            )
            db.add(record)

        db.commit()
        db.refresh(batch)
        return batch

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            409,
            "Attendance upload conflicts with an existing record.",
        )


def correct_attendance(
    db: Session,
    user: User,
    attendance_id: int,
    requested_status: str,
    reason: str,
):
    record = (
        db.query(Attendance)
        .join(Employee, Employee.id == Attendance.employee_id)
        .filter(
            Attendance.id == attendance_id,
            Employee.company_id == user.company_id,
        )
        .first()
    )

    if not record:
        raise HTTPException(404, "Attendance record not found")

    role = user.role.upper()

    if role == "EMPLOYEE":
        employee = employee_for_user(db, user)
        if not employee or employee.id != record.employee_id:
            raise HTTPException(403, "You can only view your own attendance")
        raise HTTPException(403, "Employees cannot correct attendance")

    if role not in {"COMPANY_ADMIN", "HR", "MANAGER"}:
        raise HTTPException(403, "You cannot correct attendance")

    if role == "MANAGER":
        manager = employee_for_user(db, user)
        if not manager or record.employee.manager_id != manager.id:
            raise HTTPException(403, "You can only correct your own team's attendance")

    if role == "HR":
        hr = (
            db.query(HR)
            .filter(HR.company_id == user.company_id, HR.email == user.email)
            .first()
        )
        if not hr or record.employee.hr_id != hr.id:
            raise HTTPException(403, "You can only correct attendance for assigned employees")

    batch = (
        db.query(AttendanceBatch)
        .filter(
            AttendanceBatch.company_id == user.company_id,
            AttendanceBatch.attendance_date == record.attendance_date,
        )
        .filter(
            AttendanceBatch.scope_key.in_([
                f"manager:{record.team_id}",
                f"department:{record.employee.department.casefold()}",
                f"company:{user.company_id}",
            ])
        )
        .first()
    )

    if not batch:
        raise HTTPException(409, "The original attendance upload batch was not found")

    now = utc_now()
    reopened = batch.reopened_at is not None

    if now > batch.closes_at and not reopened:
        raise HTTPException(
            403,
            "The 24-hour correction window has closed. A Company Admin must reopen it.",
        )

    new_status = status_from_input(requested_status)

    if ensure_not_on_approved_leave(db, record.employee_id, record.attendance_date):
        if new_status != AttendanceStatus.ON_LEAVE:
            raise HTTPException(
                400,
                "Approved leave prevents changing this status to another value.",
            )

    old_status = record.status

    db.add(
        AttendanceCorrection(
            attendance_id=record.id,
            previous_status=old_status,
            new_status=new_status,
            changed_by=user.id,
            reason=reason.strip(),
        )
    )

    record.status = new_status
    record.last_updated_by = user.id
    record.last_updated_at = now
    record.correction_reason = reason.strip()

    db.commit()
    db.refresh(record)
    return record


def reopen_attendance_batch(
    db: Session,
    user: User,
    batch_id: int,
    reason: str,
):
    if user.role.upper() != "COMPANY_ADMIN":
        raise HTTPException(403, "Only a Company Admin can reopen attendance")

    batch = (
        db.query(AttendanceBatch)
        .filter(
            AttendanceBatch.id == batch_id,
            AttendanceBatch.company_id == user.company_id,
        )
        .first()
    )

    if not batch:
        raise HTTPException(404, "Attendance batch not found")

    now = utc_now()

    batch.reopened_by = user.id
    batch.reopened_at = now
    batch.reopen_reason = reason.strip()

    db.add(
        AttendanceReopenAudit(
            batch_id=batch.id,
            authorized_by=user.id,
            reason=reason.strip(),
        )
    )

    db.commit()
    db.refresh(batch)
    return batch


def get_company_attendance(
    db: Session,
    company_id: int,
    attendance_date: date | None = None,
):
    query = (
        db.query(Attendance)
        .join(Employee, Employee.id == Attendance.employee_id)
        .filter(Employee.company_id == company_id)
    )

    if attendance_date:
        query = query.filter(Attendance.attendance_date == attendance_date)

    return query.order_by(
        Attendance.attendance_date.desc(),
        Attendance.employee_id,
    ).all()


def get_employee_attendance(
    db: Session,
    company_id: int,
    employee_id: int,
):
    return (
        db.query(Attendance)
        .join(Employee, Employee.id == Attendance.employee_id)
        .filter(
            Employee.company_id == company_id,
            Employee.id == employee_id,
        )
        .order_by(Attendance.attendance_date.desc())
        .all()
    )
