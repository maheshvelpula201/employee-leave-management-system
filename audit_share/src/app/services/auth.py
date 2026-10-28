
from datetime import datetime, timezone

import jwt
from sqlalchemy.orm import Session

from src.app.models.user import User
from src.app.models.company import Company
from src.app.models.refresh_token import RefreshToken

from src.app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
)

from src.app.schemas.auth import LoginRequest


def login_user(
    db: Session,
    data: LoginRequest,
):
    # 1. Find the user by email
    user = (
        db.query(User)
        .filter(User.email == data.email)
        .first()
    )

    if not user:
        raise ValueError("Invalid email or password")

    # 2. Check user account status
    if not user.is_active:
        raise ValueError("User account is inactive")

    # 3. Find the user's company
    company = (
        db.query(Company)
        .filter(Company.id == user.company_id)
        .first()
    )

    if not company:
        raise ValueError("Company not found")

    # 4. Make sure the company is operational
    if company.status != "APPROVED":
        raise ValueError("Company is not approved")

    if not company.is_active:
        raise ValueError("Company is not active")

    # 5. Verify password
    if not verify_password(
        data.password,
        user.password_hash,
    ):
        raise ValueError("Invalid email or password")

    # 6. Create access token using the database role
    access_token = create_access_token(
        user_id=user.id,
        role=user.role,
        company_id=user.company_id,
    )

    # 7. Create refresh token using the database role
    refresh_token, jti, expires_at = create_refresh_token(
        user_id=user.id,
        role=user.role,
        company_id=user.company_id,
    )

    # 8. Store refresh token
    refresh_token_record = RefreshToken(
        user_id=user.id,
        token=refresh_token,
        jti=jti,
        expires_at=expires_at,
        is_revoked=False,
    )

    db.add(refresh_token_record)
    db.commit()

    # 9. Return authentication result
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "user_id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "company_id": user.company_id,
            "is_active": user.is_active,
        },
    }


def refresh_access_token(
    db: Session,
    refresh_token: str,
):
    # 1. Decode refresh token
    try:
        payload = jwt.decode(
            refresh_token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
        )
    except jwt.ExpiredSignatureError:
        raise ValueError("Refresh token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid refresh token")

    # 2. Make sure this is a refresh token
    if payload.get("type") != "refresh":
        raise ValueError("Invalid refresh token")

    # 3. Get JTI
    jti = payload.get("jti")

    if not jti:
        raise ValueError("Invalid refresh token payload")

    # 4. Find refresh token in database
    token_record = (
        db.query(RefreshToken)
        .filter(RefreshToken.jti == jti)
        .first()
    )

    if not token_record:
        raise ValueError("Refresh token not found")

    # 5. Make sure the stored token matches
    if token_record.token != refresh_token:
        raise ValueError("Invalid refresh token")

    # 6. Check whether token was revoked
    if token_record.is_revoked:
        raise ValueError("Refresh token has been revoked")

    # 7. Check database expiry
    current_time = datetime.now(timezone.utc)

    if token_record.expires_at.replace(
        tzinfo=timezone.utc
    ) <= current_time:
        raise ValueError("Refresh token has expired")

    # 8. Get user ID
    user_id = payload.get("sub")

    if not user_id:
        raise ValueError("Invalid refresh token payload")

    # 9. Find user
    user = (
        db.query(User)
        .filter(User.id == int(user_id))
        .first()
    )

    if not user:
        raise ValueError("User not found")

    # 10. Make sure account is active
    if not user.is_active:
        raise ValueError("User account is inactive")

    # 11. Find company
    company = (
        db.query(Company)
        .filter(Company.id == user.company_id)
        .first()
    )

    if not company:
        raise ValueError("Company not found")

    # 12. Make sure company is still operational
    if company.status != "APPROVED":
        raise ValueError("Company is not approved")

    if not company.is_active:
        raise ValueError("Company is not active")

    # 13. Revoke the old refresh token
    token_record.is_revoked = True

    # 14. Create a new access token
    access_token = create_access_token(
        user_id=user.id,
        role=user.role,
        company_id=user.company_id,
    )

    # 15. Create a new refresh token
    (
        new_refresh_token,
        new_jti,
        new_expires_at,
    ) = create_refresh_token(
        user_id=user.id,
        role=user.role,
        company_id=user.company_id,
    )

    # 16. Store the new refresh token
    new_refresh_token_record = RefreshToken(
        user_id=user.id,
        token=new_refresh_token,
        jti=new_jti,
        expires_at=new_expires_at,
        is_revoked=False,
    )

    db.add(new_refresh_token_record)

    # 17. Save both changes
    db.commit()

    # 18. Return new tokens
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


def logout_user(
    db: Session,
    refresh_token: str,
):
    # 1. Decode refresh token
    try:
        payload = jwt.decode(
            refresh_token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
        )
    except jwt.ExpiredSignatureError:
        raise ValueError("Refresh token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid refresh token")

    # 2. Make sure this is a refresh token
    if payload.get("type") != "refresh":
        raise ValueError("Invalid refresh token")

    # 3. Get JTI
    jti = payload.get("jti")

    if not jti:
        raise ValueError("Invalid refresh token payload")

    # 4. Find stored refresh token
    token_record = (
        db.query(RefreshToken)
        .filter(RefreshToken.jti == jti)
        .first()
    )

    if not token_record:
        raise ValueError("Refresh token not found")

    # 5. Make sure stored token matches
    if token_record.token != refresh_token:
        raise ValueError("Invalid refresh token")

    # 6. Revoke token
    token_record.is_revoked = True

    db.commit()

    return {
        "message": "Logout successful"
    }
