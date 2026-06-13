import type { VoiceRecognizeResult } from "@/types/voice";

function buildFormData(file: Blob, format: string, sampleRate: number): FormData {
  const data = new FormData();
  data.append("file", file, `recording.${format}`);
  data.append("format", format);
  data.append("sample_rate", String(sampleRate));
  return data;
}

export async function uploadVoiceForRecognition(
  file: Blob,
  format: string,
  sampleRate: number,
): Promise<VoiceRecognizeResult> {
  const body = buildFormData(file, format, sampleRate);

  const response = await fetch("/enterprise/api/v1/voice/recognize", {
    method: "POST",
    body,
  });

  const payload = await response.json().catch(() => null);

  if (!response.ok || !payload || payload.code !== 0) {
    const message = payload?.message || `语音识别失败：${response.status}`;
    throw new Error(message);
  }
  return payload.data;
}
