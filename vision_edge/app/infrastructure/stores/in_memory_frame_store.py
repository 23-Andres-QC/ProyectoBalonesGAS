from threading import Lock

from app.application.ports.frame_store import FrameStore


class InMemoryFrameStore(FrameStore):
    def __init__(self) -> None:
        self._lock = Lock()
        self._raw: bytes | None = None
        self._processed: bytes | None = None

    def set_frames(self, raw_jpeg: bytes, processed_jpeg: bytes) -> None:
        with self._lock:
            self._raw = raw_jpeg
            self._processed = processed_jpeg

    def get_frames(self) -> tuple[bytes | None, bytes | None]:
        with self._lock:
            return self._raw, self._processed
