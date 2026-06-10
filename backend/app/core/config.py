from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = Field(default="local", alias="APP_ENV")
    database_url: str = Field(
        default="sqlite:///./education_service.db",
        alias="DATABASE_URL",
    )
    dify_api_base_url: str = Field(default="http://127.0.0.1:5001", alias="DIFY_API_BASE_URL")
    dify_api_key: str = Field(default="", alias="DIFY_API_KEY")
    dify_mock_enabled: bool = Field(default=True, alias="DIFY_MOCK_ENABLED")
    ai_tools_secret: str = Field(default="", alias="AI_TOOLS_SECRET")
    report_export_dir: str = Field(default="storage/reports", alias="REPORT_EXPORT_DIR")
    report_pdf_converter_path: str = Field(default="", alias="REPORT_PDF_CONVERTER_PATH")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        populate_by_name=True,
        extra="ignore",
    )

    @property
    def export_dir_path(self) -> Path:
        return Path(self.report_export_dir)


@lru_cache
def get_settings() -> Settings:
    return Settings()
