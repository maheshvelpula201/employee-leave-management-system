from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.app.db.database import get_db

from src.app.schemas.admin import (
    CompanyAdminCreate,
    AdminUpdate,
    AdminStatusUpdate,
    AdminResponse
)

from src.app.services.admin import (
    create_company_admin,
    get_all_admins_service,
    get_admin_by_id_service,
    update_admin_service,
    update_admin_status_service
)

from src.app.core.rbac import Permission
from src.app.core.rbac_dependencies import require_permission


router = APIRouter(
    prefix="/admins",
    tags=["Admins"]
)


# ==========================================
# FIRST ADMIN BOOTSTRAP
# ==========================================

@router.post(
    "/bootstrap/{company_id}"
)
def create_first_admin(
    company_id: int,
    data: CompanyAdminCreate,
    db: Session = Depends(get_db)
):
    try:
        return create_company_admin(
            db=db,
            company_id=company_id,
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
            detail="Failed to create first company admin"
        )


# ==========================================
# GET ALL ADMINS
# ==========================================

@router.get(
    "/",
    response_model=list[AdminResponse]
)
def get_all_admins(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission(
            Permission.VIEW_ADMINS
        )
    )
):
    return get_all_admins_service(
        db,
        current_user.company_id
    )


# ==========================================
# GET ADMIN BY ID
# ==========================================

@router.get(
    "/{admin_id}",
    response_model=AdminResponse
)
def get_admin_by_id(
    admin_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission(
            Permission.VIEW_ADMINS
        )
    )
):
    return get_admin_by_id_service(
        db,
        admin_id,
        current_user.company_id
    )


# ==========================================
# UPDATE ADMIN
# ==========================================

@router.put(
    "/{admin_id}",
    response_model=AdminResponse
)
def update_admin(
    admin_id: int,
    data: AdminUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission(
            Permission.MANAGE_ADMIN
        )
    )
):
    return update_admin_service(
        db,
        admin_id,
        data,
        current_user.company_id
    )


# ==========================================
# UPDATE ADMIN STATUS
# ==========================================

@router.patch(
    "/{admin_id}/status",
    response_model=AdminResponse
)
def update_admin_status(
    admin_id: int,
    data: AdminStatusUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission(
            Permission.MANAGE_ADMIN
        )
    )
):
    return update_admin_status_service(
        db,
        admin_id,
        data,
        current_user.company_id,
        current_user.id
    )