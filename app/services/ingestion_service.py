from typing import Optional, List, Any, Dict, TypedDict
import re
import requests
import json
import base64
import json
from pydantic import BaseModel
from app.lib.constants.reactbase import COMPONENT_FUNCTION_SCHEMA, COMPONENT_SYSTEM_PROMPT
from app.services.openai_service import OpenAIService, ChatMessage
from app.core.config import get_settings

class FetchedComponent(BaseModel):
    file: str
    fileContent: str
    path: str


class Component(BaseModel):
    name: str
    path: str
    description: str
    inputProps: List[Dict[str, Any]]
    useCases: List[str]
    codeExamples: List[str]

class CSSClass(BaseModel):
    name: str
    properties: str

class CSSMetadata(BaseModel):
    file_type: str
    file_path: str
    classes: List[CSSClass]
    custom_properties: List[str]
    media_queries: List[str]
    animations: List[str]

class CSSDetails(BaseModel):
    text: str
    name: str
    file_path: str
    metadata: str

class PackageMetadata(BaseModel):
    file_type: str
    file_path: str
    name: str
    version: str
    description: str
    dependencies: Dict[str, str]
    devDependencies: Dict[str, str]
    scripts: Dict[str, str]
    total_dependencies: int
    total_dev_dependencies: int
    total_scripts: int

class PackageDetails(BaseModel):
    text: str
    name: str
    file_path: str
    metadata: str

class ProcessedFile(BaseModel):
    text: str
    name: str
    file_path: str
    metadata: str

