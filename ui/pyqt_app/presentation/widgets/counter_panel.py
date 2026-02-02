from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QFrame, QHBoxLayout, QLineEdit, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIntValidator


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

        # TextField + Button para ajustar línea Y
        line_layout = QHBoxLayout()
        
        self.line_label = QLabel("Línea Y:")
        self.line_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        
        self.line_input = QLineEdit()
        self.line_input.setText("479")
        self.line_input.setValidator(QIntValidator(0, 2000))  # Solo números 0-2000
        self.line_input.setMaximumWidth(80)
        self.line_input.setStyleSheet("""
            QLineEdit {
                font-size: 14px;
                padding: 5px;
                border: 2px solid #ccc;
                border-radius: 5px;
            }
            QLineEdit:focus {
                border: 2px solid #0078d7;
            }
        """)
        self.line_input.returnPressed.connect(self._on_update_button_clicked)  # Enter también actualiza
        
        self.update_button = QPushButton("Actualizar")
        self.update_button.setStyleSheet("""
            QPushButton {
                background-color: #0078d7;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 5px 15px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #004578;
            }
        """)
        self.update_button.clicked.connect(self._on_update_button_clicked)
        
        line_layout.addWidget(self.line_label)
        line_layout.addWidget(self.line_input)
        line_layout.addWidget(self.update_button)
        line_layout.addStretch()
        
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

    def _on_update_button_clicked(self) -> None:
        """
        Cuando el usuario hace click en 'Actualizar' o presiona Enter.
        Valida el input y emite signal al backend.
        """
        text = self.line_input.text().strip()
        
        # Validar que no esté vacío
        if not text:
            self.line_input.setStyleSheet("""
                QLineEdit {
                    font-size: 14px;
                    padding: 5px;
                    border: 2px solid #ff6b6b;
                    border-radius: 5px;
                }
            """)
            return
        
        try:
            value = int(text)
            
            # Validar rango
            if value < 0 or value > 2000:
                self.line_input.setStyleSheet("""
                    QLineEdit {
                        font-size: 14px;
                        padding: 5px;
                        border: 2px solid #ff6b6b;
                        border-radius: 5px;
                    }
                """)
                return
            
            # Resetear estilo a normal
            self.line_input.setStyleSheet("""
                QLineEdit {
                    font-size: 14px;
                    padding: 5px;
                    border: 2px solid #28a745;
                    border-radius: 5px;
                }
            """)
            
            # Emitir signal al backend
            self.line_y_changed.emit(value)
            
            # Feedback visual temporal (verde por 1 segundo)
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(1000, lambda: self.line_input.setStyleSheet("""
                QLineEdit {
                    font-size: 14px;
                    padding: 5px;
                    border: 2px solid #ccc;
                    border-radius: 5px;
                }
            """))
            
        except ValueError:
            # Esto no debería pasar por el QIntValidator, pero por si acaso
            pass
    
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
