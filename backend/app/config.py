"""
Rayeva AI — Application Configuration
Environment-based settings using Pydantic Settings.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── API Keys ──────────────────────────────────────────────
    google_api_key: str = ""

    # ── AI Configuration ──────────────────────────────────────
    ai_model: str = "gemini-3.1-flash-lite-preview"
    ai_thinking_level: str = "LOW"
    ai_temperature_structured: float = 0.3
    ai_temperature_creative: float = 0.8
    ai_max_output_tokens: int = 8192
    ai_max_retries: int = 2

    # ── Database ──────────────────────────────────────────────
    database_url: str = "sqlite:///./rayeva.db"

    # ── Logging ───────────────────────────────────────────────
    log_level: str = "INFO"

    # ── App ───────────────────────────────────────────────────
    app_name: str = "Rayeva AI — Sustainable Commerce"
    app_version: str = "1.0.0"
    debug: bool = False

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
