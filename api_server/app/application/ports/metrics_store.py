from typing import Protocol


class MetricsStorePort(Protocol):
    """
    Port (interface) for metrics storage.
    
    Allows retrieving current metrics without knowing
    the underlying implementation (mock, vision_edge, redis, etc.).
    """

    def get_metrics(self) -> dict:
        """
        Get current metrics.
        
        Returns:
            Dict with keys: count (int), fps (float), status (str), last_update (str ISO-8601)
        """
        ...