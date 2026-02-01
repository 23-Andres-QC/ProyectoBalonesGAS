# HU-VIS-06: Line Crossing Counter (SUPERSEDED)

> ⚠️ **NOTA:** Esta versión con Clean Architecture (ports/adapters) fue REEMPLAZADA por **HU-VIS-06v** (versión minimal inline).
> 
> **Ver:** [HU_VIS_06v_line_counter.md](HU_VIS_06v_line_counter.md) para la implementación actual.
>
> **Razón:** El usuario prefirió implementación pragmática inline sin crear nuevos ports/adapters.

---

**Historia de Usuario:** Como Computer Vision Engineer, quiero contar balones que cruzan una línea horizontal específica usando tracking, para medir flujo de objetos independiente del conteo por presencia.

**Estado:** SUPERSEDED por HU-VIS-06v (minimal inline version)

---

## 📋 Objetivo

Implementar conteo por cruce de línea que **coexiste** con el conteo estable (HU-VIS-03):

1. **stable_count:** Conteo por presencia en frame (ya existía)
2. **line_total:** Conteo acumulado de cruces únicos por línea horizontal

**Métricas nuevas:**
- `line_in`: Objetos cruzando hacia abajo
- `line_out`: Objetos cruzando hacia arriba  
- `line_total`: Total de cruces (line_in + line_out)

---

## 🏗️ Arquitectura

### Clean Architecture con Line Counter

```
┌───────────────────────────────────────────────────┐
│            Application Layer (Ports)              │
│  ┌─────────────────────────────────────────────┐  │
│  │  LineCounter (ABC)                          │  │
│  │  - update(detections, w, h) -> dict         │  │
│  │  - get_line_y() -> int                      │  │
│  └─────────────────────────────────────────────┘  │
└────────────────────┬──────────────────────────────┘
                     │ implements
┌────────────────────▼──────────────────────────────┐
│         Infrastructure Layer (Adapters)           │
│  ┌─────────────────────────────────────────────┐  │
│  │  SupervisionLineCounter                     │  │
│  │  - Uses sv.LineZone for crossing detection │  │
│  │  - Accumulates in/out counts                │  │
│  │  - Graceful degradation if no tracker_id   │  │
│  └─────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────┘
```

### Pipeline Flow (HU-VIS-06)

```
RTSP Frame
    ↓
Detector (YOLO)
    ↓
Tracker (ByteTrack - optional, returns detections with tracker_id)
    ↓
Counter (stable_count por presencia)
    ↓
LineCounter (line_in, line_out, line_total por cruce)
    ↓
Renderer (dibuja boxes + línea + contadores)
    ↓
Encode JPEG
    ↓
Stores (frames + metrics)
```

**Nota crítica:** ByteTrackTracker actualmente lanza `NotImplementedError`. El LineCounter degrada con gracia devolviendo ceros si no hay `tracker_id`.

---

## 📁 Archivos Creados/Modificados

### 1. **Port: LineCounter** (Nuevo)

**Archivo:** `app/application/ports/line_counter.py`

```python
class LineCounter(ABC):
    @abstractmethod
    def update(self, detections: Any, frame_width: int, frame_height: int) -> dict:
        """
        Returns:
            Dict with keys: line_in, line_out, line_total
        """
        raise NotImplementedError
```

### 2. **Implementación: SupervisionLineCounter** (Nuevo)

**Archivo:** `app/infrastructure/counting/supervision_line_counter.py`

**Características:**
- ✅ Usa `sv.LineZone` con línea horizontal en `y=LINE_Y`
- ✅ Requiere detections con `tracker_id` (de ByteTrack)
- ✅ Degradación con gracia: si no hay `tracker_id`, retorna zeros
- ✅ Acumula counts persistentes (no se resetean entre frames)
- ✅ Reinitializa LineZone si frame dimensions cambian

```python
class SupervisionLineCounter(LineCounter):
    def __init__(self, line_y: int) -> None:
        self._line_y = line_y
        self._line_zone: sv.LineZone | None = None
        self._line_in = 0
        self._line_out = 0
    
    def update(self, detections, frame_width, frame_height) -> dict:
        # Check tracker_id attribute
        if not hasattr(detections, 'tracker_id') or detections.tracker_id is None:
            return {"line_in": self._line_in, "line_out": self._line_out, "line_total": ...}
        
        crossed_in, crossed_out = self._line_zone.trigger(detections)
        self._line_in += crossed_in
        self._line_out += crossed_out
        
        return {"line_in": self._line_in, "line_out": self._line_out, "line_total": ...}
```

