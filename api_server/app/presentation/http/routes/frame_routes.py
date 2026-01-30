from fastapi import APIRouter, Response

from app.di.container import container

router = APIRouter()


@router.get("/frame/raw")
def get_raw_frame() -> Response:
    """
    Get latest raw frame.
    
    Uses DI container (HU06) to inject either:
    - MockFrameStore (when USE_VISION_EDGE=false)
    - VisionEdgeFrameAdapter (when USE_VISION_EDGE=true)
    
    Returns:
        JPEG image as bytes.
    """
    frame_bytes = container.get_latest_frame_use_case.execute("raw")
    return Response(
        content=frame_bytes,
        media_type="image/jpeg",
        headers={"Cache-Control": "no-store"},
    )


@router.get("/frame/processed")
def get_processed_frame() -> Response:
    """
    Get latest processed frame.
    
    Uses DI container (HU06) to inject either:
    - MockFrameStore (when USE_VISION_EDGE=false)
    - VisionEdgeFrameAdapter (when USE_VISION_EDGE=true)
    
    Returns:
        JPEG image as bytes.
    """
    frame_bytes = container.get_latest_frame_use_case.execute("processed")
    return Response(
        content=frame_bytes,
        media_type="image/jpeg",
        headers={"Cache-Control": "no-store"},
    )
