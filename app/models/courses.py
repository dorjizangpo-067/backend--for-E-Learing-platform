from __future__ import annotations  
from sqlmodel import SQLModel, Field, Relationship
from typing import List, TYPE_CHECKING
from sqlalchemy.orm import relationship

if TYPE_CHECKING:
    from .categories import Category
    from .users import User

class Course(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    description: str
    video_id: str

    category_id: int = Field(foreign_key="category.id")
    author_id: int = Field(foreign_key="user.id")

    author: "User" = Relationship(
        sa_relationship=relationship("User", back_populates="courses")
    )
    category: "Category" = Relationship(
        sa_relationship=relationship("Category", back_populates="courses")
    )
