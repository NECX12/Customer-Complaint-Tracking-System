"""
ChromaDB vector store connection manager.

Handles collection creation, document storage with metadata,
similarity querying, and document deletion.

ChromaDB runs in-process with persistent storage — no external
service needed.
"""

import logging
from typing import Optional

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.ai.config import CHROMA_PERSIST_DIR, COLLECTION_NAME

logger = logging.getLogger(__name__)

# Singleton client
_client: Optional[chromadb.ClientAPI] = None


def _get_client() -> chromadb.ClientAPI:
    """Get or create the ChromaDB persistent client (singleton)."""
    global _client
    if _client is None:
        CHROMA_PERSIST_DIR.mkdir(parents=True, exist_ok=True)
        _client = chromadb.PersistentClient(
            path=str(CHROMA_PERSIST_DIR),
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        logger.info(f"ChromaDB client initialized at {CHROMA_PERSIST_DIR}")
    return _client


def get_or_create_collection():
    """Get or create the main knowledge base collection."""
    client = _get_client()
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},  # cosine similarity
    )
    return collection


def add_documents(
    ids: list[str],
    documents: list[str],
    embeddings: list[list[float]],
    metadatas: list[dict],
) -> None:
    """
    Add documents to the vector store.

    Args:
        ids: Unique identifiers for each document chunk.
        documents: The text content of each chunk.
        embeddings: Pre-computed embedding vectors.
        metadatas: Metadata dicts (source_type, source_file, section, etc.).
    """
    collection = get_or_create_collection()
    # ChromaDB upserts by default when IDs already exist
    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )
    logger.info(f"Upserted {len(ids)} documents into ChromaDB")


def query_similar(
    query_embedding: list[float],
    n_results: int = 5,
    where_filter: Optional[dict] = None,
) -> dict:
    """
    Query the vector store for the most similar documents.

    Args:
        query_embedding: The embedding vector of the query.
        n_results: Number of results to return.
        where_filter: Optional metadata filter (e.g., {"source_type": "knowledge_base"}).

    Returns:
        ChromaDB query results dict with keys:
        ids, documents, metadatas, distances.

    Returns an empty result dict (instead of raising) when the collection
    has no documents — this happens before the knowledge base is indexed.
    """
    collection = get_or_create_collection()

    # Guard: ChromaDB raises an exception if you query an empty collection.
    # Return a structured empty result so the caller handles it gracefully.
    count = collection.count()
    if count == 0:
        logger.warning(
            "ChromaDB collection is empty. "
            "Run: python -m scripts.ingest   (from the backend/ directory) "
            "to index the knowledge base."
        )
        return {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}

    # Clamp n_results to the actual collection size to avoid ChromaDB errors
    n_results = min(n_results, count)

    query_params = {
        "query_embeddings": [query_embedding],
        "n_results": n_results,
        "include": ["documents", "metadatas", "distances"],
    }
    if where_filter:
        query_params["where"] = where_filter

    results = collection.query(**query_params)
    return results


def delete_by_metadata(key: str, value: str) -> None:
    """Delete all documents matching a metadata filter."""
    collection = get_or_create_collection()
    collection.delete(where={key: value})
    logger.info(f"Deleted documents where {key}={value}")


def get_collection_stats() -> dict:
    """Return basic stats about the knowledge base collection."""
    collection = get_or_create_collection()
    count = collection.count()
    return {
        "total_chunks": count,
        "collection_name": COLLECTION_NAME,
        "persist_directory": str(CHROMA_PERSIST_DIR),
    }


def reset_collection() -> None:
    """Delete and recreate the collection (full reset)."""
    client = _get_client()
    try:
        client.delete_collection(COLLECTION_NAME)
        logger.info(f"Deleted collection: {COLLECTION_NAME}")
    except Exception:
        pass  # Collection may not exist yet
    get_or_create_collection()
    logger.info(f"Recreated collection: {COLLECTION_NAME}")
