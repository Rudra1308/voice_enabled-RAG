from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.repositories import evaluation_repo

router = APIRouter()

@router.get("/")
async def list_evaluations(db: AsyncSession = Depends(get_db)):
    """Lists recent evaluations."""
    evals = await evaluation_repo.get_multi(db, limit=50)
    
    # Calculate averages
    total_f = 0
    total_r = 0
    count = len(evals)
    
    if count > 0:
        total_f = sum(e.faithfulness_score for e in evals if e.faithfulness_score)
        total_r = sum(e.relevance_score for e in evals if e.relevance_score)
        
    return {
        "averages": {
            "faithfulness": total_f / count if count > 0 else 0,
            "relevance": total_r / count if count > 0 else 0,
            "count": count
        },
        "history": [
            {
                "id": e.id,
                "query_id": e.query_id,
                "faithfulness_score": e.faithfulness_score,
                "relevance_score": e.relevance_score,
                "feedback": e.feedback,
                "created_at": e.created_at
            }
            for e in evals
        ]
    }
