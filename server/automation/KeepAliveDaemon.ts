/**
 * KeepAliveDaemon.ts - Server continuous uptime & connectivity guardian
 * 1. Self-ping every 4 minutes to prevent Cloud Run / container idling
 * 2. Network connectivity check every 30 seconds with auto-reconnection
 * 3. Session integrity validation every 2 minutes
 */

import http from 'http';
import https from 'https';

export class KeepAliveDaemon {
  private static pingInterval: NodeJS.Timeout | null = null;
  private static networkInterval: NodeJS.Timeout | null = null;
  private static sessionInterval: NodeJS.Timeout | null = null;
  private static isNetworkOnline = true;

  public static start(port: number, onNetworkRestored?: () => void, onSessionCheck?: () => Promise<void>) {
    console.log('[KeepAliveDaemon] Initializing server resilience services...');

    // 1. Self-Ping every 4 minutes (240,000 ms)
    this.pingInterval = setInterval(() => {
      try {
        const req = http.get(`http://127.0.0.1:${port}/api/health`, (res) => {
          res.resume(); // Consume data to free memory
        });
        req.on('error', () => {
          // Silent catch for self-ping
        });
        req.setTimeout(5000, () => req.destroy());
      } catch (_) {}
    }, 4 * 60 * 1000);

    // 2. Network connectivity checker every 30 seconds
    this.networkInterval = setInterval(() => {
      https.get('https://dns.google/resolve?name=telegram.org', (res) => {
        if (!this.isNetworkOnline) {
          console.log('[KeepAliveDaemon] 🌐 Network connection restored. Resuming operations...');
          this.isNetworkOnline = true;
          if (onNetworkRestored) onNetworkRestored();
        }
        res.resume();
      }).on('error', () => {
        if (this.isNetworkOnline) {
          console.warn('[KeepAliveDaemon] ⚠️ Network offline detected. Suspending active sockets temporarily...');
          this.isNetworkOnline = false;
        }
      });
    }, 30 * 1000);

    // 3. Session validator every 2 minutes (120,000 ms)
    if (onSessionCheck) {
      this.sessionInterval = setInterval(async () => {
        try {
          await onSessionCheck();
        } catch (e) {
          console.warn('[KeepAliveDaemon] Session periodic check notice:', e);
        }
      }, 2 * 60 * 1000);
    }
  }

  public static stop() {
    if (this.pingInterval) clearInterval(this.pingInterval);
    if (this.networkInterval) clearInterval(this.networkInterval);
    if (this.sessionInterval) clearInterval(this.sessionInterval);
  }
}
