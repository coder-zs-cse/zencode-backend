import os
import sys
from pathlib import Path

# Add the parent directory to sys.path to import from app
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.services.ingestion_service import FetchComponentsService
from dotenv import load_dotenv

def test_extract_design_components():
    # Initialize the service with the GitHub repository URL
    repo_url = "https://github.com/coder-zs-cse/shabble"
    
    # Load environment variables
    load_dotenv()
    
    # Get OpenAI API key from environment variable
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    if not openai_api_key:
        print("Error: OPENAI_API_KEY environment variable is not set")
        return
    
    try:
        # Create service instance
        service = FetchComponentsService(
            repo_link=repo_url,
        )
        
        # Extract design components
        results = service.extract_design_components()
        
        # Print results
        print("\n=== Design Components Extraction Results ===\n")
        
        for idx, result in enumerate(results, 1):
            print(f"\nResult {idx}:")
            print("Text:", result['text'])
            print("Metadata:", result['metadata'])
            print("-" * 80)
            
        print(f"\nTotal components processed: {len(results)}")
        
    except Exception as e:
        print(f"Error during test: {str(e)}")

if __name__ == "__main__":
    test_extract_design_components() 