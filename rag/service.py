from app.rag.chunker import chunk_text
from app.rag.local_embeddings import LocalEmbeddingProvider
from app.rag.vector_store import VectorStore


embedding_provider = LocalEmbeddingProvider()
vector_store = VectorStore(embedding_provider=embedding_provider)


def index_document(file_id: str, filename: str, text: str) -> int:
    chunks = chunk_text(text)
    if not chunks:
        return 0
    metadata = [
        {"file_id": file_id, "filename": filename, "chunk_index": index, "text": chunk}
        for index, chunk in enumerate(chunks)
    ]
    vector_store.add(texts=chunks, metadata=metadata)
    return len(chunks)


def search_documents(
    query: str,
    top_k: int = 5,
    file_id: str | None = None,
    min_similarity: float = 0.0,
) -> list[dict]:
    return vector_store.search(query=query, top_k=top_k, file_id=file_id, min_similarity=min_similarity)


def delete_document(file_id: str) -> int:
    return vector_store.delete_by_file_id(file_id=file_id)


def get_vector_store() -> VectorStore:
    return vector_store

