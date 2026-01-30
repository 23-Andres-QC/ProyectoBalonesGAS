from collections import deque


class StableCountRule:
    def __init__(self, window: int = 15) -> None:
        self._window = max(1, window)
        self._history: deque[int] = deque(maxlen=self._window)

    def update(self, visible_count: int) -> int:
        self._history.append(int(visible_count))
        return int(round(sum(self._history) / len(self._history)))