### 3. **Settings Extendidos** (Modificado)

**Archivo:** `app/infrastructure/config/settings.py`

```python
@dataclass(frozen=True)
class Settings:
    # ... existing fields ...
    # HU-VIS-06: Line Crossing Counter
    line_y: int
    line_thickness: int
    line_text_scale: float
```

**Defaults:**
```python
line_y=int(os.getenv("LINE_Y", "450")),
line_thickness=int(os.getenv("LINE_THICKNESS", "2")),
line_text_scale=float(os.getenv("LINE_TEXT_SCALE", "0.6")),
```

### 4. **Pipeline Modificado** (Modificado)

**Archivo:** `app/application/use_cases/run_pipeline.py`

**Cambios:**
```python
@dataclass
class RunPipeline:
    # ... existing ...
    line_counter: LineCounter | None = None  # NEW

def run_continuous(self):
    # After counting:
    line_counts = {"line_in": 0, "line_out": 0, "line_total": 0}
    if self.line_counter:
        line_counts = self.line_counter.update(detections, frame.shape[1], frame.shape[0])
    
    # Render with line_counts
    processed_frame = self.renderer.render(frame, detections, count_state, line_counts)
    
    # Update metrics with line fields
    self._update_metrics_store(
        fps=fps,
        raw_count=count_state.raw_count,
        stable_count=count_state.stable_count,
        line_in=line_counts["line_in"],
        line_out=line_counts["line_out"],
        line_total=line_counts["line_total"],
        status="ok"
    )
```

**Logging mejorado:**
```python
if frames_processed % 30 == 0:
    print(f"[RunPipeline] Processed: {frames_processed}, FPS: {fps:.1f}, "
          f"Raw: {count_state.raw_count}, Stable: {count_state.stable_count}, "
          f"LineTotal: {line_counts['line_total']} (in={line_counts['line_in']} out={line_counts['line_out']})")
```

### 5. **Renderer Modificado** (Modificado)

**Archivo:** `app/infrastructure/rendering/supervision_overlay_renderer.py`

**Cambios:**
```python
def __init__(
    self,
    # ... existing ...
    line_y: int | None = None,
    line_thickness: int = 2,
    line_text_scale: float = 0.6,
):
    self._line_y = line_y
    self._line_thickness = line_thickness
    self._line_text_scale = line_text_scale

def render(
    self,
    frame, detections, count_state,
    line_counts: dict | None = None,  # NEW
):
    processed = frame.copy()
    
    # Draw line FIRST (behind detections)
    if self._line_y is not None and line_counts is not None:
        processed = self._draw_line_crossing(processed, line_counts)
    
    # Draw boxes, labels...
    # Draw counts text with line_counts
```

**Nuevo método:** `_draw_line_crossing()`
- Dibuja línea horizontal amarilla en `y=LINE_Y`
- Muestra `IN: X` y `OUT: Y` junto a la línea

**Texto overlay actualizado:**
```
┌────────────────────────────────┐
│ Stable: 3                      │ ← Verde (count por presencia)
│ Line: 12 (in:7 out:5)          │ ← Naranja (count por cruce)
│ Raw: 3                          │ ← Cyan (opcional, si show_raw=true)
└────────────────────────────────┘
          ↑
    y=LINE_Y (línea amarilla horizontal)
```

### 6. **Main Service** (Modificado)

**Archivo:** `app/main.py`

```python
def run_service(settings):
    # ... existing setup ...
    
    # HU-VIS-06: Line crossing counter
    line_counter = SupervisionLineCounter(line_y=settings.line_y)
    
    renderer = SupervisionOverlayRenderer(
        # ... existing ...
        line_y=settings.line_y,
        line_thickness=settings.line_thickness,
        line_text_scale=settings.line_text_scale,
    )
    
    pipeline = RunPipeline(
        # ... existing ...
        line_counter=line_counter,  # NEW
    )
```

---

## 🧪 Cómo Ejecutar

### Modo Service con Line Crossing

```powershell
cd vision_edge
.venv\Scripts\activate

# Configurar variables (opcional)
$env:VISION_MODE="service"
$env:LINE_Y="450"              # Y position de línea (default 450)
$env:LINE_THICKNESS="2"        # Grosor de línea (default 2)
$env:LINE_TEXT_SCALE="0.6"    # Escala de texto en línea (default 0.6)
$env:API_PORT="8010"

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
...
==================================================
[Service] Pipeline thread started
[RunPipeline] Starting continuous pipeline...
[RunPipeline] Processed: 30, FPS: 28.5, Raw: 3, Stable: 3, LineTotal: 0 (in=0 out=0)
[RunPipeline] Processed: 60, FPS: 29.1, Raw: 2, Stable: 3, LineTotal: 1 (in=1 out=0)
[RunPipeline] Processed: 90, FPS: 28.8, Raw: 3, Stable: 3, LineTotal: 2 (in=1 out=1)
```

