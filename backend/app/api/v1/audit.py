import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import verify_audit_chain
from app.core.rbac import UserContext, require_permission
from app.storage.database import get_db
from app.storage.models import AuditLog


router = APIRouter()


@router.get("/verify/chain")
async def verify_chain_endpoint(
    db: AsyncSession = Depends(get_db),
    user: UserContext = Depends(require_permission("audit:verify")),
):
    """
    Cryptographically verify the integrity of the sovereign audit trail.
    Enforces that no logs have been tampered with, deleted, or injected out of sequence.
    """
    verification = await verify_audit_chain(db)
    return verification


@router.get("/{request_id}")
async def get_audit_logs(
    request_id: str,
    db: AsyncSession = Depends(get_db),
    user: UserContext = Depends(require_permission("audit:read")),
):
    result = await db.execute(
        select(AuditLog)
        .where(AuditLog.request_id == request_id)
        .order_by(AuditLog.created_at.asc())
    )

    logs = result.scalars().all()

    if not logs:
        raise HTTPException(
            status_code=404,
            detail="Audit record not found",
        )

    return {
        "request_id": request_id,
        "events": [
            {
                "action": log.action,
                "status": log.status,
                "prev_hash": log.prev_hash,
                "record_hash": log.record_hash,
                "details": (
                    json.loads(log.details)
                    if log.details
                    else None
                ),
                "created_at": log.created_at,
            }
            for log in logs
        ],
    }
