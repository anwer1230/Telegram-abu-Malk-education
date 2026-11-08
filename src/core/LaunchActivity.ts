/**
 * LaunchActivity.ts - Official DrKLO/Telegram Android Deep Link & Intent Router
 * Replicated from org.telegram.ui.LaunchActivity.java
 *
 * Implements full Android intent-filter parsing for:
 * - tg://join?invite=hash
 * - tg://resolve?domain=username
 * - tg://openmessage?user_id=...
 * - tg://privatepost?channel=...&post=...
 * - tg://proxy?server=...&port=...
 * - tg://settings
 * - https://t.me/+hash & https://t.me/joinchat/hash
 * - https://t.me/c/{chatId}/{messageId}
 * - https://t.me/{username}
 * - telegram.me, telegram.dog, graph.org
 * - WhatsApp cross-link discovery (wa.me, chat.whatsapp.com)
 */

import { MessagesController } from './MessagesController';
import { NotificationCenter } from './NotificationCenter';
import { TLRPC } from './TLRPC';

export interface ParsedTelegramUri {
  scheme: string;
  host: string;
  path: string;
  query: Record<string, string>;
  type:
    | 'join'
    | 'resolve'
    | 'openmessage'
    | 'privatepost'
    | 'proxy'
    | 'settings'
    | 'channel_post'
    | 'whatsapp'
    | 'unknown';
  inviteHash?: string;
  username?: string;
  channelId?: string;
  postId?: string;
  userId?: string;
  rawUrl: string;
}

export class LaunchActivity {
  private static instances = new Map<number, LaunchActivity>();
  private currentAccount: number = 0;
  private isInitialized: boolean = false;

  public static getInstance(account: number = 0): LaunchActivity {
    if (!LaunchActivity.instances.has(account)) {
      LaunchActivity.instances.set(account, new LaunchActivity(account));
    }
    return LaunchActivity.instances.get(account)!;
  }

  private constructor(account: number = 0) {
    this.currentAccount = account;
    this.initIntentFilters();
  }

