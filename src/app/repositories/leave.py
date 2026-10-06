from sqlalchemy.orm import Session

from src.app.models.leave import Leave
from src.app.models.employes import Employee
from src.app.schemas.leave import LeaveCreate


def create_leave(
    db: Session,
    leave: LeaveCreate,
    company_id: int
):
    employee = (
        db.query(Employee)
        .filter(
            Employee.id == leave.employee_id,
            Employee.company_id == company_id
        )
        .first()
    )

    if not employee:
        return None

    new_leave = Leave(
        employee_id=leave.employee_id,
        leave_type=leave.leave_type,
        start_date=leave.start_date,
        end_date=leave.end_date,
        reason=leave.reason
    )

    db.add(new_leave)
    db.commit()
    db.refresh(new_leave)

    return new_leave


def get_all_leaves(
    db: Session,
    company_id: int
):
    return (
        db.query(Leave)
        .join(
            Employee,
            Leave.employee_id == Employee.id
        )
        .filter(
            Employee.company_id == company_id
        )
        .all()
    )


def get_leave_by_id(
    db: Session,
    leave_id: int,
    company_id: int
):
    return (
        db.query(Leave)
        .join(
            Employee,
            Leave.employee_id == Employee.id
        )
        .filter(
            Leave.id == leave_id,
            Employee.company_id == company_id
        )
        .first()
    )


def update_leave_status(
    db: Session,
    leave_id: int,
    status: str,
    company_id: int
):
    leave = (
        db.query(Leave)
        .join(
            Employee,
            Leave.employee_id == Employee.id
        )
        .filter(
            Leave.id == leave_id,
            Employee.company_id == company_id
        )
        .first()
    )

    if leave:
        leave.status = status
        db.commit()
        db.refresh(leave)

    return leave


def delete_leave(
    db: Session,
    leave_id: int,
    company_id: int
):
    leave = (
        db.query(Leave)
        .join(
            Employee,
            Leave.employee_id == Employee.id
        )
        .filter(
            Leave.id == leave_id,
            Employee.company_id == company_id
        )
        .first()
    )

    if leave:
        db.delete(leave)
        db.commit()

    return leave


def get_leaves_by_employee(
    db: Session,
    employee_id: int,
    company_id: int
):
    return (
        db.query(Leave)
        .join(
            Employee,
            Leave.employee_id == Employee.id
        )
        .filter(
            Leave.employee_id == employee_id,
            Employee.company_id == company_id
        )
        .all()
    )


def get_overlapping_leave(
    db: Session,
    employee_id: int,
    start_date,
    end_date,
    company_id: int
):
    return (
        db.query(Leave)
        .join(
            Employee,
            Leave.employee_id == Employee.id
        )
        .filter(
            Leave.employee_id == employee_id,
            Employee.company_id == company_id,
            Leave.start_date <= end_date,
            Leave.end_date >= start_date
        )
        .first()
    )