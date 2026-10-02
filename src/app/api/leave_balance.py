from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.app.db.database import get_db
from src.app.schemas.leave_balance import (
    LeaveBalanceCreate,
    LeaveBalanceResponse
)
from src.app.services.leave_balance import (
    create_leave_balance_service,
    get_leave_balances_by_employee_service
)


router = APIRouter(
    prefix="/leave-balances",
    tags=["Leave Balances"]
)


@router.post(
    "/",
    response_model=LeaveBalanceResponse
)
def create_leave_balance(
    balance: LeaveBalanceCreate,
    db: Session = Depends(get_db)
):
    return create_leave_balance_service(
        db,
        balance
    )


@router.get(
    "/employee/{employee_id}",
    response_model=list[LeaveBalanceResponse]
)
def get_leave_balances_by_employee(
    employee_id: int,
    db: Session = Depends(get_db)
):
    return get_leave_balances_by_employee_service(
        db,
        employee_id
    )