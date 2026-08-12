from fastapi import APIRouter

from hengwen_api import __version__

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "hengwen-api",
        "version": __version__,
    }
