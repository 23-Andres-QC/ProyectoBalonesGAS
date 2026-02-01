# HU-BACK-06: Dependency Injection Container

**Historia de Usuario:** Como Backend Developer, quiero un contenedor DI que gestione las dependencias de forma centralizada, para poder cambiar entre implementaciones Mock y VisionEdge sin modificar los endpoints.

---

## 📋 Objetivo

Implementar un Dependency Injection Container que permita:

1. **Inyección de Dependencias:** Wiring automático de stores → use cases → routes
2. **Configuración Dinámica:** Cambio Mock ↔ VisionEdge mediante env vars
3. **Fallback Resiliente:** Modo offline cuando vision_edge no responde
4. **Testing Simplificado:** Mock mode para desarrollo sin vision_edge activo

---

## 🏗️ Arquitectura

### Clean Architecture con DI

```
┌─────────────────────────────────────────────────┐
│          Presentation Layer (HTTP)              │
│  ┌────────────────────────────────────────┐     │
│  │  metrics_routes.py, frame_routes.py    │     │
│  └──────────────────┬──────────────────────┘    │
│                     │ imports container          │
└─────────────────────┼──────────────────────────┘
                      │
┌─────────────────────▼──────────────────────────┐
│           Dependency Injection (DI)            │
│  ┌────────────────────────────────────────┐    │
│  │         app/di/container.py            │    │
│  │  ┌──────────────────────────────┐      │    │
│  │  │  Container (Singleton)       │      │    │
│  │  │  - get_metrics_use_case      │      │    │
│  │  │  - get_latest_frame_use_case │      │    │
│  │  └──────────────────────────────┘      │    │
│  └─────────────┬────────────────────────────┘   │
└────────────────┼─────────────────────────────┘
                 │ wiring based on USE_VISION_EDGE
                 │
       ┌─────────▼────────────┐
       │ USE_VISION_EDGE?     │
       └─────────┬────────────┘
            ┌────┴────┐
            │         │
    False   │         │  True
            │         │
     ┌──────▼────┐ ┌──▼──────────────┐
     │   Mock    │ │  VisionEdge     │
     │   Stores  │ │  HTTP Adapters  │
     └───────────┘ └─────────────────┘
```

### Implementaciones Disponibles

| Componente         | Mock (Dev)                  | VisionEdge (Prod)                  |
|--------------------|-----------------------------|------------------------------------|
| **MetricsStore**   | `MockMetricsStore`          | `VisionEdgeMetricsAdapter`         |
| **FrameStore**     | `MockFrameStore`            | `VisionEdgeFrameAdapter`           |
| **Protocolo**      | `MetricsStorePort`          | `MetricsStorePort`                 |
| **Protocolo**      | `FrameStorePort`            | `FrameStorePort`                   |

---

## 📁 Archivos Modificados/Creados

### 1. **DI Container** (Nuevo)

**Archivo:** `app/di/container.py`

**Responsabilidad:** Wiring de dependencias según configuración

```python
class Container:
    def __init__(self) -> None:
        self._settings = get_settings()
        
        if self._settings.USE_VISION_EDGE:
            # Modo VisionEdge: HTTP adapters
            self.metrics_store = VisionEdgeMetricsAdapter(self._settings)
            self.frame_store = VisionEdgeFrameAdapter(self._settings)
        else:
            # Modo Mock: stores locales
            self.metrics_store = MockMetricsStore()
            self.frame_store = MockFrameStore()
        
        # Inyectar stores en use cases (DIP)
        self.get_metrics_use_case = GetMetrics(self.metrics_store)
        self.get_latest_frame_use_case = GetLatestFrame(self.frame_store)

# Singleton
container = Container()
```

### 2. **VisionEdge Metrics Adapter** (Nuevo)

**Archivo:** `app/infrastructure/adapters/vision_edge_metrics_adapter.py`

**Responsabilidad:** HTTP client para GET /metrics de vision_edge

**Características:**
- ✅ Mapea `stable_count` → `count` para contrato backend
- ✅ Fallback a `status="offline"` en timeout/error
- ✅ Soporta `Authorization: Bearer {API_KEY}`
- ✅ Timeout configurable vía `VISION_EDGE_TIMEOUT_SEC`

