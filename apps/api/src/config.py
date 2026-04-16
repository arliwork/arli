"""ARLI API Configuration"""
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://arli:arli_secret@127.0.0.1:5433/arli_prod"
    REDIS_URL: str = "redis://localhost:6379/0"
    JWT_SECRET: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    FRONTEND_URL: str = "http://localhost:3000"
    APP_URL: str = "http://localhost:8000"
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

# Ensure asyncpg driver
if settings.DATABASE_URL.startswith("postgresql://") and not settings.DATABASE_URL.startswith("postgresql+asyncpg://"):
    settings.DATABASE_URL = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
