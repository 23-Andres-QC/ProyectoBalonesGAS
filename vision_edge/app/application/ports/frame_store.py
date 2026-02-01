from abc import ABC, abstractmethod


class FrameStore(ABC):
    @abstractmethod
    def set_frames(self, raw_jpeg: bytes, processed_jpeg: bytes) -> None:
        """Persist latest raw/processed frames."""
        raise NotImplementedError

    @abstractmethod
    def get_frames(self) -> tuple[bytes | None, bytes | None]:
        """Return latest raw/processed frames."""
        raise NotImplementedError
