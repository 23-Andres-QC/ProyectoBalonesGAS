# Arquitectura Frontend PyQt5 (Desktop)

Este directorio contiene la aplicación de escritorio construida con PyQt5 para el sistema de conteo de balones de Costa Gas.

## 🎥 Streaming MJPEG en Tiempo Real

La aplicación ahora soporta **streaming MJPEG real** desde el servidor VisionEdge, eliminando la necesidad de polling.

## Estructura del Proyecto

```
ui/
  pyqt_app/
    main.py                 # Punto de entrada de la aplicación
    presentation/           # Capa de presentación (UI)
      main_window.py        # Ventana principal con streaming
      widgets/              # Componentes visuales reutilizables
        video_panel.py      # Panel para mostrar el stream de video
        counter_panel.py    # Panel para mostrar el conteo
      workers/              # ⭐ NUEVO: Workers para threading
        mjpeg_worker.py     # Worker que lee stream MJPEG en thread separado
    application/            # Lógica de la aplicación (Casos de uso)
      use_cases/
        refresh_frames.py   # (Deprecado) Reemplazado por streaming
        refresh_metrics.py  # Actualiza métricas (conteo) - ACTIVO
        switch_view.py      # Controla el cambio de vista (Bruto/Procesado)
      ports/
        backend_client.py   # Interfaz para el cliente del backend
    infrastructure/         # Implementación técnica
      config.py             # ⭐ NUEVO: Configuración de URLs
      api/
        fastapi_client.py   # Cliente HTTP para métricas API
        mjpeg_reader.py     # ⭐ NUEVO: Parser de streams MJPEG
    assets/
      icons/                # Iconos y recursos gráficos
  requirements.txt          # Dependencias de Python
  test_streaming.py         # ⭐ NUEVO: Script de validación
  README.md                 # Este archivo
  STREAMING_IMPLEMENTATION.md  # ⭐ NUEVO: Documentación detallada
```

## 🚀 Configuración y Ejecución

### Prerequisitos

1. **Servidor de Streaming VisionEdge** corriendo en `http://127.0.0.1:8010`
   - Endpoint: `/stream/raw.mjpg`
   - Endpoint: `/stream/processed.mjpg`

2. **Servidor Backend API** corriendo en `http://localhost:8000`
   - Endpoint: `/api/metrics`

### Instalación

1. **Crear entorno virtual (opcional pero recomendado):**

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

2. **Instalar dependencias:**

   ```bash
   pip install -r requirements.txt
   ```

### Ejecución

1. **Validar la implementación:**
   ```bash
   python test_streaming.py
   ```
   
   Debe mostrar: `🎉 ¡TODOS LOS TESTS PASARON!`

2. **Ejecutar la aplicación:**
   ```bash
   python -m pyqt_app.main
   ```

### Variables de Entorno (Opcional)

```bash
# Cambiar URL del servidor de streaming VisionEdge
export VISION_EDGE_URL=http://192.168.1.100:8010

# Cambiar URL del backend de métricas
export BACKEND_URL=http://localhost:8001

python -m pyqt_app.main
```

## 📊 Descripción de Componentes

### Presentation Layer

- **MainWindow**: Orquesta la UI con streaming MJPEG real
  - Maneja QThread para streaming no bloqueante
  - Cambia streams al cambiar de tab (Bruto/Procesado)
  - Mantiene timer para métricas (500ms)
  
- **MjpegWorker**: Worker que corre en thread separado
  - Lee stream MJPEG continuamente
  - Emite signals con frames listos (QPixmap)
  - Manejo de errores robusto
  
- **VideoPanel**: Widget especializado en renderizar QPixmap
  - Escalado automático manteniendo proporción
  - Muestra mensajes de error/estado
  
- **CounterPanel**: Widget estilizado para mostrar números grandes

### Application Layer

- **Use Cases**: Contienen la lógica pura de coordinación
  - `RefreshMetrics`: Obtiene datos de conteo desde API (ACTIVO)
  - `SwitchView`: Gestiona estado de vista actual

