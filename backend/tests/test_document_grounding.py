import pytest
from pathlib import Path
from app.rag.service import index_document, search_documents, get_vector_store
from app.api.v1.chat.router import generate_structured_response
from app.rag.vector_store import VectorStore
from app.rag.local_embeddings import LocalEmbeddingProvider


def test_document_grounding_and_p204b_query():
    # 1. Prepare MRPL_Operations_Safety_Demo_Pack text content
    content = """
# MRPL Refinery Operations & Safety Demo Pack

## 2.2 Key operating parameters
Pump P-204B vibration average: 5.8 mm/s RMS. Normal operating threshold: below 4.5 mm/s RMS. Warning threshold crossed for 3rd time in 4 weeks.

## 3.1 Incident and near-miss register
- INC-01: Minor hydrocarbon seepage observed at Pump P-204B flange seal.
- INC-07: Vibration warning alarm triggered on Pump P-204B suction loop.
- INC-13: Vibration sensor calibration overdue by 12 days for Unit 4B.

## 4.1 Pump P-204B recurring vibration
Pump P-204B is considered a critical priority due to recurring vibration levels (5.8 mm/s RMS vs 4.5 mm/s threshold). If left unresolved, risks include seal degradation, hydrocarbon leakage, unplanned unit shutdown, or escalation near ignition sources.

## 6 Corrective action plan
- CAP-01: Calibrate vibration sensor by 08 Sep 2026.
- CAP-02: Inspect pump alignment, bearings, and seal condition by 12 Sep 2026.
    """.strip()

    file_id = "test-doc-mrpl-01"
    filename = "MRPL_Operations_Safety_Demo_Pack.md"

    # 2. Ingest document and confirm chunks_created > 0
    chunks_created = index_document(file_id=file_id, filename=filename, text=content)
    assert chunks_created > 0, "Ingestion must produce at least one chunk"

    # 3. Query Pump P-204B
    query = "Why is Pump P-204B considered a critical priority? Give the evidence, risk, and recommended actions."
    retrieved_chunks = search_documents(query=query, top_k=5)
    assert len(retrieved_chunks) > 0, "Retrieval must return matching chunks"

    agent_result = {
        "intent": "document_question",
        "tool": "document_search",
        "reason": "Query about Pump P-204B",
        "sources": retrieved_chunks,
        "tool_result": None,
    }

    res = generate_structured_response(query=query, agent_result=agent_result, request_id="req_p204b_test")

    # 4. Confirm answer contains key facts
    answer = res["answer"]
    assert "Pump P-204B" in answer
    assert "5.8 mm/s RMS" in answer
    assert "4.5 mm/s RMS" in answer
    assert "INC-01" in answer or "hydrocarbon seepage" in answer
    assert "calibrate" in answer.lower() or "calibration" in answer.lower()
    assert "CAP-01" in answer or "CAP-02" in answer or "recommended actions" in answer.lower()

    # 5. Confirm sources are provided
    assert len(res["sources"]) > 0
    assert any("MRPL_Operations_Safety_Demo_Pack.md" in str(s.get("file") or s.get("filename")) for s in res["sources"])

    # 6. Query about a fact not in the document
    missing_query = "What is the monetary-loss figure for Pump P-204B?"
    agent_result_missing = {
        "intent": "document_question",
        "tool": "document_search",
        "reason": "Monetary loss query",
        "sources": [],
        "tool_result": None,
    }
    res_missing = generate_structured_response(query=missing_query, agent_result=agent_result_missing, request_id="req_missing_test")
    assert "does not provide a monetary-loss" in res_missing["answer"] or "No indexed evidence was found" in res_missing["answer"]
    assert len(res_missing["uncertainties"]) > 0

    # 7. Persistence check: Re-instantiate VectorStore from disk and confirm index still works
    reloaded_store = VectorStore(embedding_provider=LocalEmbeddingProvider())
    reloaded_results = reloaded_store.search(query=query, top_k=5)
    assert len(reloaded_results) > 0, "FAISS index must persist across process re-instantiation"
    assert any("P-204B" in r["text"] for r in reloaded_results)
