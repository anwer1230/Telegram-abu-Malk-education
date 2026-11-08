/**
 * LoginController.ts - org.telegram.ui.LoginActivity controller
 * Handles phone authentication, SMS verification, MTProto auth methods, and session activation.
 */

import { User } from '../../types';
import { UserConfig } from './UserConfig';
import { AuthTokensHelper } from './AuthTokensHelper';
import { SharedConfig } from './SharedConfig';

export interface ExtendedUser extends User {
  firstName?: string;
  lastName?: string;
}

export interface SendCodeResult {
  success: boolean;
  phoneCodeHash: string;
  isCodeSent?: boolean;
  timeout?: number;
  deliveryType?: 'app' | 'sms';
  isRealTelegramMTProto?: boolean;
  message?: string;
  error?: string;
}

export interface SignInResult {
  success: boolean;
  user?: ExtendedUser;
  sessionString?: string;
  sessionKey?: string;
  futureAuthToken?: string;
  requiresSignUp?: boolean;
  signUpRequired?: boolean;
  requires2FA?: boolean;
  requiresPassword?: boolean;
  isRealTelegramMTProto?: boolean;
  message?: string;
  error?: string;
}

export class LoginController {
  private static instance: LoginController;

  public static getInstance(): LoginController {
    if (!LoginController.instance) {
      LoginController.instance = new LoginController();
    }
    return LoginController.instance;
  }

  public async sendCode(
    phone: string,
    sendType: string = 'app',
    apiId?: number,
    apiHash?: string
  ): Promise<SendCodeResult> {
    try {
      const res = await fetch('/api/telegram/auth/send-code', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          phone,
          deliveryType: sendType,
          apiId,
          apiHash,
        }),
      });

      const data = await res.json().catch(() => null);

      if (res.ok && data?.success) {
        return {
          success: true,
          phoneCodeHash: data.phoneCodeHash || '',
          isCodeSent: true,
          timeout: data.timeout || 60,
          deliveryType: data.deliveryType || (sendType === 'sms' ? 'sms' : 'app'),
          isRealTelegramMTProto: Boolean(data.isRealTelegramMTProto),
          message: data.message,
        };
      }

      return {
        success: false,
        phoneCodeHash: '',
        isCodeSent: false,
        error: data?.error || 'SEND_CODE_FAILED',
        message: data?.message || 'تعذر إرسال رمز التحقق من خوادم تيليجرام. يرجى التأكد من صحة رقم الهاتف والمحاولة لاحقاً.',
      };
    } catch (err: any) {
      return {
        success: false,
        phoneCodeHash: '',
        isCodeSent: false,
        error: 'NETWORK_ERROR',
        message: 'حدث خطأ في الاتصال بالخادم. يرجى التحقق من اتصال الإنترنت وإعادة المحاولة.',
      };
    }
  }

  public async resendCode(
    phone: string,
    phoneCodeHash: string
  ): Promise<SendCodeResult> {
    try {
      const res = await fetch('/api/telegram/auth/resend-code', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          phone,
          phoneCodeHash,
        }),
      });

      const data = await res.json().catch(() => null);

      if (res.ok && data?.success) {
        return {
          success: true,
          phoneCodeHash: data.phoneCodeHash || phoneCodeHash,
          isCodeSent: true,
          timeout: data.timeout || 60,
          isRealTelegramMTProto: Boolean(data.isRealTelegramMTProto),
          message: data.message,
        };
      }

      return {
        success: false,
        phoneCodeHash,
        isCodeSent: false,
        error: data?.error || 'RESEND_FAILED',
        message: data?.message || 'تعذر إعادة إرسال الرمز. يرجى الانتظار والمحاولة لاحقاً.',
      };
    } catch (err: any) {
      return {
        success: false,
        phoneCodeHash,
        isCodeSent: false,
        error: 'NETWORK_ERROR',
        message: 'خطأ في الاتصال أثناء إعادة إرسال الرمز.',
      };
    }
  }

  public async signIn(
    phone: string,
    phoneCodeHash: string,
    code: string,
    password?: string
  ): Promise<SignInResult> {
    try {
      const res = await fetch('/api/telegram/auth/verify-code', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          phone,
          phoneCodeHash,
          code,
          password,
        }),
      });

      const data = await res.json().catch(() => null);

      if (res.ok && data?.success) {
        if (data.user) {
          const extUser: ExtendedUser = {
            ...data.user,
            id: String(data.user.id || ''),
            name: data.user.name || [data.user.firstName, data.user.lastName].filter(Boolean).join(' ') || data.user.phone || '',
            firstName: data.user.firstName || data.user.first_name || '',
            lastName: data.user.lastName || data.user.last_name || '',
            first_name: data.user.firstName || data.user.first_name || '',
            last_name: data.user.lastName || data.user.last_name || '',
            phone: data.user.phone || phone,
            username: data.user.username || '',
            avatar: data.user.avatar || '',
            isOnline: true,
            isPremium: Boolean(data.user.isPremium),
          };
          this.activateUserSession(extUser, data.sessionKey || data.sessionString);
          return {
            success: true,
            user: extUser,
            sessionKey: data.sessionKey || data.sessionString,
            sessionString: data.sessionString || data.sessionKey,
            isRealTelegramMTProto: Boolean(data.isRealTelegramMTProto),
            message: data.message,
          };
        }
      }

      if (data?.requiresPassword) {
        return {
          success: false,
          requiresPassword: true,
          message: data.message || 'يتطلب الحساب كلمة مرور التحقق بخطوتين (2FA).',
        };
      }

      if (data?.signUpRequired) {
        return {
          success: false,
          signUpRequired: true,
          message: data.message || 'هذا الرقم غير مسجل في تيليجرام. يرجى إنشاء حساب جديد.',
        };
      }

      return {
        success: false,
        error: data?.error || 'VERIFY_FAILED',
        message: data?.message || 'رمز التحقق غير صحيح أو انتهت صلاحيته.',
      };
    } catch (err: any) {
      return {
        success: false,
        error: 'NETWORK_ERROR',
        message: 'خطأ في الاتصال أثناء التحقق من الرمز.',
      };
    }
  }

  public async signUp(
    phone: string,
    phoneCodeHash: string,
    code: string,
    firstName: string,
    lastName: string = ''
  ): Promise<SignInResult> {
    const user: ExtendedUser = {
      id: 'tg_' + Date.now(),
      name: [firstName, lastName].filter(Boolean).join(' '),
      first_name: firstName,
      last_name: lastName,
      firstName,
      lastName,
      phone,
      username: '',
      avatar: '',
      isOnline: true,
      isPremium: false,
    };
    const sessionStr = 'session_' + Date.now();
    this.activateUserSession(user, sessionStr);
    return {
      success: true,
      user,
      sessionString: sessionStr,
      sessionKey: sessionStr,
    };
  }

  private activateUserSession(user: User, sessionKey?: string): void {
    const config = UserConfig.getInstance(0);
    config.setCurrentUser(user);

    const tokens = AuthTokensHelper.getInstance();
    if (sessionKey) {
      tokens.saveSessionKey(0, sessionKey);
    }
    tokens.saveUserBackup(0, user);

    // Goal 3: Hardware device push binding
    tokens.protectRealUserSession(0);
    tokens.registerDeviceWithPushToken(0, SharedConfig.pushString || 'fcm_direct_token');
  }
}

export const loginController = LoginController.getInstance();
