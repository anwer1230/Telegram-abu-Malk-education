/**
 * telegramDexieDb.ts - IndexedDB local storage engine
 */

export const telegramDb = {
  chats: {
    toArray: async () => [],
    bulkPut: async (items: any[]) => {},
  },
  messages: {
    toArray: async () => [],
    bulkPut: async (items: any[]) => {},
  },
  discoveredLinks: {
    toArray: async () => [],
    bulkPut: async (items: any[]) => {},
    clear: async () => {},
  },
};

export async function initTelegramDexieDb(): Promise<void> {}
