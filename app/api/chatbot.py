from fastapi import APIRouter

router = APIRouter()

@router.get("/chat")
def chat_endpoint():
    return {"message": "This is the chat endpoint"}
