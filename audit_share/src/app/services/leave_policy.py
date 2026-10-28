from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.app.repositories.leave_policy import (
    create_leave_policy,
    get_leave_policies,
    get_leave_policy
)

from src.app.schemas.leave_policy import LeavePolicyCreate


def create_leave_policy_service(
    db: Session,
    policy: LeavePolicyCreate
):
    existing_policy = get_leave_policy(
        db,
        policy.leave_type,
        policy.year
    )

    if existing_policy:
        raise HTTPException(
            status_code=400,
            detail="Leave policy already exists for this leave type and year"
        )

    return create_leave_policy(db, policy)


def get_leave_policies_service(
    db: Session,
    year: int
):
    return get_leave_policies(db, year)