import base64

_PLACEHOLDER_JPEG_B64 = (
    "/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAP//////////////////////////////////"
    "////////////////////////////////////////////////////wAALCAABAAEBAREA"
    "/8QAAFoAAQAAAAAAAAAAAAAAAAAAAAb/xAAfEAACAQQCAwAAAAAAAAAAAAAAAgMABBEh"
    "EjFhQf/aAAgBAQAAPwCxnk8g1//Z"
)

_PLACEHOLDER_JPEG_BYTES = base64.b64decode(_PLACEHOLDER_JPEG_B64)


def get_placeholder_jpeg() -> bytes:
    """Return placeholder JPEG bytes."""
    return _PLACEHOLDER_JPEG_BYTES
