import json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories import document_repo
from app.services.generation import generation_engine
from app.services.reranker import RerankingEngine
from app.services.retrieval import retrieval_engine

router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    knowledge_base_id: str = "default-kb-id"
    model: str = "llama3"
    history: list[dict] = []  # Array of {role: str, content: str}

@router.post("/stream")
async def stream_query(request: QueryRequest, db: AsyncSession = Depends(get_db)):
    """
    Executes a RAG query:
    1. Retrieves relevant chunks from Vector DB.
    2. Reranks chunks.
    3. Formats context with citations.
    4. Streams answer from local LLM.
    """
    # 1. Retrieve
    try:
        chunks = await retrieval_engine.retrieve(request.query, knowledge_base_id=request.knowledge_base_id, top_k=10)
    except Exception as e:
        print(f"Retrieval error: {e}")
        chunks = []
    
    # 3. Grounding + Citations
    # Fetch document names from DB before streaming so we don't use a closed DB session
    doc_names = {}
    if chunks:
        for chunk in chunks:
            doc_id = chunk.get("document_id")
            if doc_id and doc_id not in doc_names:
                try:
                    doc = await document_repo.get(db, doc_id)
                    if doc:
                        doc_names[doc_id] = doc.filename
                except Exception as e:
                    print(f"Error fetching doc {doc_id}: {e}")

    # 4. Stream response
    async def generate():
        yield json.dumps({"type": "token", "data": "*(Initializing AI models, this may take a few minutes on the first run...)*\n\n"}) + "\n"
        
        # 2. Rerank
        reranked_chunks = []
        if chunks:
            from app.core.config import settings
            import asyncio
            if settings.GROQ_API_KEY:
                reranked_chunks = chunks[:3]
            else:
                try:
                    reranker = RerankingEngine.get_instance()
                    reranked_chunks = await asyncio.to_thread(reranker.rerank, request.query, chunks, top_k=3)
                except Exception as e:
                    print(f"Reranker failed (fallback to original chunks): {e}")
                    reranked_chunks = chunks[:3]
            
        formatted_context = []
        citations = []
        
        for i, chunk in enumerate(reranked_chunks):
            doc_id = chunk.get("document_id")
            doc_name = doc_names.get(doc_id, "Unknown Document") if doc_id else "Unknown Document"
                    
            citation_num = i + 1
            citations.append({
                "number": citation_num,
                "document_name": doc_name,
                "document_id": doc_id,
                "snippet": chunk["content"][:100] + "..."
            })
            
            # Inject citation number into the context for the LLM
            formatted_chunk = chunk.copy()
            formatted_chunk["content"] = f"[Source {citation_num}: {doc_name}]\n{chunk['content']}"
            formatted_context.append(formatted_chunk)

        # Send citations as a special event
        yield json.dumps({"type": "citations", "data": citations}) + "\n"
        
        # Then stream tokens
        async for token in generation_engine.generate_answer_stream(request.query, formatted_context, history=request.history, model=request.model):
            yield json.dumps({"type": "token", "data": token}) + "\n"
            
    return StreamingResponse(generate(), media_type="application/x-ndjson")
