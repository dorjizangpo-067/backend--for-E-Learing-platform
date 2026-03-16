from __future__ import annotations

from typing import Literal

from fastapi import HTTPException, status
from pydantic import BaseModel, ConfigDict, EmailStr, field_validator

from ..env_loader import settings
from ..models.users import User


class UserBaseSchema(BaseModel):
    name: str
    bio: str | None = None
    email: EmailStr
    role: Literal["student", "teacher", "admin"] = "student"

    @field_validator("role", mode="before")
    @classmethod
    def normalize_role(cls, value: str) -> str:
        value = value.strip().lower()
        if value not in {"student", "teacher", "admin"}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role"
            )
        return value

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()

    @field_validator("name", mode="before")
    @classmethod
    def normalize_name(cls, v: str) -> str:
        return v.strip()


class UserCreateSchema(UserBaseSchema):
    password: str

    def to_model(self, hashed_password: str) -> User:
        data = self.model_dump(exclude_unset=True, exclude={"password"})
        return User(**data, hashed_password=hashed_password)

    def validate_admin(self) -> bool:
        if self.role == "admin" and self.email != settings.admin_email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="You are not authorized to create an Admin account.",
            )
        return True


class UserUpdateSchema(BaseModel):
    name: str | None = None
    bio: str | None = None
    email: EmailStr | None = None
    role: Literal["student", "teacher", "admin"] | None = None
    password: str | None = None


class UserReadSchema(UserBaseSchema):
    id: int

    model_config = ConfigDict(from_attributes=True)


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str


class TokenResponseSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"
