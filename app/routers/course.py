from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from ..models.models import Course
from ..schemas.course import CourseBaseSchema, CreateCourseSchema, UpdateCourseSchema, ReadCourseSchema
from ..dependencies import get_session, current_user_dependency, teacher_role_dependency

router = APIRouter(
    prefix="/courses",
    tags=["courses"]
)

@router.get("/", response_model=list[ReadCourseSchema])
async def get_courses(
    session: Annotated[Session, Depends(get_session)], 
    limit: int = 15, 
    offset: int = 0, 

    current_user:dict = Depends(current_user_dependency),
    ):
    """
    Retrieve a list of courses with pagination.<br>
    
    :param **session**: Database session
    :type **session**: Annotated[Session, Depends(get_session)]
    :param **limit**: Number of courses to retrieve
    :type **limit**: int
    :param **offset**: Number of courses to skip
    :type **offset**: int

    **dependencies**: <br>
    - **current_user**: Get the current authenticated user <br>
    """
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
    session: Annotated[Session, Depends(get_session)],

    teacher_role:bool = Depends(teacher_role_dependency),
    current_user:dict = Depends(current_user_dependency)
    ):
    """
    Create a new course.<br>
    
    :param course: Course data to create
    :type course: CreateCourseSchema
    :param session: Database session
    :type session: Annotated[Session, Depends(get_session)]

    **dependencies**: <br>
    - **current_user**: Get the current authenticated user <br>
    - **teacher_role**: Ensure the user has teacher or admin role <br>
    """
    course_with_author_id = course.model_dump(exclude_unset=True)
    course_with_author_id.update({"author_id": int(current_user.get("id"))})
    print("course_with_author_id", course_with_author_id)
    db_course = Course(**course_with_author_id)
    session.add(db_course)
    session.commit()
    session.refresh(db_course)
    return db_course

@router.delete("/delete/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    course_id: int, 
    session: Annotated[Session, Depends(get_session)],

    teacher_role:bool = Depends(teacher_role_dependency),
    current_user:dict = Depends(current_user_dependency)
    ):
    """
    Delete a course by its ID.<br>
    :param **course_id**: course ID <br>
    :type **course_id**: int <br>
    :param **session**: Database session <br>
    :type **session**: Annotated[Session, Depends(get_session)] <br>

    **dependencies**: <br>
    - **current_user**: Get the current authenticated user <br>
    - **teacher_role**: Ensure the user has teacher or admin role <br>
    """
    course = session.get(Course, course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Course not found"
            )
    if course.author_id != current_user.get("id"):
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="You are Not Creator of this course!"
            )
    session.delete(course)
    session.commit()
    return {"detail": "Course deleted successfully"}

@router.patch("/update/{course_id}", response_model=CourseBaseSchema)
async def update_course(
    course_id: int, 
    course_update: UpdateCourseSchema, 
    session: Annotated[Session, Depends(get_session)],

    teacher_role:bool = Depends(teacher_role_dependency),
    current_user:dict = Depends(current_user_dependency)
    ):
    """
    Update a course by its ID.<br>
    
    :param **course_id**: course ID <br>
    :type **course_id**: int <br>
    :param **course_update**: Course update data <br>
    :type **course_update**: UpdateCourseSchema <br>
    :param **session**: Database session <br>
    :type **session**: Annotated[Session, Depends(get_session)] <br>

    **dependencies**: <br>
    - **current_user**: Get the current authenticated user <br>
    - **teacher_role**: Ensure the user has teacher or admin role <br>
    """
    course = session.get(Course, course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Course not found"
            )
    if course.author_id != current_user.get("id"):
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="You are Not Creator of this course!"
        )
    course_data = course_update.model_dump(exclude_unset=True)
    course.sqlmodel_update(course_data)
    session.add(course)
    session.commit()
    session.refresh(course)
    return course