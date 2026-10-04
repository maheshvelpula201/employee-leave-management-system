from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.app.db.database import get_db
from src.app.schemas.company import CompanyStatusUpdate
from src.app.services.company import (
    update_company_status,
    activate_company
)


router = APIRouter(
    prefix="/companies",
    tags=["Companies"]
)


@router.patch("/{company_id}/status")
def change_company_status(
    company_id: int,
    data: CompanyStatusUpdate,
    db: Session = Depends(get_db)
):
    try:
        return update_company_status(
            db=db,
            company_id=company_id,
            new_status=data.status
        )

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Failed to update company status"
        )


@router.patch("/{company_id}/activate")
def activate_company_account(
    company_id: int,
    db: Session = Depends(get_db)
):
    try:
        return activate_company(
            db=db,
            company_id=company_id
        )

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Failed to activate company"
        )