from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from src.app.core.dependencies import get_current_user
from src.app.core.rbac import Permission
from src.app.db.database import get_db
from src.app.models.user import User


def require_permission(permission: Permission):

    def permission_checker(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        # Get the permissions belonging to the user's role
        from src.app.core.rbac import ROLE_PERMISSIONS

        user_permissions = ROLE_PERMISSIONS.get(
            current_user.role,
            set()
        )

        # Check whether the user has the required permission
        if permission not in user_permissions:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to perform this action"
            )

        return current_user

    return permission_checker