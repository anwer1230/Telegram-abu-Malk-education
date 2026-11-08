/**
 * AdvancedJoiner.ts - Intelligent Multi-Source Telegram Channel & Group Auto-Joiner
 * 1. Parses direct links, invite links, names, and scrapes external web pages
 * 2. Checks already joined chats to prevent duplicate joins
 * 3. Joins with safe delays, handles FloodWait, supports pause, resume, and stop
 */

import { TelegramClient, Api } from 'telegram';
import { TextNormalizer } from './TextNormalizer';

export interface JoinSessionState {
  userId: string;
  total: number;
  joined: number;
  skipped: number;
  failed: number;
  status: 'idle' | 'running' | 'paused' | 'stopped' | 'completed';
  currentLink?: string;
  logs: string[];
}

export class AdvancedJoiner {
  private static activeSessions = new Map<string, {
    state: JoinSessionState;
    queue: string[];
    isPaused: boolean;
    isStopped: boolean;
  }>();

  public static getSessionState(userId: string): JoinSessionState {
    const session = this.activeSessions.get(userId);
    if (session) return session.state;
    return {
      userId,
      total: 0,
      joined: 0,
      skipped: 0,
      failed: 0,
      status: 'idle',
      logs: [],
    };
  }

  /**
   * Scrapes external web pages or parses mixed text to extract all Telegram links
   */
  public static async extractLinksFromMixedSource(rawText: string): Promise<string[]> {
    const discovered = new Set<string>();
    const lines = rawText.split(/[\r\n]+/);

    for (const rawLine of lines) {
      const line = rawLine.trim();
      if (!line) continue;

      // Check if this line is an external web page URL (not telegram)
      if (/^https?:\/\/(?!t\.me|telegram\.me)/i.test(line)) {
        try {
          const controller = new AbortController();
          const timeoutId = setTimeout(() => controller.abort(), 6000);
          const res = await fetch(line, {
            signal: controller.signal,
            headers: { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)' },
          });
          clearTimeout(timeoutId);
          if (res.ok) {
            const html = await res.text();
            // Regex to find t.me links in HTML
            const matches = html.match(/https?:\/\/t\.me\/(?:\+[a-zA-Z0-9_-]+|joinchat\/[a-zA-Z0-9_-]+|[a-zA-Z0-9_]{4,32})/gi);
            if (matches) {
              matches.forEach((m) => discovered.add(m));
            }
          }
        } catch (err) {
          console.warn(`[AdvancedJoiner] Error fetching external URL ${line}:`, err);
        }
      } else {
        // Direct link or username
        const cleaned = TextNormalizer.cleanGroupLinks(line);
        cleaned.forEach((c) => discovered.add(c));
      }
    }

    return Array.from(discovered);
  }

