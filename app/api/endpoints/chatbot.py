from fastapi import APIRouter, HTTPException
from app.api.dependencies import OpenAIServiceDep
from app.services.openai_service import ChatMessage
from typing import List
from pydantic import BaseModel

router = APIRouter()

class GenerateContentRequest(BaseModel):
    prompt: str
    model: str = "gemini-2.0-flash"

class ChatCompletionRequest(BaseModel):
    messages: List[ChatMessage]
    model: str = "gemini-2.0-flash"

@router.get("/chat")
def chat_endpoint():
    return {"message": "This is the chat endpoint. Use POST /chat/completion or /generate for AI responses."}

@router.post("/generate")
def generate_content(request: GenerateContentRequest, openai_service: OpenAIServiceDep):
    try:
        response = openai_service.generate_content(
            prompt=request.prompt,
            model=request.model
        )
        return {"response": response["text"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating content: {str(e)}")

@router.post("/chat/completion")
def chat_completion(request: ChatCompletionRequest, openai_service: OpenAIServiceDep):
    try:
        response = openai_service.chat_completion(
            messages=request.messages,
            model=request.model
        )
        return {"response": response["text"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating chat completion: {str(e)}")

@router.get("/models")
def list_models(openai_service: OpenAIServiceDep):
    try:
        models = openai_service.list_models()
        return {"models": models}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing models: {str(e)}")
