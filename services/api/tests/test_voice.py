from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
def mock_stt_engine():
    with patch("app.api.voice.stt_engine") as mock:
        yield mock

@pytest.mark.asyncio
async def test_transcribe_audio(mock_stt_engine):
    mock_stt_engine.transcribe = AsyncMock(return_value="This is a test recording.")
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create a dummy audio file payload
        files = {
            "file": ("test.webm", b"dummy audio data", "audio/webm")
        }
        
        response = await client.post("/api/voice/transcribe", files=files)
        
        assert response.status_code == 200
        assert response.json() == {"text": "This is a test recording."}
        
        # Test invalid content type
        invalid_files = {
            "file": ("test.txt", b"dummy text data", "text/plain")
        }
        response_invalid = await client.post("/api/voice/transcribe", files=invalid_files)
        assert response_invalid.status_code == 400
