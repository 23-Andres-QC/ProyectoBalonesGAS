from typing import Literal, Optional

from app.application.ports.frame_store import FrameStorePort


class GetLatestFrame:
    """
    Use case: Get latest frame (raw or processed).
    
    Depends on FrameStorePort abstraction (DIP).
    """

    def __init__(self, frame_store: FrameStorePort) -> None:
        """
        Initialize use case with frame store dependency.
        
        Args:
            frame_store: Implementation of FrameStorePort.
        """
        self._frame_store = frame_store

    def execute(self, frame_type: Literal["raw", "processed"]) -> Optional[bytes]:
        """
        Execute use case to get latest frame.
        
        Args:
            frame_type: "raw" for raw frame, "processed" for processed frame.
        
        Returns:
            JPEG bytes or None if no frame available.
        """
        if frame_type == "raw":
            return self._frame_store.get_raw()
        elif frame_type == "processed":
            return self._frame_store.get_processed()
        else:
            return None