
from datetime import date

from sqlalchemy.orm import Session

from src.app.models.attendance import Attendance
from src.app.models.employes import Employee
from src.app.schemas.attendance import AttendanceMark


def mark_attendance(
    db: Session,
    company_id: int,
    data: AttendanceMark,
) -> Attendance:
    employee = (
        db.query(Employee)
        .filter(
            Employee.id == data.employee_id,
            Employee.company_id == company_id,
        )
        .first()
    )

    if employee is None:
        raise ValueError("Employee not found in this company")

    record = (
        db.query(Attendance)
        .filter(
            Attendance.employee_id == data.employee_id,
            Attendance.attendance_date == data.attendance_date,
        )
        .first()
    )

    if record:
        record.status = data.status
        record.notes = data.notes
    else:
        record = Attendance(
            employee_id=data.employee_id,
            attendance_date=data.attendance_date,
            status=data.status,
            notes=data.notes,
        )
        db.add(record)

    db.commit()
    db.refresh(record)

    return record


def get_company_attendance(
    db: Session,
    company_id: int,
    attendance_date: date | None = None,
) -> list[Attendance]:
    query = (
        db.query(Attendance)
        .join(Employee, Employee.id == Attendance.employee_id)
        .filter(Employee.company_id == company_id)
    )

    if attendance_date is not None:
        query = query.filter(
            Attendance.attendance_date == attendance_date
        )

    return query.order_by(
        Attendance.attendance_date.desc(),
        Attendance.employee_id,
    ).all()


def get_employee_attendance(
    db: Session,
    company_id: int,
    employee_id: int,
) -> list[Attendance]:
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
