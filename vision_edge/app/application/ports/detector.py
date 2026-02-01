from abc import ABC, abstractmethod

import numpy as np
import supervision as sv


class Detector(ABC):
	@abstractmethod
	def detect(self, frame: np.ndarray) -> sv.Detections:
		"""Return detections for a frame (BGR numpy array)."""
		raise NotImplementedError
