"""Управление конфигурацией."""

__author__ = "aa.blinov"

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки."""

    model_config = SettingsConfigDict(
        env_file="service.env",
        env_file_encoding="utf-8"
    )

    API_TITLE: str
    API_DESCRIPTION: str
    API_VERSION: str

    DEBUG: bool


settings = Settings()
