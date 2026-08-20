import os

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text

from app.core.database import AsyncSessionLocal, Base, engine
from app.main import app


@pytest.fixture(autouse=True)
async def setup_db():
    # Setup test DB tables and mock user
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSessionLocal() as session:
        # Check if default user exists to avoid unique constraint errors
        res = await session.execute(text("SELECT id FROM users WHERE email='demo@example.com'"))
        if not res.scalar():
            from app.repositories import kb_repo, user_repo
            user = await user_repo.create(session, obj_in={"email": "demo@example.com"})
            await kb_repo.create(session, obj_in={
                "id": "default-kb-id",
                "user_id": user.id,
                "name": "Default KB"
            })
    
    yield


@pytest.mark.asyncio
async def test_upload_document():
    # Write a dummy file
    with open("test.pdf", "wb") as f:
        f.write(b"dummy pdf content")
        
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with open("test.pdf", "rb") as f:
            response = await client.post("/api/documents/upload", files={"file": ("test.pdf", f, "application/pdf")})
            
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "File uploaded successfully"
    assert "document_id" in data
    assert data["status"] == "PENDING"
    
    # Cleanup
    os.remove("test.pdf")
