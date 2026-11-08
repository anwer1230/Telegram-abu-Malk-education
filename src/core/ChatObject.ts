/**
 * ChatObject.ts - org.telegram.messenger.ChatObject
 * Replicated directly from DrKLO/Telegram Android (TMessagesProj/src/main/java/org/telegram/messenger/ChatObject.java)
 *
 * Implements authoritative logic for reading flags (broadcast, megagroup, creator, left, admin_rights, banned_rights)
 * and evaluating permissions for sending messages, media, stickers, polls, and moderation controls.
 */

import { Chat } from '../types';
import { TLRPC } from './TLRPC';
import { LocaleController } from './LocaleController';

export type AnyChat = TLRPC.Chat | Chat;

export class ChatObject {
  /**
   * Matches ChatObject.isChannel(TLRPC.Chat chat) in Telegram Android:
   * Returns true if chat is a channel (either broadcast or megagroup/supergroup)
   */
  public static isChannel(chat?: AnyChat | null): boolean {
    if (!chat) return false;
    return Boolean(
      (chat as any).broadcast ||
      (chat as any).megagroup ||
      (chat as any).isMegagroup ||
      (chat as any).type === 'channel'
    );
  }

  /**
   * Matches ChatObject.isBroadcast(TLRPC.Chat chat) in Telegram Android:
   * Returns true if chat is a pure broadcast channel (where only admins can post)
   */
  public static isBroadcast(chat?: AnyChat | null): boolean {
    if (!chat) return false;
    if ((chat as any).broadcast !== undefined) {
      return Boolean((chat as any).broadcast);
    }
    if ((chat as any).isBroadcast !== undefined) {
      return Boolean((chat as any).isBroadcast);
    }
    // If megagroup is true, it is NOT a broadcast channel
    if ((chat as any).megagroup || (chat as any).isMegagroup) {
      return false;
    }
    if ((chat as any).type === 'group' || (chat as any).type === 'saved' || (chat as any).type === 'private' || (chat as any).type === 'bot') {
      return false;
    }
    return (chat as any).type === 'channel';
  }

  /**
   * Matches ChatObject.isMegagroup(TLRPC.Chat chat) in Telegram Android:
   * Returns true if chat is a supergroup / megagroup
   */
  public static isMegagroup(chat?: AnyChat | null): boolean {
    if (!chat) return false;
    return Boolean((chat as any).megagroup || (chat as any).isMegagroup || (chat as any).type === 'group');
  }

  /**
   * Matches ChatObject.isAdmin(TLRPC.Chat chat) in Telegram Android:
   * Returns true if current user is the owner (creator) or has admin rights
   */
  public static isAdmin(chat?: AnyChat | null): boolean {
    if (!chat) return false;
    return Boolean(
      (chat as any).creator ||
      (chat as any).isCreator ||
      (chat as any).admin_rights != null ||
      (chat as any).adminRights != null
    );
  }

  /**
   * Matches ChatObject.isCreator(TLRPC.Chat chat) in Telegram Android:
   */
  public static isCreator(chat?: AnyChat | null): boolean {
    if (!chat) return false;
    return Boolean((chat as any).creator || (chat as any).isCreator);
  }

  /**
   * Matches ChatObject.isLeft(TLRPC.Chat chat) in Telegram Android:
   */
  public static isLeft(chat?: AnyChat | null): boolean {
    if (!chat) return true;
    return Boolean((chat as any).left || (chat as any).isLeft || (chat as any).isMember === false);
  }

  /**
   * Matches ChatObject.canSendMessages(TLRPC.Chat chat) in Telegram Android:
   * In broadcast channels: only admins can post messages.
   * In megagroups: checks default_banned_rights and user banned_rights.
   */
  public static canSendMessages(chat?: AnyChat | null): boolean {
    if (!chat) return false;

    // 1. Broadcast channel check: only administrators can post
    if (this.isBroadcast(chat)) {
      return this.isAdmin(chat);
    }

    // 2. Left / not a member check
    if (this.isLeft(chat)) {
      return false;
    }

    // 3. Default banned rights check (group-wide restrictions)
    const defaultBanned = (chat as any).default_banned_rights || (chat as any).defaultBannedRights;
    if (defaultBanned && defaultBanned.send_messages) {
      return this.isAdmin(chat);
    }

    // 4. User-specific banned rights check (individual restriction)
    const userBanned = (chat as any).banned_rights || (chat as any).bannedRights;
    if (userBanned && userBanned.send_messages) {
      return false;
    }

    // 5. Read-only or restricted flags
    if ((chat as any).isReadOnly) return false;
    if ((chat as any).isRestricted) return false;

    return true;
  }

  /**
   * Matches ChatObject.canSendMedia(TLRPC.Chat chat) in Telegram Android:
   */
  public static canSendMedia(chat?: AnyChat | null): boolean {
    if (!chat) return false;
    if (!this.canSendMessages(chat)) return false;

    const defaultBanned = (chat as any).default_banned_rights || (chat as any).defaultBannedRights;
    if (defaultBanned && defaultBanned.send_media) {
      return this.isAdmin(chat);
    }

    const userBanned = (chat as any).banned_rights || (chat as any).bannedRights;
    if (userBanned && userBanned.send_media) {
      return false;
    }

    return true;
  }

