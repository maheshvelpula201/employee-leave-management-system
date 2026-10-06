from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.app.db.database import get_db
from src.app.schemas.admin import CompanyAdminCreate
from src.app.services.admin import create_company_admin

from src.app.core.rbac import Permission
from src.app.core.rbac_dependencies import require_permission


router = APIRouter(
    prefix="/companies",
    tags=["Company Admin"]
)


@router.post("/{company_id}/admins")
def create_admin(
    company_id: int,
    data: CompanyAdminCreate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission(
            Permission.INVITE_ADMIN
        )
    )
):
    if company_id != current_user.company_id:
        raise HTTPException(
            status_code=403,
            detail="You cannot manage another company"
        )

    try:
        return create_company_admin(
            db=db,
            company_id=current_user.company_id,
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
            detail="Failed to create company admin"
        )