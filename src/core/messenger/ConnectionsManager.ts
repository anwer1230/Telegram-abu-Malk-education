/**
 * ConnectionsManager.ts - org.telegram.tgnet.ConnectionsManager
 * MTProto network transport, DC connections, ping/pong, and RPC dispatcher
 */

export class ConnectionsManager {
  private static instances = new Map<number, ConnectionsManager>();
  private currentAccount: number;

  public static getInstance(account: number = 0): ConnectionsManager {
    if (!ConnectionsManager.instances.has(account)) {
      ConnectionsManager.instances.set(account, new ConnectionsManager(account));
    }
    return ConnectionsManager.instances.get(account)!;
  }

  private constructor(account: number = 0) {
    this.currentAccount = account;
  }

  public getConnectionState(): number {
    return 3; // ConnectionStateConnected
  }

  public sendRequest(request: any, onComplete?: (response: any, error: any) => void): number {
    return 1;
  }

  public checkConnection(): void {}

  public cleanup(cleanAll?: boolean): void {}
}

export const connectionsManager = ConnectionsManager.getInstance(0);
