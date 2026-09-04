from app.config import settings
from app.multimodal.base import MultimodalProvider
from app.multimodal.ollama import OllamaMultimodalProvider
from app.multimodal.unavailable import UnavailableMultimodalProvider


def get_multimodal_provider() -> MultimodalProvider:
    if settings.multimodal_provider == "ollama" and settings.vision_model:
        return OllamaMultimodalProvider(model=settings.vision_model)
    return UnavailableMultimodalProvider()
