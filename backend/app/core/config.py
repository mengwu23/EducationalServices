from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# 项目根目录：backend/ 的父目录（即 EducationalServices/）
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent

class Settings(BaseSettings):
    app_env: str = Field(default="local", alias="APP_ENV")
    dify_api_base_url: str = Field(default="http://127.0.0.1:5001", alias="DIFY_API_BASE_URL")
    dify_api_key: str = Field(default="", alias="DIFY_API_KEY")
    dify_mock_enabled: bool = Field(default=True, alias="DIFY_MOCK_ENABLED")
    dify_onboarding_api_base_url: str = Field(default="http://localhost/v1", alias="DIFY_ONBOARDING_API_BASE_URL")
    dify_onboarding_api_key: str = Field(default="app-3YDkdTb9x8Ot1X5jzhLK4nCN", alias="DIFY_ONBOARDING_API_KEY")
    deepseek_api_key: str = Field(default="", alias="DEEPSEEK_API_KEY")
    deepseek_base_url: str = Field(default="https://api.deepseek.com", alias="DEEPSEEK_BASE_URL")
    deepseek_model: str = Field(default="deepseek-chat", alias="DEEPSEEK_MODEL")
    report_export_dir: str = Field(default="storage/reports", alias="REPORT_EXPORT_DIR")
    report_pdf_converter_path: str = Field(default="", alias="REPORT_PDF_CONVERTER_PATH")

    model_config = SettingsConfigDict(
        env_file=[
            str(_PROJECT_ROOT / ".env"),          # 项目根目录 EducationalServices/.env
            str(_PROJECT_ROOT / "backend" / ".env"),  # backend/.env
            ".env",                                  # 兜底：当前目录
        ],
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
