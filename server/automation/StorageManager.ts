/**
 * StorageManager.ts - Persistent per-user configuration and tasks isolation
 * Stored securely in `data/automation/{userId}/settings.json`
 */

import fs from 'fs';
import path from 'path';
import { AutomationConfig, AutoReplyRule } from './types';

const BASE_DATA_DIR = path.join(process.cwd(), 'data', 'automation');

export class StorageManager {
  private static ensureUserDir(userId: string): string {
    const userDir = path.join(BASE_DATA_DIR, userId.replace(/[^a-zA-Z0-9_-]/g, '_'));
    if (!fs.existsSync(userDir)) {
      fs.mkdirSync(userDir, { recursive: true });
    }
    return userDir;
  }

    public static loadDefaultFixedLinks(): string[] {
    try {
      const savedPath = path.join(process.cwd(), 'data', 'saved_links.json');
      if (fs.existsSync(savedPath)) {
        const raw = fs.readFileSync(savedPath, 'utf-8');
        const data = JSON.parse(raw);
        if (Array.isArray(data.links)) {
          return data.links.map((l: any) => l.url).filter(Boolean);
        }
      }
    } catch {
      // fallback
    }
    return [];
  }

  public static getDefaultConfig(userId: string): AutomationConfig {
    return {
      userId,
      messageText: '',
      groups: [],
      images: [],
      dispatchType: 'manual',
      intervalMinutes: 60,
      totalHours: 0,
      protectionMode: 'salam',
      requiredMemberMessages: 5,
      sendToAllGroups: false,
      sequentialMessages: [],
      keywords: [],
      advancedJoinLinks: StorageManager.loadDefaultFixedLinks(),
      isMonitoring: false,
      isDispatching: false,
      lastDispatchedAt: 0,
      startedAt: 0,
      currentSequentialIndex: 0,
    };
  }

  public static loadConfig(userId: string): AutomationConfig {
    try {
      const userDir = this.ensureUserDir(userId);
      const filePath = path.join(userDir, 'settings.json');
      if (fs.existsSync(filePath)) {
        const raw = fs.readFileSync(filePath, 'utf-8');
        const parsed = JSON.parse(raw);
        return { ...this.getDefaultConfig(userId), ...parsed, userId };
      }
    } catch (e) {
      console.warn(`[StorageManager] Failed to load config for ${userId}:`, e);
    }
    return this.getDefaultConfig(userId);
  }

  public static saveConfig(userId: string, config: Partial<AutomationConfig>): AutomationConfig {
    const userDir = this.ensureUserDir(userId);
    const filePath = path.join(userDir, 'settings.json');
    const existing = this.loadConfig(userId);
    const updated: AutomationConfig = { ...existing, ...config, userId };

    try {
      fs.writeFileSync(filePath, JSON.stringify(updated, null, 2), 'utf-8');
    } catch (e) {
      console.error(`[StorageManager] Failed to save config for ${userId}:`, e);
    }
    return updated;
  }

  /**
   * Discovers all saved user configs to resume active tasks on server restart
   */
  public static loadAllConfigs(): AutomationConfig[] {
    const configs: AutomationConfig[] = [];
    try {
      if (!fs.existsSync(BASE_DATA_DIR)) return [];
      const userDirs = fs.readdirSync(BASE_DATA_DIR, { withFileTypes: true });
      for (const dir of userDirs) {
        if (dir.isDirectory()) {
          const filePath = path.join(BASE_DATA_DIR, dir.name, 'settings.json');
          if (fs.existsSync(filePath)) {
            try {
              const raw = fs.readFileSync(filePath, 'utf-8');
              const parsed = JSON.parse(raw);
              configs.push(parsed);
            } catch (_) {}
          }
        }
      }
    } catch (e) {
      console.warn('[StorageManager] Error reading all user configs:', e);
    }
    return configs;
  }

  public static loadAutoReplyRules(userId: string): { enabled: boolean; rules: AutoReplyRule[] } {
    try {
      const userDir = this.ensureUserDir(userId);
      const filePath = path.join(userDir, 'auto_replies.json');
      if (fs.existsSync(filePath)) {
        const raw = fs.readFileSync(filePath, 'utf-8');
        return JSON.parse(raw);
      }
    } catch (e) {
      console.warn(`[StorageManager] Failed to load auto replies for ${userId}:`, e);
    }
    return { enabled: true, rules: [] };
  }

  public static saveAutoReplyRules(userId: string, data: { enabled?: boolean; rules?: AutoReplyRule[] }): { enabled: boolean; rules: AutoReplyRule[] } {
    const userDir = this.ensureUserDir(userId);
    const filePath = path.join(userDir, 'auto_replies.json');
    const existing = this.loadAutoReplyRules(userId);
    const updated = {
      enabled: data.enabled !== undefined ? data.enabled : existing.enabled,
      rules: data.rules !== undefined ? data.rules : existing.rules,
    };
    try {
      fs.writeFileSync(filePath, JSON.stringify(updated, null, 2), 'utf-8');
    } catch (e) {
      console.error(`[StorageManager] Failed to save auto replies for ${userId}:`, e);
    }
    return updated;
  }
}
