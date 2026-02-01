from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QFrame, QHBoxLayout
from PyQt5.QtCore import Qt


class CounterPanel(QWidget):
    """
    Panel que muestra el contador de balones y estado de conexión del backend.
    Es 'tonto': no decide por sí solo cuándo mostrar errores.
    """
    
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
