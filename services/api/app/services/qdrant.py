import logging

import os
from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models

from app.core.config import settings

logger = logging.getLogger(__name__)

class QdrantService:
    def __init__(self, host: str = "localhost", port: int = 6333):
        qdrant_url = settings.QDRANT_URL
        qdrant_api_key = settings.QDRANT_API_KEY
        
        if qdrant_url and qdrant_api_key:
            logger.info("Connecting to Qdrant Cloud")
            self.client = AsyncQdrantClient(url=qdrant_url, api_key=qdrant_api_key)
        else:
            logger.info("Connecting to local Qdrant")
            self.client = AsyncQdrantClient(host=host, port=port)

    async def ensure_collection(self, collection_name: str, vector_dim: int):
        """Creates a collection if it doesn't exist."""
        collections_response = await self.client.get_collections()
        collection_names = [c.name for c in collections_response.collections]
        
        if collection_name not in collection_names:
            logger.info(f"Creating Qdrant collection: {collection_name}")
            await self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=vector_dim, 
                    distance=models.Distance.COSINE
                )
            )
            # Create payload indices for fast filtering
            await self.client.create_payload_index(
                collection_name=collection_name,
                field_name="knowledge_base_id",
                field_schema=models.PayloadSchemaType.KEYWORD
            )
            await self.client.create_payload_index(
                collection_name=collection_name,
                field_name="document_id",
                field_schema=models.PayloadSchemaType.KEYWORD
            )

    async def upsert_chunks(self, collection_name: str, chunks: list[dict]):
        """
        Upserts document chunks into Qdrant.
        `chunks` should be a list of dicts:
        {
            "id": "uuid-string",
            "vector": [float, ...],
            "payload": {
                "knowledge_base_id": "...",
                "document_id": "...",
                "chunk_index": 0,
                "content": "..."
            }
        }
        """
        points = [
            models.PointStruct(
                id=chunk["id"],
                vector=chunk["vector"],
                payload=chunk["payload"]
            )
            for chunk in chunks
        ]
        
        await self.client.upsert(
            collection_name=collection_name,
            points=points
        )

    async def search(self, collection_name: str, query_vector: list[float], knowledge_base_id: str | None = None, limit: int = 5):
        """Searches for similar chunks."""
        query_filter = None
        if knowledge_base_id:
            query_filter = models.Filter(
                must=[
                    models.FieldCondition(
                        key="knowledge_base_id",
                        match=models.MatchValue(value=knowledge_base_id)
                    )
                ]
            )

        results = await self.client.query_points(
            collection_name=collection_name,
            query=query_vector,
            query_filter=query_filter,
            limit=limit,
            with_payload=True
        )
        return results.points

qdrant_service = QdrantService()
