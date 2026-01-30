from dataclasses import dataclass


@dataclass(frozen=True)
class CountState:
    """
    Immutable state of the counter.
    
    Attributes:
        raw_count: Direct count from current detections (len(detections))
        stable_count: Stabilized count using window strategy (median/mode)
        window_size: Size of the sliding window used
        history: Tuple of recent raw_count values in the window
    """

    raw_count: int
    stable_count: int
    window_size: int
    history: tuple[int, ...] = ()