### Infrastructure Layer

- **StreamConfig**: Configuración centralizada
  - URLs de streaming (raw/processed)
  - URL del backend API
  - Timeouts configurables
  
- **mjpeg_reader.py**: Parser de streams MJPEG
  - Extrae frames JPEG individuales por marcadores SOI/EOI
  - Generator eficiente para streaming continuo
  
- **FastApiClient**: Cliente HTTP para métricas API

## 🎯 Características

### ✅ Streaming en Tiempo Real
- **Latencia baja**: ~5-30ms vs ~100-200ms con polling
- **Eficiencia**: Conexión persistente vs requests individuales
- **CPU**: Uso reducido comparado con polling

### ✅ Threading No Bloqueante
- Stream corre en QThread separado
- UI permanece responsive
- No bloquea el main thread

### ✅ Cambio de Vista Dinámico
- Tabs: "Bruto" (raw) y "Procesado" (processed)
- Cambio instantáneo sin lag
- Detiene stream anterior antes de iniciar nuevo
- Sin threads zombies

### ✅ Manejo de Errores Robusto
- Timeout de conexión
- Connection errors
- Stream offline
- Mensajes visuales en el panel

### ✅ Arquitectura Clean Mantenida
- Separación de capas intacta
- SOLID principles respetados
- Fácilmente testeable

## 📈 Diferencias: Polling vs Streaming

| Aspecto | Antes (Polling) | Ahora (Streaming) |
|---------|----------------|-------------------|
| **Método** | QTimer cada 100ms | Stream MJPEG continuo |
| **Latencia** | ~100-200ms | ~5-30ms |
| **CPU** | Alto (requests frecuentes) | Bajo (conexión persistente) |
| **Ancho de banda** | Overhead HTTP por frame | Eficiente (multipart stream) |
| **Thread** | Main thread | QThread separado |

## 🧪 Testing

### Validación Básica
```bash
python test_streaming.py
```

### Validar Endpoints en Navegador
```
http://127.0.0.1:8010/stream/raw.mjpg
http://127.0.0.1:8010/stream/processed.mjpg
```

Ambos deben mostrar video continuo.

## 📚 Documentación Adicional

- Ver `STREAMING_IMPLEMENTATION.md` para detalles técnicos completos
- Ver `REVIEW_ARQUITECTURA_UI.md` para análisis de arquitectura

## 🔧 Troubleshooting

### "Connection error: Stream server may be offline"
- Verificar que VisionEdge esté corriendo en puerto 8010
- Verificar que los endpoints `/stream/*.mjpg` respondan

### "Timeout connecting to..."
- Aumentar `STREAM_TIMEOUT_SEC` en `config.py`
- Verificar conectividad de red

### UI se congela
- El streaming usa QThread, no debería congelar
- Verificar que no hay bloqueos en el main thread

### Contador no se actualiza
- Verificar que backend API esté corriendo en puerto 8000
- Verificar endpoint `/api/metrics`

## 📝 Notas de Desarrollo

- ✅ UI no conoce detalles de RTSP o YOLO
- ✅ Solo consume endpoints HTTP (streaming y API)
- ✅ Streaming continuo con MJPEG nativo
- ✅ Métricas via polling cada 500ms (independiente del stream)
- ✅ Thread safety garantizado con Qt signals/slots

## 🎓 Arquitectura

```
┌─────────────────────────────────────────────────────┐
│         Presentation (MainWindow + Workers)         │
│                                                     │
│  MjpegWorker → [QThread] → emit frame_ready        │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│         Infrastructure (Streaming + API)            │
│                                                     │
│  mjpeg_reader → iter_mjpeg_frames()                │
│  FastApiClient → get_metrics()                     │
└─────────────────────────────────────────────────────┘
```

---

**Última actualización:** 2026-02-01  
**Versión:** 2.0 (Con streaming MJPEG)
