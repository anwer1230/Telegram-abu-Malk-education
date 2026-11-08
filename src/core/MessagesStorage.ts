/**
 * MessagesStorage.ts - org.telegram.messenger.MessagesStorage
 * Mirrors SQLite database persistence for dialogs and messages.
 */

import { Chat, Message } from '../types';

export class MessagesStorage {
  private static instances = new Map<number, MessagesStorage>();
  private currentAccount: number;
  private drafts = new Map<string, string>();
  private readMax = new Map<string, number>();
  private dialogFlags = new Map<string, number>();

  public static getInstance(account: number = 0): MessagesStorage {
    if (!MessagesStorage.instances.has(account)) {
      MessagesStorage.instances.set(account, new MessagesStorage(account));
    }
    return MessagesStorage.instances.get(account)!;
  }

  private constructor(account: number) {
    this.currentAccount = account;
  }

  public getDialogs(offset: number = 0, count: number = 100): Chat[] {
    if (typeof window === 'undefined') return [];
    try {
      const raw = localStorage.getItem(`tg_cached_dialogs_${this.currentAccount}`);
      if (raw) {
        const list = JSON.parse(raw);
        return Array.isArray(list) ? list.slice(offset, offset + count) : [];
      }
    } catch {}
    return [];
  }

  public saveDialog(dialog: Chat): void {
    if (typeof window === 'undefined') return;
    try {
      const key = `tg_cached_dialogs_${this.currentAccount}`;
      const existing: Chat[] = JSON.parse(localStorage.getItem(key) || '[]');
      const filtered = existing.filter((d) => d.id !== dialog.id);
      localStorage.setItem(key, JSON.stringify([dialog, ...filtered]));
    } catch {}
  }

  public saveDraft(chatId: string, draftText: string): void {
    this.drafts.set(chatId, draftText);
    if (typeof window !== 'undefined') {
      try {
        localStorage.setItem(`tg_draft_${this.currentAccount}_${chatId}`, draftText);
      } catch {}
    }
  }

  public markMessagesAsRead(dialogId: string, maxId: string | number): void {
    const num = typeof maxId === 'number' ? maxId : parseInt(maxId, 10) || 0;
    this.readMax.set(dialogId, num);
  }

  public setDialogFlags(dialogId: string, flags: number): void {
    this.dialogFlags.set(dialogId, flags);
  }

  public deleteDialog(dialogId: string, mode: number): void {
    this.dialogFlags.delete(dialogId);
    this.drafts.delete(dialogId);
  }

  public saveMessage(message: Message): void {
    if (typeof window !== 'undefined') {
      try {
        const key = `tg_msgs_${this.currentAccount}_${message.chatId}`;
        const existing = JSON.parse(localStorage.getItem(key) || '[]');
        existing.push(message);
        localStorage.setItem(key, JSON.stringify(existing));
      } catch {}
    }
  }

  public getMessages(chatId: string, count: number = 50, maxId: number = 0): Message[] {
    if (typeof window === 'undefined') return [];
    try {
      const raw = localStorage.getItem(`tg_msgs_${this.currentAccount}_${chatId}`);
      if (raw) {
        const list: Message[] = JSON.parse(raw);
        if (Array.isArray(list)) {
          return list.slice(0, count);
        }
      }
    } catch {}
    return [];
  }

  public cleanUp(cleanAll?: boolean | number): void {
    if (typeof window !== 'undefined') {
      try {
        localStorage.removeItem(`tg_cached_dialogs_${this.currentAccount}`);
      } catch {}
    }
  }
}

export const messagesStorage = MessagesStorage.getInstance(0);
