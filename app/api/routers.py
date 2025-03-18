# app/api/endpoints/__init__.py
from fastapi import APIRouter

from .endpoints.chatbot import router as chatbot_router
from .endpoints.template import router as template_router

router = APIRouter()

router.include_router(chatbot_router)
router.include_router(template_router)
