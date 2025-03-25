from httpx import AsyncClient
from app.core.config import get_settings
from typing import Optional, Dict, Any, List

settings = get_settings()

class DatabaseService:
    def __init__(self):
        self.base_url = "http://localhost:4000/api"  # Update this with your Node.js backend URL
        self.client = AsyncClient()

    async def connect(self):
        """Test the backend connection."""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            return response.status_code == 200
        except Exception as e:
            print(f"Failed to connect to backend: {e}")
            return False

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def insert_one(self, collection: str, document: Dict[str, Any]) -> str:
        """Insert a single document into the specified collection."""
        try:
            response = await self.client.post(
                f"{self.base_url}/{collection}",
                json=document
            )
            result = response.json()
            return str(result.get("insertedId"))
        except Exception as e:
            print(f"Error inserting document into {collection}: {str(e)}")
            return ""

    async def insert_many(self, collection: str, documents: List[Dict[str, Any]]) -> int:
        """Insert multiple documents into the specified collection.
        Returns the number of documents inserted."""
        try:
            response = await self.client.post(
                f"{self.base_url}/{collection}/insertMany",
                json={
                    "documents": documents
                }
            )
            result = response.json()
            return result.get("insertedCount", 0)
        except Exception as e:
            print(f"Error inserting multiple documents into {collection}: {str(e)}")
            return 0
    
    async def find_one(self, collection: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find a single document in the specified collection."""
        try:
            response = await self.client.get(
                f"{self.base_url}/{collection}/findOne",
                params={"query": query}
            )
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            print(f"Error finding document in {collection}: {str(e)}")
            return None

    async def find_many(self, collection: str, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find multiple documents in the specified collection."""
        try:
            response = await self.client.get(
                f"{self.base_url}/{collection}/find",
                params={"query": query}
            )
            return response.json() if response.status_code == 200 else []
        except Exception as e:
            print(f"Error finding documents in {collection}: {str(e)}")
            return []

    async def update_one(self, collection: str, query: Dict[str, Any], update: Dict[str, Any]) -> bool:
        """Update a single document in the specified collection."""
        try:
            response = await self.client.patch(
                f"{self.base_url}/{collection}",
                json={
                    "query": query,
                    "update": update
                }
            )
            result = response.json()
            return result.get("modifiedCount", 0) > 0
        except Exception as e:
            print(f"Error updating document in {collection}: {str(e)}")
            return False

    async def update_many(self, collection: str, query: Dict[str, Any], update: Dict[str, Any]) -> int:
        """Update multiple documents in the specified collection.
        Returns the number of documents modified."""
        try:
            response = await self.client.patch(
                f"{self.base_url}/{collection}/updateMany",
                json={
                    "query": query,
                    "update": update
                }
            )
            result = response.json()
            return result.get("modifiedCount", 0)
        except Exception as e:
            print(f"Error updating multiple documents in {collection}: {str(e)}")
            return 0

    async def delete_one(self, collection: str, query: Dict[str, Any]) -> bool:
        """Delete a single document from the specified collection."""
        try:
            response = await self.client.delete(
                f"{self.base_url}/{collection}",
                params={"query": query}
            )
            result = response.json()
            return result.get("deletedCount", 0) > 0
        except Exception as e:
            print(f"Error deleting document from {collection}: {str(e)}")
            return False

# Create a singleton instance
database_service = DatabaseService() 