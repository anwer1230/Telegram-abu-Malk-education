/**
 * audioNotification.ts - In-App Telegram Audio Synthesis & Feedback
 */

export class TelegramAudioNotification {
  public playMessageSent(): void {}
  public playMessageReceived(): void {}
  public playCallingTone(): void {}
  public playMessageChime(): void {}
  public playSentPop(): void {}
}

export const telegramAudio = new TelegramAudioNotification();
