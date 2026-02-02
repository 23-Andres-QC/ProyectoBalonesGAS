from datetime import datetime, timezone
from typing import Optional

import httpx

from app.infrastructure.config.settings import Settings


class VisionEdgeMetricsAdapter:
    """
    Adapter for fetching metrics from vision_edge via HTTP.
    
    Implements MetricsStorePort by calling vision_edge REST API.
    Falls back to offline status if vision_edge is unreachable.
    """

    def __init__(self, settings: Settings) -> None:
        """
        Initialize adapter with vision_edge configuration.
        
        Args:
            settings: Application settings with VISION_EDGE_BASE_URL and timeout.
        """
        self._base_url = settings.VISION_EDGE_BASE_URL.rstrip("/")
        self._timeout = settings.VISION_EDGE_TIMEOUT_SEC
        self._api_key = settings.VISION_EDGE_API_KEY

    def get_metrics(self) -> dict:
        """
        Get current metrics from vision_edge.
        
        Calls GET {base_url}/metrics and maps response to backend contract.
        
        Returns:
            Dict with keys: count (int), fps (float), status (str), last_update (str).
            On error, returns offline status with zeros.
        """
        try:
            url = f"{self._base_url}/metrics"
            headers = {}
            if self._api_key:
                headers["Authorization"] = f"Bearer {self._api_key}"
            
            response = httpx.get(url, headers=headers, timeout=self._timeout)
            response.raise_for_status()
            
            data = response.json()
			
            # Map vision_edge response to backend contract
            # UI "count" debe representar cuántos balones ENTRAN por la línea.
            # Priorizar line_in; si no existe, caer a line_total y luego a stable_count.
            return {
                "count": data.get("line_in", data.get("line_total", data.get("stable_count", data.get("count", 0)))),
                "fps": data.get("fps", 0.0),
                "status": data.get("status", "live"),
                "last_update": data.get("last_update", data.get("last_update_utc", self._get_current_utc_iso())),
            }
        
        except (httpx.HTTPError, httpx.TimeoutException, Exception) as e:
            # Fallback to offline status
            return {
                "count": 0,
                "fps": 0.0,
                "status": "offline",
                "last_update": self._get_current_utc_iso(),
            }

    def _get_current_utc_iso(self) -> str:
        """Get current UTC time in ISO-8601 format with Z suffix."""
        now = datetime.utcnow().replace(tzinfo=timezone.utc)
        return now.isoformat().replace("+00:00", "Z")
