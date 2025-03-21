from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional, Dict, Any

from app.services.openai_service import ChatMessage
from app.api.dependencies import PineconeServiceDep, OpenAIServiceDep

router = APIRouter()

class QueryComponentsRequest(BaseModel):
    query_text: str
    namespace: Optional[str] = None
    top_k: Optional[int] = 5
    filter: Optional[Dict[str, Any]] = None
    
class GenerateComponentRequest(BaseModel):
    query_text: str
    namespace: Optional[str] = None
    top_k: Optional[int] = 3
    filter: Optional[Dict[str, Any]] = None
    generation_prompt: str

@router.post("/components", status_code=status.HTTP_200_OK)
async def query_components(
    request: QueryComponentsRequest,
    pinecone_service: PineconeServiceDep
):
    """
    Query the Pinecone vector database for UI components 
    that match the search criteria.
    """
    try:
        results = pinecone_service.query(
            query_text=request.query_text,
            top_k=request.top_k,
            namespace=request.namespace,
            filter=request.filter
        )
        
        formatted_results = []
        for match in results.get('matches', []):
            formatted_results.append({
                'score': match['score'],
                'metadata': match['metadata']
            })
            
        return {
            "status": "success",
            "matches": formatted_results
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error querying components: {str(e)}"
        )

@router.post("/generate", status_code=status.HTTP_200_OK)
async def generate_with_rag(
    request: GenerateComponentRequest,
    pinecone_service: PineconeServiceDep,
    openai_service: OpenAIServiceDep
):
    """
    Query similar components and use them as context to generate 
    new components using the RAG approach.
    """
    try:
        query_results = pinecone_service.query(
            query_text=request.query_text,
            top_k=request.top_k,
            namespace=request.namespace,
            filter=request.filter
        )
        
        context = ""
        for i, match in enumerate(query_results.get('matches', [])):
            # Add information about the component
            context += f"Internal component Import Path: {match['metadata']['file_path']}\n"
            context += f"Internal component Content: {match['metadata']['text']}\n\n"
        
        messages = [
            ChatMessage(
                role="user",
                content= context
            ),
            ChatMessage(
                role="user",
                content= request.generation_prompt
            )
        ]
        
        response = openai_service.chat_completion(messages=messages)
        
        return {
            "status": "success",
            "generated_code": response["text"],
            "context": {
                "components_used": len(query_results.get('matches', [])),
                "query": request.query_text
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating with RAG: {str(e)}"
        ) 