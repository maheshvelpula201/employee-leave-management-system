from fastapi import APIRouter, Depends

from src.app.core.dependencies import get_current_user
from src.app.models.user import User


router = APIRouter(
    prefix="/test-auth",
    tags=["Authentication Test"]
)


@router.get("/protected")
def protected_route(
    current_user: User = Depends(get_current_user)
):
    return {
        "message": "You are authenticated",
        "current_user": {
            "user_id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "role": current_user.role,
            "company_id": current_user.company_id,
            "is_active": current_user.is_active
        }
    }
