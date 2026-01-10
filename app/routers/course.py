from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from ..models.models import Course
from ..schemas.course import CourseBaseSchema, CreateCourseSchema
from ..dependencies import get_session

router = APIRouter(
    prefix="/courses",
    tags=["courses"]
)

@router.get("/", response_model=list[CourseBaseSchema])
async def get_courses(session: Annotated[Session, Depends(get_session)], limit: int = 15, offset: int = 0):
    courses = session.exec(select(Course).offset(offset).limit(limit)).all()
    if not courses:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="No courses found"
            )
    return courses

@router.post("/create", response_model=CourseBaseSchema)
async def create_course(
    course: CreateCourseSchema, 
    session: Annotated[Session, Depends(get_session)]
    ):
    db_course = Course(**course.model_dump(exclude_unset=True))
    session.add(db_course)
    session.commit()
    session.refresh(db_course)
    return db_course