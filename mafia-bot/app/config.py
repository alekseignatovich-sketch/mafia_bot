"""Configuration module for Mafia Bot."""

from pathlib import Path
from typing import List, Optional

from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).parent.parent
LOCALES_DIR = BASE_DIR / "app" / "locales"


class Settings(BaseSettings):
    """Bot configuration settings."""
    
    # Telegram
    BOT_TOKEN: str
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/mafia_bot"
    
    # Redis (optional)
    REDIS_URL: Optional[str] = None
    
    # Bot Settings
    BOT_LANGUAGE: str = "ru"
    DEBUG: bool = False
    
    # Admin IDs
    ADMIN_IDS: List[int] = []
    
    # Game Settings
    DAY_START_HOUR: int = 8
    NIGHT_START_HOUR: int = 0
    VOTE_END_MINUTE: int = 55
    ACTION_END_MINUTE: int = 55
    
    # Webhook (optional)
    WEBHOOK_HOST: Optional[str] = None
    WEBHOOK_PATH: str = "/webhook"
    
    # Supported Languages
    SUPPORTED_LANGUAGES: List[str] = ["ru", "en", "be", "de", "es"]
    DEFAULT_LANGUAGE: str = "ru"
    
    # Game Balance
    MIN_PLAYERS: int = 4
    MAX_PLAYERS: int = 20
    XP_PER_CYCLE: int = 1
    XP_LEVEL_MULTIPLIER: int = 10
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    @property
    def webhook_url(self) -> Optional[str]:
        """Generate webhook URL if host is configured."""
        if self.WEBHOOK_HOST:
            return f"{self.WEBHOOK_HOST}{self.WEBHOOK_PATH}"
        return None
    
    @property
    def is_webhook_mode(self) -> bool:
        """Check if webhook mode is enabled."""
        return self.WEBHOOK_HOST is not None


# Global settings instance
settings = Settings()
