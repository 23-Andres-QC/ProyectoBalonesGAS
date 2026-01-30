# HU-VIS-07: MJPEG Live Streaming

**Historia de Usuario:** Como desarrollador del frontend (PyQt5/browser), necesito un endpoint de streaming MJPEG en tiempo real para visualizar el video procesado sin refrescar manualmente, para mostrar detecciones en vivo.

---

## 📋 Objetivo

Agregar endpoints de streaming MJPEG que:
- Transmiten video en tiempo real desde el pipeline de vision_edge
- Soportan múltiples clientes simultáneos
- Funcionan en navegadores y aplicaciones PyQt5
- NO requieren WebSockets ni infraestructura adicional

**Endpoints nuevos:**
- `GET /stream/raw.mjpg` - Stream del video RTSP sin procesar
- `GET /stream/processed.mjpg` - Stream con detecciones, línea y overlays

---

## 🏗️ Arquitectura

### MJPEG Streaming Flow

```
┌─────────────────────────────────────────────────┐
│         Pipeline Thread (Background)            │
│  RTSP → Detect → Track → Count → Render → Store│
│           ↓                                      │
│     InMemoryFrameStore (thread-safe)            │
│       get_frames() → (raw_jpeg, processed_jpeg) │
└──────────────────┬──────────────────────────────┘
                   │ read continuously
┌──────────────────▼──────────────────────────────┐
│         HTTP Streaming Generator                │
│  - Loop forever                                 │
│  - Read frames from store                       │
│  - Throttle to STREAM_FPS (default 15)          │
│  - Handle None frames (wait & retry)            │
│  - Catch client disconnect (GeneratorExit)      │
└──────────────────┬──────────────────────────────┘
                   │ yield MJPEG chunks
┌──────────────────▼──────────────────────────────┐
│    FastAPI StreamingResponse                    │
│  Content-Type: multipart/x-mixed-replace        │
│  --frame\r\n                                    │
│  Content-Type: image/jpeg\r\n                   │
│  Content-Length: {len}\r\n\r\n                  │
│  {jpeg_bytes}\r\n                               │
└─────────────────────────────────────────────────┘
                   │
         ┌─────────┴─────────┐
         ↓                   ↓
    Browser Client      PyQt5 Client
```

---

## 📁 Archivos Creados/Modificados

### 1. **Settings Extendidos** (Modificado)

**Archivo:** `app/infrastructure/config/settings.py`

```python
@dataclass(frozen=True)
class Settings:
    # ... existing fields ...
    # HU-VIS-07: MJPEG Streaming
    stream_fps: int
```

**Default:**
```python
stream_fps=int(os.getenv("STREAM_FPS", "15")),
```

**Nota:** FPS del stream puede ser menor que el pipeline FPS (~30). Esto reduce bandwidth sin perder calidad significativa.

---

### 2. **Stream Routes** (Nuevo)

**Archivo:** `app/presentation/http/routes/stream_routes.py`

**Funciones principales:**

#### `create_stream_router(frame_store, settings)`
Crea router con endpoints de streaming.

#### `generate_mjpeg_stream(use_processed: bool)`
Generador que:
- Lee frames del `frame_store.get_frames()`
- Si frame es `None`: espera 50ms y continúa (no crashea)
- Formatea cada frame como chunk MJPEG:
  ```
  --frame\r\n
  Content-Type: image/jpeg\r\n
  Content-Length: {len(jpeg_bytes)}\r\n\r\n
  {jpeg_bytes}\r\n
  ```
- Throttling: `sleep(1.0 / stream_fps)` para controlar bitrate
- Maneja disconnect: `except GeneratorExit` cuando cliente cierra

#### Endpoints:

**GET /stream/raw.mjpg**
```python
@router.get("/raw.mjpg")
async def stream_raw():
    return StreamingResponse(
        generate_mjpeg_stream(use_processed=False),
        media_type="multipart/x-mixed-replace; boundary=frame",
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Connection": "close",
        },
    )
```

