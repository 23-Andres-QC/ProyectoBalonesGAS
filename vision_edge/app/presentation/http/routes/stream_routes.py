"""
MJPEG streaming endpoints (HU-VIS-07).
"""
import time
from typing import Generator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.application.ports.frame_store import FrameStore
from app.infrastructure.config.settings import Settings


def create_stream_router(frame_store: FrameStore, settings: Settings) -> APIRouter:
    """
    Create router for MJPEG streaming endpoints.
    
    Args:
        frame_store: FrameStore implementation
        settings: Settings with stream_fps configuration
    
    Returns:
        APIRouter with /stream/raw.mjpg and /stream/processed.mjpg
    """
    router = APIRouter(prefix="/stream", tags=["stream"])
    
    def generate_mjpeg_stream(use_processed: bool) -> Generator[bytes, None, None]:
        """
        Generate MJPEG stream from frame store.
        
        Args:
            use_processed: If True, stream processed frames; else raw frames
        
        Yields:
            MJPEG frame chunks with multipart boundary
        """
        frame_interval = 1.0 / settings.stream_fps
        
        try:
            while True:
                start_time = time.time()
                
                # Get frames from store
                raw_jpeg, processed_jpeg = frame_store.get_frames()
                
                # Select frame based on stream type
                jpeg_bytes = processed_jpeg if use_processed else raw_jpeg
                
                # If frame not available, wait and retry
                if jpeg_bytes is None:
                    time.sleep(0.05)
                    continue
                
                # Yield MJPEG frame chunk
                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n"
                    f"Content-Length: {len(jpeg_bytes)}\r\n\r\n".encode()
                    + jpeg_bytes
                    + b"\r\n"
                )
                
                # Throttle to target FPS
                elapsed = time.time() - start_time
                sleep_time = max(0, frame_interval - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    
        except GeneratorExit:
            # Client disconnected gracefully
            pass
        except Exception:
            # Handle other errors (broken pipe, etc.)
            pass
    
    @router.get("/raw.mjpg")
    async def stream_raw():
        """
        Stream raw RTSP frames as MJPEG (HU-VIS-07).
        
        Returns:
            StreamingResponse with multipart/x-mixed-replace content
        """
        return StreamingResponse(
            generate_mjpeg_stream(use_processed=False),
            media_type="multipart/x-mixed-replace; boundary=frame",
            headers={
                "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
                "Pragma": "no-cache",
                "Connection": "close",
            },
        )
    
    @router.get("/processed.mjpg")
    async def stream_processed():
        """
        Stream processed frames (with detections and overlays) as MJPEG (HU-VIS-07).
        
        Returns:
            StreamingResponse with multipart/x-mixed-replace content
        """
        return StreamingResponse(
            generate_mjpeg_stream(use_processed=True),
            media_type="multipart/x-mixed-replace; boundary=frame",
            headers={
                "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
                "Pragma": "no-cache",
                "Connection": "close",
            },
        )
    
    return router
