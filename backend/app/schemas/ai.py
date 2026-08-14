"""Pydantic schemas for AI/RAG endpoints — suggestions, status, and ingestion responses."""

from typing import Optional
from pydantic import BaseModel


class SuggestionItem(BaseModel):
    """A single RAG-retrieved suggestion."""
    id: str
    content: str
    source: str
    source_type: str  # "knowledge_base" or "resolved_complaint"
    similarity_score: float
    category: str
    section: Optional[str] = None


class AiSuggestionResponse(BaseModel):
    """Response from the AI suggestion endpoint."""
    suggestions: list[SuggestionItem]
    synthesized_answer: Optional[str] = None
    query_text: str
    total_results: int
    error: Optional[str] = None


class KnowledgeBaseStatus(BaseModel):
    """Current status of the RAG knowledge base."""
    total_chunks: int
    collection_name: str
    last_indexed_at: Optional[str] = None
    persist_directory: str


class IngestResponse(BaseModel):
    """Response from the ingestion endpoints."""
    status: str
    chunks_ingested: Optional[int] = None
    source_files: Optional[int] = None
    indexed_at: Optional[str] = None
    message: Optional[str] = None
