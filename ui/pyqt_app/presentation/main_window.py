import sys
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTabWidget, QHBoxLayout
from PyQt5.QtCore import QTimer

from pyqt_app.presentation.widgets.video_panel import VideoPanel
from pyqt_app.presentation.widgets.counter_panel import CounterPanel

from pyqt_app.application.use_cases.refresh_frames import RefreshFrames
from pyqt_app.application.use_cases.refresh_metrics import RefreshMetrics
from pyqt_app.application.use_cases.switch_view import SwitchView
from pyqt_app.infrastructure.api.fastapi_client import FastApiClient

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Conteo de Balones - Costa Gas")
        self.resize(800, 600)

        # Dependencies
        self.client = FastApiClient(base_url="http://localhost:8000")
        self.uc_refresh_frames = RefreshFrames(self.client)
        self.uc_refresh_metrics = RefreshMetrics(self.client)
        self.uc_switch_view = SwitchView()

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

        # Counter Panel
        self.counter_panel = CounterPanel()
        self.main_layout.addWidget(self.counter_panel)

        # Timers
        self.frame_timer = QTimer()
        self.frame_timer.timeout.connect(self.update_frame)
        self.frame_timer.start(100) # 100-200ms

        self.metrics_timer = QTimer()
        self.metrics_timer.timeout.connect(self.update_metrics)
        self.metrics_timer.start(500) # 300-800ms
        
        # Initial state
        self.on_tab_changed(0)

    def on_tab_changed(self, index):
        mode = "raw" if index == 0 else "processed"
        self.uc_switch_view.execute(mode)
        # Update title or visual indicator if needed
        self.video_panel.label_title.setText(f"Vista: {mode.capitalize()}")

    def update_frame(self):
        mode = self.uc_switch_view.current_mode
        pixmap = self.uc_refresh_frames.execute(mode)
        if not pixmap.isNull():
            self.video_panel.update_image(pixmap)

    def update_metrics(self):
        count = self.uc_refresh_metrics.execute()
        self.counter_panel.update_count(count)
