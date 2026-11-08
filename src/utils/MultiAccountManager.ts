/**
 * MultiAccountManager.ts
 *
 * Direct TS port and integration of DrKLO/Telegram Multi-Account Architecture:
 * - UserConfig.java (Account slots, selectedAccount, configs, persistent storage)
 * - ConnectionsManager.java (Per-account MTProto network and transport instances)
 * - AccountInstance.java (Isolated database, storage, and message scopes)
 *
 * Allows switching between active account instances dynamically without app reloads.
 */

import { User, UserAccount, Chat, Message, AppSettings } from '../types';
import { ConnectionsManager } from '../core/ConnectionsManager';
import { DEFAULT_ACCOUNTS, INITIAL_CHATS, INITIAL_MESSAGES } from '../data/mockTelegramData';
import { SecureSessionStorage } from './secureSessionStorage';

export type MultiAccountEventType =
  | 'ACCOUNT_SWITCHED'
  | 'ACCOUNT_ADDED'
  | 'ACCOUNT_REMOVED'
  | 'ACCOUNT_UPDATED'
  | 'ACCOUNTS_SYNCED';

export interface MultiAccountEvent {
  type: MultiAccountEventType;
  selectedAccount: number;
  account?: UserAccount;
  previousAccount?: number;
  accounts: UserAccount[];
}

/**
 * UserConfig - Replicates org.telegram.messenger.UserConfig
 * Holds accounts, selected account index, and serialization logic.
 */
export class UserConfig {
  public static readonly MAX_ACCOUNT_COUNT = 4;
  public static selectedAccount: number = 0;
  public static accounts: UserAccount[] = [];
  private static isInitialized = false;

  private static STORAGE_KEY_ACCOUNTS = 'tg_multi_accounts_v3';
  private static STORAGE_KEY_SELECTED = 'tg_active_account_id_v3';

  public static initialize(): void {
    if (this.isInitialized) return;
    this.loadConfig();
    this.isInitialized = true;
  }

  public static getActivatedAccountsCount(): number {
    return this.accounts.filter((a) => a.isActive !== false).length;
  }

  public static isClientActivated(accountNum: number): boolean {
    const acc = this.accounts[accountNum];
    return !!acc && acc.isActive !== false;
  }

  /**
   * Goal 1: Purges dummy/mock/test accounts and resets selectedAccount to the real account
   */
  public static cleanupTestAccounts(): void {
    const realAccounts = this.accounts.filter((a) => {
      const isTest = (a.user as any)?.isTestAccount ||
                     a.user?.phone?.startsWith('+999') ||
                     a.user?.phone === '0000000000' ||
                     a.user?.phone?.includes('test') ||
                     (a.user as any)?.isDummy === true;
      return !isTest && a.isActive !== false;
    });

    if (realAccounts.length > 0) {
      this.accounts = realAccounts;
      this.selectedAccount = 0;
    } else {
      this.accounts = [];
      this.selectedAccount = 0;
    }
    this.saveConfig();
  }

  public static clearConfig(accountNum: number = this.selectedAccount): void {
    if (accountNum >= 0 && accountNum < this.accounts.length) {
      this.accounts.splice(accountNum, 1);
      if (this.selectedAccount >= this.accounts.length) {
        this.selectedAccount = Math.max(0, this.accounts.length - 1);
      }
      this.saveConfig();
    }
  }

  public static getAccount(accountNum: number): UserAccount | null {
    if (accountNum < 0 || accountNum >= this.accounts.length) {
      return null;
    }
    return this.accounts[accountNum];
  }

  public static getAccountById(accountId: string): UserAccount | null {
    const found = this.accounts.find((a) => a.id === accountId);
    return found || null;
  }

  public static getAccountIndex(accountId: string): number {
    return this.accounts.findIndex((a) => a.id === accountId);
  }

  public static setAccount(accountNum: number, account: UserAccount): void {
    if (accountNum >= 0 && accountNum < this.MAX_ACCOUNT_COUNT) {
      this.accounts[accountNum] = account;
      this.saveConfig(accountNum);
    }
  }

