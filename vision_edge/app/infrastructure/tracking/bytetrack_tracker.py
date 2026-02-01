from app.application.ports.tracker import Tracker


class ByteTrackTracker(Tracker):
	def update(self, detections):
		"""Tracking not implemented for ALFA skeleton."""
		raise NotImplementedError
