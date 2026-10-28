
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.app.db.database import get_db
from src.app.models.hr import HR
from src.app.models.employes import Employee
from src.app.core.rbac import Permission
from src.app.core.rbac_dependencies import require_permission
from src.app.schemas.hr import HRCreate, HRResponse
from src.app.core.dependencies import get_current_user


router = APIRouter(
    prefix="/hr",
    tags=["HR"],
)


@router.post("/", response_model=HRResponse)
def create_hr(
    hr_data: HRCreate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission(Permission.MANAGE_HR)
    ),
):
    existing_hr = (
        db.query(HR)
        .filter(
            HR.email == hr_data.email,
            HR.company_id == current_user.company_id,
        )
        .first()
    )

    if existing_hr:
        raise HTTPException(
            status_code=400,
            detail="HR member with this email already exists",
        )

    new_hr = HR(
        name=hr_data.name,
        email=hr_data.email,
        company_id=current_user.company_id,
    )

    db.add(new_hr)

    try:
        db.commit()
        db.refresh(new_hr)
    except Exception:
        db.rollback()
        raise

    return new_hr


@router.get("/", response_model=list[HRResponse])
def get_all_hr(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission(Permission.VIEW_HRS)
    ),
):
    return (
        db.query(HR)
        .filter(HR.company_id == current_user.company_id)
        .order_by(HR.name.asc())
        .all()
    )


@router.get("/{hr_id}", response_model=HRResponse)
def get_hr(
    hr_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission(Permission.VIEW_HRS)
    ),
):
    hr_member = (
        db.query(HR)
        .filter(
            HR.id == hr_id,
            HR.company_id == current_user.company_id,
        )
        .first()
    )

    if not hr_member:
        raise HTTPException(
            status_code=404,
            detail="HR member not found",
        )

    return hr_member
