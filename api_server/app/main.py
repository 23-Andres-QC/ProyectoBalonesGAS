from fastapi import APIRouter, FastAPI

from app.infrastructure.config.settings import get_settings
from app.presentation.http.routes.health_routes import router as health_router

settings = get_settings()

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

api_router = APIRouter(prefix="/api")
api_router.include_router(health_router)
app.include_router(api_router)
