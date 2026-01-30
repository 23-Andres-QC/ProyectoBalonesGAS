from abc import ABC, abstractmethod
from typing import Any

from app.domain.entities.count_state import CountState


class Counter(ABC):
    """
    Counter port for object counting.
    
    Accepts detections (any object with __len__) and returns CountState
    with raw_count and stable_count.
    """

    @abstractmethod
    def update(self, detections: Any) -> CountState:
        """
        Update counter with new detections.
        
        Args:
            detections: Object with __len__ (e.g., sv.Detections, list, etc.)
        
        Returns:
            CountState with raw_count, stable_count, and history.
        """
        raise NotImplementedError
