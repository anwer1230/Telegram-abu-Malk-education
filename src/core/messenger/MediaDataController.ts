/**
 * MediaDataController.ts - org.telegram.messenger.MediaDataController
 */

export class MediaDataController {
  private static instances = new Map<number, MediaDataController>();
  private currentAccount: number;

  public static getInstance(account: number = 0): MediaDataController {
    if (!MediaDataController.instances.has(account)) {
      MediaDataController.instances.set(account, new MediaDataController(account));
    }
    return MediaDataController.instances.get(account)!;
  }

  private constructor(account: number) {
    this.currentAccount = account;
  }
}
