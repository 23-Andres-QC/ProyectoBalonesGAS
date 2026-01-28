from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
	APP_NAME: str = "alpha-gas-counter"
	APP_VERSION: str = "0.1.0"
	HOST: str = "0.0.0.0"
	PORT: int = 8000

	model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
	return Settings()
