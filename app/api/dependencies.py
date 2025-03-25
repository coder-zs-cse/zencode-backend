from fastapi import Depends
from typing import Annotated, Optional
from app.services.gemini_service import GeminiService
from app.services.deepseek_service import DeepSeekService
from app.services.pinecone_service import PineconeService
from app.core.config import get_settings, Settings
from app.services.openai_service import OpenAIService

def get_openai_service(settings: Settings = Depends(get_settings)) -> OpenAIService:
    """Dependency for getting the OpenAI service instance."""
    return OpenAIService(api_key=settings.OPENAI_API_KEY)

def get_deepseek_service(settings: Settings = Depends(get_settings)) -> DeepSeekService:
    """Dependency for getting the DeepSeek service instance."""
    return DeepSeekService(api_key=settings.DEEPSEEK_API_KEY)

def get_pinecone_service(
    settings: Settings = Depends(get_settings),
) -> PineconeService:
    """Dependency for getting the Pinecone service instance."""
    return PineconeService(
        api_key=settings.PINECONE_API_KEY,
        environment=settings.PINECONE_ENVIRONMENT,
        index_name=settings.PINECONE_INDEX,
        openai_api_key=settings.OPENAI_API_KEY,
        dimension=3072,  # Set to match your llama-text-embed-v2 model
    )


OpenAIServiceDep = Annotated[OpenAIService, Depends(get_openai_service)]
DeepSeekServiceDep = Annotated[DeepSeekService, Depends(get_deepseek_service)]
PineconeServiceDep = Annotated[PineconeService, Depends(get_pinecone_service)]
