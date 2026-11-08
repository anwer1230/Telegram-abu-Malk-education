/**
 * NotificationCenter.ts - Telegram Central Event Bus
 * 
 * Replicated directly from DrKLO/Telegram Android:
 * org.telegram.messenger.NotificationCenter.java
 */

export interface NotificationCenterDelegate {
  didReceivedNotification(id: number | string, account: number, ...args: any[]): void;
}

export class NotificationCenter {
  // DrKLO/Telegram Android Event Constants
  public static readonly didReceiveNewMessages = 1;
  public static readonly updateInterfaces = 2;
  public static readonly dialogsNeedReload = 3;
  public static readonly closeChats = 4;
  public static readonly messagesDidLoad = 5;
  public static readonly didReceivedWebsitesList = 6;
  public static readonly didReplacedPhotoInMemCache = 7;
  public static readonly notificationsCountUpdated = 8;
  public static readonly didUpdateConnectionState = 9;
  public static readonly userFullInfoDidLoad = 10;
  public static readonly pinnedInfoDidLoad = 11;
  public static readonly messagePlayingProgressDidChanged = 12;
  public static readonly messagePlayingDidReset = 13;
  public static readonly messagePlayingPlayStateChanged = 14;
  public static readonly recordProgressChanged = 15;
  public static readonly recordStartError = 16;
  public static readonly recordStopped = 17;
  public static readonly chatDidCreated = 18;
  public static readonly chatDidFailCreate = 19;
  public static readonly chatInfoDidLoad = 20;
  public static readonly contactsDidLoad = 21;
  public static readonly userSelectedEmoji = 22;
  public static readonly userSelectedSticker = 23;
  public static readonly themeDidLoad = 24;
  public static readonly needSetDayNightTheme = 25;
  public static readonly didReceivedDraft = 26;
  public static readonly messageReceivedByAck = 27;
  public static readonly messagesDeleted = 28;
  public static readonly messagesRead = 29;
  public static readonly didClearDatabase = 30;
  public static readonly checkClientRole = 31;
  public static readonly storiesUpdated = 32;
  public static readonly topicsDidLoaded = 33;
  public static readonly privacyRulesUpdated = 34;
  public static readonly mainUserInfoChanged = 35;
  public static readonly twoStepStateUpdated = 36;
  public static readonly authorizationsUpdated = 37;
  public static readonly sponsoredMessagesLoaded = 38;
  public static readonly cloudSettingsUpdated = 39;
  public static readonly downloadSettingsUpdated = 40;
  public static readonly chatInviteLoaded = 41;
  public static readonly chatInviteJoined = 42;
  public static readonly pendingJoinRequestsUpdated = 43;

  // DrKLO/Telegram Android UPDATE_MASK constants for updateInterfaces
  public static readonly UPDATE_MASK_CHAT = 0x0001;
  public static readonly UPDATE_MASK_CHAT_ADMINS = 0x0002;
  public static readonly UPDATE_MASK_CHAT_MEMBERS = 0x0004;
  public static readonly UPDATE_MASK_STATUS = 0x0008;
  public static readonly UPDATE_MASK_NAME = 0x0010;
  public static readonly UPDATE_MASK_AVATAR = 0x0020;
  public static readonly UPDATE_MASK_READ_DIALOG_MESSAGE = 0x0040;
  public static readonly UPDATE_MASK_SELECT_DIALOG = 0x0080;
  public static readonly UPDATE_MASK_SEND_STATE = 0x0100;
  public static readonly UPDATE_MASK_ALL = 0xffff;

  private static instances = new Map<number, NotificationCenter>();
  private static globalInstance: NotificationCenter;

  private observers = new Map<number | string, Set<NotificationCenterDelegate | ((...args: any[]) => void)>>();
  private currentAccount: number;

  public static getInstance(account: number = 0): NotificationCenter {
    if (!NotificationCenter.instances.has(account)) {
      const inst = new NotificationCenter(account);
      NotificationCenter.instances.set(account, inst);
      if (account === 0 && !NotificationCenter.globalInstance) {
        NotificationCenter.globalInstance = inst;
      }
    }
    return NotificationCenter.instances.get(account)!;
  }

  public static getGlobalInstance(): NotificationCenter {
    if (!NotificationCenter.globalInstance) {
      NotificationCenter.globalInstance = NotificationCenter.getInstance(0);
    }
    return NotificationCenter.globalInstance;
  }

  private constructor(account: number = 0) {
    this.currentAccount = account;
  }

  public addObserver(
    observerOrId: NotificationCenterDelegate | ((...args: any[]) => void) | number | string,
    idOrObserver: number | string | NotificationCenterDelegate | ((...args: any[]) => void)
  ): void {
    let id: number | string;
    let observer: NotificationCenterDelegate | ((...args: any[]) => void);

    if (typeof observerOrId === 'number' || (typeof observerOrId === 'string' && typeof idOrObserver === 'function')) {
      id = observerOrId;
      observer = idOrObserver as NotificationCenterDelegate | ((...args: any[]) => void);
    } else {
      observer = observerOrId as NotificationCenterDelegate | ((...args: any[]) => void);
      id = idOrObserver as number | string;
    }

    if (!this.observers.has(id)) {
      this.observers.set(id, new Set());
    }
    this.observers.get(id)!.add(observer);
  }

  public removeObserver(
    observerOrId: NotificationCenterDelegate | ((...args: any[]) => void) | number | string,
    idOrObserver: number | string | NotificationCenterDelegate | ((...args: any[]) => void)
  ): void {
    let id: number | string;
    let observer: NotificationCenterDelegate | ((...args: any[]) => void);

    if (typeof observerOrId === 'number' || (typeof observerOrId === 'string' && typeof idOrObserver === 'function')) {
      id = observerOrId;
      observer = idOrObserver as NotificationCenterDelegate | ((...args: any[]) => void);
    } else {
      observer = observerOrId as NotificationCenterDelegate | ((...args: any[]) => void);
      id = idOrObserver as number | string;
    }

    const list = this.observers.get(id);
    if (list) {
      list.delete(observer);
      if (list.size === 0) {
        this.observers.delete(id);
      }
    }
  }

  public postNotificationName(id: number | string, ...args: any[]): void {
    const list = this.observers.get(id);
    if (list) {
      list.forEach((obs) => {
        try {
          if (typeof obs === 'function') {
            obs(...args);
          } else if (typeof obs.didReceivedNotification === 'function') {
            obs.didReceivedNotification(id, this.currentAccount, ...args);
          }
        } catch (e) {
          console.error('[NotificationCenter] Error in observer callback:', e);
        }
      });
    }

    // Also dispatch a browser CustomEvent for reactive DOM integration
    if (typeof window !== 'undefined') {
      window.dispatchEvent(
        new CustomEvent('tg-notification-center', {
          detail: { id, account: this.currentAccount, args },
        })
      );
    }
  }

  public hasObservers(id: number | string): boolean {
    return (this.observers.get(id)?.size || 0) > 0;
  }
}

export const notificationCenter = NotificationCenter.getInstance(0);
