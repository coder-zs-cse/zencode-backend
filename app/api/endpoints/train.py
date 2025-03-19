from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, validator
import os
from typing import Optional, Dict, Any
from app.services.openai_service import OpenAIService
from app.api.dependencies import get_settings, PineconeServiceDep

router = APIRouter()

class TrainGitHubRequest(BaseModel):
    github_url: str
    access_token: Optional[str] = None
    namespace: Optional[str] = None
    
    @validator('github_url')
    def validate_github_url(cls, v):
        if not v.startswith('https://github.com/'):
            raise ValueError('Must be a valid GitHub URL')
        return v

@router.post("/github", status_code=status.HTTP_200_OK, response_model=Dict[str, Any])
async def train_github_components(
    request: TrainGitHubRequest,
    pinecone_service: PineconeServiceDep,
    settings = Depends(get_settings)
):
    """
    Trains the RAG system on a GitHub repository, extracting UI components
    and storing them in the Pinecone vector database.
    """
    try:
        # Initialize services
        pinecone_api_key = settings.pinecone_api_key
        pinecone_environment = settings.pinecone_environment
        
        if not pinecone_api_key or not pinecone_environment:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Pinecone configuration not found"
            )
        
        # Train on GitHub repository
        result = pinecone_service.train_github_url(
            github_url=request.github_url,
            access_token=request.access_token,
            namespace=request.namespace
        )
        
        return {
            "status": "success",
            "message": f"Successfully indexed {result['total_components']} components",
            "details": result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing GitHub repository: {str(e)}"
        ) 