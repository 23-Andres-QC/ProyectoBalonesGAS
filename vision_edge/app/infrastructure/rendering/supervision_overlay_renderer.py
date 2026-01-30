from typing import Any

import cv2
import numpy as np
import supervision as sv

from app.application.ports.renderer import Renderer
from app.domain.entities.count_state import CountState


class SupervisionOverlayRenderer(Renderer):
    """
    Renderer implementation using supervision library (HU-VIS-04, HU-VIS-06).
    
    Annotates frames with:
    - Bounding boxes (sv.BoxAnnotator)
    - Labels (sv.LabelAnnotator, optional)
    - Count text (cv2.putText)
    - Line crossing line (HU-VIS-06)
    """

    def __init__(
        self,
        show_labels: bool = True,
        show_raw: bool = False,
        text_scale: float = 1.0,
        text_thickness: int = 2,
        box_thickness: int = 2,
        line_y: int | None = None,
        line_thickness: int = 2,
        line_text_scale: float = 0.6,
    ) -> None:
        """
        Initialize renderer with configuration.
        
        Args:
            show_labels: Show class labels on boxes
            show_raw: Show raw_count in addition to stable_count
            text_scale: Scale for count text
            text_thickness: Thickness for count text
            box_thickness: Thickness for bounding boxes
            line_y: Y position for line crossing line (HU-VIS-06)
            line_thickness: Thickness for line crossing line
            line_text_scale: Scale for line crossing text
        """
        self._show_labels = show_labels
        self._show_raw = show_raw
        self._text_scale = text_scale
        self._text_thickness = text_thickness
        self._line_y = line_y
        self._line_thickness = line_thickness
        self._line_text_scale = line_text_scale
        
        # Initialize supervision annotators
        self._box_annotator = sv.BoxAnnotator(thickness=box_thickness)
        self._label_annotator = sv.LabelAnnotator(
            text_scale=0.5,
            text_thickness=1,
        ) if show_labels else None

    def render(
        self,
        frame: np.ndarray,
        detections: Any,
        count_state: CountState,
        line_info: dict | None = None,
    ) -> np.ndarray:
        """
        Render detections, counts, and line on frame (HU-VIS-04, HU-VIS-06v).
        
        Args:
            frame: BGR frame (numpy array)
            detections: sv.Detections object
            count_state: CountState with raw_count and stable_count
            line_info: Dict with line_y, line_in, line_out, line_total, line_thickness, line_text_scale
        
        Returns:
            Processed frame with annotations (BGR numpy array).
        """
        # Create copy to avoid modifying original
        processed = frame.copy()
        
        # Draw line crossing line first (behind detections) - HU-VIS-06v
        if line_info is not None:
            processed = self._draw_line_crossing(processed, line_info)
        
        # Annotate detections if present
        if detections is not None and len(detections) > 0:
            # Draw bounding boxes
            processed = self._box_annotator.annotate(
                scene=processed,
                detections=detections,
            )
            
            # Draw labels if enabled
            if self._label_annotator is not None:
                labels = [f"obj_{i}" for i in range(len(detections))]
                processed = self._label_annotator.annotate(
                    scene=processed,
                    detections=detections,
                    labels=labels,
                )
        
        # Draw count text
        processed = self._draw_count_text(processed, count_state, line_info)
        
        return processed

    def _draw_count_text(
        self,
        frame: np.ndarray,
        count_state: CountState,
        line_info: dict | None = None,
    ) -> np.ndarray:
        """
        Draw count information on frame (HU-VIS-04, HU-VIS-06v).
        
        Args:
            frame: Frame to annotate
            count_state: Count state with raw and stable counts
            line_info: Line crossing info with line_in, line_out, line_total, line_text_scale
        
        Returns:
            Frame with count text.
        """
        h, w = frame.shape[:2]
        
        # Stable count (always shown)
        stable_text = f"Stable: {count_state.stable_count}"
        stable_pos = (20, 50)
        
        # Draw text with background for better visibility
        self._draw_text_with_background(
            frame,
            stable_text,
            stable_pos,
            scale=self._text_scale * 1.2,
            thickness=self._text_thickness + 1,
            color=(0, 255, 0),  # Green
        )
        
        # Line crossing count (HU-VIS-06v)
        if line_info is not None:
            line_text = f"Line: {line_info['line_total']} (in:{line_info['line_in']} out:{line_info['line_out']})"
            line_pos = (20, 100)
            text_scale = line_info.get('line_text_scale', self._line_text_scale)
            self._draw_text_with_background(
                frame,
                line_text,
                line_pos,
                scale=text_scale,
                thickness=self._text_thickness,
                color=(255, 165, 0),  # Orange
            )
        
        # Raw count (optional, moved down if line shown)
        if self._show_raw:
            raw_text = f"Raw: {count_state.raw_count}"
            raw_y = 150 if line_info is not None else 100
            raw_pos = (20, raw_y)
            self._draw_text_with_background(
                frame,
                raw_text,
                raw_pos,
                scale=self._text_scale * 0.8,
                thickness=self._text_thickness,
                color=(255, 255, 0),  # Cyan
            )
        
        return frame

    def _draw_line_crossing(
        self,
        frame: np.ndarray,
        line_info: dict,
    ) -> np.ndarray:
        """
        Draw line crossing line (HU-VIS-06v).
        
        Args:
            frame: Frame to annotate
            line_info: Dict with line_y, line_thickness, line_in, line_out, line_total
        
        Returns:
            Frame with line drawn.
        """
        h, w = frame.shape[:2]
        line_y = line_info.get('line_y', self._line_y or 0)
        line_y = min(max(0, line_y), h - 1)  # Clamp to frame bounds
        thickness = line_info.get('line_thickness', self._line_thickness)
        
        # Draw horizontal line
        cv2.line(
            frame,
            (0, line_y),
            (w - 1, line_y),
            (0, 255, 255),  # Yellow
            thickness,
            cv2.LINE_AA,
        )
        
        # Draw small text labels on the line
        in_text = f"IN: {line_counts['line_in']}"
        out_text = f"OUT: {line_counts['line_out']}"
        
        # Left side: IN count
        cv2.putText(
            frame,
            in_text,
            (w - 200, line_y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            self._line_text_scale * 0.8,
            (0, 255, 255),  # Yellow
            self._text_thickness - 1,
            cv2.LINE_AA,
        )
        
        # Right side: OUT count
        cv2.putText(
            frame,
            out_text,
            (w - 100, line_y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            self._line_text_scale * 0.8,
            (0, 255, 255),  # Yellow
            self._text_thickness - 1,
            cv2.LINE_AA,
        )
        
        return frame

    def _draw_text_with_background(
        self,
        frame: np.ndarray,
        text: str,
        position: tuple[int, int],
        scale: float,
        thickness: int,
        color: tuple[int, int, int],
    ) -> None:
        """
        Draw text with semi-transparent background.
        
        Args:
            frame: Frame to draw on
            text: Text to draw
            position: (x, y) position
            scale: Text scale
            thickness: Text thickness
            color: Text color (BGR)
        """
        font = cv2.FONT_HERSHEY_SIMPLEX
        
        # Get text size
        (text_w, text_h), baseline = cv2.getTextSize(
            text, font, scale, thickness
        )
        
        x, y = position
        
        # Draw background rectangle
        cv2.rectangle(
            frame,
            (x - 5, y - text_h - 5),
            (x + text_w + 5, y + baseline + 5),
            (0, 0, 0),  # Black background
            -1,  # Filled
        )
        
        # Draw text
        cv2.putText(
            frame,
            text,
            (x, y),
            font,
            scale,
            color,
            thickness,
            cv2.LINE_AA,
        )