```python
def get_metrics(self) -> dict:
    try:
        url = f"{self._base_url}/metrics"
        response = httpx.get(url, headers=headers, timeout=self._timeout)
        data = response.json()
        return {
            "count": data.get("stable_count", 0),
            "fps": data.get("fps", 0.0),
            "status": data.get("status", "live"),
            "last_update": data.get("last_update_utc"),
        }
    except Exception:
        return {"count": 0, "fps": 0.0, "status": "offline", ...}
```

### 3. **VisionEdge Frame Adapter** (Nuevo)

**Archivo:** `app/infrastructure/adapters/vision_edge_frame_adapter.py`

**Responsabilidad:** HTTP client para GET /frame/raw.jpg y /frame/processed.jpg

**Características:**
- ✅ Fallback a placeholder JPEG en 404/timeout
- ✅ Valida `Content-Type: image/*`
- ✅ Reutiliza `get_placeholder_jpeg()` para consistency

```python
def get_raw(self) -> Optional[bytes]:
    return self._fetch_frame("/frame/raw.jpg")

def _fetch_frame(self, path: str) -> Optional[bytes]:
    try:
        response = httpx.get(f"{self._base_url}{path}", ...)
        return response.content
    except Exception:
        return get_placeholder_jpeg()
```

### 4. **Settings** (Extendido)

**Archivo:** `app/infrastructure/config/settings.py`

**Nuevos campos:**

```python
@dataclass
class Settings(BaseSettings):
    # Existing fields...
    APP_NAME: str = "API Server"
    APP_VERSION: str = "0.1.0"
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    
    # VisionEdge Integration (HU06)
    USE_VISION_EDGE: bool = False
    VISION_EDGE_BASE_URL: str = "http://127.0.0.1:8010"
    VISION_EDGE_TIMEOUT_SEC: float = 2.0
    VISION_EDGE_API_KEY: str = ""
```

### 5. **Routes** (Refactorizadas)

**Archivos:**
- `app/presentation/http/routes/metrics_routes.py`
- `app/presentation/http/routes/frame_routes.py`

**Antes (HU05):**
```python
# Manual instantiation
store = MockMetricsStore()
use_case = GetMetrics(store)
result = use_case.execute()
```

**Después (HU06):**
```python
# Dependency Injection
from app.di.container import container

@router.get("/api/metrics")
async def get_metrics():
    result = container.get_metrics_use_case.execute()
    return result
```

### 6. **Requirements** (Actualizado)

**Archivo:** `requirements.txt`

```txt
fastapi
uvicorn
pydantic
pydantic-settings
motor
redis
httpx  # ← Nuevo: HTTP client para VisionEdge
```

---

## 🧪 Pruebas

### Modo 1: Mock (Default)

```powershell
# No definir USE_VISION_EDGE o establecer en false
cd api_server

# Activar venv (VS Code lo hace automáticamente)
# .venv\Scripts\activate

# Instalar httpx
pip install httpx

# Levantar API en modo mock
uvicorn app.main:app --reload

# Probar endpoints
curl http://127.0.0.1:8000/api/metrics
# → {"count": 0, "fps": 0.0, "status": "mock", "last_update": "..."}

curl http://127.0.0.1:8000/api/frame/raw --output raw.jpg
# → Placeholder JPEG
```

**Expectativas:**
- ✅ `status: "mock"` en métricas
- ✅ `count: 0` fijo
- ✅ Placeholder JPEG en frames
- ✅ Sin errores aunque vision_edge esté offline

### Modo 2: VisionEdge (HTTP Integration)

```powershell
# Terminal 1: Levantar vision_edge
cd vision_edge
.venv\Scripts\activate
python app/main.py
# → Vision Edge running on 127.0.0.1:8010

# Terminal 2: Levantar API con env var
cd api_server
$env:USE_VISION_EDGE="true"
$env:VISION_EDGE_BASE_URL="http://127.0.0.1:8010"
uvicorn app.main:app --reload

# Probar endpoints
curl http://127.0.0.1:8000/api/metrics
# → {"count": 3, "fps": 25.4, "status": "live", "last_update": "..."}

curl http://127.0.0.1:8000/api/frame/processed --output processed.jpg
# → Frame con bounding boxes + count text
```

**Expectativas:**
- ✅ `status: "live"` con contador real
- ✅ FPS del stream
- ✅ Frames con detecciones renderizadas
- ✅ Fallback a "offline" si vision_edge se cae

### Modo 3: Resilient Fallback

