import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import log_audit
from app.core.rbac import UserContext, require_permission
from app.documents.visuals import save_image
from app.multimodal.errors import MultimodalCapabilityError
from app.tools import registry
from app.storage.database import get_db


router = APIRouter(prefix="/images")


class ImageAnalysisRequest(BaseModel):
    image_id: str = Field(..., min_length=1, max_length=512)
    prompt: str | None = Field(None, max_length=2000)


@router.post("/ingest")
async def ingest_image(
    file: UploadFile = File(...),
    user: UserContext = Depends(require_permission("image:ingest")),
):
    try:
        return save_image(file.filename or "unknown", await file.read(), file.content_type)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/analyze")
async def analyze_image(
    request: ImageAnalysisRequest,
    db: AsyncSession = Depends(get_db),
    user: UserContext = Depends(require_permission("image:analyze")),
):
    if ".." in request.image_id or "\\" in request.image_id:
        raise HTTPException(status_code=400, detail="Path traversal in image_id is prohibited.")
    request_id = str(uuid.uuid4())
    try:
        result = registry.execute("image_analysis", image_ref=request.image_id, prompt=request.prompt)
        await log_audit(
            db=db, request_id=request_id, action="image_analysis", status="success",
            details={"tool": "image_analysis", "image_id": request.image_id, "provider": result.get("provider")},
        )
        return {"request_id": request_id, "status": "success", "result": result}
    except (ValueError, MultimodalCapabilityError) as exc:
        await log_audit(
            db=db, request_id=request_id, action="image_analysis", status="failed",
            details={"tool": "image_analysis", "image_id": request.image_id, "failure": str(exc)},
        )
        raise HTTPException(status_code=503 if isinstance(exc, MultimodalCapabilityError) else 400, detail=str(exc)) from exc

