from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlmodel import Session, select

from ..dependencies import (
    current_user_dependency,
    get_session,
    is_admin,
    is_teacher_or_admin,
)
from ..limiter import limiter
from ..models.categories import Category
from ..models.courses import Course
from ..schemas.course import (
    CourseBaseSchema,
    CreateCourseSchema,
    ReadCourseSchema,
    UpdateCourseSchema,
)

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("/", response_model=dict[str, list[ReadCourseSchema]])
@limiter.limit("5/second")  # Allows a quick 'burst' of 5 clicks
@limiter.limit("100/hour")  # But stops long-term heavy usage
def get_courses(
    request: Request,  # for Limiter to perform
    session: Annotated[Session, Depends(get_session)],
    limit: Annotated[int, Query(le=25)] = 15,
    offset: int = 0,
    _=Annotated[bool, Depends(is_admin)],
):
    """Retrieve a list of courses with pagination."""
    courses = session.exec(select(Course).offset(offset).limit(limit)).all()
    return {"courses": courses}


@router.post(
    "/", response_model=dict[str, CourseBaseSchema], status_code=status.HTTP_201_CREATED
)
@limiter.limit("5/second")  # type: ignore
@limiter.limit("100/hour")  # type: ignore
def create_course(
    request: Request,
    course_in: CreateCourseSchema,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[dict, Depends(current_user_dependency)],
    is_authorized: bool = Depends(is_teacher_or_admin),
):
    """Create a new course and assign it to the current user."""

    category = session.exec(
        select(Category).where(Category.name == course_in.category)
    ).first()

    if not category:
        all_categories = session.exec(select(Category)).all()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": f"Invalid category '{course_in.category}'",
                "available_categories": [c.name for c in all_categories],
            },
        )

    # Prepare data and exclude 'category' string to replace with 'category_id'
    course_data = course_in.model_dump(exclude={"category"})
    db_course = Course(
        **course_data, category_id=category.id, author_id=current_user["id"]
    )

    session.add(db_course)
    session.commit()
    session.refresh(db_course)
    return {"courses": db_course}


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("2/minute")  # type: ignore
def delete_course(
    request: Request,
    course_id: int,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[dict, Depends(current_user_dependency)],
    _=Annotated[bool, Depends(is_teacher_or_admin)],
):
    """Delete a course by its ID"""
    course = session.get(Course, course_id)

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
        )

    # Ownership check
    if course.author_id != current_user.get("id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this course",
        )

    session.delete(course)
    session.commit()
    return {"detail": "Course deleted successfully"}


@router.patch("/{course_id}", response_model=dict[str, CourseBaseSchema])
@limiter.limit("10/minute")  # Very strict
def update_course(
    request: Request,
    course_id: int,
    course_update: UpdateCourseSchema,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[dict, Depends(current_user_dependency)],
    _=Annotated[bool, Depends(is_teacher_or_admin)],
):
    """Update a course by its ID."""
    course = session.get(Course, course_id)

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
        )

    # Ownership check
    if course.author_id != current_user.get("id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to edit this course",
        )

    # Apply partial updates
    course_data = course_update.model_dump(exclude_unset=True)
    course.sqlmodel_update(course_data)

    session.add(course)
    session.commit()
    session.refresh(course)
    return {"course": course}
