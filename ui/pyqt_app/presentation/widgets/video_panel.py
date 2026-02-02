from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage


class VideoPanel(QWidget):
    """
    Panel que muestra video MJPEG o mensajes de estado.
    Maneja reescalado automático y reseteo de estilos.
    """
    
    # Estilos constantes
    STYLE_NORMAL = (
        "background-color: black; "
        "color: white; "
        "font-size: 16px; "
        "padding: 10px;"
    )
    
    STYLE_ERROR = (
        "background-color: #1a1a1a; "
        "color: #ff6b6b; "
        "font-size: 16px; "
        "padding: 10px; "
        "border: 2px solid #ff6b6b; "
        "border-radius: 5px;"
    )
    
    def __init__(self, title: str = "Video"):
        super().__init__()
        self.layout = QVBoxLayout()
        self.layout.setSpacing(2)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        
        # Título más compacto
        self.label_title = QLabel(title)
        self.label_title.setAlignment(Qt.AlignCenter)
        self.label_title.setStyleSheet("font-size: 12px; font-weight: bold; color: #666; padding: 2px;")
        self.label_title.setMaximumHeight(20)
        self.layout.addWidget(self.label_title)
        
        # Display de video - sin altura mínima fija para que se expanda
        self.video_display = QLabel("🔌 Esperando conexión...")
        self.video_display.setAlignment(Qt.AlignCenter)
        self.video_display.setStyleSheet(self.STYLE_NORMAL)
        self.video_display.setWordWrap(True)
        self.video_display.setSizePolicy(
            self.video_display.sizePolicy().Expanding,
            self.video_display.sizePolicy().Expanding
        )
        self.layout.addWidget(self.video_display, 1)  # stretch=1 para expandirse
        
        # Guardar último frame para reescalado
        self._last_pixmap = None

    def update_image(self, pixmap: QPixmap):
        """
        Actualiza el panel con una nueva imagen.
        Resetea estilos y guarda el frame para reescalar.
        """
        if not pixmap.isNull():
            # SIEMPRE resetear estilo a normal
            self.video_display.setStyleSheet(self.STYLE_NORMAL)
            
            # Limpiar cualquier texto previo
            self.video_display.setText("")
            
            # Guardar el frame original
            self._last_pixmap = pixmap
            
            # Escalar y mostrar
            scaled = pixmap.scaled(
                self.video_display.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.video_display.setPixmap(scaled)
    
    def show_message(self, message: str, is_error: bool = False):
        """
        Muestra un mensaje de texto en el panel.
        
        Args:
            message: Mensaje a mostrar
            is_error: Si True, usa estilo de error (rojo)
        """
        # Limpiar pixmap
        self.video_display.clear()
        self._last_pixmap = None
        
        # Aplicar estilo según tipo
        if is_error:
            self.video_display.setStyleSheet(self.STYLE_ERROR)
        else:
            self.video_display.setStyleSheet(self.STYLE_NORMAL)
        
        # Mostrar mensaje con word wrap
        self.video_display.setText(message)
    
    def show_connection_error(self, service: str, url_hint: str):
        """
        Muestra un mensaje específico de error de conexión.
        
        Args:
            service: Nombre del servicio (ej: "VisionEdge")
            url_hint: URL real del servicio (desde StreamConfig)
        """
        error_msg = f"❌ Sin conexión con {service}\n\n"
        error_msg += "Verifica que el servidor esté corriendo:\n"
        error_msg += f"• {url_hint}"
        
        self.show_message(error_msg, is_error=True)
    
    def resizeEvent(self, event):
        """Reescala el último frame cuando cambia el tamaño de la ventana."""
        super().resizeEvent(event)
        
        # Si hay un frame guardado, reescalarlo
        if self._last_pixmap and not self._last_pixmap.isNull():
            scaled = self._last_pixmap.scaled(
                self.video_display.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.video_display.setPixmap(scaled)
