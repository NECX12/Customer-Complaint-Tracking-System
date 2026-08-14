from app.ai.config import AI_PROVIDER, GEMINI_API_KEY, LLM_MODEL
from app.ai.rag_engine import get_suggestions


def test_gemini_defaults_are_configured_for_ai_layer():
    assert AI_PROVIDER == "gemini"
    assert LLM_MODEL.startswith("gemini-")


def test_get_suggestions_returns_retrieval_results_without_llm(monkeypatch):
    monkeypatch.setattr("app.ai.rag_engine.embed_single", lambda _query: [0.1, 0.2, 0.3])
    monkeypatch.setattr(
        "app.ai.rag_engine.query_similar",
        lambda query_embedding, n_results, where_filter=None: {
            "ids": [["doc-1"]],
            "documents": [["Example repair guidance for generator failures"]],
            "metadatas": [[{"source_type": "knowledge_base", "source_file": "generator.md", "category": "Power System"}]],
            "distances": [[0.12]],
        },
    )
    monkeypatch.setattr("app.ai.rag_engine.GEMINI_API_KEY", None)

    result = get_suggestions("Generator won't start", "Battery was replaced but engine still fails to crank.")

    assert result["total_results"] == 1
    assert result["suggestions"][0]["source"] == "generator.md"
    assert result["synthesized_answer"] is None
