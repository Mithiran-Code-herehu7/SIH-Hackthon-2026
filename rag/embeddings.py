from abc import ABC, abstractmethod

import numpy as np


class EmbeddingProvider(ABC):
    @property
    @abstractmethod
    def dimension(self) -> int:
        """Return the embedding vector dimension."""
        raise NotImplementedError

    @abstractmethod
    def embed(self, texts: list[str]) -> np.ndarray:
        """Convert text into embedding vectors."""
        raise NotImplementedError