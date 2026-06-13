"""通用 LLM 文本调用客户端。

复用 NL2SQL 已就绪的 DeepSeek 直连配置（nl2sql_llm_*），为工单分类、
情绪识别等轻量 AI 文本任务提供统一入口，避免依赖 Dify 工作流。

设计要点：
- 未配置 API Key 时 is_available() 返回 False，调用方可优雅降级而不报错。
- complete() 接收 system + user 文本，返回模型纯文本输出。
- complete_json() 在 complete() 基础上做容错 JSON 解析（剥离代码块/思考标签）。
"""

import json
import re
from typing import Any

from openai import OpenAI

from backend.app.core.config import Settings, get_settings


class LlmTextClient:
    """基于 OpenAI 兼容协议的轻量文本补全客户端。"""

    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()
        self._client: OpenAI | None = None

    def is_available(self) -> bool:
        """是否已配置可用的 LLM API Key。未配置时调用方应跳过 AI 流程。"""
        return bool(self.settings.nl2sql_llm_api_key)

    def _ensure_client(self) -> OpenAI:
        if self._client is None:
            if not self.settings.nl2sql_llm_api_key:
                raise RuntimeError("未配置 LLM API Key（nl2sql_llm_api_key）")
            self._client = OpenAI(
                api_key=self.settings.nl2sql_llm_api_key,
                base_url=self.settings.nl2sql_llm_base_url,
            )
        return self._client

    def complete(
        self,
        system_prompt: str,
        user_content: str,
        *,
        temperature: float = 0.0,
        max_tokens: int = 800,
    ) -> str:
        """调用 LLM 返回纯文本输出。"""
        client = self._ensure_client()
        response = client.chat.completions.create(
            model=self.settings.nl2sql_llm_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            stream=False,
        )
        return (response.choices[0].message.content or "").strip()

    def complete_json(
        self,
        system_prompt: str,
        user_content: str,
        *,
        temperature: float = 0.0,
        max_tokens: int = 800,
    ) -> dict[str, Any]:
        """调用 LLM 并把输出解析为 JSON 对象，解析失败时抛 ValueError。"""
        raw = self.complete(
            system_prompt,
            user_content,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        parsed = self._parse_json_object(raw)
        if parsed is None:
            raise ValueError(f"LLM 输出无法解析为 JSON：{raw[:200]}")
        return parsed

    @staticmethod
    def _parse_json_object(text: str) -> dict[str, Any] | None:
        """从模型输出中提取第一个 JSON 对象，容忍代码块和 <think> 包裹。"""
        if not text:
            return None
        cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.IGNORECASE | re.DOTALL).strip()
        fence = re.search(r"```(?:json)?\s*(.*?)```", cleaned, flags=re.IGNORECASE | re.DOTALL)
        candidates = []
        if fence:
            candidates.append(fence.group(1).strip())
        candidates.append(cleaned)
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if 0 <= start < end:
            candidates.append(cleaned[start : end + 1])
        for candidate in candidates:
            try:
                parsed = json.loads(candidate)
            except (json.JSONDecodeError, TypeError):
                continue
            if isinstance(parsed, dict):
                return parsed
        return None
