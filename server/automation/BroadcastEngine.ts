/**
 * BroadcastEngine.ts - Advanced MTProto Telegram Broadcast & Automation Engine
 * Supports:
 * - Instant (Manual) Dispatch
 * - Scheduled Interval Dispatch (with countdown heartbeats)
 * - Sequential Cyclic Dispatch
 * - 3-Phase Group Processing (Membership, Bot Protection, Decision)
 * - "Salam Alaykum" intelligent greeting & edit-after-activity mode
 * - Temporary image upload & immediate purge
 * - Telegram Saved Messages comprehensive report dispatch
 */

import fs from 'fs';
import path from 'path';
import os from 'os';
import crypto from 'crypto';
import { TelegramClient, Api } from 'telegram';
import { TextNormalizer } from './TextNormalizer';
import { StorageManager } from './StorageManager';
import { AutomationConfig, BatchReport, PreCheckItem, ProtectionMode } from './types';

// Known Telegram protection & moderation bots
const KNOWN_PROTECTION_BOTS = [
  'rose',
  'missrose_bot',
  'grouphelp',
  'grouphelpbot',
  'shieldy',
  'shieldy_bot',
  'combot',
  'cleanerbot',
  'anti_spam',
  'antispambot',
  'controllerbot',
  'protect',
  'guard',
];

export class BroadcastEngine {
  private static activeJobs = new Map<string, {
    config: AutomationConfig;
    client: TelegramClient;
    intervalTimer?: NodeJS.Timeout;
    heartbeatTimer?: NodeJS.Timeout;
    isCancelled: boolean;
  }>();

  private static socketEmitter: ((event: string, data: any) => void) | null = null;

  public static setSocketEmitter(emitter: (event: string, data: any) => void) {
    this.socketEmitter = emitter;
  }

  public static isDispatching(userId: string): boolean {
    return this.activeJobs.has(userId);
  }

