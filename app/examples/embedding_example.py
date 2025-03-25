import os
import sys
import json
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables from .env file
load_dotenv()

from services.embedding_service import EmbeddingService
from services.pinecone_service import PineconeService

def main():
    # Get API keys from environment variables
    openai_api_key = os.getenv("OPENAI_API_KEY")
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    
    if not openai_api_key or not pinecone_api_key:
        print("Error: Missing required API keys. Please set OPENAI_API_KEY and PINECONE_API_KEY environment variables.")
        return

    # Initialize embedding service
    embedding_service = EmbeddingService(api_key=openai_api_key, model="text-embedding-3-large")
    
    # Initialize Pinecone service with embedding service
    pinecone_service = PineconeService(
        api_key=pinecone_api_key,
        environment="us-east-1", # or your Pinecone environment
        index_name="v2-internal-library",
        openai_api_key=openai_api_key,
        embedding_model="text-embedding-3-large"
    )
    
    # Sample data to embed and upsert
    data = [
        {"id": "vec1", "text": "Apple is a popular fruit known for its sweetness and crisp texture."},
        {"id": "vec2", "text": "The tech company Apple is known for its innovative products like the iPhone."},
        {"id": "vec3", "text": "Many people enjoy eating apples as a healthy snack."},
        {"id": "vec4", "text": "Apple Inc. has revolutionized the tech industry with its sleek designs and user-friendly interfaces."},
        {"id": "vec5", "text": "An apple a day keeps the doctor away, as the saying goes."},
    ]
    
    # print("Embedding and upserting data to Pinecone...")
    
    # Method 1: Using embedding service directly
    # vectors = embedding_service.prepare_vectors_for_upsert(data)
    # result = pinecone_service.index.upsert_records("example_namespace", vectors)
    
    # Method 2: Using the enhanced PineconeService
    # result = pinecone_service.upsert_vectors(data, namespace="example_namespace")
    
    # print(f"Upsert result: {result}\n")
    
    # Now let's query the vectors
    query = "Tell me about the tech company known as Apple"
    print(f"Querying: '{query}'")
    
    # Execute the query using the PineconeService
    results = pinecone_service.query(
        query_text=query,
        top_k=3,
        namespace="example_namespace"
    )
    
    # Print results
    print("\nQuery Results:")
    for i, match in enumerate(results["matches"]):
        print(f"\nMatch {i+1} (Score: {match['score']:.4f}):")
        print(f"ID: {match['id']}")
        print(f"Text: {match['metadata']['text']}")

if __name__ == "__main__":
    main() 