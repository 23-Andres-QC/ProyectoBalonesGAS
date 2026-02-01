# HU05 - Backend: Capa Application (Ports + Use Cases)

## Objetivo
Introducir Clean Architecture con capa Application (ports + use cases) para preparar integración con vision_edge. Los endpoints actuales siguen funcionando con mocks, pero ahora usan una arquitectura limpia que permite cambiar la implementación sin tocar los endpoints.

## Archivos creados/modificados

### 1. Ports (Interfaces) - `app/application/ports/`

#### [frame_store.py](../app/application/ports/frame_store.py) - FrameStorePort
```python
class FrameStorePort(Protocol):
    def get_raw() -> Optional[bytes]
    def get_processed() -> Optional[bytes]
```
- Define interfaz para obtener frames (raw/processed)
- Usa `Protocol` (typing) para duck typing
- No depende de implementación concreta

#### [metrics_store.py](../app/application/ports/metrics_store.py) - MetricsStorePort
```python
class MetricsStorePort(Protocol):
    def get_metrics() -> dict
```
- Define interfaz para obtener métricas
- Retorna dict con keys: count, fps, status, last_update
- Desacoplado de la fuente de datos

### 2. Use Cases - `app/application/use_cases/`

#### [get_latest_frame.py](../app/application/use_cases/get_latest_frame.py) - GetLatestFrame
```python
class GetLatestFrame:
    def __init__(self, frame_store: FrameStorePort)
    def execute(self, frame_type: Literal["raw", "processed"]) -> Optional[bytes]
```
- Recibe FrameStorePort en constructor (DIP)
- Lógica de negocio: decidir qué método llamar según frame_type
- NO conoce si es mock, vision_edge, redis, etc.

#### [get_metrics.py](../app/application/use_cases/get_metrics.py) - GetMetrics
```python
class GetMetrics:
    def __init__(self, metrics_store: MetricsStorePort)
    def execute() -> dict
```
- Recibe MetricsStorePort en constructor (DIP)
- Lógica simple: delegar al store
- Preparado para agregar validaciones/transformaciones futuras

### 3. Infrastructure - Mocks - `app/infrastructure/stores/`

#### [mock_frame_store.py](../app/infrastructure/stores/mock_frame_store.py) - MockFrameStore (NUEVO)
```python
class MockFrameStore:
    def get_raw() -> Optional[bytes]
    def get_processed() -> Optional[bytes]
```
- Implementación mock de FrameStorePort
- Retorna placeholder JPEG (reutiliza `placeholder_jpeg.py`)
- Reemplazable por VisionEdgeFrameAdapter en HU06

#### [mock_metrics_store.py](../app/infrastructure/stores/mock_metrics_store.py) - MockMetricsStore (NUEVO)
```python
class MockMetricsStore:
    def get_metrics() -> dict
```
- Implementación mock de MetricsStorePort
- Retorna datos estáticos: count=0, fps=0.0, status="mock"
- Reemplazable por VisionEdgeMetricsAdapter en HU06

### 4. Routes actualizados - `app/presentation/http/routes/`

#### [metrics_routes.py](../app/presentation/http/routes/metrics_routes.py) - MODIFICADO
- Ahora usa `GetMetrics` use case
- Instancia temporal: `MockMetricsStore()` → `GetMetrics(store)`
- TODO HU06: reemplazar con DI container
- **Contrato JSON NO cambió**: sigue retornando MetricsDTO

#### [frame_routes.py](../app/presentation/http/routes/frame_routes.py) - MODIFICADO
- Ahora usa `GetLatestFrame` use case
- Instancia temporal: `MockFrameStore()` → `GetLatestFrame(store)`
- TODO HU06: reemplazar con DI container
- **Rutas NO cambiaron**: `/api/frame/raw` y `/api/frame/processed` intactas

## Arquitectura (Clean Architecture implementada)

```
┌─────────────────────────────────────────────────────────────┐
│  Presentation Layer (HTTP/REST)                              │
│  ┌────────────────┐  ┌─────────────────┐                    │
│  │ metrics_routes │  │  frame_routes   │                    │
│  └────────┬───────┘  └────────┬────────┘                    │
│           │                    │                             │
└───────────┼────────────────────┼─────────────────────────────┘
            │                    │
            │                    │ (usa)
            ▼                    ▼
┌─────────────────────────────────────────────────────────────┐
│  Application Layer (Use Cases + Ports)                       │
│  ┌─────────────┐           ┌──────────────────┐             │
│  │ GetMetrics  │           │ GetLatestFrame   │             │
│  │  use case   │           │    use case      │             │
│  └──────┬──────┘           └─────────┬────────┘             │
│         │                             │                      │
│         │ depende de                  │ depende de           │
│         ▼                             ▼                      │
│  ┌──────────────────┐      ┌────────────────────┐           │
│  │MetricsStorePort  │      │  FrameStorePort    │           │
│  │   (Protocol)     │      │    (Protocol)      │           │
│  └──────────────────┘      └────────────────────┘           │
└──────────────────────────────────────────────────────────────┘
            ▲                             ▲
            │ implementa                  │ implementa
            │                             │
┌───────────┼─────────────────────────────┼───────────────────┐
│  Infrastructure Layer (Adapters/Mocks)                       │
│  ┌──────────────────┐      ┌────────────────────┐           │
│  │MockMetricsStore  │      │  MockFrameStore    │           │
│  │   (HU05 mock)    │      │   (HU05 mock)      │           │
│  └──────────────────┘      └────────────────────┘           │
│                                                               │
│  Futuro HU06:                                                │
│  ┌──────────────────────┐  ┌────────────────────────┐       │
│  │VisionEdgeMetrics     │  │VisionEdgeFrame         │       │
│  │Adapter (Redis/HTTP)  │  │Adapter (Redis/HTTP)    │       │
│  └──────────────────────┘  └────────────────────────┘       │
└──────────────────────────────────────────────────────────────┘
```

