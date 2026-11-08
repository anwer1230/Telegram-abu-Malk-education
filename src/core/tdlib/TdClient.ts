/**
 * TdClient.ts - Telegram Database Client Bridge
 */

export class TdClient {
  private static instance: TdClient;

  public static getInstance(): TdClient {
    if (!TdClient.instance) {
      TdClient.instance = new TdClient();
    }
    return TdClient.instance;
  }

  public async send(request: any): Promise<any> {
    return { ok: true };
  }
}

export const tdClient = TdClient.getInstance();
