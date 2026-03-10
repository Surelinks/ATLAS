"""
Atlas AI - Application Configuration
======================================
All runtime settings are sourced from environment variables (or the ``.env``
file in development) via *pydantic-settings*.  Sensible defaults are provided
for local development so the service can start without any configuration.

Author  : Ezenwanne Kenneth
Project : Atlas AI – Operational Intelligence & Incident Response Platform
Version : 1.0.0
License : MIT
"""

from __future__ import annotations

from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Central configuration object.

    All fields can be overridden by environment variables of the same name
    (case-sensitive).  In production, set ``ENVIRONMENT=production`` and
    supply secrets via your hosting provider's secret management.
    """

    # ------------------------------------------------------------------
    # Application identity
    # ------------------------------------------------------------------
    APP_NAME: str = "Atlas AI"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"   # development | staging | production

    # ------------------------------------------------------------------
    # LLM provider selection
    # Supported values: groq | openai | ollama
    # ------------------------------------------------------------------
    LLM_PROVIDER: str = "groq"

    # Groq (default, free tier with generous rate limits)
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # OpenAI (paid, highest quality)
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"

    # Ollama (self-hosted, fully offline)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"

    # ------------------------------------------------------------------
    # Embedding model (sentence-transformers, runs locally)
    # ------------------------------------------------------------------
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------
    DATABASE_URL: str = "sqlite:///./atlas_ai.db"
    VECTOR_DB_DIRECTORY: str = "./vector_db"

    # ------------------------------------------------------------------
    # API server
    # ------------------------------------------------------------------
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = True

    # ------------------------------------------------------------------
    # CORS
    # Comma-separated list of allowed origins, or ``*`` for all.
    # In production, set ENVIRONMENT=production to allow all origins.
    # ------------------------------------------------------------------
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8501"

    @property
    def cors_origins(self) -> List[str]:
        """Return parsed list of allowed CORS origins."""
        origins = [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]
        if self.ENVIRONMENT == "production" or origins == ["*"]:
            return ["*"]
        return origins

    # ------------------------------------------------------------------
    # Logging & Security
    # ------------------------------------------------------------------
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str = "change-this-in-production-use-openssl-rand-hex-32"

    class Config:
        env_file = ".env"
        case_sensitive = True


# Singleton – import this everywhere instead of instantiating Settings().
settings = Settings()
