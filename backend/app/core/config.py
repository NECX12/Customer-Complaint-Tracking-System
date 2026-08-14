
from __future__ import annotations
from functools import lru_cache
from typing import Optional, Literal

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv(dotenv_path=".env", override=False)
load_dotenv(dotenv_path="../.env", override=False)


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env files."""

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────────
    APP_NAME: str = "Complaint Tracking System"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"

    # ── Database ───────────────────────────────────────────────────
    DATABASE_URL: str

    # ── JWT Authentication ───────────────────────────────────────
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    # ── Redis ─────────────────────────────────────────────────────
    REDIS_URL: str

    # ── Email (SMTP) ──────────────────────────────────────────────
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_USE_TLS: bool = True
    EMAIL_FROM: Optional[str] = None

    # ── Frontend URL ──────────────────────────────────────────────
    FRONTEND_URL: str = "http://localhost:5173"

    # ── AI / RAG ─────────────────────────────────────────────────
    AI_PROVIDER: str = "gemini"
    GEMINI_API_KEY: str | None = None
    OPENAI_API_KEY: str | None = None
    EMBEDDING_MODEL_NAME: str
    LLM_MODEL: str

    # ── RAG / ChromaDB ─────────────────────────────────────────────
    CHUNK_MAX_CHARS: int = 1500
    CHUNK_OVERLAP_CHARS: int = 200
    RAG_TOP_K: int = 5
    CHROMA_COLLECTION_NAME: str = "mikano_knowledge_base"

    @property
    def email_enabled(self) -> bool:
        """Email sending is enabled only when all SMTP settings are configured."""
        return all([
            self.SMTP_HOST,
            self.SMTP_USERNAME,
            self.SMTP_PASSWORD,
            self.EMAIL_FROM,
        ]) 

    @property
    def is_production(self) -> bool:
        """True only when running with ENVIRONMENT=production."""
        return self.ENVIRONMENT == "production"

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """returns the singleton setting instance"""
    return Settings()


settings: Settings = get_settings()