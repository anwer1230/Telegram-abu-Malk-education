/**
 * sqliteStorage.ts - Local Database Persistence Adapter
 */

export class TelegramSQLiteStorage {
  private initialized: boolean = false;

  public async init(): Promise<void> {
    this.initialized = true;
  }

  public isReady(): boolean {
    return this.initialized;
  }
}

export const telegramDB = new TelegramSQLiteStorage();
