"""
FastAPI application factory (HU-VIS-05, HU-VIS-07).
"""
from fastapi import FastAPI

from app.application.ports.frame_store import FrameStore
from app.application.ports.metrics_store import MetricsStore
from app.infrastructure.config.settings import Settings
from app.presentation.http.routes.frame_routes import create_frame_router
from app.presentation.http.routes.health_routes import create_health_router
from app.presentation.http.routes.metrics_routes import create_metrics_router
from app.presentation.http.routes.stream_routes import create_stream_router


def create_app(
    service_name: str,
    version: str,
    frame_store: FrameStore,
    metrics_store: MetricsStore,
    settings: Settings,
) -> FastAPI:
    """
    Create FastAPI application with all routes.
    
    Args:
        service_name: Service identifier (e.g., "vision_edge")
        version: API version (e.g., "0.1.0")
        frame_store: FrameStore implementation
        metrics_store: MetricsStore implementation
        settings: Settings with stream_fps configuration (HU-VIS-07)
    
    Returns:
        Configured FastAPI app
    """
    app = FastAPI(
        title=service_name,
        version=version,
        description="Vision Edge HTTP Service (HU-VIS-05, HU-VIS-07)",
    )
    
    # Register routers
    app.include_router(create_health_router(service_name, version))
    app.include_router(create_metrics_router(metrics_store))
    app.include_router(create_frame_router(frame_store))
    app.include_router(create_stream_router(frame_store, settings))  # HU-VIS-07
    
    return app
