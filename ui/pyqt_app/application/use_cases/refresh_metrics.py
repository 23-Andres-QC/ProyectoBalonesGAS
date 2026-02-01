from pyqt_app.application.ports.backend_client import BackendClient

class RefreshMetrics:
    def __init__(self, backend_client: BackendClient):
        self.backend_client = backend_client

    def execute(self) -> int:
        """
        Fetches metrics and returns the balloon count.
        """
        metrics = self.backend_client.get_metrics()
        # Assuming metrics format is {'count': X, ...} or similar. 
        # Adapting to whatever the backend provides.
        return metrics.get("count", 0)
