from pydantic import BaseModel, field_validator


class CategoryBaseSchema(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def name_is_valid(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Category name is empty")
        return value.lower()
