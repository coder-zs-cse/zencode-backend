from pydantic import BaseModel
from typing import List, Optional
from app.services.gemini_service import ChatMessage

class GenerateContentRequest(BaseModel):
    prompt: str
    model: Optional[str]

class ChatCompletionRequest(BaseModel):
    messages: List[ChatMessage]
    model: Optional[str]