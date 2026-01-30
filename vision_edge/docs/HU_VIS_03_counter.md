# HU-VIS-03: Counter Estabilizado con Ventana (SIN tracking)

## Objetivo
Implementar un Counter ALFA que calcule `raw_count` directo de detecciones y `stable_count` usando ventana deslizante con estrategia median/mode, sin tracking, para el prototipo de conteo de balones de gas.

## Archivos modificados/creados

### 1. Port Counter actualizado ([app/application/ports/counter.py](../app/application/ports/counter.py))
- Interfaz `Counter` ABC con método `update(detections: Any) -> CountState`
- Desacoplado de supervision (acepta cualquier objeto con `__len__`)
- Retorna `CountState` completo (raw, stable, window, history)

### 2. Entity CountState refactorizado ([app/domain/entities/count_state.py](../app/domain/entities/count_state.py))
- Dataclass inmutable `@dataclass(frozen=True)`
- Campos:
  - `raw_count: int` - conteo directo `len(detections)`
  - `stable_count: int` - conteo estabilizado por ventana
  - `window_size: int` - tamaño de ventana usada
  - `history: tuple[int, ...]` - últimos N raw_count (para debug)
- Serializable y simple (compatible con JSON)

### 3. Regla estable ([app/domain/rules/stable_count_rule.py](../app/domain/rules/stable_count_rule.py))
- Función pura `compute_stable_count(history: Sequence[int], mode: str) -> int`
- Estrategias:
  - **`median`** (default): Valor mediano (robusto a outliers)
  - **`mode`**: Valor más frecuente (si hay repetidos)
- Implementación sin numpy:
  - `_compute_median()`: sorted + índice medio
  - `_compute_mode()`: dict de frecuencias + min en caso de empate
- Maneja casos edge:
  - history vacío → 0
  - mode inválido → fallback a median

### 4. Implementación ([app/infrastructure/counting/visible_window_counter.py](../app/infrastructure/counting/visible_window_counter.py))
- Clase `VisibleWindowCounter(Counter)`
- Constructor:
  - `window: int = 15` - tamaño buffer
  - `stable_mode: str = "median"` - estrategia
- Buffer: `deque[int]` con `maxlen=window` (auto-trim)
- `update(detections)`:
  1. `raw_count = len(detections)`
  2. Append a buffer
  3. `stable_count = compute_stable_count(buffer, mode)`
  4. Return `CountState` inmutable
- Sin prints internos (solo retorna estado)

### 5. Settings actualizado ([app/infrastructure/config/settings.py](../app/infrastructure/config/settings.py))
- Agregado `stable_mode: str` al dataclass
- Env var `STABLE_MODE` con default `"median"`
- Mantiene variables existentes sin cambios (HU-VIS-01/02 intactos)

### 6. Test mode en main.py ([app/main.py](../app/main.py))
- Nueva función `run_counter_test(settings)`
- Dispatcher actualizado:
  - `VISION_MODE=rtsp_test` → `run_rtsp_test()` (HU-VIS-01)
  - `VISION_MODE=detector_test` → `run_detector_test()` (HU-VIS-02)
  - `VISION_MODE=counter_test` → `run_counter_test()` (HU-VIS-03)
- Counter test:
  1. Abre RTSP FrameSource
  2. Carga YOLO Detector
  3. Crea VisibleWindowCounter(window, stable_mode)
  4. Procesa 80 frames
  5. Cada 10 frames imprime: Raw, Stable, Window, FPS
  6. Cierra source al final
- NO renderiza, NO guarda imágenes

## Configuración

### Variables de entorno (.env)
```bash
# RTSP
RTSP_URL=rtsp://admin:admin@192.168.1.100:554/stream1
RTSP_RECONNECT_SEC=2.0
RTSP_MAX_FAILS_BEFORE_REOPEN=10
RTSP_OPEN_TIMEOUT_SEC=5.0

# YOLO
MODEL_PATH=assets/models/best.pt
CONF_THRES=0.5

# Counter
COUNT_WINDOW=15
STABLE_MODE=median

# Modo de operación
VISION_MODE=counter_test
# VISION_MODE=rtsp_test     (HU-VIS-01, default)
# VISION_MODE=detector_test (HU-VIS-02)

# Otros
JPEG_QUALITY=80
```

## Cómo ejecutar

