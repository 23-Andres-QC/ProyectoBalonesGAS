# Vision Edge (ALFA)

## Objetivo
Conectar RTSP, ejecutar detección, producir `raw_jpeg`, `processed_jpeg` y `metrics` para consumo del backend.

## Configuración
Copiar `.env.example` a `.env` y ajustar:

```
RTSP_URL=rtsp://user:pass@ip:554/stream1
MODEL_PATH=assets/models/best.pt
CONF_THRES=0.5
JPEG_QUALITY=80
COUNT_WINDOW=15
```

## Nota
- El modelo debe estar en `assets/models/best.pt`.
- Este esqueleto no ejecuta inferencia todavía.
