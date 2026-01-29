from pydantic import BaseModel, EmailStr
from typing import Literal


class UserBaseSchema(BaseModel):
    name: str
    bio: str | None = None
    email: EmailStr
    role: Literal["student", "teacher", "admin"] = "student"


class UserCreateSchema(UserBaseSchema):
    password: str


class UserUpdateSchema(BaseModel):
    name: str | None = None
    bio: str | None = None
    email: EmailStr | None = None
    role: Literal["student", "teacher", "admin"] | None = None
    password: str | None = None


class UserReadSchema(UserBaseSchema):
    id: int


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str


class TokenResponseSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"
