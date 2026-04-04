"""
Application Configuration
File: app/core/config.py

All settings come from environment variables or .env file
"""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings.
    Priority: Environment variable > .env file > default value
    """

    # ── Project Info ──────────────────────────────────────────────────────────
    PROJECT_NAME: str = "Riada Law - Legal Tech Platform"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "منصة إدارة مكتب المحاماة"

    # ── Server ────────────────────────────────────────────────────────────────
    HOST: str = "0.0.0.0"
    PORT: int = 5050
    DEBUG: bool = True

    # ── Database ──────────────────────────────────────────────────────────────
    DATABASE_URL: str = "sqlite:///./legal_tech.db"

    # ── API ───────────────────────────────────────────────────────────────────
    API_V1_STR: str = "/api/v1"

    # ── Security / JWT ────────────────────────────────────────────────────────
    SECRET_KEY: str = "your-super-secret-key-change-in-production-please"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    # ── File Uploads ──────────────────────────────────────────────────────────
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024

    # ── Email ─────────────────────────────────────────────────────────────────
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: Optional[str] = None

    # ════════════════════════════════════════════════════════════════════════
    # 🔥 AI / LLM SETTINGS (FIXED)
    # ════════════════════════════════════════════════════════════════════════

    # Provider selection
    LLM_PROVIDER: str = "gemini"   # ollama | gemini | openai | claude

    # API Keys
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None

    # Models
    GEMINI_MODEL: str = "models/gemini-2.5-flash"
    OPENAI_MODEL: str = "gpt-4o-mini"
    ANTHROPIC_MODEL: str = "claude-haiku-4-5-20251001"

    # Qdrant
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333

    # ════════════════════════════════════════════════════════════════════════

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",   # 🔥 prevents crash if extra env vars exist
    )


# ─── Singleton ────────────────────────────────────────────────────────────────
settings = Settings()