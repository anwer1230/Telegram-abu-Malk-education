/**
 * MonitoringEngine.ts - Account-Wide Keyword & Link Activity Monitor
 * 1. Listens to all incoming messages across all chats on the Telegram account
 * 2. Normalizes Arabic text (removes diacritics, unifies letters)
 * 3. Prevents duplicate alerts via seen-messages LRU cache
 * 4. Dispatches 3 parallel alert channels:
 *    - Socket.IO to connected web client
 *    - Detailed formatted Telegram card to "Saved Messages" ('me')
 *    - Web Notification trigger
 */

import { TelegramClient } from 'telegram';
import { NewMessage } from 'telegram/events';
import { TextNormalizer } from './TextNormalizer';
import { KeywordAlert } from './types';
import { StorageManager } from './StorageManager';

export class MonitoringEngine {
  private static activeMonitors = new Map<string, {
    client: TelegramClient;
    handler: (event: any) => Promise<void>;
    keywords: string[];
    seenMessageIds: Set<string>;
  }>();

  private static socketEmitter: ((event: string, data: any) => void) | null = null;

  public static setSocketEmitter(emitter: (event: string, data: any) => void) {
    this.socketEmitter = emitter;
  }

  public static isMonitoring(userId: string): boolean {
    return this.activeMonitors.has(userId);
  }

  public static getKeywords(userId: string): string[] {
    const monitor = this.activeMonitors.get(userId);
    return monitor ? monitor.keywords : StorageManager.loadConfig(userId).keywords;
  }

  public static updateKeywords(userId: string, keywords: string[]) {
    const monitor = this.activeMonitors.get(userId);
    if (monitor) {
      monitor.keywords = keywords.map((k) => k.trim()).filter(Boolean);
    }
    StorageManager.saveConfig(userId, { keywords });
  }

