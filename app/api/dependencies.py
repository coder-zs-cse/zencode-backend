from fastapi import Depends
from typing import Annotated
from app.services.openai_service import OpenAIService
from app.services.components_service import FetchComponentsService
from app.core.config import get_settings, Settings


def get_openai_service(settings: Settings = Depends(get_settings)) -> OpenAIService:
    """Dependency for getting the OpenAI service instance."""
    return OpenAIService(api_key=settings.GOOGLE_API_KEY)

def get_components_service(settings: Settings = Depends(get_settings)) -> FetchComponentsService:
    """Dependency for getting the Components through GitHub repository"""
    return FetchComponentsService(
        repo_link=settings.REPO_LINK,
        access_token=settings.GITHUB_TOKEN
    )

# Type annotation for dependency injection
OpenAIServiceDep = Annotated[OpenAIService, Depends(get_openai_service)]
FetchComponentsDep = Annotated[FetchComponentsService, Depends(get_components_service)]