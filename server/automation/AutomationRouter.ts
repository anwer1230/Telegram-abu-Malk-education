/**
 * AutomationRouter.ts - REST and Socket Endpoints for Broadcast & Monitoring
 */

import { Router, Request, Response } from 'express';
import { Server as SocketIOServer } from 'socket.io';
import { TelegramClient } from 'telegram';
import { StorageManager } from './StorageManager';
import { TextNormalizer } from './TextNormalizer';
import { MonitoringEngine } from './MonitoringEngine';
import { BroadcastEngine } from './BroadcastEngine';
import { AdvancedJoiner } from './AdvancedJoiner';
import { AutomationConfig } from './types';

export function createAutomationRouter(
  io: SocketIOServer,
  getClientForSession: (sessionString?: string, phone?: string) => Promise<TelegramClient | null>
): Router {
  const router = Router();

  // Connect engine socket emitters
  const broadcastEmitter = (event: string, data: any) => {
    io.emit(event, data);
  };
  BroadcastEngine.setSocketEmitter(broadcastEmitter);
  MonitoringEngine.setSocketEmitter(broadcastEmitter);

  // Helper to resolve client
  const resolveClient = async (req: Request): Promise<{ client: TelegramClient | null; userId: string }> => {
    const sessionString = (req.headers['x-telegram-session'] as string) || (req.body?.sessionString as string) || '';
    const phone = (req.headers['x-telegram-phone'] as string) || (req.body?.phone as string) || '';
    const customUserId = (req.headers['x-user-id'] as string) || (req.body?.userId as string) || phone || 'default_user';

    const client = await getClientForSession(sessionString, phone);
    return { client, userId: customUserId };
  };

  // 1. Get Configuration
  router.get('/config', async (req: Request, res: Response) => {
    try {
      const userId = (req.query.userId as string) || (req.headers['x-user-id'] as string) || 'default_user';
      const config = StorageManager.loadConfig(userId);
      const isMonitoring = MonitoringEngine.isMonitoring(userId);
      const isDispatching = BroadcastEngine.isDispatching(userId);
      return res.json({
        ok: true,
        config: {
          ...config,
          isMonitoring,
          isDispatching,
        },
      });
    } catch (e: any) {
      return res.status(500).json({ ok: false, error: e.message });
    }
  });

  // 2. Save Configuration
  router.post('/config', async (req: Request, res: Response) => {
    try {
      const { userId = 'default_user', ...settings } = req.body;
      const updated = StorageManager.saveConfig(userId, settings);

      // If keywords updated while monitoring, update live
      if (settings.keywords && MonitoringEngine.isMonitoring(userId)) {
        MonitoringEngine.updateKeywords(userId, settings.keywords);
      }

      return res.json({ ok: true, config: updated });
    } catch (e: any) {
      return res.status(500).json({ ok: false, error: e.message });
    }
  });

  // 3. Get Account Dialogs (Groups & Channels)
  router.get('/dialogs', async (req: Request, res: Response) => {
    try {
      const { client } = await resolveClient(req);
      if (!client) {
        return res.json({ ok: false, error: 'Telegram client not authenticated', dialogs: [] });
      }

      // Fetch user's active dialogs from MTProto
      const dialogs = await client.getDialogs({ limit: 300 });
      const formatted = dialogs.map((d: any) => {
        const entity = d.entity || {};
        const isGroup = Boolean(d.isGroup || entity.megagroup || entity.gigagroup || (entity.className === 'Chat'));
        const isChannel = Boolean(d.isChannel && !entity.megagroup && !entity.gigagroup);
        const isUser = Boolean(d.isUser);
        const title = d.title || d.name || entity.title || entity.firstName || 'مجموعة';
        const username = entity.username || '';
        const id = String(d.id || entity.id || '');
        const participantsCount = entity.participantsCount || undefined;

        let link = '';
        if (username) {
          link = `https://t.me/${username}`;
        } else if (id) {
          const cleanId = id.replace(/^-100/, '').replace(/^-/, '');
          link = `https://t.me/c/${cleanId}`;
        }

        return {
          id,
          title,
          username,
          isGroup,
          isChannel,
          isUser,
          participantsCount,
          link,
          unreadCount: d.unreadCount || 0,
        };
      });

      return res.json({ ok: true, dialogs: formatted });
    } catch (e: any) {
      console.error('[AutomationRouter] Error fetching dialogs:', e);
      return res.json({ ok: false, error: e.message, dialogs: [] });
    }
  });

  // 4. Pre-Check Groups (Membership, Protection Bots, Titles)
  router.post('/pre-check', async (req: Request, res: Response) => {
    try {
      const { client } = await resolveClient(req);
      if (!client) {
        return res.status(401).json({ ok: false, error: 'Telegram client not authenticated' });
      }

      const groups: string[] = req.body.groups || [];
      const results = await BroadcastEngine.preCheckGroups(client, groups);
      return res.json({ ok: true, results });
    } catch (e: any) {
      return res.status(500).json({ ok: false, error: e.message });
    }
  });

  // 4. Start Broadcast Dispatch (Manual / Scheduled / Sequential)
  router.post('/start-dispatch', async (req: Request, res: Response) => {
    try {
      const { client, userId } = await resolveClient(req);
      if (!client) {
        return res.status(401).json({ ok: false, error: 'Telegram client not authenticated' });
      }

      const inputConfig: AutomationConfig = req.body.config || StorageManager.loadConfig(userId);
      // Clean and sanitize groups
      inputConfig.groups = TextNormalizer.cleanGroupLinks(inputConfig.groups);

      if (inputConfig.dispatchType === 'manual') {
        // Run single batch synchronously or async
        BroadcastEngine.executeBatch(userId, client, inputConfig, inputConfig.messageText)
          .then((report) => io.emit('batch_completed', { userId, report }))
          .catch((err) => console.warn('[AutomationRouter] Batch error:', err));

        return res.json({ ok: true, message: 'Batch dispatch initiated', type: 'manual' });
      } else {
        // Continuous scheduled or sequential job
        await BroadcastEngine.startDispatchJob(userId, client, inputConfig);
        return res.json({ ok: true, message: `Continuous ${inputConfig.dispatchType} job started`, type: inputConfig.dispatchType });
      }
    } catch (e: any) {
      return res.status(500).json({ ok: false, error: e.message });
    }
  });

  // 5. Stop Broadcast Dispatch
  router.post('/stop-dispatch', async (req: Request, res: Response) => {
    try {
      const userId = (req.body?.userId as string) || 'default_user';
      BroadcastEngine.stopDispatchJob(userId);
      return res.json({ ok: true, message: 'Broadcast dispatch job stopped' });
    } catch (e: any) {
      return res.status(500).json({ ok: false, error: e.message });
    }
  });

  // 6. Toggle Keyword Monitoring
  router.post('/toggle-monitor', async (req: Request, res: Response) => {
    try {
      const { client, userId } = await resolveClient(req);
      if (!client) {
        return res.status(401).json({ ok: false, error: 'Telegram client not authenticated' });
      }

      const { enable, keywords } = req.body;
      const isCurrentlyMonitoring = MonitoringEngine.isMonitoring(userId);
      const shouldEnable = enable !== undefined ? Boolean(enable) : !isCurrentlyMonitoring;

      if (shouldEnable) {
        await MonitoringEngine.startMonitoring(userId, client, keywords);
        return res.json({ ok: true, isMonitoring: true, message: 'Monitoring started' });
      } else {
        await MonitoringEngine.stopMonitoring(userId);
        return res.json({ ok: true, isMonitoring: false, message: 'Monitoring stopped' });
      }
    } catch (e: any) {
      return res.status(500).json({ ok: false, error: e.message });
    }
  });

  // 7. Advanced Joiner: Start
  router.post('/joiner/start', async (req: Request, res: Response) => {
    try {
      const { client, userId } = await resolveClient(req);
      if (!client) {
        return res.status(401).json({ ok: false, error: 'Telegram client not authenticated' });
      }

      const { rawInput, delaySeconds = 300 } = req.body;
      const state = await AdvancedJoiner.startJoining(
        client,
        userId,
        rawInput,
        delaySeconds,
        (progress) => io.emit('joiner_progress', { userId, progress })
      );

      return res.json({ ok: true, state });
    } catch (e: any) {
      return res.status(500).json({ ok: false, error: e.message });
    }
  });

  // 8. Advanced Joiner: Controls (Pause / Resume / Stop / Status)
  router.post('/joiner/pause', (req: Request, res: Response) => {
    const userId = req.body?.userId || 'default_user';
    AdvancedJoiner.pauseJoining(userId);
    res.json({ ok: true, message: 'Joiner paused' });
  });

  router.post('/joiner/resume', (req: Request, res: Response) => {
    const userId = req.body?.userId || 'default_user';
    AdvancedJoiner.resumeJoining(userId);
    res.json({ ok: true, message: 'Joiner resumed' });
  });

  router.post('/joiner/stop', (req: Request, res: Response) => {
    const userId = req.body?.userId || 'default_user';
    AdvancedJoiner.stopJoining(userId);
    res.json({ ok: true, message: 'Joiner stopped' });
  });

  router.get('/joiner/status', (req: Request, res: Response) => {
    const userId = (req.query?.userId as string) || 'default_user';
    const state = AdvancedJoiner.getSessionState(userId);
    res.json({ ok: true, state });
  });

  // 9. Auto Replies: Get Rules
  router.get('/auto-replies', (req: Request, res: Response) => {
    try {
      const userId = (req.query?.userId as string) || (req.headers['x-user-id'] as string) || 'default_user';
      const data = StorageManager.loadAutoReplyRules(userId);
      res.json({ ok: true, success: true, enabled: data.enabled, rules: data.rules });
    } catch (e: any) {
      res.status(500).json({ ok: false, success: false, error: e.message });
    }
  });

  // 10. Auto Replies: Save Rules & Toggle
  router.post('/auto-replies', (req: Request, res: Response) => {
    try {
      const userId = (req.body?.userId as string) || (req.headers['x-user-id'] as string) || 'default_user';
      const { enabled, rules } = req.body;
      const saved = StorageManager.saveAutoReplyRules(userId, { enabled, rules });
      res.json({ ok: true, success: true, enabled: saved.enabled, rules: saved.rules });
    } catch (e: any) {
      res.status(500).json({ ok: false, success: false, error: e.message });
    }
  });

  return router;
}
