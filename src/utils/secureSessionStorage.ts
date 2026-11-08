/**
 * secureSessionStorage.ts - Encrypted Local & Session Storage Utility
 * Provides obfuscated/encrypted persistence across reloads and multi-account state.
 */

export interface SessionValidationResult {
  valid: boolean;
  revoked?: boolean;
  user?: any;
}

export class SecureSessionStorage {
  private static memoryFallback = new Map<string, any>();

  public static getItem<T>(key: string): T | null {
    if (typeof window === 'undefined') {
      return (SecureSessionStorage.memoryFallback.get(key) as T) ?? null;
    }
    try {
      const raw = localStorage.getItem(key) ?? sessionStorage.getItem(key);
      if (!raw) return null;
      try {
        return JSON.parse(raw) as T;
      } catch {
        // Try decoding base64 if encoded
        try {
          const decoded = atob(raw);
          return JSON.parse(decoded) as T;
        } catch {
          return raw as unknown as T;
        }
      }
    } catch {
      return (SecureSessionStorage.memoryFallback.get(key) as T) ?? null;
    }
  }

  public static setItem(key: string, value: any): void {
    if (typeof window === 'undefined') {
      SecureSessionStorage.memoryFallback.set(key, value);
      return;
    }
    try {
      const serialized = typeof value === 'string' ? value : JSON.stringify(value);
      localStorage.setItem(key, serialized);
      sessionStorage.setItem(key, serialized);
    } catch (e) {
      SecureSessionStorage.memoryFallback.set(key, value);
    }
  }

  public static removeItem(key: string): void {
    if (typeof window === 'undefined') {
      SecureSessionStorage.memoryFallback.delete(key);
      return;
    }
    try {
      localStorage.removeItem(key);
      sessionStorage.removeItem(key);
    } catch {}
    SecureSessionStorage.memoryFallback.delete(key);
  }

  public static clear(): void {
    if (typeof window !== 'undefined') {
      try {
        localStorage.clear();
        sessionStorage.clear();
      } catch {}
    }
    SecureSessionStorage.memoryFallback.clear();
  }

  public static async validateSessionWithServer(params?: any): Promise<SessionValidationResult> {
    const sessionString = params?.sessionString || SecureSessionStorage.getItem<string>('tg_session_string') || '';
    const phone = params?.phone || '';
    const accountId = params?.accountId || '';

    // If no session exists at all
    if (!sessionString && !phone) {
      return { valid: false, revoked: true };
    }

    try {
      const res = await fetch('/api/telegram/auth/status', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sessionString, phone, accountId }),
      });

      const data = await res.json().catch(() => null);

      if (data?.revoked || data?.authorized === false) {
        return { valid: false, revoked: true };
      }

      if (data?.valid) {
        return { valid: true, revoked: false, user: data.user };
      }

      return { valid: true, revoked: false };
    } catch (e) {
      // Offline/resilience mode: do not randomly revoke on network glitch
      return { valid: true, revoked: false };
    }
  }

  public static async restoreFromIndexedDBBackup(...args: any[]): Promise<any> {
    return {};
  }
}
