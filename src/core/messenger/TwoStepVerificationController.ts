/**
 * TwoStepVerificationController.ts
 * 
 * Direct implementation of org.telegram.messenger 2FA backend management
 * Corresponds to TwoStepVerificationActivity logic in DrKLO/Telegram Android.
 */

import { TLRPC } from '../TLRPC';
import { SRPHelper } from './SRPHelper';
import { ConnectionsManager } from '../ConnectionsManager';
import { NotificationCenter } from '../NotificationCenter';

export interface TwoStepState {
  hasPassword: boolean;
  hint: string;
  hasRecoveryEmail: boolean;
  unconfirmedEmail?: string;
  emailPattern?: string;
  pendingResetDate?: number;
  salt1?: Uint8Array | string;
  salt2?: Uint8Array | string;
}

const STORAGE_KEY_2FA = 'tg_two_step_settings_';

export class TwoStepVerificationController {
  private static instances: Map<number, TwoStepVerificationController> = new Map();
  private currentAccount: number = 0;

  private state: TwoStepState = {
    hasPassword: true,
    hint: 'Security Hint',
    hasRecoveryEmail: true,
    emailPattern: 'a***@gmail.com',
  };

  public static getInstance(account: number = 0): TwoStepVerificationController {
    let instance = TwoStepVerificationController.instances.get(account);
    if (!instance) {
      instance = new TwoStepVerificationController(account);
      TwoStepVerificationController.instances.set(account, instance);
    }
    return instance;
  }

  constructor(account: number) {
    this.currentAccount = account;
    this.loadCachedState();
  }

  private loadCachedState() {
    try {
      const raw = localStorage.getItem(`${STORAGE_KEY_2FA}${this.currentAccount}`);
      if (raw) {
        this.state = JSON.parse(raw);
      }
    } catch {
      // ignore
    }
  }

  private saveState() {
    try {
      localStorage.setItem(`${STORAGE_KEY_2FA}${this.currentAccount}`, JSON.stringify(this.state));
    } catch {
      // ignore
    }
  }

  public getState(): TwoStepState {
    return { ...this.state };
  }

  /**
   * Fetches current 2FA password settings from server:
   * account.getPassword
   */
  public async getPassword(): Promise<TLRPC.TL_account_password> {
    const conn = ConnectionsManager.getInstance(this.currentAccount);
    const req: any = {
      _: 'account.getPassword',
    };

    const res = await conn.sendRequest<TLRPC.TL_account_password>(req);

    // Update local state based on response
    if (res && res._ === 'account.password') {
      this.state.hasPassword = !!res.has_password;
      this.state.hint = res.hint || '';
      this.state.hasRecoveryEmail = !!res.has_recovery;
      this.state.emailPattern = res.login_email_pattern || (res.has_recovery ? 'u***@gmail.com' : undefined);
      this.state.unconfirmedEmail = res.email_unconfirmed_pattern;
      this.state.pendingResetDate = res.pending_reset_date;
      this.saveState();
    }

    return res;
  }

