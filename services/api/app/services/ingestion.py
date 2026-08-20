import logging
import uuid
import os
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import document_repo
from app.services.extractor import DocumentExtractor
from app.services.chunker import DocumentChunker
from app.services.embedding import EmbeddingEngine
from app.services.qdrant import qdrant_service

logger = logging.getLogger(__name__)

async def process_document_background(
    document_id: str,
    file_path: str,
    mime_type: str,
    knowledge_base_id: str,
    db: AsyncSession
):
    """Background task to extract, chunk, embed, and index a document."""
    try:
        logger.info(f"Starting ingestion for document {document_id}")
        
        # 1. Update status to PROCESSING
        doc = await document_repo.get(db, document_id)
        if doc:
            await document_repo.update(db, db_obj=doc, obj_in={"status": "PROCESSING"})
        
        # 2. Extract text
        text = DocumentExtractor.extract_text(file_path, mime_type)
        
        # 3. Chunk text
        chunker = DocumentChunker()
        chunks = chunker.chunk_text(text)
        
        # 4. Embed chunks
        embedding_engine = EmbeddingEngine.get_instance()
        texts = [chunk["content"] for chunk in chunks]
        embeddings = embedding_engine.embed_batch(texts)
        
        # 5. Format for Qdrant
        qdrant_chunks = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            qdrant_chunks.append({
                "id": str(uuid.uuid4()),
                "vector": embedding,
                "payload": {
                    "knowledge_base_id": knowledge_base_id,
                    "document_id": document_id,
                    "chunk_index": i,
                    "content": chunk["content"]
                }
            })
            
        # 6. Ensure collection and upsert
        await qdrant_service.ensure_collection("documents", embedding_engine.vector_dim)
        await qdrant_service.upsert_chunks("documents", qdrant_chunks)
        
        # 7. Mark as READY
        doc = await document_repo.get(db, document_id)
        if doc:
            await document_repo.update(db, db_obj=doc, obj_in={"status": "READY"})
        logger.info(f"Document {document_id} successfully ingested!")
        
    except Exception as e:
        logger.error(f"Failed to ingest document {document_id}: {e!s}")
        doc = await document_repo.get(db, document_id)
        if doc:
            await document_repo.update(db, db_obj=doc, obj_in={"status": "FAILED"})
