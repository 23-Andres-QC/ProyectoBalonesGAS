from dataclasses import dataclass


@dataclass
class CountState:
    count_visible: int = 0
    fps: float = 0.0
    status: str = "idle"
    last_update: float = 0.0
