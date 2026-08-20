import pytest
import respx
from httpx import Response

from app.services.generation import GenerationEngine


@pytest.fixture
def engine():
    return GenerationEngine(ollama_url="http://localhost:11434")

def test_build_prompt(engine):
    query = "What is the capital of France?"
    context = [
        {"content": "Paris is the capital of France."}
    ]
    prompt = engine.build_prompt(query, context)
    
    assert "Paris is the capital of France." in prompt
    assert "What is the capital of France?" in prompt

@pytest.mark.asyncio
@respx.mock
async def test_generate_answer_stream(engine):
    mock_url = "http://localhost:11434/api/generate"
    
    # Mocking a streaming response
    # For httpx mocking with respx, we can just return a single chunk or multiple if we simulate a stream.
    # We will just return a single JSON string that Ollama would return
    mock_response = '{"model":"llama3","created_at":"2023-08-04T19:22:45.499127Z","response":"Paris","done":false}\n'
    
    respx.post(mock_url).mock(return_value=Response(200, text=mock_response))
    
    chunks = []
    async for chunk in engine.generate_answer_stream("Test", [{"content": "Test context"}]):
        chunks.append(chunk)
        
    assert len(chunks) == 1
    assert chunks[0] == "Paris"
