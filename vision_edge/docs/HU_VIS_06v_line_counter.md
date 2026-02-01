# HU-VIS-06v: Line Crossing Counter (MINIMAL VERSION)

**Historia de Usuario:** Como desarrollador del backend, necesito que vision_edge cuente cuántos balones cruzan una línea horizontal (entrada/salida) para enviar esta métrica al API server.

**Versión:** MINIMAL - Sin crear ports ni adapters adicionales, implementación inline en el pipeline.

---

## Objetivo

Agregar conteo de línea cruzada usando `supervision.LineZone` directamente en el pipeline, sin crear nuevas capas de abstracción (ports/adapters).

---

## Implementación

### 1. Settings (Configuración de Línea)

**Archivo:** `app/infrastructure/config/settings.py`

**Cambios:**
- Agregadas variables de entorno:
  - `LINE_Y=450` (posición Y de la línea)
  - `LINE_THICKNESS=2` (grosor de la línea)
  - `LINE_TEXT_SCALE=0.6` (escala del texto de línea)

**Código:**
```python
@dataclass
class Settings:
    # ... existing fields ...
    line_y: int
    line_thickness: int
    line_text_scale: float

def get_settings() -> Settings:
    return Settings(
        # ... existing settings ...
        line_y=int(os.getenv("LINE_Y", "450")),
        line_thickness=int(os.getenv("LINE_THICKNESS", "2")),
        line_text_scale=float(os.getenv("LINE_TEXT_SCALE", "0.6")),
    )
```

---

### 2. Pipeline (LineZone Inline)

**Archivo:** `app/application/use_cases/run_pipeline.py`

**Cambios:**
- Agregados campos inline para configuración de línea en el dataclass `RunPipeline`
- En `run_continuous()`:
  - Se crea `sv.LineZone` inline cuando cambia el tamaño del frame
  - Se llama `line_zone.trigger(detections)` cuando hay `tracker_id`
  - Se leen las propiedades `line_zone.in_count`, `line_zone.out_count` (NO valores de retorno de trigger)
  - Se envían `line_in`, `line_out`, `line_total` al `metrics_store` y al `renderer`

**Código clave:**
```python
# Initialize LineZone if frame size changed
frame_h, frame_w = frame.shape[:2]
if (frame_w, frame_h) != last_frame_shape:
    line_y_clamped = max(0, min(self.line_y, frame_h - 1))
    line_zone = sv.LineZone(
        start=sv.Point(x=0, y=line_y_clamped),
        end=sv.Point(x=frame_w - 1, y=line_y_clamped),
        triggering_anchors=(sv.Position.CENTER,)
    )
    last_frame_shape = (frame_w, frame_h)

# Line crossing count (HU-VIS-06v minimal)
line_in = 0
line_out = 0
line_total = 0
if line_zone is not None:
    if hasattr(detections, 'tracker_id') and detections.tracker_id is not None:
        line_zone.trigger(detections)  # Void method
        line_in = line_zone.in_count    # Read property
        line_out = line_zone.out_count  # Read property
        line_total = line_in + line_out
```

**Importante:**
- `line_zone.trigger(detections)` NO retorna valores, es un método void
- Los conteos se leen de las propiedades `in_count` y `out_count` DESPUÉS de llamar a `trigger()`
- Si no hay `tracker_id`, no se puede detectar cruces (graceful degradation)

---

### 3. Renderer (Dibujar Línea y Texto)

**Archivo:** `app/infrastructure/rendering/supervision_overlay_renderer.py`

**Cambios:**
- `render()` recibe `line_info` dict con `line_y`, `line_in`, `line_out`, `line_total`, `line_thickness`, `line_text_scale`
- `_draw_line_crossing()` dibuja línea horizontal amarilla
- `_draw_count_text()` muestra overlay con formato: `Line: T (in:A out:B)`

**Código:**
```python
def render(
    self,
    frame: np.ndarray,
    detections: Any,
    count_state: CountState,
    line_info: dict | None = None,
) -> np.ndarray:
    processed = frame.copy()
    
    # Draw line first (behind detections)
    if line_info is not None:
        processed = self._draw_line_crossing(processed, line_info)
    
    # ... annotate detections ...
    
    # Draw count text with line stats
    processed = self._draw_count_text(processed, count_state, line_info)
    
    return processed
```

---

### 4. Main (Configuración)

**Archivo:** `app/main.py`

**Cambios:**
- Eliminado import `SupervisionLineCounter` (ya no se usa)
- Pasados `line_y`, `line_thickness`, `line_text_scale` a `RunPipeline` constructor
- Pasados config de línea a `SupervisionOverlayRenderer`