  /**
   * Matches ChatObject.canSendStickers(TLRPC.Chat chat) in Telegram Android:
   */
  public static canSendStickers(chat?: AnyChat | null): boolean {
    if (!chat) return false;
    if (!this.canSendMessages(chat)) return false;

    const defaultBanned = (chat as any).default_banned_rights || (chat as any).defaultBannedRights;
    if (defaultBanned && defaultBanned.send_stickers) {
      return this.isAdmin(chat);
    }

    const userBanned = (chat as any).banned_rights || (chat as any).bannedRights;
    if (userBanned && userBanned.send_stickers) {
      return false;
    }

    return true;
  }

  /**
   * Matches ChatObject.canSendPolls(TLRPC.Chat chat) in Telegram Android:
   */
  public static canSendPolls(chat?: AnyChat | null): boolean {
    if (!chat) return false;
    if (!this.canSendMessages(chat)) return false;

    const defaultBanned = (chat as any).default_banned_rights || (chat as any).defaultBannedRights;
    if (defaultBanned && defaultBanned.send_polls) {
      return this.isAdmin(chat);
    }

    const userBanned = (chat as any).banned_rights || (chat as any).bannedRights;
    if (userBanned && userBanned.send_polls) {
      return false;
    }

    return true;
  }

  /**
   * Matches ChatObject.canSendEmbed(TLRPC.Chat chat) in Telegram Android:
   */
  public static canSendEmbed(chat?: AnyChat | null): boolean {
    if (!chat) return false;
    if (!this.canSendMessages(chat)) return false;

    const defaultBanned = (chat as any).default_banned_rights || (chat as any).defaultBannedRights;
    if (defaultBanned && defaultBanned.embed_links) {
      return this.isAdmin(chat);
    }

    const userBanned = (chat as any).banned_rights || (chat as any).bannedRights;
    if (userBanned && userBanned.embed_links) {
      return false;
    }

    return true;
  }

  /**
   * Matches ChatObject.canPostMessages(TLRPC.Chat chat) in Telegram Android:
   */
  public static canPostMessages(chat?: AnyChat | null): boolean {
    if (!chat) return false;
    if (this.isCreator(chat)) return true;
    const adminRights = (chat as any).admin_rights || (chat as any).adminRights;
    return Boolean(adminRights && adminRights.post_messages);
  }

  /**
   * Matches ChatObject.canPinMessages(TLRPC.Chat chat) in Telegram Android:
   */
  public static canPinMessages(chat?: AnyChat | null): boolean {
    if (!chat) return false;
    if (this.isCreator(chat)) return true;
    const adminRights = (chat as any).admin_rights || (chat as any).adminRights;
    if (adminRights && adminRights.pin_messages) return true;
    const defaultBanned = (chat as any).default_banned_rights || (chat as any).defaultBannedRights;
    if (defaultBanned && defaultBanned.pin_messages) return false;
    return true;
  }

  /**
   * Matches ChatObject.canChangeChatInfo(TLRPC.Chat chat) in Telegram Android:
   */
  public static canChangeChatInfo(chat?: AnyChat | null): boolean {
    if (!chat) return false;
    if (this.isCreator(chat)) return true;
    const adminRights = (chat as any).admin_rights || (chat as any).adminRights;
    if (adminRights && adminRights.change_info) return true;
    const defaultBanned = (chat as any).default_banned_rights || (chat as any).defaultBannedRights;
    if (defaultBanned && defaultBanned.change_info) return false;
    return true;
  }

  /**
   * Matches ChatObject.canInviteUsers(TLRPC.Chat chat) in Telegram Android:
   */
  public static canInviteUsers(chat?: AnyChat | null): boolean {
    if (!chat) return false;
    if (this.isCreator(chat)) return true;
    const adminRights = (chat as any).admin_rights || (chat as any).adminRights;
    if (adminRights && adminRights.invite_users) return true;
    const defaultBanned = (chat as any).default_banned_rights || (chat as any).defaultBannedRights;
    if (defaultBanned && defaultBanned.invite_users) return false;
    return true;
  }

  /**
   * Matches ChatObject.getRestrictedNotice(TLRPC.Chat chat) in Telegram Android:
   */
  public static getRestrictedNotice(
    chat?: AnyChat | null,
    isArabic: boolean = false
  ): { restricted: boolean; message: string } {
    if (!chat) return { restricted: false, message: '' };

    if ((chat as any).isRestricted && (chat as any).restrictionReason) {
      return { restricted: true, message: (chat as any).restrictionReason };
    }

    if (this.isBroadcast(chat) && !this.isAdmin(chat)) {
      return {
        restricted: true,
        message: LocaleController.getString('ChannelBroadcastRestricted'),
      };
    }

    if (this.isMegagroup(chat) && !this.canSendMessages(chat)) {
      return {
        restricted: true,
        message: LocaleController.getString('ChannelRestricted'),
      };
    }

    return { restricted: false, message: '' };
  }
}
