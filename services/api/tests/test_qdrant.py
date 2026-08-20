import uuid

import pytest

from app.services.qdrant import QdrantService


# Test against local Docker Qdrant
@pytest.fixture
def qdrant():
    return QdrantService(host="localhost", port=6333)

@pytest.mark.asyncio
async def test_qdrant_flow(qdrant):
    collection_name = "test_collection"
    vector_dim = 3
    
    # Ensure collection
    await qdrant.ensure_collection(collection_name, vector_dim)
    
    kb_id = f"kb-{uuid.uuid4()}"
    
    # Upsert chunk
    chunk_id = str(uuid.uuid4())
    chunks = [{
        "id": chunk_id,
        "vector": [0.1, 0.2, 0.3],
        "payload": {
            "knowledge_base_id": kb_id,
            "document_id": "doc-1",
            "content": "Test content"
        }
    }]
    
    await qdrant.upsert_chunks(collection_name, chunks)
    
    # Search
    results = await qdrant.search(
        collection_name=collection_name, 
        query_vector=[0.1, 0.2, 0.3],
        knowledge_base_id=kb_id,
        limit=1
    )
    
    assert len(results) == 1
    assert results[0].id == chunk_id
    assert results[0].payload["content"] == "Test content"
    
    # Cleanup: We can't easily drop collection here without client exposed or we just leave it for tests
    await qdrant.client.delete_collection(collection_name)
