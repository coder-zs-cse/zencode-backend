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
    DEEPSEEK_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    # Pinecone settings
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_ENVIRONMENT: Optional[str] = None
    PINECONE_INDEX: str = "v2-internal-library"

    # MongoDB settings
    MONGODB_URL: str = "mongodb+srv://wcoderzs:a26XEs9UsRzcBx9n@zencode.lqwq8.mongodb.net/?retryWrites=true&w=majority&appName=zencode"
    MONGODB_DB_NAME: str = "zencode_db"
    MONGODB_USER: Optional[str] = None
    MONGODB_PASSWORD: Optional[str] = None
    
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
    def deepseek_api_key(self) -> Optional[str]:
        return self.DEEPSEEK_API_KEY

    @property
    def pinecone_api_key(self) -> Optional[str]:
        return self.PINECONE_API_KEY

    @property
    def pinecone_environment(self) -> Optional[str]:
        return self.PINECONE_ENVIRONMENT

    @property
    def mongodb_url(self) -> str:
        return self.MONGODB_URL
    
@lru_cache()
def get_settings() -> Settings:
    """Get application settings from environment with caching."""
    return Settings()
