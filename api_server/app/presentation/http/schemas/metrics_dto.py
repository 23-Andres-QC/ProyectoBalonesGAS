from pydantic import BaseModel


class MetricsDTO(BaseModel):
    """
    Data Transfer Object for metrics response.
    
    Attributes:
        count: Number of objects detected (int)
        fps: Frames per second (float)
        status: Current status (str) - 'mock' for mock data, 'live' for real data
        last_update: ISO-8601 formatted timestamp (str)
    """

    count: int
    fps: float
    status: str
    last_update: str

    class Config:
        json_schema_extra = {
            "example": {
                "count": 0,
                "fps": 0.0,
                "status": "mock",
                "last_update": "2026-01-30T16:22:10Z",
            }
        }