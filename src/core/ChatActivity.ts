/**
 * ChatActivity.ts - org.telegram.ui.ChatActivity
 * Replicated directly from DrKLO/Telegram Android (TMessagesProj/src/main/java/org/telegram/ui/ChatActivity.java)
 *
 * Encapsulates ChatActivity's UI state controller:
 * - updateBottomPanel() logic
 * - ChannelBroadcastRestrictedView vs. ChatActivityEnterView state transitions
 * - NotificationCenter observer (UPDATE_MASK_CHAT, UPDATE_MASK_CHAT_ADMINS, chatInfoDidLoad)
 * - Mute/Unmute, Discussion (linked_chat_id), and Join Channel controls
 */

import { Chat } from '../types';
import { TLRPC } from './TLRPC';
import { ChatObject, AnyChat } from './ChatObject';
import { LocaleController } from './LocaleController';
import { NotificationCenter } from './NotificationCenter';
import { MessagesController } from './MessagesController';

export enum BottomPanelMode {
  ENTER_VIEW = 'ENTER_VIEW', // Normal input bar (textarea, attachment, voice, send)
  BROADCAST_RESTRICTED = 'BROADCAST_RESTRICTED', // Channel read-only overlay with megaphone + mute/unmute + discuss
  MEGAGROUP_RESTRICTED = 'MEGAGROUP_RESTRICTED', // Supergroup banned/restricted overlay with lock icon
  JOIN_CHANNEL = 'JOIN_CHANNEL', // Not a member: show JOIN button
}

export interface BottomPanelState {
  mode: BottomPanelMode;
  canSend: boolean;
  restrictedText: string;
  isBroadcast: boolean;
  isMegagroup: boolean;
  isAdmin: boolean;
  isMuted: boolean;
  hasDiscussion: boolean;
  linkedChatId?: number | string;
  isLeft: boolean;
}

export class ChatActivity {
  private currentAccount: number = 0;
  private currentChat: AnyChat | null = null;
  private stateListeners: Set<(state: BottomPanelState) => void> = new Set();
  private notificationDelegate: (...args: any[]) => void;

  constructor(chat?: AnyChat | null, account: number = 0) {
    this.currentAccount = account;
    this.currentChat = chat || null;

    this.notificationDelegate = (id: number | string, _account: number, ...args: any[]) => {
      this.didReceivedNotification(id, _account, ...args);
    };

    this.addNotificationObservers();
  }

  public setChat(chat: AnyChat | null): void {
    this.currentChat = chat;
    this.notifyStateChanged();
    if (chat && chat.id) {
      MessagesController.getInstance(this.currentAccount).loadChatInfo(chat.id).catch(() => {});
    }
  }

  public getCurrentChat(): AnyChat | null {
    return this.currentChat;
  }

  public addStateListener(listener: (state: BottomPanelState) => void): () => void {
    this.stateListeners.add(listener);
    // Emit initial state
    listener(this.updateBottomPanel());
    return () => {
      this.stateListeners.delete(listener);
    };
  }

  private notifyStateChanged(): void {
    const state = this.updateBottomPanel();
    this.stateListeners.forEach((listener) => listener(state));
  }

