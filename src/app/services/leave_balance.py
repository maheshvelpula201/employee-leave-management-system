from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.app.models.employes import Employee
from src.app.repositories.leave_balance import (
    create_leave_balance,
    get_leave_balances_by_employee
)
from src.app.repositories.leave_policy import get_leave_policy
from src.app.schemas.leave_balance import LeaveBalanceCreate


def create_leave_balance_service(
    db: Session,
    balance: LeaveBalanceCreate
):
    employee = (
        db.query(Employee)
        .filter(Employee.id == balance.employee_id)
        .first()
    )

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    policy = get_leave_policy(
        db,
        balance.leave_type,
        balance.year
    )

    if not policy:
        raise HTTPException(
            status_code=404,
            detail="Leave policy not found"
        )

    return create_leave_balance(
        db,
        balance,
        policy.annual_days
    )


def get_leave_balances_by_employee_service(
    db: Session,
    employee_id: int
):
    employee = (
        db.query(Employee)
        .filter(Employee.id == employee_id)
        .first()
    )

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    return get_leave_balances_by_employee(
        db,
        employee_id
    )