"""Configuration management using pydantic-settings."""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_name: str = "streamYourClaw"
    app_version: str = "0.1.0"
    debug: bool = False

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_stream_prefix: str = "syc"

    # Frontend
    frontend_path: str = "frontend"

    # Agent settings
    supervisor_model: str = "gpt-4"
    openclaw_adapter: str = "mock"  # "mock" or "real"

    # LLM settings (for Supervisor)
    llm_api_key: Optional[str] = None
    llm_base_url: Optional[str] = None


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()