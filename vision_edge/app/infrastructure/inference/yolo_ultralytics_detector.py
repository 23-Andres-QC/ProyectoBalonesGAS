import numpy as np
import supervision as sv
from ultralytics import YOLO

from app.application.ports.detector import Detector


class YoloUltralyticsDetector(Detector):
    def __init__(self, model_path: str, conf_thres: float = 0.5) -> None:
        self._model_path = model_path
        self._conf_thres = conf_thres
        print(f"[YOLO] Loading model: {model_path}")
        try:
            self._model = YOLO(model_path)
            print(f"[YOLO] Model loaded successfully (conf={conf_thres})")
        except Exception as e:
            raise FileNotFoundError(
                f"Failed to load YOLO model at {model_path}: {e}"
            ) from e

    def detect(self, frame: np.ndarray) -> sv.Detections:
        """Run inference and return supervision Detections with class labels."""
        if frame is None:
            return sv.Detections.empty()

        results = self._model(frame, verbose=False, conf=self._conf_thres)[0]
        detections = sv.Detections.from_ultralytics(results)

        # Map class_id -> human-readable label using YOLO names
        # Esto permite que el renderer muestre, por ejemplo, "Gas_balon".
        try:
            class_ids = getattr(detections, "class_id", None)
            if class_ids is not None:
                names = results.names  # dict: {class_id: "label"}
                labels = np.array([
                    names.get(int(cid), f"class_{int(cid)}") for cid in class_ids
                ], dtype=object)
                # supervision.Detections permite almacenar metadata en data["class_name"]
                detections.data["class_name"] = labels
        except Exception:
            # Si algo falla al mapear nombres de clase, seguimos solo con IDs
            pass

        return detections
