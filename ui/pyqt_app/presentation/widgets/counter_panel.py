from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QFrame
from PyQt5.QtCore import Qt

class CounterPanel(QWidget):
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
        
        self.label_title = QLabel("Conteo de Balones")
        self.label_title.setAlignment(Qt.AlignCenter)
        self.label_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        frame_layout.addWidget(self.label_title)
        
        self.counter_label = QLabel("0")
        self.counter_label.setAlignment(Qt.AlignCenter)
        self.counter_label.setStyleSheet("font-size: 48px; font-weight: bold; color: #0078d7;")
        frame_layout.addWidget(self.counter_label)
        
        self.layout.addWidget(self.frame)

    def update_count(self, count: int):
        self.counter_label.setText(str(count))
