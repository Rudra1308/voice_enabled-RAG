import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


def generate_uuid():
    return str(uuid.uuid4())

def utc_now():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    knowledge_bases = relationship("KnowledgeBase", back_populates="user")

class KnowledgeBase(Base):
    __tablename__ = "knowledge_bases"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    user = relationship("User", back_populates="knowledge_bases")
    documents = relationship("Document", back_populates="knowledge_base", cascade="all, delete-orphan")
    queries = relationship("Query", back_populates="knowledge_base", cascade="all, delete-orphan")

class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=generate_uuid)
    knowledge_base_id = Column(String, ForeignKey("knowledge_bases.id"), nullable=False)
    filename = Column(String, nullable=False)
    source_type = Column(String, nullable=False) # e.g. "pdf", "url"
    source_url = Column(String, nullable=True)
    mime_type = Column(String, nullable=True)
    file_size = Column(Integer, nullable=True)
    content_hash = Column(String, nullable=True)
    status = Column(String, default="PENDING") # PENDING, PROCESSING, READY, ERROR
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    indexed_at = Column(DateTime(timezone=True), nullable=True)

    knowledge_base = relationship("KnowledgeBase", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    jobs = relationship("IngestionJob", back_populates="document", cascade="all, delete-orphan")

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(String, primary_key=True, default=generate_uuid)
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    page_number = Column(Integer, nullable=True)
    section = Column(String, nullable=True)
    token_count = Column(Integer, nullable=True)
    content_hash = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    document = relationship("Document", back_populates="chunks")
    # For query_sources relationship
    query_sources = relationship("QuerySource", back_populates="chunk")

class IngestionJob(Base):
    __tablename__ = "ingestion_jobs"

    id = Column(String, primary_key=True, default=generate_uuid)
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    status = Column(String, default="QUEUED") # QUEUED, IN_PROGRESS, COMPLETED, FAILED
    progress = Column(Float, default=0.0)
    current_stage = Column(String, nullable=True)
    error = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    document = relationship("Document", back_populates="jobs")

class Query(Base):
    __tablename__ = "queries"

    id = Column(String, primary_key=True, default=generate_uuid)
    knowledge_base_id = Column(String, ForeignKey("knowledge_bases.id"), nullable=False)
    query_text = Column(Text, nullable=False)
    intent = Column(String, nullable=True)
    latency_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    knowledge_base = relationship("KnowledgeBase", back_populates="queries")
    sources = relationship("QuerySource", back_populates="query", cascade="all, delete-orphan")
    evaluation = relationship("Evaluation", back_populates="query", uselist=False, cascade="all, delete-orphan")

class QuerySource(Base):
    __tablename__ = "query_sources"

    id = Column(String, primary_key=True, default=generate_uuid)
    query_id = Column(String, ForeignKey("queries.id"), nullable=False)
    chunk_id = Column(String, ForeignKey("document_chunks.id"), nullable=False)
    retrieval_score = Column(Float, nullable=True)
    rerank_score = Column(Float, nullable=True)
    rank = Column(Integer, nullable=False)

    query = relationship("Query", back_populates="sources")
    chunk = relationship("DocumentChunk", back_populates="query_sources")

class Evaluation(Base):
    __tablename__ = "evaluations"

    id = Column(String, primary_key=True, default=generate_uuid)
    query_id = Column(String, ForeignKey("queries.id"), nullable=False)
    faithfulness = Column(Float, nullable=True)
    relevance = Column(Float, nullable=True)
    context_precision = Column(Float, nullable=True)
    context_recall = Column(Float, nullable=True)
    grounding_score = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    query = relationship("Query", back_populates="evaluation")
