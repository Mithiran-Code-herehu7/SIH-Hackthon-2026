from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.rag.service import search_documents
from app.storage.models import Document


def document_search(query: str, top_k: int = 5, file_id: str | None = None) -> list[dict[str, Any]]:
    """Search the local FAISS knowledge base, optionally within one document."""
    if not isinstance(query, str) or not query.strip():
        return []
    return search_documents(query=query, top_k=top_k, file_id=file_id)


async def document_metadata(db: AsyncSession, file_id: str) -> dict[str, Any]:
    result = await db.execute(select(Document).where(Document.file_id == file_id))
    document = result.scalar_one_or_none()
    if document is None:
        return {"found": False, "file_id": file_id}
    return {
        "found": True,
        "file_id": document.file_id,
        "filename": document.filename,
        "content_type": document.content_type,
        "size_bytes": document.size_bytes,
        "created_at": document.created_at,
    }
