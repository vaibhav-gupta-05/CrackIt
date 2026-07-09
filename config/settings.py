"""
CrackIT — Application Settings
================================
Centralized configuration loaded from environment variables (.env file).
Uses Pydantic Settings for validation, type coercion, and documentation.

All secrets and environment-specific values live here.
No other module should read os.environ directly.
"""

from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


# ---------------------------------------------------------------------------
# Resolve the project root (parent of /config)
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """
    Application-wide settings, loaded from .env at the project root.

    Every configurable value in CrackIT flows through this class.
    Default values are safe for local development — override via .env
    or real environment variables in production.
    """

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",                     # silently ignore unknown vars
    )

    # --- LLM Provider (Groq) ------------------------------------------
    groq_api_key: str = Field(
        default="",
        description="API key for Groq. Get one at https://console.groq.com/",
    )
    groq_model_name: str = Field(
        default="llama-3.3-70b-versatile",
        description="Groq model to use for JD parsing.",
    )
    groq_base_url: str = Field(
        default="https://api.groq.com/openai/v1",
        description="Base URL for the Groq API (OpenAI-compatible).",
    )

    # --- Data Paths ----------------------------------------------------------
    cache_db_path: str = Field(
        default="./data/cache.db",
        description="Path to the SQLite cache database file.",
    )

    # --- Scraper Configuration -----------------------------------------------
    scraper_headless: bool = Field(
        default=True,
        description="Run Playwright browser in headless mode.",
    )
    scraper_delay_ms: int = Field(
        default=2000,
        ge=500,
        le=10000,
        description="Delay between page loads (rate limiting, in ms).",
    )

    # --- API Server ----------------------------------------------------------
    api_host: str = Field(default="0.0.0.0", description="FastAPI host.")
    api_port: int = Field(default=8000, ge=1024, le=65535, description="FastAPI port.")

    # --- Logging -------------------------------------------------------------
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).",
    )

    # --- Validators ----------------------------------------------------------
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Ensure log level is a valid Python logging level name."""
        v = v.upper()
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}, got '{v}'")
        return v

    @field_validator("cache_db_path")
    @classmethod
    def resolve_relative_paths(cls, v: str) -> str:
        """Resolve relative paths against the project root."""
        path = Path(v)
        if not path.is_absolute():
            path = PROJECT_ROOT / path
        return str(path.resolve())

    # --- Helpers -------------------------------------------------------------
    def configure_logging(self) -> None:
        """Apply log level globally. Call once at startup."""
        logging.basicConfig(
            level=getattr(logging, self.log_level),
            format="%(asctime)s | %(name)-25s | %(levelname)-7s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    @property
    def has_groq_key(self) -> bool:
        """Check if a Groq API key is configured."""
        return bool(self.groq_api_key)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Singleton factory for Settings.

    Uses lru_cache to ensure the .env file is read exactly once.
    Every module should call `get_settings()` rather than
    constructing Settings() directly.
    """
    return Settings()
