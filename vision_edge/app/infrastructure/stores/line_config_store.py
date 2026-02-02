from threading import Lock


class LineConfig:
	"""Thread-safe in-memory configuration for line crossing parameters.

	Currently only exposes line_y, which controls the vertical position of
	the supervision.LineZone used for counting crossings.
	"""

	def __init__(self, line_y: int) -> None:
		self._lock = Lock()
		self._line_y = int(line_y)

	def get_line_y(self) -> int:
		with self._lock:
			return int(self._line_y)

	def set_line_y(self, value: int) -> None:
		with self._lock:
			self._line_y = int(value)
