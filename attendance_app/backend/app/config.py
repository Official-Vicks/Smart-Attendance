# ======================================================
# Configuration Loader
# Reads environment variables from .env file
# and makes them accessible throughout the app.
# ======================================================

from pydantic_settings import BaseSettings
from typing import List
from pydantic import AnyUrl, field_validator


class Settings(BaseSettings):
    APP_NAME: str = "Smart Attendance API"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "sqlite:///./attendance.db"

    # Security & JWT
    SECRET_KEY: str = "f8e7c5c3d8a24168a39d77fbbbdcfdd2a2950e4b74b7323a33dc2ef99d2c5b23"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # CORS & Frontend URLs
    ALLOWED_ORIGINS: List[AnyUrl] = [
        "http://127.0.0.1:5500",
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    ]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    def parse_origins(cls, v):
        """Allow comma-separated origins in .env file."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"



# Instantiate global settings object
settings = Settings()