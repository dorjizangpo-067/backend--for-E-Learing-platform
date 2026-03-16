from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import apaginate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..dependencies import is_admin
from ..limiter import limiter
from ..models.users import User
from ..schemas.user import UserReadSchema

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
)
@limiter.limit("10/minute")
async def get_users(
    request: Request,  # for Limiter to perform
    db: Annotated[AsyncSession, Depends(get_db)],
    is_admin: Annotated[bool, Depends(is_admin)],
    offset: int = 0,
) -> Page[UserReadSchema]:
    """get all users"""
    query = select(User)
    return await apaginate(db, query)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("10/minute")
async def delete_user(
    request: Request,
    id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    is_admin: Annotated[bool, Depends(is_admin)],
) -> None:
    user = await db.get(User, id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    await db.delete(user)
    await db.commit()
