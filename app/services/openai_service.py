from google import genai
from typing import Optional, Dict, Any, List, Union
import os
from pydantic import BaseModel
class ChatMessage(BaseModel):
    role: str
    content: str

class OpenAIService:
    def __init__(self, api_key: Optional[str] = None):

        self.api_key = api_key
        if not self.api_key:
            raise ValueError("Google API key is required")
        self.client = genai.Client(api_key=self.api_key)
        # Update to match your Pinecone index model
        self.embedding_model = "llama-text-embed-v2"
        
    def generate_content(self, prompt: str, model: str = "gemini-2.0-flash", **kwargs) -> Dict[Any, Any]:

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
    
    def get_embeddings(self, texts: Union[str, List[str]], model: Optional[str] = None) -> List[List[float]]:
        model = model or self.embedding_model
        
        # Convert single string to list for consistent processing
        if isinstance(texts, str):
            texts = [texts]
            
        embeddings = []
        for text in texts:
            # Use Google's API to generate embeddings
            embedding_response = self.client.models.get_embeddings(
                model=model,
                text=text
            )
            embeddings.append(embedding_response.embedding)
            
        return embeddings



