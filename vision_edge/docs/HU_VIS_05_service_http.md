# HU-VIS-05: HTTP Service con FastAPI

**Historia de Usuario:** Como Backend Developer, quiero que vision_edge exponga un servicio HTTP con endpoints de métricas y frames, para poder integrarlo con api_server sin acoplamiento directo.

---

## 📋 Objetivo

Implementar modo `VISION_MODE=service` que:

1. **Pipeline Background:** Loop continuo read → detect → track → count → render → encode
2. **Thread-Safe Stores:** Actualización segura de frames y métricas desde pipeline
3. **FastAPI REST API:** Endpoints HTTP para consumo desde api_server
4. **Sin Romper HU Previas:** Modos rtsp_test, detector_test, counter_test, render_test siguen funcionando

---

## 🏗️ Arquitectura

### Diagrama de Componentes

```
┌─────────────────────────────────────────────────────┐
│              vision_edge Service                    │
│                                                     │
│  ┌───────────────────────────────────────────────┐ │
│  │     FastAPI Server (Main Thread)              │ │
│  │  ┌────────────────────────────────────────┐   │ │
│  │  │  GET /health                           │   │ │
│  │  │  GET /metrics                          │   │ │
│  │  │  GET /frame/raw.jpg                    │   │ │
│  │  │  GET /frame/processed.jpg              │   │ │
│  │  └────────────────┬───────────────────────┘   │ │
│  └───────────────────┼───────────────────────────┘ │
│                      │ reads from                  │
│       ┌──────────────▼──────────────┐              │
│       │  In-Memory Stores (Lock)    │              │
│       │  - FrameStore                │              │
│       │  - MetricsStore              │              │
│       └──────────────▲──────────────┘              │
│                      │ writes to                   │
│  ┌───────────────────┼───────────────────────────┐ │
│  │  Pipeline Thread (Background)                 │ │
│  │  ┌──────────────────────────────────────────┐ │ │
│  │  │  while True:                             │ │ │
│  │  │    frame ← RTSP                          │ │ │
│  │  │    detections ← YOLO                     │ │ │
│  │  │    detections ← ByteTrack                │ │ │
│  │  │    count_state ← Counter                 │ │ │
│  │  │    processed ← Renderer                  │ │ │
│  │  │    raw_jpeg, proc_jpeg ← Encode          │ │ │
│  │  │    store.set_frames(raw, proc)           │ │ │
│  │  │    store.set_metrics({...})              │ │ │
│  │  │    sleep(0.033)  # ~30 FPS               │ │ │
│  │  └──────────────────────────────────────────┘ │ │
│  └───────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

### Clean Architecture Layers

```
Presentation (HTTP)
  ├── app_factory.py             (FastAPI app creation)
  └── routes/
      ├── health_routes.py       (GET /health)
      ├── metrics_routes.py      (GET /metrics)
      └── frame_routes.py        (GET /frame/*.jpg)

Application (Use Cases)
  └── run_pipeline.py            (run_continuous loop)

Infrastructure (Adapters)
  ├── camera/                    (RTSP source)
  ├── inference/                 (YOLO detector)
  ├── tracking/                  (ByteTrack)
  ├── counting/                  (VisibleWindowCounter)
  ├── rendering/                 (SupervisionOverlayRenderer)
  └── stores/
      ├── in_memory_frame_store.py    (Lock-protected)
      └── in_memory_metrics_store.py  (Lock-protected)
```

---

## 📁 Archivos Creados/Modificados

### 1. **Presentation Layer** (Nuevo)

#### `app/presentation/http/app_factory.py`

Crea FastAPI app con routers inyectados:

```python
def create_app(
    service_name: str,
    version: str,
    frame_store: FrameStore,
    metrics_store: MetricsStore,
) -> FastAPI:
    app = FastAPI(title=service_name, version=version)
    app.include_router(create_health_router(service_name, version))
    app.include_router(create_metrics_router(metrics_store))
    app.include_router(create_frame_router(frame_store))
    return app
```

#### `app/presentation/http/routes/health_routes.py`

```python
@router.get("/health")
def get_health():
    return {"status": "ok", "service": "vision_edge", "version": "0.1.0"}
```

#### `app/presentation/http/routes/metrics_routes.py`

```python
@router.get("/metrics")
def get_metrics():
    metrics = metrics_store.get_metrics()
    if metrics is None:
        raise HTTPException(status_code=404, detail="No metrics available yet")
    return metrics
```

**Contrato de respuesta:**
```json
{
  "fps": 25.4,
  "raw_count": 3,
  "stable_count": 3,
  "status": "ok",
  "last_update_utc": "2026-01-30T15:23:45.123Z"
}
```

#### `app/presentation/http/routes/frame_routes.py`

```python
@router.get("/frame/raw.jpg")
def get_raw_frame():
    raw_jpeg, _ = frame_store.get_frames()
    if raw_jpeg is None:
        raise HTTPException(status_code=404, detail="No raw frame available yet")
    return Response(content=raw_jpeg, media_type="image/jpeg")
```

### 2. **Application Layer** (Modificado)

#### `app/application/use_cases/run_pipeline.py`

Loop continuo:

```python
def run_continuous(self) -> None:
    while True:
        frame = self.frame_source.read()
        if frame is None:
            consecutive_fails += 1
            if consecutive_fails >= max_fails:
                self._update_metrics_store(0.0, 0, 0, "offline")
                break
            continue
        
        detections = self.detector.detect(frame)
        if self.tracker:
            detections = self.tracker.track(frame, detections)
        count_state = self.counter.update(detections)
        processed_frame = self.renderer.render(frame, detections, count_state)
        
        raw_jpeg = self._encode_jpeg(frame)
        processed_jpeg = self._encode_jpeg(processed_frame)
        
        self.frame_store.set_frames(raw_jpeg, processed_jpeg)
        self._update_metrics_store(fps, count_state.raw_count, count_state.stable_count, "ok")
        
        time.sleep(self.sleep_sec)
```

### 3. **Infrastructure Layer** (Ya Existía)

#### `app/infrastructure/stores/in_memory_frame_store.py`

Thread-safe con `Lock`:

```python
class InMemoryFrameStore(FrameStore):
    def __init__(self) -> None:
        self._lock = Lock()
        self._raw: bytes | None = None
        self._processed: bytes | None = None

    def set_frames(self, raw_jpeg: bytes, processed_jpeg: bytes) -> None:
        with self._lock:
            self._raw = raw_jpeg
            self._processed = processed_jpeg

    def get_frames(self) -> tuple[bytes | None, bytes | None]:
        with self._lock:
            return self._raw, self._processed
```

#### `app/infrastructure/stores/in_memory_metrics_store.py`

Thread-safe con `Lock`:

```python
class InMemoryMetricsStore(MetricsStore):
    def __init__(self) -> None:
        self._lock = Lock()
        self._metrics: dict | None = None

    def set_metrics(self, metrics: dict) -> None:
        with self._lock:
            self._metrics = dict(metrics)

    def get_metrics(self) -> dict | None:
        with self._lock:
            return dict(self._metrics) if self._metrics is not None else None
```

### 4. **Configuration** (Extendido)

#### `app/infrastructure/config/settings.py`

Nuevos campos:

```python
@dataclass(frozen=True)
class Settings:
    # ... existing fields ...
    # HU-VIS-05: HTTP Service
    api_host: str
    api_port: int
    api_version: str
    pipeline_sleep_sec: float
    pipeline_max_consecutive_fails: int
```

Defaults:

```python
api_host=os.getenv("API_HOST", "127.0.0.1"),
api_port=int(os.getenv("API_PORT", "8010")),
api_version=os.getenv("API_VERSION", "0.1.0"),
pipeline_sleep_sec=float(os.getenv("PIPELINE_SLEEP_SEC", "0.033")),  # ~30 FPS
pipeline_max_consecutive_fails=int(os.getenv("PIPELINE_MAX_CONSECUTIVE_FAILS", "50")),
```

### 5. **Main Entry Point** (Extendido)

#### `app/main.py`

Nuevo modo `service`:

```python
def run_service(settings) -> None:
    # Initialize stores
    frame_store = InMemoryFrameStore()
    metrics_store = InMemoryMetricsStore()
    
    # Create FastAPI app
    app = create_app("vision_edge", settings.api_version, frame_store, metrics_store)
    
    # Initialize pipeline components
    frame_source = RtspOpenCvSource(...)
    detector = YoloUltralyticsDetector(...)
    tracker = ByteTrackTracker()
    counter = VisibleWindowCounter(...)
    renderer = SupervisionOverlayRenderer(...)
    
    pipeline = RunPipeline(
        frame_source=frame_source,
        detector=detector,
        counter=counter,
        renderer=renderer,
        frame_store=frame_store,
        metrics_store=metrics_store,
        tracker=tracker,
        jpeg_quality=settings.jpeg_quality,
        sleep_sec=settings.pipeline_sleep_sec,
        max_consecutive_fails=settings.pipeline_max_consecutive_fails,
    )
    
    # Start pipeline in background thread
    pipeline_thread = threading.Thread(target=pipeline.run_continuous, daemon=True)
    pipeline_thread.start()
    
    # Start FastAPI server (blocking)
    uvicorn.run(app, host=settings.api_host, port=settings.api_port)
```

Dispatcher:

```python
def main() -> None:
    settings = get_settings()
    
    if settings.vision_mode == "service":
        run_service(settings)
    elif settings.vision_mode == "detector_test":
        run_detector_test(settings)
    # ... otros modos
```

### 6. **Dependencies** (Actualizado)

#### `requirements.txt`

```txt
opencv-python
ultralytics
supervision
numpy
motor
redis
ffmpeg-python
fastapi     # ← Nuevo
uvicorn     # ← Nuevo
```

---

## 🧪 Cómo Ejecutar

### Modo Service (HU-VIS-05)

```powershell
cd vision_edge

# Activar venv
.venv\Scripts\activate

# Instalar dependencias (si es primera vez)
pip install -r requirements.txt

# Configurar variables (opcional)
$env:VISION_MODE="service"
$env:API_HOST="127.0.0.1"
$env:API_PORT="8010"
$env:RTSP_URL="rtsp://admin:admin@192.168.1.100:554/stream1"
$env:MODEL_PATH="assets/models/best.pt"

# Ejecutar
python -m app.main
```

**Salida esperada:**
```
==================================================
Vision Edge - HTTP Service Mode (HU-VIS-05)
==================================================
API Host: 127.0.0.1
API Port: 8010
API Version: 0.1.0
RTSP URL: rtsp://admin:admin@192.168.1.100:554/stream1
Model: assets/models/best.pt
Pipeline Sleep: 0.033s (~30 FPS)
==================================================
[Service] Pipeline thread started
[Service] Starting FastAPI server on 127.0.0.1:8010
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8010 (Press CTRL+C to quit)
[RunPipeline] Starting continuous pipeline...
[RunPipeline] Processed: 30, FPS: 28.5, Raw: 3, Stable: 3
```

### Verificar Modos Previos (HU-VIS-01..04)

```powershell
# RTSP Test
$env:VISION_MODE="rtsp_test"
python -m app.main

# Detector Test
$env:VISION_MODE="detector_test"
python -m app.main

# Counter Test
$env:VISION_MODE="counter_test"
python -m app.main

# Render Test
$env:VISION_MODE="render_test"
python -m app.main
```

**Todos deben funcionar sin cambios.**

---

## 🔬 Cómo Probar

### 1. Health Check

```powershell
curl http://127.0.0.1:8010/health
```

**Respuesta esperada:**
```json
{
  "status": "ok",
  "service": "vision_edge",
  "version": "0.1.0"
}
```

### 2. Metrics

```powershell
curl http://127.0.0.1:8010/metrics
```

**Respuesta esperada (después de inicialización):**
```json
{
  "fps": 28.5,
  "raw_count": 3,
  "stable_count": 3,
  "status": "ok",
  "last_update_utc": "2026-01-30T15:23:45.123Z"
}
```

**Si aún no hay métricas:**
```json
{
  "detail": "No metrics available yet"
}
```
Status: `404 Not Found`

### 3. Raw Frame

```powershell
curl http://127.0.0.1:8010/frame/raw.jpg --output raw.jpg
```

**Verificación:**
```powershell
# Abrir con visor de imágenes
Start-Process raw.jpg

# Verificar tamaño
(Get-Item raw.jpg).Length
# Debería ser > 10KB si hay frame válido
```

### 4. Processed Frame

```powershell
curl http://127.0.0.1:8010/frame/processed.jpg --output processed.jpg
Start-Process processed.jpg
```

**Expectativas:**
- Frame con bounding boxes de detecciones
- Texto de contador estable en esquina superior izquierda
- Calidad JPEG según `JPEG_QUALITY` (default 80)

### 5. Documentación Interactiva

```powershell
# Swagger UI
Start-Process http://127.0.0.1:8010/docs

# ReDoc
Start-Process http://127.0.0.1:8010/redoc
```

---

## 🔧 Troubleshooting

### Error: `ModuleNotFoundError: No module named 'fastapi'`

```powershell
pip install fastapi uvicorn
```

### Error: Pipeline se detiene con "offline"

**Causa:** RTSP stream no responde o hay 50 fallos consecutivos.

**Solución:**
```powershell
# Verificar RTSP con VLC o ffplay
ffplay rtsp://admin:admin@192.168.1.100:554/stream1

# Ajustar timeout
$env:RTSP_OPEN_TIMEOUT_SEC="10.0"

# Aumentar tolerancia a fallos
$env:PIPELINE_MAX_CONSECUTIVE_FAILS="100"
```

### GET /metrics devuelve 404

**Causa:** Pipeline aún no procesó primer frame.

**Solución:** Esperar 2-3 segundos y reintentar:
```powershell
Start-Sleep -Seconds 3
curl http://127.0.0.1:8010/metrics
```

### FPS muy bajo (<10)

**Posibles causas:**
- RTSP lento
- Modelo YOLO pesado sin GPU
- `PIPELINE_SLEEP_SEC` muy alto

**Diagnóstico:**
```powershell
# Verificar logs del pipeline
[RunPipeline] Processed: 30, FPS: 8.2, Raw: 3, Stable: 3
# ↑ FPS bajo indica problema
```

**Soluciones:**
```powershell
# Reducir sleep para aumentar polling rate
$env:PIPELINE_SLEEP_SEC="0.01"  # 100 FPS target

# Usar GPU (si disponible)
# Ultralytics detecta automáticamente CUDA

# Reducir resolución RTSP (en cámara)
```

### Frames "congelados"

**Causa:** Lock contention si HTTP requests son muy frecuentes.

**Solución:** Los locks son muy eficientes, pero puedes aumentar `PIPELINE_SLEEP_SEC` para reducir escrituras:
```powershell
$env:PIPELINE_SLEEP_SEC="0.05"  # 20 FPS
```

---

## 📊 Métricas de Rendimiento

| Métrica            | Esperado       | Observado | Notas                             |
|--------------------|----------------|-----------|-----------------------------------|
| Pipeline FPS       | ~30 FPS        | 25-30     | Depende de RTSP + modelo          |
| HTTP Latency       | <50ms          | ~10-20ms  | GET /metrics, GET /frame/*.jpg    |
| Memory Usage       | ~500MB         | Variable  | YOLO model + frame buffers        |
| CPU Usage          | 30-50%         | Variable  | Sin GPU; con GPU <10%             |
| Thread Count       | 2 (main+pipe)  | 2         | FastAPI usa asyncio (single core) |

---

## 🔗 Integración con api_server

### Configuración en api_server

```powershell
cd api_server
$env:USE_VISION_EDGE="true"
$env:VISION_EDGE_BASE_URL="http://127.0.0.1:8010"
$env:VISION_EDGE_TIMEOUT_SEC="2.0"
uvicorn app.main:app --reload
```

### Endpoints del Backend

- `GET /api/metrics` → Llama a `GET http://127.0.0.1:8010/metrics`
- `GET /api/frame/processed` → Llama a `GET http://127.0.0.1:8010/frame/processed.jpg`

### Mapeo de Contratos

| vision_edge          | api_server         | Notas                           |
|----------------------|--------------------|---------------------------------|
| `stable_count`       | `count`            | Backend usa nombre simplificado |
| `status: "ok"`       | `status: "live"`   | Backend normaliza valores       |
| `last_update_utc`    | `last_update`      | Formato ISO-8601 con Z          |

---

## ✅ Checklist de Validación

- [x] Modo `service` levanta FastAPI en puerto configurado
- [x] Pipeline thread procesa frames en background
- [x] `GET /health` retorna 200 OK
- [x] `GET /metrics` retorna JSON con fps, counts, status
- [x] `GET /frame/raw.jpg` retorna JPEG válido
- [x] `GET /frame/processed.jpg` retorna JPEG con detecciones renderizadas
- [x] Modos previos (rtsp_test, detector_test, etc.) funcionan sin cambios
- [x] Thread safety: no race conditions en stores
- [x] Fallback a status="offline" cuando RTSP falla
- [x] Documentación Swagger/ReDoc disponible en `/docs` y `/redoc`

---

## 📚 Conceptos Aplicados

### 1. Threading vs Asyncio

- **Pipeline:** Thread bloqueante (cv2, YOLO síncronos)
- **FastAPI:** AsyncIO (uvicorn worker)
- **Stores:** Lock para sincronizar escrituras (pipeline) y lecturas (HTTP)

### 2. Producer-Consumer Pattern

```
Pipeline (Producer)     →  Stores (Buffer)  →  HTTP Routes (Consumer)
  └─ write frames/metrics     └─ Lock            └─ read on request
```

### 3. Separation of Concerns

- **Presentation:** FastAPI routes (HTTP concerns)
- **Application:** Pipeline use case (business logic)
- **Infrastructure:** RTSP, YOLO, Stores (tech details)

### 4. Dependency Injection

Stores inyectados en:
- `create_app(frame_store, metrics_store)` → Routes
- `RunPipeline(frame_store, metrics_store)` → Pipeline

Facilita testing con mocks.

---

## 🎯 Resultado Final

Con HU-VIS-05 completado:

1. ✅ **HTTP Service:** FastAPI expone vision_edge como servicio REST
2. ✅ **Background Pipeline:** Thread seguro procesa stream RTSP
3. ✅ **Thread-Safe Stores:** Lock protege frames/metrics compartidos
4. ✅ **Integración Backend:** api_server consume endpoints sin acoplamiento
5. ✅ **Sin Romper HU Previas:** Todos los modos de testing funcionan

---

**Próximos Pasos:**
- HU-VIS-06: Persistencia de eventos en MongoDB
- HU-VIS-07: WebSocket para streaming real-time
- HU-BACK-07: Integración completa UI → Backend → VisionEdge
