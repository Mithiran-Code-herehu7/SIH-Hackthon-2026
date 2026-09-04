from sentence_transformers import SentenceTransformer
import numpy as np

from app.rag.embeddings import EmbeddingProvider


class LocalEmbeddingProvider(EmbeddingProvider):
    """
    Local semantic embedding provider using an open-weight
    SentenceTransformer model.
    """

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
    ):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    @property
    def dimension(self) -> int:
        return self.model.get_embedding_dimension()

    def embed(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.empty(
                (0, self.dimension),
                dtype=np.float32,
            )

        vectors = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )

        return vectors.astype(np.float32)