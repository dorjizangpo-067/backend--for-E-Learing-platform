from pydantic_settings import BaseSettings, SettingsConfigDict

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