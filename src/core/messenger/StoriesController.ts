/**
 * StoriesController.ts - org.telegram.messenger.StoriesController
 * Direct TypeScript translation of DrKLO/Telegram Android architecture
 */

import { Story } from '../../types';
import { NotificationCenter } from '../NotificationCenter';
import { ConnectionsManager } from '../ConnectionsManager';

export class StoriesController {
  private static instances = new Map<number, StoriesController>();
  private currentAccount: number;
  public storiesEnabled: boolean = true;
  public storyQualityFull: boolean = true;
  public stealthMode: boolean = false;
  private storiesByPeer = new Map<string, Story[]>();

  public static getInstance(account: number = 0): StoriesController {
    if (!StoriesController.instances.has(account)) {
      StoriesController.instances.set(account, new StoriesController(account));
    }
    return StoriesController.instances.get(account)!;
  }

  private constructor(account: number) {
    this.currentAccount = account;
    this.loadState();
  }

  private loadState(): void {
    if (typeof window === 'undefined') return;
    try {
      const raw = localStorage.getItem(`tg_stories_settings_${this.currentAccount}`);
      if (raw) {
        const parsed = JSON.parse(raw);
        this.storiesEnabled = parsed.storiesEnabled ?? true;
        this.storyQualityFull = parsed.storyQualityFull ?? true;
        this.stealthMode = parsed.stealthMode ?? false;
      }
    } catch {}
  }

  public saveSettings(): void {
    if (typeof window === 'undefined') return;
    try {
      const data = {
        storiesEnabled: this.storiesEnabled,
        storyQualityFull: this.storyQualityFull,
        stealthMode: this.stealthMode,
      };
      localStorage.setItem(`tg_stories_settings_${this.currentAccount}`, JSON.stringify(data));
    } catch {}
  }

  public async loadAllStories(force: boolean = false): Promise<any> {
    if (!this.storiesEnabled) return [];
    try {
      const conn = ConnectionsManager.getInstance(this.currentAccount);
      const req = {
        _: 'stories.getAllStories',
        flags: 0,
      };
      const res = await conn.sendRequest<any>(req);
      NotificationCenter.getInstance(this.currentAccount).postNotificationName(
        NotificationCenter.storiesUpdated,
        res
      );
      return res;
    } catch (e) {
      console.warn('[StoriesController] loadAllStories failed:', e);
      return [];
    }
  }

  public async sendStory(
    media: any,
    caption: string = '',
    period: number = 86400,
    privacyRules: any[] = []
  ): Promise<any> {
    try {
      const conn = ConnectionsManager.getInstance(this.currentAccount);
      const req = {
        _: 'stories.sendStory',
        peer: { _: 'inputPeerSelf' },
        media,
        caption,
        period,
        privacy_rules: privacyRules,
      };
      const res = await conn.sendRequest<any>(req);
      await this.loadAllStories(true);
      return res;
    } catch (e) {
      console.warn('[StoriesController] sendStory failed:', e);
      return null;
    }
  }

  public getStoriesForPeer(peerId: string): Story[] {
    return this.storiesByPeer.get(peerId) || [];
  }

  public setStoriesForPeer(peerId: string, stories: Story[]): void {
    this.storiesByPeer.set(peerId, stories);
    NotificationCenter.getInstance(this.currentAccount).postNotificationName(
      NotificationCenter.storiesUpdated,
      peerId,
      stories
    );
  }
}

export const storiesController = StoriesController.getInstance();