  /**
   * Starts or resumes the automated join flow
   */
  public static async startJoining(
    client: TelegramClient,
    userId: string,
    rawInput: string,
    delaySeconds = 300,
    onProgress?: (state: JoinSessionState) => void
  ) {
    // If already running, return current state
    let session = this.activeSessions.get(userId);
    if (session && session.state.status === 'running') {
      return session.state;
    }

    const links = await this.extractLinksFromMixedSource(rawInput);
    const state: JoinSessionState = {
      userId,
      total: links.length,
      joined: 0,
      skipped: 0,
      failed: 0,
      status: 'running',
      logs: [`بدء معالجة ${links.length} رابط ومصدر للانضمام`],
    };

    session = {
      state,
      queue: [...links],
      isPaused: false,
      isStopped: false,
    };
    this.activeSessions.set(userId, session);

    // Run async execution loop in background
    (async () => {
      // Get list of existing dialogs to skip already joined chats
      const existingPeerIds = new Set<string>();
      try {
        const dialogs = await client.getDialogs({ limit: 100 });
        dialogs.forEach((d) => {
          if (d.entity) {
            if ('username' in d.entity && d.entity.username) {
              existingPeerIds.add(d.entity.username.toLowerCase());
            }
            if ('id' in d.entity) {
              existingPeerIds.add(String(d.entity.id));
            }
          }
        });
      } catch (e) {
        console.warn('[AdvancedJoiner] Could not pre-fetch dialogs:', e);
      }

      for (let i = 0; i < session!.queue.length; i++) {
        if (session!.isStopped) {
          state.status = 'stopped';
          state.logs.push('تم إيقاف عملية الانضمام من قبل المستخدم');
          if (onProgress) onProgress(state);
          break;
        }

        while (session!.isPaused) {
          state.status = 'paused';
          if (onProgress) onProgress(state);
          await new Promise((r) => setTimeout(r, 2000));
          if (session!.isStopped) break;
        }

        const target = session!.queue[i];
        state.currentLink = target;

        try {
          // 1. Check invite hash
          let inviteHash: string | null = null;
          if (target.includes('/+')) {
            inviteHash = target.split('/+')[1]?.replace(/[?#].*$/, '') || null;
          } else if (target.includes('/joinchat/')) {
            inviteHash = target.split('/joinchat/')[1]?.replace(/[?#].*$/, '') || null;
          }

          if (inviteHash) {
            await client.invoke(new Api.messages.ImportChatInvite({ hash: inviteHash }));
            state.joined++;
            state.logs.push(`✅ تم الانضمام بنجاح عبر رابط الدعوة: ${target}`);
          } else {
            // Public username or entity
            const cleanPeer = target.replace(/^https?:\/\/t\.me\//i, '').replace(/^@/, '');

            if (existingPeerIds.has(cleanPeer.toLowerCase())) {
              state.skipped++;
              state.logs.push(`⏭ تخطي: أنت عضو بالفعل في ${cleanPeer}`);
            } else {
              const entity = await client.getEntity(cleanPeer);
              await client.invoke(new Api.channels.JoinChannel({ channel: entity }));
              state.joined++;
              state.logs.push(`✅ تم الانضمام بنجاح إلى: ${cleanPeer}`);
            }
          }
        } catch (err: any) {
          const errMsg = err?.message || err?.errorMessage || String(err);
          if (errMsg.includes('USER_ALREADY_PARTICIPANT')) {
            state.skipped++;
            state.logs.push(`⏭ تخطي (منضم مسبقاً): ${target}`);
          } else if (errMsg.includes('FLOOD_WAIT_')) {
            const waitSec = parseInt(errMsg.replace(/\D/g, ''), 10) || 60;
            state.logs.push(`⏳ قيود تيليجرام (FloodWait): الانتظار ${waitSec} ثانية...`);
            await new Promise((r) => setTimeout(r, (waitSec + 2) * 1000));
            i--; // Retry this target
            continue;
          } else {
            state.failed++;
            state.logs.push(`❌ فشل الانضمام لـ ${target}: ${errMsg}`);
          }
        }

        if (onProgress) onProgress(state);

        // Wait before next join
        if (i < session!.queue.length - 1 && !session!.isStopped) {
          await new Promise((r) => setTimeout(r, delaySeconds * 1000));
        }
      }

      if (!session!.isStopped) {
        state.status = 'completed';
        state.logs.push(`🎉 اكتملت عملية الانضمام: ${state.joined} نجاح، ${state.skipped} مستثنى، ${state.failed} فشل`);
        if (onProgress) onProgress(state);
      }
    })();

    return state;
  }

  public static pauseJoining(userId: string) {
    const session = this.activeSessions.get(userId);
    if (session) {
      session.isPaused = true;
      session.state.status = 'paused';
    }
  }

  public static resumeJoining(userId: string) {
    const session = this.activeSessions.get(userId);
    if (session) {
      session.isPaused = false;
      session.state.status = 'running';
    }
  }

  public static stopJoining(userId: string) {
    const session = this.activeSessions.get(userId);
    if (session) {
      session.isStopped = true;
      session.state.status = 'stopped';
    }
  }
}
