import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api import documents, urls, queries, voice, evaluations

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    logger.info("Starting up Academic VoiceRAG API")
    yield
    # Shutdown logic
    logger.info("Shutting down Academic VoiceRAG API")

app = FastAPI(
    title="Academic VoiceRAG API",
    description="API for the Academic VoiceRAG system.",
    version="0.1.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], # Allowed frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# (JWT middleware placeholder removed to prevent CORS preflight blocking)

app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(urls.router, prefix="/api/documents", tags=["documents"])
app.include_router(queries.router, prefix="/api/queries", tags=["queries"])
app.include_router(voice.router, prefix="/api/voice", tags=["voice"])
app.include_router(evaluations.router, prefix="/api/evaluations", tags=["evaluations"])

@app.get("/health/ready")
async def health_ready():
    """Endpoint for basic health checking"""
    return {"status": "ok", "service": "academic-voicerag-api"}

@app.get("/metrics")
async def get_metrics():
    """Endpoint for prometheus or custom metrics"""
    return {"metrics": "Not implemented yet"}