**GET /stream/processed.mjpg**
```python
@router.get("/processed.mjpg")
async def stream_processed():
    return StreamingResponse(
        generate_mjpeg_stream(use_processed=True),
        media_type="multipart/x-mixed-replace; boundary=frame",
        headers={...},
    )
```

**Headers explicados:**
- `Cache-Control: no-store` - No cachear frames (son time-sensitive)
- `Pragma: no-cache` - Compatibilidad con HTTP/1.0
- `Connection: close` - Evitar keep-alive issues en algunos clientes

---

### 3. **App Factory** (Modificado)

**Archivo:** `app/presentation/http/app_factory.py`

```python
from app.infrastructure.config.settings import Settings
from app.presentation.http.routes.stream_routes import create_stream_router

def create_app(
    service_name: str,
    version: str,
    frame_store: FrameStore,
    metrics_store: MetricsStore,
    settings: Settings,  # NEW parameter
) -> FastAPI:
    # ...
    app.include_router(create_stream_router(frame_store, settings))  # HU-VIS-07
    return app
```

**Cambio:** Ahora `create_app` requiere `settings` para pasar `stream_fps` al router de streaming.

---

### 4. **Main Service** (Modificado)

**Archivo:** `app/main.py`

```python
def run_service(settings):
    # ...
    print(f"Stream FPS: {settings.stream_fps} (HU-VIS-07)")
    
    app = create_app(
        service_name="vision_edge",
        version=settings.api_version,
        frame_store=frame_store,
        metrics_store=metrics_store,
        settings=settings,  # NEW: pass settings to app_factory
    )
```

---

## 🧪 Cómo Ejecutar

### Modo Service con Streaming

```powershell
cd vision_edge
.\.venv\Scripts\Activate.ps1

# Configurar variables
$env:VISION_MODE = "service"
$env:RTSP_URL = "rtsp://localhost:8554/stream"
$env:LINE_Y = "450"
$env:STREAM_FPS = "15"      # Optional: default 15 FPS

# Ejecutar
python -m app.main
```

**Salida esperada:**
```
==================================================
Vision Edge - HTTP Service Mode (HU-VIS-05, HU-VIS-06v, HU-VIS-07)
==================================================
API Host: 127.0.0.1
API Port: 8010
API Version: 0.1.0
RTSP URL: rtsp://localhost:8554/stream
Model: assets/models/best.pt
Pipeline Sleep: 0.03s (~33 FPS)
Line Y: 450 (HU-VIS-06v)
Stream FPS: 15 (HU-VIS-07)
==================================================
INFO:     Started server process [12345]
INFO:     Uvicorn running on http://0.0.0.0:8010
```

---

## 🔬 Cómo Probar

### 1. Stream Procesado en Browser

**Abre en navegador:**
```
http://127.0.0.1:8010/stream/processed.mjpg
```

**Expectativa:**
- Video en tiempo real con:
  - Bounding boxes de detecciones
  - Línea horizontal amarilla (HU-VIS-06v)
  - Overlay con contadores:
    - "Stable: X" (verde)
    - "Line: Y (in:A out:B)" (naranja)
- Actualización continua (~15 FPS)
- No requiere refrescar página

### 2. Stream Raw en Browser

**Abre en navegador:**
```
http://127.0.0.1:8010/stream/raw.mjpg
```

**Expectativa:**
- Video original del RTSP sin procesar
- Sin overlays ni detecciones
- Útil para comparar input vs output

### 3. Múltiples Clientes

**Escenario:** Abrir ambos streams en pestañas diferentes.

```
Tab 1: http://127.0.0.1:8010/stream/processed.mjpg
Tab 2: http://127.0.0.1:8010/stream/raw.mjpg
Tab 3: http://127.0.0.1:8010/stream/processed.mjpg (duplicado)
```

**Expectativa:**
- Los 3 streams funcionan simultáneamente
- No hay interferencia entre clientes
- frame_store maneja concurrencia con Lock

### 4. Endpoints Anteriores Intactos

