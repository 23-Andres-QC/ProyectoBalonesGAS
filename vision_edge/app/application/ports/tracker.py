from abc import ABC, abstractmethod
from typing import Iterable

from app.domain.entities.detection import Detection


class Tracker(ABC):
	@abstractmethod
	def update(self, detections: Iterable[Detection]) -> Iterable[Detection]:
		"""Return tracked detections (may add IDs)."""
		raise NotImplementedError
