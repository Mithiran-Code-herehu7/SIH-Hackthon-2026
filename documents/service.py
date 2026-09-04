from datetime import datetime
from pathlib import Path
from uuid import uuid4

from app.config import settings
from app.core.security import sanitize_filename, validate_path_containment
from app.documents.schemas import DocumentMetadata


ALLOWED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".xlsx",
    ".pptx",
    ".txt",
}


def save_document(
    filename: str,
    content: bytes,
    content_type: str,
) -> DocumentMetadata:
    if not content:
        raise ValueError("Cannot ingest an empty document.")

    if len(content) > settings.max_document_size_bytes:
        raise ValueError(
            f"Document exceeds maximum authorized size limit of {settings.max_document_size_bytes} bytes."
        )

    clean_filename = sanitize_filename(filename)
    extension = Path(clean_filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type: {extension or 'unknown'}"
        )

    file_id = str(uuid4())

    vault_dir = (settings.data_dir / "vault").resolve()
    vault_dir.mkdir(parents=True, exist_ok=True)

    safe_vault_filename = f"{file_id}{extension}"
    file_path = validate_path_containment(vault_dir / safe_vault_filename, vault_dir)

    file_path.write_bytes(content)

    return DocumentMetadata(
        file_id=file_id,
        filename=clean_filename,
        content_type=content_type,
        size_bytes=len(content),
        uploaded_at=datetime.fromtimestamp(file_path.stat().st_mtime),
    )
