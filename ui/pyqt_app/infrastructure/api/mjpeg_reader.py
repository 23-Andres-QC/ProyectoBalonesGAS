import requests
from typing import Iterator, Callable, Optional


def iter_mjpeg_frames(
    url: str,
    timeout_sec: float = 5.0,
    read_timeout_sec: float = 1.0,
    chunk_size: int = 4096,
    stop_flag: Optional[Callable[[], bool]] = None,
    max_buffer_bytes: int = 5 * 1024 * 1024,
) -> Iterator[bytes]:
    """
    Lee un stream MJPEG y devuelve frames JPEG completos (bytes).
    - Thread-friendly: soporta stop_flag
    - Seguro: cierra response siempre
    - Robusto: usa bytearray + buffer cap
    
    Args:
        url: URL del stream MJPEG
        timeout_sec: Timeout para conexión inicial
        read_timeout_sec: Timeout para lectura de cada chunk (permite stop rápido)
        chunk_size: Tamaño de cada chunk a leer
        stop_flag: Callable que retorna True cuando se debe detener
        max_buffer_bytes: Límite de buffer para evitar memory leaks
        
    Yields:
        bytes: Frame JPEG completo
        
    Raises:
        requests.RequestException: Si hay error de conexión
    """
    SOI = b"\xff\xd8"  # JPEG Start of Image
    EOI = b"\xff\xd9"  # JPEG End of Image

    headers = {"Accept": "multipart/x-mixed-replace"}

    with requests.get(
        url,
        stream=True,
        headers=headers,
        timeout=(timeout_sec, read_timeout_sec),
    ) as response:
        response.raise_for_status()

        buffer = bytearray()

        for chunk in response.iter_content(chunk_size=chunk_size):
            # Chequear stop por chunk, no solo por frame
            if stop_flag and stop_flag():
                break

            if not chunk:
                continue

            buffer.extend(chunk)

            # Evitar crecimiento infinito si se corrompe el stream
            if len(buffer) > max_buffer_bytes:
                buffer[:] = buffer[-max(2, max_buffer_bytes):]

            while True:
                start = buffer.find(SOI)
                if start == -1:
                    # conservar últimos bytes por si SOI se parte entre chunks
                    if len(buffer) > 2:
                        buffer[:] = buffer[-2:]
                    break

                end = buffer.find(EOI, start + 2)
                if end == -1:
                    # esperar más datos, pero descartando basura previa al SOI
                    if start > 0:
                        del buffer[:start]
                    break

                jpeg_data = bytes(buffer[start:end + 2])
                yield jpeg_data

                # remover todo hasta end+2
                del buffer[:end + 2]
