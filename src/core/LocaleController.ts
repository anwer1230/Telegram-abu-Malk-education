/**
 * LocaleController.ts - org.telegram.messenger.LocaleController
 * Replicated directly from DrKLO/Telegram Android
 * 
 * Provides centralized string localization and RTL management
 * for chat activities, channel headers, bottom panel restrictions, and MTProto errors.
 */

export class LocaleController {
  private static currentLocale: 'ar' | 'en' = 'ar';
  private static listeners: Set<(locale: 'ar' | 'en') => void> = new Set();

  private static strings: Record<string, { ar: string; en: string }> = {
    // Bottom Panel & Channel Restrictions
    ChannelBroadcastRestricted: {
      ar: 'فقط المشرفين يمكنهم النشر في هذه القناة',
      en: 'Only administrators can post in this channel',
    },
    ChannelRestricted: {
      ar: 'تم تقييد إمكانية إرسال الرسائل في هذه المجموعة',
      en: 'Sending messages is restricted in this group',
    },
    ChannelMute: {
      ar: 'كتم الإشعارات',
      en: 'MUTE',
    },
    ChannelUnmute: {
      ar: 'إلغاء الكتم',
      en: 'UNMUTE',
    },
    Discussion: {
      ar: 'مناقشة',
      en: 'DISCUSS',
    },
    ChannelJoin: {
      ar: 'انضمام للقناة',
      en: 'JOIN',
    },
    GroupJoin: {
      ar: 'انضمام للمجموعة',
      en: 'JOIN GROUP',
    },
    WriteAMessage: {
      ar: 'اكتب رسالة...',
      en: 'Write a message...',
    },
    SaveNote: {
      ar: 'احفظ ملاحظة أو رسالة في سحابة تيليجرام...',
      en: 'Save a note or file to your cloud storage...',
    },
    AttachMedia: {
      ar: 'إرفاق وسائط',
      en: 'Attach media',
    },
    SlowmodeWait: {
      ar: 'الوضع البطيء مفعّل. يرجى الانتظار {seconds} ثانية',
      en: 'Slow mode is active. Please wait {seconds} seconds',
    },
    YouWereKicked: {
      ar: 'تم حظرك من هذه المحادثة',
      en: 'You were kicked from this chat',
    },
    YouLeft: {
      ar: 'لقد غادرت هذه المجموعة',
      en: 'You have left this group',
    },
    BotCommands: {
      ar: 'أوامر البوت المتاحة',
      en: 'Available Bot Commands',
    },
  };

  public static setLocale(locale: 'ar' | 'en'): void {
    if (this.currentLocale !== locale) {
      this.currentLocale = locale;
      this.listeners.forEach((cb) => cb(locale));
    }
  }

  public static getLocale(): 'ar' | 'en' {
    return this.currentLocale;
  }

  public static isRTL(): boolean {
    return this.currentLocale === 'ar';
  }

  public static addListener(listener: (locale: 'ar' | 'en') => void): () => void {
    this.listeners.add(listener);
    return () => {
      this.listeners.delete(listener);
    };
  }

  /**
   * Matches org.telegram.messenger.LocaleController.getString(String key, int resId)
   */
  public static getString(key: string, _resId?: number): string {
    const entry = this.strings[key];
    if (!entry) {
      return key;
    }
    return entry[this.currentLocale] || entry.en || key;
  }

  /**
   * Matches LocaleController.formatString(String key, int resId, Object... args)
   */
  public static formatString(key: string, resId?: number, ...args: any[]): string {
    let str = this.getString(key, resId);
    args.forEach((arg, index) => {
      str = str.replace(new RegExp(`\\{${index}\\}`, 'g'), String(arg));
    });
    return str;
  }
}
