import os


class StreamConfig:
    """
    Configuración de URLs para streaming MJPEG.
    
    Las URLs pueden ser sobrescritas con variables de entorno:
    - VISION_EDGE_URL: Base URL del servidor de streaming
    """
    
    # Base URL del servidor de streaming (VisionEdge)
    BASE_URL = os.getenv("VISION_EDGE_URL", "http://127.0.0.1:8010")
    
    # Endpoints de streaming
    STREAM_RAW_URL = f"{BASE_URL}/stream/raw.mjpg"
    STREAM_PROCESSED_URL = f"{BASE_URL}/stream/processed.mjpg"
    
    # Backend API para métricas (FastAPI en puerto 8000)
    BACKEND_BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
    
    # Timeouts
    STREAM_TIMEOUT_SEC = 5.0
    API_TIMEOUT_SEC = 2.0
