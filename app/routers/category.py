from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import Annotated

from ..models.models import Category
from ..dependencies import get_session, admin_role_dependency
from ..schemas.category import CategoryBaseSchema

router = APIRouter(
    prefix="/categories", 
    tags=["categories"]
    )

@router.post("/create", response_model=CategoryBaseSchema)
async def create_category(
    category: CategoryBaseSchema,

    session: Annotated[Session, Depends(get_session)],
    admn = Depends(admin_role_dependency)
    ):
    db_category = Category(**category.model_dump(exclude_unset=True))
    session.add(db_category)
    session.commit()
    session.refresh(db_category)
    return db_category