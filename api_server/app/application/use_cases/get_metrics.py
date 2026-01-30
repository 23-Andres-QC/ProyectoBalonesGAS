from app.application.ports.metrics_store import MetricsStorePort


class GetMetrics:
    """
    Use case: Get current metrics.
    
    Depends on MetricsStorePort abstraction (DIP).
    """

    def __init__(self, metrics_store: MetricsStorePort) -> None:
        """
        Initialize use case with metrics store dependency.
        
        Args:
            metrics_store: Implementation of MetricsStorePort.
        """
        self._metrics_store = metrics_store

    def execute(self) -> dict:
        """
        Execute use case to get current metrics.
        
        Returns:
            Dict with keys: count, fps, status, last_update.
        """
        return self._metrics_store.get_metrics()