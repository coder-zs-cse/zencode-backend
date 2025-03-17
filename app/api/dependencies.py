from fastapi import Depends
from typing import Annotated
from app.services.openai_service import OpenAIService
from app.core.config import get_settings, Settings

def get_openai_service(settings: Settings = Depends(get_settings)) -> OpenAIService:
    """Dependency for getting the OpenAI service instance."""
    return OpenAIService(api_key=settings.GOOGLE_API_KEY)

# Type annotation for dependency injection
OpenAIServiceDep = Annotated[OpenAIService, Depends(get_openai_service)]
