from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.app.db.database import get_db

from src.app.schemas.invitation import (
    InvitationCreate
)

from src.app.services.invitation import (
    create_invitation_service
)

from src.app.core.rbac_dependencies import (
    require_invitation_permission
)


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