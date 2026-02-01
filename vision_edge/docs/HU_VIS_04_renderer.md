# HU-VIS-04: Renderer con Supervision (Cajas + Labels + Texto Count)

## Objetivo
Implementar un Renderer que anote frames con bounding boxes, labels opcionales y texto de conteo (stable y raw) usando la librería supervision, produciendo frames procesados listos para el prototipo ALFA.

## Archivos modificados/creados

### 1. Port Renderer actualizado ([app/application/ports/renderer.py](../app/application/ports/renderer.py))
- Interfaz `Renderer` ABC con método `render(frame: np.ndarray, detections: Any, count_state: CountState) -> np.ndarray`
- Desacoplado de supervision (acepta Any para detections)
- Retorna frame procesado (numpy array BGR), no bytes JPEG

### 2. Implementación Supervision ([app/infrastructure/rendering/supervision_overlay_renderer.py](../app/infrastructure/rendering/supervision_overlay_renderer.py))
- Clase `SupervisionOverlayRenderer(Renderer)`
- Usa `sv.BoxAnnotator` para bounding boxes
- Usa `sv.LabelAnnotator` para labels (opcional)
- Usa `cv2.putText` para texto de count (grande y visible)
- Constructor configurable:
  - `show_labels: bool` - mostrar labels en boxes
  - `show_raw: bool` - mostrar raw_count además de stable
  - `text_scale: float` - escala del texto
  - `text_thickness: int` - grosor del texto
  - `box_thickness: int` - grosor de cajas
- Maneja casos sin detecciones (len==0) sin crash
- Crea copia del frame original (`frame.copy()`)
- Texto con fondo semi-transparente para mejor visibilidad

### 3. Settings actualizado ([app/infrastructure/config/settings.py](../app/infrastructure/config/settings.py))
- Agregados campos de rendering:
  - `render_show_labels: bool` (default True)
  - `render_show_raw: bool` (default False)
  - `render_text_scale: float` (default 1.0)
  - `render_text_thickness: int` (default 2)
  - `render_box_thickness: int` (default 2)
- Env vars correspondientes con valores por defecto
- Mantiene campos existentes sin cambios (HU-VIS-01/02/03 intactos)

### 4. Test mode en main.py ([app/main.py](../app/main.py))
- Nueva función `run_render_test(settings)`
- Dispatcher actualizado:
  - `VISION_MODE=rtsp_test` → `run_rtsp_test()` (HU-VIS-01)
  - `VISION_MODE=detector_test` → `run_detector_test()` (HU-VIS-02)
  - `VISION_MODE=counter_test` → `run_counter_test()` (HU-VIS-03)
  - `VISION_MODE=render_test` → `run_render_test()` (HU-VIS-04)
- Render test:
  1. Abre RTSP FrameSource
  2. Carga YOLO Detector
  3. Crea VisibleWindowCounter
  4. Crea SupervisionOverlayRenderer
  5. Procesa 30 frames
  6. Guarda 6 imágenes (frames 10, 20, 30):
     - `outputs/raw_10.jpg`, `outputs/processed_10.jpg`
     - `outputs/raw_20.jpg`, `outputs/processed_20.jpg`
     - `outputs/raw_30.jpg`, `outputs/processed_30.jpg`
  7. Log cada 10 frames: Raw, Stable, FPS
  8. Cierra RTSP al final
- Crea carpeta `outputs/` automáticamente si no existe
- Sin romper compatibilidad con modos anteriores

## Configuración

