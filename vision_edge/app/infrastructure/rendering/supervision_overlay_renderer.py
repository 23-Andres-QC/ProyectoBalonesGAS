from typing import Any

import cv2
import numpy as np
import supervision as sv

from app.application.ports.renderer import Renderer
from app.domain.entities.count_state import CountState


class SupervisionOverlayRenderer(Renderer):
    """
    Renderer implementation using supervision library.
    
    Annotates frames with:
    - Bounding boxes (sv.BoxAnnotator)
    - Labels (sv.LabelAnnotator, optional)
    - Count text (cv2.putText)
    """

    def __init__(
        self,
        show_labels: bool = True,
        show_raw: bool = False,
        text_scale: float = 1.0,
        text_thickness: int = 2,
        box_thickness: int = 2,
    ) -> None:
        """
        Initialize renderer with configuration.
        
        Args:
            show_labels: Show class labels on boxes
            show_raw: Show raw_count in addition to stable_count
            text_scale: Scale for count text
            text_thickness: Thickness for count text
            box_thickness: Thickness for bounding boxes
        """
        self._show_labels = show_labels
        self._show_raw = show_raw
        self._text_scale = text_scale
        self._text_thickness = text_thickness
        
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
    ) -> np.ndarray:
        """
        Render detections and count on frame.
        
        Args:
            frame: BGR frame (numpy array)
            detections: sv.Detections object
            count_state: CountState with raw_count and stable_count
        
        Returns:
            Processed frame with annotations (BGR numpy array).
        """
        # Create copy to avoid modifying original
        processed = frame.copy()
        
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
        processed = self._draw_count_text(processed, count_state)
        
        return processed

    def _draw_count_text(
        self,
        frame: np.ndarray,
        count_state: CountState,
    ) -> np.ndarray:
        """
        Draw count information on frame.
        
        Args:
            frame: Frame to annotate
            count_state: Count state with raw and stable counts
        
        Returns:
            Frame with count text.
        """
        h, w = frame.shape[:2]
        
        # Stable count (always shown)
        stable_text = f"Count: {count_state.stable_count}"
        stable_pos = (20, 50)
        
        # Draw text with background for better visibility
        self._draw_text_with_background(
            frame,
            stable_text,
            stable_pos,
            scale=self._text_scale * 1.5,
            thickness=self._text_thickness + 1,
            color=(0, 255, 0),  # Green
        )
        
        # Raw count (optional)
        if self._show_raw:
            raw_text = f"Raw: {count_state.raw_count}"
            raw_pos = (20, 100)
            self._draw_text_with_background(
                frame,
                raw_text,
                raw_pos,
                scale=self._text_scale,
                thickness=self._text_thickness,
                color=(255, 255, 0),  # Cyan
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
