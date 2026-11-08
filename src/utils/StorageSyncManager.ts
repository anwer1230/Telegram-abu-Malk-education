/**
 * StorageSyncManager.ts - Synchronization between memory state and persistent disk
 */

export class StorageSyncManager {
  private static instance: StorageSyncManager;

  public static getInstance(): StorageSyncManager {
    if (!StorageSyncManager.instance) {
      StorageSyncManager.instance = new StorageSyncManager();
    }
    return StorageSyncManager.instance;
  }

  public syncAll(): void {}

  public getAllDrafts(): Record<string, string> {
    return {};
  }

  public setDraft(chatId: string, text: string): void {
    if (typeof window !== 'undefined') {
      try {
        localStorage.setItem(`tg_draft_${chatId}`, text);
      } catch {}
    }
  }

  public async loadSettings(): Promise<any | null> {
    if (typeof window === 'undefined') return null;
    try {
      const raw = localStorage.getItem('tg_app_settings');
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  }

  public saveSettings(settings: any): void {
    if (typeof window !== 'undefined') {
      try {
        localStorage.setItem('tg_app_settings', JSON.stringify(settings));
      } catch {}
    }
  }

  public saveSessions(...args: any[]): void {
    if (typeof window !== 'undefined' && args.length > 0) {
      try {
        const accountsData = args[0];
        const activeId = args[1];
        localStorage.setItem('tg_sessions', JSON.stringify(accountsData));
        localStorage.setItem('tg_multi_accounts_v3', JSON.stringify(accountsData));
        if (activeId) {
          localStorage.setItem('tg_active_account_id_v3', String(activeId));
        }
      } catch (e) {
        console.warn('[StorageSyncManager] Failed to persist accounts:', e);
      }
    }
  }

  public clearAllOnLogout(): void {
    if (typeof window !== 'undefined') {
      try {
        localStorage.removeItem('tg_sessions');
        localStorage.removeItem('tg_multi_accounts_v3');
        localStorage.removeItem('tg_active_account_id_v3');
        localStorage.removeItem('tg_active_account');
        localStorage.removeItem('tg_session_string');
      } catch {}
    }
  }
}

export const storageSyncManager = StorageSyncManager.getInstance();