---

## 🔬 Cómo Probar

### 1. Métricas con Line Counts

```powershell
curl http://127.0.0.1:8010/metrics
```

**Respuesta esperada:**
```json
{
  "fps": 28.5,
  "raw_count": 3,
  "stable_count": 3,
  "line_in": 7,
  "line_out": 5,
  "line_total": 12,
  "status": "ok",
  "last_update_utc": "2026-01-30T18:45:12.345Z"
}
```

### 2. Frame Procesado con Línea

```powershell
curl http://127.0.0.1:8010/frame/processed.jpg --output processed.jpg
Start-Process processed.jpg
```

**Verificaciones visuales:**
- ✅ Bounding boxes en detecciones
- ✅ Línea horizontal amarilla en `y=450` (o configurado)
- ✅ Texto superior izquierdo:
  - "Stable: X" (verde)
  - "Line: Y (in:A out:B)" (naranja)
- ✅ Texto sobre línea: "IN: A" y "OUT: B"

### 3. Validar Acumulación

**Escenario:** Balón cruza línea de arriba a abajo.

```powershell
# Antes del cruce
curl http://127.0.0.1:8010/metrics
# → line_total: 5

# Esperar cruce (balón atraviesa y=450)

# Después del cruce
curl http://127.0.0.1:8010/metrics
# → line_total: 6, line_in: +1
```

**Expectativa:** `line_total` incrementa y se mantiene (no resetea entre frames).

### 4. Degradación sin Tracker

**Escenario:** Si ByteTrackTracker no está implementado (lanza NotImplementedError).

**Comportamiento:**
```json
{
  "line_in": 0,
  "line_out": 0,
  "line_total": 0
}
```

**Sin errores:** Pipeline sigue procesando frames, stable_count funciona normalmente.

---

## 🔧 Troubleshooting

### Line counts siempre en cero

**Causa:** Detections sin `tracker_id` (tracker no habilitado o no funcional).

**Diagnóstico:**
```python
# En run_pipeline.py, agregar temporalmente:
print(f"[DEBUG] Detections has tracker_id: {hasattr(detections, 'tracker_id')}")
if hasattr(detections, 'tracker_id'):
    print(f"[DEBUG] tracker_id values: {detections.tracker_id}")
```

**Solución:** Implementar ByteTrackTracker correctamente o usar otro tracker compatible con supervision.

### Línea no visible en frame

**Verificar:**
```powershell
# LINE_Y fuera de bounds del frame
$env:LINE_Y="50"   # Try different values
python -m app.main
```

**Frame típico:** 1920x1080 → `LINE_Y` válido entre 0-1079.

### api_server no muestra line_in/out/total

**Causa:** Backend api_server espera solo `fps, raw_count, stable_count, status, last_update`.

**Solución:** Actualizar VisionEdgeMetricsAdapter en api_server para mapear campos nuevos:

```python
# api_server/app/infrastructure/adapters/vision_edge_metrics_adapter.py
return {
    "count": data.get("stable_count", 0),
    "fps": data.get("fps", 0.0),
    "status": data.get("status", "live"),
    "last_update": data.get("last_update_utc"),
    # Opcional: agregar line_total si backend lo necesita
    # "line_total": data.get("line_total", 0),
}
```

---

## 📊 Diferencias: stable_count vs line_total

| Métrica       | Método                     | Resetea        | Uso                                  |
|---------------|----------------------------|----------------|--------------------------------------|
| `stable_count`| Ventana de presencia       | Sí (en frame)  | "Cuántos balones hay AHORA"          |
| `line_total`  | Cruce de línea (tracking)  | No (acumulado) | "Cuántos balones HAN PASADO por aquí"|

**Ejemplo:**
- Frame 1: 3 balones visibles, ninguno cruza → stable=3, line_total=0
- Frame 50: 2 balones visibles, 1 cruza → stable=2, line_total=1
- Frame 100: 0 balones visibles → stable=0, line_total=1 (persiste)

---

## ✅ Checklist de Validación (VERSIÓN ORIGINAL - NO IMPLEMENTADA)