```powershell
# Levantar API con USE_VISION_EDGE=true pero sin vision_edge activo
cd api_server
$env:USE_VISION_EDGE="true"
uvicorn app.main:app --reload

# Probar endpoints
curl http://127.0.0.1:8000/api/metrics
# → {"count": 0, "fps": 0.0, "status": "offline", "last_update": "..."}

curl http://127.0.0.1:8000/api/frame/raw --output raw.jpg
# → Placeholder JPEG (fallback)
```

**Expectativas:**
- ✅ `status: "offline"` indica vision_edge no alcanzable
- ✅ Placeholder JPEG en lugar de error 500
- ✅ Timeout rápido (2s default) para no bloquear
- ✅ API funcional aunque vision_edge falle

---

## 🔧 Troubleshooting

### Error: `ModuleNotFoundError: No module named 'httpx'`

```powershell
# Instalar httpx
pip install httpx

# Verificar
pip list | Select-String httpx
```

### Error: `Cannot import name 'container' from 'app.di.container'`

```powershell
# Verificar que container.py existe
Get-ChildItem api_server/app/di/container.py

# Verificar imports
Get-Content api_server/app/di/container.py | Select-String "container ="
```

### Métricas siempre en "offline" con USE_VISION_EDGE=true

```powershell
# Verificar que vision_edge está corriendo
curl http://127.0.0.1:8010/metrics

# Verificar env vars
$env:USE_VISION_EDGE
$env:VISION_EDGE_BASE_URL

# Verificar logs de httpx
# Agregar temporalmente a vision_edge_metrics_adapter.py:
# except Exception as e:
#     print(f"[VisionEdge] Error: {e}")
```

### Timeout muy largo

```powershell
# Ajustar timeout (default 2.0s)
$env:VISION_EDGE_TIMEOUT_SEC="1.0"
uvicorn app.main:app --reload
```

---

## 📚 Conceptos Aplicados

### 1. Dependency Inversion Principle (DIP)

```
High-level modules (routes) depend on abstractions (ports),
not on low-level modules (concrete stores).
```

**Beneficio:** Podemos cambiar MockMetricsStore → VisionEdgeMetricsAdapter sin tocar routes.

### 2. Dependency Injection (DI)

```
Dependencies are "injected" from outside, not created inside classes.
```

**Beneficio:** Testing simple (inyectar mocks), wiring centralizado.

### 3. Protocol Pattern (Duck Typing)

```python
class MetricsStorePort(Protocol):
    def get_metrics(self) -> dict: ...
```

**Beneficio:** MockMetricsStore y VisionEdgeMetricsAdapter implementan el mismo protocolo sin herencia.

### 4. Singleton Pattern

```python
container = Container()  # Una sola instancia
```

**Beneficio:** Una única configuración de dependencias para toda la app.

### 5. Adapter Pattern

```
VisionEdgeMetricsAdapter adapta la interfaz HTTP de vision_edge
a MetricsStorePort que espera la aplicación.
```

**Beneficio:** Aísla cambios en API externa de lógica interna.

---

## ✅ Checklist Implementación

- [x] Crear `app/di/container.py` con lógica de wiring
- [x] Crear `VisionEdgeMetricsAdapter` con httpx
- [x] Crear `VisionEdgeFrameAdapter` con httpx
- [x] Extender `settings.py` con env vars VisionEdge
- [x] Refactorizar `metrics_routes.py` para usar container
- [x] Refactorizar `frame_routes.py` para usar container
- [x] Agregar `httpx` a `requirements.txt`
- [x] Documentar HU06 en este archivo
- [ ] Probar modo mock (USE_VISION_EDGE=false)
- [ ] Probar modo integration (USE_VISION_EDGE=true)
- [ ] Probar fallback resilient (vision_edge offline)

---

## 🎯 Resultado Final

Con HU06 completado:

1. **Sin modificar routes:** Cambio Mock ↔ VisionEdge con env var
2. **Resiliente:** Fallback automático cuando vision_edge falla
3. **Testing:** Mock mode para desarrollo sin dependencias externas
4. **Escalable:** Agregar nuevos adapters (Redis, DB) sin cambiar use cases
5. **SOLID:** DIP + DI + Adapter pattern aplicados correctamente

---

**Próximos Pasos:**
- HU07: Integración UI → API (mostrar contador real en frontend)
- HU08: WebSocket real-time para métricas live
- HU09: Persistencia de eventos en MongoDB
