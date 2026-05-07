from functools import cached_property

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "archive-system-api"
    app_version: str = "0.1.0"
    app_env: str = "development"
    api_prefix: str = "/api"
    database_url: str = (
        "postgresql+psycopg://archive:archive_password@127.0.0.1:15432/archive_system"
    )
    backend_cors_origins: str = Field(
        default="http://127.0.0.1:15173,http://localhost:15173"
    )
    log_level: str = "INFO"
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 480
    default_admin_password: str = "Admin@123456"
    default_user_password: str = "User@123456"

    @cached_property
    def cors_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.backend_cors_origins.split(",")
            if origin.strip()
        ]


settings = Settings()
