from google import genai
from typing import Optional, Dict, Any
import os
from pydantic import BaseModel

class ChatMessage(BaseModel):
    role: str
    content: str

class OpenAIService:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the OpenAI service with Google's Generative AI client."""
        self.api_key = api_key
        if not self.api_key:
            raise ValueError("Google API key is required")
        self.client = genai.Client(api_key=self.api_key)
        
    def generate_content(self, prompt: str, model: str = "gemini-2.0-flash", **kwargs) -> Dict[Any, Any]:
        """Generate content using the specified model."""
        response = self.client.models.generate_content(
            model=model,
            contents=prompt,
            **kwargs
        )
        return {
            "text": response.text,
            "raw_response": response
        }
    
    def chat_completion(self, messages: list[ChatMessage], model: str = "gemini-2.0-flash", **kwargs) -> Dict[Any, Any]:
        """Generate a chat completion for the provided messages."""
        # Format messages for Google's Generative AI API
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                "parts": [{"text": msg.content}],
                "role": msg.role
            })
        
        response = self.client.models.generate_content(
            model=model,
            contents=formatted_messages,
            **kwargs
        )
        return {
            "text": response.text,
            "raw_response": response
        }
    
    def list_models(self) -> list[str]:
        """List available models."""
        models = self.client.models.list()
        return [model.name for model in models]
