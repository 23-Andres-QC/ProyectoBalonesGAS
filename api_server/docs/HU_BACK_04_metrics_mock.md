# HU4 - Backend: Endpoint de Métricas (MOCK)

## Objetivo
Exponer endpoint `GET /api/metrics` que retorne métricas mock para que la UI pueda mostrar contador/estado sin depender de vision_edge todavía.

## Archivos creados/modificados

### 1. DTO creado ([app/presentation/http/schemas/metrics_dto.py](../app/presentation/http/schemas/metrics_dto.py))
- Pydantic model `MetricsDTO` con validación automática
- Campos:
  - `count: int` - Número de objetos detectados
  - `fps: float` - Frames por segundo
  - `status: str` - Estado actual ("mock" o "live")
  - `last_update: str` - Timestamp ISO-8601
- Incluye ejemplo en schema OpenAPI

### 2. Router creado ([app/presentation/http/routes/metrics_routes.py](../app/presentation/http/routes/metrics_routes.py))
- Define `router = APIRouter()`
- Endpoint `@router.get("/metrics", response_model=MetricsDTO)`
- Implementación mock:
  - `count = 0`
  - `fps = 0.0`
  - `status = "mock"`
  - `last_update = UTC now en formato ISO-8601` (ej: "2026-01-30T16:22:10Z")
- Usa `datetime.utcnow()` con timezone UTC
- Formato ISO con sufijo "Z" para indicar UTC

### 3. Router registrado ([app/main.py](../app/main.py))
- Importado `metrics_router`
- Agregado `api_router.include_router(metrics_router)`
- Registrado bajo prefix `/api` (igual que otros routers)
- NO se cambió ningún router existente

## Configuración

No requiere configuración adicional. Usa la misma estructura existente de FastAPI.

## Cómo ejecutar

### Iniciar servidor
```bash
cd api_server

# Activar entorno virtual (si no está activo)
# Windows:
.\.venv\Scripts\Activate.ps1
# Linux/Mac:
source .venv/bin/activate

# Ejecutar servidor
uvicorn app.main:app --reload
```

**Salida esperada:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using StatReload
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

## Pruebas

### Test 1: curl básico
```bash
curl http://localhost:8000/api/metrics
```

**Respuesta esperada:**
```json
{
  "count": 0,
  "fps": 0.0,
  "status": "mock",
  "last_update": "2026-01-30T16:22:10Z"
}
```

### Test 2: curl con formato
```bash
curl http://localhost:8000/api/metrics | jq
```

**Respuesta esperada (formateada):**
```json
{
  "count": 0,
  "fps": 0.0,
  "status": "mock",
  "last_update": "2026-01-30T16:22:10Z"
}
```

### Test 3: Navegador
Abrir en navegador:
```
http://localhost:8000/api/metrics
```

### Test 4: Swagger UI (OpenAPI docs)
Abrir en navegador:
```
http://localhost:8000/docs
```

Buscar endpoint `GET /api/metrics` y hacer clic en "Try it out" → "Execute"

### Test 5: Verificar formato timestamp
```bash
# Ejecutar múltiples veces para verificar que timestamp cambia
curl http://localhost:8000/api/metrics | jq '.last_update'
sleep 2
curl http://localhost:8000/api/metrics | jq '.last_update'
```

**Resultado:** Deberías ver timestamps diferentes (actualizados)

## Validación de compatibilidad

### ✅ Endpoint /api/health sigue funcionando
```bash
curl http://localhost:8000/api/health
```
**Respuesta esperada:**
```json
{
  "status": "ok",
  "app": "Vision API",
  "version": "0.1.0-alfa"
}
```

### ✅ Endpoint /api/frame/raw sigue funcionando
```bash
curl http://localhost:8000/api/frame/raw --output test.jpg
```
**Resultado:** Descarga imagen placeholder

### ✅ Endpoint /api/frame/processed sigue funcionando
```bash
curl http://localhost:8000/api/frame/processed --output test.jpg
```
**Resultado:** Descarga imagen placeholder

### ✅ Nuevo endpoint /api/metrics funciona
```bash
curl http://localhost:8000/api/metrics
```
**Resultado:** JSON con métricas mock

## Estructura final

```
api_server/
  app/
    presentation/
      http/
        routes/
          health_routes.py       ← Ya existía
          frame_routes.py        ← Ya existía
          metrics_routes.py      ← NUEVO (HU4)
        schemas/
          metrics_dto.py         ← NUEVO (HU4)
    main.py                      ← MODIFICADO (agregado import + include_router)
  docs/
    HU2_health.md
    HU3_frames.md
    HU_BACK_04_metrics_mock.md   ← NUEVO (este archivo)
```

