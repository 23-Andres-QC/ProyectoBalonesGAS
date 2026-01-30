from app.application.ports.counter import Counter
from app.domain.rules.stable_count_rule import StableCountRule


class VisibleWindowCounter(Counter):
    def __init__(self, window: int = 15) -> None:
        self._rule = StableCountRule(window=window)

    def update(self, visible_count: int) -> int:
        return self._rule.update(visible_count)
