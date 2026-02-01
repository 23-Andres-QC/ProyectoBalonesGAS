from collections import deque
from typing import Any

from app.application.ports.counter import Counter
from app.domain.entities.count_state import CountState
from app.domain.rules.stable_count_rule import compute_stable_count


class VisibleWindowCounter(Counter):
    """
    Counter that stabilizes raw counts using a sliding window.
    
    Maintains a buffer of the last N raw_count values and computes
    a stable_count using the specified strategy (median/mode).
    """

    def __init__(self, window: int = 15, stable_mode: str = "median") -> None:
        """
        Initialize counter with sliding window.
        
        Args:
            window: Size of sliding window (default 15)
            stable_mode: "median" or "mode" (default "median")
        """
        self._window = max(1, window)
        self._stable_mode = stable_mode
        self._history: deque[int] = deque(maxlen=self._window)

    def update(self, detections: Any) -> CountState:
        """
        Update counter with new detections.
        
        Args:
            detections: Object with __len__ (e.g., sv.Detections)
        
        Returns:
            CountState with raw_count, stable_count, window_size, and history.
        """
        # Compute raw count from detections
        raw_count = len(detections)
        
        # Add to history buffer
        self._history.append(raw_count)
        
        # Compute stable count using rule
        stable_count = compute_stable_count(list(self._history), self._stable_mode)
        
        # Return immutable state
        return CountState(
            raw_count=raw_count,
            stable_count=stable_count,
            window_size=self._window,
            history=tuple(self._history),
        )
