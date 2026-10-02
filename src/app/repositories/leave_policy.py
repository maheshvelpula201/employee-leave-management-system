from sqlalchemy.orm import Session

from src.app.models.leave_policy import LeavePolicy
from src.app.schemas.leave_policy import LeavePolicyCreate


def create_leave_policy(
    db: Session,
    policy: LeavePolicyCreate
):
    new_policy = LeavePolicy(
        leave_type=policy.leave_type,
        annual_days=policy.annual_days,
        year=policy.year
    )

    db.add(new_policy)
    db.commit()
    db.refresh(new_policy)

    return new_policy


def get_leave_policies(
    db: Session,
    year: int
):
    return (
        db.query(LeavePolicy)
        .filter(LeavePolicy.year == year)
        .all()
    )


def get_leave_policy(
    db: Session,
    leave_type: str,
    year: int
):
    return (
        db.query(LeavePolicy)
        .filter(
            LeavePolicy.leave_type == leave_type,
            LeavePolicy.year == year
        )
        .first()
    )