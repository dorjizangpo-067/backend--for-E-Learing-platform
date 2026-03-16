from pydantic import BaseModel, ConfigDict


class CourseBaseSchema(BaseModel):
    title: str
    description: str | None = None
    course_url: str


class ReadCourseSchema(CourseBaseSchema):
    id: int
    author_id: int
    category_id: int

    model_config = ConfigDict(from_attributes=True)


class CreateCourseSchema(CourseBaseSchema):
    category: str


class UpdateCourseSchema(BaseModel):
    title: str | None = None
    description: str | None = None
    category: str | None = None
    course_url: str | None = None
