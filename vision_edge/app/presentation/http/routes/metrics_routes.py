"""
Metrics routes (HU-VIS-05).
"""
from fastapi import APIRouter, HTTPException

from app.application.ports.metrics_store import MetricsStore


def create_metrics_router(metrics_store: MetricsStore) -> APIRouter:
    """
    Create metrics router.
    
    Args:
        metrics_store: MetricsStore implementation
    
    Returns:
        Configured router
    """
    router = APIRouter()
    
    @router.get("/metrics")
    def get_metrics():
        """
        Get current pipeline metrics.
        
        Returns:
            Dict with fps, raw_count, stable_count, status, last_update_utc.
        
        Raises:
            HTTPException: 404 if no metrics available yet.
        """
        metrics = metrics_store.get_metrics()
        if metrics is None:
            raise HTTPException(status_code=404, detail="No metrics available yet")
        return metrics
    
    return router
