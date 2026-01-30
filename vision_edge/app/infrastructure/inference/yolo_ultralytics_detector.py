from app.application.ports.detector import Detector


class YoloUltralyticsDetector(Detector):
    def __init__(self, model_path: str, conf_thres: float = 0.5) -> None:
        self._model_path = model_path
        self._conf_thres = conf_thres

    def detect(self, frame_bgr: "object"):
        """Inference not implemented for ALFA skeleton."""
        raise NotImplementedError
