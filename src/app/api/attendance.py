
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.app.db.database import get_db
from src.app.core.rbac import Permission
from src.app.core.rbac_dependencies import require_permission

from src.app.schemas.attendance import AttendanceMark, AttendanceResponse
from src.app.services.attendance import (
    mark_attendance,
    get_company_attendance,
    get_employee_attendance,
)


router = APIRouter(
    prefix="/attendance",
    tags=["Attendance"],
)


@router.post("/mark", response_model=AttendanceResponse)
def mark_attendance_endpoint(
    data: AttendanceMark,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission(Permission.MANAGE_ATTENDANCE)
    ),
):
    try:
        return mark_attendance(
            db=db,
            company_id=current_user.company_id,
            data=data,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )


@router.get("/", response_model=list[AttendanceResponse])
def get_attendance_endpoint(
    attendance_date: date | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission(Permission.VIEW_ATTENDANCE)
    ),
):
    return get_company_attendance(
        db=db,
        company_id=current_user.company_id,
        attendance_date=attendance_date,
    )


@router.get(
    "/employee/{employee_id}",
    response_model=list[AttendanceResponse],
)
def get_employee_attendance_endpoint(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission(Permission.VIEW_ATTENDANCE)
    ),
):
    return get_employee_attendance(
        db=db,
        company_id=current_user.company_id,
        employee_id=employee_id,
    )
