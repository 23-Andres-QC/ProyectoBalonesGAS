from typing import Optional

import httpx

from app.infrastructure.config.settings import Settings
from app.infrastructure.stores.placeholder_jpeg import get_placeholder_jpeg


class VisionEdgeFrameAdapter:
    """
    Adapter for fetching frames from vision_edge via HTTP.
    
    Implements FrameStorePort by calling vision_edge REST API.
    Falls back to placeholder JPEG if vision_edge is unreachable.
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

    def get_raw(self) -> Optional[bytes]:
        """
        Get latest raw frame from vision_edge.
        
        Calls GET {base_url}/frame/raw.jpg
        
        Returns:
            JPEG bytes or placeholder if error.
        """
        return self._fetch_frame("/frame/raw.jpg")

    def get_processed(self) -> Optional[bytes]:
        """
        Get latest processed frame from vision_edge.
        
        Calls GET {base_url}/frame/processed.jpg
        
        Returns:
            JPEG bytes or placeholder if error.
        """
        return self._fetch_frame("/frame/processed.jpg")

    def _fetch_frame(self, path: str) -> Optional[bytes]:
        """
        Fetch frame from vision_edge.
        
        Args:
            path: API path (e.g., "/frame/raw.jpg")
        
        Returns:
            JPEG bytes or placeholder on error.
        """
        try:
            url = f"{self._base_url}{path}"
            headers = {}
            if self._api_key:
                headers["Authorization"] = f"Bearer {self._api_key}"
            
            response = httpx.get(url, headers=headers, timeout=self._timeout)
            response.raise_for_status()
            
            # Verify content type is image
            content_type = response.headers.get("content-type", "")
            if "image" not in content_type.lower():
                return get_placeholder_jpeg()
            
            return response.content
        
        except (httpx.HTTPError, httpx.TimeoutException, Exception) as e:
            # Fallback to placeholder JPEG
            return get_placeholder_jpeg()
