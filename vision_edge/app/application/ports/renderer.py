from abc import ABC, abstractmethod


class Renderer(ABC):
    @abstractmethod
    def render(self, frame_bgr: "object", detections: "object") -> bytes:
        """Render detections and return JPEG bytes."""
        raise NotImplementedError
