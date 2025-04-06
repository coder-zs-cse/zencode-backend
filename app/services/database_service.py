from httpx import AsyncClient
from app.core.config import get_settings
from typing import Optional, Dict, Any, List, Union
from pydantic import BaseModel, Field

settings = get_settings()

class ComponentFile(BaseModel):
    """Model representing a React component file in the database."""
    name: str
    path: str 
    description: str = ""
    inputProps: List[Dict[str, Any]] = Field(default_factory=list)
    useCases: List[str] = Field(default_factory=list)
    codeExamples: List[str] = Field(default_factory=list)
    user_id: Optional[str] = None
    file_type: str = "react_component"
    
    class Config:
        validate_assignment = True
        arbitrary_types_allowed = True

class CSSFile(BaseModel):
    """Model representing a CSS file in the database."""
    name: str
    path: str
    classes: List[Dict[str, str]] = Field(default_factory=list)
    custom_properties: List[str] = Field(default_factory=list)
    media_queries: List[str] = Field(default_factory=list)
    animations: List[str] = Field(default_factory=list)
    text: str = ""  # For search purposes
    user_id: Optional[str] = None
    file_type: str = "css"
    
    class Config:
        validate_assignment = True
        arbitrary_types_allowed = True

class PackageFile(BaseModel):
    """Model representing a package.json file in the database."""
    name: str
    githubUrl: str
    path: str
    version: str = ""
    description: str = ""
    dependencies: Dict[str, str] = Field(default_factory=dict)
    devDependencies: Dict[str, str] = Field(default_factory=dict)
    scripts: Dict[str, str] = Field(default_factory=dict)
    total_dependencies: int = 0
    total_dev_dependencies: int = 0
    total_scripts: int = 0
    text: str = ""  # For search purposes
    user_id: Optional[str] = None
    file_type: str = "package.json"
    
    class Config:
        validate_assignment = True
        arbitrary_types_allowed = True

class DesignConfigFile(BaseModel):
    """Model representing a design configuration file in the database."""
    name: str
    path: str
    has_theme: bool = False
    has_plugins: bool = False
    has_extends: bool = False
    colors: Dict[str, str] = Field(default_factory=dict)
    theme_preview: str = ""
    plugins_preview: str = ""
    extends_preview: str = ""
    text: str = ""  # For search purposes
    user_id: Optional[str] = None
    file_type: str = "design_config"
    
    class Config:
        validate_assignment = True
        arbitrary_types_allowed = True

class GithubRepo(BaseModel):
    """Model representing a GitHub repository in the database."""
    githubUrl: str
    userId: str
    indexingStatus: str = Field(None, pattern='^(IN_PROGRESS|ERROR|COMPLETED)$')
    componentList: List[str] = Field(default_factory=list)
    packageJson: Optional[str] = None
    cssFiles: Optional[str] = None
    designConfigFiles: Optional[str] = None
    
    class Config:
        validate_assignment = True
        arbitrary_types_allowed = True

class Component(BaseModel):
    """Model representing a component in the database."""
    userId: str
    githubUrl: str
    componentName: str
    indexingStatus: bool = False
    componentPath: str
    description: str = ""
    useCase: str = ""
    codeSamples: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    importPath: str = ""
    
    class Config:
        validate_assignment = True
        arbitrary_types_allowed = True

class FileNode(BaseModel):
    """Model representing a file in the codebase."""
    fileName: str
    filePath: str
    fileContent: str

class Message(BaseModel):
    """Model representing a message in the session."""
    role: str
    content: Union[str, Dict[str, Any]]

class Session(BaseModel):
    """Model representing a chat session."""
    userId: str
    messages: List[Message] = Field(default_factory=list)
    codebase: List[FileNode] = Field(default_factory=list)
    internalComponents: List[str] = Field(default_factory=list)
    npmPackages: List[str] = Field(default_factory=list)
    
    class Config:
        validate_assignment = True
        arbitrary_types_allowed = True

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
            result = response.json()
            return result if response.status_code == 200 else []
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

    async def update_many(self, collection: str, updates: List[Dict[str, Any]]) -> int:
        """Update multiple documents in the specified collection using bulk operations.
        
        Args:
            collection: The collection to update
            updates: List of update operations, each containing 'filter' and 'update' keys
            
        Returns:
            Number of documents modified
        """
        try:
            response = await self.client.patch(
                f"{self.base_url}/{collection}/updateMany",
                json={
                    "updates": updates
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

    async def get_or_create_session(self, user_id: str) -> str:
        """Get an existing session or create a new one for the user.
        
        Returns:
            Tuple of (session_data, is_new_session)
        """
        try:
            # Try to find existing session
            # session = await self.find_one("sessions", {"userId": user_id})
            # if session:
            #     return session, False
            
            # # Create new session if none exists
            new_session = Session(userId=user_id)
            session_id = await self.insert_one("sessions", new_session.dict())
            if not session_id:
                raise Exception("Failed to create new session")
            
            return session_id
            
        except Exception as e:
            print(f"Error in get_or_create_session: {str(e)}")
            raise

    async def update_session(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """Update a session with new data.
        
        Args:
            session_id: The ID of the session to update
            updates: The updates to apply to the session
            
        Returns:
            bool indicating success
        """
        try:
            success = await self.update_one(
                "sessions",
                {"_id": session_id},
                {"$set": updates}
            )
            return success
        except Exception as e:
            print(f"Error updating session: {str(e)}")
            return False

# Create a singleton instance
database_service = DatabaseService() 