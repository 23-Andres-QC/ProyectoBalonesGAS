from PyQt5.QtGui import QPixmap
from pyqt_app.application.ports.backend_client import BackendClient

class RefreshFrames:
    def __init__(self, backend_client: BackendClient):
        self.backend_client = backend_client

    def execute(self, mode: str) -> QPixmap:
        """
        Fetches the frame based on mode ('raw' or 'processed') and returns a QPixmap.
        """
        if mode == 'raw':
            data = self.backend_client.get_raw_frame()
        else:
            data = self.backend_client.get_processed_frame()
            
        if data:
            pixmap = QPixmap()
            pixmap.loadFromData(data)
            return pixmap
        return QPixmap()
