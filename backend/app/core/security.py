import ipaddress
from pathlib import Path
import re
from urllib.parse import urlparse

from app.config import settings
from app.core.errors import AirGappedSecurityViolation, SecurityValidationError

_SENSITIVE_PATTERNS = [
    (re.compile(r"sk-[a-zA-Z0-9_\-]{16,}", re.IGNORECASE), "[REDACTED_API_KEY]"),
    (re.compile(r"Bearer\s+[a-zA-Z0-9\-._~+/]+=*", re.IGNORECASE), "Bearer [REDACTED_TOKEN]"),
    (re.compile(r"(?i)(password|passwd|pwd|secret|api[_-]?key)\s*[:=]\s*['\"]?([^'\"\s,]+)['\"]?"), r"\1: [REDACTED]"),
    (re.compile(r"-----BEGIN [A-Z ]+ PRIVATE KEY-----[\s\S]*?-----END [A-Z ]+ PRIVATE KEY-----"), "[REDACTED_PRIVATE_KEY]"),
    (re.compile(r"([?&](?:api_key|key|token|access_token|password)=)[^&\s]+", re.IGNORECASE), r"\1[REDACTED]"),
]


def redact_sensitive_text(text: str | None) -> str:
    """Scrub sensitive credentials, keys, and tokens from error messages and logs."""
    if not text:
        return ""
    redacted = str(text)
    for pattern, replacement in _SENSITIVE_PATTERNS:
        redacted = pattern.sub(replacement, redacted)
    return redacted


def validate_outbound_url(url: str) -> None:
    """
    Enforce strict air-gapped sovereignty.
    When air_gapped_mode is enabled, outbound network calls are strictly restricted
    to verified local loopback hosts and approved ports. External domains/IPs are blocked.
    """
    if not settings.air_gapped_mode:
        return

    parsed = urlparse(url)
    scheme = (parsed.scheme or "").lower()
    if scheme not in {"http", "https"}:
        raise AirGappedSecurityViolation(
            f"Unsupported outbound protocol '{scheme}' in air-gapped sovereign mode."
        )

    hostname = (parsed.hostname or "").strip().lower()
    if not hostname:
        raise AirGappedSecurityViolation("Invalid URL: missing hostname.")

    clean_host = hostname.strip("[]")

    is_allowed = False
    if clean_host in [h.lower() for h in settings.allowed_local_hosts]:
        is_allowed = True
    else:
        try:
            ip = ipaddress.ip_address(clean_host)
            if ip.is_loopback:
                is_allowed = True
        except ValueError:
            is_allowed = False

    if not is_allowed:
        redacted = redact_sensitive_text(url)
        raise AirGappedSecurityViolation(
            f"External outbound request to '{clean_host}' is strictly prohibited in air-gapped mode: {redacted}"
        )

    if parsed.port and settings.allowed_local_ports:
        if parsed.port not in settings.allowed_local_ports:
            raise AirGappedSecurityViolation(
                f"Outbound connection to unapproved local port '{parsed.port}' is prohibited in air-gapped mode."
            )


def sanitize_filename(filename: str) -> str:
    """
    Sanitize uploaded filenames to defend against path traversal, control characters,
    and injection into local filesystems.
    """
    if not filename:
        return "unnamed_document"

    clean = filename.replace("\x00", "")
    clean = clean.split("\\")[-1].split("/")[-1]
    clean = re.sub(r"^[a-zA-Z]:", "", clean)
    clean = clean.replace("..", "")
    clean = re.sub(r"[^\w\.\-\s]", "_", clean)
    clean = clean.strip(" .\t\r\n")

    if not clean:
        return "unnamed_document"

    return clean


def validate_path_containment(target_path: Path | str, base_dir: Path) -> Path:
    """
    Ensure the target path resolves strictly within the approved base directory boundary.
    """
    base = base_dir.resolve()
    target = Path(target_path)
    if not target.is_absolute():
        target = (base / target).resolve()
    else:
        target = target.resolve()

    try:
        target.relative_to(base)
    except ValueError:
        raise SecurityValidationError("Path traversal detected: target path is outside authorized boundary.")

    return target


def safe_path(base_dir: Path, user_path: str) -> Path:
    """
    Backward-compatible safe path resolver that raises ValueError on traversal.
    """
    base = base_dir.resolve()
    target = (base / user_path).resolve()

    try:
        target.relative_to(base)
    except ValueError:
        raise ValueError("Path traversal detected")

    return target