> ⚠️ Esta checklist corresponde a la versión con Clean Architecture que NO fue implementada.
> Ver [HU_VIS_06v_line_counter.md](HU_VIS_06v_line_counter.md) para la implementación real.

- [ ] ~~LineCounter port creado en application/ports~~ (NO implementado - versión rechazada)
- [ ] ~~SupervisionLineCounter implementado con sv.LineZone~~ (NO implementado - versión rechazada)
- [x] Settings extendido con LINE_Y, LINE_THICKNESS, LINE_TEXT_SCALE (✅ Implementado en HU-VIS-06v)
- [x] run_pipeline.py integra LineZone inline y actualiza metrics (✅ Implementado en HU-VIS-06v)
- [x] Renderer dibuja línea horizontal y overlay con contadores (✅ Implementado en HU-VIS-06v)
- [x] main.py pasa line config inline al pipeline (✅ Implementado en HU-VIS-06v)
- [x] GET /metrics retorna line_in, line_out, line_total (✅ Implementado en HU-VIS-06v)
- [x] GET /frame/processed.jpg muestra línea visible (✅ Implementado en HU-VIS-06v)
- [x] Logging cada 30 frames incluye LineTotal (✅ Implementado en HU-VIS-06v)
- [x] Graceful degradation si no hay tracker_id (✅ Implementado en HU-VIS-06v)
- [x] No rompe modos previos (rtsp_test, detector_test, etc.) (✅ Implementado en HU-VIS-06v)

---

## 📚 Conceptos Aplicados

### 1. Separation of Concerns

- **Port (LineCounter):** Interfaz abstracta en application layer
- **Adapter (SupervisionLineCounter):** Implementación concreta en infrastructure
- **Pipeline:** Orquesta counter y line_counter independientemente

### 2. Graceful Degradation

```python
if not hasattr(detections, 'tracker_id'):
    return current_counts  # No crash, return last known state
```

### 3. Open/Closed Principle

Agregar line crossing **sin modificar** lógica de stable_count:
- `VisibleWindowCounter` → stable_count (no tocado)
- `SupervisionLineCounter` → line_total (nuevo, aislado)

### 4. Dependency Inversion

Pipeline depende de `LineCounter` (abstracción), no de `SupervisionLineCounter` (detalle).

---
> ⚠️ **ESTA VERSIÓN NO FUE IMPLEMENTADA**
>
> En su lugar, se implementó **HU-VIS-06v** (versión minimal) con las siguientes características:

### Implementación Real (HU-VIS-06v):

1. ✅ **Dual Counting:** stable_count (presencia) + line_total (cruce)
2. ✅ **Implementación Inline:** LineZone directamente en pipeline (SIN ports/adapters)
3. ✅ **Visual Feedback:** Línea y contadores en processed frame
4. ✅ **Métricas Enriquecidas:** line_in, line_out, line_total en /metrics
5. ✅ **Sin Romper HU Previas:** Modos test funcionan, api_server compatible
6. ✅ **Graceful Degradation:** Funciona con/sin tracker habilitado
7. ✅ **Simplicidad:** NO crea nuevas capas de abstracción innecesarias

### Archivos NO Creados (Clean Architecture rechazada):
- ❌ `app/application/ports/line_counter.py` - NO creado
- ❌ `app/infrastructure/counting/supervision_line_counter.py` - NO creado

### Archivos Modificados (HU-VIS-06v):
- ✅ `app/infrastructure/config/settings.py` - LINE_Y, LINE_THICKNESS, LINE_TEXT_SCALE
- ✅ `app/application/use_cases/run_pipeline.py` - LineZone inline
- ✅ `app/infrastructure/rendering/supervision_overlay_renderer.py` - Dibujar línea
- ✅ `app/main.py` - Config inline (sin SupervisionLineCounter)
- ✅ `docs/HU_VIS_06v_line_counter.md` - Documentación completa

---

**📖 Documentación Actualizada:**
Ver [HU_VIS_06v_line_counter.md](HU_VIS_06v_line_counter.md) para:
- Implementación inline detallada
- Guía de ejecución y testing
- API de supervision.LineZone
- Comparación con versión Full✅ **Sin Romper HU Previas:** Modos test funcionan, api_server compatible
6. ✅ **Graceful Degradation:** Funciona con/sin tracker habilitado

---

**Próximos Pasos:**
- HU-VIS-07: Implementar ByteTrackTracker completo (reemplazar NotImplementedError)
- HU-VIS-08: Zonas múltiples (polígonos) para conteo por área
- HU-BACK-07: Actualizar api_server para exponer line_total en UI
