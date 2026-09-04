import base64
import json
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

from app.core.security import validate_outbound_url
from app.multimodal.base import MultimodalProvider
from app.multimodal.errors import MultimodalCapabilityError


class OllamaMultimodalProvider(MultimodalProvider):
    def __init__(self, model: str, base_url: str = "http://localhost:11434") -> None:
        self.base_url = base_url.rstrip("/")
        validate_outbound_url(self.base_url)
        self.model = model

    @property
    def identifier(self) -> str:
        return f"ollama:{self.model}"

    def analyze_image(self, image_path: Path, prompt: str | None = None) -> dict[str, Any]:
        image_bytes = image_path.read_bytes()
        payload = {
            "model": self.model,
            "prompt": prompt or (
                "Describe only what is visually observable. Separate observations, "
                "uncertainties, and safety-relevant warnings. Do not present inferences as facts."
            ),
            "images": [base64.b64encode(image_bytes).decode("ascii")],
            "stream": False,
        }
        request = Request(
            f"{self.base_url}/api/generate",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=120) as response:
                data = json.loads(response.read().decode("utf-8"))
        except (URLError, TimeoutError, OSError) as exc:
            raise MultimodalCapabilityError(
                "Local vision model is unavailable. Confirm Ollama is running and the configured vision model is installed."
            ) from exc
        description = str(data.get("response", "")).strip()
        if not description:
            raise MultimodalCapabilityError("Local vision model returned no analysis.")
        return {
            "description": description,
            "observations": [],
            "warnings": ["Visual interpretation is not a verified engineering assessment."],
            "confidence": "model_reported_unspecified",
            "provider": self.identifier,
        }
