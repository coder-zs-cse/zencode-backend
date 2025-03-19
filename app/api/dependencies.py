from fastapi import Depends
from typing import Annotated
from app.services.openai_service import OpenAIService
from app.services.ingestion_service import FetchComponentsService
from app.services.pinecone_service import PineconeService
from app.core.config import get_settings, Settings


def get_openai_service(settings: Settings = Depends(get_settings)) -> OpenAIService:
    """Dependency for getting the OpenAI service instance."""
    return OpenAIService(api_key=settings.GOOGLE_API_KEY)

def get_pinecone_service(
    settings: Settings = Depends(get_settings),
) -> PineconeService:
    """Dependency for getting the Pinecone service instance."""
    return PineconeService(
        api_key=settings.PINECONE_API_KEY,
        environment=settings.PINECONE_ENVIRONMENT,
        index_name=settings.PINECONE_INDEX,
        dimension=1024,  # Set to match your llama-text-embed-v2 model
    )

OpenAIServiceDep = Annotated[OpenAIService, Depends(get_openai_service)]
PineconeServiceDep = Annotated[PineconeService, Depends(get_pinecone_service)]