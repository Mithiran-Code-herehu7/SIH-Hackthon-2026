import logging
import re
from typing import Any
from app.rag.chunker import chunk_text_with_metadata
from app.rag.local_embeddings import LocalEmbeddingProvider
from app.rag.vector_store import VectorStore

logger = logging.getLogger(__name__)

embedding_provider = LocalEmbeddingProvider()
vector_store = VectorStore(embedding_provider=embedding_provider)

KNOWN_AREAS = [
    "Crude Transfer Area",
    "Tank Farm Corridor",
    "CDU-1",
    "Maintenance Workshop",
    "Utility Block",
]


def index_document(file_id: str, filename: str, text: str) -> int:
    chunk_items = chunk_text_with_metadata(text)
    if not chunk_items:
        return 0
    metadata: list[dict[str, Any]] = [
        {
            "document_id": file_id,
            "file_id": file_id,
            "filename": filename,
            "chunk_id": f"{file_id}_chunk_{index}",
            "chunk_index": index,
            "section": item.get("section", "Overview"),
            "ids": item.get("ids", []),
            "content_type": item.get("content_type", "evidence"),
            "page": None,
            "text": item["text"],
        }
        for index, item in enumerate(chunk_items)
    ]
    vector_store.add(texts=[item["text"] for item in chunk_items], metadata=metadata)
    return len(chunk_items)


def search_documents(
    query: str,
    top_k: int = 5,
    file_id: str | None = None,
    min_similarity: float = 0.0,
) -> list[dict[str, Any]]:
    """
    Search FAISS vector store. For multi-entity or comparison queries,
    split retrieval into area subqueries, merge results, remove duplicates, and rerank.
    """
    if vector_store.index.ntotal == 0:
        logger.warning(
            "Retrieval failed | reason='FAISS index is empty (ntotal=0)' query='%s' file_id=%s",
            query,
            file_id,
        )
        return []

    q_lower = query.lower()
    mentioned_areas: list[str] = []
    for area in KNOWN_AREAS:
        area_clean = area.lower()
        if area_clean in q_lower or area_clean.replace("-", " ") in q_lower or area_clean.replace(" ", "") in q_lower:
            mentioned_areas.append(area)

    is_comparison = "compare" in q_lower or "comparison" in q_lower or len(mentioned_areas) >= 2

    if is_comparison and mentioned_areas:
        effective_top_k = max(top_k, 12)
        all_candidates: list[dict[str, Any]] = []
        seen_chunk_ids: set[str] = set()

        # 1. Primary query search
        main_results = vector_store.search(query=query, top_k=effective_top_k, file_id=file_id, min_similarity=min_similarity)
        for c in main_results:
            cid = str(c.get("chunk_id") or c.get("text"))
            if cid not in seen_chunk_ids:
                seen_chunk_ids.add(cid)
                all_candidates.append(c)

        # 2. Subquery search for each area entity
        for area in mentioned_areas:
            subquery = f"{area} safety operational incidents risks"
            sub_results = vector_store.search(query=subquery, top_k=6, file_id=file_id, min_similarity=min_similarity)
            for c in sub_results:
                cid = str(c.get("chunk_id") or c.get("text"))
                if cid not in seen_chunk_ids:
                    seen_chunk_ids.add(cid)
                    all_candidates.append(c)

        all_candidates.sort(key=lambda item: (-item.get("score", 0), str(item.get("file_id", "")), item.get("chunk_index", -1)))
        results = all_candidates[:effective_top_k]
    else:
        results = vector_store.search(query=query, top_k=top_k, file_id=file_id, min_similarity=min_similarity)

    if not results:
        logger.warning(
            "Retrieval returned 0 chunks | query='%s' min_similarity=%s index_total=%s",
            query,
            min_similarity,
            vector_store.index.ntotal,
        )
    else:
        logger.info(
            "Retrieval success | query='%s' retrieved_count=%d index_total=%d",
            query,
            len(results),
            vector_store.index.ntotal,
        )

    return results


def delete_document(file_id: str) -> int:
    return vector_store.delete_by_file_id(file_id=file_id)


def get_vector_store() -> VectorStore:
    return vector_store


def get_rag_status() -> dict[str, Any]:
    """Return live status of active vector store index and indexed documents."""
    docs = sorted(list({str(m.get("filename", m.get("file_id", "unknown"))) for m in vector_store.metadata}))
    return {
        "index_path": str(vector_store.index_path.resolve()),
        "total_chunks": vector_store.index.ntotal,
        "indexed_documents_count": len(docs),
        "indexed_documents": docs,
    }
