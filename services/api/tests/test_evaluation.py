from unittest.mock import AsyncMock, patch

import pytest

from app.services.evaluation import evaluation_engine


@pytest.fixture
def mock_generation_engine():
    with patch("app.services.evaluation.generation_engine") as mock:
        yield mock

@pytest.fixture
def mock_evaluation_repo():
    with patch("app.services.evaluation.evaluation_repo") as mock:
        yield mock

@pytest.mark.asyncio
async def test_evaluate_query(mock_generation_engine, mock_evaluation_repo):
    # Mock LLM returning valid JSON
    async def mock_generate(*args, **kwargs):
        yield '{"faithfulness": 0.9, "relevance": 0.8}'
        
    mock_generation_engine.generate_answer_stream = mock_generate
    
    # Mock DB repo
    mock_evaluation_repo.create = AsyncMock(return_value={"id": "eval-1", "faithfulness_score": 0.9, "relevance_score": 0.8})
    
    result = await evaluation_engine.evaluate_query(None, "q1", "Q?", "A.", "C.")
    
    assert result["faithfulness_score"] == 0.9
    assert result["relevance_score"] == 0.8
    mock_evaluation_repo.create.assert_called_once()
