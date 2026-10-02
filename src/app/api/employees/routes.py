from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.app.db.database import get_db
from src.app.models.employes import Employee
from src.app.schemas.employee import EmployeeCreate


router = APIRouter(
    prefix="/employees",
    tags=["Employees"]
)


@router.post("/")
def create_employee(
    employee: EmployeeCreate,
    db: Session = Depends(get_db)
):
    new_employee = Employee(
        name=employee.name,
        email=employee.email,
        department=employee.department,
        manager_id=employee.manager_id
    )

    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)

    return new_employee


@router.patch("/{employee_id}/manager")
def assign_manager(
    employee_id: int,
    manager_id: int,
    db: Session = Depends(get_db)
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