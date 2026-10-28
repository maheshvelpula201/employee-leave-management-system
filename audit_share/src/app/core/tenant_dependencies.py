from fastapi import Depends

from src.app.core.dependencies import get_current_user
from src.app.models.user import User


def get_current_company_id(
    current_user: User = Depends(get_current_user)
) -> int:
    return current_user.company_id