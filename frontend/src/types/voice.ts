export interface VoiceRecognizeRequest {
  file: Blob;
  format: string;
  sample_rate: number;
}

export interface VoiceRecognizeResult {
  text: string;
  duration_seconds: number;
}
