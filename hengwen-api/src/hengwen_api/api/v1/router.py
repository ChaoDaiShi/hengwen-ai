from fastapi import APIRouter

from hengwen_api.api.v1.documents import router as documents_router
from hengwen_api.api.v1.health import router as health_router
from hengwen_api.api.v1.reports import router as reports_router
from hengwen_api.api.v1.review_tasks import router as review_tasks_router

router = APIRouter(prefix="/api/v1")
router.include_router(health_router)
router.include_router(documents_router)
router.include_router(review_tasks_router)
router.include_router(reports_router)
