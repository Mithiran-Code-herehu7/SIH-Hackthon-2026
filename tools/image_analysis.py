from pathlib import Path
from typing import Any

from app.documents.visuals import ALLOWED_IMAGE_EXTENSIONS, resolve_image_reference
from app.multimodal.errors import MultimodalCapabilityError
from app.multimodal.provider import get_multimodal_provider


def image_analysis(image_ref: str, prompt: str | None = None) -> dict[str, Any]:
    """Analyze only an approved local image artifact through the local provider."""
    image_path = resolve_image_reference(image_ref)
    try:
        result = get_multimodal_provider().analyze_image(image_path, prompt)
    except MultimodalCapabilityError:
        raise
    except OSError as exc:
        raise MultimodalCapabilityError("Unable to read the local image artifact.") from exc
    return {"image_id": image_ref, "artifact_name": image_path.name, **result}
