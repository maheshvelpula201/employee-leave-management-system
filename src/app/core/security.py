import os
import uuid

from datetime import datetime, timedelta, timezone

import jwt
from argon2 import PasswordHasher
from dotenv import load_dotenv


load_dotenv()


password_hasher = PasswordHasher()


JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

JWT_ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 30

REFRESH_TOKEN_EXPIRE_DAYS = 7


if not JWT_SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY is not set")


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(
    password: str,
    password_hash: str
) -> bool:
    try:
        password_hasher.verify(
            password_hash,
            password
        )
        return True

    except Exception:
        return False


def create_access_token(
    user_id: int,
    role: str,
    company_id: int
):
    expire = datetime.now(
        timezone.utc
    ) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "role": role,
        "company_id": company_id,
        "type": "access",
        "exp": expire
    }

    return jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM
    )


def create_refresh_token(
    user_id: int,
    role: str,
    company_id: int
):
    expire = datetime.now(
        timezone.utc
    ) + timedelta(
        days=REFRESH_TOKEN_EXPIRE_DAYS
    )

    jti = str(uuid.uuid4())

    payload = {
        "sub": str(user_id),
        "role": role,
        "company_id": company_id,
        "type": "refresh",
        "jti": jti,
        "exp": expire
    }

    token = jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM
    )

    return token, jti, expire
