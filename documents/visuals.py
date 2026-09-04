from datetime import datetime
from pathlib import Path
from uuid import uuid4

from app.config import settings
from app.core.security import sanitize_filename


ALLOWED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
CONTENT_TYPES = {
    ".png": {"image/png"},
    ".jpg": {"image/jpeg"},
    ".jpeg": {"image/jpeg"},
    ".webp": {"image/webp"},
}


def _has_valid_signature(content: bytes, extension: str) -> bool:
    if extension == ".png":
        return content.startswith(b"\x89PNG\r\n\x1a\n")
    if extension in {".jpg", ".jpeg"}:
        return content.startswith(b"\xff\xd8\xff")
    if extension == ".webp":
        return len(content) >= 12 and content[:4] == b"RIFF" and content[8:12] == b"WEBP"
    return False


def save_image(filename: str, content: bytes, content_type: str | None = None) -> dict[str, str | int]:
    clean_filename = sanitize_filename(filename)
    extension = Path(clean_filename).suffix.lower()
    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValueError("Unsupported image type.")
    if not content or len(content) > settings.max_image_size_bytes:
        raise ValueError(f"Image must be non-empty and no larger than {settings.max_image_size_bytes // (1024 * 1024)} MiB.")
    if content_type and content_type != "application/octet-stream" and content_type.lower() not in CONTENT_TYPES[extension]:
        raise ValueError("Image content type does not match its extension.")
    if not _has_valid_signature(content, extension):
        raise ValueError("Image content is malformed or does not match its extension.")

    image_id = f"images/{uuid4()}{extension}"
    path = resolve_image_reference(image_id, require_exists=False)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return {
        "image_id": image_id,
        "filename": clean_filename,
        "content_type": content_type or CONTENT_TYPES[extension].copy().pop(),
        "size_bytes": len(content),
        "created_at": datetime.fromtimestamp(path.stat().st_mtime).isoformat(),
    }


def resolve_image_reference(image_ref: str, require_exists: bool = True) -> Path:
    if not isinstance(image_ref, str) or not image_ref.strip():
        raise ValueError("An image reference is required.")
    relative = Path(image_ref)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError("Image reference must stay inside the approved data directory.")
    root = settings.data_dir.resolve()
    path = (root / relative).resolve()
    if not path.is_relative_to(root) or path.suffix.lower() not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValueError("Image reference is not an approved image artifact.")
    if require_exists and (not path.exists() or not path.is_file()):
        raise ValueError("Image artifact was not found.")
    return path
