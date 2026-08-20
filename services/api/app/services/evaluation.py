import json
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import evaluation_repo
from app.services.generation import generation_engine

logger = logging.getLogger(__name__)

class EvaluationEngine:
    """Evaluates RAG queries using LLM-as-a-judge."""

    async def evaluate_query(self, db: AsyncSession, query_id: str, question: str, answer: str, context: str):
        """Evaluates Faithfulness and Answer Relevance."""
        
        prompt = f"""You are an impartial judge evaluating a RAG system.
Evaluate the following ANSWER based on the given QUESTION and CONTEXT.
Provide two scores from 0 to 1:
1. "faithfulness": How well the answer is supported by the context (0 if hallucinated).
2. "relevance": How directly the answer addresses the question.

Return ONLY a JSON object with these two keys and float values.

QUESTION:
{question}

CONTEXT:
{context}

ANSWER:
{answer}
"""
        
        # We will use generation_engine to get the evaluation
        eval_result = ""
        # Mock context chunks to reuse generation_engine logic but override prompt
        async for chunk in generation_engine.generate_answer_stream(prompt, [], model="llama3"):
            eval_result += chunk
            
        try:
            # Parse JSON
            start = eval_result.find("{")
            end = eval_result.rfind("}") + 1
            if start != -1 and end != -1:
                json_str = eval_result[start:end]
                scores = json.loads(json_str)
            else:
                scores = {"faithfulness": 0.0, "relevance": 0.0}
                
            faithfulness = float(scores.get("faithfulness", 0.0))
            relevance = float(scores.get("relevance", 0.0))
            
            # Save to DB
            eval_record = await evaluation_repo.create(db, obj_in={
                "query_id": query_id,
                "faithfulness_score": faithfulness,
                "relevance_score": relevance,
                "feedback": "Auto-evaluated by LLM"
            })
            return eval_record
            
        except Exception as e:
            logger.error(f"Failed to evaluate query {query_id}: {e}")
            return None

evaluation_engine = EvaluationEngine()
