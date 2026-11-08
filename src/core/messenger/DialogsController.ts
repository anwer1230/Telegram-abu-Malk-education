/**
 * DialogsController.ts - org.telegram.messenger.DialogsController
 * Manages active dialog entries, read offsets, pinning state, folders, and dialog lists per account.
 */

import { TLRPC } from '../TLRPC';

export interface DialogItem {
  id: string;
  peerId: string;
  topMessageId: number;
  unreadCount: number;
  readInboxMaxId: number;
  readOutboxMaxId: number;
  isPinned: boolean;
  pinIndex: number;
  folderId: number;
  lastMessageDate: number;
  draftMessage?: string;
  isMuted?: boolean;
}

export class DialogsController {
  private static instances: Map<number, DialogsController> = new Map();
  public account: number;
  public dialogs: Map<string, DialogItem> = new Map();
  public pinnedDialogs: string[] = [];

  constructor(account: number = 0) {
    this.account = account;
    this.loadState();
  }

  public static getInstance(account: number = 0): DialogsController {
    let instance = DialogsController.instances.get(account);
    if (!instance) {
      instance = new DialogsController(account);
      DialogsController.instances.set(account, instance);
    }
    return instance;
  }

  private loadState(): void {
    try {
      if (typeof window !== 'undefined' && window.localStorage) {
        const raw = localStorage.getItem(`tg_dialogs_state_${this.account}`);
        if (raw) {
          const list: DialogItem[] = JSON.parse(raw);
          list.forEach((d) => this.dialogs.set(d.id, d));
          this.pinnedDialogs = list.filter((d) => d.isPinned).map((d) => d.id);
        }
      }
    } catch (e) {
      console.warn(`[DialogsController_${this.account}] Failed to load dialog state`, e);
    }
  }

  public saveState(): void {
    try {
      if (typeof window !== 'undefined' && window.localStorage) {
        const list = Array.from(this.dialogs.values());
        localStorage.setItem(`tg_dialogs_state_${this.account}`, JSON.stringify(list));
      }
    } catch (e) {
      console.warn(`[DialogsController_${this.account}] Failed to save dialog state`, e);
    }
  }

  public markDialogAsRead(dialogId: string | number, maxId: number): void {
    const id = String(dialogId);
    let item = this.dialogs.get(id);
    if (!item) {
      item = {
        id,
        peerId: id,
        topMessageId: maxId,
        unreadCount: 0,
        readInboxMaxId: maxId,
        readOutboxMaxId: maxId,
        isPinned: false,
        pinIndex: 0,
        folderId: 0,
        lastMessageDate: Date.now(),
      };
      this.dialogs.set(id, item);
    } else {
      item.unreadCount = 0;
      item.readInboxMaxId = Math.max(item.readInboxMaxId, maxId);
    }
    this.saveState();
  }

  public setDialogPinned(dialogId: string | number, isPinned: boolean): void {
    const id = String(dialogId);
    let item = this.dialogs.get(id);
    if (!item) {
      item = {
        id,
        peerId: id,
        topMessageId: 0,
        unreadCount: 0,
        readInboxMaxId: 0,
        readOutboxMaxId: 0,
        isPinned,
        pinIndex: isPinned ? Date.now() : 0,
        folderId: 0,
        lastMessageDate: Date.now(),
      };
      this.dialogs.set(id, item);
    } else {
      item.isPinned = isPinned;
      item.pinIndex = isPinned ? Date.now() : 0;
    }

    if (isPinned) {
      if (!this.pinnedDialogs.includes(id)) {
        this.pinnedDialogs.unshift(id);
      }
    } else {
      this.pinnedDialogs = this.pinnedDialogs.filter((did) => did !== id);
    }
    this.saveState();
  }

  public getDialog(dialogId: string | number): DialogItem | undefined {
    return this.dialogs.get(String(dialogId));
  }

  public getAllDialogs(): DialogItem[] {
    return Array.from(this.dialogs.values()).sort((a, b) => {
      if (a.isPinned && !b.isPinned) return -1;
      if (!a.isPinned && b.isPinned) return 1;
      return b.lastMessageDate - a.lastMessageDate;
    });
  }

  public getDialogsInFolder(folderId: number = 0): DialogItem[] {
    return this.getAllDialogs().filter((d) => d.folderId === folderId);
  }

  public deleteDialog(dialogId: string | number): void {
    const id = String(dialogId);
    this.dialogs.delete(id);
    this.pinnedDialogs = this.pinnedDialogs.filter((did) => did !== id);
    this.saveState();
  }
}

export const dialogsController = DialogsController.getInstance(0);
