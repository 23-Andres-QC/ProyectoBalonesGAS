import sys
import os

# Adapt sys.path to include the specific app directory so imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
# Add pyqt_app directory to path so 'presentation' etc are importable as top-level if needed,
# or to support absolute imports within the submodules if they are not using relative.
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Also add parent (ui) to path to allow "import pyqt_app" if needed
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from PyQt5.QtWidgets import QApplication

from pyqt_app.presentation.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    # Optional: Set global styles or themes here
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
