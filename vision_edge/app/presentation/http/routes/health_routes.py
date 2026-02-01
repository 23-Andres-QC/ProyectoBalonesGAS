"""
Health check routes (HU-VIS-05).
"""
from fastapi import APIRouter


def create_health_router(service_name: str, version: str) -> APIRouter:
    """
    Create health check router.
    
    Args:
        service_name: Service identifier
        version: API version
    
    Returns:
        Configured router
    """
    router = APIRouter()
    
    @router.get("/health")
    def get_health():
        """
        Health check endpoint.
        
        Returns:
            Dict with status, service name, and version.
        """
        return {
            "status": "ok",
            "service": service_name,
            "version": version,
        }
    
    return router
