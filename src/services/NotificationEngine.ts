/**
 * NotificationEngine.ts - In-App Banner and Push Notification Engine
 */

export class NotificationEngine {
  private static instance: NotificationEngine;
  private listeners: ((notif: any) => void)[] = [];

  public static getInstance(): NotificationEngine {
    if (!NotificationEngine.instance) {
      NotificationEngine.instance = new NotificationEngine();
    }
    return NotificationEngine.instance;
  }

  public handleIncoming(message: any): void {}

  public registerNavigationHandler(fn: any): void {}

  public registerMuteChecker(fn: any): void {}

  public setSoundEffectsEnabled(enabled: boolean): void {}

  public dismissNotification(id: string): void {}

  public showNotification(notif: any): void {
    this.listeners.forEach((l) => l(notif));
  }

  public subscribe(fn: (notif: any) => void): () => void {
    this.listeners.push(fn);
    return () => {
      this.listeners = this.listeners.filter((l) => l !== fn);
    };
  }
}

export const notificationEngine = NotificationEngine.getInstance();
