import os
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Enforce offline Hugging Face / Transformers operation in sovereign mode
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("HF_DATASETS_OFFLINE", "1")


class Settings(BaseSettings):
    app_name: str = "Sovereign AI Workbench"
    app_version: str = "0.1.0"
    debug: bool = False

    # Air-Gapped Sovereignty and Network Security
    air_gapped_mode: bool = True
    allowed_local_hosts: list[str] = ["localhost", "127.0.0.1", "::1"]
    allowed_local_ports: list[int] = [11434, 8000, 8080, 5173, 3000, 8081]
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen3:8b"

    # API and Documentation Controls
    enable_docs: bool = True

    # Security & File Limits
    max_document_size_bytes: int = 50 * 1024 * 1024  # 50 MiB
    max_image_size_bytes: int = 10 * 1024 * 1024  # 10 MiB

    # RBAC & Audit Settings
    enforce_rbac: bool = True
    default_user_role: str = "ENGINEER"
    audit_secret_key: str = "sovereign-audit-secret-mrpl-2026"

    # Model Artifact Integrity Verification Settings
    model_integrity_paths: str = ""
    model_integrity_hashes: str = ""


    @field_validator("debug", "air_gapped_mode", "enable_docs", "enforce_rbac", mode="before")
    @classmethod
    def parse_bools(cls, v: object) -> bool:
        if isinstance(v, bool):
            return v
        if isinstance(v, (int, float)):
            return bool(v)
        if isinstance(v, str):
            return v.strip().lower() in {"true", "1", "yes", "on", "t", "y", "debug"}
        return False

    frontend_origins: str = (
        "http://localhost:3000,"
        "http://localhost:5173,"
        "http://127.0.0.1:3000,"
        "http://127.0.0.1:5173"
    )

    data_dir: Path = Path("./data")
    llm_provider: str = "mock"
    multimodal_provider: str = "ollama"
    vision_model: str | None = None
    embedding_model: str = "all-MiniLM-L6-v2"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def frontend_origin_list(self) -> list[str]:
        return [
            item.strip()
            for item in self.frontend_origins.split(",")
            if item.strip()
        ]

    @property
    def db_dir(self) -> Path:
        return self.data_dir / "db"

    @property
    def database_url(self) -> str:
        return f"sqlite+aiosqlite:///{self.db_dir / 'workbench.db'}"

    @property
    def parsed_integrity_paths(self) -> dict[str, str]:
        return self._parse_dict_config(self.model_integrity_paths)

    @property
    def parsed_integrity_hashes(self) -> dict[str, str]:
        return self._parse_dict_config(self.model_integrity_hashes)

    @staticmethod
    def _parse_dict_config(val: str | dict[str, str]) -> dict[str, str]:
        if isinstance(val, dict):
            return val
        if not val or not str(val).strip():
            return {}
        val_str = str(val).strip()
        if val_str.startswith("{"):
            try:
                import json
                return json.loads(val_str)
            except Exception:
                pass
        result = {}
        for item in val_str.split(","):
            if "=" in item:
                k, v = item.split("=", 1)
                result[k.strip()] = v.strip()
        return result



settings = Settings()