  /**
   * Pre-checks a list of groups to analyze membership and protection bots
   */
  public static async preCheckGroups(client: TelegramClient, rawInputs: string[]): Promise<PreCheckItem[]> {
    const cleanedTargets = TextNormalizer.cleanGroupLinks(rawInputs);
    const results: PreCheckItem[] = [];

    for (const target of cleanedTargets) {
      const item: PreCheckItem = {
        rawInput: target,
        normalizedPeer: target,
        title: target,
        isMember: false,
        isChannel: false,
        isProtected: false,
        chosenMode: 'salam',
        status: 'valid',
      };

      try {
        let cleanPeer = target.replace(/^https?:\/\/t\.me\//i, '').replace(/^@/, '');
        if (cleanPeer.includes('/+')) {
          cleanPeer = cleanPeer.split('/+')[1];
        }

        const entity = await client.getEntity(cleanPeer);
        if (entity) {
          if ('title' in entity) item.title = (entity as any).title;
          if ('broadcast' in entity && (entity as any).broadcast) item.isChannel = true;

          // Check membership
          try {
            const me = await client.getMe();
            const participant = await client.invoke(
              new Api.channels.GetParticipant({
                channel: entity,
                participant: me,
              })
            );
            if (participant) {
              item.isMember = true;
            }
          } catch (_) {
            item.isMember = false;
            item.status = 'not_member';
          }

          // Check protection bots
          try {
            const participants = await client.getParticipants(entity, { limit: 50 });
            for (const p of participants) {
              if (p.bot) {
                const botUsername = (p.username || '').toLowerCase();
                const matchedBot = KNOWN_PROTECTION_BOTS.find((b) => botUsername.includes(b));
                if (matchedBot) {
                  item.isProtected = true;
                  item.protectionBotName = `@${p.username}`;
                  item.status = 'protected';
                  break;
                }
              }
            }
          } catch (_) {}
        }
      } catch (err: any) {
        item.status = 'invalid';
        item.error = err?.message || 'تعذر جلب تفاصيل المجموعة';
      }

      results.push(item);
    }

    return results;
  }

  /**
   * Executes a single broadcast batch
   */
  public static async executeBatch(
    userId: string,
    client: TelegramClient,
    config: AutomationConfig,
    batchMessageText: string
  ): Promise<BatchReport> {
    const batchId = `batch_${Date.now()}_${crypto.randomBytes(3).toString('hex')}`;
    const missingMembershipGroups: string[] = [];

    // 1. Resolve targets
    let targets: string[] = [];
    if (config.sendToAllGroups) {
      try {
        const dialogs = await client.getDialogs({ limit: 100 });
        targets = dialogs
          .filter((d) => d.isGroup || d.isChannel)
          .map((d) => String(d.id));
      } catch (e) {
        console.warn('[BroadcastEngine] Error fetching all groups:', e);
      }
    } else {
      targets = TextNormalizer.cleanGroupLinks(config.groups);
    }

    const report: BatchReport = {
      batchId,
      userId,
      timestamp: new Date().toLocaleTimeString('ar-SA'),
      totalGroups: targets.length,
      successCount: 0,
      failCount: 0,
      skippedCount: 0,
      details: [],
    };

    console.log(`[BroadcastEngine] 🚀 Starting Batch ${batchId} to ${targets.length} groups for user ${userId}`);

    // Temporary image file handling
    const tempImagePaths: string[] = [];
    if (config.images && config.images.length > 0) {
      for (let i = 0; i < config.images.length; i++) {
        const imgData = config.images[i];
        if (imgData.startsWith('data:image/')) {
          try {
            const matches = imgData.match(/^data:image\/([a-zA-Z0-9]+);base64,(.+)$/);
            if (matches) {
              const ext = matches[1] || 'jpg';
              const buffer = Buffer.from(matches[2], 'base64');
              const tempFilePath = path.join(os.tmpdir(), `tg_broadcast_${Date.now()}_${i}.${ext}`);
              fs.writeFileSync(tempFilePath, buffer);
              tempImagePaths.push(tempFilePath);
            }
          } catch (e) {
            console.warn('[BroadcastEngine] Error preparing temp image:', e);
          }
        }
      }
    }

    // Process each target sequentially with safety delay
    for (let i = 0; i < targets.length; i++) {
      const target = targets[i];
      let groupTitle = target;
      let appliedMode = config.protectionMode;

      try {
        // Resolve entity
        let cleanPeer = target.replace(/^https?:\/\/t\.me\//i, '').replace(/^@/, '');
        let entity: any = null;
        try {
          entity = await client.getEntity(cleanPeer);
          if (entity && 'title' in entity) {
            groupTitle = entity.title;
          }
        } catch (_) {
          // Keep cleanPeer
        }

        // ============================================
        // PHASE 1: Membership Check (فحص العضوية)
        // ============================================
        let isMember = false;
        if (entity) {
          try {
            const me = await client.getMe();
            const p = await client.invoke(
              new Api.channels.GetParticipant({
                channel: entity,
                participant: me,
              })
            );
            if (p) isMember = true;
          } catch (_) {
            isMember = false;
          }
        }

        if (!isMember && entity) {
          missingMembershipGroups.push(`- ${groupTitle} (${target})`);
          report.skippedCount++;
          report.details.push({
            target,
            title: groupTitle,
            status: 'skipped',
            modeApplied: appliedMode,
            note: 'المستخدم ليس عضواً في المجموعة (تم التخطي وتنبيهه في الرسائل المحفوظة)',
          });
          continue;
        }

        // ============================================
        // PHASE 2: Protection Bots Check (فحص الحماية)
        // ============================================
        let isProtected = false;
        let detectedBotName = '';
        if (entity) {
          try {
            const participants = await client.getParticipants(entity, { limit: 40 });
            for (const p of participants) {
              if (p.bot) {
                const u = (p.username || '').toLowerCase();
                const matched = KNOWN_PROTECTION_BOTS.find((bot) => u.includes(bot));
                if (matched) {
                  isProtected = true;
                  detectedBotName = `@${p.username}`;
                  break;
                }
              }
            }
          } catch (_) {}
        }

        // ============================================
        // PHASE 3: Decision & Adaptive Dispatch (اتخاذ القرار)
        // ============================================
        if (isProtected && appliedMode === 'skip') {
          report.skippedCount++;
          report.details.push({
            target,
            title: groupTitle,
            status: 'skipped',
            modeApplied: 'skip',
            note: `مجموعة محمية بواسطة ${detectedBotName} (تم التخطي تلقائياً)`,
          });
          continue;
        }

        let finalMessage = batchMessageText;

        if (isProtected || appliedMode === 'smart') {
          appliedMode = 'smart';
          finalMessage = TextNormalizer.sanitizeSmartMessage(batchMessageText);
        } else if (appliedMode === 'convert_links') {
          finalMessage = TextNormalizer.convertWhatsAppLinks(batchMessageText);
        }

        // Handle Salam Mode: Send Salam, wait for members' chatter, then edit
        if (appliedMode === 'salam') {
          const salamMsg = await client.sendMessage(entity || target, {
            message: 'السلام عليكم ورحمة الله وبركاته',
          });

          // Wait asynchronously for group activity up to requiredMemberMessages
          const requiredCount = config.requiredMemberMessages || 5;
          let memberChatterCount = 0;

          // Poll for 30 seconds max to see if members speak
          for (let sec = 0; sec < 15; sec++) {
            await new Promise((r) => setTimeout(r, 2000));
            try {
              const recentMsgs = await client.getMessages(entity || target, { limit: 8 });
              const otherMemberMsgs = recentMsgs.filter((m) => m.id > salamMsg.id && !m.out);
              if (otherMemberMsgs.length >= requiredCount) {
                memberChatterCount = otherMemberMsgs.length;
                break;
              }
            } catch (_) {}
          }

          if (memberChatterCount >= requiredCount) {
            // Activity threshold met: Edit Salam into full message!
            await client.editMessage(entity || target, {
              message: salamMsg.id,
              text: finalMessage,
            });
            report.successCount++;
            report.details.push({
              target,
              title: groupTitle,
              status: 'success',
              modeApplied: 'salam',
              note: `تم إرسال السلام واستبداله بعد تفاعل ${memberChatterCount} أعضاء`,
            });
          } else {
            // Timeout or low activity: update directly or fallback safely
            await client.editMessage(entity || target, {
              message: salamMsg.id,
              text: finalMessage,
            });
            report.successCount++;
            report.details.push({
              target,
              title: groupTitle,
              status: 'success',
              modeApplied: 'salam',
              note: 'تم إرسال الرسالة وتحديث التحية',
            });
          }
        } else {
          // Direct Dispatch with media if available
          if (tempImagePaths.length > 0) {
            await client.sendFile(entity || target, {
              file: tempImagePaths[0],
              caption: finalMessage,
            });
          } else {
            await client.sendMessage(entity || target, {
              message: finalMessage,
            });
          }

          report.successCount++;
          report.details.push({
            target,
            title: groupTitle,
            status: 'success',
            modeApplied: appliedMode,
          });
        }

        // Emit live progress to UI
        if (this.socketEmitter) {
          this.socketEmitter('dispatch_progress', {
            batchId,
            current: i + 1,
            total: targets.length,
            groupTitle,
            status: 'success',
          });
        }
      } catch (err: any) {
        const errMsg = err?.message || err?.errorMessage || String(err);
        report.failCount++;
        report.details.push({
          target,
          title: groupTitle,
          status: 'failed',
          modeApplied: appliedMode,
          note: errMsg,
        });

        if (this.socketEmitter) {
          this.socketEmitter('dispatch_progress', {
            batchId,
            current: i + 1,
            total: targets.length,
            groupTitle,
            status: 'failed',
            error: errMsg,
          });
        }
      }

      // Safe delay between groups (3 seconds) to prevent flood
      if (i < targets.length - 1) {
        await new Promise((r) => setTimeout(r, 3000));
      }
    }

    // Clean up temporary image files
    for (const tempPath of tempImagePaths) {
      try {
        if (fs.existsSync(tempPath)) fs.unlinkSync(tempPath);
      } catch (_) {}
    }

    // ============================================
    // Notify Missing Membership in Saved Messages
    // ============================================
    if (missingMembershipGroups.length > 0) {
      const missingCard =
        `⚠️ **تنبيه: مجموعات تحتاج إلى انضمامك اليدوي**\n\n` +
        `أثناء تنفيذ دفعة الإرسال (${batchId})، تبين أنك غير منضم للمجموعات التالية:\n` +
        missingMembershipGroups.join('\n') +
        `\n\n💡 _النظام احترم أمان حسابك ولم يقم بالانضمام التلقائي._`;
      try {
        await client.sendMessage('me', { message: missingCard, parseMode: 'md' });
      } catch (_) {}
    }

    // ============================================
    // Comprehensive Batch Report in Saved Messages
    // ============================================
    const reportCard =
      `📊 **تقرير إرسال الدفعة [ ${batchId} ]**\n\n` +
      `🕒 **التوقيت:** ${report.timestamp}\n` +
      `🎯 **إجمالي المجموعات:** ${report.totalGroups}\n` +
      `✅ **ناجح:** ${report.successCount}\n` +
      `⏭ **مستثنى / متخطى:** ${report.skippedCount}\n` +
      `❌ **فاشل:** ${report.failCount}\n\n` +
      `📋 **ملاحظات الدفعة:**\n` +
      report.details
        .slice(0, 15)
        .map((d) => `• ${d.title}: ${d.status === 'success' ? '✅' : d.status === 'skipped' ? '⏭' : '❌'} ${d.note ? `(${d.note})` : ''}`)
        .join('\n') +
      (report.details.length > 15 ? `\n... و ${report.details.length - 15} مجموعة أخرى.` : '');

    try {
      await client.sendMessage('me', { message: reportCard, parseMode: 'md' });
    } catch (_) {}

    // Emit batch report to connected web sockets
    if (this.socketEmitter) {
      this.socketEmitter('batch_report', report);
    }

    // Update config persistence
    StorageManager.saveConfig(userId, {
      lastDispatchedAt: Date.now(),
    });

    return report;
  }

  /**
   * Starts a continuous scheduled or sequential automation job
   */
  public static async startDispatchJob(userId: string, client: TelegramClient, config: AutomationConfig) {
    if (this.activeJobs.has(userId)) {
      this.stopDispatchJob(userId);
    }

    const updatedConfig = StorageManager.saveConfig(userId, {
      ...config,
      isDispatching: true,
      startedAt: Date.now(),
    });

    const job = {
      config: updatedConfig,
      client,
      isCancelled: false,
      intervalTimer: undefined as NodeJS.Timeout | undefined,
      heartbeatTimer: undefined as NodeJS.Timeout | undefined,
    };
    this.activeJobs.set(userId, job);

    console.log(`[BroadcastEngine] ⏱ Started continuous ${updatedConfig.dispatchType} job for user ${userId}`);

    // Initial batch execution
    const runBatch = async () => {
      if (job.isCancelled) return;

      // Check max run duration in hours
      if (job.config.totalHours > 0) {
        const elapsedHours = (Date.now() - job.config.startedAt) / (1000 * 60 * 60);
        if (elapsedHours >= job.config.totalHours) {
          console.log(`[BroadcastEngine] 🏁 Total duration (${job.config.totalHours}h) reached for ${userId}. Stopping...`);
          try {
            await client.sendMessage('me', {
              message: `⏰ **انتهت مدة التشغيل الكلية المحددة (${job.config.totalHours} ساعة).**\nتم إيقاف الإرسال التلقائي بنجاح. يمكنك استئنافه من لوحة التحكم.`,
              parseMode: 'md',
            });
          } catch (_) {}
          this.stopDispatchJob(userId);
          return;
        }
      }

      // Determine message content
      let textToSend = job.config.messageText;
      if (job.config.dispatchType === 'sequential' && job.config.sequentialMessages.length > 0) {
        const idx = job.config.currentSequentialIndex % job.config.sequentialMessages.length;
        textToSend = job.config.sequentialMessages[idx];
        // Advance cycle
        job.config.currentSequentialIndex = (idx + 1) % job.config.sequentialMessages.length;
        StorageManager.saveConfig(userId, { currentSequentialIndex: job.config.currentSequentialIndex });
      }

      await this.executeBatch(userId, client, job.config, textToSend);
    };

    // Execute right away
    runBatch();

    // Schedule next batches
    const intervalMs = Math.max(1, job.config.intervalMinutes) * 60 * 1000;
    job.intervalTimer = setInterval(runBatch, intervalMs);

    // Heartbeat ticker for UI countdown (every 5 seconds)
    job.heartbeatTimer = setInterval(() => {
      if (this.socketEmitter && !job.isCancelled) {
        const nextRunAt = job.config.lastDispatchedAt ? job.config.lastDispatchedAt + intervalMs : Date.now() + intervalMs;
        const remainingSeconds = Math.max(0, Math.floor((nextRunAt - Date.now()) / 1000));
        this.socketEmitter('countdown_tick', {
          userId,
          remainingSeconds,
          dispatchType: job.config.dispatchType,
          currentSequentialIndex: job.config.currentSequentialIndex,
        });
      }
    }, 5000);
  }

  public static stopDispatchJob(userId: string) {
    const job = this.activeJobs.get(userId);
    if (job) {
      job.isCancelled = true;
      if (job.intervalTimer) clearInterval(job.intervalTimer);
      if (job.heartbeatTimer) clearInterval(job.heartbeatTimer);
      this.activeJobs.delete(userId);
    }
    StorageManager.saveConfig(userId, { isDispatching: false });
    console.log(`[BroadcastEngine] ⏹ Stopped dispatch job for user ${userId}`);
  }
}
