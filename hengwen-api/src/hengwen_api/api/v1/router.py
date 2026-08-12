from fastapi import APIRouter

from hengwen_api.api.v1.documents import router as documents_router
from hengwen_api.api.v1.health import router as health_router

router = APIRouter(prefix="/api/v1")
router.include_router(health_router)
router.include_router(documents_router)
