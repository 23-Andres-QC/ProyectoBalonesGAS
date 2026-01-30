import time

from app.infrastructure.camera.rtsp_opencv_source import RtspOpenCvSource
from app.infrastructure.config.settings import get_settings


def main() -> None:
    settings = get_settings()
    print("=" * 50)
    print("Vision Edge - RTSP Test Mode")
    print("=" * 50)
    print(f"RTSP_URL: {settings.rtsp_url}")
    print(f"Reconnect delay: {settings.rtsp_reconnect_sec}s")
    print(f"Max fails before reopen: {settings.rtsp_max_fails_before_reopen}")
    print("=" * 50)

    source = RtspOpenCvSource(
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
            frame = source.read()
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
        source.close()
        elapsed = time.time() - start_time
        fps = frames_ok / elapsed if elapsed > 0 else 0
        print("=" * 50)
        print(f"Total frames OK: {frames_ok}")
        print(f"Total frames FAIL: {frames_fail}")
        print(f"Average FPS: {fps:.2f}")
        print(f"Elapsed time: {elapsed:.2f}s")
        print("=" * 50)


if __name__ == "__main__":
    main()
