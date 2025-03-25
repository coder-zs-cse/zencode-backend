from openai import OpenAI
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class EmbeddingService:
    def __init__(self, api_key: str, model: str = "text-embedding-3-large"):
        """
        Initialize the embedding service with the OpenAI API key and model.
        
        Args:
            api_key: OpenAI API key
            model: Embedding model to use, defaults to text-embedding-3-large
        """
        self.api_key = api_key
        self.model = model
        self.client = OpenAI(api_key=self.api_key)
        
        # Dimensions mapping for different models
        self.dimensions = {
            "text-embedding-3-large": 3072,
            "text-embedding-3-small": 1536,
            "text-embedding-ada-002": 1536
        }
    
    def get_dimension(self) -> int:
        """
        Get the embedding dimension for the current model.
        
        Returns:
            int: The dimension of the embedding vectors
        """
        return self.dimensions.get(self.model, 3072)  # Default to 3072 if model not found
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of text strings.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        response = self.client.embeddings.create(
            input=texts,
            model=self.model
        )
        
        # Extract embeddings from response
        embeddings = [data.embedding for data in response.data]
        return embeddings
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text string.
        
        Args:
            text: Text string to embed
            
        Returns:
            Embedding vector
        """
        embeddings = self.embed_texts([text])
        return embeddings[0]
    
    def prepare_vectors_for_upsert(
        self, 
        data: List[Dict[str, Any]], 
        text_field: str = "text"
    ) -> List[Dict[str, Any]]:
        """
        Prepare data for upserting to Pinecone by adding embeddings.
        
        Args:
            data: List of data dictionaries, each must have 'id' and a text field
            text_field: Name of the field containing text to embed
            
        Returns:
            List of vectors ready for Pinecone upsert
        """
        # Extract texts for embedding
        texts = [item[text_field] for item in data]
        
        # Generate embeddings
        embeddings = self.embed_texts(texts)
        
        # Prepare vectors for Pinecone
        vectors = []
        for item, embedding in zip(data, embeddings):
            vector = {
                "id": item["id"],
                "values": embedding,
                "metadata": {k: v for k, v in item.items() if k != "id"}
            }
            vectors.append(vector)
            
        return vectors 