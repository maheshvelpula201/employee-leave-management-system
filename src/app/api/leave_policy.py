from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.app.db.database import get_db

from src.app.schemas.leave_policy import (
    LeavePolicyCreate,
    LeavePolicyResponse
)

from src.app.services.leave_policy import (
    create_leave_policy_service,
    get_leave_policies_service
)


router = APIRouter(
    prefix="/leave-policies",
    tags=["Leave Policies"]
)


@router.post(
    "/",
    response_model=LeavePolicyResponse
)
def create_leave_policy(
    policy: LeavePolicyCreate,
    db: Session = Depends(get_db)
):
    return create_leave_policy_service(db, policy)


@router.get(
    "/{year}",
    response_model=list[LeavePolicyResponse]
)
def get_leave_policies(
    year: int,
    db: Session = Depends(get_db)
):
    return get_leave_policies_service(db, year)