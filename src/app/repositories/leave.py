from sqlalchemy.orm import Session

from src.app.models.leave import Leave
from src.app.schemas.leave import LeaveCreate


def create_leave(db: Session, leave: LeaveCreate):
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


def get_all_leaves(db: Session):
    return db.query(Leave).all()


def get_leave_by_id(db: Session, leave_id: int):
    return (
        db.query(Leave)
        .filter(Leave.id == leave_id)
        .first()
    )


def update_leave_status(
    db: Session,
    leave_id: int,
    status: str
):
    leave = (
        db.query(Leave)
        .filter(Leave.id == leave_id)
        .first()
    )

    if leave:
        leave.status = status
        db.commit()
        db.refresh(leave)

    return leave


def delete_leave(db: Session, leave_id: int):
    leave = (
        db.query(Leave)
        .filter(Leave.id == leave_id)
        .first()
    )

    if leave:
        db.delete(leave)
        db.commit()

    return leave


def get_leaves_by_employee(
    db: Session,
    employee_id: int
):
    return (
        db.query(Leave)
        .filter(Leave.employee_id == employee_id)
        .all()
    )


def get_overlapping_leave(
    db: Session,
    employee_id: int,
    start_date,
    end_date
):
    return (
        db.query(Leave)
        .filter(
            Leave.employee_id == employee_id,
            Leave.start_date <= end_date,
            Leave.end_date >= start_date
        )
        .first()
    )