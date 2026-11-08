/**
 * SharedConfig.ts - org.telegram.messenger.SharedConfig
 * Telegram global shared configuration, preferences, push configuration, and UI state.
 */

export interface ProxyConfig {
  address: string;
  port: number;
  secret?: string;
  user?: string;
  password?: string;
  enabled: boolean;
}

export class SharedConfigClass {
  // Push Notification token & config
  public pushString: string = '';
  public pushType: number = 2; // 2 = Google Play Services / FCM
  public pushAuthKey: string = '';
  public pushStatSent: boolean = false;

  // Media Playback & Auto Download
  public streamMedia: boolean = true;
  public streamAllVideo: boolean = true;
  public streamAudio: boolean = true;
  public saveToGallery: boolean = false;
  public autoplayGifs: boolean = true;
  public autoplayVideo: boolean = true;
  public loopStickers: boolean = true;

  // UI & Appearance
  public fontSize: number = 16;
  public bubbleRadius: number = 16;
  public isNightMode: boolean = true;
  public useSystemFont: boolean = true;
  public drawDialogIcons: boolean = true;
  public showNotifications: boolean = true;
  public inAppSounds: boolean = true;
  public inAppVibrate: boolean = true;
  public inAppPreview: boolean = true;

  // Audio Player
  public repeatMode: number = 0; // 0 = none, 1 = repeat all, 2 = repeat one
  public shuffleMusic: boolean = false;

  // Network & Proxy
  public currentProxy: ProxyConfig | null = null;
  public proxyList: ProxyConfig[] = [];
  public proxyRotation: boolean = false;

  // Cache & Storage
  public keepMedia: number = 0; // 0 = forever, 3 = 3 days, 7 = 1 week, 30 = 1 month
  public maxSelectedPhotos: number = 100;

  private static instance: SharedConfigClass | null = null;

  constructor() {
    this.loadConfig();
  }

  public static getInstance(): SharedConfigClass {
    if (!SharedConfigClass.instance) {
      SharedConfigClass.instance = new SharedConfigClass();
    }
    return SharedConfigClass.instance;
  }

  public loadConfig(): void {
    try {
      if (typeof window !== 'undefined' && window.localStorage) {
        const saved = localStorage.getItem('tg_shared_config');
        if (saved) {
          const parsed = JSON.parse(saved);
          Object.assign(this, parsed);
        }
        const savedPush = localStorage.getItem('tg_push_token');
        if (savedPush) {
          this.pushString = savedPush;
        }
      }
    } catch (e) {
      console.warn('[SharedConfig] Failed to load config from storage', e);
    }
  }

  public saveConfig(): void {
    try {
      if (typeof window !== 'undefined' && window.localStorage) {
        const state = {
          pushString: this.pushString,
          pushType: this.pushType,
          streamMedia: this.streamMedia,
          streamAllVideo: this.streamAllVideo,
          streamAudio: this.streamAudio,
          saveToGallery: this.saveToGallery,
          autoplayGifs: this.autoplayGifs,
          autoplayVideo: this.autoplayVideo,
          loopStickers: this.loopStickers,
          fontSize: this.fontSize,
          bubbleRadius: this.bubbleRadius,
          isNightMode: this.isNightMode,
          showNotifications: this.showNotifications,
          inAppSounds: this.inAppSounds,
          inAppVibrate: this.inAppVibrate,
          inAppPreview: this.inAppPreview,
          repeatMode: this.repeatMode,
          shuffleMusic: this.shuffleMusic,
          currentProxy: this.currentProxy,
          proxyList: this.proxyList,
          keepMedia: this.keepMedia,
        };
        localStorage.setItem('tg_shared_config', JSON.stringify(state));
        if (this.pushString) {
          localStorage.setItem('tg_push_token', this.pushString);
        }
      }
    } catch (e) {
      console.warn('[SharedConfig] Failed to save config to storage', e);
    }
  }

  public setPushString(token: string): void {
    this.pushString = token;
    this.saveConfig();
  }

  public toggleNightMode(): boolean {
    this.isNightMode = !this.isNightMode;
    this.saveConfig();
    return this.isNightMode;
  }
}

export const SharedConfig = SharedConfigClass.getInstance();
