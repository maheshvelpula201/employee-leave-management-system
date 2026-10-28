from sqlalchemy.orm import Session

from src.app.models.employee_history import EmployeeHistory
from src.app.models.employes import Employee


def create_employee_history(
    db: Session,
    employee_id: int,
    action: str,
    old_value: str | None,
    new_value: str | None,
    company_id: int,
):
    """Add history to the current transaction without committing it."""

    employee = (
        db.query(Employee)
        .filter(
            Employee.id == employee_id,
            Employee.company_id == company_id,
        )
        .first()
    )

    if employee is None:
        return None

    history = EmployeeHistory(
        employee_id=employee.id,
        action=action,
        old_value=old_value,
        new_value=new_value,
    )

    db.add(history)
    db.flush()
    return history


def get_employee_history(
    db: Session,
    employee_id: int,
    company_id: int,
):
    return (
        db.query(EmployeeHistory)
        .join(
            Employee,
            EmployeeHistory.employee_id == Employee.id,
        )
        .filter(
            EmployeeHistory.employee_id == employee_id,
            Employee.company_id == company_id,
        )
        .order_by(EmployeeHistory.changed_at.desc())
        .all()
    )
