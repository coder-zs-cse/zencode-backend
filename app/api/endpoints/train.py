from fastapi import APIRouter, Depends, HTTPException, status, Header
from pydantic import BaseModel, validator
import os
from typing import Optional, Dict, Any
from app.services.gemini_service import GeminiService
from app.api.dependencies import get_settings, PineconeServiceDep
import asyncio
from app.services.database_service import DatabaseService

router = APIRouter()

class TrainGitHubRequest(BaseModel):
    github_url: str
    access_token: Optional[str] = None
    
    @validator('github_url')
    def validate_github_url(cls, v):
        if not v.startswith('https://github.com/'):
            raise ValueError('Must be a valid GitHub URL')
        return v

@router.post("/github", status_code=status.HTTP_200_OK, response_model=Dict[str, Any])
async def train_github_components(
    request: TrainGitHubRequest,
    pinecone_service: PineconeServiceDep,
    userId: str = Header(None),
    settings = Depends(get_settings),
    database_service: DatabaseService = Depends()
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
        
        # Start training as a background asyncio task
        
        
        async def train_in_background():
            try:
                # Update user status to IN_PROGRESS
                await database_service.update_one(
                    "users",
                    {"_id": userId},
                    {"$set": {
                        "indexingStatus": "IN_PROGRESS",
                        "lastIndexedRepo": request.github_url,
                    }}
                )

                # Train on GitHub repository
                result = pinecone_service.train_github_url(
                    github_url=request.github_url,
                    access_token=request.access_token,
                    namespace=userId
                )
                print(f"Training completed: {result['total_components']} components indexed")

                # Update user status to COMPLETED
                await database_service.update_one(
                    "users",
                    {"_id": userId},
                    {"$set": {
                        "indexingStatus": "COMPLETED",
                        "lastIndexedRepo": request.github_url,
                        "totalComponents": result['total_components']
                    }}
                )
            except Exception as e:
                print(f"Error in background training: {str(e)}")
                # Update user status to ERROR
                await database_service.update_one(
                    "users",
                    {"_id": userId},
                    {"$set": {
                        "indexingStatus": "ERROR",
                        "lastError": str(e)
                    }}
                )
        
        # Create and launch a background task
        asyncio.create_task(train_in_background())
        
        
        return {
            "status": "success",
            "message": "Training in progress",
            "details": {
                "github_url": request.github_url,
                "namespace": userId
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing GitHub repository: {str(e)}"
        ) 