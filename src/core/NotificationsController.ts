/**
 * NotificationsController.ts - org.telegram.messenger.NotificationsController
 * Handles push notifications and sound alerts.
 */

export class NotificationsController {
  private static instances = new Map<number, NotificationsController>();
  private currentAccount: number;

  public static getInstance(account: number = 0): NotificationsController {
    if (!NotificationsController.instances.has(account)) {
      NotificationsController.instances.set(account, new NotificationsController(account));
    }
    return NotificationsController.instances.get(account)!;
  }

  private constructor(account: number) {
    this.currentAccount = account;
  }

  public showNotification(title: string, message: string): void {
    if (typeof Notification !== 'undefined' && Notification.permission === 'granted') {
      new Notification(title, { body: message });
    }
  }
}

export const notificationsController = NotificationsController.getInstance(0);
