from sqlalchemy.orm import Session

from src.app.models.employee_history import EmployeeHistory


def create_employee_history(
    db: Session,
    employee_id: int,
    action: str,
    old_value: str | None,
    new_value: str | None
):
    history = EmployeeHistory(
        employee_id=employee_id,
        action=action,
        old_value=old_value,
        new_value=new_value
    )

    db.add(history)
    db.commit()
    db.refresh(history)

    return history


def get_employee_history(
    db: Session,
    employee_id: int
):
    return (
        db.query(EmployeeHistory)
        .filter(
            EmployeeHistory.employee_id == employee_id
        )
        .order_by(
            EmployeeHistory.changed_at.desc()
        )
        .all()
    )

