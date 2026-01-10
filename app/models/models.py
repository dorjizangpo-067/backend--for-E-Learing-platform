from sqlmodel import SQLModel, Field, Relationship
from typing import List

class Course(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    description: str
    video_id: str

    category_id: int = Field(foreign_key="category.id")
    author_id: int = Field(foreign_key="user.id")

    author: "User" = Relationship(back_populates="courses")
    category: "Category" = Relationship(back_populates="courses")


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    bio: str | None = Field(default=None)
    email: str = Field(index=True, unique=True)
    role: str
    hashed_password: str

    courses: List["Course"] = Relationship(back_populates="author")


class Category(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str

    courses: List["Course"] = Relationship(back_populates="category")
