from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Application settings."""
    
    # API Keys
    GOOGLE_API_KEY: Optional[str] = None
    GITHUB_TOKEN: Optional[str] = None

    # GitHub Repository Link
    REPO_LINK: Optional[str] = None
    
    # Application settings
    APP_NAME: str = "FastAPI Backend"
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Get application settings from environment with caching."""
    return Settings()