### Modo RTSP Test (HU-VIS-01) - Default
```bash
cd vision_edge
python -m app.main
```

### Modo Detector Test (HU-VIS-02)
```bash
cd vision_edge
# Windows (PowerShell)
$env:VISION_MODE="detector_test"
python -m app.main

# Linux/Mac
export VISION_MODE=detector_test
python -m app.main
```

### Modo Counter Test (HU-VIS-03)
```bash
cd vision_edge
# Windows (PowerShell)
$env:VISION_MODE="counter_test"
$env:COUNT_WINDOW="15"
$env:STABLE_MODE="median"
python -m app.main

# Linux/Mac
export VISION_MODE=counter_test
export COUNT_WINDOW=15
export STABLE_MODE=median
python -m app.main
```

O editar `.env`:
```
VISION_MODE=counter_test
COUNT_WINDOW=15
STABLE_MODE=median
```

## Logs esperados

### Modo counter_test (exitoso con median)
```
==================================================
Vision Edge - Counter Test Mode (HU-VIS-03)
==================================================
RTSP_URL: rtsp://admin:admin@192.168.1.100:554/stream1
MODEL_PATH: assets/models/best.pt
CONF_THRES: 0.5
COUNT_WINDOW: 15
STABLE_MODE: median
==================================================
[RTSP] Connected: rtsp://admin:admin@192.168.1.100:554/stream1
[YOLO] Loading model: assets/models/best.pt
[YOLO] Model loaded successfully (conf=0.5)
[10/80] Raw=3, Stable=3, Window=15, FPS=28.5
[20/80] Raw=2, Stable=3, Window=15, FPS=29.1
[30/80] Raw=4, Stable=3, Window=15, FPS=28.7
[40/80] Raw=1, Stable=3, Window=15, FPS=29.0
[50/80] Raw=3, Stable=3, Window=15, FPS=28.8
[60/80] Raw=3, Stable=3, Window=15, FPS=28.9
[70/80] Raw=2, Stable=3, Window=15, FPS=29.2
[80/80] Raw=4, Stable=3, Window=15, FPS=28.6
[RTSP] Closed
==================================================
Total frames processed: 80
Average FPS: 28.85
Elapsed time: 2.77s
==================================================
```

### Modo counter_test con mode strategy
```
$env:STABLE_MODE="mode"
python -m app.main

# Salida similar pero stable_count puede diferir:
[10/80] Raw=3, Stable=3, Window=15, FPS=28.5
[20/80] Raw=2, Stable=3, Window=15, FPS=29.1
# stable_count = valor más frecuente en ventana
```

### Validación que HU-VIS-01 no se rompió
```
cd vision_edge
python -m app.main
# O sin .env:
$env:VISION_MODE="rtsp_test"
python -m app.main

# Output:
==================================================
Vision Edge - RTSP Test Mode (HU-VIS-01)
==================================================
...
[50/200] OK=50, FAIL=0, FPS=29.4
...
```

### Validación que HU-VIS-02 no se rompió
```
$env:VISION_MODE="detector_test"
python -m app.main

# Output:
==================================================
Vision Edge - Detector Test Mode (HU-VIS-02)
==================================================
...
[10/50] Processed=10, Detections=3, Avg=2.8, FPS=28.5
...
```

## Estrategias de estabilización

### Median (default, recomendado)
- Robusto a outliers
- Si hay spike temporal (ej: 2, 3, 3, 10, 3) → median=3
- Ideal para ambientes con oclusiones o detecciones falsas ocasionales

### Mode
- Útil si hay valores muy repetidos
- Si distribución es uniforme, puede ser inestable
- Ejemplo: [2, 2, 2, 3, 3, 4] → mode=2

### Ejemplo comparativo
```
Historia: [2, 3, 3, 3, 2, 3, 10, 3, 3, 2, 3, 3, 3, 2, 3]

MEDIAN:
  sorted = [2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 10]
  median = 3 (índice 7)

MODE:
  freq = {2: 4, 3: 10, 10: 1}
  max_freq = 10
  mode = 3
```

## Validación de compatibilidad

### ✅ HU-VIS-01 sigue funcionando
- Sin `VISION_MODE` o con `VISION_MODE=rtsp_test`
- Ejecuta test de 200 frames RTSP
- Sin cargar detector ni counter

