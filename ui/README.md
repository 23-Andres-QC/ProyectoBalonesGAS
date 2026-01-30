# Arquitectura Frontend PyQt5 (Desktop)

Este directorio contiene la aplicación de escritorio construida con PyQt5 para el sistema de conteo de balones de Costa Gas.

## Estructura del Proyecto

```
ui/
  pyqt_app/
    main.py                 # Punto de entrada de la aplicación
    presentation/           # Capa de presentación (UI)
      main_window.py        # Ventana principal
      widgets/              # Componentes visuales reutilizables
        video_panel.py      # Panel para mostrar el stream de video
        counter_panel.py    # Panel para mostrar el conteo
    application/            # Lógica de la aplicación (Casos de uso)
      use_cases/
        refresh_frames.py   # Obtiene y procesa cuadros de video
        refresh_metrics.py  # Actualiza métricas (conteo)
        switch_view.py      # Controla el cambio de vista (Bruto/Procesado)
      ports/
        backend_client.py   # Interfaz para el cliente del backend
    infrastructure/         # Implementación técnica
      api/
        fastapi_client.py   # Cliente HTTP para comunicarse con la API (FastAPI)
    assets/
      icons/                # Iconos y recursos gráficos
  requirements.txt          # Dependencias de Python
  README.md                 # Este archivo
```

## Configuración y Ejecución

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

3. **Ejecutar la aplicación:**
   Desde el directorio `ui/`:
   ```bash
   python -m pyqt_app.main
   ```
   _Nota: Se asume que el backend (FastAPI) está corriendo en `http://localhost:8000`._

## Descripción de Componentes

### Presentation Layer

- **MainWindow**: Orquesta la UI, manejando las pestañas y los temporizadores (Timers) para refrescar datos.
- **VideoPanel**: Widget especializado en renderizar `QPixmap`.
- **CounterPanel**: Widget estilizado para mostrar números grandes.

### Application Layer

- **Use Cases**: Contienen la lógica pura de coordinación. No dependen de la implementación HTTP directa, sino de interfaces (Ports).
  - `RefreshFrames`: Llama al puerto para obtener RAW o PROCESSED y devuelve un objeto de imagen listo para la UI.
  - `RefreshMetrics`: Obtiene los datos numéricos.

### Infrastructure Layer

- **FastApiClient**: Implementa la interfaz `BackendClient` usando `requests` para hablar con el backend real.

## Notas de Desarrollo

- La UI no conoce los detalles de RTSP o YOLO. Solo consume endpoints HTTP que devuelven imágenes (MJPEG/Blob frames) y JSON.
- Frecuencia de actualización de video: ~100-200ms.
- Frecuencia de actualización de métricas: ~300-800ms.
