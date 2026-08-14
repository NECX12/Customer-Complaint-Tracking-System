"""
Ingestion orchestrator.

Provides functions to:
1. ingest_knowledge_base()      — load all markdown docs and add to ChromaDB
2. ingest_resolved_complaint()  — embed a single resolved complaint
3. rebuild_index()              — full re-index of everything
"""

import logging
from datetime import datetime, timezone

from app.ai.document_loader import load_knowledge_base, create_complaint_chunk
from app.ai.embeddings import embed_texts
from app.ai.vector_store import add_documents, reset_collection, get_collection_stats

logger = logging.getLogger(__name__)

# Track the last time the knowledge base was indexed
_last_indexed_at: str | None = None


def ingest_knowledge_base() -> dict:
    """
    Load all knowledge base markdown documents, embed them,
    and store in ChromaDB.

    Returns a summary dict with counts.
    """
    global _last_indexed_at

    logger.info("Starting knowledge base ingestion...")
    chunks = load_knowledge_base()

    if not chunks:
        logger.warning("No knowledge base documents found to ingest")
        return {"status": "warning", "chunks_ingested": 0, "message": "No documents found"}

    # Extract content for embedding
    contents = [chunk.content for chunk in chunks]

    # Generate embeddings in batches
    logger.info(f"Generating embeddings for {len(contents)} chunks...")
    batch_size = 64
    all_embeddings: list[list[float]] = []

    for i in range(0, len(contents), batch_size):
        batch = contents[i : i + batch_size]
        batch_embeddings = embed_texts(batch)
        all_embeddings.extend(batch_embeddings)
        logger.info(f"  Embedded batch {i // batch_size + 1}/{(len(contents) + batch_size - 1) // batch_size}")

    # Prepare for ChromaDB
    ids = [chunk.chunk_id for chunk in chunks]
    metadatas = [chunk.metadata for chunk in chunks]

    # Store in ChromaDB
    add_documents(
        ids=ids,
        documents=contents,
        embeddings=all_embeddings,
        metadatas=metadatas,
    )

    _last_indexed_at = datetime.now(timezone.utc).isoformat()

    result = {
        "status": "success",
        "chunks_ingested": len(chunks),
        "source_files": len(set(m.get("source_file", "") for m in metadatas)),
        "indexed_at": _last_indexed_at,
    }
    logger.info(f"Knowledge base ingestion complete: {result}")
    return result


def ingest_resolved_complaint(
    complaint_id: str,
    title: str,
    description: str,
    resolution_comments: list[str],
) -> dict:
    """
    Embed and store a single resolved complaint for future retrieval.

    Called automatically when a complaint transitions to RESOLVED status.

    Args:
        complaint_id: The complaint UUID as string.
        title: Complaint title.
        description: Complaint description.
        resolution_comments: List of resolution comment strings from status history.

    Returns:
        Summary dict.
    """
    logger.info(f"Ingesting resolved complaint: {complaint_id}")

    try:
        chunk = create_complaint_chunk(
            complaint_id=complaint_id,
            title=title,
            description=description,
            resolution_comments=resolution_comments,
        )

        # Generate embedding
        embedding = embed_texts([chunk.content])

        if not embedding:
            return {"status": "error", "message": "Failed to generate embedding"}

        # Store in ChromaDB
        add_documents(
            ids=[chunk.chunk_id],
            documents=[chunk.content],
            embeddings=embedding,
            metadatas=[chunk.metadata],
        )

        result = {
            "status": "success",
            "complaint_id": complaint_id,
            "chunk_id": chunk.chunk_id,
        }
        logger.info(f"Complaint ingested: {result}")
        return result

    except Exception as e:
        logger.error(f"Failed to ingest complaint {complaint_id}: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}


def rebuild_index() -> dict:
    """
    Full re-index: reset ChromaDB and re-ingest the knowledge base.

    Note: This does NOT re-ingest resolved complaints — those would need
    to be re-ingested separately from the database.
    """
    global _last_indexed_at

    logger.info("Rebuilding RAG index from scratch...")

    # Reset the collection
    reset_collection()

    # Re-ingest knowledge base
    kb_result = ingest_knowledge_base()

    result = {
        "status": "success",
        "knowledge_base": kb_result,
        "message": "Index rebuilt. Note: resolved complaints must be re-ingested separately.",
    }
    logger.info(f"Index rebuild complete: {result}")
    return result


def get_index_status() -> dict:
    """Return the current status of the RAG index."""
    stats = get_collection_stats()
    return {
        "total_chunks": stats["total_chunks"],
        "collection_name": stats["collection_name"],
        "last_indexed_at": _last_indexed_at,
        "persist_directory": stats["persist_directory"],
    }
