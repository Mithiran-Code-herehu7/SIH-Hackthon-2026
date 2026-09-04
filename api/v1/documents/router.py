import shutil
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.rbac import UserContext, require_permission
from app.core.security import validate_path_containment
from app.documents.extractor import extract_pdf_visuals, extract_text
from app.documents.schemas import DocumentResponse
from app.documents.service import save_document
from app.rag.service import delete_document as delete_rag_document
from app.rag.service import index_document, search_documents as rag_search_documents
from app.storage.database import get_db
from app.storage.models import Document

router = APIRouter()

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=10000)
    top_k: int = Field(5, ge=1, le=100)
    file_id: str | None = None

async def _is_duplicate(db: AsyncSession, filename: str, content: bytes) -> bool:
    result = await db.execute(select(Document).where(Document.filename == filename, Document.size_bytes == len(content)))
    for document in result.scalars():
        path = settings.data_dir / "vault" / f"{document.file_id}{Path(document.filename).suffix.lower()}"
        if path.exists() and path.read_bytes() == content:
            return True
    return False

@router.post("/ingest", response_model=DocumentResponse)
async def ingest_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user: UserContext = Depends(require_permission("document:ingest")),
):
    filename = file.filename or "unknown"
    content = await file.read()
    if not content:
        raise HTTPException(400, "Cannot ingest an empty document.")
    if len(content) > settings.max_document_size_bytes:
        raise HTTPException(400, f"File exceeds maximum allowed size of {settings.max_document_size_bytes} bytes.")
    if await _is_duplicate(db, filename, content):
        raise HTTPException(409, "This document has already been ingested.")
    try:
        document = save_document(filename, content, file.content_type or "application/octet-stream")
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc

    extension = Path(filename).suffix.lower()
    vault_path = settings.data_dir / "vault" / f"{document.file_id}{extension}"
    extracted_path = settings.data_dir / "extracted" / f"{document.file_id}.txt"
    visuals_path = settings.data_dir / "visuals" / document.file_id
    visual_artifacts: list[dict[str, str | int]] = []
    try:
        extracted_text = extract_text(vault_path).strip()
        if not extracted_text:
            raise ValueError("No extractable text was found in this document.")
        extracted_path.parent.mkdir(parents=True, exist_ok=True)
        extracted_path.write_text(extracted_text, encoding="utf-8")
        chunk_count = index_document(document.file_id, document.filename, extracted_text)
        if chunk_count == 0:
            raise ValueError("Document did not produce any searchable content.")
        if extension == ".pdf":
            visual_artifacts = extract_pdf_visuals(vault_path, document.file_id)
        db.add(Document(file_id=document.file_id, filename=document.filename, content_type=document.content_type, size_bytes=document.size_bytes, created_at=document.uploaded_at))
        await db.commit()
    except Exception as exc:
        delete_rag_document(document.file_id)
        for path in (vault_path, extracted_path):
            if path.exists():
                path.unlink()
        if visuals_path.exists():
            shutil.rmtree(visuals_path)
        await db.rollback()
        raise HTTPException(422, f"Document ingestion failed: {exc}") from exc
    return DocumentResponse(**document.model_dump(), status=f"processed:{chunk_count}_chunks;{len(visual_artifacts)}_visuals")

@router.post("/search")
async def search_documents(
    request: SearchRequest,
    user: UserContext = Depends(require_permission("document:search")),
):
    return {"query": request.query, "results": rag_search_documents(request.query, request.top_k, file_id=request.file_id)}

@router.get("")
async def list_documents(
    db: AsyncSession = Depends(get_db),
    user: UserContext = Depends(require_permission("document:read")),
):
    result = await db.execute(select(Document).order_by(Document.created_at.desc()))
    return {"documents": [{"file_id": d.file_id, "filename": d.filename, "content_type": d.content_type, "size_bytes": d.size_bytes, "created_at": d.created_at} for d in result.scalars().all()]}

@router.get("/{file_id}/download")
async def download_document(
    file_id: str,
    db: AsyncSession = Depends(get_db),
    user: UserContext = Depends(require_permission("document:read")),
):
    if ".." in file_id or "/" in file_id or "\\" in file_id:
        raise HTTPException(400, "Invalid file identifier.")
    document = (await db.execute(select(Document).where(Document.file_id == file_id))).scalar_one_or_none()
    if document is None:
        raise HTTPException(404, "Document not found")
    vault_dir = (settings.data_dir / "vault").resolve()
    raw_path = vault_dir / f"{document.file_id}{Path(document.filename).suffix.lower()}"
    try:
        path = validate_path_containment(raw_path, vault_dir)
    except Exception:
        raise HTTPException(400, "Security violation: file path escape detected.")
    if not path.exists():
        raise HTTPException(404, "Document file not found")
    return FileResponse(path=path, filename=document.filename, media_type=document.content_type)

@router.delete("/{file_id}")
async def delete_document(
    file_id: str,
    db: AsyncSession = Depends(get_db),
    user: UserContext = Depends(require_permission("document:delete")),
):
    if ".." in file_id or "/" in file_id or "\\" in file_id:
        raise HTTPException(400, "Invalid file identifier.")
    document = (await db.execute(select(Document).where(Document.file_id == file_id))).scalar_one_or_none()
    if document is None:
        raise HTTPException(404, "Document not found")
    deleted_chunks = delete_rag_document(file_id)
    for path in (settings.data_dir / "vault" / f"{file_id}{Path(document.filename).suffix.lower()}", settings.data_dir / "extracted" / f"{file_id}.txt"):
        if path.exists():
            path.unlink()
    visuals_path = settings.data_dir / "visuals" / file_id
    if visuals_path.exists():
        shutil.rmtree(visuals_path)
    await db.delete(document)
    await db.commit()
    return {"file_id": file_id, "status": "deleted", "deleted_chunks": deleted_chunks}

