from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.categories import Category
from ..schemas.course import CreateCourseSchema, UpdateCourseSchema


async def category_check(
    db: AsyncSession, new_course: UpdateCourseSchema | CreateCourseSchema
) -> Category:
    stmt = select(Category).where(Category.name == new_course.category)
    result = await db.execute(stmt)
    category = result.scalar_one_or_none()

    if not category:
        categories_result = await db.execute(select(Category.name))
        all_categories = categories_result.scalars().all()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": f"Invalid category '{new_course.category}'",
                "available_categories": all_categories,
            },
        )
    return category
