"""
Document loader and chunker for the knowledge base.

Loads markdown files from the knowledge_base/ directory, splits them
into semantic chunks (by ## headers first, then by paragraph if too long),
and returns structured chunks with metadata for embedding.
"""

import hashlib
import logging
from pathlib import Path
from typing import NamedTuple

from app.ai.config import KNOWLEDGE_BASE_DIR, CHUNK_MAX_CHARS, CHUNK_OVERLAP_CHARS

logger = logging.getLogger(__name__)


class DocumentChunk(NamedTuple):
    """A single chunk of a document ready for embedding."""
    chunk_id: str       # Unique ID (hash of content + metadata)
    content: str        # The text content
    metadata: dict      # source_type, source_file, section, chunk_index, category


def _generate_chunk_id(source_file: str, chunk_index: int, content: str) -> str:
    """Generate a deterministic unique ID for a chunk."""
    raw = f"{source_file}::{chunk_index}::{content[:100]}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _split_by_headers(text: str) -> list[tuple[str, str]]:
    """
    Split a markdown document by ## headers.

    Returns a list of (section_title, section_content) tuples.
    """
    sections: list[tuple[str, str]] = []
    current_title = "Introduction"
    current_lines: list[str] = []

    for line in text.split("\n"):
        if line.startswith("## "):
            # Save previous section
            if current_lines:
                content = "\n".join(current_lines).strip()
                if content:
                    sections.append((current_title, content))
            current_title = line.lstrip("#").strip()
            current_lines = []
        else:
            current_lines.append(line)

    # Save the last section
    if current_lines:
        content = "\n".join(current_lines).strip()
        if content:
            sections.append((current_title, content))

    return sections


def _split_long_section(
    section_content: str,
    max_chars: int = CHUNK_MAX_CHARS,
    overlap_chars: int = CHUNK_OVERLAP_CHARS,
) -> list[str]:
    """
    Split a long section into smaller chunks at paragraph boundaries.

    Respects paragraph boundaries when possible, with character overlap
    between chunks for context continuity.
    """
    if len(section_content) <= max_chars:
        return [section_content]

    paragraphs = section_content.split("\n\n")
    chunks: list[str] = []
    current_chunk: list[str] = []
    current_length = 0

    for para in paragraphs:
        para_length = len(para)

        if current_length + para_length > max_chars and current_chunk:
            # Save the current chunk
            chunks.append("\n\n".join(current_chunk))
            # Keep the last paragraph as overlap
            if overlap_chars > 0 and current_chunk:
                last_para = current_chunk[-1]
                if len(last_para) <= overlap_chars:
                    current_chunk = [last_para]
                    current_length = len(last_para)
                else:
                    current_chunk = []
                    current_length = 0
            else:
                current_chunk = []
                current_length = 0

        current_chunk.append(para)
        current_length += para_length

    if current_chunk:
        chunks.append("\n\n".join(current_chunk))

    return chunks


def _get_category_from_path(file_path: Path) -> str:
    """Derive a human-readable category from the file's parent directory."""
    parent = file_path.parent.name
    categories = {
        "products": "Product Documentation",
        "troubleshooting": "Troubleshooting Guide",
        "policies": "Policy & Procedure",
        "maintenance": "Maintenance Guide",
        "faq": "FAQ",
    }
    return categories.get(parent, "General")


def load_knowledge_base() -> list[DocumentChunk]:
    """
    Load all markdown files from the knowledge base directory
    and return a list of document chunks ready for embedding.
    """
    if not KNOWLEDGE_BASE_DIR.exists():
        logger.warning(f"Knowledge base directory not found: {KNOWLEDGE_BASE_DIR}")
        return []

    all_chunks: list[DocumentChunk] = []
    md_files = sorted(KNOWLEDGE_BASE_DIR.rglob("*.md"))

    logger.info(f"Found {len(md_files)} markdown files in knowledge base")

    for file_path in md_files:
        try:
            text = file_path.read_text(encoding="utf-8")
            relative_path = file_path.relative_to(KNOWLEDGE_BASE_DIR)
            category = _get_category_from_path(file_path)

            # Split by headers
            sections = _split_by_headers(text)

            chunk_index = 0
            for section_title, section_content in sections:
                # Split long sections further
                sub_chunks = _split_long_section(section_content)

                for sub_chunk in sub_chunks:
                    if len(sub_chunk.strip()) < 50:
                        continue  # Skip very short chunks

                    chunk_id = _generate_chunk_id(str(relative_path), chunk_index, sub_chunk)

                    all_chunks.append(DocumentChunk(
                        chunk_id=f"kb_{chunk_id}",
                        content=f"{section_title}\n\n{sub_chunk}",
                        metadata={
                            "source_type": "knowledge_base",
                            "source_file": str(relative_path),
                            "section": section_title,
                            "chunk_index": chunk_index,
                            "category": category,
                        },
                    ))
                    chunk_index += 1

            logger.info(f"  Loaded {chunk_index} chunks from {relative_path}")

        except Exception as e:
            logger.error(f"Failed to load {file_path}: {e}")

    logger.info(f"Total knowledge base chunks: {len(all_chunks)}")
    return all_chunks


def create_complaint_chunk(
    complaint_id: str,
    title: str,
    description: str,
    resolution_comments: list[str],
) -> DocumentChunk:
    """
    Create a document chunk from a resolved complaint.

    Combines the complaint title, description, and resolution comments
    into a single searchable chunk.
    """
    parts = [
        f"Complaint: {title}",
        f"\nDescription: {description}",
    ]
    if resolution_comments:
        parts.append("\nResolution:")
        for comment in resolution_comments:
            parts.append(f"- {comment}")

    content = "\n".join(parts)
    chunk_id = _generate_chunk_id(f"complaint_{complaint_id}", 0, content)

    return DocumentChunk(
        chunk_id=f"complaint_{chunk_id}",
        content=content,
        metadata={
            "source_type": "resolved_complaint",
            "complaint_id": complaint_id,
            "title": title,
            "category": "Past Resolution",
        },
    )
