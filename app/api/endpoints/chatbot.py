from fastapi import APIRouter, HTTPException
from app.api.dependencies import OpenAIServiceDep, DeepSeekServiceDep
from app.models.request import GenerateContentRequest, ChatCompletionRequest
from app.models.response import GenerateContentResponse, ChatCompletionResponse
from app.examples.component_enhancer_example import ComponentEnhancer
from app.examples.design_components_test import test_extract_design_components
router = APIRouter()

@router.get("/chat")
def chat_endpoint():
    return {"message": "This is the chat endpoint. Use POST /chat/completion or /generate for AI responses."}

@router.post("/generate", response_model=GenerateContentResponse)
def generate_content(request: GenerateContentRequest, openai_service: DeepSeekServiceDep):
    try:
        response = openai_service.generate_content(
            prompt=request.prompt,
            model=request.model if request.model else "deepseek-chat"
        )
        return GenerateContentResponse(response=response["text"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating content: {str(e)}")

@router.post("/chat/completion", response_model=ChatCompletionResponse)
def chat_completion(request: ChatCompletionRequest, openai_service: OpenAIServiceDep):
    try:
        response = openai_service.chat_completion(
            messages=request.messages,
            model=request.model
        )
        return ChatCompletionResponse(response=response["text"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating chat completion: {str(e)}")

@router.get("/models")
def list_models(openai_service: OpenAIServiceDep):
    try:
        # Test the component enhancer
        # enhancer = ComponentEnhancer()
        # result = enhancer.run_example()
        # test_extract_design_components()
        models = openai_service.list_models()
        return {
            # "enhanced_component": result,
            "models": models
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing models: {str(e)}")

    