import time
import os

import cv2

from app.infrastructure.camera.rtsp_opencv_source import RtspOpenCvSource
from app.infrastructure.config.settings import get_settings


def run_rtsp_test(settings) -> None:
    """HU-VIS-01: Test RTSP frame capture."""
    print("=" * 50)
    print("Vision Edge - RTSP Test Mode (HU-VIS-01)")
    print("=" * 50)
    print(f"RTSP_URL: {settings.rtsp_url}")
    print(f"Reconnect delay: {settings.rtsp_reconnect_sec}s")
    print(f"Max fails before reopen: {settings.rtsp_max_fails_before_reopen}")
    print("=" * 50)

    frame_source = RtspOpenCvSource(
        rtsp_url=settings.rtsp_url,
        reconnect_sec=settings.rtsp_reconnect_sec,
        max_fails_before_reopen=settings.rtsp_max_fails_before_reopen,
        open_timeout_sec=settings.rtsp_open_timeout_sec,
    )

    frames_ok = 0
    frames_fail = 0
    start_time = time.time()
    max_frames = 200

    try:
        for i in range(max_frames):
            frame = frame_source.read()
            if frame is not None:
                frames_ok += 1
            else:
                frames_fail += 1

            if (i + 1) % 50 == 0:
                elapsed = time.time() - start_time
                fps = frames_ok / elapsed if elapsed > 0 else 0
                print(
                    f"[{i+1}/{max_frames}] OK={frames_ok}, FAIL={frames_fail}, FPS={fps:.1f}"
                )

            time.sleep(0.03)  # ~30 FPS target

    except KeyboardInterrupt:
        print("\n[INTERRUPTED] Stopping...")
    finally:
        frame_source.close()
        elapsed = time.time() - start_time
        fps = frames_ok / elapsed if elapsed > 0 else 0
        print("=" * 50)
        print(f"Total frames OK: {frames_ok}")
        print(f"Total frames FAIL: {frames_fail}")
        print(f"Average FPS: {fps:.2f}")
        print(f"Elapsed time: {elapsed:.2f}s")
        print("=" * 50)


def run_detector_test(settings) -> None:
    """HU-VIS-02: Test YOLO detector with RTSP frames."""
    from app.infrastructure.inference.yolo_ultralytics_detector import (
        YoloUltralyticsDetector,
    )

    print("=" * 50)
    print("Vision Edge - Detector Test Mode (HU-VIS-02)")
    print("=" * 50)
    print(f"RTSP_URL: {settings.rtsp_url}")
    print(f"MODEL_PATH: {settings.model_path}")
    print(f"CONF_THRES: {settings.conf_thres}")
    print("=" * 50)

    frame_source = RtspOpenCvSource(
        rtsp_url=settings.rtsp_url,
        reconnect_sec=settings.rtsp_reconnect_sec,
        max_fails_before_reopen=settings.rtsp_max_fails_before_reopen,
        open_timeout_sec=settings.rtsp_open_timeout_sec,
    )

    detector = YoloUltralyticsDetector(
        model_path=settings.model_path, conf_thres=settings.conf_thres
    )

    frames_processed = 0
    total_detections = 0
    start_time = time.time()
    max_frames = 50

    try:
        for i in range(max_frames):
            frame = frame_source.read()
            if frame is None:
                continue

            detections = detector.detect(frame)
            frames_processed += 1
            total_detections += len(detections)

            if (i + 1) % 10 == 0:
                elapsed = time.time() - start_time
                fps = frames_processed / elapsed if elapsed > 0 else 0
                avg_det = total_detections / frames_processed if frames_processed > 0 else 0
                print(
                    f"[{i+1}/{max_frames}] Processed={frames_processed}, "
                    f"Detections={len(detections)}, Avg={avg_det:.1f}, FPS={fps:.1f}"
                )

            time.sleep(0.03)

    except KeyboardInterrupt:
        print("\n[INTERRUPTED] Stopping...")
    finally:
        frame_source.close()
        elapsed = time.time() - start_time
        fps = frames_processed / elapsed if elapsed > 0 else 0
        avg_det = total_detections / frames_processed if frames_processed > 0 else 0
        print("=" * 50)
        print(f"Total frames processed: {frames_processed}")
        print(f"Total detections: {total_detections}")
        print(f"Average detections per frame: {avg_det:.2f}")
        print(f"Average FPS: {fps:.2f}")
        print(f"Elapsed time: {elapsed:.2f}s")
        print("=" * 50)


