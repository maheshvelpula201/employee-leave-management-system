from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.app.db.database import get_db
from src.app.models.employes import Employee
from src.app.core.dependencies import get_current_user

from src.app.schemas.employee import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeExit
)

from src.app.repositories.employee_history import (
    create_employee_history
)

from src.app.services.employee_history import (
    get_employee_history_service
)


router = APIRouter(
    prefix="/employees",
    tags=["Employees"]
)


@router.post("/")
def create_employee(
    employee: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    new_employee = Employee(
        name=employee.name,
        email=employee.email,
        department=employee.department,
        designation=employee.designation,
        joining_date=employee.joining_date,
        leaving_date=employee.leaving_date,
        termination_reason=employee.termination_reason,
        employment_status=employee.employment_status,
        phone=employee.phone,
        emergency_contact_name=employee.emergency_contact_name,
        emergency_contact_phone=employee.emergency_contact_phone,
        manager_id=employee.manager_id
    )

    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)

    return new_employee


@router.get("/")
def get_all_employees(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return db.query(Employee).all()


@router.get("/{employee_id}")
def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
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

    return employee


@router.put("/{employee_id}")
def update_employee(
    employee_id: int,
    employee_data: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
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

    update_data = employee_data.model_dump(
        exclude_unset=True
    )

    if "email" in update_data:
        existing_employee = (
            db.query(Employee)
            .filter(
                Employee.email == update_data["email"],
                Employee.id != employee_id
            )
            .first()
        )

        if existing_employee:
            raise HTTPException(
                status_code=400,
                detail="Employee with this email already exists"
            )

    for field, value in update_data.items():
        setattr(employee, field, value)

    db.commit()
    db.refresh(employee)

    return employee


@router.patch("/{employee_id}/manager")
def assign_manager(
    employee_id: int,
    manager_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
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

    manager = (
        db.query(Employee)
        .filter(Employee.id == manager_id)
        .first()
    )

    if not manager:
        raise HTTPException(
            status_code=404,
            detail="Manager not found"
        )

    if employee_id == manager_id:
        raise HTTPException(
            status_code=400,
            detail="Employee cannot be their own manager"
        )

    employee.manager_id = manager_id

    db.commit()
    db.refresh(employee)

    return employee


@router.patch("/{employee_id}/status")
def update_employee_status(
    employee_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
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

    if status not in ["ACTIVE", "INACTIVE"]:
        raise HTTPException(
            status_code=400,
            detail="Status must be ACTIVE or INACTIVE"
        )

    old_status = employee.employment_status

    employee.employment_status = status

    db.commit()
    db.refresh(employee)

    create_employee_history(
        db=db,
        employee_id=employee.id,
        action="STATUS_CHANGED",
        old_value=old_status,
        new_value=status
    )

    return {
        "message": "Employee status updated successfully",
        "employee_id": employee.id,
        "old_status": old_status,
        "new_status": employee.employment_status
    }


@router.patch("/{employee_id}/exit")
def employee_exit(
    employee_id: int,
    exit_data: EmployeeExit,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
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

    if employee.employment_status == "INACTIVE":
        raise HTTPException(
            status_code=400,
            detail="Employee is already inactive"
        )

    old_status = employee.employment_status

    employee.employment_status = "INACTIVE"
    employee.leaving_date = exit_data.leaving_date
    employee.termination_reason = exit_data.termination_reason

    db.commit()
    db.refresh(employee)

    create_employee_history(
        db=db,
        employee_id=employee.id,
        action="EMPLOYEE_EXIT",
        old_value=old_status,
        new_value="INACTIVE"
    )

    return {
        "message": "Employee exit processed successfully",
        "employee_id": employee.id,
        "employment_status": employee.employment_status,
        "leaving_date": employee.leaving_date,
        "termination_reason": employee.termination_reason
    }


@router.get("/{employee_id}/history")
def get_employee_history(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return get_employee_history_service(
        db,
        employee_id
    )