  public static async startMonitoring(userId: string, client: TelegramClient, keywords?: string[]) {
    if (this.activeMonitors.has(userId)) {
      await this.stopMonitoring(userId);
    }

    const config = StorageManager.loadConfig(userId);
    const activeKeywords = (keywords && keywords.length > 0)
      ? keywords.map((k) => k.trim()).filter(Boolean)
      : config.keywords.map((k) => k.trim()).filter(Boolean);

    StorageManager.saveConfig(userId, {
      isMonitoring: true,
      keywords: activeKeywords,
    });

    const seenMessageIds = new Set<string>();

    const handler = async (event: any) => {
      try {
        const message = event.message;
        if (!message || !message.text) return;

        const msgKey = `${message.chatId || message.peerId}_${message.id}`;
        if (seenMessageIds.has(msgKey)) return;
        seenMessageIds.add(msgKey);

        // Keep set bounded to 5,000 entries
        if (seenMessageIds.size > 5000) {
          const first = seenMessageIds.values().next().value;
          if (first) seenMessageIds.delete(first);
        }

        const rawText = message.text;

        // Auto Reply Check (الردود التلقائية)
        try {
          const autoReplyData = StorageManager.loadAutoReplyRules(userId);
          if (autoReplyData.enabled && autoReplyData.rules.length > 0) {
            const isPrivate = Boolean(message.isPrivate);
            for (const rule of autoReplyData.rules) {
              if (!rule.isEnabled || !rule.keyword || !rule.replyText) continue;
              if (rule.scope === 'private' && !isPrivate) continue;
              if (rule.scope === 'groups' && isPrivate) continue;

              let isMatched = false;
              if (rule.matchType === 'exact') {
                isMatched = rawText.trim().toLowerCase() === rule.keyword.trim().toLowerCase();
              } else if (rule.matchType === 'regex') {
                try {
                  isMatched = new RegExp(rule.keyword, 'i').test(rawText);
                } catch (_) {}
              } else {
                isMatched = TextNormalizer.matchKeyword(rawText, rule.keyword);
              }

              if (isMatched) {
                await message.reply({ message: rule.replyText });
                rule.timesTriggered = (rule.timesTriggered || 0) + 1;
                rule.lastUsed = new Date().toISOString();
                StorageManager.saveAutoReplyRules(userId, { rules: autoReplyData.rules });
                break;
              }
            }
          }
        } catch (autoErr) {
          console.warn('[MonitoringEngine] Auto reply evaluation error:', autoErr);
        }

        const currentKeywords = this.getKeywords(userId);
        if (currentKeywords.length === 0) return;

        // Match against normalized text
        let matchedKeyword: string | null = null;
        for (const kw of currentKeywords) {
          if (TextNormalizer.matchKeyword(rawText, kw)) {
            matchedKeyword = kw;
            break;
          }
        }

        if (!matchedKeyword) return;

        // Extract chat & sender metadata
        let chatTitle = 'محادثة تيليجرام';
        try {
          const chatEntity = await message.getChat();
          if (chatEntity && 'title' in chatEntity) {
            chatTitle = chatEntity.title;
          } else if (chatEntity && 'firstName' in chatEntity) {
            chatTitle = [chatEntity.firstName, chatEntity.lastName].filter(Boolean).join(' ');
          }
        } catch (_) {}

        let senderName = 'عضو';
        let senderUsername: string | undefined;
        try {
          const senderEntity = await message.getSender();
          if (senderEntity) {
            if ('firstName' in senderEntity) {
              senderName = [senderEntity.firstName, senderEntity.lastName].filter(Boolean).join(' ') || 'مستخدم';
            }
            if ('username' in senderEntity && senderEntity.username) {
              senderUsername = senderEntity.username;
            }
          }
        } catch (_) {}

        const alert: KeywordAlert = {
          id: `alert_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`,
          userId,
          keyword: matchedKeyword,
          chatTitle,
          chatId: String(message.chatId || message.peerId || ''),
          senderName,
          senderUsername,
          senderId: String(message.senderId || ''),
          timestamp: new Date().toLocaleTimeString('ar-SA'),
          text: rawText,
        };

        console.log(`[MonitoringEngine] 🎯 Keyword matched: "${matchedKeyword}" in "${chatTitle}" by "${senderName}"`);

        // Parallel Alert Channel 1: Web Interface Socket
        if (this.socketEmitter) {
          this.socketEmitter('keyword_alert', alert);
        }

        // Parallel Alert Channel 2: Telegram Saved Messages ('me')
        const telegramCard =
          `🚨 **تنبيه رصد كلمة مفتاحية: [ ${matchedKeyword} ]**\n\n` +
          `📍 **المجموعة / القناة:** ${chatTitle}\n` +
          `👤 **المرسل:** ${senderName}${senderUsername ? ` (@${senderUsername})` : ''}\n` +
          `🕒 **التوقيت:** ${alert.timestamp}\n\n` +
          `📝 **نص الرسالة المرصودة:**\n` +
          `"${rawText.length > 500 ? rawText.slice(0, 500) + '...' : rawText}"`;

        try {
          await client.sendMessage('me', {
            message: telegramCard,
            parseMode: 'md',
          });
        } catch (tgErr) {
          console.warn('[MonitoringEngine] Failed to dispatch alert card to Saved Messages:', tgErr);
        }
      } catch (err) {
        console.warn('[MonitoringEngine] Handler error:', err);
      }
    };

    client.addEventHandler(handler, new NewMessage({}));

    this.activeMonitors.set(userId, {
      client,
      handler,
      keywords: activeKeywords,
      seenMessageIds,
    });

    console.log(`[MonitoringEngine] ✅ Started monitoring for user ${userId} with ${activeKeywords.length} keywords.`);
  }

  public static async stopMonitoring(userId: string) {
    const monitor = this.activeMonitors.get(userId);
    if (monitor) {
      try {
        monitor.client.removeEventHandler(monitor.handler, new NewMessage({}));
      } catch (e) {
        console.warn('[MonitoringEngine] Error removing event handler:', e);
      }
      this.activeMonitors.delete(userId);
    }
    StorageManager.saveConfig(userId, { isMonitoring: false });
    console.log(`[MonitoringEngine] ⏹ Stopped monitoring for user ${userId}.`);
  }
}
