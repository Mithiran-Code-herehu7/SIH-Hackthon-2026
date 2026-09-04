from datetime import datetime
import hashlib
import hmac
import json
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.storage.models import AuditLog


def compute_audit_hash(
    prev_hash: str | None,
    request_id: str,
    action: str,
    status: str,
    details_str: str | None,
    created_at_iso: str,
) -> str:
    """Compute an HMAC-SHA256 digest over the canonical audit log fields."""
    canonical_payload = (
        f"{prev_hash or 'GENESIS'}|"
        f"{request_id}|"
        f"{action}|"
        f"{status}|"
        f"{details_str or ''}|"
        f"{created_at_iso}"
    )
    secret = settings.audit_secret_key.encode("utf-8")
    return hmac.new(
        secret,
        canonical_payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


async def log_audit(
    db: AsyncSession,
    request_id: str,
    action: str,
    status: str,
    details: dict[str, Any] | None = None,
) -> AuditLog:
    """
    Append an audit log record with cryptographic chaining to ensure tamper evidence.
    """
    # Find the previous log's record_hash to maintain the linear hash chain
    last_record_result = await db.execute(
        select(AuditLog).order_by(AuditLog.id.desc()).limit(1)
    )
    last_record = last_record_result.scalar_one_or_none()
    prev_hash = last_record.record_hash if (last_record and last_record.record_hash) else "GENESIS"

    details_str = (
        json.dumps(details, ensure_ascii=False)
        if details is not None
        else None
    )
    created_at = datetime.utcnow()
    created_at_iso = created_at.isoformat()

    record_hash = compute_audit_hash(
        prev_hash=prev_hash,
        request_id=request_id,
        action=action,
        status=status,
        details_str=details_str,
        created_at_iso=created_at_iso,
    )

    audit_log = AuditLog(
        request_id=request_id,
        action=action,
        status=status,
        details=details_str,
        prev_hash=prev_hash,
        record_hash=record_hash,
        created_at=created_at,
    )

    db.add(audit_log)
    await db.commit()
    await db.refresh(audit_log)

    return audit_log


async def verify_audit_chain(db: AsyncSession) -> dict[str, Any]:
    """
    Cryptographically verify the integrity of the audit log chain.
    Detects any unauthorized modification, deletion, or reordering of records.
    """
    result = await db.execute(
        select(AuditLog).order_by(AuditLog.id.asc())
    )
    records = list(result.scalars().all())

    if not records:
        return {
            "valid": True,
            "total_records": 0,
            "verified_records": 0,
            "tampered_ids": [],
            "status": "empty_chain",
        }

    expected_prev = "GENESIS"
    verified_count = 0
    tampered_ids: list[int] = []

    for record in records:
        # If legacy records without hashes exist, handle gracefully
        if not record.record_hash:
            continue

        if record.prev_hash != expected_prev:
            tampered_ids.append(record.id)
            return {
                "valid": False,
                "total_records": len(records),
                "verified_records": verified_count,
                "tampered_ids": tampered_ids,
                "error": f"Chain broken at record ID {record.id}: prev_hash mismatch. Expected {expected_prev}, found {record.prev_hash}",
            }

        recalculated_hash = compute_audit_hash(
            prev_hash=record.prev_hash,
            request_id=record.request_id,
            action=record.action,
            status=record.status,
            details_str=record.details,
            created_at_iso=record.created_at.isoformat(),
        )

        if recalculated_hash != record.record_hash:
            tampered_ids.append(record.id)
            return {
                "valid": False,
                "total_records": len(records),
                "verified_records": verified_count,
                "tampered_ids": tampered_ids,
                "error": f"Content tampering detected at record ID {record.id}: hash mismatch.",
            }

        expected_prev = record.record_hash
        verified_count += 1

    return {
        "valid": True,
        "total_records": len(records),
        "verified_records": verified_count,
        "tampered_ids": [],
        "status": "verified_authentic",
    }
