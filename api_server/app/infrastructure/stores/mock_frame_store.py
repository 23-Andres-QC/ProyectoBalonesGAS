from typing import Optional

from app.infrastructure.stores.placeholder_jpeg import get_placeholder_jpeg


class MockFrameStore:
    """
    Mock implementation of FrameStorePort.
    
    Returns placeholder JPEG for both raw and processed frames.
    Will be replaced by VisionEdgeFrameAdapter in HU06.
    """

    def get_raw(self) -> Optional[bytes]:
        """
        Get mock raw frame.
        
        Returns:
            Placeholder JPEG bytes.
        """
        return get_placeholder_jpeg()

    def get_processed(self) -> Optional[bytes]:
        """
        Get mock processed frame.
        
        Returns:
            Placeholder JPEG bytes (same as raw for mock).
        """
        return get_placeholder_jpeg()
