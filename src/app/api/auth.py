from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.app.db.database import get_db

from src.app.schemas.auth import (
    LoginRequest,
    RefreshTokenRequest,
    LogoutRequest
)

from src.app.services.auth import (
    login_user,
    refresh_access_token,
    logout_user
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/login")
def login(
    data: LoginRequest,
    db: Session = Depends(get_db)
):
    try:
        return login_user(
            db=db,
            data=data
        )

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=401,
            detail=str(error)
        )


@router.post("/refresh")
def refresh(
    data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    try:
        return refresh_access_token(
            db=db,
            refresh_token=data.refresh_token
        )

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=401,
            detail=str(error)
        )


@router.post("/logout")
def logout(
    data: LogoutRequest,
    db: Session = Depends(get_db)
):
    try:
        return logout_user(
            db=db,
            refresh_token=data.refresh_token
        )

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=401,
            detail=str(error)
        )
