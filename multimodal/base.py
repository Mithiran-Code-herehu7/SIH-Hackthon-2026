from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class MultimodalProvider(ABC):
    """Local-only interface for optional visual analysis providers."""

    @property
    @abstractmethod
    def identifier(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def analyze_image(self, image_path: Path, prompt: str | None = None) -> dict[str, Any]:
        raise NotImplementedError

    def analyze_document_visual(self, image_path: Path, prompt: str | None = None) -> dict[str, Any]:
        return self.analyze_image(image_path, prompt)
