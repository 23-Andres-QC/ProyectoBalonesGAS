import time
from dataclasses import dataclass
from datetime import datetime, timezone

import cv2
import numpy as np
import supervision as sv

from app.application.ports.counter import Counter
from app.application.ports.detector import Detector
from app.application.ports.frame_source import FrameSource
from app.application.ports.frame_store import FrameStore
from app.application.ports.metrics_store import MetricsStore
from app.application.ports.renderer import Renderer
from app.application.ports.tracker import Tracker


@dataclass
class RunPipeline:
    """
    Pipeline orchestrator (HU-VIS-05, HU-VIS-06v minimal).
    
    Continuous loop: read → detect → track → count → line_count → render → encode → store.
    Updates frame_store and metrics_store with thread-safe operations.
    """
    frame_source: FrameSource
    detector: Detector
    counter: Counter
    renderer: Renderer
    frame_store: FrameStore
    metrics_store: MetricsStore
    tracker: Tracker | None = None
    jpeg_quality: int = 80
    sleep_sec: float = 0.033  # ~30 FPS
    max_consecutive_fails: int = 50
    # HU-VIS-06v: Line crossing (minimal)
    line_y: int = 450
    line_thickness: int = 2
    line_text_scale: float = 0.6

    def run_continuous(self) -> None:
        """
        Run pipeline loop until interrupted or max consecutive fails.
        
        Updates stores on each successful iteration:
        - frame_store: raw_jpeg, processed_jpeg
        - metrics_store: fps, raw_count, stable_count, line_in, line_out, line_total, status, last_update_utc
        """
        frames_processed = 0
        consecutive_fails = 0
        start_time = time.time()
        
        # HU-VIS-06v: LineZone for crossing detection (minimal inline)
        line_zone: sv.LineZone | None = None
        last_frame_shape = (0, 0)
        
        # Initial status
        self._update_metrics_store(0.0, 0, 0, 0, 0, 0, "starting")
        
        print("[RunPipeline] Starting continuous pipeline...")
        print(f"  Sleep interval: {self.sleep_sec}s (~{1/self.sleep_sec:.1f} FPS target)")
        print(f"  Max consecutive fails: {self.max_consecutive_fails}")
        print("  Press Ctrl+C to stop")
        
        try:
            while True:
                iteration_start = time.time()
                
                # Read frame
                frame = self.frame_source.read()
                if frame is None:
                    consecutive_fails += 1
                    if consecutive_fails >= self.max_consecutive_fails:
                        print(f"[RunPipeline] Max consecutive fails reached ({self.max_consecutive_fails})")
                        self._update_metrics_store(0.0, 0, 0, 0, 0, 0, "offline")
                        break
                    time.sleep(self.sleep_sec)
                    continue
                
                consecutive_fails = 0  # Reset on success
                
                # Initialize/reinitialize LineZone if frame size changed (HU-VIS-06v)
                frame_h, frame_w = frame.shape[:2]
                if (frame_w, frame_h) != last_frame_shape:
                    line_y_clamped = max(0, min(self.line_y, frame_h - 1))
                    line_zone = sv.LineZone(
                        start=sv.Point(x=0, y=line_y_clamped),
                        end=sv.Point(x=frame_w - 1, y=line_y_clamped),
                        triggering_anchors=(sv.Position.CENTER,)
                    )
                    last_frame_shape = (frame_w, frame_h)
                
                # Detect
                detections = self.detector.detect(frame)
                
                # Track (optional) - skip if tracker raises NotImplementedError
                if self.tracker:
                    try:
                        detections = self.tracker.update(detections)
                    except NotImplementedError:
                        pass  # Tracker not implemented yet, use raw detections
                
                # Count (stable by presence)
                count_state = self.counter.update(detections)
                
                # Line crossing count (HU-VIS-06v minimal)
                line_in = 0
                line_out = 0
                line_total = 0
                if line_zone is not None:
                    # Check if detections have tracker_id (required for LineZone)
                    if hasattr(detections, 'tracker_id') and detections.tracker_id is not None:
                        # Trigger crossing detection
                        line_zone.trigger(detections)
                        # Read accumulated counts from LineZone
                        line_in = line_zone.in_count
                        line_out = line_zone.out_count
                        line_total = line_in + line_out
                
                # Render (pass line info for overlay)
                line_info = {
                    "line_y": self.line_y,
                    "line_in": line_in,
                    "line_out": line_out,
                    "line_total": line_total,
                    "line_thickness": self.line_thickness,
                    "line_text_scale": self.line_text_scale,
                }
                processed_frame = self.renderer.render(
                    frame, detections, count_state, line_info
                )
                
                # Encode both frames to JPEG
                raw_jpeg = self._encode_jpeg(frame)
                processed_jpeg = self._encode_jpeg(processed_frame)
                
                # Store frames
                self.frame_store.set_frames(raw_jpeg, processed_jpeg)
                
                # Calculate FPS
                frames_processed += 1
                elapsed = time.time() - start_time
                fps = frames_processed / elapsed if elapsed > 0 else 0.0
                
                # Store metrics
                self._update_metrics_store(
                    fps=fps,
                    raw_count=count_state.raw_count,
                    stable_count=count_state.stable_count,
                    line_in=line_in,
                    line_out=line_out,
                    line_total=line_total,
                    status="ok"
                )
                
                # Log progress periodically
                if frames_processed % 30 == 0:
                    print(f"[RunPipeline] Processed: {frames_processed}, FPS: {fps:.1f}, "
                          f"Raw: {count_state.raw_count}, Stable: {count_state.stable_count}, "
                          f"LineTotal: {line_total} (in={line_in} out={line_out})")
                
                # Sleep to maintain target FPS
                iteration_time = time.time() - iteration_start
                sleep_time = max(0, self.sleep_sec - iteration_time)
                time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            print("\n[RunPipeline] Interrupted by user")
        finally:
            elapsed = time.time() - start_time
            final_fps = frames_processed / elapsed if elapsed > 0 else 0.0
            print(f"[RunPipeline] Stopped. Total frames: {frames_processed}, "
                  f"Avg FPS: {final_fps:.2f}, Elapsed: {elapsed:.1f}s")
            self.frame_source.close()

    def _encode_jpeg(self, frame: np.ndarray) -> bytes:
        """Encode BGR frame to JPEG bytes."""
        success, buffer = cv2.imencode(
            ".jpg",
            frame,
            [cv2.IMWRITE_JPEG_QUALITY, self.jpeg_quality]
        )
        if not success:
            raise RuntimeError("Failed to encode frame to JPEG")
        return buffer.tobytes()

    def _update_metrics_store(
        self,
        fps: float,
        raw_count: int,
        stable_count: int,
        line_in: int,
        line_out: int,
        line_total: int,
        status: str
    ) -> None:
        """Update metrics store with current values (HU-VIS-05, HU-VIS-06)."""
        now = datetime.now(timezone.utc)
        last_update_utc = now.isoformat().replace("+00:00", "Z")
        
        metrics = {
            "fps": fps,
            "raw_count": raw_count,
            "stable_count": stable_count,
            "line_in": line_in,
            "line_out": line_out,
            "line_total": line_total,
            "status": status,
            "last_update_utc": last_update_utc,
        }
        self.metrics_store.set_metrics(metrics)
