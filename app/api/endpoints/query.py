from fastapi import APIRouter, HTTPException, status, Header, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
import json
from app.services.gemini_service import ChatMessage
from app.api.dependencies import PineconeServiceDep, OpenAIServiceDep, DeepSeekServiceDep
from app.lib.constants.model_config import SYSTEM_PROMPTS
from app.models.context import Context, FileNode, InternalComponent
from app.services.database_service import DatabaseService
import app.utils.llm_parser as Utils
from app.models.builder_steps import ReactResponse

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

class GenerateComponentResponse(BaseModel):
    status: str
    generated_code: ReactResponse
    conversation: list[ChatMessage]
    context: dict = {
        "components_used": int,
        "query": str
    }

@router.post("/generate", status_code=status.HTTP_200_OK)
async def generate_with_rag(
    request: GenerateComponentRequest,
    pinecone_service: PineconeServiceDep,
    openai_service: DeepSeekServiceDep,
    userId: str = Header(None),
    database_service: DatabaseService = Depends(DatabaseService)
):
    """
    Query similar components and use them as context to generate 
    new components using the RAG approach.
    """
    try:
        # Get components from vector search
        query_results = {}
        if request.enableAISelection:

            query_results = pinecone_service.query(
                query_text=request.query_text,
                namespace=userId,
            )
        
        # Get paths from both vector search and forced components
        component_paths = [match['id'] for match in query_results.get('matches', [])]
        component_paths.extend(request.forcedComponents)
        
        # Fetch component details from database
        components = []
        if component_paths:
            db_components = await database_service.find_many(
                "components",
                {
                    "componentPath": {"$in": component_paths},
                    "userId": userId
                }
            )
            
            # Create internal components with full details
            for component in db_components:
                components.append(
                    InternalComponent(
                        path=component["componentPath"],
                        name=component["componentName"],
                        description=component.get("description", ""),
                        useCase=component.get("useCase", ""),
                        codeSamples=component.get("codeSamples", []),
                        dependencies=component.get("dependencies", []),
                        importPath=component.get("importPath", "")
                    )
                )
        
        # Create context object
        context = Context(
            user_query=request.query_text,
            codebase=request.codebase, 
            system_prompt=SYSTEM_PROMPTS["react_generator"],
            internal_components=components,
            conversation=request.conversation,
            additional_user_prompt=SYSTEM_PROMPTS["DESIGN"] if not request.conversation else None
        )
        
        # Construct messages from context
        messages = context.construct_messages()
        
        response = openai_service.chat_completion(messages=messages)
        
        react_response = Utils.parse_llm_response_to_react_steps(response.get("text", "")) 

        request.conversation.extend([ChatMessage(role="user",content=request.query_text)])

        return {
            "status": "success",
            "generated_code": react_response,
            "conversation": request.conversation,
            "context": {
                "components_used": len(components),
                "query": request.query_text
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating with RAG: {str(e)}"
        ) 