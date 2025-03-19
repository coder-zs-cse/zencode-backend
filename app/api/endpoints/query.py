from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

from app.services.openai_service import OpenAIService, ChatMessage
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
            query_text=request.generation_prompt,
            top_k=request.top_k,
            namespace=request.namespace,
            filter=request.filter
        )
        
        context = ""
        for i, match in enumerate(query_results.get('matches', [])):
            # Add information about the component
            context += f"File Import Path: {match['metadata']['file_path']}\n"
            context += f"File Content: {match['metadata']['text']}\n\n"
        
        messages = [
            ChatMessage(
                role="user",
                content=f"""You are a code generation assistant that MUST FOLLOW THESE STRICT RULES:
1. ONLY use components from our internal component library shown in the context below
2. DO NOT import or use any external libraries that aren't already visible in the provided component examples
3. If a needed component is not available in the context, you may create a basic version using only native elements
4. If a component is having input props, then use only those input props that fit the use case.
5. Maintain consistent styling and patterns with the provided examples
6. Generate ONLY the code, without explanations or comments

Below are the available components from our internal library:

{context}

Your task is to generate code for:
{request.generation_prompt}
"""
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