### Variables de entorno (.env)
```bash
# ============================================
# RTSP (HU-VIS-01)
# ============================================
RTSP_URL=rtsp://admin:admin@192.168.1.100:554/stream1
RTSP_RECONNECT_SEC=2.0
RTSP_MAX_FAILS_BEFORE_REOPEN=10
RTSP_OPEN_TIMEOUT_SEC=5.0

# ============================================
# YOLO (HU-VIS-02)
# ============================================
MODEL_PATH=assets/models/best.pt
CONF_THRES=0.25
# ⚠️ Recomendado 0.25 para render_test (más detecciones visibles)

# ============================================
# Counter (HU-VIS-03)
# ============================================
COUNT_WINDOW=15
STABLE_MODE=median

# ============================================
# Renderer (HU-VIS-04)
# ============================================
RENDER_SHOW_LABELS=1
# 1=mostrar labels en cajas, 0=solo cajas

RENDER_SHOW_RAW=0
# 1=mostrar raw_count, 0=solo stable_count

RENDER_TEXT_SCALE=1.0
# Escala del texto (0.5-2.0 recomendado)

RENDER_TEXT_THICKNESS=2
# Grosor del texto (1-4 recomendado)

RENDER_BOX_THICKNESS=2
# Grosor de bounding boxes (1-4 recomendado)

# ============================================
# Modo de operación
# ============================================
VISION_MODE=render_test
# VISION_MODE=rtsp_test     (HU-VIS-01, default)
# VISION_MODE=detector_test (HU-VIS-02)
# VISION_MODE=counter_test  (HU-VIS-03)

# ============================================
# Otros
# ============================================
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
$env:VISION_MODE="detector_test"
python -m app.main
```

### Modo Counter Test (HU-VIS-03)
```bash
cd vision_edge
$env:VISION_MODE="counter_test"
python -m app.main
```

### Modo Render Test (HU-VIS-04)
```bash
cd vision_edge
# Windows (PowerShell)
$env:VISION_MODE="render_test"
$env:CONF_THRES="0.25"
$env:RENDER_SHOW_RAW="1"
python -m app.main

# Linux/Mac
export VISION_MODE=render_test
export CONF_THRES=0.25
export RENDER_SHOW_RAW=1
python -m app.main
```

O editar `.env`:
```
VISION_MODE=render_test
CONF_THRES=0.25
RENDER_SHOW_RAW=1
```

## Logs esperados

### Modo render_test (exitoso)
```
==================================================
Vision Edge - Render Test Mode (HU-VIS-04)
==================================================
RTSP_URL: rtsp://admin:admin@192.168.1.100:554/stream1
MODEL_PATH: assets/models/best.pt
CONF_THRES: 0.25
COUNT_WINDOW: 15
STABLE_MODE: median
RENDER_SHOW_LABELS: True
RENDER_SHOW_RAW: True
==================================================
[OUTPUT] Created directory: outputs
[RTSP] Connected: rtsp://admin:admin@192.168.1.100:554/stream1
[YOLO] Loading model: assets/models/best.pt
[YOLO] Model loaded successfully (conf=0.25)
[10/30] Raw=4, Stable=3, FPS=27.8
[SAVED] Frame 10: outputs/raw_10.jpg and outputs/processed_10.jpg
[20/30] Raw=3, Stable=3, FPS=28.5
[SAVED] Frame 20: outputs/raw_20.jpg and outputs/processed_20.jpg
[30/30] Raw=2, Stable=3, FPS=28.2
[SAVED] Frame 30: outputs/raw_30.jpg and outputs/processed_30.jpg
[RTSP] Closed
==================================================
Total frames processed: 30
Average FPS: 28.17
Elapsed time: 1.06s
Output images saved in: outputs/
==================================================
```

## Outputs generados

Después de ejecutar `render_test`, en la carpeta `vision_edge/outputs/` encontrarás:

```
vision_edge/
  outputs/
    raw_10.jpg         ← Frame original del frame 10
    processed_10.jpg   ← Frame anotado con cajas + texto count
    raw_20.jpg         ← Frame original del frame 20
    processed_20.jpg   ← Frame anotado con cajas + texto count
    raw_30.jpg         ← Frame original del frame 30
    processed_30.jpg   ← Frame anotado con cajas + texto count
```

### Qué validar visualmente en processed_*.jpg:

