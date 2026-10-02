from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.app.db.database import get_db

from src.app.schemas.hr import (
    HRCreate,
    HRResponse
)

from src.app.services.hr import (
    create_hr_service,
    get_all_hrs_service,
    get_hr_by_id_service,
    assign_employee_to_hr_service,
    get_employees_by_hr_service
)


router = APIRouter(
    prefix="/hrs",
    tags=["HR"]
)


@router.post(
    "/",
    response_model=HRResponse
)
def create_hr(
    hr: HRCreate,
    db: Session = Depends(get_db)
):
    return create_hr_service(
        db,
        hr
    )


@router.get(
    "/",
    response_model=list[HRResponse]
)
def get_all_hrs(
    db: Session = Depends(get_db)
):
    return get_all_hrs_service(db)


@router.get(
    "/{hr_id}",
    response_model=HRResponse
)
def get_hr_by_id(
    hr_id: int,
    db: Session = Depends(get_db)
):
    return get_hr_by_id_service(
        db,
        hr_id
    )


@router.post(
    "/{hr_id}/employees/{employee_id}"
)
def assign_employee_to_hr(
    hr_id: int,
    employee_id: int,
    db: Session = Depends(get_db)
):
    return assign_employee_to_hr_service(
        db,
        hr_id,
        employee_id
    )


@router.get(
    "/{hr_id}/employees"
)
def get_employees_by_hr(
    hr_id: int,
    db: Session = Depends(get_db)
):
    return get_employees_by_hr_service(
        db,
        hr_id
    )