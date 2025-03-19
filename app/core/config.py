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
    # Pinecone settings
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_ENVIRONMENT: Optional[str] = None
    PINECONE_INDEX: str = "internal-design-library"

    # Application settings
    APP_NAME: str = "FastAPI Backend"
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
    
    # Convenience properties for consistent naming in endpoints
    @property
    def google_api_key(self) -> Optional[str]:
        return self.GOOGLE_API_KEY

    @property
    def pinecone_api_key(self) -> Optional[str]:
        return self.PINECONE_API_KEY

    @property
    def pinecone_environment(self) -> Optional[str]:
        return self.PINECONE_ENVIRONMENT

@lru_cache()
def get_settings() -> Settings:
    """Get application settings from environment with caching."""
    return Settings()
