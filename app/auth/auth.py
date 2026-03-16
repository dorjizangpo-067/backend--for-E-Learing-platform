from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import Response
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..dependencies import current_user_dependency
from ..limiter import limiter
from ..schemas.user import UserCreateSchema, UserLoginSchema, UserReadSchema
from .utilits import (
    authenticate_user,
    build_login_response,
    create_user_token,
)
from .utilits import (
    hash_password as func_hash_password,
)

router = APIRouter(prefix="/auth", tags=["auth"])


# reginster user
@router.post("/register", status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def register_user(
    request: Request,
    register_data: UserCreateSchema,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserReadSchema:
    """
    User registration endpoint <br>
    """
    # admin validation
    register_data.validate_admin()

    # Create user models for schemas
    user = register_data.to_model(
        hashed_password=func_hash_password(register_data.password)
    )

    # insert into db
    try:
        db.add(user)
        await db.commit()
        await db.refresh(user)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "User with this email already exists."},
        )
    return UserReadSchema.model_validate(user)


# login user
@router.post("/login", status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def login_user(
    request: Request,
    login_data: UserLoginSchema,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Response:
    """
    User login endpoint <br>
    """
    user = await authenticate_user(db, login_data.email, login_data.password)
    access_token = create_user_token(user)
    request.state.user = user
    return build_login_response(access_token)


# Logout user
@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("5/minute")
async def logout_user(
    request: Request,
    user_data: Annotated[dict, Depends(current_user_dependency)],
) -> Response:
    """
    User logout endpoint.
    """
    response = Response()
    response.delete_cookie(
        key="access_token", httponly=True, secure=True, samesite="lax"
    )
    return response
