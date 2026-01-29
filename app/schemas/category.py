from pydantic import BaseModel


class CategoryBaseSchema(BaseModel):
    name: str
