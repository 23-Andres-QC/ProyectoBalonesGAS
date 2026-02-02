from fastapi import APIRouter, FastAPI

from app.infrastructure.config.settings import get_settings
from app.presentation.http.routes.frame_routes import router as frame_router
from app.presentation.http.routes.health_routes import router as health_router
from app.presentation.http.routes.metrics_routes import router as metrics_router
from app.presentation.http.routes.line_routes import router as line_router

settings = get_settings()

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

api_router = APIRouter(prefix="/api")
api_router.include_router(frame_router)
api_router.include_router(health_router)
api_router.include_router(metrics_router)
api_router.include_router(line_router)
app.include_router(api_router)
