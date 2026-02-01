from datetime import datetime, timezone


class MockMetricsStore:
    """
    Mock implementation of MetricsStorePort.
    
    Returns static mock data for testing and development.
    Will be replaced by VisionEdgeMetricsAdapter in HU06.
    """

    def get_metrics(self) -> dict:
        """
        Get mock metrics.
        
        Returns:
            Dict with mock data: count=0, fps=0.0, status="mock", last_update=now.
        """
        # Generate current timestamp in ISO-8601 format with Z suffix
        now = datetime.utcnow().replace(tzinfo=timezone.utc)
        iso_timestamp = now.isoformat().replace("+00:00", "Z")
        
        return {
            "count": 0,
            "fps": 0.0,
            "status": "mock",
            "last_update": iso_timestamp,
        }
