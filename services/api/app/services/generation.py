import json
import logging
from collections.abc import AsyncGenerator

import httpx

logger = logging.getLogger(__name__)

import os
from app.core.config import settings

class GenerationEngine:
    """Service to communicate with a local LLM (Ollama) or Cloud LLM (Groq) to generate grounded answers."""
    
    def __init__(self, ollama_url: str = "http://localhost:11434", default_model: str = "llama3"):
        self.ollama_url = ollama_url
        self.default_model = default_model
        self.groq_api_key = settings.GROQ_API_KEY

    def build_prompt(self, query: str, context_chunks: list[dict], history: list[dict] = None) -> str:
        """Constructs a prompt string with context and history, grouped by document."""
        
        # Group by document
        if not context_chunks:
            context_text = "NO CONTEXT WAS FOUND FOR THIS QUERY. You MUST state that no relevant documents were found in the uploaded content, and refuse to answer the question based on your own knowledge."
        else:
            context_text = "\n\n".join([
                f"{chunk['content']}" 
                for chunk in context_chunks
            ])
        
        history_text = ""
        if history:
            history_text = "\nPREVIOUS CONVERSATION:\n"
            for msg in history[-3:]: # only keep last 3 to avoid overflow
                role = msg.get("role", "User")
                content = msg.get("content", "")
                history_text += f"{role.capitalize()}: {content}\n"
        
        prompt = f"""You are a helpful and precise academic research assistant.
Use the following pieces of context to answer the user's question. 
If the context is empty, or if you don't know the answer based on the context, you MUST say that you don't know or that no relevant documents were found. Do NOT try to make up an answer or answer from your general knowledge.
Keep the answer concise and academic in tone.
Always cite your sources if possible based on the context provided.

CONTEXT:
{context_text}
{history_text}
USER QUESTION:
{query}

ANSWER:
"""
        return prompt

    async def generate_answer_stream(self, query: str, context_chunks: list[dict], history: list[dict] = None, model: str | None = None) -> AsyncGenerator[str, None]:
        """Streams the answer from the LLM."""
        prompt = self.build_prompt(query, context_chunks, history)
        
        if self.groq_api_key:
            async for chunk in self._generate_groq_stream(prompt):
                yield chunk
        else:
            async for chunk in self._generate_ollama_stream(prompt, model):
                yield chunk
            
    async def _generate_groq_stream(self, prompt: str) -> AsyncGenerator[str, None]:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama3-8b-8192",
            "messages": [{"role": "user", "content": prompt}],
            "stream": True,
            "temperature": 0.2
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream("POST", url, headers=headers, json=payload) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:]
                            if data_str == "[DONE]":
                                break
                            try:
                                data = json.loads(data_str)
                                delta = data["choices"][0]["delta"]
                                if "content" in delta:
                                    yield delta["content"]
                            except json.JSONDecodeError:
                                logger.warning("Failed to decode JSON chunk from Groq.")
        except Exception as e:
            logger.error(f"Error communicating with Groq: {e!s}")
            yield f"\n[Error communicating with Cloud LLM: {e!s}]"

    async def _generate_ollama_stream(self, prompt: str, model: str | None) -> AsyncGenerator[str, None]:
        model_name = model or self.default_model
        payload = {
            "model": model_name,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": 0.2 # Lower temperature for factual retrieval
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream("POST", f"{self.ollama_url}/api/generate", json=payload) as response:
                    response.raise_for_status()
                    async for chunk in response.aiter_text():
                        if chunk:
                            try:
                                data = json.loads(chunk)
                                if "response" in data:
                                    yield data["response"]
                            except json.JSONDecodeError:
                                logger.warning("Failed to decode JSON chunk from Ollama.")
        except httpx.HTTPStatusError as e:
            error_body = ""
            try:
                error_body = await e.response.aread()
                error_body = error_body.decode('utf-8')
            except Exception:
                pass
            logger.error(f"Error communicating with Ollama: {e!s} - Body: {error_body}")
            yield f"\n[Error communicating with local LLM: {e!s}\nDetails: {error_body}]"
        except Exception as e:
            logger.error(f"Error communicating with Ollama: {e!s}")
            yield f"\n[Error communicating with local LLM: {e!s}]"

generation_engine = GenerationEngine()