## Cómo funciona ahora (HU05)

### Flujo GET /api/metrics:
1. `metrics_routes.py` recibe request
2. Llama `_get_metrics_use_case.execute()`
3. Use case llama `_metrics_store.get_metrics()` (MockMetricsStore)
4. MockMetricsStore retorna dict mock
5. Route convierte a MetricsDTO y retorna JSON

### Flujo GET /api/frame/raw:
1. `frame_routes.py` recibe request
2. Llama `_get_latest_frame_use_case.execute("raw")`
3. Use case llama `_frame_store.get_raw()` (MockFrameStore)
4. MockFrameStore retorna placeholder JPEG bytes
5. Route retorna Response con imagen

## Cómo se usará en HU06 (DI Container)

En HU06 crearemos `app/di/container.py`:

```python
# HU06 - Dependency Injection Container (ejemplo)
from app.application.use_cases.get_metrics import GetMetrics
from app.application.use_cases.get_latest_frame import GetLatestFrame
from app.infrastructure.stores.mock_metrics_store import MockMetricsStore
from app.infrastructure.stores.mock_frame_store import MockFrameStore
# Futuro:
# from app.infrastructure.adapters.vision_edge_metrics_adapter import VisionEdgeMetricsAdapter
# from app.infrastructure.adapters.vision_edge_frame_adapter import VisionEdgeFrameAdapter

class Container:
    def __init__(self):
        # HU06: Cambiar Mock* por VisionEdge*Adapter según configuración
        self.metrics_store = MockMetricsStore()
        self.frame_store = MockFrameStore()
        
        # Use cases con dependencias inyectadas
        self.get_metrics_use_case = GetMetrics(self.metrics_store)
        self.get_latest_frame_use_case = GetLatestFrame(self.frame_store)

# Singleton global
container = Container()
```

Luego en routes (HU06):

```python
# metrics_routes.py (HU06)
from app.di.container import container

@router.get("/metrics")
def get_metrics():
    metrics_dict = container.get_metrics_use_case.execute()
    return MetricsDTO(**metrics_dict)
```

**Ventaja:** Cambiar de Mock a VisionEdge solo requiere modificar `Container.__init__()`, sin tocar routes.

## Principios SOLID aplicados

### 1. Single Responsibility Principle (SRP)
- **FrameStorePort**: solo define interfaz para obtener frames
- **GetLatestFrame**: solo orquesta llamada al store según tipo
- **MockFrameStore**: solo implementa lógica mock
- **frame_routes**: solo maneja HTTP (request/response)

### 2. Open/Closed Principle (OCP)
- Sistema abierto a extensión: agregar VisionEdgeFrameAdapter sin modificar use cases
- Cerrado a modificación: use cases no cambian cuando cambia store

### 3. Liskov Substitution Principle (LSP)
- MockFrameStore y VisionEdgeFrameAdapter son intercambiables
- Ambos cumplen contrato de FrameStorePort
- Use case funciona con cualquier implementación

### 4. Interface Segregation Principle (ISP)
- FrameStorePort: interfaz específica para frames (get_raw, get_processed)
- MetricsStorePort: interfaz específica para métricas (get_metrics)
- NO interfaces gordas con métodos innecesarios

### 5. Dependency Inversion Principle (DIP) ⭐
- **Alto nivel** (GetMetrics) NO depende de bajo nivel (MockMetricsStore)
- **Ambos dependen de abstracción** (MetricsStorePort)
- Inversión: store implementa puerto, use case solo conoce puerto

## Validación de compatibilidad

### ✅ GET /api/health - Intacto
```bash
curl http://localhost:8000/api/health
```
**Resultado:** Sin cambios, sigue funcionando

### ✅ GET /api/metrics - Funciona con nueva arquitectura
```bash
curl http://localhost:8000/api/metrics
```
**Resultado:**
```json
{
  "count": 0,
  "fps": 0.0,
  "status": "mock",
  "last_update": "2026-01-30T17:30:00Z"
}
```
**Cambio interno:** Ahora usa GetMetrics + MockMetricsStore (arquitectura limpia)
**Contrato externo:** JSON idéntico al HU04

