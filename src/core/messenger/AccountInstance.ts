/**
 * AccountInstance.ts - org.telegram.messenger.AccountInstance
 * Replicated directly from DrKLO/Telegram Android
 * Provides isolated context for multi-account management
 */

import { connectionsManager, ConnectionsManager } from '../ConnectionsManager';
import { messagesController, MessagesController } from '../MessagesController';
import { notificationsController, NotificationsController } from '../NotificationsController';
import { NotificationCenter } from '../NotificationCenter';
import { MessagesStorage } from '../MessagesStorage';
import { TdClient, tdClient } from '../tdlib/TdClient';
import { UserConfig } from './UserConfig';
import { ContactsController } from './ContactsController';
import { MediaDataController } from './MediaDataController';
import { SendMessagesHelper } from './SendMessagesHelper';
import { SecretChatHelper } from './SecretChatHelper';
import { StoriesController } from './StoriesController';
import { DownloadController } from './DownloadController';
import { PrivacySettingsController } from './PrivacySettingsController';
import { TwoStepVerificationController } from './TwoStepVerificationController';

export class AccountInstance {
  private static instances = new Map<number, AccountInstance>();
  private currentAccount: number;

  public static getInstance(accountNum: number = 0): AccountInstance {
    if (!AccountInstance.instances.has(accountNum)) {
      AccountInstance.instances.set(accountNum, new AccountInstance(accountNum));
    }
    return AccountInstance.instances.get(accountNum)!;
  }

  private constructor(accountNum: number) {
    this.currentAccount = accountNum;
  }

  public getCurrentAccount(): number {
    return this.currentAccount;
  }

  public getUserConfig(): UserConfig {
    return UserConfig.getInstance(this.currentAccount);
  }

  public getConnectionsManager(): ConnectionsManager {
    return ConnectionsManager.getInstance(this.currentAccount);
  }

  public getMessagesController(): MessagesController {
    return MessagesController.getInstance(this.currentAccount);
  }

  public getNotificationCenter(): NotificationCenter {
    return NotificationCenter.getInstance(this.currentAccount);
  }

  public getMessagesStorage(): MessagesStorage {
    return MessagesStorage.getInstance(this.currentAccount);
  }

  public getContactsController(): ContactsController {
    return ContactsController.getInstance();
  }

  public getMediaDataController(): MediaDataController {
    return MediaDataController.getInstance(this.currentAccount);
  }

  public getStoriesController(): StoriesController {
    return StoriesController.getInstance(this.currentAccount);
  }

  public getDownloadController(): DownloadController {
    return DownloadController.getInstance(this.currentAccount);
  }

  public getPrivacySettingsController(): PrivacySettingsController {
    return PrivacySettingsController.getInstance(this.currentAccount);
  }

  public getTwoStepVerificationController(): TwoStepVerificationController {
    return TwoStepVerificationController.getInstance(this.currentAccount);
  }

  public getSendMessagesHelper(): SendMessagesHelper {
    return SendMessagesHelper.getInstance();
  }

  public getSecretChatHelper(): SecretChatHelper {
    return SecretChatHelper.getInstance();
  }

  public getNotificationsController(): NotificationsController {
    return NotificationsController.getInstance(this.currentAccount);
  }

  public getTdClient(): TdClient {
    return tdClient;
  }
}