class FetchComponentsService:
    def __init__(self, 
                 repo_link: Optional[str] = None, 
                 access_token: Optional[str] = None,
                ):
        self.repo_link = repo_link
        self.access_token = access_token
        self.openai_service = OpenAIService(api_key=get_settings().OPENAI_API_KEY)
        
        if not self.repo_link:
            raise ValueError("GitHub Repository link is required")
        
        # Extract owner and repo from the link
        parts = self.repo_link.rstrip('/').split('/')
        if len(parts) < 2:
            raise ValueError("Invalid GitHub repository link")
        self.owner = parts[-2]
        self.repo = parts[-1]

        # Set up headers with authentication if token is provided
        self.headers = {}
        if self.access_token:
            self.headers['Authorization'] = f'token {self.access_token}'

    def parse_components(self, components: List[FetchedComponent]) -> List[Component]:
        """Parse multiple components using OpenAI LLM with batch processing to prevent token limit issues."""
        try:
            result_components = []
            
            # Batch processing - process 3 components at a time
            # This number can be adjusted based on component size and model token limits
            BATCH_SIZE = 10
            
            for i in range(0, len(components), BATCH_SIZE):
                batch = components[i:i+BATCH_SIZE]
                
                # Skip empty batches
                if not batch:
                    continue
                    
                print(f"Processing batch {i//BATCH_SIZE + 1}/{(len(components) + BATCH_SIZE - 1)//BATCH_SIZE}: {len(batch)} components")
                
                # Process this batch and add results to our list
                batch_components = self._process_component_batch(batch)
                result_components.extend(batch_components)

            return result_components

        except Exception as e:
            print(f"Error in parse_components: {str(e)}")
            return []
            
    def _process_component_batch(self, batch: List[FetchedComponent]) -> List[Component]:
        """Process a batch of components using OpenAI LLM."""
        try:
            # Combine all component files with their paths for this batch
            combined_content = "\n\n".join([
                f"File: {comp.path}\n{comp.fileContent}" 
                for comp in batch
            ])

            # Prepare messages for the LLM with a more direct prompt
            messages = [
                ChatMessage(role="system", content=COMPONENT_SYSTEM_PROMPT),
                ChatMessage(
                    role="user", 
                    content=(
                        f"Analyze these React components and provide detailed information about them in JSON format. "
                        f"The response should be a valid JSON object with a 'components' array containing component details. "
                        f"Each component should have: description, inputProps (array of objects with name, type, description, required), "
                        f"useCases (array of strings), and codeExamples (array of strings).\n\n{combined_content}"
                    )
                )
            ]

            # Call OpenAI without function calling
            response = self.openai_service.chat_completion(
                messages=messages
            )

            # Extract JSON using regex
            response_text = response.get("text", "")
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            
            if not json_match:
                print("No JSON found in response for batch")
                return []

            batch_components = []
            try:
                parsed_data = json.loads(json_match.group(0))
                components_data = parsed_data.get("components", [])
                
                # Create Component objects with correct name and path from original FetchedComponent
                # Make sure we have the same number of components in both lists
                min_length = min(len(components_data), len(batch))
                
                # Use zip to iterate through both lists simultaneously
                for orig_comp, comp_data in zip(batch, components_data[:min_length]):
                    # Use the original component's path and name
                    comp_data["name"] = orig_comp.file
                    comp_data["path"] = orig_comp.path
                    batch_components.append(Component(**comp_data))
                
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON from response: {str(e)}")
            except Exception as e:
                print(f"Error parsing component data: {str(e)}")

            return batch_components
            
        except Exception as e:
            print(f"Error in _process_component_batch: {str(e)}")
            return []

    def fetch_directory_contents(self, path: str = "") -> list[FetchedComponent]:
        """Recursively fetch contents of a directory."""
        try:
            # GitHub API endpoint for repository contents
            api_url = f"https://api.github.com/repos/{self.owner}/{self.repo}/contents/{path}"
            response = requests.get(api_url, headers=self.headers)
            response.raise_for_status()
            
            fetchedComponents = []
            
            for item in response.json():
                if item['type'] == 'file':
                    # Get file content
                    content_response = requests.get(item['download_url'], headers=self.headers)
                    content_response.raise_for_status()
                    
                    fetchedComponents.append(FetchedComponent(
                        file=item['name'],
                        fileContent=content_response.text,
                        path=item['path']
                    ))
                elif item['type'] == 'dir':
                    # Recursively fetch contents of subdirectories
                    subdir_contents = self.fetch_directory_contents(item['path'])
                    fetchedComponents.extend(subdir_contents)
            
            return fetchedComponents
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching contents for path {path}:", str(e))
            raise
        except Exception as e:
            print(f"Caught Exception for path {path}:", str(e))
            raise

    def extract_components(self):
        """Main method to extract all components from the repository."""
        try:
            return self.fetch_directory_contents()
        except Exception as e:
            print("Error in extract_components:", str(e))
            raise

    def parse_css_file(self, file_name: str, file_content: str, file_path: str) -> CSSDetails:
        """
        Parse CSS file content to extract meaningful information for Pinecone.
        Returns both text for embedding and structured metadata for LLM context.
        """
        # Initialize containers
        classes = []
        custom_properties = []
        media_queries = []
        animations = []
        
        # Extract CSS classes
        class_matches = re.finditer(r'\.([a-zA-Z0-9_-]+)\s*{([^}]+)}', file_content)
        for match in class_matches:
            class_name = match.group(1)
            properties = match.group(2).strip()
            classes.append(CSSClass(name=class_name, properties=properties))
        
        # Extract CSS custom properties
        custom_prop_matches = re.finditer(r'--([a-zA-Z0-9_-]+)\s*:', file_content)
        for match in custom_prop_matches:
            custom_properties.append(match.group(1))
        
        # Extract media queries
        media_matches = re.finditer(r'@media\s+([^{]+)\s*{([^}]+)}', file_content)
        for match in media_matches:
            media_queries.append(match.group(1).strip())
        
        # Extract animations/keyframes
        animation_matches = re.finditer(r'@keyframes\s+([a-zA-Z0-9_-]+)\s*{([^}]+)}', file_content)
        for match in animation_matches:
            animations.append(match.group(1))
        
        # Create text representation for embedding
        text_parts = [
            f"CSS file {file_path}",
            f"Contains {len(classes)} classes: {', '.join(c.name for c in classes)}",
            f"Custom properties: {', '.join(custom_properties)}",
            f"Media queries: {', '.join(media_queries)}",
            f"Animations: {', '.join(animations)}"
        ]
        
        # Create metadata for LLM context
        metadata = CSSMetadata(
            file_type="css",
            file_path=file_path,
            classes=classes,
            custom_properties=custom_properties,
            media_queries=media_queries,
            animations=animations,
        )
        
        return CSSDetails(
            text=" ".join(text_parts),
            name=file_name,
            file_path=file_path,
            metadata=metadata.model_dump_json()
        )

    def parse_package_json(self, file_name: str, file_content: str, file_path: str) -> PackageDetails:
        """
        Parse package.json content to extract meaningful information for Pinecone.
        Returns both text for embedding and structured metadata for LLM context.
        """
        try:
            package_data = json.loads(file_content)
            
            # Extract key information
            name = package_data.get("name", "")
            version = package_data.get("version", "")
            description = package_data.get("description", "")
            
            # Process dependencies
            dependencies = package_data.get("dependencies", {})
            dev_dependencies = package_data.get("devDependencies", {})
            
            # Extract scripts
            scripts = package_data.get("scripts", {})
            
            # Create text representation for embedding
            text_parts = [
                f"Package {name} version {version}",
                f"Description: {description}",
                f"Main dependencies: {', '.join(dependencies.keys())}",
                f"Dev dependencies: {', '.join(dev_dependencies.keys())}",
                f"Available scripts: {', '.join(scripts.keys())}"
            ]
            
            # Create metadata for LLM context
            metadata = PackageMetadata(
                file_type="package.json",
                file_path=file_path,
                name=name,
                version=version,
                description=description,
                dependencies=dependencies,
                devDependencies=dev_dependencies,
                scripts=scripts,
                total_dependencies=len(dependencies),
                total_dev_dependencies=len(dev_dependencies),
                total_scripts=len(scripts)
            )
            
            return PackageDetails(
                text=" ".join(text_parts),
                name=file_name,
                file_path=file_path,
                metadata=metadata.model_dump_json()
            )
            
        except json.JSONDecodeError as e:
            print(f"Error parsing package.json: {str(e)}")
            metadata = PackageMetadata(
                file_type="package.json",
                file_path=file_path,
                name="",
                version="",
                description=f"Invalid package.json: {str(e)}",
                dependencies={},
                devDependencies={},
                scripts={},
                total_dependencies=0,
                total_dev_dependencies=0,
                total_scripts=0
            )
            return PackageDetails(
                text=f"Invalid package.json file at {file_path}",
                file_path=file_path,
                metadata=metadata.model_dump_json()
            )

    def extract_design_components(self) -> List[ProcessedFile]:
        try:
            allComponents = self.extract_components()

            # Process different file types
            processed_files: List[ProcessedFile] = []
            react_components = []
            
            for component in allComponents:
                file_name = component.file
                file_path = component.path
                file_content = component.fileContent
                
                if file_path.endswith('.css'):
                    css_details = self.parse_css_file(file_name, file_content, file_path)
                    processed_files.append(ProcessedFile(**css_details.model_dump()))
                elif file_path.endswith('package.json'):
                    package_details = self.parse_package_json(file_name, file_content, file_path)
                    processed_files.append(ProcessedFile(**package_details.model_dump()))
                elif (
                    file_path.endswith(('.tsx', '.jsx')) or  # React component files
                    'components' in file_path.lower() or     # Files in component directories
                    'ui' in file_path.lower()               # UI-related files
                ) and file_content.strip() != '':
                    react_components.append(component)

            # Process all React components at once
            if react_components:
                parsed_components = self.parse_components(react_components)
                for parsed in parsed_components:
                    processed_files.append(ProcessedFile(
                        text=f"{parsed.name} {parsed.description} {' '.join(parsed.useCases)}",
                        name=parsed.name,
                        file_path=parsed.path,
                        metadata=parsed.model_dump_json()
                    ))

            return processed_files

        except Exception as e:
            print("Error in extract_design_components:", str(e))
            raise

