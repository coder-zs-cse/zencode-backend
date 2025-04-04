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
                    model: str = "gpt-4o-mini"):
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.model = model 

class OpenAIService:
    def __init__(self, 
                 api_key: Optional[str] = None,
                 max_tokens: int = DEFAULT_MAX_TOKENS,
                 temperature: float = DEFAULT_TEMPERATURE,
                 model: str = "gpt-4o-mini"):
        
        self.api_key = api_key
        if not self.api_key:
            raise ValueError("OPENAI API key is required")
            
        self.client = OpenAI(
            api_key=self.api_key
        )
        
        self.model_config = ModelConfig(
            max_tokens=max_tokens,
            temperature=temperature,
            model=model
        )
        
    def generate_content(self, prompt: str, model: Optional[str] = None, system_prompt: Optional[str] = None) -> Dict[Any, Any]:
        model = model or self.model_config.model
        
        messages = [{"role": "user", "content": prompt}]
        if system_prompt:
            messages.insert(0, {"role": "system", "content": system_prompt})
        
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=self.model_config.max_tokens,
            temperature=self.model_config.temperature,
            response_format={"type": "json_object"},
            stream=False
        )
        
        return {
            "text": response.choices[0].message.content,
            "raw_response": response
        }
    
    def chat_completion(self, messages: list[ChatMessage], model: Optional[str] = None, response_format: Optional[Dict[str, str]] = None, tools: Optional[List[Dict]] = None, tool_choice: Optional[Dict] = None) -> Dict[Any, Any]:
        model = model or self.model_config.model
        formatted_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        # Add system message if not present
        # if not any(msg.role == "system" for msg in messages):
        #     formatted_messages.insert(0, {
        #         "role": "system",
        #         "content": SYSTEM_PROMPTS["XML_SYSTEM_PROMPT"]
        #     })
        
        completion_args = {
            "model": model,
            "messages": formatted_messages,
            "max_tokens": self.model_config.max_tokens,
            "temperature": self.model_config.temperature,
        }
        
        if response_format:
            completion_args["response_format"] = response_format
            
        if tools:
            completion_args["tools"] = tools
            
        if tool_choice:
            completion_args["tool_choice"] = tool_choice

        response = self.client.chat.completions.create(**completion_args)

        return {
            "text": response.choices[0].message.content,
            "raw_response": response
        }
    
    async def lc_chat_completion(self, messages: list[ChatMessage], model: Optional[str] = None) -> Dict[Any, Any]:
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
        response = await structured_llm.ainvoke(formatted_messages)

        return {
            "text": response.text,
            "raw_response": response
        }
    
    def list_models(self) -> list[str]:
        """List available models."""
        # DeepSeek currently only has one main model
        return [""]
