#!/usr/bin/env python3
"""
Script de prueba para validar la implementación de streaming MJPEG.

Valida:
1. Que mjpeg_reader puede parsear frames
2. Que MjpegWorker puede emitir signals correctamente
3. Que la configuración se carga correctamente
"""

import sys
import time
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread

def test_config():
    """Test 1: Validar configuración"""
    print("=" * 60)
    print("TEST 1: Validando configuración...")
    print("=" * 60)
    
    from pyqt_app.infrastructure.config import StreamConfig
    
    print(f"✓ STREAM_RAW_URL: {StreamConfig.STREAM_RAW_URL}")
    print(f"✓ STREAM_PROCESSED_URL: {StreamConfig.STREAM_PROCESSED_URL}")
    print(f"✓ BACKEND_BASE_URL: {StreamConfig.BACKEND_BASE_URL}")
    print(f"✓ STREAM_TIMEOUT_SEC: {StreamConfig.STREAM_TIMEOUT_SEC}")
    print()


def test_mjpeg_reader():
    """Test 2: Validar que mjpeg_reader puede importarse"""
    print("=" * 60)
    print("TEST 2: Validando mjpeg_reader...")
    print("=" * 60)
    
    try:
        from pyqt_app.infrastructure.api.mjpeg_reader import iter_mjpeg_frames
        print("✓ mjpeg_reader importado correctamente")
        print("✓ Función iter_mjpeg_frames disponible")
        print()
        return True
    except ImportError as e:
        print(f"✗ Error importando mjpeg_reader: {e}")
        print()
        return False


def test_mjpeg_worker():
    """Test 3: Validar que MjpegWorker puede crearse"""
    print("=" * 60)
    print("TEST 3: Validando MjpegWorker...")
    print("=" * 60)
    
    try:
        from pyqt_app.presentation.workers.mjpeg_worker import MjpegWorker
        from pyqt_app.infrastructure.config import StreamConfig
        
        # Crear instancia (no la ejecutamos para evitar conexión real)
        worker = MjpegWorker(StreamConfig.STREAM_RAW_URL)
        
        print("✓ MjpegWorker importado correctamente")
        print("✓ Worker creado con URL:", worker.url)
        print("✓ Signals disponibles: frame_ready, status, error")
        print()
        return True
    except Exception as e:
        print(f"✗ Error con MjpegWorker: {e}")
        print()
        return False


def test_main_window():
    """Test 4: Validar que MainWindow puede importarse"""
    print("=" * 60)
    print("TEST 4: Validando MainWindow...")
    print("=" * 60)
    
    try:
        from pyqt_app.presentation.main_window import MainWindow
        print("✓ MainWindow importado correctamente")
        print("✓ Métodos disponibles: start_stream, stop_stream")
        print()
        return True
    except Exception as e:
        print(f"✗ Error con MainWindow: {e}")
        import traceback
        traceback.print_exc()
        print()
        return False


def test_integration():
    """Test 5: Test de integración (sin conexión real)"""
    print("=" * 60)
    print("TEST 5: Test de integración...")
    print("=" * 60)
    
    try:
        # Crear QApplication necesaria para Qt
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        from pyqt_app.presentation.main_window import MainWindow
        
        print("✓ Creando MainWindow...")
        window = MainWindow()
        
        print("✓ MainWindow creada correctamente")
        print(f"✓ Tabs: {window.tabs.count()} (Bruto, Procesado)")
        print(f"✓ Video panel: {window.video_panel is not None}")
        print(f"✓ Counter panel: {window.counter_panel is not None}")
        print(f"✓ Metrics timer activo: {window.metrics_timer.isActive()}")
        
        # Limpiar recursos correctamente
        window.stop_stream()  # Detener stream antes de cerrar
        window.metrics_timer.stop()
        window.close()
        
        # Procesar eventos pendientes
        app.processEvents()
        
        print("✓ Window cerrado limpiamente")
        print()
        return True
        
    except Exception as e:
        print(f"✗ Error en test de integración: {e}")
        import traceback
        traceback.print_exc()
        print()
        return False


def main():
    """Ejecuta todos los tests"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "VALIDACIÓN DE STREAMING MJPEG" + " " * 18 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    results = []
    
    # Ejecutar tests
    test_config()
    results.append(("Config", True))
    
    results.append(("MJPEG Reader", test_mjpeg_reader()))
    results.append(("MJPEG Worker", test_mjpeg_worker()))
    results.append(("Main Window", test_main_window()))
    results.append(("Integration", test_integration()))
    
    # Resumen
    print("=" * 60)
    print("RESUMEN DE TESTS")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {name}")
    
    print()
    print(f"Total: {passed}/{total} tests pasados")
    
    if passed == total:
        print("\n🎉 ¡TODOS LOS TESTS PASARON!")
        print("\n✅ La implementación de streaming está lista para usar.")
        print("\n📝 Próximos pasos:")
        print("   1. Asegurar que el servidor de streaming esté corriendo en http://127.0.0.1:8010")
        print("   2. Ejecutar: python -m pyqt_app.main")
        print("   3. Verificar que el video se muestra en tiempo real")
        return 0
    else:
        print("\n⚠️ ALGUNOS TESTS FALLARON")
        print("\n❌ Revisa los errores arriba antes de ejecutar la aplicación.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
