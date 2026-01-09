from sqlmodel import create_engine, SQLModel
from pydantic_settings import BaseSettings
from .models.models import User, Course, Category

class Settings(BaseSettings):
    sqlite_url: str

    class Config:
        env_file = ".env"

settings = Settings()

connect_args = {"check_same_thread": False}
engine = create_engine(settings.sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)