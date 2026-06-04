"""
SecureHub — Application Configuration
Loads all settings from environment variables via pydantic-settings.
"""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── App ────────────────────────────────────
    APP_NAME: str = "SecureHub"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # ── PostgreSQL ─────────────────────────────
    POSTGRES_USER: str = "securehub_user"
    POSTGRES_PASSWORD: str = "changeme"
    POSTGRES_DB: str = "securehub_db"
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: str = "postgresql+asyncpg://securehub_user:changeme@db:5432/securehub_db"

    # ── Redis ──────────────────────────────────
    REDIS_URL: str = "redis://redis:6379/0"

    # ── MongoDB ────────────────────────────────
    MONGO_URL: str = "mongodb://mongo:27017"
    MONGO_DB_NAME: str = "securehub_logs"

    # ── JWT ────────────────────────────────────
    JWT_SECRET_KEY: str = "change-this-secret"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # ── CORS ───────────────────────────────────
    CORS_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:80",
        "http://localhost:3000",
        "http://127.0.0.1",
    ]

    # ── Rate Limiting ─────────────────────────
    RATE_LIMIT_PER_MINUTE: int = 100


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance — loaded once per process."""
    return Settings()
