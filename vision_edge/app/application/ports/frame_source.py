from abc import ABC, abstractmethod

import numpy as np


class FrameSource(ABC):
    @abstractmethod
    def read(self) -> np.ndarray | None:
        """Return next frame (BGR numpy array) or None if unavailable."""
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        """Release resources."""
        raise NotImplementedError
