/**
 * TopicsController.ts - org.telegram.messenger.TopicsController
 * Manages Forum supergroup topics, pins, and thread isolation.
 */

import { NotificationCenter } from '../NotificationCenter';

export interface ForumTopic {
  id: number;
  title: string;
  iconColor?: number;
  iconEmojiId?: string;
  unreadCount?: number;
  isPinned?: boolean;
  pinned?: boolean;
  isClosed?: boolean;
  totalMessages?: number;
}

export class TopicsController {
  private static instance: TopicsController;
  private topicsMap = new Map<string, ForumTopic[]>();

  public static getInstance(): TopicsController {
    if (!TopicsController.instance) {
      TopicsController.instance = new TopicsController();
    }
    return TopicsController.instance;
  }

  public loadTopics(chatId: string): ForumTopic[] {
    if (this.topicsMap.has(chatId)) {
      return this.topicsMap.get(chatId)!;
    }
    const defaultTopics: ForumTopic[] = [
      { id: 1, title: 'General', isPinned: true, pinned: true, unreadCount: 0, totalMessages: 12 },
      { id: 2, title: 'Announcements', isPinned: false, pinned: false, unreadCount: 0, totalMessages: 5 },
    ];
    this.topicsMap.set(chatId, defaultTopics);
    return defaultTopics;
  }

  public getTopics(chatId: string): ForumTopic[] {
    return this.topicsMap.get(chatId) || this.loadTopics(chatId);
  }

  public createTopic(chatId: string, title: string, iconColor?: number): ForumTopic {
    const list = this.getTopics(chatId);
    const newTopic: ForumTopic = {
      id: Date.now(),
      title,
      iconColor: iconColor || 0x2481cc,
      isPinned: false,
      pinned: false,
      unreadCount: 0,
      totalMessages: 0,
    };
    const updated = [...list, newTopic];
    this.topicsMap.set(chatId, updated);
    NotificationCenter.getGlobalInstance().postNotificationName(NotificationCenter.topicsDidLoaded, chatId);
    return newTopic;
  }

  public deleteTopic(chatId: string, topicId: number): void {
    const list = this.getTopics(chatId);
    this.topicsMap.set(chatId, list.filter((t) => t.id !== topicId));
  }

  public togglePinTopic(chatId: string, topicId: number): void {
    const list = this.getTopics(chatId);
    const updated = list.map((t) => {
      if (t.id === topicId) {
        const next = !t.isPinned;
        return { ...t, isPinned: next, pinned: next };
      }
      return t;
    });
    this.topicsMap.set(chatId, updated);
  }
}

export const topicsController = TopicsController.getInstance();
