from functools import lru_cache
from pathlib import Path

from pydantic import AliasChoices, Field,field_validator
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

    @field_validator("dify_api_base_url", mode="after")
    @classmethod
    def validate_dify_base_url(cls, v: str) -> str:
        """检测 DIFY_API_BASE_URL 是否误包含路径后缀，启动时打印警告。"""
        forbidden_suffixes = ("/chat-messages", "/workflows/run", "/files/upload", "/completion-messages")
        v_stripped = v.rstrip("/")
        for suffix in forbidden_suffixes:
            if v_stripped.endswith(suffix):
                import warnings
                warnings.warn(
                    f"DIFY_API_BASE_URL 以 '{suffix}' 结尾，可能导致 URL 拼接异常。"
                    f"应仅填写基础地址（如 http://host/v1），当前值: {v}",
                    UserWarning,
                )
                break
        return v

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parents[3] / ".env"),
        env_file_encoding="utf-8-sig",
        populate_by_name=True,
        extra="ignore",
    )

    @property
    def export_dir_path(self) -> Path:
        return Path(self.report_export_dir)


@lru_cache
def get_settings() -> Settings:
    return Settings()
