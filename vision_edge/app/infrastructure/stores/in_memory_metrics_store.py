from threading import Lock

from app.application.ports.metrics_store import MetricsStore


class InMemoryMetricsStore(MetricsStore):
    def __init__(self) -> None:
        self._lock = Lock()
        self._metrics: dict | None = None

    def set_metrics(self, metrics: dict) -> None:
        with self._lock:
            self._metrics = dict(metrics)

    def get_metrics(self) -> dict | None:
        with self._lock:
            return dict(self._metrics) if self._metrics is not None else None
