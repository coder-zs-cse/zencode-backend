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
from app.models.builder_steps import ReactResponse, get_dummy_response
import re

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
    internalComponents: list[str] = []
    enableAISelection: bool = True
    session_id: Optional[str] = ""

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
    openai_service: OpenAIServiceDep,
    userId: str = Header(None),
    database_service: DatabaseService = Depends(DatabaseService)
):
    """
    Query similar components and use them as context to generate 
    new components using the RAG approach.
    """
    try:
        if request.session_id:
            session_id = request.session_id
        else:   
            session_id = await database_service.get_or_create_session(userId)
        
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
        css_files = []
        dependencies = {}
        
        if component_paths:
            # Fetch components
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
                        # description=component.get("description", ""),
                        # useCase=component.get("useCase", ""),
                        # codeSamples=component.get("codeSamples", []),
                        # dependencies=component.get("dependencies", []),
                        inputProps=component.get("inputProps", "")
                    )
                )

            # Fetch GitHub repo data for CSS and dependencies
            github_data = await database_service.find_one(
                "github",
                {
                    "userId": userId,
                    "githubUrl": {"$exists": True}
                }
            )

            if github_data:
                # Get CSS files
                if github_data.get("cssFiles"):
                    css_files = json.loads(github_data["cssFiles"])

                # Parse package.json data
                if github_data.get("packageJson"):
                    package_data = json.loads(github_data["packageJson"])
                    if package_data:
                        # Get the first package.json entry (assuming main package.json)
                        main_package = package_data[0] if isinstance(package_data, list) else package_data
                        if main_package:
                            if "dependencies" in main_package:
                                dependencies["dependencies"] = main_package["dependencies"].split(",")
                            if "devDependencies" in main_package:
                                dependencies["devDependencies"] = main_package["devDependencies"].split(",")
        
        # Create context object
        context = Context(
            user_query=request.query_text,
            codebase=request.codebase, 
            system_prompt=SYSTEM_PROMPTS["react_generator"],
            internal_components=components,
            conversation=request.conversation,
            additional_user_prompt=SYSTEM_PROMPTS["DESIGN"] if not request.conversation else None,
            css_tokens={"files": css_files},
            dependencies=dependencies
        )
        
        # Construct messages from context
        messages = context.construct_messages()
        
        # Use dummy response instead of actual generation
        # react_response = get_dummy_response()

        response = openai_service.chat_completion(messages=messages)
        
        react_response = Utils.parse_llm_response_to_react_steps(response.get("text", ""))

        request.conversation.extend([ChatMessage(role="user",content=request.query_text)])
        request.conversation.extend([ChatMessage(role="assistant",content=react_response)])

        session_updates = {
            "userId": userId,
            "messages": [msg.model_dump() for msg in request.conversation],  # Serialize message objects
            "codebase": [file.model_dump() for file in request.codebase],  # Serialize file objects
        }
        await database_service.update_session(session_id, session_updates)

        return {
            "status": "success",
            "session_id": session_id,
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