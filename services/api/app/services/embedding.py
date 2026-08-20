import logging

logger = logging.getLogger(__name__)

class EmbeddingEngine:
    """Service to generate dense vector embeddings from text chunks."""
    
    _instance = None

    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        import torch
        from sentence_transformers import SentenceTransformer
        # Detect device to optimize for GPU if available, respecting the user's RTX3050.
        # bge-small is very lightweight (~130MB) so it easily fits in 6GB VRAM.
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Loading embedding model {model_name} on {self.device}")
        
        self.model = SentenceTransformer(model_name, device=self.device)
        self.vector_dim = self.model.get_embedding_dimension()

    @classmethod
    def get_instance(cls):
        """Singleton pattern so we don't load the model into memory multiple times."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def embed_text(self, text: str) -> list[float]:
        """Generate embedding for a single string. Returns a list of floats."""
        # For BGE models, query prefixes are sometimes needed. We assume standard document embedding here.
        embedding = self.model.encode(text, normalize_embeddings=True)
        return embedding.tolist()

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a batch of strings."""
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()
