from functools import lru_cache
from pathlib import Path
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/ (where this file’s package lives)
_BACKEND_DIR = Path(__file__).resolve().parent
# repo root (parent of backend/)
_PROJECT_DIR = _BACKEND_DIR.parent


class Settings(BaseSettings):
    # Database — explicit URL override (preferred for Docker/production)
    DATABASE_URL: str = ""

    # Postgres connection fields (used when DATABASE_URL is not set or for raw psycopg2 access)
    DB_HOST: str = "localhost"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_NAME: str = "ai_voice"
    DB_PORT: int = 5432

    # JWT
    SECRET_KEY: str = "change-me-in-production-use-random-32-char-string"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Email (Gmail / SMTP for verification and notifications)
    EMAIL_USER: str = ""
    EMAIL_PASSWORD: str = ""

    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"

    # Vapi
    VAPI_API_KEY: str = ""
    VAPI_PHONE_NUMBER_ID: str = ""
    VAPI_ASSISTANT_PHONE_NUMBER: str = ""
    VAPI_WEBHOOK_SECRET: str = ""

    # Twilio (for call transfer)
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    HUMAN_TRANSFER_NUMBER: str = ""

    # App
    BACKEND_URL: str = "http://localhost:8001"
    FRONTEND_URL: str = "http://localhost:5173"
    ENVIRONMENT: str = "development"

    # Password reset email (optional — if SMTP_HOST empty, dev logs reset URL instead)
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = ""
    PASSWORD_RESET_TOKEN_HOURS: int = 1

    @property
    def DATABASE_CONFIG(self) -> dict:
        """Raw connection dict for libraries that need individual fields (e.g. psycopg2)."""
        return {
            "host": self.DB_HOST,
            "user": self.DB_USER,
            "password": self.DB_PASSWORD,
            "database": self.DB_NAME,
            "port": self.DB_PORT,
        }

    @property
    def resolved_database_url(self) -> str:
        """
        Resolve DB URL in this order:
        1) DATABASE_URL if set
        2) DB_* fields (Postgres)
        """
        explicit = self.DATABASE_URL.strip()
        if explicit:
            return explicit

        user = quote_plus(self.DB_USER)
        password = quote_plus(self.DB_PASSWORD)
        host = self.DB_HOST
        port = self.DB_PORT
        name = self.DB_NAME
        return f"postgresql://{user}:{password}@{host}:{port}/{name}"

    model_config = SettingsConfigDict(
        # Later files override earlier (repo root .env wins over backend/.env).
        env_file=tuple(
            str(p)
            for p in (_BACKEND_DIR / ".env", _PROJECT_DIR / ".env")
            if p.is_file()
        )
        or None,
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

# ── Module-level exports for legacy direct imports (e.g. from config import SECRET_KEY) ──
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS
DATABASE_URL = settings.resolved_database_url
