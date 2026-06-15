"""本地 Whisper 语音识别客户端。

使用 OpenAI openai-whisper 库，首次调用自动下载 small 模型（~460MB）。
无需 API Key，完全离线运行。

音频读取策略：soundfile 优先（wav/flac），ffmpeg 降级（m4a/webm/mp3/aac/opus）。
"""

import logging
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)

_whisper_model = None
_whisper_load_error: Optional[str] = None
_model_size = "small"

_FFMPEG_PATH = shutil.which("ffmpeg") or "D:\\Conda\\Library\\bin\\ffmpeg.exe"


def _get_model():
    """延迟加载 Whisper 模型（单例），失败后下次调用自动重试。"""
    global _whisper_model, _whisper_load_error

    if _whisper_model is not None:
        return _whisper_model

    try:
        import whisper
    except ImportError:
        _whisper_load_error = "未安装 openai-whisper，请运行 pip install openai-whisper"
        logger.warning(_whisper_load_error)
        return None

    try:
        _whisper_model = whisper.load_model(_model_size)
        _whisper_load_error = None
        logger.info(f"Whisper {_model_size} 模型加载完成")
    except Exception as e:
        msg = f"Whisper 模型加载失败: {e}"
        _whisper_load_error = msg
        logger.warning(msg)
        return None

    return _whisper_model


def is_whisper_available() -> bool:
    return _get_model() is not None


def get_whisper_error() -> Optional[str]:
    return _whisper_load_error


def _read_audio(filepath: str) -> "tuple[np.ndarray, int]":
    """读取音频为 numpy 数组。先试 soundfile（wav/flac），失败则 ffmpeg 转码。"""
    try:
        import soundfile as sf
        audio, sr = sf.read(filepath, dtype="float32")
        if audio.ndim > 1:
            audio = audio.mean(axis=1)
        return audio, sr
    except Exception:
        pass

    # ffmpeg 转码为 raw PCM
    raw_path = filepath + ".raw"
    try:
        subprocess.run(
            [_FFMPEG_PATH, "-y", "-i", filepath, "-f", "s16le", "-acodec", "pcm_s16le",
             "-ar", "16000", "-ac", "1", raw_path],
            capture_output=True, check=True, timeout=30,
        )
        raw_data = Path(raw_path).read_bytes()
        audio = np.frombuffer(raw_data, dtype=np.int16).astype(np.float32) / 32768.0
        return audio, 16000
    finally:
        Path(raw_path).unlink(missing_ok=True)


def recogn_file(audio_data: bytes, file_format: str = "wav", sample_rate: int = 16000) -> str:
    """用本地 Whisper 识别音频，返回文本。

    支持 WAV/PCM/FLAC（soundfile 直接读）和 MP3/M4A/WebM/AAC/OPUS（ffmpeg 转码）。
    """
    model = _get_model()
    if model is None:
        raise RuntimeError(_whisper_load_error or "Whisper 不可用")

    suffix = f".{file_format.strip('.')}"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(audio_data)
        tmp_path = tmp.name

    try:
        audio, sr = _read_audio(tmp_path)
        if sr != 16000:
            import scipy.signal
            audio = scipy.signal.resample(audio, int(len(audio) * 16000 / sr))

        result = model.transcribe(audio, language="zh", fp16=False)
        text = result["text"].strip()
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    return text
