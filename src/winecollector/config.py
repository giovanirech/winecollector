from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    POSTGRES_USER: str = "winecollector"
    POSTGRES_PASSWORD: str = "changeme"
    POSTGRES_DB: str = "winecollector"
    DATABASE_URL: str = (
        "postgresql+asyncpg://winecollector:changeme@localhost:5432/winecollector"
    )

    SECRET_KEY: str = Field(min_length=32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    IMAGES_DIR: str = "data/images"

    SCRAPER_TIMEOUT: float = 15.0
    SCRAPER_USER_AGENT: str = "WineCollector/1.0 (personal wine cellar manager)"

    ENVIRONMENT: Literal["development", "production"] = "development"

    @field_validator("SECRET_KEY")
    @classmethod
    def _secret_key_long_enough(cls, value: str) -> str:
        if len(value) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the singleton ``Settings`` instance.

    Cached via ``lru_cache`` so the environment is parsed exactly once per
    process. Tests that need to override values should clear the cache via
    ``get_settings.cache_clear()`` between cases.
    """
    return Settings()  # type: ignore[call-arg]
