from sqlmodel import create_engine, SQLModel
from pydantic_settings import BaseSettings, SettingsConfigDict

from .models.categories import Category
from .models.users import User
from .models.courses import Course
from .env_loader import settings

connect_args = {"check_same_thread": False}
engine = create_engine(settings.sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)