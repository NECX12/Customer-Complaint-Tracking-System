"""
Embedding generation wrapper.

Loads the sentence-transformers model once (singleton pattern) and
exposes a simple function for generating embeddings from text.

The model (~90 MB) is downloaded automatically on first use and cached
locally by sentence-transformers.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Singleton holder — model is loaded lazily on first call
_model: Optional[object] = None


def _get_model():
    """Lazy-load the SentenceTransformer model (singleton)."""
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            from app.ai.config import EMBEDDING_MODEL_NAME

            logger.info(f"Loading embedding model: {EMBEDDING_MODEL_NAME}")
            _model = SentenceTransformer(EMBEDDING_MODEL_NAME)
            logger.info("Embedding model loaded successfully")
        except ImportError:
            logger.error(
                "sentence-transformers not installed. "
                "Run: pip install sentence-transformers"
            )
            raise
    return _model


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings for a list of text strings.

    Args:
        texts: list of strings to embed.

    Returns:
        List of embedding vectors (each is a list of floats).
    """
    if not texts:
        return []

    model = _get_model()
    embeddings = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
    return embeddings.tolist()


def embed_single(text: str) -> list[float]:
    """Generate an embedding for a single text string."""
    result = embed_texts([text])
    return result[0] if result else []
