from fastapi import APIRouter

from app.di.container import container
from app.presentation.http.schemas.metrics_dto import MetricsDTO

router = APIRouter()


@router.get("/metrics", response_model=MetricsDTO)
def get_metrics() -> MetricsDTO:
    """
    Get current metrics.
    
    Uses DI container (HU06) to inject either:
    - MockMetricsStore (when USE_VISION_EDGE=false)
    - VisionEdgeMetricsAdapter (when USE_VISION_EDGE=true)
    
    Returns:
        MetricsDTO with count, fps, status, last_update.
    """
    metrics_dict = container.get_metrics_use_case.execute()
    return MetricsDTO(**metrics_dict)
