from fastapi import APIRouter, Depends, Header, HTTPException
from typing import Dict, Any
from app.services.user_service import UserService
from pydantic import BaseModel

router = APIRouter()

class UserPreferences(BaseModel):
    preferences: Dict[str, Any]

@router.get("/me")
async def get_current_user_info(x_user_id: str = Header(None)):
    """
    Get current user information.
    If X-User-ID header is not provided, creates a new user.
    """
    user_service = UserService()  # Create an instance of UserService
    user = await user_service.get_or_create_user(user_id=x_user_id)  # Pass the user_id from the header
    return user

@router.put("/preferences")
async def update_user_preferences(
    preferences: UserPreferences,
):
    """Update user preferences."""
    user_service = UserService()
    success = await user_service.update_preferences(
        user_id=user["user_id"],
        preferences=preferences.preferences
    )
    if success:
        return {"message": "Preferences updated successfully"}
    return {"message": "Failed to update preferences"} 