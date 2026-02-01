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
