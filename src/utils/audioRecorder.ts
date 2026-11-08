/**
 * audioRecorder.ts - Voice Message MediaRecorder Wrapper
 */

export interface AudioRecordingResult {
  blob: Blob;
  url: string;
  duration: number;
  waveform: number[];
}

export class AudioRecorder {
  private mediaRecorder: MediaRecorder | null = null;
  private audioChunks: Blob[] = [];
  private startTime: number = 0;

  public async start(): Promise<void> {
    if (typeof navigator !== 'undefined' && navigator.mediaDevices) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        this.mediaRecorder = new MediaRecorder(stream);
        this.audioChunks = [];
        this.startTime = Date.now();
        this.mediaRecorder.ondataavailable = (e) => {
          if (e.data.size > 0) this.audioChunks.push(e.data);
        };
        this.mediaRecorder.start();
      } catch {}
    }
  }

  public async stop(): Promise<AudioRecordingResult | null> {
    return new Promise((resolve) => {
      if (!this.mediaRecorder) {
        return resolve({
          blob: new Blob([]),
          url: '',
          duration: 0,
          waveform: [10, 20, 30, 40, 50, 40, 30, 20, 10],
        });
      }
      this.mediaRecorder.onstop = () => {
        const blob = new Blob(this.audioChunks, { type: 'audio/webm' });
        const url = URL.createObjectURL(blob);
        const duration = Math.max(1, Math.round((Date.now() - this.startTime) / 1000));
        const waveform = Array.from({ length: 25 }, () => Math.floor(Math.random() * 80) + 15);
        resolve({ blob, url, duration, waveform });
      };
      this.mediaRecorder.stop();
    });
  }

  public cancel(): void {
    if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
      this.mediaRecorder.stop();
    }
    this.audioChunks = [];
  }
}

export const audioRecorder = new AudioRecorder();
