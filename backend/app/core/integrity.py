import hashlib
from pathlib import Path
from typing import Any

from app.config import settings
from app.core.errors import ModelIntegrityError


def calculate_file_sha256(file_path: Path | str, chunk_size: int = 65536) -> str:
    """
    Deterministically compute the SHA-256 digest of a local artifact file.
    Streams in binary chunks for memory efficiency.
    Rejects directories with a controlled error.
    """
    path = Path(file_path)
    if path.is_dir():
        raise ModelIntegrityError(
            "Configured artifact path is a directory. Directory integrity hashing is not supported."
        )
    if not path.exists():
        raise ModelIntegrityError("Artifact file not found for integrity verification.")

    hasher = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    return hasher.hexdigest().lower()


def verify_artifact_integrity(
    artifact_key: str,
    file_path: Path | str,
    expected_hash: str,
) -> dict[str, Any]:
    """
    Verify a local model or artifact file against its configured expected SHA-256 hash.
    Raises ModelIntegrityError on mismatch or missing file.
    Never exposes absolute filesystem paths in exceptions or outputs.
    """
    if not expected_hash or not expected_hash.strip():
        raise ModelIntegrityError(
            f"Expected SHA-256 hash is empty for artifact '{artifact_key}'."
        )

    path = Path(file_path)
    if not path.exists():
        raise ModelIntegrityError(
            f"Model artifact '{artifact_key}' is missing from local storage. "
            "Automatic downloads are strictly prohibited in air-gapped sovereign mode."
        )
    if path.is_dir():
        raise ModelIntegrityError(
            f"Model artifact '{artifact_key}' points to a directory. "
            "Directory integrity verification is prohibited; configure individual artifact files."
        )

    calculated = calculate_file_sha256(path)
    clean_expected = expected_hash.strip().lower()

    if calculated != clean_expected:
        raise ModelIntegrityError(
            f"Integrity verification failed for model artifact '{artifact_key}': "
            "SHA-256 digest mismatch."
        )

    return {
        "status": "verified",
        "artifact_key": artifact_key,
    }


def check_configured_model_integrity() -> dict[str, Any]:
    """
    Inspect all configured model/artifact integrity specifications.
    Returns safe status dictionary suitable for health probes.
    Never exposes secrets, expected hashes, or filesystem paths.
    """
    expected_hashes = settings.parsed_integrity_hashes
    paths = settings.parsed_integrity_paths

    if not expected_hashes:
        return {
            "status": "not_configured",
        }

    for key, expected_hash in expected_hashes.items():
        if key not in paths:
            return {
                "status": "failed",
                "failed_artifact": key,
            }
        target_path = Path(paths[key])
        if not target_path.exists():
            return {
                "status": "missing",
                "failed_artifact": key,
            }
        if target_path.is_dir():
            return {
                "status": "failed",
                "failed_artifact": key,
            }
        try:
            calculated = calculate_file_sha256(target_path)
            if calculated != expected_hash.strip().lower():
                return {
                    "status": "failed",
                    "failed_artifact": key,
                }
        except Exception:
            return {
                "status": "failed",
                "failed_artifact": key,
            }

    return {
        "status": "verified",
        "verified_count": len(expected_hashes),
    }


def enforce_configured_model_integrity() -> None:
    """
    Strictly enforce configured model artifact hashes on boot.
    Raises ModelIntegrityError if any configured model fails verification.
    """
    expected_hashes = settings.parsed_integrity_hashes
    paths = settings.parsed_integrity_paths

    if not expected_hashes:
        return

    for key, expected_hash in expected_hashes.items():
        if key not in paths:
            raise ModelIntegrityError(
                f"Missing path configuration for model artifact '{key}'."
            )
        verify_artifact_integrity(
            artifact_key=key,
            file_path=paths[key],
            expected_hash=expected_hash,
        )

