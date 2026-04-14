from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    APP_NAME: str = "GlavKrepezh"
    DEBUG: bool = True
    HOST: str
    PORT: int

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    SECRET_KEY: str
    ADMIN_PANEL_PATH: str = "/admin"
    ADMIN_DEFAULT_PASSWORD: str
    PASSWORD_PEPPER: str
    
    CORS_ORIGINS: List[str] = [
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]
    
    STATIC_DIR: Path = BASE_DIR / "static"
    IMAGES_DIR: Path = STATIC_DIR / "images"
    UPLOAD_DIR: Path = BASE_DIR / "uploads" 

    TELEGRAM_BOT_TOKEN: str | None = None
    TELEGRAM_CHAT_IDS: str | None = None

    VK_BOT_TOKEN: str | None = None
    VK_USER_IDS: str | None = None

    SMTP_HOST: str = "smtp.yandex.ru"
    SMTP_PORT: int = 465
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    EMAIL_RECIPIENTS: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

settings.IMAGES_DIR.mkdir(parents=True, exist_ok=True)
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)