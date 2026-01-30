"""
Dependency Injection Container (HU06).

Wires all dependencies (stores, use cases) and provides singleton access.
Supports switching between Mock and VisionEdge implementations via settings.
"""

from app.application.use_cases.get_latest_frame import GetLatestFrame
from app.application.use_cases.get_metrics import GetMetrics
from app.infrastructure.adapters.vision_edge_frame_adapter import (
    VisionEdgeFrameAdapter,
)
from app.infrastructure.adapters.vision_edge_metrics_adapter import (
    VisionEdgeMetricsAdapter,
)
from app.infrastructure.config.settings import get_settings
from app.infrastructure.stores.mock_frame_store import MockFrameStore
from app.infrastructure.stores.mock_metrics_store import MockMetricsStore


class Container:
    """
    Dependency Injection Container.
    
    Constructs all application dependencies based on configuration.
    Provides singleton access to use cases for routes.
    """

    def __init__(self) -> None:
        """
        Initialize container and wire dependencies.
        
        Reads settings to determine which implementations to use:
        - USE_VISION_EDGE=false (default): MockStores
        - USE_VISION_EDGE=true: VisionEdgeAdapters (HTTP)
        """
        self._settings = get_settings()
        
        # Wire dependencies based on configuration
        if self._settings.USE_VISION_EDGE:
            # Production mode: use VisionEdge adapters via HTTP
            self.metrics_store = VisionEdgeMetricsAdapter(self._settings)
            self.frame_store = VisionEdgeFrameAdapter(self._settings)
        else:
            # Development mode: use mock stores
            self.metrics_store = MockMetricsStore()
            self.frame_store = MockFrameStore()
        
        # Wire use cases with injected dependencies (DIP)
        self.get_metrics_use_case = GetMetrics(self.metrics_store)
        self.get_latest_frame_use_case = GetLatestFrame(self.frame_store)


# Singleton instance
container = Container()
