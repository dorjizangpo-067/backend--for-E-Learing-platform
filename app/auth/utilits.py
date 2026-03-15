from __future__ import annotations

from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from pwdlib import PasswordHash
from pydantic import SecretStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..env_loader import settings
from ..models.users import User

hashed_hasdher = PasswordHash.recommended()


def hash_password(plain_password: str) -> str:
    """hash plain password"""
    return hashed_hasdher.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """verify plain password with hashed password"""
    return hashed_hasdher.verify(plain_password, hashed_password)


def create_access_token(
    data: dict,
    secret_key: SecretStr,
    algorithm: str,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret_key.get_secret_value(), algorithm)


# Utils for login endpoint
async def authenticate_user(db: AsyncSession, email: str, password: str) -> User:
    statement = select(User).where(User.email == email)
    result = await db.execute(statement)
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    return user


def create_user_token(user: User) -> str:
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    return create_access_token(
        data={
            "sub": str(user.email),
            "role": str(user.role),
            "id": str(user.id),
            "name": user.name,
        },
        secret_key=settings.secret_key,
        algorithm=settings.algorithm,
        expires_delta=access_token_expires,
    )


def build_login_response(token: str) -> JSONResponse:
    response = JSONResponse(content={"message": "Successfully logged in"})
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,  # TODO: True in production
        samesite="lax",
        max_age=settings.access_token_expire_minutes * 60,
    )
    return response
