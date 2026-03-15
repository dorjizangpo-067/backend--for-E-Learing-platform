from pydantic import BaseModel


class CourseBaseSchema(BaseModel):
    title: str
    description: str | None = None
    video_id: str


class ReadCourseSchema(CourseBaseSchema):
    id: int
    author_id: int
    category_id: int

    class Config:
        from_attributes = True


class CreateCourseSchema(CourseBaseSchema):
    category: str


class UpdateCourseSchema(BaseModel):
    title: str | None = None
    description: str | None = None
    video_id: str | None = None
    category: str | None = None
