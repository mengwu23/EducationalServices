from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = Field(default="local", alias="APP_ENV")
    database_url: str = Field(
        default="mysql+pymysql://root:123456@localhost:3306/education_service_ai",
        alias="DATABASE_URL",
    )

    dify_api_base_url: str = Field(default="http://localhost/v1", alias="DIFY_API_BASE_URL")
    dify_api_key: str = Field(default="", alias="DIFY_API_KEY")
    dify_cj_api_key: str = Field(default="", alias="DIFY_CJ_API_KEY")
    dify_service_agent_api_key: str = Field(default="", alias="DIFY_SERVICE_AGENT_API_KEY")
    dify_mock_enabled: bool = Field(default=True, alias="DIFY_MOCK_ENABLED")
    dify_onboarding_api_base_url: str = Field(default="http://localhost/v1", alias="DIFY_ONBOARDING_API_BASE_URL")
    dify_onboarding_api_key: str = Field(default="", alias="DIFY_ONBOARDING_API_KEY")
    report_export_dir: str = Field(default="storage/reports", alias="REPORT_EXPORT_DIR")
    report_pdf_converter_path: str = Field(default="", alias="REPORT_PDF_CONVERTER_PATH")

    # 学生助手 — Dify + DeepSeek
    dify_api_url: str = Field(default="http://localhost/v1/chat-messages", alias="DIFY_API_URL")
    dify_life_key: str = Field(default="", alias="DIFY_LIFE_KEY")
    dify_policy_key: str = Field(default="", alias="DIFY_POLICY_KEY")
    deepseek_api_url: str = Field(default="https://api.deepseek.com/chat/completions", alias="DEEPSEEK_API_URL")
    deepseek_api_key: str = Field(default="", alias="DEEPSEEK_API_KEY")

    # NL2SQL — LLM 配置
    nl2sql_llm_api_key: str = Field(default="", alias="NL2SQL_LLM_API_KEY")
    nl2sql_llm_base_url: str = Field(default="https://api.deepseek.com", alias="NL2SQL_LLM_BASE_URL")
    nl2sql_llm_model: str = Field(default="deepseek-chat", alias="NL2SQL_LLM_MODEL")

    # DeepSeek 基础 URL（企业业务办理用）
    deepseek_base_url: str = Field(default="https://api.deepseek.com", alias="DEEPSEEK_BASE_URL")

    # AI Tools 密钥
    ai_tools_secret: str = Field(default="", alias="AI_TOOLS_SECRET")

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parent.parent.parent / ".env"),
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
