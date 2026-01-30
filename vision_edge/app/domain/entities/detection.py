from dataclasses import dataclass


@dataclass(frozen=True)
class Detection:
	bbox: tuple[float, float, float, float]
	confidence: float
	class_id: int
	label: str | None = None
