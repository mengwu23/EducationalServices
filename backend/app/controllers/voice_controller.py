"""语音识别接口。

提供 REST 接口供前端上传音频，返回识别文本。
"""

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from ..integrations.qwen_asr import QwenAsrClient

router = APIRouter(prefix="/api/v1/voice", tags=["语音识别"])


@router.post("/recognize", summary="一句话语音识别")
async def recognize(
    file: UploadFile = File(description="音频文件，支持 wav/pcm/opus/mp3/m4a/webm/aac"),
    format: str = Form(default="wav", description="音频格式"),
    sample_rate: int = Form(default=16000, description="采样率"),
):
    """上传音频并返回识别文本。

    前端录音后调用此接口获取文字，再传入 /execute 执行业务操作。

    ### 请求
    使用 multipart/form-data 上传音频文件。

    ### 示例
    ```bash
    curl -X POST http://localhost:8088/enterprise/api/v1/voice/recognize \\
      -F "file=@recording.wav" \\
      -F "format=wav" \\
      -F "sample_rate=16000"
    ```

    ### 接入流程
    1. 前端 MediaRecorder 录音 → 获取 blob
    2. POST /voice/recognize 上传 → 得到 text
    3. 展示 text 给用户确认
    4. POST /execute {"query": text} → 执行业务操作
    """
    client = QwenAsrClient()

    if not client.is_available():
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="语音识别服务未配置（需设置 QWEN_ASR_API_KEY）",
        )

    if file.content_type and not file.content_type.startswith("audio/"):
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

    try:
        text = client.recognize_file(audio_data, file_format=format, sample_rate=sample_rate)
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(e),
        )

    return {
        "code": 0,
        "message": "success",
        "data": {
            "text": text,
            "duration_seconds": round(len(audio_data) / (sample_rate * 2), 1) if sample_rate else 0,
        },
        "trace_id": None,
    }
