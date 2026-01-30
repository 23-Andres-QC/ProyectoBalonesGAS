from app.application.ports.renderer import Renderer


class SupervisionOverlayRenderer(Renderer):
    def render(self, frame_bgr: "object", detections: "object") -> bytes:
        """Rendering not implemented for ALFA skeleton."""
        raise NotImplementedError
