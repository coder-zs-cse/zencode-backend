from typing import Optional, Dict, Any, List
from datetime import datetime
from app.services.database_service import database_service
import uuid

class UserService:
    COLLECTION_NAME = "users"

    async def get_or_create_user(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get an existing user or create a new one if user_id is not provided."""
        if user_id:
            existing_user = await self.get_user_by_id(user_id)
            if existing_user:
                return existing_user

        # Generate new user_id if not provided or if provided id doesn't exist
        new_user_id = user_id if user_id else str(uuid.uuid4())
        
        # Create new user document
        user_doc = {
            "user_id": new_user_id,
            "created_at": datetime.utcnow(),
            "last_active": datetime.utcnow(),
            "preferences": {},  # Store user preferences here
            "is_active": True
        }

        # Insert user into database
        await database_service.insert_one(self.COLLECTION_NAME, user_doc)
        return user_doc

    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a user by their ID."""
        return await database_service.find_one(
            self.COLLECTION_NAME,
            {"user_id": user_id}
        )

    async def update_user(self, user_id: str, update_data: Dict[str, Any]) -> bool:
        """Update user information."""
        update_data["last_active"] = datetime.utcnow()
        return await database_service.update_one(
            self.COLLECTION_NAME,
            {"user_id": user_id},
            update_data
        )

    async def update_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """Update user preferences."""
        return await database_service.update_one(
            self.COLLECTION_NAME,
            {"user_id": user_id},
            {"preferences": preferences, "last_active": datetime.utcnow()}
        )

    async def delete_user(self, user_id: str) -> bool:
        """Delete a user."""
        return await database_service.delete_one(
            self.COLLECTION_NAME,
            {"user_id": user_id}
        )
