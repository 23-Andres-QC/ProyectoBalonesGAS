import time

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


def main() -> None:
    settings = get_settings()

    if settings.vision_mode == "detector_test":
        run_detector_test(settings)
    else:
        run_rtsp_test(settings)


if __name__ == "__main__":
    main()
