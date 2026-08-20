from sentence_transformers import CrossEncoder
import torch
import logging

logger = logging.getLogger(__name__)

class RerankingEngine:
    """Service to rerank retrieved documents using a cross-encoder."""

    _instance = None

    def __init__(self, model_name: str = "BAAI/bge-reranker-base"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Loading reranking model {model_name} on {self.device}")
        
        # CrossEncoder predicts a score between 0 and 1 (or logits) for (query, document) pairs
        self.model = CrossEncoder(model_name, device=self.device)

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def rerank(self, query: str, chunks: list[dict], top_k: int = 5) -> list[dict]:
        """
        Reranks a list of chunks based on a query.
        chunks must be a list of dictionaries, each containing a 'content' key.
        """
        if not chunks:
            return []

        # Create pairs of (query, chunk_content)
        pairs = [[query, chunk["content"]] for chunk in chunks]
        
        # Predict scores
        scores = self.model.predict(pairs)
        
        # Combine chunks with new scores
        reranked = []
        for i, chunk in enumerate(chunks):
            new_chunk = chunk.copy()
            new_chunk["rerank_score"] = float(scores[i])
            reranked.append(new_chunk)
            
        # Sort by rerank score descending
        reranked.sort(key=lambda x: x["rerank_score"], reverse=True)
        
        return reranked[:top_k]
