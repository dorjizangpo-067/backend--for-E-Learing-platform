from __future__ import annotations  
from sqlmodel import SQLModel, Field, Relationship
from typing import List, TYPE_CHECKING
from sqlalchemy.orm import relationship

if TYPE_CHECKING:
    from .courses import Course

class Category(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str

    courses: List["Course"] = Relationship(
        sa_relationship=relationship("Course", back_populates="category")
    )