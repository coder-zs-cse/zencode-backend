# app/api/endpoints/__init__.py
from fastapi import APIRouter

from .endpoints.chatbot import router as chatbot_router
from .endpoints.template import router as template_router
from .endpoints.train import router as train_router
from .endpoints.query import router as query_router
from .endpoints.users import router as users_router

router = APIRouter()

router.include_router(chatbot_router)
router.include_router(template_router)
router.include_router(train_router, prefix="/train", tags=["train"])
router.include_router(query_router, prefix="/query", tags=["query"])
router.include_router(users_router, prefix="/users", tags=["users"])
