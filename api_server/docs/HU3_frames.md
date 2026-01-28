# HU3 — Frames (placeholders)

## Resumen
Se agregaron endpoints de frames con JPEG placeholder y se registró el router en `main.py`. También se redujo la cantidad de `__init__.py` para simplificar la estructura.

## Archivos creados/modificados
- `app/presentation/http/routes/frame_routes.py`: rutas de frames (raw/processed).
- `app/infrastructure/stores/placeholder_jpeg.py`: helper de bytes JPEG placeholder.
- `app/main.py`: registro del router de frames.

## Cómo probar
1) Arrancar el servidor:
   ```bash
   uvicorn app.main:app --reload
   ```
2) Probar endpoints:
   ```bash
   curl -o raw.jpg http://localhost:8000/api/frame/raw
   curl -o processed.jpg http://localhost:8000/api/frame/processed
   ```

## Nota sobre __init__.py
- Se removieron `__init__.py` no esenciales para evitar ruido.
- Se dejó únicamente el mínimo necesario para que los imports funcionen con `app.main`.

## Compatibilidad
- Compatible con `uvicorn app.main:app --reload`.
- Mantiene `/api/health` y agrega `/api/frame/raw` y `/api/frame/processed`.
