from abc import ABC, abstractmethod
from typing import Iterable

from app.domain.entities.detection import Detection


class Detector(ABC):
	@abstractmethod
	def detect(self, frame_bgr: "object") -> Iterable[Detection]:
		"""Return detections for a frame."""
		raise NotImplementedError
