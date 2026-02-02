from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QFrame, QHBoxLayout, QLineEdit, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIntValidator


class CounterPanel(QWidget):
    """Panel que muestra el contador y permite ajustar la línea de conteo."""

    line_y_changed = pyqtSignal(int)

    # Estilos constantes
    DEFAULT_INFO_STYLE = "font-size: 10px; color: #666;"
    ERROR_INFO_STYLE = "font-size: 10px; color: #ff6b6b;"

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)
        self.setLayout(self.layout)
        self.setMaximumHeight(150)  # Limitar altura del panel

        # Frame for styling
        self.frame = QFrame()
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setStyleSheet("background-color: #f0f0f0; border-radius: 5px; padding: 5px;")

        frame_layout = QVBoxLayout()
        frame_layout.setSpacing(3)
        self.frame.setLayout(frame_layout)

        # Contenedor horizontal: Título + Contador + Controles
        main_horizontal = QHBoxLayout()
        main_horizontal.setSpacing(20)

        # ==== COLUMNA IZQUIERDA: Título con status ====
        left_column = QVBoxLayout()
        left_column.setSpacing(2)
        
        title_layout = QHBoxLayout()
        self.label_title = QLabel("Conteo de Balones")
        self.label_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #333;")
        
        self.status_indicator = QLabel("🟢")
        self.status_indicator.setStyleSheet("font-size: 12px;")
        self.status_indicator.setToolTip("Backend API conectado")
        
        title_layout.addWidget(self.label_title)
        title_layout.addWidget(self.status_indicator)
        title_layout.addStretch()
        
        left_column.addLayout(title_layout)
        
        # Info label
        self.info_label = QLabel("")
        self.info_label.setStyleSheet(self.DEFAULT_INFO_STYLE)
        left_column.addWidget(self.info_label)
        
        main_horizontal.addLayout(left_column, 2)

        # ==== COLUMNA CENTRAL: Contador (destacado) ====
        counter_layout = QVBoxLayout()
        counter_layout.setAlignment(Qt.AlignCenter)
        
        self.counter_label = QLabel("0")
        self.counter_label.setAlignment(Qt.AlignCenter)
        self.counter_label.setStyleSheet("font-size: 36px; font-weight: bold; color: #0078d7;")
        counter_layout.addWidget(self.counter_label)
        
        main_horizontal.addLayout(counter_layout, 1)

        # ==== COLUMNA DERECHA: Control de Línea Y ====
        line_control = QHBoxLayout()
        line_control.setSpacing(5)
        
        self.line_label = QLabel("Línea Y:")
        self.line_label.setStyleSheet("font-size: 12px; font-weight: bold;")
        
        self.line_input = QLineEdit()
        self.line_input.setText("479")
        self.line_input.setValidator(QIntValidator(0, 2000))
        self.line_input.setMaximumWidth(60)
        self.line_input.setStyleSheet("""
            QLineEdit {
                font-size: 12px;
                padding: 3px;
                border: 2px solid #ccc;
                border-radius: 3px;
            }
            QLineEdit:focus {
                border: 2px solid #0078d7;
            }
        """)
        self.line_input.returnPressed.connect(self._on_update_button_clicked)
        
        self.update_button = QPushButton("Actualizar")
        self.update_button.setMaximumWidth(80)
        self.update_button.setStyleSheet("""
            QPushButton {
                background-color: #0078d7;
                color: white;
                font-size: 11px;
                font-weight: bold;
                padding: 4px 8px;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #004578;
            }
        """)
        self.update_button.clicked.connect(self._on_update_button_clicked)
        
        line_control.addWidget(self.line_label)
        line_control.addWidget(self.line_input)
        line_control.addWidget(self.update_button)
        line_control.addStretch()
        
        main_horizontal.addLayout(line_control, 2)

        frame_layout.addLayout(main_horizontal)
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
                    font-size: 12px;
                    padding: 3px;
                    border: 2px solid #ff6b6b;
                    border-radius: 3px;
                }
            """)
            return
        
        try:
            value = int(text)
            
            # Validar rango
            if value < 0 or value > 2000:
                self.line_input.setStyleSheet("""
                    QLineEdit {
                        font-size: 12px;
                        padding: 3px;
                        border: 2px solid #ff6b6b;
                        border-radius: 3px;
                    }
                """)
                return
            
            # Resetear estilo a normal con borde verde
            self.line_input.setStyleSheet("""
                QLineEdit {
                    font-size: 12px;
                    padding: 3px;
                    border: 2px solid #28a745;
                    border-radius: 3px;
                }
            """)
            
            # Emitir signal al backend
            self.line_y_changed.emit(value)
            
            # Feedback visual temporal (verde → gris después de 1 seg)
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(1000, lambda: self.line_input.setStyleSheet("""
                QLineEdit {
                    font-size: 12px;
                    padding: 3px;
                    border: 2px solid #ccc;
                    border-radius: 3px;
                }
            """))
            
        except ValueError:
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
