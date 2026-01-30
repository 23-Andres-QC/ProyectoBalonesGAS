from abc import ABC, abstractmethod
from typing import Any


class LineCounter(ABC):
    """
    Port for line crossing counter (HU-VIS-06).
    
    Counts unique detections crossing a horizontal line.
    Independent of specific tracking/detection implementations.
    """

    @abstractmethod
    def update(self, detections: Any, frame_width: int, frame_height: int) -> dict:
        """
        Update line crossing counter with new detections.
        
        Args:
            detections: Detection objects (supervision.Detections or similar with tracker_id)
            frame_width: Frame width in pixels
            frame_height: Frame height in pixels
        
        Returns:
            Dict with keys:
                - line_in: int (objects crossing line downward)
                - line_out: int (objects crossing line upward)
                - line_total: int (total crossings, line_in + line_out)
        """
        raise NotImplementedError

    @abstractmethod
    def get_line_y(self) -> int:
        """
        Get current line Y position.
        
        Returns:
            Y coordinate of horizontal line.
        """
        raise NotImplementedError
