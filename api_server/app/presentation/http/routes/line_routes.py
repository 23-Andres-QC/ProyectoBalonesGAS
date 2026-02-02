from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx

from app.infrastructure.config.settings import get_settings


router = APIRouter()


class LineYUpdate(BaseModel):
	line_y: int


@router.put("/line_y")
def update_line_y(payload: LineYUpdate):
	"""Proxy to update line_y in vision_edge via HTTP."""
	settings = get_settings()
	base_url = settings.VISION_EDGE_BASE_URL.rstrip("/")
	try:
		resp = httpx.put(
			f"{base_url}/config/line_y",
			json={"line_y": payload.line_y},
			timeout=settings.VISION_EDGE_TIMEOUT_SEC,
		)
		resp.raise_for_status()
		return resp.json()
	except httpx.HTTPError:
		raise HTTPException(status_code=502, detail="VisionEdge unavailable")
