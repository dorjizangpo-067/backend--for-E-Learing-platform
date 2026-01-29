from typing import Annotated
from fastapi import Depends, APIRouter, status, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlmodel import Session, select
from datetime import timedelta
from sqlalchemy.exc import IntegrityError

from .utilits import create_access_token, hash_password as func_hash_password, verify_password
from ..schemas.user import UserCreateSchema, UserReadSchema, UserLoginSchema
from ..dependencies import get_session, get_current_user, current_user_dependency
from ..models.users import User
from ..limiter import limiter
from ..env_loader import settings


router = APIRouter(prefix="/auth", tags=["auth"])

# reginster user
@router.post("/register", response_model=UserReadSchema, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def register_user(
    request: Request,
    register_data: UserCreateSchema,
    session: Annotated[Session, Depends(get_session)]
    ):
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
            detail="You are not Admin"
        )
    # password hashing
    hash_password = func_hash_password(register_data.password)
    user_form.password = hash_password

    # Mapping UserCreateSchema to User model
    try:
        user = User(**user_form.model_dump(exclude_unset=True), hashed_password=hash_password)
        session.add(user)
        session.commit()
        session.refresh(user)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "User with this email already exists."}
        )
    return {"user": user}

# login user
@router.post("/login", status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def login_user(
    request: Request,
    login_data: UserLoginSchema,
    session: Annotated[Session, Depends(get_session)],
    ):
    """
    User login endpoint <br>
    
    :param **login_data**: form data containing user login details <br>
    :type **session**: database session dependency <br>
    """
    creditals_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, 
        detail={"error": "Invalid email or password"}
        )
    # check user is already login or not
    token_user = get_current_user(request=request, secret_key=settings.secret_key, algorithms=[settings.algorithm])
    if token_user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mr/Ms.{token_user.get("name")} had already login"
        )
    statement = select(User).where(User.email == login_data.email)
    user = session.exec(statement).first()
    if not user:
        raise creditals_error

    # verify password
    is_valid_password = verify_password(login_data.password, user.hashed_password)
    if not is_valid_password:
        raise creditals_error

    response = JSONResponse(content={"message": "Successfully logged in"})

    # jwt token creation
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={
            "sub": str(user.email), 
            "role": str(user.role),
            "id": user.id,
            "name": (user.name)
        }, 
        secret_key=settings.secret_key, 
        algorithm=settings.algorithm, 
        expires_delta=access_token_expires
    )
    # response = Response()
    response = JSONResponse(content={"message": "Successfully logged in"})
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="lax"
    )
    request.state.user = user
    return response

# Logout user
@router.post("/logout", status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def logout_user(
    request: Request,
    # ensures only logged-in users can reach this code
    user_data: Annotated[dict, Depends(current_user_dependency)]
    ):
    """
    User logout endpoint.
    """
    # Create the response object FIRST
    response = JSONResponse(content={"message": f"Goodbye {user_data.get('name')}, successfully logged out"})

    # Delete the cookie
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=True,
        samesite="lax"
    )

    # Clear the state (the "backpack")
    request.state.user = None

    return response