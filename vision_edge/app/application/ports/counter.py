from abc import ABC, abstractmethod


class Counter(ABC):
    @abstractmethod
    def update(self, visible_count: int) -> int:
        """Update counter state and return stabilized count."""
        raise NotImplementedError
