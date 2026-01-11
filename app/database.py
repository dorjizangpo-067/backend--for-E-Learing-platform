from sqlmodel import create_engine, SQLModel
from pydantic_settings import BaseSettings, SettingsConfigDict

from .models.models import User, Course, Category

class Settings(BaseSettings):
    sqlite_url: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    admin_email: str

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="allow",
    )

settings = Settings()

connect_args = {"check_same_thread": False}
engine = create_engine(settings.sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)