from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.app.db.database import get_db
from src.app.models.employes import Employee

from src.app.schemas.leave import (
    LeaveCreate,
    LeaveResponse,
    LeaveStatusUpdate
)

from src.app.services.leave import (
    create_leave_service,
    get_all_leaves_service,
    get_leave_by_id_service,
    update_leave_status_service,
    delete_leave_service,
    get_leaves_by_employee_service
)

from src.app.core.rbac import Permission
from src.app.core.rbac_dependencies import require_permission


router = APIRouter(
    prefix="/leaves",
    tags=["Leaves"]
)


@router.post(
    "/",
    response_model=LeaveResponse
)
def create_leave(
    leave: LeaveCreate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission(
            Permission.VIEW_LEAVES
        )
    )
):
    employee = (
        db.query(Employee)
        .filter(
            Employee.id == leave.employee_id,
            Employee.company_id == current_user.company_id
        )
        .first()
    )

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    return create_leave_service(
        db,
        leave,
        current_user.company_id
    )


@router.get(
    "/",
    response_model=list[LeaveResponse]
)
def get_all_leaves(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission(
            Permission.VIEW_LEAVES
        )
    )
):
    return get_all_leaves_service(
        db,
        current_user.company_id
    )


@router.get(
    "/{leave_id}",
    response_model=LeaveResponse
)
def get_leave_by_id(
    leave_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission(
            Permission.VIEW_LEAVES
        )
    )
):
    return get_leave_by_id_service(
        db,
        leave_id,
        current_user.company_id
    )


@router.patch(
    "/{leave_id}/status",
    response_model=LeaveResponse
)
def update_leave_status(
    leave_id: int,
    leave: LeaveStatusUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission(
            Permission.MANAGE_LEAVES
        )
    )
):
    return update_leave_status_service(
        db,
        leave_id,
        leave.status,
        current_user.company_id
    )


@router.delete(
    "/{leave_id}",
    response_model=LeaveResponse
)
def delete_leave(
    leave_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission(
            Permission.MANAGE_LEAVES
        )
    )
):
    return delete_leave_service(
        db,
        leave_id,
        current_user.company_id
    )


@router.get(
    "/employee/{employee_id}",
    response_model=list[LeaveResponse]
)
def get_leaves_by_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission(
            Permission.VIEW_LEAVES
        )
    )
):
    employee = (
        db.query(Employee)
        .filter(
            Employee.id == employee_id,
            Employee.company_id == current_user.company_id
        )
        .first()
    )

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    return get_leaves_by_employee_service(
        db,
        employee_id,
        current_user.company_id
    )