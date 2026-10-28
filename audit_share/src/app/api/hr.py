from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.app.db.database import get_db
from src.app.schemas.hr import HRCreate

from src.app.services.hr import (
    create_hr_service,
    get_all_hrs_service,
    get_hr_by_id_service,
    assign_employee_to_hr_service,
    get_employees_by_hr_service
)

from src.app.core.rbac import Permission
from src.app.core.rbac_dependencies import require_permission


router = APIRouter(
    prefix="/hrs",
    tags=["HR"]
)


@router.post("/")
def create_hr(
    data: HRCreate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission(
            Permission.INVITE_HR
        )
    )
):
    return create_hr_service(
        db,
        data,
        current_user.company_id
    )


@router.get("/")
def get_all_hrs(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission(
            Permission.VIEW_HRS
        )
    )
):
    return get_all_hrs_service(
        db,
        current_user.company_id
    )


@router.get("/{hr_id}")
def get_hr_by_id(
    hr_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission(
            Permission.VIEW_HRS
        )
    )
):
    return get_hr_by_id_service(
        db,
        hr_id,
        current_user.company_id
    )


@router.patch("/{hr_id}/employees/{employee_id}")
def assign_employee_to_hr(
    hr_id: int,
    employee_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission(
            Permission.ASSIGN_EMPLOYEE_HR
        )
    )
):
    return assign_employee_to_hr_service(
        db,
        hr_id,
        employee_id,
        current_user.company_id
    )


@router.get("/{hr_id}/employees")
def get_employees_by_hr(
    hr_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission(
            Permission.VIEW_HRS
        )
    )
):
    return get_employees_by_hr_service(
        db,
        hr_id,
        current_user.company_id
    )