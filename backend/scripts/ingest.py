"""
Knowledge base ingestion script.

Loads all markdown documents from backend/knowledge_base/, generates
embeddings with sentence-transformers, and stores them in ChromaDB.

Run from the backend/ directory with the venv active:

    python -m scripts.ingest

Optional flags:
    --rebuild     Wipe the existing ChromaDB collection first, then re-index
                  (use this if you edited any knowledge base documents)

Exit codes:
    0 — success
    1 — failure (check the error message printed above)
"""

import sys
import os
import argparse
import time

# Make sure app/ is importable when run as  python -m scripts.ingest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main() -> int:
    parser = argparse.ArgumentParser(description="Index the RAG knowledge base into ChromaDB.")
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Wipe the existing ChromaDB collection before re-indexing.",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("  Mikano RAG Knowledge Base Indexer")
    print("=" * 60)

    # ── 1. Verify knowledge base directory exists and has files ──
    print("\n[1/5] Checking knowledge base directory...")
    try:
        from app.ai.config import KNOWLEDGE_BASE_DIR, CHROMA_PERSIST_DIR, COLLECTION_NAME, EMBEDDING_MODEL_NAME
    except Exception as e:
        print(f"  ERROR: Could not load AI config: {e}")
        print("  Make sure you are running from the backend/ directory with the venv active.")
        return 1

    if not KNOWLEDGE_BASE_DIR.exists():
        print(f"  ERROR: Knowledge base directory not found at: {KNOWLEDGE_BASE_DIR}")
        return 1

    md_files = list(KNOWLEDGE_BASE_DIR.rglob("*.md"))
    if not md_files:
        print(f"  ERROR: No .md files found in {KNOWLEDGE_BASE_DIR}")
        return 1

    print(f"  OK — found {len(md_files)} markdown file(s):")
    for f in sorted(md_files):
        print(f"       {f.relative_to(KNOWLEDGE_BASE_DIR)}")

    # ── 2. Load and chunk the documents ─────────────────────────
    print("\n[2/5] Loading and chunking documents...")
    try:
        from app.ai.document_loader import load_knowledge_base
        chunks = load_knowledge_base()
    except Exception as e:
        print(f"  ERROR: Document loading failed: {e}")
        return 1

    if not chunks:
        print("  ERROR: No chunks were produced. Check that the markdown files have content.")
        return 1

    print(f"  OK — produced {len(chunks)} chunk(s) across {len(md_files)} file(s)")

    # ── 3. Load the embedding model ──────────────────────────────
    print(f"\n[3/5] Loading embedding model: {EMBEDDING_MODEL_NAME}")
    print("  (This downloads ~90 MB on first run — may take a minute...)")
    try:
        t0 = time.time()
        from app.ai.embeddings import embed_texts
        # Warm up with a test sentence to trigger the download now
        test_vec = embed_texts(["test"])
        elapsed = time.time() - t0
        if not test_vec or not test_vec[0]:
            print("  ERROR: Embedding model returned an empty vector.")
            return 1
        print(f"  OK — model loaded in {elapsed:.1f}s, vector dimensions: {len(test_vec[0])}")
    except ImportError:
        print("  ERROR: sentence-transformers is not installed.")
        print("  Fix:  pip install sentence-transformers")
        return 1
    except Exception as e:
        print(f"  ERROR: Failed to load embedding model: {e}")
        return 1

    # ── 4. Optionally wipe existing collection ───────────────────
    if args.rebuild:
        print(f"\n[4/5] Rebuilding — wiping existing collection '{COLLECTION_NAME}'...")
        try:
            from app.ai.vector_store import reset_collection
            reset_collection()
            print("  OK — collection wiped.")
        except Exception as e:
            print(f"  ERROR: Could not reset collection: {e}")
            return 1
    else:
        print(f"\n[4/5] Skipping wipe (run with --rebuild to start fresh)")

    # ── 5. Generate embeddings and store in ChromaDB ─────────────
    print(f"\n[5/5] Embedding {len(chunks)} chunks and writing to ChromaDB...")
    print(f"      Storage path: {CHROMA_PERSIST_DIR}")

    try:
        t0 = time.time()
        contents = [chunk.content for chunk in chunks]
        batch_size = 64
        all_embeddings: list[list[float]] = []

        for i in range(0, len(contents), batch_size):
            batch = contents[i : i + batch_size]
            batch_embeddings = embed_texts(batch)
            all_embeddings.extend(batch_embeddings)
            batches_total = (len(contents) + batch_size - 1) // batch_size
            current_batch = i // batch_size + 1
            print(f"      Embedded batch {current_batch}/{batches_total} "
                  f"({min(i + batch_size, len(contents))}/{len(contents)} chunks)")

        from app.ai.vector_store import add_documents, get_collection_stats
        add_documents(
            ids=[c.chunk_id for c in chunks],
            documents=contents,
            embeddings=all_embeddings,
            metadatas=[c.metadata for c in chunks],
        )

        elapsed = time.time() - t0
        stats = get_collection_stats()

        print(f"\n{'=' * 60}")
        print(f"  SUCCESS — Knowledge base indexed in {elapsed:.1f}s")
        print(f"  Collection : {stats['collection_name']}")
        print(f"  Total chunks in DB : {stats['total_chunks']}")
        print(f"  Storage : {stats['persist_directory']}")
        print(f"{'=' * 60}")
        print("\n  You can now use the AI Suggestion Panel in the frontend.")
        print("  Restart the backend (uvicorn) if it is currently running.\n")

    except Exception as e:
        print(f"\n  ERROR: Indexing failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
