from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage

class VideoPanel(QWidget):
    def __init__(self, title: str = "Video"):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        self.label_title = QLabel(title)
        self.label_title.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label_title)
        
        self.video_display = QLabel("Waiting for video...")
        self.video_display.setAlignment(Qt.AlignCenter)
        self.video_display.setStyleSheet("background-color: black; color: white; min-height: 480px;")
        self.layout.addWidget(self.video_display)

    def update_image(self, pixmap: QPixmap):
        if not pixmap.isNull():
            scaled = pixmap.scaled(self.video_display.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.video_display.setPixmap(scaled)
