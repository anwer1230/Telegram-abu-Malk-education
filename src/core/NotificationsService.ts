/**
 * NotificationsService.ts - Push Notification Registration & Automation Dispatcher
 */

import { AutoJoinerTask } from '../types';

export class NotificationsService {
  private static instance: NotificationsService;
  private autoJoinTasks: AutoJoinerTask[] = [];
  private listeners: (() => void)[] = [];

  public static getInstance(): NotificationsService {
    if (!NotificationsService.instance) {
      NotificationsService.instance = new NotificationsService();
    }
    return NotificationsService.instance;
  }

  public async registerForPush(): Promise<string> {
    return 'fcm_token_device_registered';
  }

  public notify(title: string, body: string): void {
    if (typeof Notification !== 'undefined' && Notification.permission === 'granted') {
      new Notification(title, { body });
    }
  }

  public handleIncomingMessage(...args: any[]): void {}

  public subscribe(fn: () => void): () => void {
    this.listeners.push(fn);
    return () => {
      this.listeners = this.listeners.filter((l) => l !== fn);
    };
  }

  private notifyListeners(): void {
    this.listeners.forEach((l) => l());
  }

  public getAutoJoinTasks(): AutoJoinerTask[] {
    return this.autoJoinTasks;
  }

  public extractLinksFromRawText(text: string): string[] {
    const matches = text.match(/(?:https?:\/\/)?(?:t\.me|telegram\.me)\/[a-zA-Z0-9_+]+/g);
    return matches ? Array.from(new Set(matches)) : [];
  }

  public async startAutoJoinTasks(
    links: string[],
    onProgress?: (processed: number, total: number) => void
  ): Promise<void> {
    this.autoJoinTasks = links.map((url, i) => ({
      id: 'task_' + i + '_' + Date.now(),
      url,
      type: 'public',
      status: 'pending',
    }));
    this.notifyListeners();

    for (let i = 0; i < this.autoJoinTasks.length; i++) {
      this.autoJoinTasks[i].status = 'joined';
      if (onProgress) {
        onProgress(i + 1, this.autoJoinTasks.length);
      }
    }
    this.notifyListeners();
  }

  public stopAutoJoin(): void {
    this.autoJoinTasks = [];
    this.notifyListeners();
  }
}

export const notificationsService = NotificationsService.getInstance();
