from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QFrame, QHBoxLayout, QSlider
from PyQt5.QtCore import Qt, pyqtSignal


class CounterPanel(QWidget):
    """Panel que muestra el contador y permite ajustar la línea de conteo."""

    line_y_changed = pyqtSignal(int)

    # Estilos constantes
    DEFAULT_INFO_STYLE = "font-size: 11px; color: #666;"
    ERROR_INFO_STYLE = "font-size: 11px; color: #ff6b6b;"

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Frame for styling
        self.frame = QFrame()
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setStyleSheet("background-color: #f0f0f0; border-radius: 10px; padding: 10px;")

        frame_layout = QVBoxLayout()
        self.frame.setLayout(frame_layout)

        # Title with status indicator
        title_layout = QHBoxLayout()

        self.label_title = QLabel("Conteo de Balones")
        self.label_title.setAlignment(Qt.AlignCenter)
        self.label_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")

        self.status_indicator = QLabel("🟢")
        self.status_indicator.setStyleSheet("font-size: 14px;")
        self.status_indicator.setToolTip("Backend API conectado")

        title_layout.addStretch()
        title_layout.addWidget(self.label_title)
        title_layout.addWidget(self.status_indicator)
        title_layout.addStretch()

        frame_layout.addLayout(title_layout)

        # Counter label
        self.counter_label = QLabel("0")
        self.counter_label.setAlignment(Qt.AlignCenter)
        self.counter_label.setStyleSheet("font-size: 48px; font-weight: bold; color: #0078d7;")
        frame_layout.addWidget(self.counter_label)

        # Slider para ajustar línea Y
        line_layout = QHBoxLayout()
        self.line_label = QLabel("Línea Y: 450")
        self.line_slider = QSlider(Qt.Horizontal)
        self.line_slider.setRange(0, 1000)
        self.line_slider.setValue(450)
        self.line_slider.valueChanged.connect(self._on_line_slider_changed)
        line_layout.addWidget(self.line_label)
        line_layout.addWidget(self.line_slider)
        frame_layout.addLayout(line_layout)

        # Info label for backend status
        self.info_label = QLabel("")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet(self.DEFAULT_INFO_STYLE)
        frame_layout.addWidget(self.info_label)

        self.layout.addWidget(self.frame)

    def set_count(self, count: int):
        """
        Actualiza el contador.
        Solo actualiza el número, no cambia estado de conexión.
        """
        self.counter_label.setText(str(count))

    def _on_line_slider_changed(self, value: int) -> None:
        """Handle local slider change and emit signal to backend."""
        self.line_label.setText(f"Línea Y: {value}")
        self.line_y_changed.emit(int(value))
    
    def show_connection_status(self, is_connected: bool, message: str = ""):
        """
        Actualiza el indicador visual de conexión.
        
        Args:
            is_connected: True si hay conexión, False si no
            message: Mensaje opcional a mostrar (vacío para limpiar)
        """
        if is_connected:
            # Estado conectado
            self.status_indicator.setText("🟢")
            self.status_indicator.setToolTip("Backend API conectado")
            self.info_label.setText("")
            self.info_label.setStyleSheet(self.DEFAULT_INFO_STYLE)
        else:
            # Estado desconectado
            self.status_indicator.setText("🔴")
            self.status_indicator.setToolTip("Backend API desconectado")
            self.info_label.setText(message if message else "⚠️ Sin conexión con Backend API")
            self.info_label.setStyleSheet(self.ERROR_INFO_STYLE)
