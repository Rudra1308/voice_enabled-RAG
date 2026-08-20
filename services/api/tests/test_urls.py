import pytest
import respx
from httpx import ASGITransport, AsyncClient, Response

from app.main import app


@pytest.mark.asyncio
@respx.mock
async def test_ingest_url():
    # Mock external URL call
    mock_url = "https://example.com/academic-paper"
    respx.get(mock_url).mock(return_value=Response(200, text="<html><head><title>Test Paper</title></head><body><p>This is a test academic paper.</p></body></html>"))

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/documents/url", json={
            "url": mock_url,
            "knowledge_base_id": "test-kb"
        })
            
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "URL ingested successfully"
    assert "document_id" in data
    assert data["status"] == "READY"