```powershell
# Health
curl http://127.0.0.1:8010/health

# Metrics
curl http://127.0.0.1:8010/metrics

# Single frame (raw)
curl http://127.0.0.1:8010/frame/raw.jpg --output test_raw.jpg

# Single frame (processed)
curl http://127.0.0.1:8010/frame/processed.jpg --output test_processed.jpg
```

**Expectativa:** Todos siguen funcionando como antes (backward compatibility).

---

## 🖼️ HTML Test Page (Opcional)

Para probar ambos streams simultáneamente, crea `test_stream.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Vision Edge Streams</title>
    <style>
        body { 
            background: #1a1a1a; 
            color: white; 
            font-family: monospace; 
            padding: 20px;
        }
        .stream-container {
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }
        .stream {
            border: 2px solid #333;
            padding: 10px;
            background: #2a2a2a;
        }
        img {
            max-width: 640px;
            border: 1px solid #555;
        }
        h2 {
            margin-top: 0;
            color: #4CAF50;
        }
    </style>
</head>
<body>
    <h1>🎥 Vision Edge - Live Streams (HU-VIS-07)</h1>
    
    <div class="stream-container">
        <div class="stream">
            <h2>Raw Stream</h2>
            <img src="http://127.0.0.1:8010/stream/raw.mjpg" alt="Raw MJPEG Stream">
        </div>
        
        <div class="stream">
            <h2>Processed Stream (with detections)</h2>
            <img src="http://127.0.0.1:8010/stream/processed.mjpg" alt="Processed MJPEG Stream">
        </div>
    </div>
    
    <p>
        <a href="http://127.0.0.1:8010/metrics" target="_blank">📊 View Metrics</a> |
        <a href="http://127.0.0.1:8010/docs" target="_blank">📚 API Docs</a>
    </p>
</body>
</html>
```

**Uso:**
```powershell
# Open in browser
Start-Process test_stream.html
```

---

## 🔧 Troubleshooting

### Stream no carga / "Loading..." infinito

**Causa 1:** Pipeline no está generando frames.

**Diagnóstico:**
```powershell
curl http://127.0.0.1:8010/frame/processed.jpg --output test.jpg
```

Si devuelve 404 o error → pipeline no está corriendo.

**Solución:**
- Verificar RTSP_URL está accesible
- Ver logs del pipeline: `[RunPipeline] Processed: ...`

---

**Causa 2:** Firewall bloquea streaming.

**Solución:**
```powershell
# Allow port 8010
New-NetFirewallRule -DisplayName "Vision Edge" -Direction Inbound -LocalPort 8010 -Protocol TCP -Action Allow
```

---

### Stream muy lento / laggy

**Causa:** STREAM_FPS demasiado alto para el ancho de banda.

**Solución:**
```powershell
$env:STREAM_FPS = "10"  # Reduce from 15 to 10
python -m app.main
```

**Trade-off:**
- FPS más bajo = menos bandwidth, menos smooth
- FPS más alto = más bandwidth, más smooth

**Recomendación:** 10-15 FPS es óptimo para monitoring (30 FPS es overkill).

---

### Browser muestra frames "congelados"

**Causa:** Cache del browser está sirviendo frames viejos.

**Solución:**
```
Ctrl+Shift+R  (hard refresh)
```

O verificar headers de respuesta incluyen `Cache-Control: no-store`.

---

### Múltiples clientes causan stuttering

**Expectativa:** frame_store es thread-safe, DEBERÍA soportar múltiples lectores.

**Si ocurre:** Verificar que `InMemoryFrameStore` usa `Lock` correctamente:

```python
# app/infrastructure/stores/in_memory_frame_store.py
def get_frames(self) -> tuple[bytes | None, bytes | None]:
    with self._lock:
        return self._raw_jpeg, self._processed_jpeg
```

---

### Cliente PyQt5 no muestra stream

**Causa:** PyQt5 requiere manejo específico de MJPEG.

**Solución:** Usar `QNetworkAccessManager` con `QMovie` o `QImageReader`:

```python
# PyQt5 example (pseudocode)
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PyQt5.QtCore import QUrl

manager = QNetworkAccessManager()
request = QNetworkRequest(QUrl("http://127.0.0.1:8010/stream/processed.mjpg"))
reply = manager.get(request)

# Parse multipart/x-mixed-replace manually
# Extract JPEG frames from --frame boundaries
```

