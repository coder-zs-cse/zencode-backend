from pydantic import BaseModel
from typing import List, Optional
from app.services.openai_service import ChatMessage

class GenerateContentRequest(BaseModel):
    prompt: str
    model: Optional[str] = "gemini-2.0-flash"

class ChatCompletionRequest(BaseModel):
    messages: List[ChatMessage]
    model: Optional[str] = "gemini-2.0-flash" 