1. **Bounding boxes verdes** alrededor de objetos detectados
2. **Labels** tipo "obj_0", "obj_1", etc. (si `RENDER_SHOW_LABELS=1`)
3. **Texto grande "Count: X"** en esquina superior izquierda (verde)
4. **Texto "Raw: Y"** debajo del count (cyan) si `RENDER_SHOW_RAW=1`
5. **Fondo negro semi-transparente** detrás del texto para legibilidad

### Comparación raw vs processed:

| Frame | raw_*.jpg | processed_*.jpg |
|-------|-----------|-----------------|
| Frame 10 | Imagen original sin anotaciones | Cajas + labels + "Count: 3" |
| Frame 20 | Imagen original sin anotaciones | Cajas + labels + "Count: 3" |
| Frame 30 | Imagen original sin anotaciones | Cajas + labels + "Count: 3" |

## Validación de compatibilidad

### ✅ HU-VIS-01 sigue funcionando
```bash
cd vision_edge
python -m app.main
# O explícito:
$env:VISION_MODE="rtsp_test"
python -m app.main
```
**Salida esperada:** Test de 200 frames RTSP sin detector, counter ni renderer

### ✅ HU-VIS-02 sigue funcionando
```bash
$env:VISION_MODE="detector_test"
python -m app.main
```
**Salida esperada:** Test de 50 frames con YOLO detector, sin counter ni renderer

### ✅ HU-VIS-03 sigue funcionando
```bash
$env:VISION_MODE="counter_test"
python -m app.main
```
**Salida esperada:** Test de 80 frames con YOLO + Counter, sin renderer ni guardado

### ✅ HU-VIS-04 funciona
```bash
$env:VISION_MODE="render_test"
python -m app.main
```
**Salida esperada:** Test de 30 frames con YOLO + Counter + Renderer, guarda 6 imágenes en `outputs/`

## Estructura final

```
vision_edge/
  app/
    application/
      ports/
        renderer.py              ← Interfaz Renderer actualizada
    infrastructure/
      rendering/
        supervision_overlay_renderer.py  ← Implementación con supervision
      config/
        settings.py              ← Agregados campos render_*
    main.py                      ← Agregado render_test mode
  outputs/                       ← Carpeta creada automáticamente
    raw_10.jpg
    processed_10.jpg
    raw_20.jpg
    processed_20.jpg
    raw_30.jpg
    processed_30.jpg
  docs/
    HU_VIS_04_renderer.md        ← Este archivo
  .env.example                   ← Agregadas vars RENDER_*
```

## Decisiones de diseño

### Por qué retornar np.ndarray y no bytes JPEG?
- **Separación de responsabilidades:** Renderer solo anota, no codifica
- **Flexibilidad:** Permite post-procesamiento antes de codificar
- **Performance:** Evita codificación múltiple innecesaria
- **Clean Architecture:** Encoding JPEG será responsabilidad de stores (HU-VIS-05)

### Por qué supervision en lugar de OpenCV puro?
- **Menos código:** BoxAnnotator y LabelAnnotator ya implementados
- **Mejor calidad:** Anotaciones más limpias y profesionales
- **Consistencia:** Misma librería usada para detections (sv.Detections)
- **Mantenibilidad:** API estable y bien documentada

### Por qué frame.copy() en render?
- **Inmutabilidad:** No modificar frame original (puede ser usado en otros lugares)
- **Debugging:** Permite comparar raw vs processed
- **Side effects:** Evita efectos secundarios inesperados

### Por qué texto con fondo negro?
- **Legibilidad:** Texto siempre legible independientemente del fondo
- **Profesionalismo:** Mejor aspecto visual
- **Contraste:** Facilita lectura en condiciones variadas

### Por qué solo 30 frames en render_test?
- **Velocidad:** Test rápido (1-2 segundos)
- **Validación:** Suficiente para verificar anotaciones
- **Recursos:** No llena disco con imágenes innecesarias
- **Muestras:** 3 frames clave suficientes para validar

