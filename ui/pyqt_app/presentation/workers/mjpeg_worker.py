from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QImage
import requests

from pyqt_app.infrastructure.api.mjpeg_reader import iter_mjpeg_frames


class MjpegWorker(QObject):
    """
    Worker que lee un stream MJPEG en un thread separado y emite frames al main thread.
    
    THREAD-SAFE: Emite QImage (no QPixmap) porque QImage es thread-safe.
    La conversión a QPixmap se hace en el GUI thread.
    
    Signals:
        frame_ready(QImage): Emitido cuando hay un nuevo frame disponible
        status(str): Emitido para reportar el estado del stream
        error(str): Emitido cuando ocurre un error
        finished(): Emitido cuando el worker termina (éxito o error)
    """
    
    frame_ready = pyqtSignal(QImage)
    status = pyqtSignal(str)
    error = pyqtSignal(str)
    finished = pyqtSignal()
    
    def __init__(self, url: str, timeout_sec: float = 5.0):
        """
        Args:
            url: URL del stream MJPEG
            timeout_sec: Timeout para la conexión inicial
        """
        super().__init__()
        self.url = url
        self.timeout_sec = timeout_sec
        self._should_stop = False
    
    def run(self):
        """
        Método principal que se ejecuta en el thread separado.
        Lee el stream MJPEG y emite frames continuamente hasta que se llame stop().
        """
        self.status.emit(f"Connecting to {self.url}...")
        
        try:
            for jpeg_data in iter_mjpeg_frames(
                self.url,
                timeout_sec=self.timeout_sec,
                read_timeout_sec=1.0,  # Timeout corto para poder parar rápido
                stop_flag=lambda: self._should_stop,
            ):
                if self._should_stop:
                    break
                
                # Convertir JPEG bytes a QImage (thread-safe)
                img = QImage.fromData(jpeg_data, "JPG")
                if not img.isNull():
                    self.frame_ready.emit(img)
                    
        except requests.Timeout:
            self.error.emit(f"⚠️ Timeout connecting to {self.url}")
        except requests.ConnectionError:
            self.error.emit("⚠️ Connection error: Stream server may be offline")
        except requests.RequestException as e:
            self.error.emit(f"⚠️ Request error: {str(e)}")
        except Exception as e:
            self.error.emit(f"⚠️ Unexpected error: {str(e)}")
        finally:
            self.status.emit("Stream ended")
            self.finished.emit()
    
    def stop(self):
        """
        Detiene el loop de lectura del stream de forma thread-safe.
        El stop_flag es chequeado por chunk en iter_mjpeg_frames.
        """
        self._should_stop = True