def run_counter_test(settings) -> None:
    """HU-VIS-03: Test counter with YOLO detector and stabilization."""
    from app.infrastructure.inference.yolo_ultralytics_detector import (
        YoloUltralyticsDetector,
    )
    from app.infrastructure.counting.visible_window_counter import (
        VisibleWindowCounter,
    )

    print("=" * 50)
    print("Vision Edge - Counter Test Mode (HU-VIS-03)")
    print("=" * 50)
    print(f"RTSP_URL: {settings.rtsp_url}")
    print(f"MODEL_PATH: {settings.model_path}")
    print(f"CONF_THRES: {settings.conf_thres}")
    print(f"COUNT_WINDOW: {settings.count_window}")
    print(f"STABLE_MODE: {settings.stable_mode}")
    print("=" * 50)

    frame_source = RtspOpenCvSource(
        rtsp_url=settings.rtsp_url,
        reconnect_sec=settings.rtsp_reconnect_sec,
        max_fails_before_reopen=settings.rtsp_max_fails_before_reopen,
        open_timeout_sec=settings.rtsp_open_timeout_sec,
    )

    detector = YoloUltralyticsDetector(
        model_path=settings.model_path, conf_thres=settings.conf_thres
    )

    counter = VisibleWindowCounter(
        window=settings.count_window, stable_mode=settings.stable_mode
    )

    frames_processed = 0
    start_time = time.time()
    max_frames = 80

    try:
        for i in range(max_frames):
            frame = frame_source.read()
            if frame is None:
                continue

            # Detect objects
            detections = detector.detect(frame)

            # Update counter
            state = counter.update(detections)

            frames_processed += 1

            if (i + 1) % 10 == 0:
                elapsed = time.time() - start_time
                fps = frames_processed / elapsed if elapsed > 0 else 0
                print(
                    f"[{i+1}/{max_frames}] Raw={state.raw_count}, "
                    f"Stable={state.stable_count}, Window={state.window_size}, "
                    f"FPS={fps:.1f}"
                )

            time.sleep(0.03)

    except KeyboardInterrupt:
        print("\n[INTERRUPTED] Stopping...")
    finally:
        frame_source.close()
        elapsed = time.time() - start_time
        fps = frames_processed / elapsed if elapsed > 0 else 0
        print("=" * 50)
        print(f"Total frames processed: {frames_processed}")
        print(f"Average FPS: {fps:.2f}")
        print(f"Elapsed time: {elapsed:.2f}s")
        print("=" * 50)


def run_render_test(settings) -> None:
    """HU-VIS-04: Test renderer with YOLO detector, counter, and overlay."""
    from app.infrastructure.inference.yolo_ultralytics_detector import (
        YoloUltralyticsDetector,
    )
    from app.infrastructure.counting.visible_window_counter import (
        VisibleWindowCounter,
    )
    from app.infrastructure.rendering.supervision_overlay_renderer import (
        SupervisionOverlayRenderer,
    )

    print("=" * 50)
    print("Vision Edge - Render Test Mode (HU-VIS-04)")
    print("=" * 50)
    print(f"RTSP_URL: {settings.rtsp_url}")
    print(f"MODEL_PATH: {settings.model_path}")
    print(f"CONF_THRES: {settings.conf_thres}")
    print(f"COUNT_WINDOW: {settings.count_window}")
    print(f"STABLE_MODE: {settings.stable_mode}")
    print(f"RENDER_SHOW_LABELS: {settings.render_show_labels}")
    print(f"RENDER_SHOW_RAW: {settings.render_show_raw}")
    print("=" * 50)

    # Create outputs directory if not exists
    output_dir = "outputs"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"[OUTPUT] Created directory: {output_dir}")

    frame_source = RtspOpenCvSource(
        rtsp_url=settings.rtsp_url,
        reconnect_sec=settings.rtsp_reconnect_sec,
        max_fails_before_reopen=settings.rtsp_max_fails_before_reopen,
        open_timeout_sec=settings.rtsp_open_timeout_sec,
    )

    detector = YoloUltralyticsDetector(
        model_path=settings.model_path, conf_thres=settings.conf_thres
    )

    counter = VisibleWindowCounter(
        window=settings.count_window, stable_mode=settings.stable_mode
    )

    renderer = SupervisionOverlayRenderer(
        show_labels=settings.render_show_labels,
        show_raw=settings.render_show_raw,
        text_scale=settings.render_text_scale,
        text_thickness=settings.render_text_thickness,
        box_thickness=settings.render_box_thickness,
    )

    frames_processed = 0
    start_time = time.time()
    max_frames = 30
    save_frames = [10, 20, 30]  # Save these frame numbers

    try:
        for i in range(max_frames):
            frame = frame_source.read()
            if frame is None:
                continue

            # Detect objects
            detections = detector.detect(frame)

            # Update counter
            state = counter.update(detections)

            # Render processed frame
            processed = renderer.render(frame, detections, state)

            frames_processed += 1

            # Save specific frames to disk
            if (i + 1) in save_frames:
                raw_path = os.path.join(output_dir, f"raw_{i+1}.jpg")
                processed_path = os.path.join(output_dir, f"processed_{i+1}.jpg")
                
                cv2.imwrite(raw_path, frame)
                cv2.imwrite(processed_path, processed)
                
                print(f"[SAVED] Frame {i+1}: {raw_path} and {processed_path}")

            # Log progress
            if (i + 1) % 10 == 0:
                elapsed = time.time() - start_time
                fps = frames_processed / elapsed if elapsed > 0 else 0
                print(
                    f"[{i+1}/{max_frames}] Raw={state.raw_count}, "
                    f"Stable={state.stable_count}, FPS={fps:.1f}"
                )

            time.sleep(0.03)

    except KeyboardInterrupt:
        print("\n[INTERRUPTED] Stopping...")
    finally:
        frame_source.close()
        elapsed = time.time() - start_time
        fps = frames_processed / elapsed if elapsed > 0 else 0
        print("=" * 50)
        print(f"Total frames processed: {frames_processed}")
        print(f"Average FPS: {fps:.2f}")
        print(f"Elapsed time: {elapsed:.2f}s")
        print(f"Output images saved in: {output_dir}/")
        print("=" * 50)


