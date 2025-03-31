import re
import json
from typing import TypeVar, Type, Optional
from pydantic import BaseModel
from app.models.builder_steps import ReactResponse, FileStep

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
    except Exception:
        return []

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