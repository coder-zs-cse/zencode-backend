from httpx import AsyncClient
from app.core.config import get_settings
from typing import Optional, Dict, Any, List, Union
from pydantic import BaseModel, Field
from app.models.component import FileNode, InternalComponent
import json 
import requests

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
            response = await self.client.post(
                f"{self.base_url}/{collection}/findOne",
                json={
                    "query": query
                }
            )
            data = response.json() if response.status_code == 200 else None
            return data
        except Exception as e:
            print(f"Error finding document in {collection}: {str(e)}")
            return None

    async def find_many(self, collection: str, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find multiple documents in the specified collection."""
        try:
            response = await self.client.post(
                f"{self.base_url}/{collection}/find",
                json={
                    "query": query
                }
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

    async def get_missing_internal_components(
        self,
        component_paths: List[str],
        userId: str
    ) -> List[InternalComponent]:
        """
        Fetch internal components by their paths and user ID
        This is a pure database operation that takes a list of component paths and returns FileNodes
        
        Args:
            component_paths: List of component paths to fetch
            userId: The user ID that owns the components
            
        Returns:
            List of FileNode objects with the component details
        """
        if not component_paths:
            return []
            
        # Fetch components from database in a single call
        db_components = await self.find_many(
            "components",
            {
                "componentPath": {"$in": component_paths},
                "userId": userId
            }
        )
        
        # Convert to FileNode objects
        file_nodes = []
        for component in db_components:
            file_nodes.append(
                InternalComponent(
                    path=component["componentPath"],
                    name=component["componentName"],
                    inputProps=component.get("inputProps", ""),
                    useCase=component.get("useCase", ""),
                    code=component.get("code", ""),
                    dependencies=component.get("dependencies", []),
                    codeSamples=component.get("codeSamples", []),
                    useCases=component.get("useCases", []),
                )
            )
            
        return file_nodes

    async def fetch_components_by_paths(
        self, 
        component_paths: List[str], 
        userId: str
    ) -> List[InternalComponent]:
        """
        Fetch multiple components by their paths and user ID
        
        Args:
            component_paths: List of component paths to fetch
            userId: The user ID that owns the components
            
        Returns:
            List of InternalComponent objects with the component details
        """
        components = []
        
        if not component_paths:
            return components
            
        # Fetch components from database
        db_components = await self.find_many(
            "components",
            {
                "componentPath": {"$in": component_paths},
                "userId": userId
            }
        )
        
        # Create internal components with full details
        for component in db_components:
            components.append(
                InternalComponent(
                    path=component["componentPath"],
                    name=component["componentName"],
                    inputProps=component.get("inputProps", ""),
                    useCase=component.get("useCase", ""),
                )
            )
            
        return components
        
    async def fetch_github_data(self, userId: str) -> Optional[Dict[str, Any]]:
        """
        Fetch GitHub repository data for a user
        
        Args:
            userId: The user ID to fetch GitHub data for
            
        Returns:
            Dictionary containing GitHub repository data or None if not found
        """
        # Fetch GitHub repo data
        response = await self.find_one(
            "github",
            {
                "userId": userId,
                "githubUrl": {"$exists": True}
            }
        )
        if response.get("success") and response.get("data"):
            return response["data"]
        return None

    def parse_component_code_sync(self, code: str) -> Dict[str, Any]:
        """Synchronous version of parse_component_code"""
        
        response = requests.post(
            f"{self.base_url}/parse",
            json={"code": code}
        )
        return response.json()
    
    async def parse_component_code(self, code: str) -> Dict[str, Any]:
        """Parse component code to extract dependencies and other metadata"""
        response = await self.client.post(
                f"{self.base_url}/parse",
                json={"code": code}
            )
        data = response.json()
        return data
    
    async def get_github_resources(self, userId: str) -> tuple[List[str], Dict[str, List[str]]]:
        """
        Fetch GitHub resources (CSS files and dependencies) for a user
        
        Args:
            userId: User ID to fetch resources for
            
        Returns:
            Tuple containing:
            - List of CSS files
            - Dictionary of dependencies and devDependencies
        """
        # Initialize empty return values
        css_files = []
        dependencies = {
            "dependencies": [],
            "devDependencies": []
        }
        
        # Fetch GitHub data
        github_data = await self.fetch_github_data(userId)
        
        if github_data:
            # Process CSS files
            if github_data.get("cssFiles"):
                try:
                    css_files = json.loads(github_data["cssFiles"])
                except json.JSONDecodeError:
                    pass
            
            # Process package.json data
            if github_data.get("packageJson"):
                try:
                    package_data = json.loads(github_data["packageJson"])
                    if package_data:
                        if "dependencies" in package_data:
                            dependencies["dependencies"] = package_data["dependencies"].split(",")
                        if "devDependencies" in package_data:
                            dependencies["devDependencies"] = package_data["devDependencies"].split(",")
                except json.JSONDecodeError:
                    pass
        
        return css_files, dependencies

# Create a singleton instance
database_service = DatabaseService() 