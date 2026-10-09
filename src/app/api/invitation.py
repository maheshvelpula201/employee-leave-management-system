from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.app.db.database import get_db

from src.app.schemas.invitation import (
    InvitationCreate,
    InvitationAccept,
    InvitationResponse
)

from src.app.services.invitation import (
    create_invitation_service,
    get_all_invitations_service,
    accept_invitation_service
)

from src.app.core.rbac_dependencies import (
    require_invitation_permission,
    require_permission
)

from src.app.core.rbac import Permission


router = APIRouter(
    prefix="/invitations",
    tags=["Invitations"]
)


@router.post("/")
def create_invitation(
    data: InvitationCreate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_invitation_permission
    )
):
    return create_invitation_service(
        db=db,
        data=data,
        company_id=current_user.company_id
    )


@router.get(
    "/",
    response_model=list[InvitationResponse]
)
def get_all_invitations(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission(
            Permission.VIEW_COMPANY
        )
    )
):
    return get_all_invitations_service(
        db=db,
        company_id=current_user.company_id
    )


@router.post("/accept")
def accept_invitation(
    data: InvitationAccept,
    db: Session = Depends(get_db)
):
    return accept_invitation_service(
        db=db,
        data=data
    )