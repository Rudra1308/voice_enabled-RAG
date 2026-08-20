import pytest
from unittest.mock import patch

@pytest.fixture(scope="module")
def reranker():
    with patch('app.services.reranker.CrossEncoder') as MockCrossEncoder:
        # Mock the predict method
        mock_instance = MockCrossEncoder.return_value
        # For our test, return specific scores:
        # Index 0 (mitochondria) -> 0.1
        # Index 1 (Paris) -> 0.9
        # Index 2 (France) -> 0.8
        mock_instance.predict.return_value = [0.1, 0.9, 0.8]
        
        from app.services.reranker import RerankingEngine
        # Reset instance
        RerankingEngine._instance = None
        engine = RerankingEngine.get_instance()
        return engine

def test_reranker(reranker):
    query = "What is the capital of France?"
    chunks = [
        {"id": 1, "content": "The mitochondria is the powerhouse of the cell."},
        {"id": 2, "content": "Paris is the capital and most populous city of France."},
        {"id": 3, "content": "France is a country in Western Europe. Its capital is Paris."}
    ]
    
    # We pass 3 chunks, and want top 2
    results = reranker.rerank(query, chunks, top_k=2)
    
    assert len(results) == 2
    
    # The first result should definitely be id 2 or 3 (about Paris) and NOT id 1
    assert results[0]["id"] in [2, 3]
    assert results[1]["id"] in [2, 3]
    assert "rerank_score" in results[0]
    
    # Assert id 1 is nowhere in the top 2
    ids = [r["id"] for r in results]
    assert 1 not in ids
