from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

import jwt

from src.app.db.database import get_db
from src.app.models.user import User
from src.app.core.security import (
    JWT_SECRET_KEY,
    JWT_ALGORITHM
)


security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    # 1. Get the JWT

    token = credentials.credentials

    # 2. Verify and decode the JWT

    try:

        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM]
        )

    except jwt.ExpiredSignatureError:

        raise HTTPException(
            status_code=401,
            detail="Token has expired"
        )

    except jwt.InvalidTokenError:

        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    # 3. Make sure this is an access token

    if payload.get("type") != "access":

        raise HTTPException(
            status_code=401,
            detail="Invalid access token"
        )

    # 4. Get the user ID from the token

    user_id = payload.get("sub")

    if not user_id:

        raise HTTPException(
            status_code=401,
            detail="Invalid token payload"
        )

    # 5. Find the actual user in the database

    user = (
        db.query(User)
        .filter(User.id == int(user_id))
        .first()
    )

    if not user:

        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    # 6. Check whether the account is still active

    if not user.is_active:

        raise HTTPException(
            status_code=401,
            detail="User account is inactive"
        )

    # 7. Return the actual database user

    return user