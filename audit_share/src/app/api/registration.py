from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.app.db.database import get_db
from src.app.schemas.registration import CompanyRegistration
from src.app.services.registration import register_company


router = APIRouter(
    prefix="/registration",
    tags=["Registration"]
)


@router.post("/")
def register_company_account(
    data: CompanyRegistration,
    db: Session = Depends(get_db)
):
    try:
        return register_company(
            db=db,
            data=data
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
            detail="Company registration failed"
        )