from pydantic import BaseModel


class CourseBaseSchema(BaseModel):
    title: str
    description: str | None = None
    category_id: int
    author_id: int