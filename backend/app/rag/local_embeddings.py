import hashlib
import numpy as np

from app.rag.embeddings import EmbeddingProvider

try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False


class LocalEmbeddingProvider(EmbeddingProvider):
    """
    Local semantic embedding provider using an open-weight
    SentenceTransformer model with lightweight deterministic hash-vector fallback.
    """

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
    ):
        self.model_name = model_name
        self.model = None
        if HAS_SENTENCE_TRANSFORMERS:
            try:
                self.model = SentenceTransformer(model_name)
            except Exception:
                self.model = None

    @property
    def dimension(self) -> int:
        if self.model is not None:
            try:
                return self.model.get_embedding_dimension()
            except Exception:
                pass
        return 384

    def embed(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.empty(
                (0, self.dimension),
                dtype=np.float32,
            )

        if self.model is not None:
            try:
                vectors = self.model.encode(
                    texts,
                    convert_to_numpy=True,
                    normalize_embeddings=True,
                    show_progress_bar=False,
                )
                return vectors.astype(np.float32)
            except Exception:
                pass

        # Robust lightweight deterministic hash-based normalized embedding fallback
        dim = self.dimension
        vectors = np.zeros((len(texts), dim), dtype=np.float32)
        for i, text in enumerate(texts):
            words = text.lower().split()
            for w in words:
                h = int(hashlib.md5(w.encode("utf-8")).hexdigest(), 16) % dim
                vectors[i, h] += 1.0
            norm = np.linalg.norm(vectors[i])
            if norm > 0:
                vectors[i] /= norm
        return vectors