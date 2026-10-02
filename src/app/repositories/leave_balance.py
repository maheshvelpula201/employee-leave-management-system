from sqlalchemy.orm import Session

from src.app.models.leave_balance import LeaveBalance
from src.app.schemas.leave_balance import LeaveBalanceCreate


def create_leave_balance(
    db: Session,
    balance: LeaveBalanceCreate,
    total_days: int
):
    new_balance = LeaveBalance(
        employee_id=balance.employee_id,
        leave_type=balance.leave_type,
        total_days=total_days,
        used_days=0,
        remaining_days=total_days
    )

    db.add(new_balance)
    db.commit()
    db.refresh(new_balance)

    return new_balance


def get_leave_balances_by_employee(
    db: Session,
    employee_id: int
):
    return (
        db.query(LeaveBalance)
        .filter(LeaveBalance.employee_id == employee_id)
        .all()
    )


def get_leave_balance(
    db: Session,
    employee_id: int,
    leave_type: str
):
    return (
        db.query(LeaveBalance)
        .filter(
            LeaveBalance.employee_id == employee_id,
            LeaveBalance.leave_type == leave_type
        )
        .first()
    )


def deduct_leave_balance(
    db: Session,
    balance: LeaveBalance,
    days: int
):
    balance.used_days += days
    balance.remaining_days -= days

    db.commit()
    db.refresh(balance)

    return balance