### ✅ GET /api/frame/raw - Funciona con nueva arquitectura
```bash
curl http://localhost:8000/api/frame/raw --output test_raw.jpg
```
**Resultado:** Descarga placeholder JPEG
**Cambio interno:** Ahora usa GetLatestFrame + MockFrameStore
**Contrato externo:** Imagen idéntica

### ✅ GET /api/frame/processed - Funciona con nueva arquitectura
```bash
curl http://localhost:8000/api/frame/processed --output test_processed.jpg
```
**Resultado:** Descarga placeholder JPEG
**Cambio interno:** Ahora usa GetLatestFrame + MockFrameStore
**Contrato externo:** Imagen idéntica

## Estructura final

```
api_server/
  app/
    application/                    ← CAPA APPLICATION (HU05)
      ports/
        frame_store.py             ← NUEVO: FrameStorePort (Protocol)
        metrics_store.py           ← NUEVO: MetricsStorePort (Protocol)
      use_cases/
        get_latest_frame.py        ← NUEVO: GetLatestFrame use case
        get_metrics.py             ← NUEVO: GetMetrics use case
    
    infrastructure/                 ← CAPA INFRASTRUCTURE
      stores/
        mock_frame_store.py        ← NUEVO: Mock implementation
        mock_metrics_store.py      ← NUEVO: Mock implementation
        placeholder_jpeg.py        ← Ya existía (reutilizado)
    
    presentation/                   ← CAPA PRESENTATION
      http/
        routes/
          metrics_routes.py        ← MODIFICADO: usa GetMetrics
          frame_routes.py          ← MODIFICADO: usa GetLatestFrame
          health_routes.py         ← INTACTO
        schemas/
          metrics_dto.py           ← INTACTO
    
    main.py                        ← INTACTO (HU06 agregará DI)
  
  docs/
    HU_BACK_04_metrics_mock.md
    HU_BACK_05_application_layer.md  ← NUEVO (este archivo)
```

## Cómo probar

### 1. Iniciar servidor
```bash
cd api_server
uvicorn app.main:app --reload
```

### 2. Probar endpoints (deben funcionar igual que HU04)
```bash
# Métricas
curl http://localhost:8000/api/metrics

# Frame raw
curl http://localhost:8000/api/frame/raw --output test_raw.jpg

# Frame processed
curl http://localhost:8000/api/frame/processed --output test_processed.jpg

# Health (sin cambios)
curl http://localhost:8000/api/health
```

### 3. Verificar OpenAPI docs
```
http://localhost:8000/docs
```
Todos los endpoints deben aparecer y funcionar igual.

## Preparación para HU06 (DI Container)

En HU06 crearemos:

1. **`app/di/container.py`**
   - Factory para construir use cases con dependencias
   - Singleton global: `container = Container()`
   - Configurable vía env vars (MOCK vs VISION_EDGE)

2. **Actualizar routes para usar container**
   ```python
   # Antes (HU05):
   _metrics_store = MockMetricsStore()
   _get_metrics_use_case = GetMetrics(_metrics_store)
   
   # Después (HU06):
   from app.di.container import container
   # usar container.get_metrics_use_case
   ```

3. **Crear VisionEdgeAdapters** (cuando vision_edge esté listo)
   ```python
   # app/infrastructure/adapters/vision_edge_metrics_adapter.py
   class VisionEdgeMetricsAdapter:
       def __init__(self, redis_client):
           self._redis = redis_client
       
       def get_metrics(self) -> dict:
           # Leer de Redis/HTTP vision_edge
           return {"count": ..., "fps": ..., ...}
   ```

4. **Configurar Container para usar adapters**
   ```python
   # di/container.py (HU06)
   if os.getenv("USE_VISION_EDGE") == "true":
       self.metrics_store = VisionEdgeMetricsAdapter(redis_client)
   else:
       self.metrics_store = MockMetricsStore()
   ```

## Ventajas de esta arquitectura

✅ **Testeable**: Puedes mockear stores fácilmente en tests  
✅ **Flexible**: Cambiar implementación sin tocar use cases  
✅ **Escalable**: Agregar nuevos stores (Redis, MongoDB, etc.) sin refactor  
✅ **Mantenible**: Cada capa tiene responsabilidad única  
✅ **SOLID**: Todos los principios aplicados correctamente  
✅ **DIP**: Inversión de dependencias correcta (use cases no conocen infraestructura)  

## Próximos pasos

- **HU06:** Crear DI container (`app/di/container.py`)
- **HU07:** Crear VisionEdgeFrameAdapter (leer de Redis/HTTP vision_edge)
- **HU08:** Crear VisionEdgeMetricsAdapter (leer de Redis/HTTP vision_edge)
- **HU09:** Configurar container para cambiar entre Mock y VisionEdge vía env vars
- **HU10:** WebSockets para streaming en tiempo real

---

**✅ HU05 completado exitosamente. Arquitectura limpia implementada. Endpoints funcionando sin cambios externos. Preparado para integración con vision_edge.**
