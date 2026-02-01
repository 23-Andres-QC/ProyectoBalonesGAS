import time

import cv2
import numpy as np

from app.application.ports.frame_source import FrameSource


class RtspOpenCvSource(FrameSource):
    def __init__(
        self,
        rtsp_url: str,
        reconnect_sec: float = 2.0,
        max_fails_before_reopen: int = 10,
        open_timeout_sec: float = 5.0,
    ) -> None:
        self._rtsp_url = rtsp_url
        self._reconnect_sec = reconnect_sec
        self._max_fails = max_fails_before_reopen
        self._open_timeout_sec = open_timeout_sec
        self._cap: cv2.VideoCapture | None = None
        self._fail_count = 0
        self._is_closed = False
        self._open()

    def _open(self) -> None:
        """Open RTSP stream."""
        if self._is_closed:
            return
        try:
            self._cap = cv2.VideoCapture(self._rtsp_url)
            if self._cap.isOpened():
                print(f"[RTSP] Connected: {self._rtsp_url}")
                self._fail_count = 0
            else:
                print(f"[RTSP] Failed to open: {self._rtsp_url}")
                self._cap = None
        except Exception as e:
            print(f"[RTSP] Error opening stream: {e}")
            self._cap = None

    def _close(self) -> None:
        """Close RTSP stream."""
        if self._cap is not None:
            self._cap.release()
            self._cap = None

    def read(self) -> np.ndarray | None:
        """Read next frame with auto-reconnect on failures."""
        if self._is_closed or self._cap is None:
            return None

        ret, frame = self._cap.read()
        if ret and frame is not None:
            self._fail_count = 0
            return frame

        # Frame read failed
        self._fail_count += 1
        if self._fail_count >= self._max_fails:
            print(f"[RTSP] Offline (fails={self._fail_count}), reconnecting...")
            self._close()
            time.sleep(self._reconnect_sec)
            self._open()
            self._fail_count = 0

        return None

    def close(self) -> None:
        """Release resources."""
        self._is_closed = True
        self._close()
        print("[RTSP] Closed")
