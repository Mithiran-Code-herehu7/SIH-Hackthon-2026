from app.config import settings
from app.llm.base import LLMProvider
from app.llm.mock import MockLLMProvider
from app.llm.ollama import OllamaLLMProvider


def get_llm_provider() -> LLMProvider:
    if settings.llm_provider == "ollama":
        return OllamaLLMProvider(
            model=settings.ollama_model,
            base_url=settings.ollama_base_url,
        )

    return MockLLMProvider()