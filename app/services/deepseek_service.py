from openai import OpenAI
from typing import Optional, Dict, Any, List, Union
from pydantic import BaseModel
from app.models.builder_steps import ReactResponse
from app.lib.constants.model_config import SYSTEM_PROMPTS, DEFAULT_MAX_TOKENS, DEFAULT_TEMPERATURE, DEFAULT_LLM_MODEL
from langchain_openai import ChatOpenAI

class ChatMessage(BaseModel):
    role: str
    content: str

class ModelConfig:
    def __init__(self, 
                    max_tokens: int = DEFAULT_MAX_TOKENS,
                    temperature: float = DEFAULT_TEMPERATURE,
                    model: str = "deepseek-chat"):
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.model = model 

class DeepSeekService:
    def __init__(self, 
                 api_key: Optional[str] = None,
                 max_tokens: int = DEFAULT_MAX_TOKENS,
                 temperature: float = DEFAULT_TEMPERATURE,
                 model: str = "deepseek-chat"):
        
        self.api_key = api_key
        if not self.api_key:
            raise ValueError("DeepSeek API key is required")
            
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com"
        )
        
        self.model_config = ModelConfig(
            max_tokens=max_tokens,
            temperature=temperature,
            model=model
        )
        
    def generate_content(self, prompt: str, model: Optional[str] = None) -> Dict[Any, Any]:
        model = model or self.model_config.model
        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPTS["react_generator"]},
                {"role": "user", "content": prompt}
            ],
            max_tokens=self.model_config.max_tokens,
            temperature=self.model_config.temperature,
            stream=False
        )
        
        return {
            "text": response.choices[0].message.content,
            "raw_response": response
        }
    
    def chat_completion(self, messages: list[ChatMessage], model: Optional[str] = None) -> Dict[Any, Any]:
        model = model or self.model_config.model
        formatted_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        # Add system message if not present
        if not any(msg.role == "system" for msg in messages):
            formatted_messages.insert(0, {
                "role": "system",
                # "content": SYSTEM_PROMPTS["react_generator"]
                "content": SYSTEM_PROMPTS["XML_SYSTEM_PROMPT"]
            })
        
        response = self.client.beta.chat.completions.parse(
            model=model,
            messages=formatted_messages,
            max_tokens=self.model_config.max_tokens,
            temperature=self.model_config.temperature,
            # response_format=ReactResponse,
        )

        return {
            "text": response.choices[0].message.content,
            "raw_response": response
        }
    
    def lc_chat_completion(self, messages: list[ChatMessage], model: Optional[str] = None) -> Dict[Any, Any]:
        model = model or self.model_config.model
        formatted_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        # Add system message if not present
        if not any(msg.role == "system" for msg in messages):
            formatted_messages.insert(0, {
                "role": "system",
                "content": SYSTEM_PROMPTS["react_generator"]
            })
        
        # Initialize the LLM with structured output
        llm = ChatOpenAI(model=model, temperature=self.model_config.temperature)
        structured_llm = llm.with_structured_output(ReactResponse)

        # Invoke the structured LLM
        response = structured_llm.invoke(formatted_messages)

        return {
            "text": response.text,
            "raw_response": response
        }
    
    def list_models(self) -> list[str]:
        """List available models."""
        # DeepSeek currently only has one main model
        return ["deepseek-chat"]
