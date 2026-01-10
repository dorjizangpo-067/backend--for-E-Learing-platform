from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from ..models.models import Course
from ..schemas.course import CourseBaseSchema
from ..dependencies import get_session

router = APIRouter(
    prefix="/courses",
    tags=["courses"]
)

@router.get("/", response_model=list[CourseBaseSchema])
async def get_courses(session: Annotated[Session, Depends(get_session)]):
    courses = session.exec(select(Course)).all()
    if not courses:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="No courses found"
            )
    return courses