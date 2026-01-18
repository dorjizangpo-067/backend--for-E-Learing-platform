import jwt
from fastapi import Request, Depends, HTTPException, status
from sqlmodel import Session
from typing import Annotated

from jwt.exceptions import ExpiredSignatureError, InvalidTokenError, InvalidSignatureError
from .database import engine
from .env_loader import settings

        

def get_session():
    with Session(engine) as session:
        yield session

def verify_access_token(token: str, secret_key: str, algorithms: list[str]) -> dict | None:
    """Verify a JWT access token and return the payload if valid."""
    try:
        data = jwt.decode(token, secret_key, algorithms=algorithms)
        return data
    except ExpiredSignatureError:
        return None
    except InvalidSignatureError:
        return None
    except InvalidTokenError:
        return None

def get_current_user(request: Request, secret_key: str, algorithms: list[str]) -> dict | None:
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
        print("Current User:", user)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    request.state.user = user
    return user

# get current_user_role
async def current_user_role(current_user: Annotated[dict, Depends(current_user_dependency)]) -> str:
    role = current_user.get("role")
    return role

async def is_teacher_or_admin(current_role: Annotated[str, Depends(current_user_role)]):
    if current_role not in ["teacher", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation not permitted"
        )
    return True

async def is_admin(current_role: Annotated[str, Depends(current_user_role)] = current_user_role):
    if current_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation not permitted"
        )
    return True
