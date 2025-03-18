from fastapi import APIRouter
from app.api.lib.constants.reactbase import reactBase

router = APIRouter()

@router.get("/template")
def get_template():
    return {"template": reactBase} 