### ✅ HU-VIS-02 sigue funcionando
- Con `VISION_MODE=detector_test`
- Carga modelo YOLO
- Procesa 50 frames con detección
- Muestra cantidad de detecciones por frame

### ✅ HU-VIS-03 funciona
- Con `VISION_MODE=counter_test`
- Carga RTSP + YOLO + Counter
- Procesa 80 frames con conteo raw + stable
- Muestra diferencia entre raw y stable cada 10 frames

## Estructura final

```
vision_edge/
  app/
    application/
      ports/
        counter.py               ← Interfaz Counter(ABC) actualizada
    domain/
      entities/
        count_state.py           ← CountState inmutable refactorizado
      rules/
        stable_count_rule.py     ← Funciones median/mode sin numpy
    infrastructure/
      counting/
        visible_window_counter.py ← Implementación con deque
      config/
        settings.py              ← Agregado stable_mode
    main.py                      ← Agregado counter_test mode
  docs/
    HU_VIS_03_counter.md         ← Este archivo
  .env.example                   ← Agregado COUNT_WINDOW, STABLE_MODE
```

## Decisiones de diseño

### Por qué mediana y no promedio?
- **Promedio** es sensible a outliers: [2, 3, 3, 100] → avg=27
- **Mediana** es robusta: [2, 3, 3, 100] → median=3
- Para visión con detecciones ruidosas, mediana es más estable

### Por qué no numpy?
- Evitar dependencia extra solo para median/mode
- Implementación simple con sorted() y dict
- Mantiene el proyecto ligero

### Por qué CountState inmutable?
- @dataclass(frozen=True) previene modificaciones accidentales
- Facilita debugging (estado siempre consistente)
- Compatible con dataclass serialization (para futuro API)

### Por qué history en CountState?
- Útil para debugging y análisis
- Permite visualizar comportamiento de ventana
- Pequeño overhead (15 ints ≈ 60 bytes)

## Próximos pasos (fuera de scope HU-VIS-03)
- HU-VIS-04: Renderer con supervision (BoxAnnotator, LabelAnnotator)
- HU-VIS-05: Pipeline completo (FrameSource → Detector → Counter → Renderer → Stores)
- Integración con api_server (enviar stable_count via WebSocket/HTTP)

## Testing manual

### Test 1: Verificar median con outlier
```bash
# Crear script test_counter.py temporal:
from app.infrastructure.counting.visible_window_counter import VisibleWindowCounter

class FakeDetections:
    def __init__(self, n):
        self.n = n
    def __len__(self):
        return self.n

counter = VisibleWindowCounter(window=5, stable_mode="median")

# Simular detecciones: 3, 3, 3, 10, 3
for count in [3, 3, 3, 10, 3]:
    state = counter.update(FakeDetections(count))
    print(f"Raw={state.raw_count}, Stable={state.stable_count}, History={state.history}")

# Output esperado:
# Raw=3, Stable=3, History=(3,)
# Raw=3, Stable=3, History=(3, 3)
# Raw=3, Stable=3, History=(3, 3, 3)
# Raw=10, Stable=3, History=(3, 3, 3, 10)
# Raw=3, Stable=3, History=(3, 3, 3, 10, 3)
#                        sorted=[3,3,3,3,10] median=3
```

### Test 2: Verificar mode con frecuencias
```bash
counter = VisibleWindowCounter(window=5, stable_mode="mode")

for count in [2, 3, 3, 2, 3]:
    state = counter.update(FakeDetections(count))
    print(f"Raw={state.raw_count}, Stable={state.stable_count}")

# Output esperado:
# Raw=2, Stable=2
# Raw=3, Stable=2 (o 3, empate)
# Raw=3, Stable=3 (freq: 3=2, 2=1)
# Raw=2, Stable=2 (freq: 3=2, 2=2, empate → min=2)
# Raw=3, Stable=3 (freq: 3=3, 2=2)
```

### Test 3: Counter test real con RTSP
```bash
cd vision_edge
$env:VISION_MODE="counter_test"
$env:COUNT_WINDOW="10"
$env:STABLE_MODE="median"
python -m app.main

# Verificar:
# ✅ Se conecta a RTSP
# ✅ Carga YOLO
# ✅ Muestra Raw != Stable en frames con variación
# ✅ Stable converge después de COUNT_WINDOW frames
```
