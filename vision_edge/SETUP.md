# 🚀 Guía de Setup - Vision Edge (ALFA)

**Proyecto:** Sistema de conteo de balones de gas con visión por computadora  
**Módulo:** vision_edge - Pipeline de procesamiento RTSP + YOLO + Counter  
**Fecha:** Enero 2026

---

## 📋 Tabla de Contenidos
1. [Requisitos Previos](#requisitos-previos)
2. [Instalación Paso a Paso](#instalación-paso-a-paso)
3. [Configuración](#configuración)
4. [Obtener el Modelo YOLO](#obtener-el-modelo-yolo)
5. [Ejecución](#ejecución)
6. [Modos de Operación](#modos-de-operación)
7. [Solución de Problemas](#solución-de-problemas)

---

## 📦 Requisitos Previos

### 1. Python
- **Versión requerida:** Python 3.12.3 o superior
- Verificar versión:
  ```bash
  python --version
  ```

### 2. Sistema Operativo
- ✅ **Windows 10/11** (probado en PowerShell)
- ✅ **Linux** (Ubuntu 20.04+)
- ✅ **macOS** (con ajustes menores)

### 3. Hardware
- **Mínimo:**
  - 4 GB RAM
  - 2 núcleos CPU
- **Recomendado:**
  - 8 GB RAM
  - GPU NVIDIA (para YOLO más rápido, opcional)
  - 4+ núcleos CPU

### 4. Cámara RTSP
- URL RTSP accesible (formato: `rtsp://user:pass@ip:port/stream`)
- Red estable con la cámara

---

## 🔧 Instalación Paso a Paso

### Paso 1: Clonar el Repositorio

```bash
# Clonar repositorio completo
git clone https://github.com/23-Andres-QC/ProyectoBalonesGAS.git

# Navegar a la carpeta vision_edge
cd ProyectoBalonesGAS/vision_edge
```

### Paso 2: Crear Entorno Virtual

#### En Windows (PowerShell):
```powershell
# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
.\.venv\Scripts\Activate.ps1

# Si hay error de permisos, ejecutar primero:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### En Linux/macOS:
```bash
# Crear entorno virtual
python3 -m venv .venv

# Activar entorno virtual
source .venv/bin/activate
```

**✅ Verificar que estés en el entorno virtual:**
- Deberías ver `(.venv)` al inicio de la línea de comando

### Paso 3: Instalar Dependencias

```bash
# Actualizar pip (recomendado)
python -m pip install --upgrade pip

# Instalar todas las dependencias
pip install -r requirements.txt
```

**Dependencias instaladas:**
- `opencv-python` - Captura RTSP
- `ultralytics` - YOLO v8
- `supervision` - Utilidades para detecciones
- `numpy` - Operaciones numéricas
- `motor` - MongoDB async (futuro)
- `redis` - Cache (futuro)
- `ffmpeg-python` - Procesamiento video (futuro)

**⏱️ Tiempo estimado:** 2-5 minutos dependiendo de la conexión

---

## ⚙️ Configuración

### Paso 1: Crear archivo `.env`

```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# En Windows (PowerShell):
Copy-Item .env.example .env
```

### Paso 2: Editar `.env` con tus valores

Abrir `.env` con cualquier editor de texto y configurar:

```bash
# ============================================
# CONFIGURACIÓN RTSP (REQUERIDO)
# ============================================
RTSP_URL=rtsp://admin:admin@192.168.1.100:554/stream1
# ⚠️ IMPORTANTE: Cambiar por tu URL RTSP real

RTSP_RECONNECT_SEC=2.0
# Tiempo de espera antes de reconectar (segundos)

RTSP_MAX_FAILS_BEFORE_REOPEN=10
# Intentos fallidos antes de reabrir stream

RTSP_OPEN_TIMEOUT_SEC=5.0
# Timeout para abrir conexión RTSP

# ============================================
# CONFIGURACIÓN YOLO (REQUERIDO)
# ============================================
MODEL_PATH=assets/models/best.pt
# ⚠️ Ruta al modelo YOLO (ver sección siguiente)

CONF_THRES=0.5
# Umbral de confianza (0.0 - 1.0)
# Valores comunes: 0.3 (más detecciones) - 0.7 (más precisión)

# ============================================
# CONFIGURACIÓN COUNTER (HU-VIS-03)
# ============================================
COUNT_WINDOW=15
# Tamaño de ventana para estabilización

STABLE_MODE=median
# Estrategia: "median" (robusto) o "mode" (frecuente)

# ============================================
# MODO DE OPERACIÓN
# ============================================
VISION_MODE=rtsp_test
# Opciones:
#   - rtsp_test     (solo RTSP, sin detector)
#   - detector_test (RTSP + YOLO)
#   - counter_test  (RTSP + YOLO + Counter)

# ============================================
# OTROS
# ============================================
JPEG_QUALITY=80
# Calidad JPEG (0-100)
```

### Paso 3: Verificar configuración

```bash
# Ver el contenido del .env
cat .env

# En Windows (PowerShell):
Get-Content .env
```

---

## 🤖 Obtener el Modelo YOLO

### Opción 1: Modelo Pre-entrenado del Proyecto

**Si tu equipo ya tiene el modelo `best.pt`:**

1. Colocar el archivo en: `vision_edge/assets/models/best.pt`
2. Verificar que existe:
   ```bash
   # Linux/Mac
   ls -lh assets/models/best.pt
   
   # Windows (PowerShell)
   Get-Item assets/models/best.pt
   ```

### Opción 2: Entrenar tu Propio Modelo

```python
# Script para entrenar YOLO (ejecutar fuera del proyecto)
from ultralytics import YOLO

# Cargar modelo base
model = YOLO('yolov8n.pt')  # n=nano, s=small, m=medium, l=large, x=xlarge

# Entrenar con tu dataset
model.train(
    data='path/to/data.yaml',
    epochs=100,
    imgsz=640,
    batch=16,
    name='gas_cylinder_detector'
)

# El modelo estará en: runs/detect/gas_cylinder_detector/weights/best.pt
```

### Opción 3: Modelo de Prueba (solo testing)

```python
# Descargar un modelo YOLO general para probar
from ultralytics import YOLO

model = YOLO('yolov8n.pt')  # Descarga automáticamente
model.save('assets/models/best.pt')
```

**⚠️ IMPORTANTE:** El modelo debe estar en `assets/models/best.pt` exactamente.

---

## ▶️ Ejecución

### Verificación Rápida

Antes de ejecutar, verifica que todo esté listo:

```bash
# 1. Estás en la carpeta correcta?
pwd
# Deberías ver: .../ProyectoBalonesGAS/vision_edge

# 2. Entorno virtual activo?
# Deberías ver (.venv) en la línea de comando

# 3. Modelo YOLO existe?
# Windows:
Test-Path assets/models/best.pt
# Linux/Mac:
[ -f assets/models/best.pt ] && echo "✅ Modelo existe" || echo "❌ Modelo no encontrado"

# 4. Archivo .env existe?
# Windows:
Test-Path .env
# Linux/Mac:
[ -f .env ] && echo "✅ .env existe" || echo "❌ .env no encontrado"
```

### Ejecutar el Proyecto

```bash
# Ejecutar con configuración del .env
python -m app.main
```

**✅ Si todo está bien, deberías ver:**
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
...
```

---

## 🎯 Modos de Operación

El sistema tiene **3 modos** que puedes cambiar con la variable `VISION_MODE`:

### 1️⃣ Modo RTSP Test (HU-VIS-01) - DEFAULT

**Qué hace:** Prueba solo la conexión RTSP (200 frames)

**Configuración:**
```bash
# En .env
VISION_MODE=rtsp_test

# O por línea de comandos (Windows):
$env:VISION_MODE="rtsp_test"
python -m app.main

# O por línea de comandos (Linux/Mac):
export VISION_MODE=rtsp_test
python -m app.main
```

**Salida esperada:**
```
[RTSP] Connected: rtsp://...
[50/200] OK=50, FAIL=0, FPS=29.4
[100/200] OK=100, FAIL=0, FPS=29.7
[150/200] OK=150, FAIL=0, FPS=29.6
[200/200] OK=200, FAIL=0, FPS=29.5
Total frames OK: 200
```

**Cuándo usar:** Para verificar que la cámara RTSP funciona correctamente.

---

### 2️⃣ Modo Detector Test (HU-VIS-02)

**Qué hace:** RTSP + Detección YOLO (50 frames)

**Configuración:**
```bash
# En .env
VISION_MODE=detector_test

# O por línea de comandos (Windows):
$env:VISION_MODE="detector_test"
python -m app.main

# O por línea de comandos (Linux/Mac):
export VISION_MODE=detector_test
python -m app.main
```

**Salida esperada:**
```
[YOLO] Loading model: assets/models/best.pt
[YOLO] Model loaded successfully (conf=0.5)
[10/50] Processed=10, Detections=3, Avg=2.8, FPS=28.5
[20/50] Processed=20, Detections=2, Avg=2.5, FPS=29.1
...
Total detections: 135
Average detections per frame: 2.70
```

**Cuándo usar:** Para verificar que YOLO detecta objetos correctamente.

---

### 3️⃣ Modo Counter Test (HU-VIS-03)

**Qué hace:** RTSP + YOLO + Contador Estabilizado (80 frames)

**Configuración:**
```bash
# En .env
VISION_MODE=counter_test
COUNT_WINDOW=15
STABLE_MODE=median

# O por línea de comandos (Windows):
$env:VISION_MODE="counter_test"
$env:COUNT_WINDOW="15"
$env:STABLE_MODE="median"
python -m app.main

# O por línea de comandos (Linux/Mac):
export VISION_MODE=counter_test
export COUNT_WINDOW=15
export STABLE_MODE=median
python -m app.main
```

**Salida esperada:**
```
[YOLO] Model loaded successfully
[10/80] Raw=3, Stable=3, Window=15, FPS=28.5
[20/80] Raw=2, Stable=3, Window=15, FPS=29.1
[30/80] Raw=4, Stable=3, Window=15, FPS=28.7
...
Total frames processed: 80
```

**Cuándo usar:** Para verificar el conteo estabilizado (producción).

**Diferencia Raw vs Stable:**
- **Raw:** Conteo directo del frame actual (puede variar mucho)
- **Stable:** Conteo estabilizado con ventana (más confiable)

---

## 🔧 Solución de Problemas

### ❌ Error: "ModuleNotFoundError: No module named 'cv2'"

**Causa:** opencv-python no instalado  
**Solución:**
```bash
pip install opencv-python
```

---

### ❌ Error: "FileNotFoundError: Failed to load YOLO model at assets/models/best.pt"

**Causa:** Modelo YOLO no existe  
**Solución:**
1. Verificar ruta:
   ```bash
   ls assets/models/best.pt
   ```
2. Si no existe, ver sección [Obtener el Modelo YOLO](#obtener-el-modelo-yolo)

---

### ❌ Error: "[RTSP] Failed to open: rtsp://..."

**Causas posibles:**
1. URL incorrecta
2. Credenciales incorrectas
3. Cámara apagada/desconectada
4. Firewall bloqueando puerto

**Solución:**
1. Verificar URL con VLC o similar:
   ```
   VLC → Media → Open Network Stream → Pegar URL RTSP
   ```
2. Verificar formato correcto:
   ```
   rtsp://usuario:contraseña@192.168.1.100:554/stream1
   ```
3. Hacer ping a la cámara:
   ```bash
   ping 192.168.1.100
   ```
4. Verificar puerto abierto:
   ```bash
   # Windows:
   Test-NetConnection -ComputerName 192.168.1.100 -Port 554
   
   # Linux:
   nc -zv 192.168.1.100 554
   ```

---

### ❌ Error: "cannot be loaded because running scripts is disabled"

**Causa:** Política de ejecución de PowerShell (solo Windows)  
**Solución:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

### ❌ El programa se cierra inmediatamente

**Causa:** Posible error en .env o falta de configuración  
**Solución:**
1. Verificar que `.env` existe:
   ```bash
   cat .env
   ```
2. Ejecutar con modo verbose:
   ```bash
   python -m app.main 2>&1 | Tee-Object -FilePath debug.log
   ```
3. Revisar `debug.log` para ver el error completo

---

### ❌ FPS muy bajo (< 10 FPS)

**Causas posibles:**
1. CPU lento
2. Modelo YOLO muy grande
3. Red lenta (RTSP)

**Soluciones:**
1. Usar modelo más pequeño:
   ```
   yolov8n.pt (nano) - más rápido
   yolov8s.pt (small) - equilibrado
   yolov8m.pt (medium) - más preciso pero lento
   ```
2. Bajar resolución en settings (futuro)
3. Usar GPU si está disponible

---

### 🐛 Cómo reportar bugs

Si encuentras un error no documentado:

1. Capturar logs completos:
   ```bash
   python -m app.main > logs.txt 2>&1
   ```
2. Información del sistema:
   ```bash
   python --version
   pip list | grep -E "(opencv|ultralytics|supervision)"
   ```
3. Compartir:
   - `logs.txt`
   - Versión de Python
   - Sistema operativo
   - Contenido de `.env` (sin credenciales)

---

## 📚 Documentación Adicional

- **HU-VIS-01:** [docs/HU-VIS-01.md](docs/HU-VIS-01.md) - RTSP FrameSource
- **HU-VIS-02:** [docs/HU_VIS_02_detector.md](docs/HU_VIS_02_detector.md) - Detector YOLO
- **HU-VIS-03:** [docs/HU_VIS_03_counter.md](docs/HU_VIS_03_counter.md) - Counter Estabilizado

---

## 🎓 Comandos Útiles (Cheat Sheet)

```bash
# ========== BÁSICOS ==========
# Activar entorno virtual (Windows)
.\.venv\Scripts\Activate.ps1

# Activar entorno virtual (Linux/Mac)
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# ========== EJECUCIÓN ==========
# Modo por defecto (rtsp_test)
python -m app.main

# Modo detector (Windows)
$env:VISION_MODE="detector_test"; python -m app.main

# Modo counter (Windows)
$env:VISION_MODE="counter_test"; python -m app.main

# Modo detector (Linux/Mac)
VISION_MODE=detector_test python -m app.main

# Modo counter (Linux/Mac)
VISION_MODE=counter_test python -m app.main

# ========== DEBUGGING ==========
# Ver versiones instaladas
pip list

# Ver solo deps importantes
pip list | findstr -i "opencv ultralytics supervision numpy"

# Verificar Python
python --version

# Verificar modelo
Test-Path assets/models/best.pt  # Windows
ls -lh assets/models/best.pt     # Linux/Mac

# ========== TESTING RTSP ==========
# Probar URL RTSP con ffmpeg (si lo tienes instalado)
ffplay rtsp://admin:admin@192.168.1.100:554/stream1

# Probar URL RTSP con VLC
vlc rtsp://admin:admin@192.168.1.100:554/stream1
```

---

## ✅ Checklist Final

Antes de empezar, verifica:

- [ ] Python 3.12.3+ instalado
- [ ] Entorno virtual creado y activado (`.venv`)
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] Archivo `.env` creado y configurado
- [ ] Modelo YOLO en `assets/models/best.pt`
- [ ] URL RTSP válida y accesible
- [ ] Puedes hacer ping a la cámara
- [ ] `python -m app.main` ejecuta sin errores

---

## 👥 Soporte

Si tienes problemas o preguntas:
1. Revisar sección [Solución de Problemas](#solución-de-problemas)
2. Verificar logs con `python -m app.main > logs.txt 2>&1`
3. Consultar documentación en `docs/`
4. Contactar al equipo de desarrollo

---

**¡Listo para empezar! 🚀**
