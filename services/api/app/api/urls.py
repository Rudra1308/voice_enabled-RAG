import hashlib

import httpx
from bs4 import BeautifulSoup
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel, HttpUrl
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories import document_repo, kb_repo, user_repo

router = APIRouter()

class UrlIngestRequest(BaseModel):
    url: HttpUrl
    knowledge_base_id: str = "default-kb-id"

@router.post("/url")
async def ingest_url(
    request: UrlIngestRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    url_str = str(request.url)
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url_str)
            response.raise_for_status()
            html_content = response.text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {e!s}")

    soup = BeautifulSoup(html_content, "html.parser")
    # Clean text
    for script in soup(["script", "style"]):
        script.extract()
    text_content = soup.get_text(separator="\n", strip=True)
    
    # Hash for deduplication
    content_hash = hashlib.sha256(text_content.encode("utf-8")).hexdigest()

    # Make sure we have a user and KB
    kb = await kb_repo.get(db, request.knowledge_base_id)
    if not kb:
        user = await user_repo.create(db, obj_in={"email": "demo_url@example.com"})
        kb = await kb_repo.create(db, obj_in={
            "id": request.knowledge_base_id,
            "user_id": user.id,
            "name": "Default Knowledge Base"
        })

    # Create document record
    doc = await document_repo.create(db, obj_in={
        "knowledge_base_id": kb.id,
        "filename": soup.title.string if soup.title else "Untitled Webpage",
        "source_type": "url",
        "source_url": url_str,
        "mime_type": "text/html",
        "file_size": len(text_content.encode('utf-8')),
        "content_hash": content_hash,
        "status": "READY" # No need to extract further, it's already text
    })

    # We could write text to a local file or keep it in DB/chunks directly.
    # For Phase 5 we just save the record to indicate ingestion success.

    return {"message": "URL ingested successfully", "document_id": doc.id, "status": doc.status}