  /**
   * Replicates ChatActivity.updateBottomPanel() from Telegram Android
   */
  public updateBottomPanel(): BottomPanelState {
    const chat = this.currentChat;

    if (!chat) {
      return {
        mode: BottomPanelMode.ENTER_VIEW,
        canSend: true,
        restrictedText: '',
        isBroadcast: false,
        isMegagroup: false,
        isAdmin: false,
        isMuted: false,
        hasDiscussion: false,
        isLeft: false,
      };
    }

    const isLeft = ChatObject.isLeft(chat);
    const isBroadcast = ChatObject.isBroadcast(chat);
    const isMegagroup = ChatObject.isMegagroup(chat);
    const isAdmin = ChatObject.isAdmin(chat);
    const isMuted = Boolean((chat as any).isMuted);
    const linkedChatId = (chat as any).linked_chat_id || (chat as any).linkedChatId;
    const hasDiscussion = Boolean(linkedChatId);

    // If user is not in chat/channel and it's a channel/megagroup -> show JOIN view
    if (isLeft && (isBroadcast || isMegagroup)) {
      return {
        mode: BottomPanelMode.JOIN_CHANNEL,
        canSend: false,
        restrictedText: LocaleController.getString('ChannelJoin'),
        isBroadcast,
        isMegagroup,
        isAdmin: false,
        isMuted,
        hasDiscussion,
        linkedChatId,
        isLeft: true,
      };
    }

    // Pure broadcast channel logic
    if (isBroadcast) {
      if (!isAdmin) {
        // Non-admin in broadcast channel: hide input bar, show channel restriction overlay
        return {
          mode: BottomPanelMode.BROADCAST_RESTRICTED,
          canSend: false,
          restrictedText: LocaleController.getString('ChannelBroadcastRestricted'),
          isBroadcast: true,
          isMegagroup: false,
          isAdmin: false,
          isMuted,
          hasDiscussion,
          linkedChatId,
          isLeft: false,
        };
      } else {
        // Administrator in broadcast channel: can post messages
        return {
          mode: BottomPanelMode.ENTER_VIEW,
          canSend: true,
          restrictedText: '',
          isBroadcast: true,
          isMegagroup: false,
          isAdmin: true,
          isMuted,
          hasDiscussion,
          linkedChatId,
          isLeft: false,
        };
      }
    }

    // Megagroup / Supergroup restriction logic
    if (isMegagroup) {
      const canSend = ChatObject.canSendMessages(chat);
      if (!canSend) {
        return {
          mode: BottomPanelMode.MEGAGROUP_RESTRICTED,
          canSend: false,
          restrictedText: (chat as any).restrictionReason || LocaleController.getString('ChannelRestricted'),
          isBroadcast: false,
          isMegagroup: true,
          isAdmin,
          isMuted,
          hasDiscussion: false,
          isLeft: false,
        };
      } else {
        return {
          mode: BottomPanelMode.ENTER_VIEW,
          canSend: true,
          restrictedText: '',
          isBroadcast: false,
          isMegagroup: true,
          isAdmin,
          isMuted,
          hasDiscussion: false,
          isLeft: false,
        };
      }
    }

    // Normal private chat or regular group
    const canSend = ChatObject.canSendMessages(chat);
    return {
      mode: canSend ? BottomPanelMode.ENTER_VIEW : BottomPanelMode.MEGAGROUP_RESTRICTED,
      canSend,
      restrictedText: canSend ? '' : LocaleController.getString('ChannelRestricted'),
      isBroadcast: false,
      isMegagroup: false,
      isAdmin,
      isMuted,
      hasDiscussion: false,
      isLeft: false,
    };
  }

  /**
   * Replicates ChatActivity.didReceivedNotification() from Telegram Android
   */
  public didReceivedNotification(id: number | string, _account: number, ...args: any[]): void {
    if (id === NotificationCenter.updateInterfaces) {
      const mask = typeof args[0] === 'number' ? args[0] : 0;
      if (
        (mask & NotificationCenter.UPDATE_MASK_CHAT) !== 0 ||
        (mask & NotificationCenter.UPDATE_MASK_CHAT_ADMINS) !== 0 ||
        (mask & NotificationCenter.UPDATE_MASK_SELECT_DIALOG) !== 0
      ) {
        this.notifyStateChanged();
      }
    } else if (id === NotificationCenter.chatInfoDidLoad) {
      const chatId = args[0];
      if (this.currentChat && String(this.currentChat.id) === String(chatId)) {
        if (args[1] && typeof args[1] === 'object') {
          // Merge newly loaded chat flags
          Object.assign(this.currentChat, args[1]);
        }
        this.notifyStateChanged();
      }
    }
  }

  public addNotificationObservers(): void {
    const nc = NotificationCenter.getInstance(this.currentAccount);
    nc.addObserver(this.notificationDelegate, NotificationCenter.updateInterfaces);
    nc.addObserver(this.notificationDelegate, NotificationCenter.chatInfoDidLoad);
  }

  public removeNotificationObservers(): void {
    const nc = NotificationCenter.getInstance(this.currentAccount);
    nc.removeObserver(this.notificationDelegate, NotificationCenter.updateInterfaces);
    nc.removeObserver(this.notificationDelegate, NotificationCenter.chatInfoDidLoad);
    this.stateListeners.clear();
  }

  public onDestroy(): void {
    this.removeNotificationObservers();
  }
}
