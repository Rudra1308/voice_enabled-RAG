import json
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
def mock_retrieval_engine():
    with patch("app.api.queries.retrieval_engine") as mock:
        yield mock

@pytest.fixture
def mock_reranker():
    with patch("app.api.queries.RerankingEngine.get_instance") as mock:
        yield mock

@pytest.fixture
def mock_generation_engine():
    with patch("app.api.queries.generation_engine") as mock:
        yield mock

@pytest.mark.asyncio
async def test_stream_query(mock_retrieval_engine, mock_reranker, mock_generation_engine):
    # Mock retrieval
    mock_retrieval_engine.retrieve = AsyncMock(return_value=[{"id": "c1", "content": "chunk 1", "document_id": "d1"}])
    
    # Mock reranker
    mock_reranker_instance = mock_reranker.return_value
    mock_reranker_instance.rerank.return_value = [{"id": "c1", "content": "chunk 1", "document_id": "d1", "rerank_score": 0.9}]
    
    # Mock generation (async generator)
    async def mock_generator(*args, **kwargs):
        yield "Hello"
        yield " World"
        
    mock_generation_engine.generate_answer_stream = mock_generator

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/queries/stream", json={"query": "Test query?"})
        
        assert response.status_code == 200
        
        # Read streaming NDJSON response
        lines = [line for line in response.text.split("\n") if line.strip()]
        assert len(lines) == 3
        
        # First line is citations
        data0 = json.loads(lines[0])
        assert data0["type"] == "citations"
        assert len(data0["data"]) == 1
        assert data0["data"][0]["number"] == 1
        
        # Second line is first token
        data1 = json.loads(lines[1])
        assert data1["type"] == "token"
        assert data1["data"] == "Hello"
        
        # Third line is second token
        data2 = json.loads(lines[2])
        assert data2["type"] == "token"
        assert data2["data"] == " World"
