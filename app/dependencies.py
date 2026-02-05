from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Request, status
from jwt.exceptions import (
    ExpiredSignatureError,
    InvalidSignatureError,
    InvalidTokenError,
)
from sqlmodel import Session

from .database import engine
from .env_loader import settings


def get_session() -> Session:  # type: ignore
    with Session(engine) as session:
        yield session  # type: ignore


def verify_access_token(
    token: str, secret_key: str, algorithms: list[str]
) -> dict | None:
    """Verify a JWT access token and return the payload if valid."""
    try:
        return jwt.decode(token, secret_key, algorithms=algorithms)
    except ExpiredSignatureError:
        return None
    except InvalidSignatureError:
        return None
    except InvalidTokenError:
        return None


def get_current_user(
    request: Request, secret_key: str, algorithms: list[str]
) -> dict | None:
    """Get the current user from the JWT token."""
    try:
        token = request.cookies.get("access_token")
    except AttributeError:
        return None
    if not token:
        return None
    payload = verify_access_token(token, secret_key, algorithms)
    if payload is None:
        return None
    return payload


async def current_user_dependency(request: Request) -> dict | None:
    user = get_current_user(request, settings.secret_key, [settings.algorithm])
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    request.state.user = user
    return user


# get current_user_role
async def current_user_role(
    current_user: Annotated[dict, Depends(current_user_dependency)],
) -> str | None:
    return current_user.get("role")


async def is_teacher_or_admin(
    current_role: Annotated[str, Depends(current_user_role)],
) -> bool:
    if current_role not in ["teacher", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Operation not permitted"
        )
        return False
    return True


async def is_admin(current_role: Annotated[str, Depends(current_user_role)]) -> bool:
    if current_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Operation not permitted"
        )
    return True
