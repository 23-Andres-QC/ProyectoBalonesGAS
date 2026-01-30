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
	render_show_labels: bool
	render_show_raw: bool
	render_text_scale: float
	render_text_thickness: int
	render_box_thickness: int
	vision_mode: str
	# HU-VIS-05: HTTP Service
	api_host: str
	api_port: int
	api_version: str
	pipeline_sleep_sec: float
	pipeline_max_consecutive_fails: int


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
		render_show_labels=os.getenv("RENDER_SHOW_LABELS", "1") == "1",
		render_show_raw=os.getenv("RENDER_SHOW_RAW", "0") == "1",
		render_text_scale=float(os.getenv("RENDER_TEXT_SCALE", "1.0")),
		render_text_thickness=int(os.getenv("RENDER_TEXT_THICKNESS", "2")),
		render_box_thickness=int(os.getenv("RENDER_BOX_THICKNESS", "2")),
		vision_mode=os.getenv("VISION_MODE", "rtsp_test"),
		# HU-VIS-05: HTTP Service
		api_host=os.getenv("API_HOST", "127.0.0.1"),
		api_port=int(os.getenv("API_PORT", "8010")),
		api_version=os.getenv("API_VERSION", "0.1.0"),
		pipeline_sleep_sec=float(os.getenv("PIPELINE_SLEEP_SEC", "0.033")),  # ~30 FPS
		pipeline_max_consecutive_fails=int(os.getenv("PIPELINE_MAX_CONSECUTIVE_FAILS", "50")),
	)
