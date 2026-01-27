from fastapi import APIRouter, Depends, Request
from sqlmodel import Session, select
from typing import Annotated

from ..models.categories import Category
from ..dependencies import get_session, is_admin
from ..schemas.category import CategoryBaseSchema
from ..limiter import limiter

router = APIRouter(
    prefix="/categories", 
    tags=["categories"]
    )


@router.post("/create", response_model=CategoryBaseSchema)
@limiter.limit("10/minute")
async def create_category(
    request: Request,
    category: CategoryBaseSchema,

    session: Annotated[Session, Depends(get_session)],
    _ = Depends(is_admin)
    ):
    """  Add category by admin  """
    db_category = Category(**category.model_dump(exclude_unset=True))
    session.add(db_category)
    session.commit()
    session.refresh(db_category)
    return {"category": db_category}