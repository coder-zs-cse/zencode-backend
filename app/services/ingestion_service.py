from typing import Optional, List, Any, Dict, TypedDict
import re
import requests
import json
import base64
import json
from pydantic import BaseModel
from app.services.openai_service import OpenAIService, ChatMessage
from app.core.config import get_settings
from app.lib.constants.model_config import SYSTEM_PROMPTS
from app.utils.llm_parser import parse_llm_response_to_model_list


class FetchedComponent(BaseModel):
    file: str
    fileContent: str
    path: str

class LLMComponent(BaseModel):
    description: str
    inputProps: List[Dict[str, Any]]
    useCases: List[str]
    codeExamples: List[str]

class Component(BaseModel):
    name: str
    path: str
    code: str
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
            raise RuntimeError(f"Error during parsing components: {str(e)}")
            
    def _process_component_batch(self, batch: List[FetchedComponent]) -> List[Component]:
        """Process a batch of components using OpenAI LLM."""
        try:
            result_components: list[Component] = []
            # Combine all component files with their paths for this batch
            combined_content = "\n\n".join([
                f"File: {comp.path}\n{comp.fileContent}" 
                for comp in batch
            ])

            # Prepare messages for the LLM with a more direct prompt
            messages = [
                ChatMessage(role="system", content=SYSTEM_PROMPTS["COMPONENT_SYSTEM_PROMPT"]),
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

            # Parse the response into Component objects using our utility function
            parsed_components = parse_llm_response_to_model_list(
                text=response.get("text", ""),
                model_class=LLMComponent,
                list_key="components"
            )

            # Update components with original file information
            min_length = min(len(parsed_components), len(batch))
            for i in range(min_length):

                component_data = parsed_components[i].model_dump()

                component_data["name"] = batch[i].file
                component_data["path"] = batch[i].path  
                component_data["code"] = batch[i].fileContent

                result_components.append(Component(**component_data))

            return result_components
            
        except Exception as e:
            print(f"Error in _process_component_batch: {str(e)}")
            raise RuntimeError(f"Error during component batch processing: {str(e)}")

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
                        path=self._modify_path_with_internal(item['path'])
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

    def filter_components_by_type(self, all_components: List[FetchedComponent]) -> Dict[str, List[FetchedComponent]]:
        """
        Filter components by file type and location.
        
        Returns:
            Dictionary with categorized components:
            - 'react_components': TSX/JSX files in components/ui directories
            - 'css_files': CSS files
            - 'design_config_files': Design configuration files like tailwind.config.js
            - 'package_files': package.json files
            - 'other_files': All other files
        """
        filtered_components = {
            'react_components': [],
            'css_files': [],
            'design_config_files': [],
            'package_files': [],
            'other_files': []
        }
        
        design_config_patterns = ['tailwind.config.js', 'theme.config.js', 'styles.config.js', 'tailwind.config.ts', 'theme.config.ts', 'styles.config.ts'  ]
        
        for component in all_components:
            file_path = component.path
            file_content = component.fileContent
            
            # Skip empty files
            if file_content.strip() == '':
                continue
                
            # Check for React components in UI/components directories
            if file_path.endswith(('.tsx', '.jsx')) and ('components' in file_path.lower() or 'ui' in file_path.lower()):
                filtered_components['react_components'].append(component)
            
            # CSS files
            elif file_path.endswith('.css'):
                filtered_components['css_files'].append(component)
            
            # Design configuration files
            elif any(file_path.endswith(pattern) for pattern in design_config_patterns):
                filtered_components['design_config_files'].append(component)
            
            # Package.json files
            elif file_path.endswith('package.json'):
                filtered_components['package_files'].append(component)
            
            # All other files
            else:
                filtered_components['other_files'].append(component)
                
        return filtered_components
        
    # def process_filtered_components(self, filtered_components: Dict[str, List[FetchedComponent]]) -> List[ProcessedFile]:
        """
        Process components based on their category.
        
        Args:
            filtered_components: Dictionary with categorized components
            
        Returns:
            List of processed files ready for vectorization
        """
        processed_files = []
        
        # Process CSS files
        for component in filtered_components['css_files']:
            css_details = self.parse_css_file(component.file, component.fileContent, component.path)
            processed_files.append(ProcessedFile(**css_details.model_dump()))
        
        # Process package.json files
        for component in filtered_components['package_files']:
            package_details = self.parse_package_json(component.file, component.fileContent, component.path)
            processed_files.append(ProcessedFile(**package_details.model_dump()))
        
        # Process React components
        if filtered_components['react_components']:
            parsed_components = self.parse_components(filtered_components['react_components'])
            for parsed in parsed_components:
                processed_files.append(ProcessedFile(
                    text=f"{parsed.name} {parsed.description} {' '.join(parsed.useCases)}",
                    name=parsed.name,
                    file_path=parsed.path,
                    metadata=parsed.model_dump_json()
                ))
                
        # Process design configuration files
        for component in filtered_components['design_config_files']:
            design_config = self.parse_design_config(component.file, component.fileContent, component.path)
            processed_files.append(ProcessedFile(**design_config.model_dump()))
        
        return processed_files
        
    # def parse_design_config(self, file_name: str, file_content: str, file_path: str) -> ProcessedFile:
    #     """
    #     Parse design configuration files like tailwind.config.js.
        
    #     Args:
    #         file_name: Name of the file
    #         file_content: Content of the file
    #         file_path: Path to the file
            
    #     Returns:
    #         ProcessedFile with text for embedding and metadata for context
    #     """
    #     # Create type-specific metadata based on file name
    #     if file_name == 'tailwind.config.js':
    #         return self._parse_tailwind_config(file_name, file_content, file_path)
    #     else:
    #         # Generic design config handling
    #         metadata = {
    #             "file_type": "design_config",
    #             "file_path": file_path,
    #             "file_name": file_name,
    #             "content_preview": file_content[:200] + "..." if len(file_content) > 200 else file_content
    #         }
            
    #         text = f"Design configuration file: {file_path}\nContent: {file_content[:500]}"
            
    #         return ProcessedFile(
    #             text=text,
    #             name=file_name,
    #             file_path=file_path,
    #             metadata=json.dumps(metadata)
    #         )
            
    # def _parse_tailwind_config(self, file_name: str, file_content: str, file_path: str) -> ProcessedFile:
    #     """
    #     Parse Tailwind CSS configuration file.
        
    #     Args:
    #         file_name: Name of the file
    #         file_content: Content of the file
    #         file_path: Path to the file
            
    #     Returns:
    #         ProcessedFile with Tailwind-specific text and metadata
    #     """
    #     # Extract key Tailwind config sections using regex
    #     theme_match = re.search(r'theme\s*:\s*{([^}]+)}', file_content, re.DOTALL)
    #     plugins_match = re.search(r'plugins\s*:\s*\[([^\]]+)\]', file_content, re.DOTALL)
    #     extends_match = re.search(r'extends\s*:\s*{([^}]+)}', file_content, re.DOTALL)
        
    #     theme = theme_match.group(1).strip() if theme_match else ""
    #     plugins = plugins_match.group(1).strip() if plugins_match else ""
    #     extends = extends_match.group(1).strip() if extends_match else ""
        
    #     # Extract color palette if available
    #     colors = {}
    #     color_matches = re.finditer(r'colors\s*:\s*{([^}]+)}', file_content, re.DOTALL)
    #     for match in color_matches:
    #         color_section = match.group(1)
    #         color_entries = re.finditer(r'(\w+)\s*:\s*[\'"]([^\'\"]+)[\'"]', color_section)
    #         for entry in color_entries:
    #             colors[entry.group(1)] = entry.group(2)
        
    #     # Create metadata
    #     metadata = {
    #         "file_type": "tailwind_config",
    #         "file_path": file_path,
    #         "has_theme": bool(theme),
    #         "has_plugins": bool(plugins),
    #         "has_extends": bool(extends),
    #         "colors": colors
    #     }
        
    #     # Create text representation for embedding
    #     text_parts = [
    #         f"Tailwind configuration file: {file_path}",
    #         f"Theme configuration: {theme[:200] + '...' if len(theme) > 200 else theme}",
    #         f"Plugins: {plugins[:200] + '...' if len(plugins) > 200 else plugins}",
    #         f"Extensions: {extends[:200] + '...' if len(extends) > 200 else extends}",
    #         f"Color palette: {', '.join(f'{k}: {v}' for k, v in colors.items())}"
    #     ]
        
    #     return ProcessedFile(
    #         text="\n".join(text_parts),
    #         name=file_name,
    #         file_path=file_path,
    #         metadata=json.dumps(metadata)
    #     )

    # def extract_design_components(self) -> List[ProcessedFile]:
        try:
            # Extract all components from the repository
            all_components = self.extract_components()
            
            # Filter components by type
            filtered_components = self.filter_components_by_type(all_components)
            
            # Process each type of component
            processed_files = self.process_filtered_components(filtered_components)
            
            return processed_files

        except Exception as e:
            print("Error in extract_design_components:", str(e))
            raise

    def _modify_path_with_internal(self, path: str) -> str:
        """Add 'internal' directory after 'ui' in the path if 'ui' exists."""
        parts = path.split('/')
        for i, part in enumerate(parts):
            if part.lower() == 'ui':
                # Insert 'internal' after 'ui'
                parts.insert(i + 1, 'internal')
                break
        return '/'.join(parts)
    
