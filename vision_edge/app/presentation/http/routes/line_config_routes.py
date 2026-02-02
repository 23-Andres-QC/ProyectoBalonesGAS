"""Routes to configure line crossing parameters at runtime."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.infrastructure.stores.line_config_store import LineConfig


class LineYUpdate(BaseModel):
	line_y: int


def create_line_config_router(line_config: LineConfig) -> APIRouter:
	"""Create router to get/update line_y used by the pipeline."""
	router = APIRouter()

	@router.get("/config/line_y")
	def get_line_y() -> dict:
		return {"line_y": line_config.get_line_y()}

	@router.put("/config/line_y")
	def update_line_y(payload: LineYUpdate) -> dict:
		if payload.line_y < 0:
			raise HTTPException(status_code=400, detail="line_y must be non-negative")
		line_config.set_line_y(payload.line_y)
		return {"line_y": line_config.get_line_y()}

	return router
