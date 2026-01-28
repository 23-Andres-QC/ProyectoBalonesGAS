from fastapi import APIRouter

from app.infrastructure.config.settings import get_settings

router = APIRouter()


@router.get("/health")
def health_check() -> dict:
    """Health check endpoint."""
    settings = get_settings()
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }
