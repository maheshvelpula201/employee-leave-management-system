from sqlalchemy.orm import Session

from src.app.models.employes import Employee
from src.app.models.hr import HR


def create_hr(
    db: Session,
    name: str,
    email: str
):
    new_hr = HR(
        name=name,
        email=email
    )

    db.add(new_hr)
    db.commit()
    db.refresh(new_hr)

    return new_hr


def get_all_hrs(db: Session):
    return db.query(HR).all()


def get_hr_by_id(
    db: Session,
    hr_id: int
):
    return (
        db.query(HR)
        .filter(HR.id == hr_id)
        .first()
    )


def get_hr_by_email(
    db: Session,
    email: str
):
    return (
        db.query(HR)
        .filter(HR.email == email)
        .first()
    )


def assign_employee_to_hr(
    db: Session,
    employee: Employee,
    hr: HR
):
    employee.hr_id = hr.id

    db.commit()
    db.refresh(employee)

    return employee


def get_employees_by_hr(
    db: Session,
    hr_id: int
):
    return (
        db.query(Employee)
        .filter(Employee.hr_id == hr_id)
        .all()
    )