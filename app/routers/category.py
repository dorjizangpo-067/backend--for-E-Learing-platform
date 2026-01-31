from typing import Annotated

from fastapi import APIRouter, Depends, Request
from sqlmodel import Session

from ..dependencies import get_session, is_admin
from ..limiter import limiter
from ..models.categories import Category
from ..schemas.category import CategoryBaseSchema

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("/create", response_model=CategoryBaseSchema)
@limiter.limit("10/minute")
def create_category(
    request: Request,
    category: CategoryBaseSchema,
    session: Annotated[Session, Depends(get_session)],
    _=Depends(is_admin),  # noqa: ANN001
):
    """Add category by admin"""
    db_category = Category(**category.model_dump(exclude_unset=True))
    session.add(db_category)
    session.commit()
    session.refresh(db_category)
    return db_category
