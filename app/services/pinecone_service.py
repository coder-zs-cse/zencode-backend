import os
from typing import Dict, List, Optional, Any, Union
from pinecone import Pinecone
from .ingestion_service import FetchComponentsService
from ..lib.constants.testing.internal_components import components as internalComponents

class PineconeService:
    def __init__(
        self, 
        api_key: str,
        environment: str,
        index_name: str,
        dimension: int = 1024  # Changed to match llama-text-embed-v2
    ):
        self.api_key = api_key
        self.environment = environment
        self.index_name = index_name
        self.dimension = dimension
        
        self.pc = Pinecone(api_key=self.api_key)
        
        try:
            self.index = self.pc.Index(self.index_name)
        except Exception:
            self.pc.create_index_from_model(
                name=self.index_name,
                embed={
                    "model": "llama-text-embed-v2",
                    "field_map": {
                        "text": "text"  # Field to embed
                    }
                },
                dimension=self.dimension,
                metric="cosine"
            )
            self.index = self.pc.Index(self.index_name)
    
    def upsert_vectors(self, records: List[Dict[str, Any]], namespace: Optional[str] = None) -> Dict[str, Any]:
        return self.index.upsert_records(namespace or "", records)
    
    def train_github_url(
        self, 
        github_url: str, 
        access_token: Optional[str] = None,
        namespace: Optional[str] = None
    ) -> Dict[str, Any]:
        # For testing purposes, using a constant list of components
        # components = internalComponents

        # Comment out the actual extraction for testing
        fetch_service = FetchComponentsService(github_url, access_token)
        components = fetch_service.extract_design_components()

        records = []
        for component in components:
            file_name = component.file
            file_path = component.path
            file_content = component.fileContent
            
            record = {
                'id': file_path,  
                'text': file_content,  
                'file_name': file_name,
                'file_path': file_path,
                'source': github_url
            }
            
            records.append(record)
        
        result = self.index.upsert_records(namespace or "", records)
        
        return {
            'total_components': len(components),
            'vectors_upserted': len(records),
            'namespace': namespace
        }
    
    def query(
        self,
        query_text: str,
        top_k: int = 5,
        namespace: Optional[str] = None,
        filter: Optional[Dict[str, Any]] = None,
        include_metadata: bool = True
    ) -> Dict[str, Any]:
        
        # if filter:
        #     query_params["query"]["filter"] = filter
        
        # Execute query
        results = self.index.search_records(
            namespace=namespace,
            query={
                "inputs": {
                    "text": query_text
                },
                "top_k": top_k,
                "filter" : filter or {}
            }
        )

        formatted_results = {
            'matches': []
        }
        
        hits = results.get('result', {}).get('hits', [])

        for hit in hits:
            match = {
                'id': hit.get('_id'),
                'score': hit.get('_score'),
                'metadata': {
                    'file_name': hit.get('fields', {}).get('file_name'),
                    'file_path': hit.get('fields', {}).get('file_path'),
                    'source': hit.get('fields', {}).get('source'),
                    'text': hit.get('fields', {}).get('text'),
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