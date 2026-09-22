"""Application configuration and environment management."""

import os
from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # API Keys
    NEWS_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # Server Configuration
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    ENVIRONMENT: str = "development"

    # CORS Settings
    FRONTEND_ORIGIN: str = "http://localhost:5500,http://127.0.0.1:5500"

    # Limits and Cache
    NEWS_CACHE_MINUTES: int = 10
    MAX_ARTICLE_LENGTH: int = 12000

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origins(self) -> List[str]:
        """Parse comma-separated frontend origins for CORS."""
        if not self.FRONTEND_ORIGIN or self.FRONTEND_ORIGIN.strip() == "*":
            return ["*"] if self.ENVIRONMENT == "development" else []
        return [origin.strip() for origin in self.FRONTEND_ORIGIN.split(",") if origin.strip()]

    @property
    def is_news_api_configured(self) -> bool:
        """Check if NewsAPI key is configured and not placeholder."""
        val = (self.NEWS_API_KEY or "").strip()
        return bool(val and val != "your_newsapi_key_here" and len(val) > 5)

    @property
    def is_groq_configured(self) -> bool:
        """Check if Groq API key is configured and not placeholder."""
        val = (self.GROQ_API_KEY or "").strip()
        return bool(val and val != "your_groq_api_key_here" and len(val) > 5)

    def log_safe_status(self) -> dict:
        """Return safe configuration status dictionary with masked secrets."""
        return {
            "NEWS_API_KEY configured": self.is_news_api_configured,
            "GROQ_API_KEY configured": self.is_groq_configured,
            "GROQ_MODEL": self.GROQ_MODEL,
            "ENVIRONMENT": self.ENVIRONMENT,
            "NEWS_CACHE_MINUTES": self.NEWS_CACHE_MINUTES,
            "MAX_ARTICLE_LENGTH": self.MAX_ARTICLE_LENGTH,
            "CORS_ORIGINS": self.cors_origins,
        }


@lru_cache()
def get_settings() -> Settings:
    """Return cached Settings instance."""
    return Settings()


settings = get_settings()
