from app.services.embedding import EmbeddingEngine
from app.services.qdrant import QdrantService, qdrant_service


class RetrievalEngine:
    def __init__(self, qdrant: QdrantService, collection_name: str = "documents"):
        self.qdrant = qdrant
        self.collection_name = collection_name
        self._embedding = None

    @property
    def embedding(self):
        if self._embedding is None:
            self._embedding = EmbeddingEngine.get_instance()
        return self._embedding

    async def retrieve(self, query: str, knowledge_base_id: str | None = None, top_k: int = 5) -> list[dict]:
        """
        Retrieves top_k relevant chunks for a given query.
        (Currently dense vector search. Can be extended to hybrid BM25).
        """
        # Embed query
        query_vector = self.embedding.embed_text(query)
        
        # Search Qdrant
        results = await self.qdrant.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            knowledge_base_id=knowledge_base_id,
            limit=top_k
        )
        
        # Format results
        formatted_results = []
        for point in results:
            formatted_results.append({
                "id": point.id,
                "score": point.score,
                "content": point.payload.get("content", ""),
                "document_id": point.payload.get("document_id", ""),
                "knowledge_base_id": point.payload.get("knowledge_base_id", ""),
                "chunk_index": point.payload.get("chunk_index", 0)
            })
            
        return formatted_results

retrieval_engine = RetrievalEngine(qdrant_service)
