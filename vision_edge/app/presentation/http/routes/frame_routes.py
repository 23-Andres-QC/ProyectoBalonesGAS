"""
Frame routes (HU-VIS-05).
"""
from fastapi import APIRouter, HTTPException, Response

from app.application.ports.frame_store import FrameStore


def create_frame_router(frame_store: FrameStore) -> APIRouter:
    """
    Create frame router.
    
    Args:
        frame_store: FrameStore implementation
    
    Returns:
        Configured router
    """
    router = APIRouter()
    
    @router.get("/frame/raw.jpg")
    def get_raw_frame():
        """
        Get latest raw frame as JPEG.
        
        Returns:
            JPEG image bytes.
        
        Raises:
            HTTPException: 404 if no frame available yet.
        """
        raw_jpeg, _ = frame_store.get_frames()
        if raw_jpeg is None:
            raise HTTPException(status_code=404, detail="No raw frame available yet")
        
        return Response(
            content=raw_jpeg,
            media_type="image/jpeg",
            headers={"Cache-Control": "no-store"},
        )
    
    @router.get("/frame/processed.jpg")
    def get_processed_frame():
        """
        Get latest processed frame as JPEG.
        
        Returns:
            JPEG image bytes with detections/count rendered.
        
        Raises:
            HTTPException: 404 if no frame available yet.
        """
        _, processed_jpeg = frame_store.get_frames()
        if processed_jpeg is None:
            raise HTTPException(status_code=404, detail="No processed frame available yet")
        
        return Response(
            content=processed_jpeg,
            media_type="image/jpeg",
            headers={"Cache-Control": "no-store"},
        )
    
    return router
