"""千问（通义）语音识别客户端。

流程：保存音频 → 通过公网可访问 URL 提交给 DashScope ASR → 返回识别文本
"""

import json
import os
import time
import uuid
from pathlib import Path
from typing import Optional

import requests
from fastapi import UploadFile

from ..core.config import get_settings

# 音频文件存储目录
AUDIO_DIR = Path(__file__).resolve().parent.parent.parent / "storage" / "audio"

TASK_API = "https://dashscope.aliyuncs.com/api/v1/services/audio/asr/transcriptions"
QUERY_API = "https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}"


class QwenAsrClient:
    """千问语音识别客户端。"""

    def __init__(self):
        settings = get_settings()
        self.api_key = settings.qwen_asr_api_key or os.getenv("QWEN_ASR_API_KEY")
        AUDIO_DIR.mkdir(parents=True, exist_ok=True)

    def is_available(self) -> bool:
        return bool(self.api_key)

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

    def save_audio(self, audio_data: bytes, file_format: str) -> str:
        """保存音频到本地，返回相对路径名。"""
        fmt = file_format.strip(".")
        filename = f"{uuid.uuid4().hex}.{fmt}"
        filepath = AUDIO_DIR / filename
        filepath.write_bytes(audio_data)
        return filename

    def get_file_url(self, filename: str) -> str:
        """构造音频文件的公网访问 URL（依赖外部可访问的文件服务）。"""
        # 本地开发时无法直接提供公网 URL，
        # 此处预留接口，后续对接 OSS 或 CDN 后替换
        return f"/storage/audio/{filename}"

    def recognize_file(self, audio_data: bytes, file_format: str = "wav",
                       sample_rate: int = 16000) -> str:
        """语音识别：需要音频文件具有公网可访问的 URL。"""
        if not self.is_available():
            raise RuntimeError("未配置 QWEN_ASR_API_KEY")

        raise RuntimeError(
            "DashScope ASR 需要音频文件具有公网可访问的 HTTP URL。\n"
            "请将音频文件上传至 OSS/CDN 后，直接调用 /execute 传入文本即可。\n"
            "或在前端使用 Web Speech API 直接识别：\n"
            "const recognition = new webkitSpeechRecognition();\n"
            "recognition.onresult = (e) => fetch('/execute', {body: JSON.stringify({query: e.results[0][0].transcript})});"
        )
