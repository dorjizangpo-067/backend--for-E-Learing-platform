from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..dependencies import (
    current_user_dependency,
    is_teacher_or_admin,
)
from ..limiter import limiter
from ..models.courses import Course
from ..schemas.course import (
    CreateCourseSchema,
    ReadCourseSchema,
    UpdateCourseSchema,
)
from .utils import category_check

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("/")
@limiter.limit("5/second")
@limiter.limit("100/hour")
async def get_courses(
    request: Request,  # for Limiter to perform
    db: Annotated[AsyncSession, Depends(get_db)],
    is_authorized: Annotated[bool, Depends(current_user_dependency)],
) -> Page[ReadCourseSchema]:
    """Retrieve a list of courses with pagination."""
    query = select(Course)
    return await paginate(db, query)


@router.post("/", status_code=status.HTTP_201_CREATED)
@limiter.limit("3/second")
@limiter.limit("100/hour")
async def create_course(
    request: Request,
    course_in: CreateCourseSchema,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(current_user_dependency)],
    is_authorized: Annotated[bool, Depends(is_teacher_or_admin)],
) -> ReadCourseSchema:
    """Create a new course"""

    # check category
    category = await category_check(db=db, new_course=course_in)

    # Prepare data and exclude 'category' string to replace with 'category_id'
    course_data = course_in.model_dump(exclude={"category"})
    db_course = Course(
        **course_data, category_id=category.id, author_id=int(current_user["id"])
    )

    db.add(db_course)
    await db.commit()
    await db.refresh(db_course)
    return ReadCourseSchema.model_validate(db_course)


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("2/minute")
async def delete_course(
    request: Request,
    course_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(current_user_dependency)],
    is_authorized: Annotated[bool, Depends(is_teacher_or_admin)],
) -> None:
    """Delete a course by its ID"""
    course = await db.get(Course, course_id)

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
        )

    # Ownership check
    if str(course.author_id) != current_user.get("id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this course",
        )

    await db.delete(course)
    await db.commit()
    return


@router.patch("/{course_id}", status_code=status.HTTP_202_ACCEPTED)
@limiter.limit("10/minute")  # Very strict
async def update_course(
    request: Request,
    course_id: int,
    course_update: UpdateCourseSchema,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(current_user_dependency)],
    is_authorized: Annotated[bool, Depends(is_teacher_or_admin)],
) -> ReadCourseSchema:
    """Update a course by its ID."""
    course = await db.get(Course, course_id)

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
        )

    # Ownership check
    if str(course.author_id) != current_user.get("id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to edit this course",
        )

    # Prepare data and exclude 'category' string to replace with 'category_id'
    update_data = course_update.model_dump(exclude_unset=True, exclude={"category"})

    # Apply partial updates
    for key, value in update_data.items():
        setattr(course, key, value)

    if course_update.category is not None:
        category = await category_check(db=db, new_course=course_update)
        course.category_id = category.id

    db.add(course)
    await db.commit()
    await db.refresh(course)
    return ReadCourseSchema.model_validate(course)