  public static setCurrentUser(accountNum: number, user: User): void {
    const acc = this.getAccount(accountNum);
    if (acc) {
      acc.user = { ...acc.user, ...user };
      this.saveConfig(accountNum);
    }
  }

  public static loadConfig(): void {
    try {
      if (typeof window !== 'undefined') {
        const saved = SecureSessionStorage.getItem<UserAccount[]>(this.STORAGE_KEY_ACCOUNTS);
        const savedActiveId = SecureSessionStorage.getItem<string>(this.STORAGE_KEY_SELECTED);

        if (saved && Array.isArray(saved) && saved.length > 0) {
          this.accounts = saved.slice(0, this.MAX_ACCOUNT_COUNT);
        }

        if (this.accounts.length === 0) {
          this.accounts = [...DEFAULT_ACCOUNTS];
        }

        if (savedActiveId) {
          const idx = this.getAccountIndex(savedActiveId);
          this.selectedAccount = idx >= 0 ? idx : 0;
        } else {
          this.selectedAccount = 0;
        }
      } else {
        this.accounts = [...DEFAULT_ACCOUNTS];
        this.selectedAccount = 0;
      }
    } catch (e) {
      console.warn('[UserConfig] Error loading configuration:', e);
      this.accounts = [...DEFAULT_ACCOUNTS];
      this.selectedAccount = 0;
    }
  }

  public static saveConfig(accountNum?: number): void {
    try {
      if (typeof window !== 'undefined') {
        SecureSessionStorage.setItem(this.STORAGE_KEY_ACCOUNTS, this.accounts);
        const activeAcc = this.getAccount(this.selectedAccount);
        if (activeAcc) {
          SecureSessionStorage.setItem(this.STORAGE_KEY_SELECTED, activeAcc.id);
        }
      }
    } catch (e) {
      console.warn('[UserConfig] Error saving configuration:', e);
    }
  }

  public static removeAccount(accountNum: number): boolean {
    if (this.accounts.length <= 1) return false;
    if (accountNum < 0 || accountNum >= this.accounts.length) return false;

    this.accounts.splice(accountNum, 1);
    if (this.selectedAccount >= this.accounts.length) {
      this.selectedAccount = Math.max(0, this.accounts.length - 1);
    }
    this.saveConfig();
    return true;
  }
}

/**
 * MultiAccountManager - Replicates DrKLO MultiAccountManager & AccountInstance Switcher
 * Provides non-blocking, dynamic account switching without app reloads.
 */
export class MultiAccountManager {
  private static instance: MultiAccountManager;
  private listeners = new Set<(event: MultiAccountEvent) => void>();

  public static getInstance(): MultiAccountManager {
    if (!MultiAccountManager.instance) {
      MultiAccountManager.instance = new MultiAccountManager();
    }
    return MultiAccountManager.instance;
  }

  private constructor() {
    UserConfig.initialize();
  }

  /**
   * Returns current active account index (0-based)
   */
  public getSelectedAccount(): number {
    return UserConfig.selectedAccount;
  }

  /**
   * Returns active UserAccount data
   */
  public getSelectedAccountInstance(): UserAccount | null {
    return UserConfig.getAccount(UserConfig.selectedAccount);
  }

  /**
   * Returns all registered accounts
   */
  public getAccounts(): UserAccount[] {
    return [...UserConfig.accounts];
  }

  /**
   * Returns active accounts count
   */
  public getActivatedAccountsCount(): number {
    return UserConfig.getActivatedAccountsCount();
  }

  /**
   * Obtains the ConnectionsManager MTProto transport instance for the specified account index
   */
  public getConnectionsManager(accountNum?: number): ConnectionsManager {
    const num = typeof accountNum === 'number' ? accountNum : UserConfig.selectedAccount;
    return ConnectionsManager.getInstance(num);
  }

  /**
   * Obtains the ConnectionsManager for the currently selected active account
   */
  public getSelectedConnectionsManager(): ConnectionsManager {
    return this.getConnectionsManager(UserConfig.selectedAccount);
  }

