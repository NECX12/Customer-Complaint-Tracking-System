"""
RAG engine — the main retrieval-augmented generation pipeline.

Accepts a complaint (title + description), embeds it, queries the
ChromaDB vector store for similar documents, and returns structured
results.

Operates in two tiers:
- Without LLM API key: pure retrieval — returns top-K similar chunks
- With LLM API key: synthesizes a tailored resolution suggestion from
  the retrieved context (not implemented in this version)
"""

import logging
from typing import Optional

from app.ai.embeddings import embed_single
from app.ai.vector_store import query_similar
from app.ai.config import TOP_K_RESULTS, AI_PROVIDER, GEMINI_API_KEY, LLM_MODEL

logger = logging.getLogger(__name__)


def get_suggestions(
    complaint_title: str,
    complaint_description: str,
    n_results: int = TOP_K_RESULTS,
    source_type_filter: Optional[str] = None,
) -> dict:
    """
    Get RAG-powered resolution suggestions for a complaint.

    Args:
        complaint_title: The complaint title.
        complaint_description: The complaint description.
        n_results: Number of similar documents to retrieve.
        source_type_filter: Optional filter — "knowledge_base" or "resolved_complaint".

    Returns:
        Dict with:
        - suggestions: list of dicts with content, source, similarity_score, metadata
        - synthesized_answer: str or None (None in retrieval-only mode)
        - query_text: the text used for the search
    """
    # Combine title and description for the search query
    query_text = f"{complaint_title}\n{complaint_description}"

    try:
        # Generate embedding for the query
        query_embedding = embed_single(query_text)

        if not query_embedding:
            msg = (
                "Embedding model failed to produce a vector. "
                "Check that sentence-transformers is installed and the model has been downloaded."
            )
            logger.error(msg)
            return _empty_result(query_text, error=msg)

        # Build optional metadata filter
        where_filter = None
        if source_type_filter:
            where_filter = {"source_type": source_type_filter}

        # Query the vector store
        results = query_similar(
            query_embedding=query_embedding,
            n_results=n_results,
            where_filter=where_filter,
        )

        # Parse results into structured suggestions
        suggestions = _parse_results(results)

        # If nothing came back, tell the caller why so the UI can show a
        # useful message rather than the generic "no results" hint.
        if not suggestions:
            from app.ai.vector_store import get_collection_stats
            stats = get_collection_stats()
            if stats["total_chunks"] == 0:
                return _empty_result(
                    query_text,
                    error=(
                        "The knowledge base has not been indexed yet. "
                        "Run:  python -m scripts.ingest  "
                        "from the backend/ directory to populate it."
                    ),
                )

        synthesized_answer = _synthesize_answer(query_text, suggestions)

        return {
            "suggestions": suggestions,
            "synthesized_answer": synthesized_answer,
            "query_text": query_text,
            "total_results": len(suggestions),
        }

    except Exception as e:
        logger.error(f"RAG query failed: {e}", exc_info=True)
        return _empty_result(query_text, error=str(e))


def _parse_results(results: dict) -> list[dict]:
    """
    Parse ChromaDB query results into structured suggestion dicts.

    ChromaDB returns distances (cosine distance). We convert to
    similarity scores (1 - distance) for a more intuitive metric
    where 1.0 = identical and 0.0 = completely different.
    """
    suggestions = []

    if not results or not results.get("ids") or not results["ids"][0]:
        return suggestions

    ids = results["ids"][0]
    documents = results["documents"][0] if results.get("documents") else [None] * len(ids)
    metadatas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(ids)
    distances = results["distances"][0] if results.get("distances") else [1.0] * len(ids)

    for i, doc_id in enumerate(ids):
        # Convert cosine distance to similarity score
        distance = distances[i] if i < len(distances) else 1.0
        similarity_score = round(max(0.0, 1.0 - distance), 4)

        metadata = metadatas[i] if i < len(metadatas) else {}
        content = documents[i] if i < len(documents) else ""

        # Determine the source display name
        source_type = metadata.get("source_type", "unknown")
        if source_type == "knowledge_base":
            source = metadata.get("source_file", "Unknown Document")
        elif source_type == "resolved_complaint":
            source = f"Past Complaint: {metadata.get('title', 'Unknown')}"
        else:
            source = "Unknown Source"

        suggestions.append({
            "id": doc_id,
            "content": content,
            "source": source,
            "source_type": source_type,
            "similarity_score": similarity_score,
            "category": metadata.get("category", "General"),
            "section": metadata.get("section", ""),
            "metadata": metadata,
        })

    # Sort by similarity score (highest first)
    suggestions.sort(key=lambda x: x["similarity_score"], reverse=True)

    return suggestions


def _synthesize_answer(query_text: str, suggestions: list[dict]) -> Optional[str]:
    """Synthesize a helpful answer from the retrieved context when a Gemini key is available."""
    if AI_PROVIDER != "gemini" or not GEMINI_API_KEY:
        return None

    if not suggestions:
        return None

    try:
        import google.generativeai as genai

        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(LLM_MODEL)

        context = "\n\n---\n\n".join(
            f"Source: {item.get('source', 'unknown')}\n{item.get('content', '')}"
            for item in suggestions[:3]
        )

        prompt = (
            "You are a support specialist helping resolve a customer complaint. "
            "Use only the provided context to give practical resolution guidance. "
            "Keep it concise, specific, and action-oriented.\n\n"
            f"Complaint: {query_text}\n\nContext:\n{context}"
        )

        response = model.generate_content(prompt)
        return getattr(response, "text", None) or str(response)
    except Exception as exc:
        logger.warning(f"Gemini synthesis unavailable: {exc}")
        return None


def _empty_result(query_text: str, error: Optional[str] = None) -> dict:
    """Return an empty result structure."""
    result = {
        "suggestions": [],
        "synthesized_answer": None,
        "query_text": query_text,
        "total_results": 0,
    }
    if error:
        result["error"] = error
    return result
