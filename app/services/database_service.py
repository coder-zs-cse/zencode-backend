from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import get_settings
from typing import Optional, Dict, Any, List

settings = get_settings()

class DatabaseService:
    def __init__(self):
        # self.client = AsyncIOMotorClient(settings.mongodb_url)
        # self.db = self.client[settings.MONGODB_DB_NAME]
        self.client = AsyncIOMotorClient('mongodb+srv://sampleuser:1234@zencode.lqwq8.mongodb.net/?retryWrites=true&w=majority&appName=zencode')
        self.db = self.client[settings.MONGODB_DB_NAME]

    async def connect(self):
        """Test the database connection."""
        try:
            await self.client.admin.command('ping')
            return True
        except Exception as e:
            print(f"Failed to connect to MongoDB: {e}")
            return False

    async def close(self):
        """Close the database connection."""
        self.client.close()

    async def insert_one(self, collection: str, document: Dict[str, Any]) -> str:
        """Insert a single document into the specified collection."""
        result = await self.db[collection].insert_one(document)
        return str(result.inserted_id)

    async def find_one(self, collection: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find a single document in the specified collection."""
        return await self.db[collection].find_one(query)

    async def find_many(self, collection: str, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find multiple documents in the specified collection."""
        cursor = self.db[collection].find(query)
        return await cursor.to_list(length=None)

    async def update_one(self, collection: str, query: Dict[str, Any], update: Dict[str, Any]) -> bool:
        """Update a single document in the specified collection."""
        result = await self.db[collection].update_one(query, {"$set": update})
        return result.modified_count > 0

    async def delete_one(self, collection: str, query: Dict[str, Any]) -> bool:
        """Delete a single document from the specified collection."""
        result = await self.db[collection].delete_one(query)
        return result.deleted_count > 0

# Create a singleton instance
database_service = DatabaseService() 