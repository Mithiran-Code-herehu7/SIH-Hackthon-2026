from pathlib import Path
from typing import Any

from app.multimodal.base import MultimodalProvider
from app.multimodal.errors import MultimodalCapabilityError


class UnavailableMultimodalProvider(MultimodalProvider):
    """Safe default when no local vision model has been configured."""

    @property
    def identifier(self) -> str:
        return "unavailable"

    def analyze_image(self, image_path: Path, prompt: str | None = None) -> dict[str, Any]:
        raise MultimodalCapabilityError(
            "Local visual analysis is unavailable. Configure an installed local Ollama vision model to enable it."
        )
