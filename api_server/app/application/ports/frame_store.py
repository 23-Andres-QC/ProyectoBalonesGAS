from typing import Optional, Protocol


class FrameStorePort(Protocol):
    """
    Port (interface) for frame storage.
    
    Allows retrieving raw and processed frames without knowing
    the underlying implementation (mock, vision_edge, redis, etc.).
    """

    def get_raw(self) -> Optional[bytes]:
        """
        Get latest raw frame as JPEG bytes.
        
        Returns:
            JPEG bytes or None if no frame available.
        """
        ...

    def get_processed(self) -> Optional[bytes]:
        """
        Get latest processed frame as JPEG bytes.
        
        Returns:
            JPEG bytes or None if no frame available.
        """
        ...