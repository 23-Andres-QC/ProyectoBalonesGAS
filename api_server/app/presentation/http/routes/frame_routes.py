from fastapi import APIRouter, Response

from app.infrastructure.stores.placeholder_jpeg import get_placeholder_jpeg

router = APIRouter()


@router.get("/frame/raw")
def get_raw_frame() -> Response:
    """Return placeholder raw frame as JPEG bytes."""
    return Response(
        content=get_placeholder_jpeg(),
        media_type="image/jpeg",
        headers={"Cache-Control": "no-store"},
    )


@router.get("/frame/processed")
def get_processed_frame() -> Response:
    """Return placeholder processed frame as JPEG bytes."""
    return Response(
        content=get_placeholder_jpeg(),
        media_type="image/jpeg",
        headers={"Cache-Control": "no-store"},
    )
