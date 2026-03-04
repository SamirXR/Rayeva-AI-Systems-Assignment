"""
Rayeva AI — Application Configuration
Environment-based settings using Pydantic Settings.
"""

from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings

# Resolve .env relative to this file: backend/app/config.py → ../../.env
_ENV_FILE = Path(__file__).resolve().parent.parent.parent / ".env"


class Settings(BaseSettings):
    # ── API Keys ──────────────────────────────────────────────
    openai_api_key: str = ""
    azure_ai_endpoint: str = "https://ai-samirawm76076ai528478683931.services.ai.azure.com/openai/v1/"

    # ── AI Configuration ──────────────────────────────
    ai_model: str = "grok-4-fast-reasoning"
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

    model_config = {"env_file": str(_ENV_FILE), "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
