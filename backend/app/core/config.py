
from __future__ import annotations
from functools import lru_cache
from typing import Optional, Literal
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application's settings Loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # ── Application ──────────────────────────────────────────────
    APP_NAME: str = "Complaint Tracking System"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # ___ Set the environment for creating the app _______________
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"

    # ── Database (Supabase PostgreSQL or local) ──────────────────
    DATABASE_URL: str

    # ── JWT Authentication ───────────────────────────────────────
    SECRET_KEY: str 
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 hours

    # ── Redis ────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"

    # ── Email (SMTP) — disabled by default for development ───────
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_USE_TLS: bool = True
    EMAIL_FROM: Optional[str] = None

    # ── Frontend URL (for CORS and email links) ──────────────────
    FRONTEND_URL: str = "http://localhost:5173"  


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