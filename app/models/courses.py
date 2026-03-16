from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base

if TYPE_CHECKING:
    from .categories import Category
    from .users import User


class Course(Base):
    __tablename__ = "course"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(120), index=True)
    description: Mapped[str] = mapped_column(Text)
    course_url: Mapped[str] = mapped_column(String, nullable=True)
    created_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    category_id: Mapped[int] = mapped_column(ForeignKey("category.id"))
    author_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

    author: Mapped[User] = relationship(back_populates="courses")
    category: Mapped[Category] = relationship(back_populates="courses")
