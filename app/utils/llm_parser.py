import re
import json
import httpx
from typing import TypeVar, Type, Optional, List, Dict, Any, Tuple
from pydantic import BaseModel
from app.models.builder_steps import ReactResponse, FileStep
from app.models.component import FileNode
from app.services.database_service import database_service

T = TypeVar('T', bound=BaseModel)

def extract_json_from_llm_response(text: str) -> Optional[dict]:
    """
    Extract a JSON object from an LLM response text.
    
    Args:
        text (str): The raw text response from an LLM
        
    Returns:
        Optional[dict]: Extracted JSON object or None if no valid JSON found
    """
    # Try to find JSON-like content within the text using regex
    json_match = re.search(r'\{[\s\S]*\}', text)
    if not json_match:
        return None
        
    try:
        # Parse the matched text as JSON
        json_str = json_match.group(0)
        return json.loads(json_str)
    except json.JSONDecodeError:
        return None

def parse_llm_response_to_model(text: str, model_class: Type[T]) -> Optional[T]:
    """
    Parse an LLM response text into a Pydantic model instance.
    
    Args:
        text (str): The raw text response from an LLM
        model_class (Type[T]): The Pydantic model class to parse into
        
    Returns:
        Optional[T]: Instance of the model_class or None if parsing fails
    """
    json_data = extract_json_from_llm_response(text)
    if not json_data:
        return None
        
    try:
        # Attempt to create an instance of the model class from the JSON data
        return model_class(**json_data)
    except Exception:
        return None

def parse_llm_response_to_model_list(text: str, model_class: Type[T], list_key: str = "components") -> list[T]:
    """
    Parse an LLM response text into a list of Pydantic model instances.
    
    Args:
        text (str): The raw text response from an LLM
        model_class (Type[T]): The Pydantic model class to parse into
        list_key (str): The key in the JSON object that contains the list of items
        
    Returns:
        list[T]: List of model_class instances. Returns empty list if parsing fails.
    """
    json_data = extract_json_from_llm_response(text)
    if not json_data:
        return []
        
    try:
        # Extract the list from the JSON using the list_key
        items = json_data.get(list_key, [])
        # Parse each item into a model instance
        return [model_class(**item) for item in items]
    except Exception as e:
        raise RuntimeError(f"Error during LLM parsing: {str(e)}")

def parse_llm_response_to_react_steps(text: str) -> ReactResponse:
    """
    Parse an LLM response text specifically into a ReactResponse model containing FileSteps.
    
    Args:
        text (str): The raw text response from an LLM that should contain a JSON with steps
        
    Returns:
        ReactResponse: ReactResponse instance with parsed steps. Returns empty steps list if parsing fails.
    """
    try:
        # First try to extract and parse the JSON
        json_data = extract_json_from_llm_response(text)
        if not json_data:
            return ReactResponse(steps=[])
            
        # If the JSON has a 'steps' key directly, use it
        if 'steps' in json_data:
            return ReactResponse(**json_data)
            
        # If the JSON itself is an array, treat it as the steps array
        if isinstance(json_data, list):
            return ReactResponse(steps=json_data)
            
        # If we got here, we couldn't find a valid steps structure
        return ReactResponse(steps=[])
        
    except Exception as e:
        print(f"Error parsing LLM response to ReactResponse: {str(e)}")
        return ReactResponse(steps=[])

def filter_internal_components(codebase: List[FileNode]) -> Tuple[List[str], List[FileNode], FileNode]:
    """Filter out internal component paths from codebase"""
    internal_components = []
    package_json_file = None
    for file in codebase:
        if '/ui/internal/' in file.filePath:
            internal_components.append(file.filePath)
        if file.fileName == 'package.json':
            package_json_file = file


    filtered_codebase = [file for file in codebase if file.filePath not in internal_components]
    return internal_components, filtered_codebase, package_json_file




async def process_react_steps_for_internal_components(
    react_response: ReactResponse,
    existing_internal_components: List[str],
    package_json_file: FileNode,
    userId: str
) -> list[FileStep]:
    """
    Process React steps to find and include missing internal components
    
    Args:
        react_response: The ReactResponse object with steps
        existing_internal_components: List of already existing internal component paths
        userId: User ID for database queries
        
    Returns:
        Updated ReactResponse with additional steps for internal components
    """
    import_steps: list[FileStep] = []
    missing_component_paths = []
    missing_dependencies = []

    if react_response and react_response.steps:
        for step in react_response.steps:
            if step.path == package_json_file.filePath:
                package_json_file.fileContent = step.content
            if step.content:
                # Parse component code to extract dependencies
                parsed_data = await database_service.parse_component_code(step.content)
                
                if parsed_data and "dependencies" in parsed_data:
                    # Find missing internal components
                    for dep in parsed_data["dependencies"]:
                        if '/ui/internal/' in dep and dep not in existing_internal_components:
                            # Extract the component name after 'internal/' and construct the full path
                            component_name = dep.split('/ui/internal/')[-1]
                            full_path = f"src/components/ui/internal/{component_name}.tsx"
                            missing_component_paths.append(full_path)
                        # else:
                        #     missing_dependencies.append(dep)
    
    # Only make a database call if there are missing components
    if missing_component_paths:
        # Fetch all missing components in a single database call
        missing_components = await database_service.get_missing_internal_components(
            missing_component_paths,
            userId
        )
        
        # Add import steps for missing components
        for comp in missing_components:
            # for dep in comp.dependencies:
            #     if dep not in missing_dependencies:
            #         missing_dependencies.append(dep)

            import_step = FileStep(
                id=len(react_response.steps) + len(import_steps) + 1,
                title=f"Importing Internal Component {comp.fileName}",
                type=0,
                content=comp.fileContent,
                path=comp.filePath
            )
            import_steps.append(import_step)
    
    # Add the import steps to the original steps
    return import_steps 


def transform_absolute_path(path: str) -> str:
    """
    Transform an absolute path to a relative path
    """
    if path.startswith('src/'):
        path = path.replace('src/', '@/', 1)
    return path
