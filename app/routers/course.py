from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from ..models.models import Course
from ..schemas.course import CourseBaseSchema, CreateCourseSchema, UpdateCourseSchema
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

@router.delete("/delete/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    course_id: int, 
    session: Annotated[Session, Depends(get_session)]
    ):
    course = session.get(Course, course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Course not found"
            )
    session.delete(course)
    session.commit()
    return {"detail": "Course deleted successfully"}

@router.patch("/update/{course_id}", response_model=CourseBaseSchema)
async def update_course(
    course_id: int, 
    course_update: UpdateCourseSchema, 
    session: Annotated[Session, Depends(get_session)]
    ):
    """
    Update a course by its ID.<br>
    
    :param **course_id**: course ID <br>
    :type **course_id**: int <br>
    :param **course_update**: Course update data <br>
    :type **course_update**: UpdateCourseSchema <br>
    :param **session**: Database session <br>
    :type **session**: Annotated[Session, Depends(get_session)] <br>
    :return: Updated course <br>
    """
    course = session.get(Course, course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Course not found"
            )
    course_data = course_update.model_dump(exclude_unset=True)
    course.sqlmodel_update(course_data)
    session.add(course)
    session.commit()
    session.refresh(course)
    return course