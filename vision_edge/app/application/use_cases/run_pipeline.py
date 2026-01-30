from dataclasses import dataclass

from app.application.ports.counter import Counter
from app.application.ports.detector import Detector
from app.application.ports.frame_source import FrameSource
from app.application.ports.frame_store import FrameStore
from app.application.ports.metrics_store import MetricsStore
from app.application.ports.renderer import Renderer
from app.application.ports.tracker import Tracker


@dataclass
class RunPipeline:
    frame_source: FrameSource
    detector: Detector
    counter: Counter
    renderer: Renderer
    frame_store: FrameStore
    metrics_store: MetricsStore
    tracker: Tracker | None = None

    def run_once(self) -> None:
        """Skeleton run step (ALFA): no real processing yet."""
        raise NotImplementedError("Pipeline execution not implemented yet.")
