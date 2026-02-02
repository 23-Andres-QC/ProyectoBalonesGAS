from abc import ABC, abstractmethod

class BackendClient(ABC):
    @abstractmethod
    def get_raw_frame(self) -> bytes:
        pass

    @abstractmethod
    def get_processed_frame(self) -> bytes:
        pass

    @abstractmethod
    def get_metrics(self) -> dict:
        pass

    @abstractmethod
    def set_line_y(self, line_y: int) -> None:
        """Update line_y in backend (api_server -> vision_edge)."""
        pass
