import os
import asyncio
from typing import Dict, List, Optional, Any, Union
from pinecone import Pinecone
from .ingestion_service import FetchComponentsService, ProcessedFile
from .embedding_service import EmbeddingService
from app.lib.constants.model_config import DEFAULT_EMBEDDING_MODEL
from .database_service import database_service

class PineconeService:
    def __init__(
        self, 
        api_key: str,
        environment: str,
        index_name: str,
        openai_api_key: Optional[str] = None,
        embedding_model: str = DEFAULT_EMBEDDING_MODEL,
        dimension: Optional[int] = None
    ):
        self.api_key = api_key
        self.environment = environment
        self.index_name = index_name
        
        # Initialize embedding service if OpenAI API key is provided
        self.embedding_service = None
        if openai_api_key:
            self.embedding_service = EmbeddingService(api_key=openai_api_key, model=embedding_model)
            # Get dimension from embedding model if not specified
            if dimension is None:
                dimension = self.embedding_service.get_dimension()
        
        # Default dimension if not specified and no embedding service
        self.dimension = dimension or 1536
        
        self.pc = Pinecone(api_key=self.api_key)
        
        try:
            self.index = self.pc.Index(self.index_name)
        except Exception:
            self.pc.create_index_from_model(
                name=self.index_name,
                embed={
                    "model": embedding_model,
                    "field_map": {
                        "text": "text"  # Field to embed
                    }
                },
                dimension=self.dimension,
                metric="cosine"
            )
            self.index = self.pc.Index(self.index_name)
    
    async def upsert_vectors(self, records: List[Dict[str, Any]], namespace: Optional[str] = None) -> Dict[str, Any]:

        if self.embedding_service and all('values' not in record for record in records) and all('text' in record for record in records):
            data_to_embed = []
            for i, record in enumerate(records):
                if 'id' not in record:
                    record['id'] = f"record_{i}"
                data_to_embed.append(record)
            
            vectors = self.embedding_service.prepare_vectors_for_upsert(data_to_embed)
            result = self.index.upsert(namespace= namespace or "", vectors = vectors)
            
        return result
    
    async def _save_records_to_database(self, records: List[Dict[str, Any]], user_id: Optional[str] = None):
        """Save the records to MongoDB via the Node.js backend."""
        if not user_id:
            return
            
        # Prepare data for MongoDB
        components_data = []
        for record in records:
            component_data = {
                "name": record.get("name"),
                "path": record.get("id"),
                "text": record.get("text", ""),
                "metadata": record.get("metadata", {}),
                "user_id": user_id
            }
            components_data.append(component_data)
            
        # Save to 'components' collection
        if components_data:
            await database_service.insert_many(
                "components",
                components_data
            )
    
    async def train_github_url(
        self, 
        github_url: str, 
        access_token: Optional[str] = None,
        namespace: Optional[str] = None
    ) -> Dict[str, Any]:

        fetch_service = FetchComponentsService(github_url, access_token)
        components: List[ProcessedFile] = fetch_service.extract_design_components()

        records = []
        for component in components:
            record = {
                'id': component.file_path,  
                'name': component.name,
                'text': component.text,   
                'metadata': component.metadata, 
                'user_id': namespace 
            }
            records.append(record)
        
        if namespace:
            await self.upsert_vectors(records, namespace)
            await self._save_records_to_database(records, namespace)


        return {
            'total_components': len(components),
            'vectors_upserted': len(records),
            'namespace': namespace,
            'user_id': namespace
        }
    
    def query(
        self,
        query_text: str,
        top_k: int = 5,
        namespace: Optional[str] = None,
        filter: Optional[Dict[str, Any]] = None,
        include_metadata: bool = True
    ) -> Dict[str, Any]:
        # Generate embedding for query if embedding service is available
        query_vector = None
        if self.embedding_service:
            query_vector = self.embedding_service.embed_text(query_text)
            
            # Execute vector query
            results = self.index.query(
                namespace=namespace,
                vector=query_vector,
                top_k=3,
                include_values=False,
                include_metadata=include_metadata or True
            )
        else:
            # Use text-based query if no embedding service
            results = self.index.search_records(
                namespace=namespace,
                query={
                    "inputs": {
                        "text": query_text
                    },
                    "top_k": top_k,
                    "filter": filter or {}
                }
            )

        formatted_results = {
            'matches': []
        }
        
        hits = results.get('matches', [])

        for hit in hits:
            match = {
                'id': hit.get('id'),  # Adjusted to match typical Pinecone response
                'score': hit.get('score'),  # Adjusted to match typical Pinecone response
                'metadata': {
                    # 'file_name': hit.get('metadata', {}).get('file_name'),  # Adjusted to match typical Pinecone response
                    # 'file_path': hit.get('metadata', {}).get('file_path'),  # Adjusted to match typical Pinecone response
                    # 'source': hit.get('metadata', {}).get('source'),  # Adjusted to match typical Pinecone response
                    'text': hit.get('metadata', {}).get('text'),  # Adjusted to match typical Pinecone response
                }
            }
            formatted_results['matches'].append(match)
        
        return formatted_results
    
    def delete_vectors(
        self,
        ids: Optional[List[str]] = None,
        delete_all: bool = False,
        namespace: Optional[str] = None,
        filter: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:

        if delete_all:
            return self.index.delete_all(namespace=namespace or "")
        elif ids:
            return self.index.delete(ids=ids, namespace=namespace or "")
        elif filter:
            return self.index.delete(filter=filter, namespace=namespace or "")
        else:
            raise ValueError("Must provide either ids, delete_all=True, or a filter") 