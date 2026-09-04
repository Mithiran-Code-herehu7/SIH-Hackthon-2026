from fastapi import APIRouter

from app.api.v1.audit import router as audit_router
from app.api.v1.chat.router import router as chat_router
from app.api.v1.documents.router import router as documents_router
from app.api.v1.health import router as health_router
from app.api.v1.images import router as images_router


router = APIRouter(prefix="/api/v1")
router.include_router(health_router)
router.include_router(chat_router)
router.include_router(documents_router, prefix="/documents")
router.include_router(audit_router, prefix="/audit")
router.include_router(images_router)
