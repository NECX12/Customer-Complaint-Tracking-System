"""
AI endpoints — RAG-powered resolution suggestions, knowledge base management.

Endpoints:
  GET  /api/v1/ai/suggestions/{complaint_id}  — AGENT/ADMIN — get AI suggestions
  POST /api/v1/ai/ingest                       — ADMIN — trigger re-indexing
  GET  /api/v1/ai/status                       — ADMIN — knowledge base stats
"""

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import require_role
from app.db.session import get_db
from app.db.models.user import User, UserRole
from app.db.models.complaint import Complaint
from app.db.models.complaint_history import ComplaintStatusHistory
from app.schemas.ai import (
    AiSuggestionResponse,
    SuggestionItem,
    KnowledgeBaseStatus,
    IngestResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/suggestions/{complaint_id}",
    response_model=AiSuggestionResponse,
    summary="Get AI-powered resolution suggestions for a complaint",
)
def get_ai_suggestions(
    complaint_id: uuid.UUID,
    current_user: User = Depends(require_role(UserRole.AGENT, UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    """
    Query the RAG knowledge base for resolution suggestions relevant
    to the specified complaint.

    Returns the top-5 most similar documents from the knowledge base
    and past resolved complaints, ranked by relevance.
    """
    # Fetch the complaint
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Complaint not found",
        )

    try:
        from app.ai.rag_engine import get_suggestions

        result = get_suggestions(
            complaint_title=complaint.title,
            complaint_description=complaint.description,
        )

        # Map to response schema
        suggestions = [
            SuggestionItem(
                id=s["id"],
                content=s["content"],
                source=s["source"],
                source_type=s["source_type"],
                similarity_score=s["similarity_score"],
                category=s["category"],
                section=s.get("section", ""),
            )
            for s in result.get("suggestions", [])
        ]

        return AiSuggestionResponse(
            suggestions=suggestions,
            synthesized_answer=result.get("synthesized_answer"),
            query_text=result.get("query_text", ""),
            total_results=result.get("total_results", 0),
            error=result.get("error"),
        )

    except ImportError as e:
        logger.error(f"AI dependencies not installed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI module dependencies not installed. Run: pip install chromadb sentence-transformers",
        )
    except Exception as e:
        logger.error(f"AI suggestion failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI suggestion failed: {str(e)}",
        )


@router.post(
    "/ingest",
    response_model=IngestResponse,
    summary="Trigger knowledge base re-indexing",
)
def trigger_ingest(
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """
    Re-index the entire knowledge base. Admin only.

    This will reload all markdown documents from the knowledge_base/
    directory and regenerate their embeddings in the vector store.
    """
    try:
        from app.ai.ingest import rebuild_index

        result = rebuild_index()

        kb_data = result.get("knowledge_base", {})
        return IngestResponse(
            status=result.get("status", "success"),
            chunks_ingested=kb_data.get("chunks_ingested", 0),
            source_files=kb_data.get("source_files", 0),
            indexed_at=kb_data.get("indexed_at"),
            message=result.get("message"),
        )

    except ImportError as e:
        logger.error(f"AI dependencies not installed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI module dependencies not installed. Run: pip install chromadb sentence-transformers",
        )
    except Exception as e:
        logger.error(f"Ingest failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ingestion failed: {str(e)}",
        )


@router.get(
    "/status",
    response_model=KnowledgeBaseStatus,
    summary="Get knowledge base status and statistics",
)
def get_kb_status(
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """
    Return the current status of the RAG knowledge base including
    document count, collection info, and last indexed timestamp.
    """
    try:
        from app.ai.ingest import get_index_status

        status_data = get_index_status()

        return KnowledgeBaseStatus(
            total_chunks=status_data.get("total_chunks", 0),
            collection_name=status_data.get("collection_name", ""),
            last_indexed_at=status_data.get("last_indexed_at"),
            persist_directory=status_data.get("persist_directory", ""),
        )

    except ImportError as e:
        logger.error(f"AI dependencies not installed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI module dependencies not installed",
        )
    except Exception as e:
        logger.error(f"Status check failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Status check failed: {str(e)}",
        )