  /**
   * Sets or updates 2FA password and recovery email:
   * account.updatePasswordSettings
   */
  public async updatePasswordSettings(params: {
    currentPassword?: string;
    newPassword?: string;
    hint?: string;
    email?: string;
  }): Promise<{ ok: boolean; needEmailConfirm?: boolean; unconfirmedEmail?: string }> {
    const conn = ConnectionsManager.getInstance(this.currentAccount);

    let newHash: string | undefined;
    let newAlgo: TLRPC.PasswordKdfAlgo | undefined;

    if (params.newPassword) {
      const salt1 = SRPHelper.generateRandomSalt(32);
      const salt2 = SRPHelper.generateRandomSalt(32);
      newHash = await SRPHelper.makePasswordHash(salt1, salt2, params.newPassword);
      newAlgo = {
        _: 'passwordKdfAlgoSHA256SHA256PBKDF2',
        salt1: SRPHelper.toHex(salt1),
        salt2: SRPHelper.toHex(salt2),
      };
      this.state.salt1 = salt1;
      this.state.salt2 = salt2;
    }

    let flags = 0;
    if (newHash) flags |= 1; // has new password
    if (params.hint !== undefined) flags |= 2; // has hint
    if (params.email !== undefined) flags |= 4; // has email

    const req: any = {
      _: 'account.updatePasswordSettings',
      password: params.currentPassword ? { hash: params.currentPassword } : undefined,
      new_settings: {
        _: 'account.passwordInputSettings',
        flags,
        new_algo: newAlgo,
        new_password_hash: newHash,
        hint: params.hint,
        email: params.email,
      },
    };

    await conn.sendRequest(req);

    // If new password is empty -> removed
    if (params.newPassword === '' || params.newPassword === null) {
      this.state.hasPassword = false;
      this.state.hint = '';
      this.state.hasRecoveryEmail = false;
      this.state.emailPattern = undefined;
      this.state.unconfirmedEmail = undefined;
    } else if (params.newPassword) {
      this.state.hasPassword = true;
      if (params.hint !== undefined) this.state.hint = params.hint;
      if (params.email) {
        this.state.unconfirmedEmail = params.email;
        this.state.hasRecoveryEmail = true;
        this.state.emailPattern = `${params.email.charAt(0)}***@${params.email.split('@')[1] || 'gmail.com'}`;
      }
    }

    this.saveState();

    // Post notification to notify UI and active activities
    NotificationCenter.getInstance(this.currentAccount).postNotificationName(
      NotificationCenter.updateInterfaces,
      0x0008
    );

    const needEmailConfirm = !!params.email && params.email.length > 0;
    return {
      ok: true,
      needEmailConfirm,
      unconfirmedEmail: params.email,
    };
  }

  /**
   * Confirms recovery email via 6-digit code received on email:
   * account.confirmPasswordEmail
   */
  public async confirmEmailCode(code: string): Promise<boolean> {
    const conn = ConnectionsManager.getInstance(this.currentAccount);
    const req: TLRPC.TL_account_confirmPasswordEmail = {
      _: 'account.confirmPasswordEmail',
      code: code.trim(),
    };

    await conn.sendRequest(req);
    this.state.unconfirmedEmail = undefined;
    this.state.hasRecoveryEmail = true;
    this.saveState();

    NotificationCenter.getInstance(this.currentAccount).postNotificationName(
      NotificationCenter.updateInterfaces,
      0x0008
    );
    return true;
  }

  /**
   * Resends verification code to recovery email:
   * account.resendPasswordEmail
   */
  public async resendEmailCode(): Promise<boolean> {
    const conn = ConnectionsManager.getInstance(this.currentAccount);
    const req: TLRPC.TL_account_resendPasswordEmail = {
      _: 'account.resendPasswordEmail',
    };
    await conn.sendRequest(req);
    return true;
  }

  /**
   * Cancels email confirmation flow:
   * account.cancelPasswordEmail
   */
  public async cancelEmailConfirmation(): Promise<boolean> {
    const conn = ConnectionsManager.getInstance(this.currentAccount);
    const req: TLRPC.TL_account_cancelPasswordEmail = {
      _: 'account.cancelPasswordEmail',
    };
    await conn.sendRequest(req);
    this.state.unconfirmedEmail = undefined;
    this.saveState();
    return true;
  }

  /**
   * Initiates 7-day password reset countdown for forgotten passwords without email:
   * account.resetPassword
   */
  public async resetPassword(): Promise<{ pendingResetDate: number }> {
    const conn = ConnectionsManager.getInstance(this.currentAccount);
    const req: TLRPC.TL_account_resetPassword = {
      _: 'account.resetPassword',
    };
    await conn.sendRequest(req);
    const pendingDate = Math.floor(Date.now() / 1000) + 7 * 86400;
    this.state.pendingResetDate = pendingDate;
    this.saveState();
    return { pendingResetDate: pendingDate };
  }
}

export const twoStepController = TwoStepVerificationController.getInstance(0);
