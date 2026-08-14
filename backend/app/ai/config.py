"""
AI-specific configuration.

Centralizes all AI-related settings: embedding model choice,
ChromaDB persistence path, chunk sizing, and optional LLM provider settings.

All values have sensible defaults so the RAG system works out-of-the-box
without any API keys (pure retrieval mode).
"""

from __future__ import annotations

import os
from pathlib import Path

from app.core.config import settings


# ── Paths ────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent.parent
KNOWLEDGE_BASE_DIR: Path = BASE_DIR / "knowledge_base"
CHROMA_PERSIST_DIR: Path = BASE_DIR / ".chroma_db"


# ── Embedding Model ─────────────────────────────────────────────
EMBEDDING_MODEL_NAME: str = settings.EMBEDDING_MODEL_NAME or "all-MiniLM-L6-v2"


# ── Document Chunking ───────────────────────────────────────────
CHUNK_MAX_CHARS: int = settings.CHUNK_MAX_CHARS
CHUNK_OVERLAP_CHARS: int = settings.CHUNK_OVERLAP_CHARS


# ── Retrieval ────────────────────────────────────────────────────
TOP_K_RESULTS: int = settings.RAG_TOP_K
RAG_TOP_K: int = TOP_K_RESULTS


# ── ChromaDB ────────────────────────────────────────────────────
COLLECTION_NAME: str = settings.CHROMA_COLLECTION_NAME


# ── AI / LLM Provider ───────────────────────────────────────────
AI_PROVIDER: str = (settings.AI_PROVIDER or "gemini").lower()


# ── Gemini / OpenAI keys ─────────────────────────────────────────
GEMINI_API_KEY: str | None = (
    settings.GEMINI_API_KEY
    or os.getenv("GEMINI_API_KEY")
    or os.getenv("GOOGLE_API_KEY")
)
OPENAI_API_KEY: str | None = settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")


# ── LLM Model ────────────────────────────────────────────────────
if AI_PROVIDER == "gemini":
    LLM_MODEL: str = settings.LLM_MODEL or "gemini-1.5-flash"
elif AI_PROVIDER == "openai":
    LLM_MODEL: str = settings.LLM_MODEL or "gpt-4o-mini"
else:
    LLM_MODEL: str = settings.LLM_MODEL or "gemini-1.5-flash"


# ── Convenience Properties ──────────────────────────────────────
def gemini_enabled() -> bool:
    """Return True when Gemini is the configured provider and a key is available."""
    return AI_PROVIDER == "gemini" and bool(GEMINI_API_KEY)


def llm_enabled() -> bool:
    """Return True when an LLM provider is configured and available."""
    return gemini_enabled() or (AI_PROVIDER == "openai" and bool(OPENAI_API_KEY))
