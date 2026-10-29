"""Pydantic v2 application settings for EriWatch API."""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed environment settings for the EriWatch API service."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "EriWatch API"
    app_version: str = "0.1.0"
    environment: Literal["development", "staging", "production", "test"] = "development"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    database_url: str = Field(
        default="postgresql+psycopg://eriwatch:eriwatch_local@localhost:5432/eriwatch",
        description="SQLAlchemy 2 connection string for PostgreSQL (PostGIS + pgvector)",
    )
    cors_origins: list[str] = Field(
        default=["http://localhost:3000"],
        description="Allowed CORS origins for the web client",
    )


@lru_cache
def get_settings() -> Settings:
    """Return cached Settings instance."""
    return Settings()
