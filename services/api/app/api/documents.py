import hashlib
import os

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories import document_repo, kb_repo, user_repo

router = APIRouter()

UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/uploads"))

# Ensure upload dir exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    knowledge_base_id: str = "default-kb-id",  # In a real app, this comes from the user context/request
    db: AsyncSession = Depends(get_db)
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename missing")

    # Read content to hash it for deduplication
    content = await file.read()
    file_hash = hashlib.sha256(content).hexdigest()

    # Make sure we have a user and KB (Mocking for Phase 3 so it works standalone)
    kb = await kb_repo.get(db, knowledge_base_id)
    if not kb:
        # Create a mock user and KB for demo purposes
        user = await user_repo.create(db, obj_in={"email": "demo@example.com"})
        kb = await kb_repo.create(db, obj_in={
            "id": "default-kb-id",
            "user_id": user.id,
            "name": "Default Knowledge Base"
        })

    # Check if document with this hash already exists in this KB
    from sqlalchemy.future import select
    from app.models import Document
    
    existing_doc_query = await db.execute(
        select(Document).filter(
            Document.knowledge_base_id == kb.id,
            Document.content_hash == file_hash
        )
    )
    existing_doc = existing_doc_query.scalars().first()
    if existing_doc:
        return {"message": "File already exists", "document_id": existing_doc.id, "status": existing_doc.status}

    # Save file locally using hash to avoid collisions
    ext = os.path.splitext(file.filename)[1]
    safe_filename = f"{file_hash}{ext}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)

    with open(file_path, "wb") as f:
        f.write(content)

    from app.services.ingestion import process_document_background

    # Create document record
    doc = await document_repo.create(db, obj_in={
        "knowledge_base_id": kb.id,
        "filename": file.filename,
        "source_type": "file",
        "mime_type": file.content_type,
        "file_size": len(content),
        "content_hash": file_hash,
        "status": "PENDING"
    })
    
    # Trigger background task
    from app.core.database import AsyncSessionLocal
    
    async def run_ingestion():
        async with AsyncSessionLocal() as session:
            await process_document_background(
                document_id=doc.id,
                file_path=file_path,
                mime_type=file.content_type,
                knowledge_base_id=kb.id,
                db=session
            )
            
    background_tasks.add_task(run_ingestion)

    return {"message": "File uploaded successfully", "document_id": doc.id, "status": doc.status}

@router.get("")
async def list_documents(
    knowledge_base_id: str = "default-kb-id",
    db: AsyncSession = Depends(get_db)
):
    from sqlalchemy.future import select
    from app.models import Document
    
    result = await db.execute(
        select(Document)
        .filter(Document.knowledge_base_id == knowledge_base_id)
        .order_by(Document.created_at.desc())
    )
    docs = result.scalars().all()
    
    return {
        "documents": [
            {
                "id": doc.id,
                "filename": doc.filename,
                "status": doc.status,
                "file_size": doc.file_size,
                "created_at": doc.created_at
            }
            for doc in docs
        ]
    }