## Arquitectura (Clean Architecture + SOLID)

### Por qué esta estructura:

1. **Separation of Concerns (SoC)**
   - `MetricsDTO` (schemas): Define contrato de datos (solo estructura)
   - `metrics_routes.py` (routes): Define endpoint HTTP (solo presentación)
   - NO hay lógica de negocio (es mock, futuro: use_cases/)

2. **Dependency Inversion Principle (DIP)**
   - Router no depende de implementaciones concretas
   - Cuando sea real, usará ports/adapters para obtener datos de vision_edge
   - Por ahora retorna datos directamente (mock simple)

3. **Open/Closed Principle (OCP)**
   - Se agregó nuevo router sin modificar routers existentes
   - Solo se agregó 1 línea de import y 1 línea de include_router en main.py
   - Extensión sin modificación de código existente

4. **Single Responsibility Principle (SRP)**
   - MetricsDTO: solo define estructura de datos
   - metrics_routes: solo define endpoint HTTP
   - Cada archivo tiene una única razón de cambio

5. **Preparado para el futuro**
   - Estructura permite reemplazar mock con datos reales fácilmente
   - Futuro: crear `get_metrics_use_case.py` en `application/use_cases/`
   - Futuro: crear adapter para obtener datos de vision_edge stores
   - El DTO y router NO cambiarán cuando integremos vision_edge

## Próximos pasos (fuera de scope HU4)

- **HU5 (futuro):** Integrar vision_edge con api_server
  - Crear use case `GetMetrics` en `application/use_cases/`
  - Crear adapter para leer de vision_edge stores (Redis/in-memory)
  - Modificar `metrics_routes.py` para usar el use case en lugar de mock
  - Cambiar `status: "mock"` → `status: "live"`
  - Retornar datos reales: count, fps desde vision_edge

- **HU6 (futuro):** WebSockets para métricas en tiempo real
  - Endpoint WS `/ws/metrics` para streaming
  - UI puede suscribirse a cambios en tiempo real
  - Sin polling HTTP

## Testing automatizado (opcional, futuro)

```python
# tests/test_metrics_routes.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_metrics_returns_200():
    response = client.get("/api/metrics")
    assert response.status_code == 200

def test_get_metrics_has_correct_fields():
    response = client.get("/api/metrics")
    data = response.json()
    assert "count" in data
    assert "fps" in data
    assert "status" in data
    assert "last_update" in data

def test_get_metrics_mock_status():
    response = client.get("/api/metrics")
    data = response.json()
    assert data["status"] == "mock"
    assert data["count"] == 0
    assert data["fps"] == 0.0

def test_get_metrics_timestamp_format():
    response = client.get("/api/metrics")
    data = response.json()
    # Verificar que termina en Z (UTC)
    assert data["last_update"].endswith("Z")
```

## Troubleshooting

### ❌ Error: "ModuleNotFoundError: No module named 'app.presentation.http.routes.metrics_routes'"

**Causa:** Archivo no creado o mal ubicado  
**Solución:** Verificar que existe `api_server/app/presentation/http/routes/metrics_routes.py`

### ❌ Error: "404 Not Found" al hacer curl

**Causa:** Servidor no reiniciado o ruta incorrecta  
**Solución:**
1. Reiniciar servidor: `uvicorn app.main:app --reload`
2. Verificar ruta: debe ser `/api/metrics` no `/metrics`

### ❌ Error: "ImportError: cannot import name 'MetricsDTO'"

**Causa:** Archivo schemas/metrics_dto.py vacío o mal creado  
**Solución:** Verificar que existe y tiene la clase MetricsDTO

### ❌ Timestamp siempre igual

**Causa:** No debería pasar, se genera en cada request  
**Solución:** Verificar que no hay caché. Probar con curl varias veces.

---

## Resumen

✅ **HU4 implementado exitosamente**

**Archivos creados:**
- `app/presentation/http/schemas/metrics_dto.py` (28 líneas)
- `app/presentation/http/routes/metrics_routes.py` (30 líneas)
- `docs/HU_BACK_04_metrics_mock.md` (este archivo)

**Archivos modificados:**
- `app/main.py` (+2 líneas: import + include_router)

**Endpoints existentes:** ✅ Sin cambios
**Nuevo endpoint:** ✅ GET /api/metrics funcionando
**Clean Architecture:** ✅ Respetada
**SOLID:** ✅ Aplicado

**Listo para integración con UI y futuro vision_edge!**
