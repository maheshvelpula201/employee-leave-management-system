from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from src.app.core.dependencies import get_current_user
from src.app.core.rbac import Permission
from src.app.db.database import get_db
from src.app.models.user import User
from src.app.schemas.invitation import InvitationCreate


def require_permission(permission: Permission):

    def permission_checker(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        from src.app.core.rbac import ROLE_PERMISSIONS

        user_permissions = ROLE_PERMISSIONS.get(
            current_user.role,
            set()
        )

        if permission not in user_permissions:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to perform this action"
            )

        return current_user

    return permission_checker


def require_invitation_permission(
    data: InvitationCreate,
    current_user: User = Depends(get_current_user)
):
    invitation_permissions = {
        "COMPANY_ADMIN": Permission.INVITE_ADMIN,
        "HR": Permission.INVITE_HR,
        "MANAGER": Permission.INVITE_MANAGER,
        "EMPLOYEE": Permission.INVITE_EMPLOYEE
    }

    role = data.role.upper()

    required_permission = invitation_permissions.get(
        role
    )

    if not required_permission:
        raise HTTPException(
            status_code=400,
            detail="Invalid invitation role"
        )

    from src.app.core.rbac import ROLE_PERMISSIONS

    user_permissions = ROLE_PERMISSIONS.get(
        current_user.role,
        set()
    )

    if required_permission not in user_permissions:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to invite this role"
        )

    return current_user