## Configuraciones recomendadas por escenario

### Para debugging (ver todo):
```bash
CONF_THRES=0.25
RENDER_SHOW_LABELS=1
RENDER_SHOW_RAW=1
RENDER_TEXT_SCALE=1.2
```

### Para producción (limpio):
```bash
CONF_THRES=0.5
RENDER_SHOW_LABELS=0
RENDER_SHOW_RAW=0
RENDER_TEXT_SCALE=1.5
```

### Para demo (vistoso):
```bash
CONF_THRES=0.4
RENDER_SHOW_LABELS=1
RENDER_SHOW_RAW=1
RENDER_TEXT_SCALE=1.5
RENDER_BOX_THICKNESS=3
```

## Próximos pasos (fuera de scope HU-VIS-04)

- **HU-VIS-05:** Pipeline completo
  - Integrar FrameSource → Detector → Counter → Renderer
  - Guardar frames en Stores (in-memory o Redis)
  - Convertir a JPEG bytes
  - Exponer métricas
- **Integración con api_server:**
  - Conectar stores con endpoints `/api/frame/raw` y `/api/frame/processed`
  - Endpoint `/api/metrics` con stable_count, fps, etc.
- **Optimizaciones futuras:**
  - Threading para pipeline asíncrono
  - Buffer ring para frames
  - Skip frames si CPU sobrecargada

## Testing manual

### Test 1: Verificar que genera imágenes
```bash
cd vision_edge
$env:VISION_MODE="render_test"
python -m app.main

# Verificar outputs:
dir outputs
# Deberías ver 6 archivos .jpg
```

### Test 2: Verificar anotaciones visualmente
```bash
# Abrir processed_10.jpg con visor de imágenes
# Verificar:
# ✅ Cajas verdes alrededor de objetos
# ✅ Texto "Count: X" visible en esquina superior izquierda
# ✅ Fondo negro detrás del texto
```

### Test 3: Comparar raw vs processed
```bash
# Abrir raw_10.jpg y processed_10.jpg lado a lado
# Verificar que processed tiene anotaciones pero mismo frame base
```

### Test 4: Probar sin detecciones (opcional)
```bash
# Configurar CONF_THRES muy alto para forzar cero detecciones
$env:CONF_THRES="0.99"
$env:VISION_MODE="render_test"
python -m app.main

# Verificar que no crashea y muestra "Count: 0"
```

### Test 5: Probar con RENDER_SHOW_RAW=1
```bash
$env:RENDER_SHOW_RAW="1"
$env:VISION_MODE="render_test"
python -m app.main

# Abrir processed_10.jpg
# Verificar que aparece "Raw: Y" debajo de "Count: X"
```

## Troubleshooting

### ❌ Error: "ModuleNotFoundError: No module named 'supervision'"
**Causa:** supervision no instalado  
**Solución:**
```bash
pip install supervision
```

### ❌ Error: "FileNotFoundError: outputs/"
**Causa:** No debería pasar, el código crea la carpeta  
**Solución:**
```bash
mkdir outputs
```

### ❌ Imágenes se ven vacías o negras
**Causa:** RTSP no conecta o modelo no detecta nada  
**Solución:**
1. Verificar RTSP funciona con `rtsp_test`
2. Bajar `CONF_THRES=0.25`
3. Verificar modelo existe en `assets/models/best.pt`

### ❌ Texto count no visible
**Causa:** Color o escala inadecuados  
**Solución:**
```bash
$env:RENDER_TEXT_SCALE="2.0"
$env:RENDER_TEXT_THICKNESS="3"
```

### ❌ Demasiadas cajas (false positives)
**Causa:** CONF_THRES muy bajo  
**Solución:**
```bash
$env:CONF_THRES="0.5"  # O más alto
```

---

**✅ HU-VIS-04 implementado y validado. Renderer produce frames anotados con supervision y está listo para integración en pipeline completo (HU-VIS-05).**
