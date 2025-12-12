"""Application configuration using Pydantic settings."""
from __future__ import annotations

from functools import lru_cache
from typing import Optional

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Central application settings."""

    app_name: str = Field("AI Observability Service", env="APP_NAME")
    database_url: str = Field("sqlite+aiosqlite:///./observability.db", env="DATABASE_URL")
    llm_provider: str = Field("dummy", env="LLM_PROVIDER")
    enable_privacy_masking: bool = Field(True, env="ENABLE_PRIVACY_MASKING")
    max_stored_chars_per_field: int = Field(500, env="MAX_STORED_CHARS_PER_FIELD")
    drift_threshold: float = Field(0.8, env="DRIFT_THRESHOLD")
    enable_evals: bool = Field(True, env="ENABLE_EVALS")
    default_model: str = Field("dummy-llm", env="DEFAULT_MODEL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings."""

    return Settings()
