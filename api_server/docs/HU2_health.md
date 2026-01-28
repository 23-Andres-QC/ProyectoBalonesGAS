# HU2 — Health Endpoint

## Resumen
Se agregó el endpoint GET `/api/health` siguiendo Clean Architecture (ruta en `presentation`, configuración en `infrastructure`).

## Archivos tocados
- `app/presentation/http/routes/health_routes.py`: router y handler del endpoint de salud.
- `app/main.py`: registro del router de health dentro del router base `/api`.

## Cómo probar
1) Arrancar el servidor:
   ```bash
   uvicorn app.main:app --reload
   ```
2) Probar:
   ```bash
   curl http://localhost:8000/api/health
   ```

## Sobre __init__.py
- En Python 3.3+ no son estrictamente obligatorios (namespace packages), pero ayudan a asegurar imports predecibles.
- Mínimo recomendado aquí: mantener `__init__.py` en `app/` y en los paquetes que se importan por ruta absoluta (`app.presentation.http.routes`).
- Si se desea reducir, se podrían evaluar `__init__.py` en carpetas que no se importan aún, pero no es necesario para HU2.
