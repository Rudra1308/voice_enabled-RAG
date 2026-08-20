# Academic VoiceRAG

A production-grade, voice-first academic research assistant.

## Features
- Voice and text query interface.
- Local LLM inference (Ollama).
- Local embeddings and reranking.
- Hybrid Retrieval (Qdrant + BM25).
- Multi-document reasoning with citation backing.
- Local STT (faster-whisper) and TTS (Piper).
- Intelligent document chunking and metadata extraction.

## Prerequisites
- Docker and Docker Compose
- Python 3.11+
- Node.js 18+
- Ollama (installed locally on the host)

## Setup

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Start the infrastructure:
   ```bash
   docker compose up -d
   ```

