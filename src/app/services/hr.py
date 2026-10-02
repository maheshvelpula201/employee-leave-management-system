from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.app.models.employes import Employee
from src.app.schemas.hr import HRCreate

from src.app.repositories.hr import (
    create_hr,
    get_all_hrs,
    get_hr_by_id,
    get_hr_by_email,
    assign_employee_to_hr,
    get_employees_by_hr
)


def create_hr_service(
    db: Session,
    hr: HRCreate
):
    existing_hr = get_hr_by_email(
        db,
        hr.email
    )

    if existing_hr:
        raise HTTPException(
            status_code=400,
            detail="HR with this email already exists"
        )

    return create_hr(
        db,
        hr.name,
        hr.email
    )


def get_all_hrs_service(db: Session):
    return get_all_hrs(db)


def get_hr_by_id_service(
    db: Session,
    hr_id: int
):
    hr = get_hr_by_id(
        db,
        hr_id
    )

    if not hr:
        raise HTTPException(
            status_code=404,
            detail="HR not found"
        )

    return hr


def assign_employee_to_hr_service(
    db: Session,
    hr_id: int,
    employee_id: int
):
    hr = get_hr_by_id(
        db,
        hr_id
    )

    if not hr:
        raise HTTPException(
            status_code=404,
            detail="HR not found"
        )

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

    return assign_employee_to_hr(
        db,
        employee,
        hr
    )


def get_employees_by_hr_service(
    db: Session,
    hr_id: int
):
    hr = get_hr_by_id(
        db,
        hr_id
    )

    if not hr:
        raise HTTPException(
            status_code=404,
            detail="HR not found"
        )

    return get_employees_by_hr(
        db,
        hr_id
    )