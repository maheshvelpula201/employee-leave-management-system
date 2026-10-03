from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.app.repositories.employee_history import (
    get_employee_history
)


def get_employee_history_service(
    db: Session,
    employee_id: int
):
    history = get_employee_history(
        db,
        employee_id
    )

    if not history:
        raise HTTPException(
            status_code=404,
            detail="No history found for this employee"
        )

    return history
