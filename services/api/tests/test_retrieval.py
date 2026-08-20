import uuid

import pytest

from app.services.embedding import EmbeddingEngine
from app.services.qdrant import QdrantService
from app.services.retrieval import RetrievalEngine


@pytest.fixture(scope="module")
def embedding_engine():
    return EmbeddingEngine.get_instance()

@pytest.fixture
def qdrant():
    return QdrantService(host="localhost", port=6333)

@pytest.mark.asyncio
async def test_retrieval(embedding_engine, qdrant):
    collection_name = "test_retrieval_collection"
    kb_id = f"kb-{uuid.uuid4()}"
    
    await qdrant.ensure_collection(collection_name, embedding_engine.vector_dim)
    
    engine = RetrievalEngine(embedding_engine, qdrant, collection_name=collection_name)
    
    # Let's ingest a chunk
    doc_text = "The mitochondria is the powerhouse of the cell."
    vector = embedding_engine.embed_text(doc_text)
    
    chunk_id = str(uuid.uuid4())
    await qdrant.upsert_chunks(collection_name, [{
        "id": chunk_id,
        "vector": vector,
        "payload": {
            "knowledge_base_id": kb_id,
            "document_id": "doc-1",
            "content": doc_text,
            "chunk_index": 0
        }
    }])
    
    # Retrieve
    results = await engine.retrieve("What is the powerhouse of the cell?", knowledge_base_id=kb_id, top_k=1)
    
    assert len(results) == 1
    assert results[0]["id"] == chunk_id
    assert "mitochondria" in results[0]["content"]
    assert results[0]["score"] > 0.5  # Cosine similarity should be high
