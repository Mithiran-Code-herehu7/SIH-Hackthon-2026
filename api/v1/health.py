from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.audit import verify_audit_chain
from app.rag.service import get_vector_store
from app.storage.database import get_db


router = APIRouter()


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    # 1. Probe database
    db_status = "connected"
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        db_status = "unreachable"

    # 2. Probe vector store
    vector_store_status = "ready"
    total_vectors = 0
    try:
        vs = get_vector_store()
        total_vectors = int(vs.index.ntotal)
    except Exception:
        vector_store_status = "unavailable"

    # 3. Quick audit chain verification
    audit_chain_status = "verified_authentic"
    try:
        audit_res = await verify_audit_chain(db)
        if not audit_res.get("valid", False):
            audit_chain_status = "compromised"
    except Exception:
        audit_chain_status = "unverified"

    # 4. Model artifact integrity probe
    from app.core.integrity import check_configured_model_integrity
    integrity_res = check_configured_model_integrity()
    integrity_status = integrity_res.get("status", "not_configured")

    is_healthy = (
        db_status == "connected"
        and vector_store_status == "ready"
        and audit_chain_status != "compromised"
        and integrity_status not in {"failed", "missing"}
    )
    overall_status = "ok" if is_healthy else "degraded"

    return {
        "status": overall_status,
        "service": settings.app_name,
        "version": settings.app_version,
        "air_gapped_mode": settings.air_gapped_mode,
        "sovereignty_posture": "enforced_air_gapped" if settings.air_gapped_mode else "standard",
        "llm_provider": settings.llm_provider,
        "llm_model": settings.ollama_model if settings.llm_provider == "ollama" else "mock-engine",
        "embedding_provider": f"local_sentence_transformers ({settings.embedding_model})",
        "multimodal_provider": settings.multimodal_provider,
        "database_status": db_status,
        "vector_store_status": vector_store_status,
        "indexed_chunks": total_vectors,
        "audit_chain_status": audit_chain_status,
        "model_integrity": {
            "status": integrity_status,
        },
    }


