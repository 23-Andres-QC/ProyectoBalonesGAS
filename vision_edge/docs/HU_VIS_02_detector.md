# HU-VIS-02: Detector YOLO con Supervision

## Objetivo
Implementar un Detector YOLO robusto y desacoplado que reciba frames BGR (numpy.ndarray) y retorne detecciones (supervision.Detections) para el prototipo ALFA.

## Archivos modificados

### 1. Port actualizado ([app/application/ports/detector.py](../app/application/ports/detector.py))
- Interfaz `Detector` con método `detect(frame: np.ndarray) -> sv.Detections`
- Desacoplado de Ultralytics (solo interfaz ABC)
- Tipado numpy para frames

### 2. Implementación YOLO ([app/infrastructure/inference/yolo_ultralytics_detector.py](../app/infrastructure/inference/yolo_ultralytics_detector.py))
- Clase `YoloUltralyticsDetector(Detector)`
- Carga modelo YOLO una sola vez en `__init__`
- Manejo de errores si `best.pt` no existe
- Retorna `sv.Detections` usando `from_ultralytics()`
- Logs claros al cargar modelo

### 3. Settings actualizado ([app/infrastructure/config/settings.py](../app/infrastructure/config/settings.py))
- Agregado `vision_mode` para controlar modo de operación
- Valores: `rtsp_test` (default, HU-VIS-01) o `detector_test` (HU-VIS-02)
- Mantiene variables existentes sin cambios

### 4. Test runner mejorado ([app/main.py](../app/main.py))
- Dispatcher según `VISION_MODE`
- `run_rtsp_test()`: modo HU-VIS-01 (200 frames, sin detector)
- `run_detector_test()`: modo HU-VIS-02 (50 frames, con detector YOLO)
- Sin romper compatibilidad con HU-VIS-01

### 5. Dependencias ([requirements.txt](../requirements.txt))
- Agregado `supervision` (para sv.Detections)
- Confirmadas: `ultralytics`, `numpy`, `opencv-python`

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

# Modo de operación
VISION_MODE=detector_test
# VISION_MODE=rtsp_test   (default si no se especifica)

# Otros
JPEG_QUALITY=80
COUNT_WINDOW=15
```

## Cómo ejecutar

### Modo RTSP Test (HU-VIS-01) - Default
Sin setear `VISION_MODE` o con `VISION_MODE=rtsp_test`:
```bash
cd vision_edge
python -m app.main
```

### Modo Detector Test (HU-VIS-02)
Con `VISION_MODE=detector_test`:
```bash
cd vision_edge
# En Windows (PowerShell)
$env:VISION_MODE="detector_test"
python -m app.main

# En Linux/Mac
export VISION_MODE=detector_test
python -m app.main
```

O editar `.env`:
```
VISION_MODE=detector_test
```

## Logs esperados

### Modo detector_test (exitoso)
```
==================================================
Vision Edge - Detector Test Mode (HU-VIS-02)
==================================================
RTSP_URL: rtsp://admin:admin@192.168.1.100:554/stream1
MODEL_PATH: assets/models/best.pt
CONF_THRES: 0.5
==================================================
[RTSP] Connected: rtsp://admin:admin@192.168.1.100:554/stream1
[YOLO] Loading model: assets/models/best.pt
[YOLO] Model loaded successfully (conf=0.5)
[10/50] Processed=10, Detections=3, Avg=2.8, FPS=28.5
[20/50] Processed=20, Detections=2, Avg=2.5, FPS=29.1
[30/50] Processed=30, Detections=4, Avg=2.9, FPS=28.7
[40/50] Processed=40, Detections=1, Avg=2.6, FPS=29.0
[50/50] Processed=50, Detections=3, Avg=2.7, FPS=28.8
[RTSP] Closed
==================================================
Total frames processed: 50
Total detections: 135
Average detections per frame: 2.70
Average FPS: 28.82
Elapsed time: 1.74s
==================================================
```

### Modo rtsp_test (HU-VIS-01 sin cambios)
```
==================================================
Vision Edge - RTSP Test Mode (HU-VIS-01)
==================================================
RTSP_URL: rtsp://admin:admin@192.168.1.100:554/stream1
Reconnect delay: 2.0s
Max fails before reopen: 10
==================================================
[RTSP] Connected: rtsp://...
[50/200] OK=50, FAIL=0, FPS=29.4
[100/200] OK=100, FAIL=0, FPS=29.7
[150/200] OK=150, FAIL=0, FPS=29.6
[200/200] OK=200, FAIL=0, FPS=29.5
[RTSP] Closed
==================================================
```

### Error si falta best.pt
```
[YOLO] Loading model: assets/models/best.pt
FileNotFoundError: Failed to load YOLO model at assets/models/best.pt: [Errno 2] No such file or directory
```

## Validación de compatibilidad

### ✅ HU-VIS-01 sigue funcionando
- Sin `VISION_MODE` o con `VISION_MODE=rtsp_test`
- Ejecuta test de 200 frames RTSP
- Sin cargar detector YOLO

### ✅ HU-VIS-02 funciona
- Con `VISION_MODE=detector_test`
- Carga modelo YOLO
- Procesa 50 frames con detección
- Muestra cantidad de detecciones por frame

## Estructura final

```
vision_edge/
  app/
    application/
      ports/
        detector.py          ← Interfaz Detector actualizada
    infrastructure/
      inference/
        yolo_ultralytics_detector.py  ← Implementación YOLO
      config/
        settings.py          ← Agregado vision_mode
    main.py                  ← Dispatcher con 2 modos
  assets/
    models/
      best.pt                ← Modelo YOLO (requerido)
  docs/
    HU_VIS_02_detector.md    ← Este archivo
  requirements.txt           ← Agregado supervision
  .env.example
```

## Próximos pasos (fuera de scope HU-VIS-02)
- HU-VIS-03: Contador estable (VisibleWindowCounter)
- HU-VIS-04: Renderer con supervision (cajas/labels)
- HU-VIS-05: Pipeline completo (FrameSource → Detector → Counter → Renderer → Stores)