def run_service(settings) -> None:
    """HU-VIS-05: Run FastAPI HTTP service with background pipeline."""
    import threading
    
    import uvicorn
    
    from app.application.use_cases.run_pipeline import RunPipeline
    from app.infrastructure.camera.rtsp_opencv_source import RtspOpenCvSource
    from app.infrastructure.counting.visible_window_counter import (
        VisibleWindowCounter,
    )
    from app.infrastructure.inference.yolo_ultralytics_detector import (
        YoloUltralyticsDetector,
    )
    from app.infrastructure.rendering.supervision_overlay_renderer import (
        SupervisionOverlayRenderer,
    )
    from app.infrastructure.stores.in_memory_frame_store import InMemoryFrameStore
    from app.infrastructure.stores.in_memory_metrics_store import InMemoryMetricsStore
    from app.infrastructure.tracking.bytetrack_tracker import ByteTrackTracker
    from app.presentation.http.app_factory import create_app
    
    print("=" * 50)
    print("Vision Edge - HTTP Service Mode (HU-VIS-05)")
    print("=" * 50)
    print(f"API Host: {settings.api_host}")
    print(f"API Port: {settings.api_port}")
    print(f"API Version: {settings.api_version}")
    print(f"RTSP URL: {settings.rtsp_url}")
    print(f"Model: {settings.model_path}")
    print(f"Pipeline Sleep: {settings.pipeline_sleep_sec}s (~{1/settings.pipeline_sleep_sec:.0f} FPS)")
    print("=" * 50)
    
    # Initialize stores
    frame_store = InMemoryFrameStore()
    metrics_store = InMemoryMetricsStore()
    
    # Create FastAPI app
    app = create_app(
        service_name="vision_edge",
        version=settings.api_version,
        frame_store=frame_store,
        metrics_store=metrics_store,
    )
    
    # Initialize pipeline components
    frame_source = RtspOpenCvSource(
        rtsp_url=settings.rtsp_url,
        reconnect_sec=settings.rtsp_reconnect_sec,
        max_fails_before_reopen=settings.rtsp_max_fails_before_reopen,
        open_timeout_sec=settings.rtsp_open_timeout_sec,
    )
    
    detector = YoloUltralyticsDetector(
        model_path=settings.model_path,
        conf_thres=settings.conf_thres,
    )
    
    tracker = ByteTrackTracker()
    
    counter = VisibleWindowCounter(
        window=settings.count_window,
        stable_mode=settings.stable_mode,
    )
    
    renderer = SupervisionOverlayRenderer(
        show_labels=settings.render_show_labels,
        show_raw_count=settings.render_show_raw,
        text_scale=settings.render_text_scale,
        text_thickness=settings.render_text_thickness,
        box_thickness=settings.render_box_thickness,
    )
    
    # Create pipeline
    pipeline = RunPipeline(
        frame_source=frame_source,
        detector=detector,
        counter=counter,
        renderer=renderer,
        frame_store=frame_store,
        metrics_store=metrics_store,
        tracker=tracker,
        jpeg_quality=settings.jpeg_quality,
        sleep_sec=settings.pipeline_sleep_sec,
        max_consecutive_fails=settings.pipeline_max_consecutive_fails,
    )
    
    # Start pipeline in background thread
    pipeline_thread = threading.Thread(
        target=pipeline.run_continuous,
        daemon=True,
        name="PipelineThread",
    )
    pipeline_thread.start()
    print("[Service] Pipeline thread started")
    
    # Start FastAPI server (blocking)
    print(f"[Service] Starting FastAPI server on {settings.api_host}:{settings.api_port}")
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        log_level="info",
    )


def main() -> None:
    settings = get_settings()

    if settings.vision_mode == "service":
        run_service(settings)
    elif settings.vision_mode == "detector_test":
        run_detector_test(settings)
    elif settings.vision_mode == "counter_test":
        run_counter_test(settings)
    elif settings.vision_mode == "render_test":
        run_render_test(settings)
    else:
        run_rtsp_test(settings)


if __name__ == "__main__":
    main()
