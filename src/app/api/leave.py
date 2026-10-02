from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.app.db.database import get_db
from src.app.schemas.leave import LeaveCreate, LeaveResponse, LeaveStatusUpdate
from src.app.services.leave import (
    create_leave_service,
    get_all_leaves_service,
    get_leave_by_id_service,
    update_leave_status_service,
    delete_leave_service,
    get_leaves_by_employee_service
)

router = APIRouter(prefix="/leaves", tags=["Leaves"])


@router.post("/", response_model=LeaveResponse)
def create_leave(leave: LeaveCreate, db: Session = Depends(get_db)):
    return create_leave_service(db, leave)


@router.get("/", response_model=list[LeaveResponse])
def get_all_leaves(db: Session = Depends(get_db)):
    return get_all_leaves_service(db)

@router.get("/{leave_id}", response_model=LeaveResponse)
def get_leave_by_id(leave_id: int, db: Session = Depends(get_db)):
    return get_leave_by_id_service(db, leave_id)

@router.patch("/{leave_id}/status", response_model=LeaveResponse)
def update_leave_status(
    leave_id: int,
    leave: LeaveStatusUpdate,
    db: Session = Depends(get_db)
):
    return update_leave_status_service(db, leave_id, leave.status)

@router.delete("/{leave_id}", response_model=LeaveResponse)
def delete_leave(leave_id: int, db: Session = Depends(get_db)):
    return delete_leave_service(db, leave_id)

@router.get("/employee/{employee_id}", response_model=list[LeaveResponse])
def get_leaves_by_employee(
    employee_id: int,
    db: Session = Depends(get_db)
):
    return get_leaves_by_employee_service(db, employee_id)