**Alternativa:** Usar `cv2.VideoCapture`:

```python
import cv2

cap = cv2.VideoCapture("http://127.0.0.1:8010/stream/processed.mjpg")

while True:
    ret, frame = cap.read()
    if not ret:
        break
    # Display frame in PyQt5 widget
    cv2.imshow("Stream", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
```

---

## 📊 Comparación: Single Frame vs Streaming

| Aspecto              | GET /frame/processed.jpg | GET /stream/processed.mjpg |
|----------------------|--------------------------|----------------------------|
| **Uso**              | Snapshot único           | Video continuo             |
| **Actualización**    | Manual (polling)         | Automática (push)          |
| **Bandwidth**        | Bajo (1 frame)           | Medio (15 FPS)             |
| **Latencia**         | Alta (depende de polling)| Baja (~67ms @ 15 FPS)      |
| **Browser support**  | Universal                | Chrome, Firefox, Edge      |
| **Best for**         | API integrations         | Live monitoring UI         |

---

## 🎯 Resultado Final

Con HU-VIS-07 completado:

1. ✅ **Live Streaming:** MJPEG endpoints con video en tiempo real
2. ✅ **Multi-cliente:** Soporta múltiples browsers/apps simultáneamente
3. ✅ **Throttling:** Configurable via STREAM_FPS (default 15 FPS)
4. ✅ **Graceful Handling:** Maneja disconnect, None frames, errores
5. ✅ **Backward Compatible:** Endpoints previos (/frame, /metrics, /health) intactos
6. ✅ **No Cache:** Headers correctos para video time-sensitive
7. ✅ **Browser Ready:** Funciona directo en `<img src="...">` tag

---

## 📚 Conceptos Aplicados

### 1. HTTP Streaming con Multipart

**Content-Type: multipart/x-mixed-replace**
- HTTP estándar para streaming
- Cada "part" es un frame JPEG completo
- Boundary `--frame` separa frames
- Browser procesa automáticamente (no requiere JS)

### 2. Generator-based Streaming

```python
def generate_mjpeg_stream():
    while True:
        yield frame_chunk
```

- FastAPI StreamingResponse consume generator
- Generator mantiene estado entre yields
- `GeneratorExit` detecta disconnect del cliente
- Memory-efficient (solo 1 frame en memoria por cliente)

### 3. Frame Store como Single Source of Truth

```
Pipeline (writer) → FrameStore ← Multiple stream clients (readers)
```

- Pipeline escribe 1 vez por frame
- N clientes leen independientemente
- Lock protege concurrencia
- No duplicación de frames en memoria

### 4. Graceful Degradation

```python
if jpeg_bytes is None:
    time.sleep(0.05)
    continue
```

- Si pipeline está atrasado → espera
- Si RTSP disconnected temporalmente → no crashea stream
- Cliente ve "freeze" en lugar de error 500

---

## ✅ Checklist de Validación

- [x] Settings extendido con STREAM_FPS (default 15)
- [x] stream_routes.py creado con /stream/raw.mjpg y /stream/processed.mjpg
- [x] app_factory.py incluye stream router y recibe settings
- [x] main.py pasa settings a create_app()
- [x] MJPEG multipart/x-mixed-replace format correcto
- [x] Headers no-cache configurados
- [x] Throttling a STREAM_FPS implementado
- [x] Manejo de None frames (wait & retry)
- [x] Manejo de client disconnect (GeneratorExit)
- [x] Múltiples clientes soportados (thread-safe)
- [x] Endpoints previos no afectados (backward compatibility)
- [x] Logs muestran Stream FPS al iniciar service

---

**Próximos Pasos:**
- HU-VIS-08: WebSocket para métricas en tiempo real (alternativa a polling /metrics)
- HU-VIS-09: Implementar ByteTrackTracker completo para mejorar line crossing
- HU-FRONT-01: Integrar streams en UI PyQt5/React
