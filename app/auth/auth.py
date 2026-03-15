from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..dependencies import current_user_dependency
from ..env_loader import settings
from ..limiter import limiter
from ..models.users import User
from ..schemas.user import UserCreateSchema, UserLoginSchema, UserReadSchema
from .utilits import (
    create_access_token,
    verify_password,
)
from .utilits import (
    hash_password as func_hash_password,
)

router = APIRouter(prefix="/auth", tags=["auth"])


# reginster user
@router.post(
    "/register", response_model=UserReadSchema, status_code=status.HTTP_201_CREATED
)
@limiter.limit("5/minute")
async def register_user(
    request: Request,
    register_data: UserCreateSchema,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """
    User registration endpoint <br>

    :param **register_data**: form data containing user registration details <br>
    :type **session**: database session dependency <br>
    """
    # Copy register_data to modify
    user_form = register_data.model_copy()

    if user_form.role == "admin" and user_form.email != settings.admin_email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to create an Admin account.",
        )
    # password hashing
    hash_password = func_hash_password(register_data.password)
    user_data = register_data.model_dump(exclude={"password"}, exclude_unset=True)

    # Mapping UserCreateSchema to User model
    try:
        user = User(**user_data, hashed_password=hash_password)
        db.add(user)
        await db.commit()
        await db.refresh(user)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "User with this email already exists."},
        )
    return user


# login user
@router.post("/login", status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def login_user(
    request: Request,
    login_data: UserLoginSchema,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> JSONResponse:
    """
    User login endpoint <br>

    :param **login_data**: form data containing user login details <br>
    :type **session**: database session dependency <br>
    """
    creditals_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid email or password",
    )
    statement = select(User).where(User.email == login_data.email)
    result = await db.execute(statement)
    user = result.scalar_one_or_none()

    # Checking user exist and verifyibg passoward
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise creditals_error

    # jwt token creation
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={
            "sub": str(user.email),
            "role": str(user.role),
            "id": str(user.id),
            "name": (user.name),
        },
        secret_key=settings.secret_key,
        algorithm=settings.algorithm,
        expires_delta=access_token_expires,
    )
    response = JSONResponse(content={"message": "Successfully logged in"})

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        # TODO set to True while Production
        secure=False,
        samesite="lax",
        max_age=settings.access_token_expire_minutes * 60,
    )
    request.state.user = user
    return response


# Logout user
@router.post("/logout", status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def logout_user(
    request: Request,
    # ensures only logged-in users can reach this code
    user_data: Annotated[dict, Depends(current_user_dependency)],
) -> JSONResponse:
    """
    User logout endpoint.
    """
    # Create the response object FIRST
    response = JSONResponse(
        content={"message": f"Goodbye {user_data.get('name')}, successfully logged out"}
    )

    # Delete the cookie
    response.delete_cookie(
        key="access_token", httponly=True, secure=True, samesite="lax"
    )

    # Clear the state (the "backpack")
    request.state.user = None

    return response
