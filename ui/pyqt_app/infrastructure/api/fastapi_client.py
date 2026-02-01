import requests
from pyqt_app.application.ports.backend_client import BackendClient

class FastApiClient(BackendClient):
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url

    def get_raw_frame(self) -> bytes:
        try:
            response = requests.get(f"{self.base_url}/api/frame/raw", timeout=2)
            if response.status_code == 200:
                return response.content
        except Exception as e:
            print(f"Error fetching raw frame: {e}")
        return b""

    def get_processed_frame(self) -> bytes:
        try:
            response = requests.get(f"{self.base_url}/api/frame/processed", timeout=2)
            if response.status_code == 200:
                return response.content
        except Exception as e:
            print(f"Error fetching processed frame: {e}")
        return b""

    def get_metrics(self) -> dict:
        try:
            response = requests.get(f"{self.base_url}/api/metrics", timeout=0.5)  # ⚡ 500ms en vez de 2s
            if response.status_code == 200:
                return response.json()
        except requests.Timeout:
            pass  # Silencioso, el UI ya muestra indicador
        except Exception:
            pass
        return {}