  /**
   * Switches account dynamically without requiring page reload.
   * Resumes network on the new instance, pauses inactive connection if needed,
   * updates selectedAccount in UserConfig, and notifies listeners.
   */
  public async switchToAccount(
    target: number | string,
    reloadUI: boolean = true
  ): Promise<UserAccount> {
    const previousAccount = UserConfig.selectedAccount;
    let targetIndex: number;

    if (typeof target === 'string') {
      targetIndex = UserConfig.getAccountIndex(target);
      if (targetIndex < 0) {
        throw new Error(`[MultiAccountManager] Account ID "${target}" not found.`);
      }
    } else {
      targetIndex = target;
    }

    if (targetIndex < 0 || targetIndex >= UserConfig.accounts.length) {
      throw new Error(`[MultiAccountManager] Invalid account index: ${targetIndex}`);
    }

    const targetAccount = UserConfig.getAccount(targetIndex);
    if (!targetAccount) {
      throw new Error(`[MultiAccountManager] Account at index ${targetIndex} is null.`);
    }

    if (previousAccount === targetIndex) {
      return targetAccount;
    }

    // 1. Pause network transport for the outgoing account if desired
    try {
      const prevConn = ConnectionsManager.getInstance(previousAccount);
      prevConn.pauseNetwork();
    } catch {}

    // 2. Set new selected account index in UserConfig
    UserConfig.selectedAccount = targetIndex;
    UserConfig.saveConfig(targetIndex);

    // 3. Resume network transport on the new account instance (MTProto DC connection)
    const newConn = ConnectionsManager.getInstance(targetIndex);
    newConn.resumeNetworkMaybe();

    // 4. Dispatch event to observers for immediate UI re-render without reload
    const event: MultiAccountEvent = {
      type: 'ACCOUNT_SWITCHED',
      selectedAccount: targetIndex,
      account: targetAccount,
      previousAccount,
      accounts: [...UserConfig.accounts],
    };
    this.notifyObservers(event);

    return targetAccount;
  }

  /**
   * Adds a new account into UserConfig, assigns isolated storage, and resumes its connection.
   */
  public async addAccount(newAccountData: {
    name: string;
    phone: string;
    username?: string;
    avatar?: string;
    bio?: string;
  }): Promise<UserAccount> {
    if (UserConfig.accounts.length >= UserConfig.MAX_ACCOUNT_COUNT) {
      throw new Error(
        `[MultiAccountManager] Maximum account limit (${UserConfig.MAX_ACCOUNT_COUNT}) reached.`
      );
    }

    const newId = `acc_${Date.now()}_${Math.random().toString(36).substring(2, 6)}`;
    const defaultSettings: AppSettings = {
      theme: 'dark',
      accentColor: '#2481cc',
      fontSize: 16,
      language: 'ar',
      sendByEnter: true,
      soundEffects: true,
      autoDownloadMedia: true,
      chatWallpaper: 'pattern_classic',
    };

    const newUser: User = {
      id: `user_${newId}`,
      name: newAccountData.name,
      phone: newAccountData.phone,
      username: newAccountData.username || undefined,
      avatar: newAccountData.avatar || '',
      bio: newAccountData.bio || 'New Telegram Account (Multi-Instance)',
      isOnline: true,
      isVerified: false,
      isPremium: false,
    };

    // Build isolated default chat list for the newly provisioned account
    const initialAccChats: Chat[] = [
      {
        id: 'chat_saved_messages',
        type: 'saved',
        title: 'Saved Messages',
        avatar: '',
        isPinned: true,
        unreadCount: 0,
        lastMessage: {
          id: `m_saved_${newId}`,
          senderName: 'You',
          text: `مرحباً بك في حسابك الجديد (${newUser.name}). مساحتك السحابية المعزولة والمشفرة.`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          isOutgoing: true,
          status: 'read',
        },
        description: 'مساحتك السحابية الخاصة لحفظ الرسائل والملفات مع تشفير MTProto 2.0.',
      },
    ];

    const initialAccMessages: Record<string, Message[]> = {
      chat_saved_messages: [
        {
          id: `m_init_${newId}`,
          chatId: 'chat_saved_messages',
          senderId: newUser.id,
          senderName: newUser.name,
          text: `مرحباً بك في تيليجرام. تم إنشاء الحساب "${newUser.name}" بنجاح مع عزل كامل لقواعد البيانات والاتصال.`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          date: new Date().toISOString().split('T')[0],
          isOutgoing: false,
          status: 'read',
        },
      ],
    };

    const newAccount: UserAccount = {
      id: newId,
      user: newUser,
      settings: defaultSettings,
      chats: initialAccChats,
      messages: initialAccMessages,
      unreadCount: 0,
      isActive: true,
    };

    const newIndex = UserConfig.accounts.length;
    UserConfig.accounts.push(newAccount);
    UserConfig.saveConfig(newIndex);

    // Switch to the newly created account immediately
    await this.switchToAccount(newIndex, true);

    const event: MultiAccountEvent = {
      type: 'ACCOUNT_ADDED',
      selectedAccount: newIndex,
      account: newAccount,
      accounts: [...UserConfig.accounts],
    };
    this.notifyObservers(event);

    return newAccount;
  }