**Código:**
```python
# Create pipeline (HU-VIS-06v: line config passed inline, no line_counter port)
pipeline = RunPipeline(
    frame_source=frame_source,
    detector=detector,
    counter=counter,
    renderer=renderer,
    frame_store=frame_store,
    metrics_store=metrics_store,
    tracker=None,
    line_y=settings.line_y,
    line_thickness=settings.line_thickness,
    line_text_scale=settings.line_text_scale,
    jpeg_quality=settings.jpeg_quality,
    sleep_sec=settings.pipeline_sleep_sec,
    max_consecutive_fails=settings.pipeline_max_consecutive_fails,
)
```

---

## Ejecución

### Service Mode (con LineZone)

```powershell
cd vision_edge

# Activar entorno virtual
.\.venv\Scripts\Activate.ps1

# Configurar variables de entorno
$env:VISION_MODE = "service"
$env:RTSP_URL = "rtsp://localhost:8554/stream"
$env:LINE_Y = "450"
$env:LINE_THICKNESS = "2"
$env:LINE_TEXT_SCALE = "0.6"

# Ejecutar
python -m app.main
```

**Salida esperada:**
```
==================================================
Vision Edge - HTTP Service Mode (HU-VIS-05, HU-VIS-06v)
==================================================
API Host: 0.0.0.0
API Port: 8010
API Version: 1.0.0
RTSP URL: rtsp://localhost:8554/stream
Model: assets/models/best.pt
Pipeline Sleep: 0.03s (~33 FPS)
Line Y: 450 (HU-VIS-06v)
==================================================
INFO:     Started server process [12345]
INFO:     Uvicorn running on http://0.0.0.0:8010
```

---

## Testing

### 1. Health Check

```bash
curl http://127.0.0.1:8010/health
```

**Respuesta:**
```json
{
  "service": "vision_edge",
  "version": "1.0.0",
  "status": "ok"
}
```

### 2. Metrics (con Line Counts)

```bash
curl http://127.0.0.1:8010/metrics
```

**Respuesta esperada:**
```json
{
  "fps": 28.5,
  "raw_count": 3,
  "stable_count": 2,
  "line_in": 5,
  "line_out": 3,
  "line_total": 8,
  "status": "running",
  "last_update_utc": "2025-01-30T12:34:56.789Z"
}
```

### 3. Processed Frame (con Línea Dibujada)

```bash
curl http://127.0.0.1:8010/frame/processed.jpg --output test_frame.jpg
```

- Abre `test_frame.jpg`
- Verifica:
  - Línea horizontal amarilla en Y=450
  - Texto verde: "Stable: 2"
  - Texto naranja: "Line: 8 (in:5 out:3)"
  - Bounding boxes de detecciones

---

## Notas Técnicas

### Diferencias con HU-VIS-06 Full

| Aspecto | HU-VIS-06 Full | HU-VIS-06v Minimal |
|---------|----------------|-------------------|
| Port `LineCounter` | ✅ Creado | ❌ NO creado |
| Adapter `SupervisionLineCounter` | ✅ Creado | ❌ NO creado |
| LineZone | En adapter | Inline en pipeline |
| Complejidad | Clean Architecture | Pragmática inline |

### API de supervision.LineZone

**IMPORTANTE:**
```python
# ❌ INCORRECTO (trigger NO retorna valores)
crossed_in, crossed_out = line_zone.trigger(detections)

# ✅ CORRECTO (leer propiedades después de trigger)
line_zone.trigger(detections)
line_in = line_zone.in_count
line_out = line_zone.out_count
```

### Graceful Degradation

Si no hay `tracker_id` en las detecciones (porque ByteTrackTracker no está implementado):
- `line_zone.trigger()` NO se llama
- `line_in`, `line_out`, `line_total` permanecen en 0
- La línea se dibuja igual
- El servicio NO crashea

---

## Logs del Pipeline

```
[RunPipeline] Processed: 30, FPS: 28.3, Raw: 3, Stable: 2, LineTotal: 8 (in=5 out=3)
[RunPipeline] Processed: 60, FPS: 29.1, Raw: 3, Stable: 2, LineTotal: 10 (in=6 out=4)
```

---

## Integración con api_server

El `api_server` consumirá:
- `GET http://vision-edge:8010/metrics` → JSON con `line_in`, `line_out`, `line_total`
- `GET http://vision-edge:8010/frame/processed.jpg` → JPEG con línea dibujada

Esto cumple con HU-BACK para integración de métricas.

---

## Conclusión

HU-VIS-06v implementa line crossing de forma **MINIMAL** sin crear nuevos ports/adapters:
- ✅ LineZone inline en pipeline
- ✅ Métricas `line_in`, `line_out`, `line_total` en `/metrics`
- ✅ Línea dibujada en `/frame/processed.jpg`
- ✅ Graceful degradation sin tracker
- ✅ Configuración vía env vars

**Resultado:** Funcionalidad completa con mínima complejidad arquitectónica.
