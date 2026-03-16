from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    postgresql_url: str | None = None
    sqlite_url: str | None = None
    secret_key: SecretStr
    algorithm: str
    access_token_expire_minutes: int
    admin_email: str

    @property
    def database_url(self) -> str:
        """Use PostgreSQL in production, SQLite as fallback for testing."""
        if self.postgresql_url:
            return self.postgresql_url
        if self.sqlite_url:
            return self.sqlite_url
        raise ValueError("Either postgresql_url or sqlite_url must be set")

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
    )


settings = Settings()  # type: ignore
