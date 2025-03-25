import asyncio
import os
import sys
from typing import List, Dict, Any
import json
from fastapi import APIRouter, Depends, HTTPException, status, Header


# Add the parent directory to sys.path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.services.pinecone_service import PineconeService
from app.services.database_service import database_service
from app.core.config import get_settings, Settings

async def test_save_records_to_database():
    """
    Test the _save_records_to_database function by inserting dummy documents.
    This demonstrates how records are processed and saved to MongoDB.
    """
    print("Starting test of _save_records_to_database...")
    
    # Create dummy records in the format that pinecone_service.py would generate
    dummy_records = [
        {
            'id': 'component_1',
            'text': 'This is a test component with some React code.',
            'metadata': json.dumps({
                'file_name': 'TestComponent.jsx',
                'file_path': 'src/components/TestComponent.jsx',
                'component_type': 'react',
                'tags': ['ui', 'button', 'form']
            }),
            'user_id': 'test_user'
        },
        {
            'id': 'component_2',
            'text': 'Another component with CSS styling and HTML structure.',
            'metadata': json.dumps({
                'file_name': 'Card.tsx',
                'file_path': 'src/components/Card.tsx',
                'component_type': 'react',
                'tags': ['ui', 'card', 'container']
            }),
            'user_id': 'test_user'
        }
    ]

    # Initialize PineconeService with minimal parameters
    # We won't actually connect to Pinecone in this test
    try:
        settings = get_settings()
        pinecone_service=  PineconeService(
                        api_key=settings.PINECONE_API_KEY,
                        environment=settings.PINECONE_ENVIRONMENT,
                        index_name=settings.PINECONE_INDEX,
                        openai_api_key=settings.OPENAI_API_KEY,
                        dimension=3072,  # Set to match your llama-text-embed-v2 model
                    )
        
        print("PineconeService initialized")
        
        # Test connection to the database backend
        connected = await database_service.connect()
        if not connected:
            print("Failed to connect to database backend. Make sure the Node.js server is running.")
            return
            
        print("Connected to database backend")
        
        # Call the _save_records_to_database method directly
        print("Saving records to database...")
        await pinecone_service._save_records_to_database(dummy_records, "test_user")
        print("Records saved to database")
        
        # Verify the records were saved to MongoDB
        # Fetch the saved documents to verify they were inserted correctly
        print("Fetching saved components...")
        saved_components = await database_service.find_many(
            "components", 
            {"user_id": "test_user"}
        )
        
        print(f"Saved {len(saved_components)} components to database")
        print("\nSaved components:")
        for component in saved_components:
            print(f"ID: {component.get('component_id')}")
            print(f"Text: {component.get('text')[:50]}...")
            print(f"User ID: {component.get('user_id')}")
            print(f"Metadata: {json.dumps(component.get('metadata'), indent=2)}")
            print("-" * 50)

        # Optional: Clean up test data
        # print("Cleaning up test data...")
        # try:
        #     # Try to use delete_many if it exists
        #     await database_service.delete_many("components", {"user_id": "test_user"})
        # except AttributeError:
        #     # Fallback to delete_one if delete_many doesn't exist
        #     print("delete_many not available, using delete_one instead")
        #     components = await database_service.find_many("components", {"user_id": "test_user"})
        #     deleted_count = 0
        #     for component in components:
        #         if "_id" in component:
        #             success = await database_service.delete_one("components", {"_id": component["_id"]})
        #             if success:
        #                 deleted_count += 1
        #     print(f"Deleted {deleted_count} components with delete_one")
        # print("Test data cleaned up from database")
        
    except Exception as e:
        print(f"Error during test: {e}")
    finally:
        # Close the database connection
        await database_service.close()
        print("Database connection closed")

if __name__ == "__main__":
    asyncio.run(test_save_records_to_database()) 