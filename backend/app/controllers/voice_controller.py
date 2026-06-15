"""语音识别接口。

提供 REST 接口供前端上传音频，返回识别文本。

识别引擎优先级：本地 Whisper → Qwen ASR（fallback）
"""

import logging
import tempfile
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from ..integrations.whisper_asr import get_whisper_error, is_whisper_available, recogn_file

logger = logging.getLogger("app.voice")

router = APIRouter(prefix="/api/v1/voice", tags=["语音识别"])


@router.post("/recognize", summary="一句话语音识别")
async def recognize(
    file: UploadFile = File(description="音频文件，支持 wav/pcm/opus/mp3/m4a/webm/aac"),
    format: str = Form(default="wav", description="音频格式"),
    sample_rate: int = Form(default=16000, description="采样率"),
):
    """上传音频并返回识别文本。

    前端录音后调用此接口获取文字，再传入 /execute 执行业务操作。

    识别引擎：优先使用本地 Whisper（免费离线），不可用时降级到 Qwen ASR。
    """
    # content-type check: allow audio/*, application/octet-stream, or missing
    if file.content_type and (
        not file.content_type.startswith("audio/")
        and file.content_type not in ("application/octet-stream", "multipart/form-data")
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的音频类型: {file.content_type}",
        )

    audio_data = await file.read()
    if not audio_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="上传的音频文件为空",
        )

    text = None
    engine = None
    whisper_fail_reason = None

    # 方案 B 优先：本地 Whisper（免费、离线）
    if is_whisper_available():
        try:
            text = recogn_file(audio_data, file_format=format, sample_rate=sample_rate)
            engine = "whisper"
            logger.info(f"Whisper 识别成功: {text[:80]}...")
        except Exception as e:
            whisper_fail_reason = str(e)
            logger.warning(f"Whisper 识别失败，尝试 Qwen fallback: {e}")

    # 方案 A 降级：Qwen ASR
    if text is None:
        from ..integrations.qwen_asr import QwenAsrClient

        client = QwenAsrClient()
        if not client.is_available():
            detail = "语音识别服务未配置。"
            reasons = []
            if whisper_fail_reason:
                reasons.append(f"Whisper: {whisper_fail_reason}")
            else:
                whisper_error = get_whisper_error()
                if whisper_error:
                    reasons.append(f"Whisper: {whisper_error}")
                else:
                    reasons.append("Whisper 模型未安装（pip install openai-whisper）")
            reasons.append("Qwen ASR: 未配置 QWEN_ASR_API_KEY")
            detail += " " + "；".join(reasons)
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail=detail,
            )

        try:
            text = client.recognize_file(audio_data, file_format=format, sample_rate=sample_rate)
            engine = "qwen"
        except RuntimeError as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=str(e),
            )

    if not text:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="语音识别未返回内容，音频可能不含有效语音",
        )

    duration = round(len(audio_data) / (sample_rate * 2), 1) if sample_rate else 0

    return {
        "code": 0,
        "message": f"success ({engine})",
        "data": {
            "text": text,
            "duration_seconds": duration,
            "engine": engine,
        },
        "trace_id": None,
    }
