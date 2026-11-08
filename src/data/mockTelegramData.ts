/**
 * mockTelegramData.ts
 * Telegram initial dataset configuration.
 * Note: Following Goal 1, DEFAULT_ACCOUNTS is strictly empty [] to prevent
 * unauthenticated mock accounts from leaking into user sessions.
 */

import { User, UserAccount, Folder, TelegramApiConfig, Chat, Message } from '../types';

export const CURRENT_USER: User = {
  id: '',
  name: '',
  first_name: '',
  last_name: '',
  username: '',
  phone: '',
  avatar: '',
  isOnline: false,
  isPremium: false,
};

// Goal 1: Zero mock/test accounts. Real accounts only upon successful login.
export const DEFAULT_ACCOUNTS: UserAccount[] = [];

export const DEFAULT_FOLDERS: Folder[] = [
  { id: 'all', name: 'All Chats', nameAr: 'كل المحادثات', icon: 'all', unreadCount: 0, includedChatIds: [] },
  { id: 'personal', name: 'Personal', nameAr: 'شخصي', icon: 'user', unreadCount: 0, includedChatIds: [] },
  { id: 'channels', name: 'Channels', nameAr: 'القنوات', icon: 'megaphone', unreadCount: 0, includedChatIds: [] },
];

export const DEFAULT_TELEGRAM_API_CONFIG: TelegramApiConfig = {
  apiId: '22043994',
  apiHash: '56f64582b363d367280db96586b97801',
  dcId: 4,
  dcIp: '149.154.167.91',
  port: 443,
  connectionStatus: 'connected',
  sessionString: '',
  mtprotoVersion: '2.0 (Layer 184)',
  pingMs: 42,
};

export const INITIAL_CHATS: Chat[] = [];

export const INITIAL_MESSAGES: Record<string, Message[]> = {};

export const POPULAR_REACTIONS = ['👍', '❤️', '🔥', '🎉', '👏', '😂', '😍', '🤔'];

export const TELEGRAM_STICKERS = [
  { id: 'stk_1', emoji: '👍', url: 'https://telegram.org/img/t_logo.png', title: 'Thumbs Up', name: 'Thumbs Up' },
  { id: 'stk_2', emoji: '🔥', url: 'https://telegram.org/img/t_logo.png', title: 'Fire', name: 'Fire' },
  { id: 'stk_3', emoji: '🎉', url: 'https://telegram.org/img/t_logo.png', title: 'Party', name: 'Party' },
  { id: 'stk_4', emoji: '❤️', url: 'https://telegram.org/img/t_logo.png', title: 'Heart', name: 'Heart' },
];
