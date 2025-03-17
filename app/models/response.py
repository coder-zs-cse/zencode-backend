from pydantic import BaseModel

class GenerateContentResponse(BaseModel):
    response: str

class ChatCompletionResponse(BaseModel):
    response: str