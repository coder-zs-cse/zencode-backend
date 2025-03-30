from fastapi import APIRouter, HTTPException, status, Header
from pydantic import BaseModel
from typing import Optional, Dict, Any
import json
from app.services.gemini_service import ChatMessage
from app.api.dependencies import PineconeServiceDep, OpenAIServiceDep, DeepSeekServiceDep
from app.lib.constants.model_config import SYSTEM_PROMPTS
from app.models.context import Context, FileNode, InternalComponent

router = APIRouter()

class QueryComponentsRequest(BaseModel):
    query_text: str
    namespace: Optional[str] = None
    top_k: Optional[int] = 5
    filter: Optional[Dict[str, Any]] = None



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


class GenerateComponentRequest(BaseModel):
    query_text: str
    conversation: list[ChatMessage] = []
    codebase: list[FileNode] = []
    forcedComponents: list[str] = []
    enableAISelection: bool = True


@router.post("/generate", status_code=status.HTTP_200_OK)
async def generate_with_rag(
    request: GenerateComponentRequest,
    pinecone_service: PineconeServiceDep,
    openai_service: DeepSeekServiceDep,
    userId: str = Header(None),
):
    """
    Query similar components and use them as context to generate 
    new components using the RAG approach.
    """
    try:
        query_results = pinecone_service.query(
            query_text=request.query_text,
            namespace=userId,
        )
        
        # Create internal components from query results
        internal_components = []
        for match in query_results.get('matches', []):
            internal_components.append(
                InternalComponent(
                    import_path=match['id'],
                    content=match['metadata']
                )
            )
        
        # Create context object
        context = Context(
            user_query=request.query_text,
            codebase=request.codebase, 
            system_prompt=SYSTEM_PROMPTS["react_generator"],
            internal_components=internal_components,
            conversation=request.conversation,
            additional_user_prompt=SYSTEM_PROMPTS["DESIGN"] if not request.conversation else None
        )
        
        # Construct messages from context
        messages = context.construct_messages()
        
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