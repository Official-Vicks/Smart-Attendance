from pydantic_settings import BaseSettings
from pathlib import Path
from typing import List

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    APP_NAME: str = "Smart Attendance"
    DEBUG: bool = False

    DATABASE_URL: str
    SECRET_KEY: str

    SUPABASE_URL: str
    SUPABASE_SERVICE_ROLE_KEY: str

    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    CORS_ORIGINS: str = ""

    class Config:
        env_file = BASE_DIR / ".env"
        env_file_encoding = "utf-8"

    @property
    def cors_origins(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


settings = Settings()
