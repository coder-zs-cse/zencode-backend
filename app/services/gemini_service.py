from google import genai
from typing import Optional, Dict, Any, List, Union
from google.genai import types
from pydantic import BaseModel
from app.models.builder_steps import ReactResponse
from app.lib.constants.model_config import SYSTEM_PROMPTS, DEFAULT_MAX_TOKENS, DEFAULT_TEMPERATURE, DEFAULT_LLM_MODEL, DEFAULT_EMBEDDING_MODEL

class ChatMessage(BaseModel):
    role: str
    content: str

class ModelConfig:
    def __init__(self, 
                    max_tokens: int = DEFAULT_MAX_TOKENS,
                    temperature: float = DEFAULT_TEMPERATURE,
                    model: str = DEFAULT_LLM_MODEL):
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.model = model 

class GeminiService:
    def __init__(self, 
                 api_key: Optional[str] = None,
                 max_tokens: int = DEFAULT_MAX_TOKENS,
                 temperature: float = DEFAULT_TEMPERATURE,
                 model: str = DEFAULT_LLM_MODEL):
        
        self.api_key = api_key
        if not self.api_key:
            raise ValueError("Google API key is required")
            
        self.client = genai.Client(api_key=self.api_key)
        self.embedding_model = DEFAULT_EMBEDDING_MODEL
        self.model_config = ModelConfig(
            max_tokens=max_tokens,
            temperature=temperature,
            model=model
        )
        
    def generate_content(self, prompt: str, model: Optional[str] = None) -> Dict[Any, Any]:
        model = model or self.model_config.model
        response = self.client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPTS["react_generator"],
                max_output_tokens=self.model_config.max_tokens,
                temperature=self.model_config.temperature,
                response_mime_type='application/json',
                response_schema=ReactResponse,
            ),
        )
        return {
            "text": response.text,
            "raw_response": response
        }
    
    def chat_completion(self, messages: list[ChatMessage], model: Optional[str] = None) -> Dict[Any, Any]:
        model = model or self.model_config.model
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                "parts": [{"text": msg.content}],
                "role": msg.role or "user"
            })
        
        response = self.client.models.generate_content(
            model=model,
            contents=formatted_messages,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPTS["react_generator"],
                max_output_tokens=self.model_config.max_tokens,
                temperature=self.model_config.temperature,
                response_mime_type='application/json',
                response_schema=ReactResponse,
            ),
        )

        return {
            "text": response.text,
            "raw_response": response
        }
    
    def list_models(self) -> list[str]:
        """List available models."""
        models = self.client.models.list()
        return [model.name for model in models]
    



