from sqlmodel import create_engine, SQLModel
from pydantic_settings import BaseSettings, SettingsConfigDict

from .models.models import User, Course, Category
from .env_loader import settings

connect_args = {"check_same_thread": False}
engine = create_engine(settings.sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)