"""
Application Configuration
File: app/core/config.py

All settings come from environment variables or .env file
CONNECTION STRING → DATABASE_URL
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings.
    Values are loaded from environment variables or .env file.

    Priority: Environment variable > .env file > default value
    """

    # ── Project Info ──────────────────────────────────────────────────────────
    PROJECT_NAME: str = "Riada Law - Legal Tech Platform"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "منصة إدارة مكتب المحاماة"

    # ── Server ────────────────────────────────────────────────────────────────
    HOST: str = "0.0.0.0"
    PORT: int = 5050
    DEBUG: bool = True                      # Set False in production

    # ── *** DATABASE CONNECTION STRING *** ────────────────────────────────────
    # Default: SQLite file in project root (no setup needed!)
    # Change this in your .env file for PostgreSQL/MySQL
    DATABASE_URL: str = "sqlite:///./legal_tech.db"
    #
    # PostgreSQL example:
    # DATABASE_URL=postgresql://postgres:mypassword@localhost:5432/legaltech
    #
    # MySQL example:
    # DATABASE_URL=mysql+pymysql://root:mypassword@localhost:3306/legaltech

    # ── API ───────────────────────────────────────────────────────────────────
    API_V1_STR: str = "/api/v1"

    # ── Security / JWT ────────────────────────────────────────────────────────
    # CHANGE THIS IN PRODUCTION! Generate with: openssl rand -hex 32
    SECRET_KEY: str = "your-super-secret-key-change-in-production-please"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7   # 7 days

    # ── File Uploads ──────────────────────────────────────────────────────────
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024           # 50 MB

    # ── Email (optional, leave blank to disable) ──────────────────────────────
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: Optional[str] = None

    # ── AI/LLM (optional) ─────────────────────────────────────────────────────
    ANTHROPIC_API_KEY: Optional[str] = None
    LLM_MODEL: str = "claude-sonnet-4-5-20250929"

    class Config:
        # Looks for .env file in project root
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# ─── Singleton ────────────────────────────────────────────────────────────────
settings = Settings()