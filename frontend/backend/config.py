import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application settings and configuration."""
    APP_NAME: str = "TRIAGE-AI"
    APP_ENV: str = "development"
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    
    # Database: SQLite by default, easily swapped to PostgreSQL via env var
    DATABASE_URL: str = "sqlite:///./triage.db"
    
    # Uploads folder
    UPLOAD_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
    MAX_UPLOAD_SIZE_MB: int = 10
    
    # AI Engine settings
    AI_PROVIDER: str = "local"  # 'local', 'gemini', or 'openai'
    GEMINI_ENABLED: bool = False
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="allow")

settings = Settings()

# Ensure uploads directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
