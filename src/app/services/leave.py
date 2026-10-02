from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.app.models.employes import Employee

from src.app.repositories.leave import (
    create_leave,
    get_all_leaves,
    get_leave_by_id,
    update_leave_status,
    delete_leave,
    get_leaves_by_employee,
    get_overlapping_leave
)

from src.app.repositories.leave_balance import (
    get_leave_balance,
    deduct_leave_balance
)

from src.app.schemas.leave import LeaveCreate


def create_leave_service(db: Session, leave: LeaveCreate):
    employee = (
        db.query(Employee)
        .filter(Employee.id == leave.employee_id)
        .first()
    )

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    existing_leave = get_overlapping_leave(
        db,
        leave.employee_id,
        leave.start_date,
        leave.end_date
    )

    if existing_leave:
        raise HTTPException(
            status_code=400,
            detail="Leave dates overlap with an existing leave"
        )

    return create_leave(db, leave)


def get_all_leaves_service(db: Session):
    return get_all_leaves(db)


def get_leave_by_id_service(db: Session, leave_id: int):
    leave = get_leave_by_id(db, leave_id)

    if not leave:
        raise HTTPException(
            status_code=404,
            detail="Leave not found"
        )

    return leave


def update_leave_status_service(
    db: Session,
    leave_id: int,
    status: str
):
    leave = get_leave_by_id(db, leave_id)

    if not leave:
        raise HTTPException(
            status_code=404,
            detail="Leave not found"
        )

    if leave.status != "Pending":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot change status from {leave.status}"
        )

    if status == "Approved":

        days = (leave.end_date - leave.start_date).days + 1

        balance = get_leave_balance(
            db,
            leave.employee_id,
            leave.leave_type
        )

        if not balance:
            raise HTTPException(
                status_code=404,
                detail="Leave balance not found"
            )

        if balance.remaining_days < days:
            raise HTTPException(
                status_code=400,
                detail="Insufficient leave balance"
            )

        deduct_leave_balance(
            db,
            balance,
            days
        )

    return update_leave_status(
        db,
        leave_id,
        status
    )


def delete_leave_service(db: Session, leave_id: int):
    leave = get_leave_by_id(db, leave_id)

    if not leave:
        raise HTTPException(
            status_code=404,
            detail="Leave not found"
        )

    if leave.status != "Pending":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete a {leave.status} leave"
        )

    return delete_leave(db, leave_id)


def get_leaves_by_employee_service(
    db: Session,
    employee_id: int
):
    return get_leaves_by_employee(
        db,
        employee_id
    )