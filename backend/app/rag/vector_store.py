import json
from typing import Any

import faiss

from app.config import settings
from app.rag.embeddings import EmbeddingProvider


class VectorStore:
    def __init__(self, embedding_provider: EmbeddingProvider) -> None:
        self.embedding_provider = embedding_provider
        self.index_dir = settings.data_dir / "faiss_index"
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self.index_path = self.index_dir / "documents.index"
        self.metadata_path = self.index_dir / "metadata.json"
        self.index = faiss.IndexFlatIP(embedding_provider.dimension)
        self.metadata: list[dict[str, Any]] = []
        self._load()

    def add(self, texts: list[str], metadata: list[dict[str, Any]]) -> None:
        if not texts:
            return
        if len(texts) != len(metadata):
            raise ValueError("texts and metadata must have the same length")
        vectors = self.embedding_provider.embed(texts)
        self.index.add(vectors)
        self.metadata.extend(metadata)
        self._save()

    def search(
        self,
        query: str,
        top_k: int = 5,
        file_id: str | None = None,
        min_similarity: float = 0.0,
    ) -> list[dict[str, Any]]:
        """Return deterministic positive-similarity matches, optionally for one file."""
        if not isinstance(query, str) or not query.strip() or self.index.ntotal == 0:
            return []
        if isinstance(top_k, bool) or not isinstance(top_k, int) or top_k <= 0:
            return []
        if not isinstance(min_similarity, (int, float)) or min_similarity < 0:
            raise ValueError("min_similarity must be a non-negative number")
        if len(self.metadata) != self.index.ntotal:
            raise RuntimeError("FAISS index and metadata are out of sync")

        query_vector = self.embedding_provider.embed([query])
        # Search all vectors before filtering so file-specific searches retain true top-k.
        scores, indices = self.index.search(query_vector, self.index.ntotal)
        candidates: list[dict[str, Any]] = []
        for score, index in zip(scores[0], indices[0]):
            if index < 0 or score <= 0 or score < min_similarity:
                continue
            item = self.metadata[int(index)]
            if file_id is not None and item.get("file_id") != file_id:
                continue
            candidates.append({**item, "score": float(score)})

        candidates.sort(key=lambda item: (-item["score"], str(item.get("file_id", "")), item.get("chunk_index", -1)))
        return candidates[:top_k]

    def delete_by_file_id(self, file_id: str) -> int:
        keep_indices = [index for index, item in enumerate(self.metadata) if item.get("file_id") != file_id]
        deleted_count = len(self.metadata) - len(keep_indices)
        if deleted_count == 0:
            return 0
        self.metadata = [self.metadata[index] for index in keep_indices]
        self.index = faiss.IndexFlatIP(self.embedding_provider.dimension)
        if self.metadata:
            self.index.add(self.embedding_provider.embed([item["text"] for item in self.metadata]))
        self._save()
        return deleted_count

    def _save(self) -> None:
        faiss.write_index(self.index, str(self.index_path))
        self.metadata_path.write_text(json.dumps(self.metadata, ensure_ascii=False, indent=2), encoding="utf-8")

    def _load(self) -> None:
        if not self.index_path.exists() or not self.metadata_path.exists():
            return
        loaded_index = faiss.read_index(str(self.index_path))
        if loaded_index.d != self.embedding_provider.dimension:
            raise ValueError("FAISS index dimension does not match the embedding provider")
        loaded_metadata = json.loads(self.metadata_path.read_text(encoding="utf-8"))
        if not isinstance(loaded_metadata, list) or len(loaded_metadata) != loaded_index.ntotal:
            raise ValueError("FAISS index and metadata are out of sync")
        self.index = loaded_index
        self.metadata = loaded_metadata
