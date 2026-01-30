import sys
import os

# Ensure the current directory to sys.path so 'pyqt_app' is found
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from pyqt_app.main import main

if __name__ == "__main__":
    main()