  /**
   * Initializes browser-level intent filter listeners equivalent to AndroidManifest.xml
   */
  public initIntentFilters(): void {
    if (this.isInitialized || typeof window === 'undefined') return;
    this.isInitialized = true;

    // Listen for custom tg-handle-link and tg-intent events
    window.addEventListener('tg-handle-link' as any, (e: CustomEvent<string>) => {
      if (e.detail) {
        this.handleIntent(e.detail);
      }
    });

    window.addEventListener('hashchange', () => {
      if (window.location.hash) {
        const hash = window.location.hash.replace(/^#/, '');
        if (hash.startsWith('tg=') || hash.startsWith('t.me/') || hash.startsWith('tg://')) {
          const target = hash.startsWith('tg=') ? decodeURIComponent(hash.slice(3)) : hash;
          this.handleIntent(target);
        }
      }
    });

    // Check initial search or hash param on boot
    try {
      const searchParams = new URLSearchParams(window.location.search);
      const tgParam = searchParams.get('tg') || searchParams.get('link') || searchParams.get('join');
      if (tgParam) {
        setTimeout(() => this.handleIntent(tgParam), 500);
      }
    } catch (e) {
      console.warn('[LaunchActivity] Boot check error:', e);
    }
  }

  /**
   * Parses raw URI into structured Telegram Intent data
   */
  public parseUri(raw: string): ParsedTelegramUri {
    const clean = raw.trim();
    let scheme = '';
    let host = '';
    let path = '';
    const query: Record<string, string> = {};

    // Standard tg:// custom scheme
    if (clean.startsWith('tg://')) {
      scheme = 'tg';
      const parts = clean.slice(5).split('?');
      host = parts[0] || '';
      path = parts[0] || '';
      if (parts[1]) {
        const params = new URLSearchParams(parts[1]);
        params.forEach((val, key) => {
          query[key] = val;
        });
      }

      if (host === 'join' || host.startsWith('join')) {
        return {
          scheme,
          host,
          path,
          query,
          type: 'join',
          inviteHash: query.invite || query.hash || '',
          rawUrl: clean,
        };
      }

      if (host === 'resolve' || host.startsWith('resolve')) {
        return {
          scheme,
          host,
          path,
          query,
          type: 'resolve',
          username: query.domain || '',
          rawUrl: clean,
        };
      }

      if (host === 'openmessage') {
        return {
          scheme,
          host,
          path,
          query,
          type: 'openmessage',
          userId: query.user_id,
          rawUrl: clean,
        };
      }

      if (host === 'privatepost') {
        return {
          scheme,
          host,
          path,
          query,
          type: 'privatepost',
          channelId: query.channel,
          postId: query.post,
          rawUrl: clean,
        };
      }

      if (host === 'proxy') {
        return {
          scheme,
          host,
          path,
          query,
          type: 'proxy',
          rawUrl: clean,
        };
      }

      if (host === 'settings') {
        return {
          scheme,
          host,
          path,
          query,
          type: 'settings',
          rawUrl: clean,
        };
      }
    }

    // HTTP(S) URLs: t.me, telegram.me, telegram.dog, graph.org
    const isTelegramHttp =
      clean.includes('t.me/') ||
      clean.includes('telegram.me/') ||
      clean.includes('telegram.dog/') ||
      clean.includes('graph.org/');

    if (isTelegramHttp) {
      scheme = 'https';
      // Match t.me/joinchat/hash or t.me/+hash
      const joinMatch = clean.match(/(?:t\.me|telegram\.me|telegram\.dog)\/(?:joinchat\/|\+)([a-zA-Z0-9_-]+)/i);
      if (joinMatch) {
        return {
          scheme,
          host: 't.me',
          path: joinMatch[0],
          query: {},
          type: 'join',
          inviteHash: joinMatch[1],
          rawUrl: clean,
        };
      }

      // Match t.me/c/123456789/123
      const channelPostMatch = clean.match(/(?:t\.me|telegram\.me|telegram\.dog)\/c\/(\d+)\/(\d+)/i);
      if (channelPostMatch) {
        return {
          scheme,
          host: 't.me',
          path: clean,
          query: {},
          type: 'channel_post',
          channelId: channelPostMatch[1],
          postId: channelPostMatch[2],
          rawUrl: clean,
        };
      }

      // Match username or username/postId: t.me/mychannel or t.me/mychannel/45
      const usernameMatch = clean.match(/(?:t\.me|telegram\.me|telegram\.dog)\/([a-zA-Z0-9_]{3,32})(?:\/(\d+))?/i);
      if (usernameMatch) {
        const uname = usernameMatch[1];
        if (uname.toLowerCase() !== 'joinchat' && uname.toLowerCase() !== 'c') {
          return {
            scheme,
            host: 't.me',
            path: clean,
            query: {},
            type: usernameMatch[2] ? 'channel_post' : 'resolve',
            username: uname,
            postId: usernameMatch[2],
            rawUrl: clean,
          };
        }
      }
    }

    // WhatsApp detection
    if (clean.includes('wa.me/') || clean.includes('chat.whatsapp.com/')) {
      return {
        scheme: 'https',
        host: 'whatsapp',
        path: clean,
        query: {},
        type: 'whatsapp',
        rawUrl: clean,
      };
    }

    return {
      scheme: scheme || 'unknown',
      host,
      path,
      query,
      type: 'unknown',
      rawUrl: clean,
    };
  }

  /**
   * Primary intent handler replicated directly from LaunchActivity.handleIntent
   */
  public async handleIntent(
    intentOrUri: string | { data?: string; action?: string },
    isNew: boolean = false
  ): Promise<boolean> {
    const raw = typeof intentOrUri === 'string' ? intentOrUri : intentOrUri?.data || '';
    if (!raw) return false;

    const parsed = this.parseUri(raw);
    const messagesCtrl = MessagesController.getInstance(this.currentAccount);

    switch (parsed.type) {
      case 'join': {
        const hash = parsed.inviteHash;
        if (!hash) return false;

        try {
          // Check invite with MTProto RPC
          const invite = await messagesCtrl.checkChatInvite(hash);

          // Dispatch preview event for UI (ChatActivity preview screen + Blue Join Button)
          if (typeof window !== 'undefined') {
            window.dispatchEvent(
              new CustomEvent('tg-open-chat-preview', {
                detail: {
                  invite,
                  hash,
                  account: this.currentAccount,
                },
              })
            );
          }
          return true;
        } catch (e) {
          console.warn('[LaunchActivity] handleIntent join error:', e);
          return false;
        }
      }

      case 'resolve': {
        if (parsed.username) {
          messagesCtrl.openByUserName(parsed.username);
          return true;
        }
        return false;
      }

      case 'channel_post': {
        messagesCtrl.openByLink(parsed.rawUrl);
        return true;
      }

      case 'openmessage': {
        if (parsed.userId) {
          messagesCtrl.openByUserName(parsed.userId);
          return true;
        }
        return false;
      }

      case 'settings': {
        NotificationCenter.getInstance(this.currentAccount).postNotificationName(
          NotificationCenter.updateInterfaces,
          NotificationCenter.UPDATE_MASK_ALL
        );
        if (typeof window !== 'undefined') {
          window.dispatchEvent(new CustomEvent('tg-open-settings'));
        }
        return true;
      }

      case 'whatsapp': {
        if (typeof window !== 'undefined') {
          window.dispatchEvent(
            new CustomEvent('tg-whatsapp-link-captured', {
              detail: { url: parsed.rawUrl },
            })
          );
        }
        return true;
      }

      default: {
        // Fallback: check if it's a raw hash or username
        const trimmed = raw.trim();
        if (/^[a-zA-Z0-9_-]{10,}$/.test(trimmed)) {
          return this.handleIntent(`tg://join?invite=${trimmed}`, isNew);
        }
        if (/^@[a-zA-Z0-9_]{3,}$/.test(trimmed)) {
          return this.handleIntent(`tg://resolve?domain=${trimmed.slice(1)}`, isNew);
        }
        return false;
      }
    }
  }
}

export const launchActivity = LaunchActivity.getInstance();
