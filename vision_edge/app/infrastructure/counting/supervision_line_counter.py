from typing import Any

import numpy as np
import supervision as sv

from app.application.ports.line_counter import LineCounter


class SupervisionLineCounter(LineCounter):
    """
    Line crossing counter using supervision.LineZone (HU-VIS-06).
    
    Counts unique tracked objects crossing a horizontal line.
    Requires detections with tracker_id attribute (from ByteTrack or similar).
    
    Graceful degradation: if detections lack tracker_id, returns zeros.
    """

    def __init__(self, line_y: int) -> None:
        """
        Initialize line counter.
        
        Args:
            line_y: Y coordinate for horizontal counting line.
        """
        self._line_y = line_y
        self._line_zone: sv.LineZone | None = None
        self._line_in = 0
        self._line_out = 0
        self._last_frame_shape = (0, 0)

    def update(self, detections: Any, frame_width: int, frame_height: int) -> dict:
        """
        Update line counter with tracked detections.
        
        Args:
            detections: supervision.Detections with tracker_id attribute
            frame_width: Frame width
            frame_height: Frame height
        
        Returns:
            Dict with line_in, line_out, line_total counts.
        """
        # Reinitialize LineZone if frame dimensions changed
        if (frame_width, frame_height) != self._last_frame_shape:
            self._initialize_line_zone(frame_width, frame_height)
            self._last_frame_shape = (frame_width, frame_height)

        # Check if detections have tracker_id (required for line crossing)
        if not hasattr(detections, 'tracker_id') or detections.tracker_id is None:
            # No tracking available - return current counts without update
            return {
                "line_in": self._line_in,
                "line_out": self._line_out,
                "line_total": self._line_in + self._line_out,
            }

        # Filter out detections without valid tracker_id
        valid_mask = detections.tracker_id >= 0
        if not np.any(valid_mask):
            return {
                "line_in": self._line_in,
                "line_out": self._line_out,
                "line_total": self._line_in + self._line_out,
            }

        # Trigger line zone with valid tracked detections
        crossed_in, crossed_out = self._line_zone.trigger(detections)
        
        # Update accumulated counts
        self._line_in += crossed_in
        self._line_out += crossed_out

        return {
            "line_in": self._line_in,
            "line_out": self._line_out,
            "line_total": self._line_in + self._line_out,
        }

    def get_line_y(self) -> int:
        """Get line Y position."""
        return self._line_y

    def _initialize_line_zone(self, frame_width: int, frame_height: int) -> None:
        """
        Initialize LineZone with current frame dimensions.
        
        Args:
            frame_width: Frame width
            frame_height: Frame height
        """
        # Clamp line_y to frame bounds
        line_y = max(0, min(self._line_y, frame_height - 1))
        
        # Create horizontal line from left to right
        start = sv.Point(x=0, y=line_y)
        end = sv.Point(x=frame_width - 1, y=line_y)
        
        self._line_zone = sv.LineZone(
            start=start,
            end=end,
            triggering_anchors=(sv.Position.CENTER,)
        )
