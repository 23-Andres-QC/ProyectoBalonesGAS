import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
	rtsp_url: str
	rtsp_reconnect_sec: float
	rtsp_max_fails_before_reopen: int
	rtsp_open_timeout_sec: float
	model_path: str
	conf_thres: float
	jpeg_quality: int
	count_window: int
	stable_mode: str
	vision_mode: str


def get_settings() -> Settings:
	return Settings(
		rtsp_url=os.getenv("RTSP_URL", "rtsp://admin:admin@192.168.1.100:554/stream1"),
		rtsp_reconnect_sec=float(os.getenv("RTSP_RECONNECT_SEC", "2.0")),
		rtsp_max_fails_before_reopen=int(os.getenv("RTSP_MAX_FAILS_BEFORE_REOPEN", "10")),
		rtsp_open_timeout_sec=float(os.getenv("RTSP_OPEN_TIMEOUT_SEC", "5.0")),
		model_path=os.getenv("MODEL_PATH", "assets/models/best.pt"),
		conf_thres=float(os.getenv("CONF_THRES", "0.5")),
		jpeg_quality=int(os.getenv("JPEG_QUALITY", "80")),
		count_window=int(os.getenv("COUNT_WINDOW", "15")),
		stable_mode=os.getenv("STABLE_MODE", "median"),
		vision_mode=os.getenv("VISION_MODE", "rtsp_test"),
	)
