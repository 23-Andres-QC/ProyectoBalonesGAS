from abc import ABC, abstractmethod
from typing import Any

import numpy as np

from app.domain.entities.count_state import CountState


class Renderer(ABC):
    """
    Renderer port for annotating frames with detections and count.
    
    Receives BGR frame, detections, and count state.
    Returns processed frame as numpy array (BGR).
    """

    @abstractmethod
    def render(
        self,
        frame: np.ndarray,
        detections: Any,
        count_state: CountState,
    ) -> np.ndarray:
        """
        Render detections and count on frame.
        
        Args:
            frame: BGR frame (numpy array)
            detections: Detections object (e.g., sv.Detections)
            count_state: CountState with raw_count and stable_count
        
        Returns:
            Processed frame (numpy array BGR) with annotations.
        """
        raise NotImplementedError
