from abc import ABC, abstractmethod


class MetricsStore(ABC):
    @abstractmethod
    def set_metrics(self, metrics: dict) -> None:
        """Persist latest metrics."""
        raise NotImplementedError

    @abstractmethod
    def get_metrics(self) -> dict | None:
        """Return latest metrics."""
        raise NotImplementedError
