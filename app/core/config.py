"""Application configuration using Pydantic Settings."""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = Field(default="Employee Management System", alias="APP_NAME")
    app_env: Literal["development", "staging", "production"] = Field(
        default="development", alias="APP_ENV"
    )
    debug: bool = Field(default=False, alias="DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # MongoDB
    mongo_uri: str = Field(default="mongodb://localhost:27017", alias="MONGO_URI")
    database_name: str = Field(default="employee_management", alias="DATABASE_NAME")

    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")

    # JWT
    jwt_secret_key: str = Field(default="change-me", alias="JWT_SECRET_KEY")
    jwt_refresh_secret_key: str = Field(
        default="change-me-refresh", alias="JWT_REFRESH_SECRET_KEY"
    )
    access_token_expire_minutes: int = Field(
        default=15, alias="ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    refresh_token_expire_days: int = Field(default=7, alias="REFRESH_TOKEN_EXPIRE_DAYS")
    jwt_algorithm: str = "HS256"

    # Celery
    celery_broker_url: str = Field(
        default="redis://localhost:6379/1", alias="CELERY_BROKER_URL"
    )
    celery_result_backend: str = Field(
        default="redis://localhost:6379/2", alias="CELERY_RESULT_BACKEND"
    )

    # Cache
    employee_cache_ttl_seconds: int = 300  # 5 minutes

    # Google OAuth
    google_client_id: str = Field(default="", alias="GOOGLE_CLIENT_ID")
    google_client_secret: str = Field(default="", alias="GOOGLE_CLIENT_SECRET")
    google_redirect_uri: str = Field(
        default="http://localhost:8000/api/v1/auth/google/callback",
        alias="GOOGLE_REDIRECT_URI",
    )
    frontend_url: str = Field(default="http://localhost:5173", alias="FRONTEND_URL")

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"

    @property
    def google_auth_enabled(self) -> bool:
        return bool(self.google_client_id)


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
