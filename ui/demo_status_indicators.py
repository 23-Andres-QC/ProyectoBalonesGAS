#!/usr/bin/env python3
"""
Demo visual de los indicadores de estado de conexión.

Muestra cómo se ven los mensajes de error cuando:
1. VisionEdge está offline
2. Backend API está offline
3. Todo está conectado correctamente
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout
from PyQt5.QtCore import QTimer

# Add parent directory to path
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyqt_app.presentation.widgets.video_panel import VideoPanel
from pyqt_app.presentation.widgets.counter_panel import CounterPanel


class DemoWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Demo de Indicadores de Estado")
        self.resize(800, 700)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        
        # Buttons para simular estados
        buttons_layout = QHBoxLayout()
        
        btn_vision_error = QPushButton("❌ Simular Error VisionEdge")
        btn_vision_error.clicked.connect(self.show_vision_error)
        buttons_layout.addWidget(btn_vision_error)
        
        btn_backend_error = QPushButton("❌ Simular Error Backend")
        btn_backend_error.clicked.connect(self.show_backend_error)
        buttons_layout.addWidget(btn_backend_error)
        
        btn_connected = QPushButton("✅ Simular Todo Conectado")
        btn_connected.clicked.connect(self.show_connected)
        buttons_layout.addWidget(btn_connected)
        
        btn_connecting = QPushButton("🔄 Simular Conectando")
        btn_connecting.clicked.connect(self.show_connecting)
        buttons_layout.addWidget(btn_connecting)
        
        main_layout.addLayout(buttons_layout)
        
        # Video panel
        self.video_panel = VideoPanel("Vista de Cámara (DEMO)")
        main_layout.addWidget(self.video_panel)
        
        # Counter panel
        self.counter_panel = CounterPanel()
        main_layout.addWidget(self.counter_panel)
        
        # Estado inicial
        self.show_connecting()
    
    def show_vision_error(self):
        """Simula error de VisionEdge"""
        self.video_panel.show_connection_error("VisionEdge")
        print("📺 Mostrando error de VisionEdge")
    
    def show_backend_error(self):
        """Simula error de Backend API"""
        self.counter_panel.show_connection_status(False)
        print("📊 Mostrando error de Backend API")
    
    def show_connected(self):
        """Simula estado conectado"""
        self.video_panel.show_message("✅ Conectado - Mostrando video...", is_error=False)
        self.counter_panel.show_connection_status(True)
        self.counter_panel.update_count(42)
        print("✅ Mostrando estado conectado")
    
    def show_connecting(self):
        """Simula estado conectando"""
        self.video_panel.show_message("🔄 Conectando a VisionEdge...", is_error=False)
        self.counter_panel.show_connection_status(True)
        self.counter_panel.update_count(0)
        print("🔄 Mostrando estado conectando")


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = DemoWindow()
    window.show()
    
    print("\n" + "="*60)
    print("DEMO DE INDICADORES DE ESTADO")
    print("="*60)
    print("\nUsa los botones para simular diferentes estados:")
    print("  ❌ Error VisionEdge  - Muestra panel rojo con mensaje")
    print("  ❌ Error Backend     - Muestra indicador rojo en contador")
    print("  ✅ Todo Conectado    - Muestra estado normal")
    print("  🔄 Conectando        - Muestra mensaje de conexión")
    print("\n" + "="*60 + "\n")
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
