/**
 * DownloadController.ts - org.telegram.messenger.DownloadController
 * Direct TypeScript translation of DrKLO/Telegram Android architecture
 */

import { Message } from '../../types';
import { NotificationCenter } from '../NotificationCenter';

export interface NetworkDownloadConfig {
  photos: boolean;
  videos: boolean;
  files: boolean;
  music: boolean;
  maxFileSizeMb: number;
}

export interface AutoDownloadSettings {
  mobile: NetworkDownloadConfig;
  wifi: NetworkDownloadConfig;
  roaming: NetworkDownloadConfig;
  autoPlayGifs: boolean;
  autoPlayVideos: boolean;
  streamMedia: boolean;
}

export class DownloadController {
  public static readonly AUTODOWNLOAD_MASK_PHOTO = 1;
  public static readonly AUTODOWNLOAD_MASK_AUDIO = 2;
  public static readonly AUTODOWNLOAD_MASK_VIDEO = 4;
  public static readonly AUTODOWNLOAD_MASK_DOCUMENT = 8;

  private static instances = new Map<number, DownloadController>();
  private currentAccount: number;

  private settings: AutoDownloadSettings = {
    mobile: { photos: true, videos: false, files: false, music: true, maxFileSizeMb: 10 },
    wifi: { photos: true, videos: true, files: true, music: true, maxFileSizeMb: 50 },
    roaming: { photos: false, videos: false, files: false, music: false, maxFileSizeMb: 1 },
    autoPlayGifs: true,
    autoPlayVideos: true,
    streamMedia: true,
  };

  public static getInstance(account: number = 0): DownloadController {
    if (!DownloadController.instances.has(account)) {
      DownloadController.instances.set(account, new DownloadController(account));
    }
    return DownloadController.instances.get(account)!;
  }

  private constructor(account: number) {
    this.currentAccount = account;
    this.loadSettings();
  }

  public getSettings(): AutoDownloadSettings {
    return { ...this.settings };
  }

  public updateSettings(partial: Partial<AutoDownloadSettings>): void {
    this.settings = { ...this.settings, ...partial };
    this.saveSettings();
    NotificationCenter.getInstance(this.currentAccount).postNotificationName(
      NotificationCenter.downloadSettingsUpdated,
      this.settings
    );
  }

  public setNetworkConfig(type: 'mobile' | 'wifi' | 'roaming', config: Partial<NetworkDownloadConfig>): void {
    this.settings[type] = { ...this.settings[type], ...config };
    this.saveSettings();
    NotificationCenter.getInstance(this.currentAccount).postNotificationName(
      NotificationCenter.downloadSettingsUpdated,
      this.settings
    );
  }

  private loadSettings(): void {
    if (typeof window === 'undefined') return;
    try {
      const raw = localStorage.getItem(`tg_download_settings_${this.currentAccount}`);
      if (raw) {
        this.settings = { ...this.settings, ...JSON.parse(raw) };
      }
    } catch {}
  }

  private saveSettings(): void {
    if (typeof window === 'undefined') return;
    try {
      localStorage.setItem(`tg_download_settings_${this.currentAccount}`, JSON.stringify(this.settings));
    } catch {}
  }

  public canDownloadMedia(type: number): boolean {
    const currentMask =
      DownloadController.AUTODOWNLOAD_MASK_PHOTO |
      DownloadController.AUTODOWNLOAD_MASK_AUDIO |
      DownloadController.AUTODOWNLOAD_MASK_DOCUMENT;
    return (currentMask & type) !== 0;
  }

  public checkAndDownloadMedia(message: Message): void {
    if (!message || !message.media) return;
    // Handled via FileLoader
  }
}

export const downloadController = DownloadController.getInstance();
