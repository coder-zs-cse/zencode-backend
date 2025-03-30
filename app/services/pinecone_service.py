import os
import asyncio
import json
from typing import Dict, List, Optional, Any, Union
from pinecone import Pinecone
from .ingestion_service import FetchComponentsService, ProcessedFile
from .embedding_service import EmbeddingService
from app.lib.constants.model_config import DEFAULT_EMBEDDING_MODEL
from .database_service import database_service, ComponentFile, CSSFile, PackageFile, DesignConfigFile
from .database_service import Component, GithubRepo

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
        """
        Upsert vectors to Pinecone.
        Only stores file paths in Pinecone - full component data is stored in MongoDB.
        
        Args:
            records: List of records containing component data
            namespace: Namespace to upsert vectors to
            
        Returns:
            Result of upsert operation
        """
        result = None
        
        if self.embedding_service and all('text' in record for record in records):
            # Prepare minimal vector data with just filepath for Pinecone
            pinecone_records = []
            for record in records:
                pinecone_record = {
                    'id': record['id'],  # file path as ID
                    'text': record['text']  # text for embedding
                }
                pinecone_records.append(pinecone_record)
            
            vectors = self.embedding_service.prepare_vectors_for_upsert(pinecone_records)
            result = self.index.upsert(namespace=namespace or "", vectors=vectors)
            
        return result or {"upserted_count": 0}
    
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

        # Initialize the fetch service
        fetch_service = FetchComponentsService(github_url, access_token)
        
        # Extract all components first
        all_components = fetch_service.extract_components()
        
        # Filter components by type
        filtered_components = fetch_service.filter_components_by_type(all_components)
        
        # Save non-React components directly to MongoDB without parsing
        await self._save_non_react_components_to_db(filtered_components, namespace, github_url)
        
        # Process React components in batches
        react_components = filtered_components['react_components']
        total_react_components = len(react_components)
        total_processed = 0
        BATCH_SIZE = 10
        
        total_vectors_upserted = 0
        
        # Process React components in batches
        for i in range(0, total_react_components, BATCH_SIZE):
            batch = react_components[i:i+BATCH_SIZE]
            batch_size = len(batch)
            
            # Parse this batch of React components
            parsed_components = fetch_service.parse_components(batch)
            
            # Create Pinecone records (minimal info for vector search)
            pinecone_records = []
            # Create list to store MongoDB updates
            mongo_updates = []
            
            for parsed in parsed_components:
                # Prepare MongoDB update operation for this component
                filter_query = {
                    'userId': namespace,
                    'componentPath': parsed.path,
                    'githubUrl': github_url
                }
                
                update_operation = {
                    '$set': {
                        'indexingStatus': True,
                        'description': parsed.description,
                        'useCase': ' '.join(parsed.useCases) if parsed.useCases else '',
                        'codeSamples': parsed.codeExamples,
                        'dependencies': parsed.dependencies if hasattr(parsed, 'dependencies') else [],
                        'importPath': parsed.importPath if hasattr(parsed, 'importPath') else ''
                    }
                }
                
                # Add to batch updates
                mongo_updates.append({
                    'filter': filter_query,
                    'update': update_operation
                })
                
                # Create a minimal record for Pinecone
                pinecone_record = {
                    'id': parsed.path,  # file path as ID
                    'text': f"{parsed.name} {parsed.description} {' '.join(parsed.useCases)}",  # text for embedding
                    'user_id': namespace
                }
                pinecone_records.append(pinecone_record)
            
            # Batch update MongoDB components
            if namespace and mongo_updates:
                await database_service.update_many('components', mongo_updates)
            
            # Upsert vectors to Pinecone
            if namespace and pinecone_records:
                await self.upsert_vectors(pinecone_records, namespace)
                total_vectors_upserted += len(pinecone_records)
            
            # Update total processed count
            total_processed += batch_size
            
        # Return statistics about the operation
        return {
            'total_components': len(all_components),
            'total_react_components': total_react_components,
            'vectors_upserted': total_vectors_upserted,
            'namespace': namespace,
            'user_id': namespace
        }
        
    async def _save_non_react_components_to_db(
        self, 
        filtered_components: Dict[str, List], 
        user_id: Optional[str] = None,
        github_url: Optional[str] = None,
    ):
        """Save non-React components to MongoDB without parsing, updating the github collection."""
        if not user_id or not github_url:
            return
            
        # Prepare data for GitHub collection
        css_files_data = []
        package_json_data = []
        design_config_data = []
        react_component_paths = []
        
        # Collect CSS files data
        for component in filtered_components.get('css_files', []):
            css_files_data.append({
                'path': component.path,
                'content': component.fileContent
            })
            
        # Collect package.json files data
        for component in filtered_components.get('package_files', []):
            package_json_data.append({
                'path': component.path,
                'content': component.fileContent
            })
            
        # Collect design config files data
        for component in filtered_components.get('design_config_files', []):
            design_config_data.append({
                'path': component.path,
                'content': component.fileContent
            })
            
        # Collect React component paths
        for component in filtered_components.get('react_components', []):
            react_component_paths.append(component.path)
            
        # Create GitHub repo model
        github_repo = GithubRepo(
            githubUrl=github_url,
            userId=user_id,
            indexingStatus='IN_PROGRESS',
            componentList=react_component_paths,
            packageJson=json.dumps(package_json_data) if package_json_data else None,
            cssFiles=json.dumps(css_files_data) if css_files_data else None,
            designConfigFiles=json.dumps(design_config_data) if design_config_data else None
        )
        
        # Update or insert the GitHub repo document
        query = {
            'githubUrl': github_url,
            'userId': user_id
        }
        
        update = {
            '$set': github_repo.model_dump(exclude_none=True)
        }
        
        # Try to update existing document, if not exists create new one
        result = await database_service.update_one('github', query, update)
        # if not result:
        #     await database_service.insert_one('github', github_repo.model_dump(exclude_none=True))
            
        # Initialize components in the components table
        components_to_insert = []
         
        # Initialize React components
        for component in filtered_components.get('react_components', []):
            # Extract component name from path
            component = Component(
                userId=user_id,
                githubUrl=github_url,
                componentName=component.file,
                componentPath=component.path,
                indexingStatus=False  # Initialize as not indexed
            )
            components_to_insert.append(component.model_dump())
            
        # Insert all components
        if components_to_insert:
            await database_service.insert_many('components', components_to_insert)
    
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
                top_k=top_k,
                include_values=False,
                include_metadata=include_metadata
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
                'metadata': hit.get('metadata', {})  # Include all metadata, not just the text field
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