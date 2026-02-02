import sys
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTabWidget, QHBoxLayout
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, QObject
from PyQt5.QtGui import QPixmap

from pyqt_app.presentation.widgets.video_panel import VideoPanel
from pyqt_app.presentation.widgets.counter_panel import CounterPanel
from pyqt_app.presentation.workers.mjpeg_worker import MjpegWorker

from pyqt_app.application.use_cases.refresh_metrics import RefreshMetrics
from pyqt_app.application.use_cases.switch_view import SwitchView
from pyqt_app.infrastructure.api.fastapi_client import FastApiClient
from pyqt_app.infrastructure.config import StreamConfig


class LineYWorker(QObject):
    """Worker para enviar line_y al backend sin bloquear la UI."""
    finished = pyqtSignal()
    
    def __init__(self, client: FastApiClient, line_y: int):
        super().__init__()
        self.client = client
        self.line_y = line_y
    
    def run(self):
        """Ejecutar request HTTP en thread separado."""
        self.client.set_line_y(self.line_y)
        self.finished.emit()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Conteo de Balones - Costa Gas")
        self.resize(800, 600)

        # Dependencies for metrics (keep existing API client)
        self.client = FastApiClient(base_url=StreamConfig.BACKEND_BASE_URL)
        self.uc_refresh_metrics = RefreshMetrics(self.client)
        self.uc_switch_view = SwitchView()

        # Streaming state
        self.current_thread = None
        self.current_worker = None
        self.current_stream_url = None
        
        # Backend failure tracking
        self.backend_fail_streak = 0
        
        # Line Y update thread
        self.line_y_thread = None
        self.line_y_worker = None

        # UI Components
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # Tabs for Raw/Processed
        self.tabs = QTabWidget()
        self.tabs.addTab(QWidget(), "Bruto")
        self.tabs.addTab(QWidget(), "Procesado")
        self.tabs.currentChanged.connect(self.on_tab_changed)
        self.main_layout.addWidget(self.tabs)

        # Video Panel
        self.video_panel = VideoPanel("Vista de Cámara")
        self.main_layout.addWidget(self.video_panel)

        # Counter Panel (with line control)
        self.counter_panel = CounterPanel()
        self.counter_panel.line_y_changed.connect(self.on_line_y_changed)
        self.main_layout.addWidget(self.counter_panel)

        # Timer for metrics only (streaming handles frames)
        self.metrics_timer = QTimer()
        self.metrics_timer.timeout.connect(self.update_metrics)
        self.metrics_timer.start(1000)  # 1 segundo
        
        # Initial state - start streaming
        self.on_tab_changed(0)

    def on_tab_changed(self, index):
        """Cambia el stream cuando se cambia de tab."""
        mode = "raw" if index == 0 else "processed"
        self.uc_switch_view.execute(mode)
        self.video_panel.label_title.setText(f"Vista: {mode.capitalize()}")
        
        # Detener stream anterior y arrancar el nuevo
        self.stop_stream()
        self.start_stream(mode)

    def start_stream(self, mode: str):
        """Inicia un nuevo stream MJPEG en un thread separado."""
        # Determinar URL según modo
        url = StreamConfig.STREAM_RAW_URL if mode == "raw" else StreamConfig.STREAM_PROCESSED_URL
        self.current_stream_url = url
        
        # Crear worker y thread
        self.current_worker = MjpegWorker(url, StreamConfig.STREAM_TIMEOUT_SEC)
        self.current_thread = QThread()
        
        # Mover worker al thread
        self.current_worker.moveToThread(self.current_thread)
        
        # Conectar signals
        self.current_worker.frame_ready.connect(self.on_frame_received)
        self.current_worker.status.connect(self.on_stream_status)
        self.current_worker.error.connect(self.on_stream_error)
        
        # Cuando termine el worker, cerrar el thread
        self.current_worker.finished.connect(self.current_thread.quit)
        
        # Limpieza Qt automática (evita leaks)
        self.current_worker.finished.connect(self.current_worker.deleteLater)
        self.current_thread.finished.connect(self.current_thread.deleteLater)
        
        self.current_thread.started.connect(self.current_worker.run)
        
        # Iniciar thread
        self.current_thread.start()
    
    def stop_stream(self):
        """Detiene el stream actual de forma segura."""
        if self.current_worker:
            self.current_worker.stop()
        
        if self.current_thread:
            try:
                if self.current_thread.isRunning():
                    self.current_thread.quit()
                    self.current_thread.wait(2000)  # Esperar máximo 2 segundos
            except RuntimeError:
                # Thread ya fue eliminado por deleteLater, es OK
                pass
            
        self.current_worker = None
        self.current_thread = None
        self.current_stream_url = None
    
    def on_frame_received(self, image):
        """
        Callback cuando llega un nuevo frame del stream.
        Convierte QImage a QPixmap en el GUI thread (thread-safe).
        """
        pixmap = QPixmap.fromImage(image)
        self.video_panel.update_image(pixmap)
    
    def on_stream_status(self, message: str):
        """Callback para mensajes de estado del stream."""
        if "Connecting" in message:
            self.video_panel.show_message(f"🔄 {message}", is_error=False)
    
    def on_stream_error(self, error_message: str):
        """Callback cuando hay un error en el stream."""
        # Determinar si es error de VisionEdge
        if "Connection error" in error_message or "Timeout" in error_message:
            # Mostrar error con URL real del stream
            self.video_panel.show_connection_error("VisionEdge", self.current_stream_url or "")
        else:
            self.video_panel.show_message(error_message, is_error=True)

    def update_metrics(self):
        """
        Actualiza las métricas desde el backend API.
        Maneja streak de fallos para mostrar 🔴 solo después de 3 fallos consecutivos.
        """
        try:
            count = self.uc_refresh_metrics.execute()
            
            # RefreshMetrics retorna un int (puede ser 0 legítimo)
            # Si llegamos aquí sin exception, es éxito
            if count is not None:
                # Éxito: resetear streak y actualizar UI
                self.backend_fail_streak = 0
                self.counter_panel.show_connection_status(is_connected=True)
                self.counter_panel.set_count(count)
            else:
                # Si execute() retorna None explícitamente, contarlo como fallo
                raise ValueError("Backend returned None")
                
        except Exception:
            # Fallo: incrementar streak
            self.backend_fail_streak += 1
            
            # Solo mostrar error después de 3 fallos consecutivos
            if self.backend_fail_streak >= 3:
                backend_url = f"{StreamConfig.BACKEND_BASE_URL}/api/metrics"
                self.counter_panel.show_connection_status(
                    is_connected=False,
                    message=f"⚠️ Verifica {backend_url}"
                )

    def on_line_y_changed(self, value: int):
        """
        Enviar nuevo valor de línea Y al backend de forma asíncrona (no bloquea UI).
        """
        # Si hay un thread anterior corriendo, no hacer nada (evita saturar)
        if self.line_y_thread is not None:
            try:
                if self.line_y_thread.isRunning():
                    return
            except RuntimeError:
                # Thread ya fue eliminado por deleteLater, es OK continuar
                pass
        
        # Crear worker y thread para el request HTTP
        self.line_y_worker = LineYWorker(self.client, value)
        self.line_y_thread = QThread()
        
        self.line_y_worker.moveToThread(self.line_y_thread)
        
        # Conectar signals
        self.line_y_worker.finished.connect(self.line_y_thread.quit)
        self.line_y_worker.finished.connect(self.line_y_worker.deleteLater)
        self.line_y_thread.finished.connect(self.line_y_thread.deleteLater)
        self.line_y_thread.finished.connect(self._on_line_y_thread_finished)
        
        self.line_y_thread.started.connect(self.line_y_worker.run)
        self.line_y_thread.start()
    
    def _on_line_y_thread_finished(self):
        """Limpia las referencias cuando el thread termina."""
        self.line_y_thread = None
        self.line_y_worker = None
    
    def closeEvent(self, event):
        """Limpia recursos al cerrar la ventana."""
        self.stop_stream()
        self.metrics_timer.stop()
        
        # Esperar a que termine el thread de line_y si está corriendo
        if self.line_y_thread is not None:
            try:
                if self.line_y_thread.isRunning():
                    self.line_y_thread.quit()
                    self.line_y_thread.wait(1000)
            except RuntimeError:
                # Thread ya fue eliminado, es OK
                pass
        
        event.accept()
