import json
from urllib.error import URLError
from urllib.request import Request, urlopen

from app.core.errors import ModelAvailabilityError
from app.core.security import validate_outbound_url
from app.llm.base import LLMProvider


class OllamaLLMProvider(LLMProvider):
    def __init__(
        self,
        model: str = "qwen3:8b",
        base_url: str = "http://localhost:11434",
    ):
        self.base_url = base_url.rstrip("/")
        validate_outbound_url(self.base_url)
        self.model = model

    def check_availability(self) -> bool:
        """
        Verify that the local Ollama instance is accessible and that the
        specified model is already present locally. Prohibits auto-download.
        """
        validate_outbound_url(self.base_url)
        request = Request(
            f"{self.base_url}/api/tags",
            headers={"Content-Type": "application/json"},
            method="GET",
        )
        try:
            with urlopen(request, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))
        except (URLError, TimeoutError, OSError) as exc:
            raise ModelAvailabilityError(
                f"Local Ollama server is unreachable at {self.base_url}. "
                "Ensure local Ollama service is active."
            ) from exc

        models = data.get("models", [])
        installed_names = [m.get("name", "").lower() for m in models]
        target = self.model.lower()
        target_base = target.split(":")[0]

        has_model = any(
            target == name or name.startswith(f"{target}:") or name.startswith(f"{target_base}:")
            for name in installed_names
        )

        if not has_model:
            raise ModelAvailabilityError(
                f"Local model '{self.model}' is not installed in Ollama. "
                "In air-gapped sovereign mode, automatic downloading is prohibited. "
                f"Install the model locally via 'ollama pull {self.model}'."
            )

        return True

    def generate(self, prompt: str) -> str:
        validate_outbound_url(self.base_url)
        payload = json.dumps({
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }).encode("utf-8")

        request = Request(
            f"{self.base_url}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urlopen(request, timeout=120) as response:
                data = json.loads(
                    response.read().decode("utf-8")
                )
        except (URLError, TimeoutError, OSError) as exc:
            raise ModelAvailabilityError(
                "Unable to connect to local Ollama server. "
                "Make sure Ollama is running."
            ) from exc

        return data["response"].strip()