  /**
   * Removes an account from UserConfig and switches cleanly to the first available account if needed
   */
  public async removeAccount(
    target: number | string
  ): Promise<{ success: boolean; nextSelectedAccount?: number }> {
    let targetIndex: number;
    if (typeof target === 'string') {
      targetIndex = UserConfig.getAccountIndex(target);
    } else {
      targetIndex = target;
    }

    if (targetIndex < 0 || targetIndex >= UserConfig.accounts.length) {
      return { success: false };
    }

    if (UserConfig.accounts.length <= 1) {
      return { success: false };
    }

    const wasSelected = UserConfig.selectedAccount === targetIndex;
    const removedAcc = UserConfig.accounts[targetIndex];

    UserConfig.removeAccount(targetIndex);

    if (wasSelected) {
      const nextIdx = Math.max(0, Math.min(targetIndex, UserConfig.accounts.length - 1));
      await this.switchToAccount(nextIdx, true);
    }

    const event: MultiAccountEvent = {
      type: 'ACCOUNT_REMOVED',
      selectedAccount: UserConfig.selectedAccount,
      account: removedAcc,
      accounts: [...UserConfig.accounts],
    };
    this.notifyObservers(event);

    return { success: true, nextSelectedAccount: UserConfig.selectedAccount };
  }

  /**
   * Updates profile data for a specific account
   */
  public updateAccountProfile(target: number | string, profile: Partial<User>): void {
    let targetIndex: number;
    if (typeof target === 'string') {
      targetIndex = UserConfig.getAccountIndex(target);
    } else {
      targetIndex = target;
    }

    const acc = UserConfig.getAccount(targetIndex);
    if (acc) {
      acc.user = { ...acc.user, ...profile };
      UserConfig.saveConfig(targetIndex);

      const event: MultiAccountEvent = {
        type: 'ACCOUNT_UPDATED',
        selectedAccount: UserConfig.selectedAccount,
        account: acc,
        accounts: [...UserConfig.accounts],
      };
      this.notifyObservers(event);
    }
  }

  /**
   * Synchronizes internal UserConfig with state from external contexts
   */
  public syncWithStorage(accountsList: UserAccount[], activeId?: string): void {
    if (Array.isArray(accountsList) && accountsList.length > 0) {
      UserConfig.accounts = [...accountsList].slice(0, UserConfig.MAX_ACCOUNT_COUNT);
      if (activeId) {
        const idx = UserConfig.getAccountIndex(activeId);
        if (idx >= 0) {
          UserConfig.selectedAccount = idx;
        }
      }
      UserConfig.saveConfig();

      const event: MultiAccountEvent = {
        type: 'ACCOUNTS_SYNCED',
        selectedAccount: UserConfig.selectedAccount,
        accounts: [...UserConfig.accounts],
      };
      this.notifyObservers(event);
    }
  }

  /**
   * Subscribes to multi-account lifecycle and switching events
   */
  public subscribe(listener: (event: MultiAccountEvent) => void): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  private notifyObservers(event: MultiAccountEvent): void {
    this.listeners.forEach((listener) => {
      try {
        listener(event);
      } catch (err) {
        console.error('[MultiAccountManager] Observer error:', err);
      }
    });
  }
}

export const multiAccountManager = MultiAccountManager.getInstance();
