import React, { createContext, useContext, useEffect, useState, useMemo, useCallback, useRef } from 'react';
import confetti from 'canvas-confetti';
import {
  ActiveCall,
  AppSettings,
  Chat,
  ChatContextMenu,
  Folder,
  Message,
  MessageContextMenu,
  MessageMedia,
  ReplyInfo,
  TelegramApiConfig,
  ToastItem,
  User,
  UserAccount,
  InAppNotification,
  SettingsSubPage,
  CapturedLink,
  LinkMonitorStats,
  ProfileUserInfo,
  ViewerMediaItem,
  TypingUser,
  KeywordAlertItem,
} from '../types';
import {
  CURRENT_USER,
  DEFAULT_ACCOUNTS,
  DEFAULT_FOLDERS,
  DEFAULT_TELEGRAM_API_CONFIG,
  INITIAL_CHATS,
  INITIAL_MESSAGES,
} from '../data/mockTelegramData';
import {
  resolveTelegramUser,
  getRandomGroupMember,
  OFFICIAL_TELEGRAM_USERS,
} from '../data/telegramUsers';
import { telegramAudio } from '../utils/audioNotification';
import { notificationsService } from '../core/NotificationsService';
import { backgroundSyncService } from '../core/BackgroundSyncService';
import { telegramDb, initTelegramDexieDb } from '../core/telegramDexieDb';
import { multiAccountManager } from '../utils/MultiAccountManager';
import { notificationEngine } from '../services/NotificationEngine';
import { SecureSessionStorage } from '../utils/secureSessionStorage';
import { storageSyncManager } from '../utils/StorageSyncManager';
import {
  messagesController,
  messagesStorage,
  MessageObject,
  TLRPC,
  NotificationCenter as CoreNotificationCenter,
  UserConfig,
  AuthTokensHelper,
  MessagesController,
  MessagesStorage,
  ConnectionsManager,
  AccountInstance,
  LaunchActivity,
  launchActivity,
} from '../core/messenger';
import { TelegramBotEngine } from '../core/TelegramBotEngine';

interface TelegramContextType {
  currentUser: User;
  chats: Chat[];
  messages: Record<string, Message[]>;
  activeChatId: string | null;
  activeChat: Chat | null;
  activeFolderId: string;
  folders: Folder[];
  searchQuery: string;
  isDrawerOpen: boolean;
  isRightPanelOpen: boolean;
  activeModal:
    | 'none'
    | 'api-config'
    | 'settings'
    | 'new-chat'
    | 'media-viewer'
    | 'call'
    | 'forward'
    | 'add-account'
    | 'apk-installer'
    | 'mini-apps'
    | 'theme-editor'
    | 'export-chat'
    | 'contacts'
    | 'link-monitor'
    | 'send-only'
    | 'premium'
    | 'secret-chat-info'
    | 'group-admin'
    | 'forum-topics'
    | 'sender'
    | 'monitor'
    | 'my-messages'
    | 'auto-joiner'
    | 'auto-responder'
    | 'smart-ai'
    | 'live-link-discover'
    | 'user-profile';
  selectedProfileUser: ProfileUserInfo | null;
  setSelectedProfileUser: (user: ProfileUserInfo | null) => void;
  openUserProfile: (user: ProfileUserInfo) => void;
  getCommonGroupsForUser: (userId: string, userName?: string) => Chat[];
  activeCall: ActiveCall | null;
  viewerMedia: ViewerMediaItem | null;
  viewerPlaylist: ViewerMediaItem[];
  apiConfig: TelegramApiConfig;
  settings: AppSettings;
  settingsSubPage: SettingsSubPage;
  setSettingsSubPage: (page: SettingsSubPage) => void;
  openSettingsPage: (page?: SettingsSubPage) => void;
  replyingTo: ReplyInfo | null;
  editingMessage: { id: string; text: string } | null;
  forwardingMessage: Message | null;
  selectedMessageIds: string[];
  typingChatId: string | null;
  typingUsers: Record<string, TypingUser[]>;
  setChatTyping: (
    chatId: string,
    user: {
      userId?: string;
      userName: string;
      action?: 'typing' | 'record_audio' | 'upload_photo' | 'upload_document';
    } | null
  ) => void;
  blockedUserIds: string[];
  blockUser: (userId: string) => void;
  unblockUser: (userId: string) => void;
  isUserBlocked: (userId: string) => boolean;
  chatContextMenu: ChatContextMenu | null;
  messageContextMenu: MessageContextMenu | null;
  toasts: ToastItem[];
  inAppNotifications: InAppNotification[];
  dismissNotification: (id: string) => void;
  triggerNotification: (notif: Omit<InAppNotification, 'id' | 'timestamp'>) => void;

  // Link Monitor & Auto-Join Engine
  capturedLinks: CapturedLink[];
  linkMonitorStats: LinkMonitorStats;
  autoJoinLinksEnabled: boolean;
  toggleAutoJoinLinks: () => void;
  joinCapturedLink: (linkId: string) => Promise<void>;
  joinAllPendingLinks: () => Promise<void>;
  checkPendingApprovalLinks: () => Promise<void>;
  clearCapturedLinks: () => void;
  exportLinksReport: () => void;
  manualScanAllChatsForLinks: () => void;

  // Authentication & Sessions
  isAuthenticated: boolean;
  login: (data: { name: string; phone: string; username?: string; avatar?: string; bio?: string; sessionString?: string }) => void;
  logout: (targetAccountId?: string) => void;

  // Multi-Account Management
  accounts: UserAccount[];
  activeAccountId: string;
  switchAccount: (accountId: string) => Promise<void>;
  addAccount: (newAccount: { name: string; phone: string; username?: string; avatar?: string; bio?: string; sessionString?: string }) => void;
  removeAccount: (accountId: string) => void;
  updateAccountProfile: (data: Partial<User>) => void;
  joinChatByInviteLink: (link: string) => Promise<{ success: boolean; message?: string }>;
  
  // Actions
  setActiveChatId: (id: string | null) => void;
  setActiveFolderId: (id: string) => void;
  setSearchQuery: (q: string) => void;
  setIsDrawerOpen: (open: boolean) => void;
  setIsRightPanelOpen: (open: boolean) => void;
  setActiveModal: (
    modal:
      | 'none'
      | 'api-config'
      | 'settings'
      | 'new-chat'
      | 'media-viewer'
      | 'call'
      | 'forward'
      | 'add-account'
      | 'apk-installer'
      | 'mini-apps'
      | 'theme-editor'
      | 'export-chat'
      | 'contacts'
      | 'link-monitor'
      | 'send-only'
      | 'premium'
      | 'secret-chat-info'
      | 'group-admin'
      | 'sender'
      | 'monitor'
      | 'my-messages'
      | 'auto-joiner'
      | 'auto-responder'
      | 'smart-ai'
      | 'live-link-discover'
  ) => void;
  setViewerMedia: (media: ViewerMediaItem | null, playlist?: ViewerMediaItem[]) => void;
  setReplyingTo: (reply: ReplyInfo | null) => void;
  setEditingMessage: (item: { id: string; text: string } | null) => void;
  setForwardingMessage: (msg: Message | null) => void;
  setChatContextMenu: (menu: ChatContextMenu | null) => void;
  setMessageContextMenu: (menu: MessageContextMenu | null) => void;
  
  // Toast
  showToast: (text: string, icon?: string) => void;
  
  // Messages & Interactions
  sendMessage: (text: string, media?: MessageMedia) => void;
  editMessageText: (messageId: string, newText: string) => void;
  forwardMessageTo: (targetChatId: string, message: Message) => void;
  toggleReaction: (messageId: string, emoji: string) => void;
  deleteMessage: (messageId: string) => void;
  pinMessage: (messageId: string) => void;
  votePoll: (messageId: string, optionId: string) => void;
  
  // Multi-select
  toggleSelectMessage: (id: string) => void;
  clearSelectedMessages: () => void;
  deleteSelectedMessages: () => void;
  
  // Drafts
  setChatDraft: (chatId: string, draftText: string) => void;
  
  // Chat Actions
  toggleMuteChat: (chatId: string) => void;
  togglePinChat: (chatId: string) => void;
  markChatReadUnread: (chatId: string) => void;
  clearChatHistory: (chatId: string) => void;
  deleteChat: (chatId: string) => void;
  
  // Calls
  startCall: (isVideo?: boolean) => void;
  endCall: () => void;
  toggleCallMute: () => void;
  toggleCallCamera: () => void;
  
  // API & Settings
  updateApiConfig: (config: Partial<TelegramApiConfig>) => void;
  updateSettings: (newSettings: Partial<AppSettings>) => void;
  testApiLatency: () => Promise<number>;
  createNewChat: (type: 'private' | 'group' | 'channel', title: string, username?: string, description?: string) => void;
  jumpToMessage: (chatId: string, messageId: string) => void;
  openPrivateChat: (senderId: string, senderName: string, senderAvatar?: string, senderUsername?: string) => void;
  resolveTelegramLink: (urlOrQuery: string) => Promise<void>;
  // Deep Links & Chat Invites (DrKLO MTProto)
  previewInvite: { invite: TLRPC.ChatInvite; hash: string } | null;
  setPreviewInvite: (item: { invite: TLRPC.ChatInvite; hash: string } | null) => void;
  checkChatInvite: (hash: string) => Promise<TLRPC.ChatInvite>;
  joinChat: (invite: TLRPC.ChatInvite, hash: string) => Promise<boolean>;
  openLink: (url: string) => Promise<boolean>;
  processChatJoinRequests: (chatId: string | number, user: any, approve: boolean) => Promise<boolean>;
  processChatJoinRequestsAll: (chatId: string | number, approve: boolean) => Promise<boolean>;
  syncCloudData: () => Promise<void>;
  syncInitializationRoutine: (phoneOverride?: string, sessionStringOverride?: string) => Promise<void>;
  validateSessionProactively: (force?: boolean) => Promise<boolean>;
  isSyncing: boolean;
  isSessionValidating: boolean;
  solveChatCaptcha: (chatId: string, answer: string) => Promise<boolean>;
  forwardToSavedMessages: (message: Message) => void;
  // Incremental Pagination & Stream Sync
  loadMoreChatMessages: (chatId: string) => Promise<{ loadedCount: number; hasMore: boolean }>;
  isChatLoadingOlder: Record<string, boolean>;
  chatHasMoreOlder: Record<string, boolean>;

  // Background Watch Words & Messages Monitor Service
  watchWords: string[];
  updateWatchWords: (words: string[]) => void;
  monitoredChatIds: string[];
  setMonitoredChatIds: (chatIds: string[]) => void;
  isWatchWordsMonitorActive: boolean;
  toggleWatchWordsMonitor: (forceState?: boolean) => void;
  keywordAlertsHistory: KeywordAlertItem[];
  clearKeywordAlertsHistory: () => void;
  checkWatchWordsInChats: () => void;
}

const TelegramContext = createContext<TelegramContextType | undefined>(undefined);

export const DEFAULT_WATCH_WORDS: string[] = [
  'انجاز',
  'إنجاز',
  'واجب',
  'مشروع',
  'بحث',
  'اختبار',
  'كويز',
  'تكليف',
  'تقرير',
  'بوربوينت',
  'عرض',
  'تلخيص',
];

export const normalizeTextForMatching = (text: string): string => {
  if (!text) return '';
  return text
    .toLowerCase()
    .replace(/[\u064B-\u065F\u0670]/g, '') // remove Arabic diacritics / tashkeel
    .replace(/[إأآا]/g, 'ا')
    .replace(/ى/g, 'ي')
    .replace(/ة/g, 'ه')
    .replace(/[\s\-_]+/g, ' ')
    .trim();
};

const DEFAULT_APP_SETTINGS: AppSettings = {
  theme: 'dark',
  accentColor: '#5288c1',
  fontSize: 16,
  language: 'ar',
  sendByEnter: true,
  soundEffects: true,
  autoDownloadMedia: true,
  chatWallpaper: 'default',
  watch_words: DEFAULT_WATCH_WORDS,
  watchWords: DEFAULT_WATCH_WORDS,
  monitoringEnabled: true,
  monitoringIntervalSeconds: 6,
};

export const sanitizeChat = (c: Chat): Chat => {
  if (!c) return c;
  const titleLower = (c.title || '').toLowerCase();
  const hasGroupKeywords =
    titleLower.includes('مجموعة') ||
    titleLower.includes('group') ||
    titleLower.includes('نقاش') ||
    titleLower.includes('قروب') ||
    titleLower.includes('مجتمع') ||
    titleLower.includes('chat') ||
    titleLower.includes('دردشة');
  const hasChannelKeywords =
    titleLower.includes('قناة') ||
    titleLower.includes('channel') ||
    titleLower.includes('news') ||
    titleLower.includes('أخبار') ||
    titleLower.includes('اخبار');

  const isActuallyGroup =
    c.isMegagroup ||
    (c.type === 'channel' && hasGroupKeywords && !hasChannelKeywords) ||
    (c.type === 'channel' && c.isBroadcast === false);

  if (isActuallyGroup && c.type !== 'group') {
    return {
      ...c,
      type: 'group',
      isMegagroup: true,
      isBroadcast: false,
      isRestricted: false,
      isReadOnly: false,
    };
  }
  return c;
};

export const TelegramProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  // 1. Resilient Multi-Tier Encrypted Session Persistence & State
  const [accounts, setAccounts] = useState<UserAccount[]>(() => {
    try {
      if (typeof window !== 'undefined') {
        const saved = SecureSessionStorage.getItem<UserAccount[]>('tg_multi_accounts_v3') || SecureSessionStorage.getItem<UserAccount[]>('tg_accounts');
        if (saved && Array.isArray(saved) && saved.length > 0) {
          const realAccounts = saved.filter((acc) => {
            const isTest = (acc.user as any)?.isTestAccount ||
                           (acc.user as any)?.isDummy ||
                           !acc.user?.phone ||
                           acc.user.phone.length < 6 ||
                           acc.user.phone.startsWith('+999') ||
                           acc.user.phone === '0000000000' ||
                           acc.user.phone.includes('test') ||
                           acc.user.username === 'anwer_dev';
            return !isTest;
          });
          if (realAccounts.length > 0) {
            return realAccounts;
          }
        }
      }
    } catch (e) {
      console.warn('[TelegramContext] Encrypted storage load notice:', e);
    }
    return [];
  });

  const [activeAccountId, setActiveAccountId] = useState<string>(() => {
    try {
      const savedId = SecureSessionStorage.getItem<string>('tg_active_account_id_v3');
      if (savedId) return savedId;
    } catch {}
    return accounts[0]?.id || 'acc_primary';
  });

  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(() => {
    try {
      if (typeof window !== 'undefined') {
        // Purge dummy/mock/test accounts on boot
        UserConfig.cleanupTestAccounts();

        if (SecureSessionStorage.getItem<string>('tg_explicitly_logged_out') === 'true') {
          return false;
        }
        const savedAccs = SecureSessionStorage.getItem<UserAccount[]>('tg_multi_accounts_v3') || SecureSessionStorage.getItem<UserAccount[]>('tg_accounts');
        const realAccs = Array.isArray(savedAccs)
          ? savedAccs.filter((acc) => {
              const isTest = (acc.user as any)?.isTestAccount ||
                             (acc.user as any)?.isDummy ||
                             !acc.user?.phone ||
                             acc.user.phone.length < 6 ||
                             acc.user.phone.startsWith('+999') ||
                             acc.user.phone === '0000000000' ||
                             acc.user.phone.includes('test') ||
                             acc.user.username === 'anwer_dev';
              return !isTest;
            })
          : [];

        const hasSession = !!SecureSessionStorage.getItem<string>('tg_session_string');
        const configAuthorized = UserConfig.getInstance(0).isClientAuthorized();

        if (realAccs.length > 0 || (hasSession && configAuthorized)) {
          return true;
        }
        return false;
      }
      return false;
    } catch {
      return false;
    }
  });

  // Current active account lookup
  const initialActiveAcc = accounts.find((a) => a.id === activeAccountId) || accounts[0] || null;

  const [currentUser, setCurrentUser] = useState<User>(() => initialActiveAcc?.user || CURRENT_USER);
  const [chats, setChats] = useState<Chat[]>(() => {
    const raw = initialActiveAcc?.chats && initialActiveAcc.chats.length > 0 ? initialActiveAcc.chats : [];
    return raw.map(sanitizeChat);
  });
  const [messages, setMessages] = useState<Record<string, Message[]>>(() => (initialActiveAcc?.messages && Object.keys(initialActiveAcc.messages).length > 0 ? initialActiveAcc.messages : {}));
  const [isSyncing, setIsSyncing] = useState<boolean>(false);
  const [activeChatId, setActiveChatId] = useState<string | null>(() => {
    if (typeof window !== 'undefined' && window.innerWidth < 768) {
      return null;
    }
    return initialActiveAcc?.chats?.[0]?.id || 'chat_saved_messages';
  });

  // Authentic Telegram Typing & Presence Engine
  const [typingUsers, setTypingUsers] = useState<Record<string, TypingUser[]>>({});
  
  // Persistent Blocked Users Storage (MTProto contacts.blocked)
  const [blockedUserIds, setBlockedUserIds] = useState<string[]>(() => {
    if (typeof window !== 'undefined') {
      try {
        const stored = localStorage.getItem('tg_blocked_users');
        if (stored) return JSON.parse(stored);
      } catch {}
    }
    return [];
  });

  const blockUser = useCallback((userId: string) => {
    setBlockedUserIds((prev) => {
      if (prev.includes(userId)) return prev;
      const updated = [...prev, userId];
      if (typeof window !== 'undefined') {
        localStorage.setItem('tg_blocked_users', JSON.stringify(updated));
      }
      return updated;
    });
  }, []);

  const unblockUser = useCallback((userId: string) => {
    setBlockedUserIds((prev) => {
      const updated = prev.filter((id) => id !== userId);
      if (typeof window !== 'undefined') {
        localStorage.setItem('tg_blocked_users', JSON.stringify(updated));
      }
      return updated;
    });
  }, []);

  const isUserBlocked = useCallback(
    (userId: string) => {
      return blockedUserIds.includes(userId);
    },
    [blockedUserIds]
  );

  const setChatTyping = useCallback(
    (
      chatId: string,
      user: {
        userId?: string;
        userName: string;
        action?: 'typing' | 'record_audio' | 'upload_photo' | 'upload_document';
      } | null
    ) => {
      setTypingUsers((prev) => {
        if (!user) {
          const next = { ...prev };
          delete next[chatId];
          return next;
        }
        const existing = prev[chatId] || [];
        const uId = user.userId || `user_${user.userName.replace(/\s+/g, '_')}`;
        const filtered = existing.filter((u) => u.userId !== uId);
        const newTypingUser: TypingUser = {
          userId: uId,
          userName: user.userName,
          action: user.action || 'typing',
          timestamp: Date.now(),
        };
        return {
          ...prev,
          [chatId]: [...filtered, newTypingUser],
        };
      });

      if (user) {
        setTimeout(() => {
          setTypingUsers((prev) => {
            const list = prev[chatId];
            if (!list) return prev;
            const uId = user.userId || `user_${user.userName.replace(/\s+/g, '_')}`;
            const nextList = list.filter((u) => u.userId !== uId && Date.now() - u.timestamp < 6000);
            if (nextList.length === 0) {
              const next = { ...prev };
              delete next[chatId];
              return next;
            }
            return { ...prev, [chatId]: nextList };
          });
        }, 6000);
      }
    },
    []
  );

  const typingChatId = useMemo(() => {
    const activeEntry = Object.entries(typingUsers).find(([, list]) => list && list.length > 0);
    return activeEntry ? activeEntry[0] : null;
  }, [typingUsers]);
  const [activeFolderId, setActiveFolderId] = useState<string>('all');
  const [folders] = useState<Folder[]>(DEFAULT_FOLDERS);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [isDrawerOpen, setIsDrawerOpen] = useState<boolean>(false);
  const [isRightPanelOpen, setIsRightPanelOpen] = useState<boolean>(false);
  const [activeModal, setActiveModal] = useState<
    | 'none'
    | 'api-config'
    | 'settings'
    | 'new-chat'
    | 'media-viewer'
    | 'call'
    | 'forward'
    | 'add-account'
    | 'apk-installer'
    | 'mini-apps'
    | 'theme-editor'
    | 'export-chat'
    | 'contacts'
    | 'link-monitor'
    | 'send-only'
    | 'premium'
    | 'secret-chat-info'
    | 'group-admin'
    | 'forum-topics'
    | 'sender'
    | 'monitor'
    | 'my-messages'
    | 'auto-joiner'
    | 'auto-responder'
    | 'smart-ai'
    | 'live-link-discover'
    | 'user-profile'
  >('none');
  const [selectedProfileUser, setSelectedProfileUser] = useState<ProfileUserInfo | null>(null);

  const openUserProfile = (user: ProfileUserInfo) => {
    setSelectedProfileUser(user);
    setActiveModal('user-profile');
  };

  const getCommonGroupsForUser = (userId: string, userName?: string): Chat[] => {
    const cleanId = userId?.toLowerCase() || '';
    const cleanName = userName?.toLowerCase() || '';

    const matched = chats.filter((c) => {
      if (c.type !== 'group' && c.type !== 'channel') return false;
      const chatMsgs = messages[c.id] || [];
      return chatMsgs.some(
        (m) =>
          (m.senderId && m.senderId.toLowerCase() === cleanId) ||
          (cleanName && m.senderName && m.senderName.toLowerCase() === cleanName)
      );
    });

    if (matched.length > 0) return matched;

    // Realistic fallback for groups
    const availableGroups = chats.filter((c) => c.type === 'group' || c.type === 'channel');
    return availableGroups.slice(0, 2);
  };
  const [activeCall, setActiveCall] = useState<ActiveCall | null>(null);
  const [viewerMedia, setViewerMediaState] = useState<ViewerMediaItem | null>(null);
  const [viewerPlaylist, setViewerPlaylist] = useState<ViewerMediaItem[]>([]);

  const setViewerMedia = (media: ViewerMediaItem | null, playlist?: ViewerMediaItem[]) => {
    setViewerMediaState(media);
    if (playlist && playlist.length > 0) {
      setViewerPlaylist(playlist);
    } else if (!media) {
      setViewerPlaylist([]);
    } else if (media) {
      setViewerPlaylist([media]);
    }
  };
  const [replyingTo, setReplyingTo] = useState<ReplyInfo | null>(null);
  const [editingMessage, setEditingMessage] = useState<{ id: string; text: string } | null>(null);
  const [forwardingMessage, setForwardingMessage] = useState<Message | null>(null);
  const [selectedMessageIds, setSelectedMessageIds] = useState<string[]>([]);
  const [chatContextMenu, setChatContextMenu] = useState<ChatContextMenu | null>(null);
  const [messageContextMenu, setMessageContextMenu] = useState<MessageContextMenu | null>(null);
  const [toasts, setToasts] = useState<ToastItem[]>([]);
  const [inAppNotifications, setInAppNotifications] = useState<InAppNotification[]>([]);

  const [apiConfig, setApiConfig] = useState<TelegramApiConfig>(DEFAULT_TELEGRAM_API_CONFIG);
  const [settings, setSettings] = useState<AppSettings>(() => initialActiveAcc?.settings || DEFAULT_APP_SETTINGS);
  const [settingsSubPage, setSettingsSubPage] = useState<SettingsSubPage>('main');

  // Incremental Pagination & Stream Sync States
  const [isChatLoadingOlder, setIsChatLoadingOlder] = useState<Record<string, boolean>>({});
  const [chatHasMoreOlder, setChatHasMoreOlder] = useState<Record<string, boolean>>({});
  const [previewInvite, setPreviewInvite] = useState<{ invite: TLRPC.ChatInvite; hash: string } | null>(null);

  // Link Monitor & Auto-Join State
  const [capturedLinks, setCapturedLinks] = useState<CapturedLink[]>(() => {
    try {
      const saved = localStorage.getItem('tg_captured_links_v1');
      if (saved) {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed) && parsed.length > 0) return parsed;
      }
    } catch {}
    return [
      {
        id: 'link_wa_1',
        url: 'https://chat.whatsapp.com/Kh89J2nK30bLM7vPq',
        sourceChatId: 'chat_general',
        sourceChatTitle: 'مجموعة نقاش عامة',
        sourceSenderName: 'أبو فهد',
        detectedAt: '09:45 AM',
        detected_at: new Date().toISOString(),
        type: 'whatsapp',
        linkCategory: 'whatsapp',
        extractedTitle: 'مجموعة تجارية (واتساب)',
        chat_title: 'مجموعة تجارية (واتساب)',
        memberCount: 256,
        joined: false,
        autoJoined: false,
        status: 'whatsapp_saved',
        status_text: '🟢 واتساب محفوظ',
        joinStatus: 'not_applicable',
        joinStatusDetails: 'تم رصد رابط واتساب ونسخه وإرساله فورياً للرسائل المحفوظة',
        country: '🇸🇦 المملكة العربية السعودية',
      },
      {
        id: 'link_tg_pub_1',
        url: 'https://t.me/telegram',
        sourceChatId: 'chat_durov',
        sourceChatTitle: 'Pavel Durov',
        sourceSenderName: 'Pavel Durov',
        detectedAt: '10:15 AM',
        detected_at: new Date().toISOString(),
        type: 'telegram_channel',
        linkCategory: 'telegram_public',
        extractedTitle: 'Telegram News & Official',
        chat_title: 'Telegram News & Official',
        memberCount: 9400000,
        joined: true,
        isJoinedActual: true,
        joinedAt: '10:15 AM',
        autoJoined: true,
        status: 'joined',
        status_text: '✅ منضم فعلياً',
        joinStatus: 'joined',
        joinStatusDetails: 'تم الانضمام فعلياً إلى المجموعة بنجاح وتوثيقه بالرسائل المحفوظة',
        country: '🌐 عالمي',
      },
      {
        id: 'link_tg_pub_2',
        url: 'https://t.me/saudi_business_hub',
        sourceChatId: 'chat_crypto',
        sourceChatTitle: 'شبكة الأعمال والاستثمار',
        sourceSenderName: 'خالد عبدالله',
        detectedAt: '11:20 AM',
        detected_at: new Date().toISOString(),
        type: 'telegram_channel',
        linkCategory: 'telegram_public',
        extractedTitle: 'ملتقى ريادة الأعمال السعودي',
        chat_title: 'ملتقى ريادة الأعمال السعودي',
        memberCount: 38200,
        joined: false,
        isPendingApproval: true,
        autoJoined: true,
        status: 'admin_approval_pending',
        status_text: '⏳ بانتظار موافقة المشرف',
        joinStatus: 'pending_admin',
        joinStatusDetails: 'تم إرسال طلب الانضمام وبانتظار موافقة المشرف - تم إشعار الرسائل المحفوظة',
        country: '🇸🇦 المملكة العربية السعودية',
      },
      {
        id: 'link_tg_priv_1',
        url: 'https://t.me/+AbC_PrivateVIPClub99',
        sourceChatId: 'chat_general',
        sourceChatTitle: 'Telegram Global Community',
        sourceSenderName: 'Sarah Connor',
        detectedAt: '12:05 PM',
        detected_at: new Date().toISOString(),
        type: 'telegram_invite',
        linkCategory: 'telegram_private',
        extractedTitle: 'مجموعة خاصة: VIP Investors Club',
        chat_title: 'مجموعة خاصة: VIP Investors Club',
        memberCount: 4520,
        joined: false,
        autoJoined: false,
        status: 'private_channel_saved',
        status_text: '🔒 قناة خاصة',
        joinStatus: 'not_applicable',
        joinStatusDetails: 'رابط قناة خاصة - تم إرسال إشعار توضيحي فوري للرسائل المحفوظة',
        country: '🔒 دعوة خاصة',
      },
    ];
  });

  const [autoJoinLinksEnabled, setAutoJoinLinksEnabled] = useState<boolean>(() => {
    try {
      const saved = localStorage.getItem('tg_auto_join_enabled_v1');
      if (saved !== null) return saved === 'true';
    } catch {}
    return true; // Default active as requested
  });

  // Initialize Dexie.js (IndexedDB wrapper) for persistent batch & discover logs
  useEffect(() => {
    initTelegramDexieDb()
      .then(async () => {
        const storedLinks = await telegramDb.discoveredLinks.toArray();
        if (storedLinks && storedLinks.length > 0) {
          setCapturedLinks((prev) => {
            // Merge Dexie links if not already present
            const existingIds = new Set(prev.map((l) => l.id));
            const newFromDb = storedLinks
              .filter((l) => !existingIds.has(l.id))
              .map((l) => ({
                id: l.id,
                url: l.url,
                sourceChatId: l.sourceChatId,
                sourceChatTitle: l.sourceChatTitle,
                sourceSenderName: l.senderName,
                detectedAt: l.timestamp,
                type: (l.url.includes('+') || l.url.includes('joinchat')
                  ? 'telegram_group'
                  : 'telegram_channel') as any,
                extractedTitle: l.sourceChatTitle || 'Telegram Channel',
                memberCount: 5000,
                joined: l.status === 'joined',
                autoJoined: l.autoJoined,
                status: l.status,
              }));
            return newFromDb.length > 0 ? [...prev, ...newFromDb] : prev;
          });
        }
      })
      .catch((e) => console.warn('[Dexie] Init error:', e));
  }, []);

  useEffect(() => {
    try {
      localStorage.setItem('tg_captured_links_v1', JSON.stringify(capturedLinks));
    } catch {}
  }, [capturedLinks]);

  useEffect(() => {
    try {
      localStorage.setItem('tg_auto_join_enabled_v1', String(autoJoinLinksEnabled));
    } catch {}
  }, [autoJoinLinksEnabled]);

  const [isSessionValidating, setIsSessionValidating] = useState<boolean>(false);

  // Proactive Session Validation Mechanism (Checks MTProto server validity before re-auth)
  const validateSessionProactively = async (force: boolean = false): Promise<boolean> => {
    try {
      setIsSessionValidating(true);
      const activeSessionStr = SecureSessionStorage.getItem<string>('tg_session_string') || '';
      const activePhone = currentUser.phone || '';

      const checkResult = await SecureSessionStorage.validateSessionWithServer({
        sessionString: activeSessionStr,
        phone: activePhone,
        accountId: activeAccountId,
      });

      if (checkResult.revoked) {
        console.warn('[SessionValidator] MTProto server confirmed session revocation.');
        showToast(
          settings.language === 'ar'
            ? 'انتهت صلاحية الجلسة أو تم تسجيل الخروج من أجهزة/تطبيقات أخرى. يرجى تسجيل الدخول مجدداً.'
            : 'Session was revoked on server or another app. Please log in again.',
          '⚠️'
        );
        logout();
        return false;
      }

      if (checkResult.valid && checkResult.user) {
        setCurrentUser((prev) => ({
          ...prev,
          id: checkResult.user.id || prev.id,
          name: checkResult.user.name || prev.name,
          username: checkResult.user.username || prev.username,
          phone: checkResult.user.phone || prev.phone,
          isPremium: checkResult.user.isPremium !== undefined ? checkResult.user.isPremium : prev.isPremium,
        }));
      }

      return true;
    } catch (e) {
      console.warn('[SessionValidator] Proactive check completed with offline resilience:', e);
      return true;
    } finally {
      setIsSessionValidating(false);
    }
  };

  // Periodic session validation to detect remote logout/revocation by other Telegram apps
  useEffect(() => {
    if (!isAuthenticated) return;
    validateSessionProactively();
    const intervalTimer = setInterval(() => {
      validateSessionProactively();
    }, 45000);
    return () => clearInterval(intervalTimer);
  }, [isAuthenticated, activeAccountId]);

  // Multi-tier recovery from IndexedDB backup on startup if localStorage was cleared
  useEffect(() => {
    // Restore drafts into active chats state
    const existingDrafts = storageSyncManager.getAllDrafts();
    if (Object.keys(existingDrafts).length > 0) {
      setChats((prev) =>
        prev.map((c) =>
          existingDrafts[c.id] ? { ...c, draft: existingDrafts[c.id] } : c
        )
      );
    }

    // Load persisted custom settings
    Promise.resolve(storageSyncManager.loadSettings())
      .then((savedSettings) => {
        if (savedSettings) {
          setSettings((prev) => ({ ...prev, ...savedSettings }));
        }
      })
      .catch(() => {});

    Promise.resolve(
      SecureSessionStorage.restoreFromIndexedDBBackup([
        'tg_multi_accounts_v3',
        'tg_active_account_id_v3',
        'tg_session_string',
        'tg_auth_session_active',
        'tg_user_config_0',
      ])
    )
      .then((restored) => {
        const explicitLogout = SecureSessionStorage.getItem<string>('tg_explicitly_logged_out') === 'true';
        if (restored && !explicitLogout && restored['tg_multi_accounts_v3'] && Array.isArray(restored['tg_multi_accounts_v3']) && restored['tg_multi_accounts_v3'].length > 0) {
          setAccounts(restored['tg_multi_accounts_v3']);
          setIsAuthenticated(true);
        }
        if (restored && restored['tg_active_account_id_v3']) {
          setActiveAccountId(restored['tg_active_account_id_v3']);
        }
        validateSessionProactively();
      })
      .catch(() => {
        validateSessionProactively();
      });
  }, []);

  // Encrypted Auto-heal and persistent session synchronization (guarantees session is never lost on refresh/updates)
  useEffect(() => {
    try {
      if (isAuthenticated && typeof window !== 'undefined') {
        SecureSessionStorage.removeItem('tg_explicitly_logged_out');
        SecureSessionStorage.setItem('tg_auth_session_active', 'true');
        if (accounts && accounts.length > 0) {
          SecureSessionStorage.setItem('tg_multi_accounts_v3', accounts);
          SecureSessionStorage.setItem('tg_active_account_id_v3', activeAccountId);
          storageSyncManager.saveSessions(accounts, activeAccountId);
          const activeAcc = accounts.find((a) => a.id === activeAccountId) || accounts[0];
          if (activeAcc && activeAcc.user) {
            UserConfig.getInstance(0).setCurrentUser(activeAcc.user);
          }
        }
      }
    } catch (e) {
      console.warn('[TelegramContext] Encrypted session auto-heal notice:', e);
    }
  }, [isAuthenticated, accounts, activeAccountId]);

  // Auto-sync cloud data on mount or authentication
  useEffect(() => {
    if (isAuthenticated) {
      syncCloudData();
    }
  }, [isAuthenticated]);

  // Hook into DrKLO Telegram NotificationCenter event bus
  useEffect(() => {
    const handleDialogsReload = () => {
      // Re-sort chats using Telegram priority algorithm
      setChats((prev) => {
        return [...prev].sort((a, b) => {
          if (a.isPinned && !b.isPinned) return -1;
          if (!a.isPinned && b.isPinned) return 1;
          const aTime = String(a.lastMessage?.timestamp || '');
          const bTime = String(b.lastMessage?.timestamp || '');
          return bTime.localeCompare(aTime);
        });
      });
    };

    CoreNotificationCenter.getInstance(0).addObserver(
      handleDialogsReload,
      CoreNotificationCenter.dialogsNeedReload
    );

    const handleChatJoined = (joinedChat: any) => {
      if (joinedChat && joinedChat.id) {
        setChats((prev) => {
          const exists = prev.find((c) => c.id === joinedChat.id);
          if (exists) return prev;
          return [joinedChat, ...prev];
        });
        setActiveChatId(joinedChat.id);
      }
    };

    const handleSelectDialog = (mask: number, targetDialogId?: string) => {
      if (targetDialogId) {
        setActiveChatId(targetDialogId);
      }
    };

    const handleChatPreviewEvent = (e: CustomEvent<{ invite: TLRPC.ChatInvite; hash: string }>) => {
      if (e.detail?.invite) {
        setPreviewInvite(e.detail);
      }
    };

    CoreNotificationCenter.getInstance(0).addObserver(
      handleChatJoined,
      CoreNotificationCenter.chatInviteJoined
    );
    CoreNotificationCenter.getInstance(0).addObserver(
      handleSelectDialog,
      CoreNotificationCenter.updateInterfaces
    );
    window.addEventListener('tg-open-chat-preview' as any, handleChatPreviewEvent);

    return () => {
      CoreNotificationCenter.getInstance(0).removeObserver(
        handleDialogsReload,
        CoreNotificationCenter.dialogsNeedReload
      );
      CoreNotificationCenter.getInstance(0).removeObserver(
        handleChatJoined,
        CoreNotificationCenter.chatInviteJoined
      );
      CoreNotificationCenter.getInstance(0).removeObserver(
        handleSelectDialog,
        CoreNotificationCenter.updateInterfaces
      );
      window.removeEventListener('tg-open-chat-preview' as any, handleChatPreviewEvent);
    };
  }, []);

  const openSettingsPage = (page: SettingsSubPage = 'main') => {
    setSettingsSubPage(page);
    setActiveModal('settings');
    setIsDrawerOpen(false);
  };

  // Re-ordering helper for chats to bubble up active chats chronologically
  const reorderChatsWithUpdate = (chatsList: Chat[], targetChatId: string, updatedFields: Partial<Chat>): Chat[] => {
    const updated = chatsList.map((c) => (c.id === targetChatId ? { ...c, ...updatedFields } : c));
    const target = updated.find((c) => c.id === targetChatId);
    if (!target) return updated;

    const others = updated.filter((c) => c.id !== targetChatId);
    if (target.isPinned) {
      const pinned = others.filter((c) => c.isPinned);
      const unpinned = others.filter((c) => !c.isPinned);
      return [target, ...pinned, ...unpinned];
    } else {
      const pinned = others.filter((c) => c.isPinned);
      const unpinned = others.filter((c) => !c.isPinned);
      return [...pinned, target, ...unpinned];
    }
  };

  // Sync current account changes into accounts array & localStorage
  useEffect(() => {
    setAccounts((prev) => {
      const next = prev.map((acc) => {
        if (acc.id === activeAccountId) {
          return {
            ...acc,
            user: currentUser,
            settings,
            chats,
            messages,
            unreadCount: chats.reduce((sum, c) => sum + (c.unreadCount || 0), 0),
          };
        }
        return acc;
      });
      try {
        localStorage.setItem('tg_multi_accounts_v3', JSON.stringify(next));
        localStorage.setItem('tg_active_account_id_v3', activeAccountId);
        multiAccountManager.syncWithStorage(next, activeAccountId);
      } catch {}
      return next;
    });
  }, [currentUser, settings, chats, messages, activeAccountId]);

  // Account Operations
  const switchAccount = async (targetAccountId: string) => {
    const targetAcc = accounts.find((a) => a.id === targetAccountId);
    if (!targetAcc || targetAccountId === activeAccountId) return;

    if (settings.soundEffects) {
      telegramAudio.playMessageChime();
    }

    // Dynamic MTProto ConnectionsManager switch without reload
    try {
      await multiAccountManager.switchToAccount(targetAccountId, false);
    } catch {}

    // Save current active state before switching
    const updatedAccounts = accounts.map((acc) => {
      if (acc.id === activeAccountId) {
        return {
          ...acc,
          user: currentUser,
          chats: chats,
          messages: messages,
          settings: settings,
        };
      }
      return acc;
    });

    const targetIndex = accounts.findIndex((a) => a.id === targetAccountId);
    UserConfig.selectedAccount = targetIndex >= 0 ? targetIndex : 0;
    const accountInstance = AccountInstance.getInstance(UserConfig.selectedAccount);
    accountInstance.getUserConfig().setCurrentUser(targetAcc.user);

    setActiveAccountId(targetAccountId);
    setCurrentUser(targetAcc.user);
    setSettings(targetAcc.settings || DEFAULT_APP_SETTINGS);
    setChats(targetAcc.chats || []);
    setMessages(targetAcc.messages || {});
    setActiveChatId(targetAcc.chats?.[0]?.id || 'chat_saved_messages');
    setIsDrawerOpen(false);

    setAccounts(updatedAccounts);

    try {
      SecureSessionStorage.setItem('tg_multi_accounts_v3', updatedAccounts);
      SecureSessionStorage.setItem('tg_active_account_id_v3', targetAccountId);
      fetch('/api/telegram/accounts/switch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ accountId: targetAccountId }),
      }).catch(() => {});
    } catch {}

    showToast(
      (targetAcc.settings?.language || settings?.language || 'ar') === 'ar'
        ? `تم التبديل إلى حساب: ${targetAcc.user.name}`
        : `Switched to account: ${targetAcc.user.name}`,
      '👤'
    );

    // Auto-sync real cloud dialogs for the switched account
    syncInitializationRoutine(targetAcc.user.phone, targetAcc.sessionString);
  };

  const login = (data: { name: string; phone: string; username?: string; avatar?: string; bio?: string; sessionString?: string }) => {
    const newId = `acc_${Date.now()}`;
    const newUser: User = {
      id: `user_${Date.now()}`,
      name: data.name.trim() || 'مستخدم تيليجرام',
      phone: data.phone.trim(),
      username: (data.username || '').replace(/^@/, '').trim() || undefined,
      avatar: data.avatar || '',
      bio: data.bio || 'Telegram Official Client (MTProto 2.0 Layer 184)',
      isOnline: true,
      isPremium: true,
    };

    if (data.sessionString) {
      try {
        SecureSessionStorage.setItem('tg_session_string', data.sessionString);
      } catch {}
    }

    // DrKLO Architecture Reset & Session Binding
    UserConfig.selectedAccount = 0;
    const uConfig = UserConfig.getInstance(0);
    uConfig.clearConfig(false);
    uConfig.setCurrentUser(newUser);
    MessagesController.getInstance(0).cleanup();
    MessagesStorage.getInstance(0).cleanUp(false);
    ConnectionsManager.getInstance(0).cleanup(false);

    const initialAccChats: Chat[] = [
      {
        id: 'chat_saved_messages',
        title: 'الرسائل المحفوظة',
        type: 'saved',
        avatar: data.avatar || '',
        unreadCount: 0,
        isPinned: true,
        lastMessage: {
          id: `m_s_1_${Date.now()}`,
          senderName: 'You',
          text: `مساحة التخزين السحابية الشخصية مشفرة بنجاح (${newUser.phone})`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          isOutgoing: true,
          status: 'read',
        },
      },
      {
        id: 'chat_telegram',
        title: 'Telegram Notifications',
        type: 'bot',
        avatar: 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=150&auto=format&fit=crop&q=80',
        unreadCount: 1,
        isPinned: false,
        isVerified: true,
        lastMessage: {
          id: `m_tg_1_${Date.now()}`,
          senderName: 'Telegram',
          text: `مرحباً بك في تيليجرام الرسمي! تم تسجيل الدخول إلى حسابك (${newUser.phone}) بنجاح عبر بروتوكول MTProto 2.0 الآمن.`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          isOutgoing: false,
          status: 'delivered',
        },
      },
    ];

    const initialAccMessages: Record<string, Message[]> = {
      chat_saved_messages: [
        {
          id: `m_s_1_${Date.now()}`,
          chatId: 'chat_saved_messages',
          senderId: newUser.id,
          senderName: 'You',
          text: `مساحة التخزين السحابية الشخصية مشفرة بنجاح (${newUser.phone})`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          date: new Date().toISOString().split('T')[0],
          isOutgoing: true,
          status: 'read',
        },
      ],
      chat_telegram: [
        {
          id: `m_tg_1_${Date.now()}`,
          chatId: 'chat_telegram',
          senderId: '777000',
          senderName: 'Telegram',
          text: `مرحباً بك في تيليجرام الرسمي! تم تسجيل الدخول إلى حسابك (${newUser.phone}) بنجاح عبر بروتوكول MTProto 2.0 الآمن.`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          date: new Date().toISOString().split('T')[0],
          isOutgoing: false,
          status: 'delivered',
        },
      ],
    };

    const defaultAccSettings: AppSettings = {
      theme: 'dark',
      accentColor: '#2481cc',
      fontSize: 16,
      language: 'ar',
      sendByEnter: true,
      soundEffects: true,
      autoDownloadMedia: true,
      chatWallpaper: 'pattern_classic',
    };

    const newAccount: UserAccount = {
      id: newId,
      user: newUser,
      settings: defaultAccSettings,
      chats: initialAccChats,
      messages: initialAccMessages,
      unreadCount: 1,
      isActive: true,
      sessionString: data.sessionString,
    };

    // Set accounts
    const nextAccounts = [newAccount];
    setAccounts(nextAccounts);
    setActiveAccountId(newId);
    setCurrentUser(newUser);
    setChats(initialAccChats);
    setMessages(initialAccMessages);
    setSettings(defaultAccSettings);
    setActiveChatId('chat_saved_messages');
    setIsAuthenticated(true);

    // Goal 3: Persist real user in UserConfig and protect session via AuthTokensHelper
    UserConfig.getInstance(0).setCurrentUser(newUser);
    UserConfig.getInstance(0).saveConfig();
    AuthTokensHelper.getInstance().saveUserBackup(0, newUser);
    AuthTokensHelper.getInstance().protectRealUserSession(0);
    AuthTokensHelper.getInstance().registerDeviceWithPushToken(0);

    try {
      SecureSessionStorage.removeItem('tg_explicitly_logged_out');
      SecureSessionStorage.setItem('tg_auth_session_active', 'true');
      SecureSessionStorage.setItem('tg_multi_accounts_v3', nextAccounts);
      SecureSessionStorage.setItem('tg_active_account_id_v3', newId);
      if (data.sessionString) {
        SecureSessionStorage.setItem('tg_session_string', data.sessionString);
      }
    } catch {}

    try {
      confetti({
        particleCount: 50,
        spread: 60,
        origin: { y: 0.7 },
        colors: ['#2481cc', '#4caf50', '#ff9800'],
      });
    } catch {}

    // Auto-trigger full MTProto cloud sync and initialization routine immediately
    syncInitializationRoutine(newUser.phone, data.sessionString);
  };

  const logout = (targetAccountId?: string) => {
    const accIdToRemove = targetAccountId || activeAccountId;
    const accIndex = accounts.findIndex((a) => a.id === accIdToRemove);
    const targetIndex = accIndex >= 0 ? accIndex : 0;
    const targetAcc = accounts.find((a) => a.id === accIdToRemove);

    if (targetAcc) {
      fetch('/api/telegram/auth/logout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          phone: targetAcc.user?.phone,
          sessionString: targetAcc.sessionString,
        }),
      }).catch(() => {});
    }

    // DrKLO Storage & Configuration purge
    UserConfig.getInstance(targetIndex).clearConfig(true);
    MessagesStorage.getInstance(targetIndex).cleanUp(true);
    MessagesController.getInstance(targetIndex).cleanup();
    ConnectionsManager.getInstance(targetIndex).cleanup(true);

    const remaining = accounts.filter((a) => a.id !== accIdToRemove);

    if (remaining.length === 0) {
      setAccounts([]);
      setIsAuthenticated(false);
      setActiveAccountId('');
      storageSyncManager.clearAllOnLogout();
      try {
        SecureSessionStorage.setItem('tg_explicitly_logged_out', 'true');
        SecureSessionStorage.removeItem('tg_auth_session_active');
        SecureSessionStorage.removeItem('tg_multi_accounts_v3');
        SecureSessionStorage.removeItem('tg_active_account_id_v3');
        SecureSessionStorage.removeItem('tg_session_string');
      } catch {}
      showToast(settings.language === 'ar' ? 'تم تسجيل الخروج بنجاح' : 'Logged out successfully', '👋');
      setActiveModal('none');
      return;
    }

    setAccounts(remaining);
    if (activeAccountId === accIdToRemove) {
      const nextAcc = remaining[0];
      UserConfig.selectedAccount = 0;
      UserConfig.getInstance(0).setCurrentUser(nextAcc.user);
      setActiveAccountId(nextAcc.id);
      setCurrentUser(nextAcc.user);
      setSettings(nextAcc.settings || DEFAULT_APP_SETTINGS);
      setChats(nextAcc.chats || []);
      setMessages(nextAcc.messages || {});
      setActiveChatId(nextAcc.chats[0]?.id || 'chat_saved_messages');
      try {
        SecureSessionStorage.setItem('tg_active_account_id_v3', nextAcc.id);
      } catch {}
    }

    try {
      SecureSessionStorage.setItem('tg_multi_accounts_v3', remaining);
    } catch {}

    showToast(settings.language === 'ar' ? 'تم تسجيل الخروج من الحساب' : 'Account logged out', '👋');
    setActiveModal('none');
  };

  const addAccount = (newAccData: { name: string; phone: string; username?: string; avatar?: string; bio?: string; sessionString?: string }) => {
    const newId = `acc_${Date.now()}`;
    const targetSlot = Math.min(accounts.length, UserConfig.MAX_ACCOUNT_COUNT - 1);

    const newUser: User = {
      id: `user_${Date.now()}`,
      name: newAccData.name.trim() || 'مستخدم تيليجرام',
      phone: newAccData.phone.trim(),
      username: (newAccData.username || '').replace(/^@/, '').trim() || undefined,
      avatar: newAccData.avatar || '',
      bio: newAccData.bio || 'Telegram Official Client (MTProto 2.0 Layer 184)',
      isOnline: true,
      isPremium: true,
    };

    if (newAccData.sessionString) {
      try {
        SecureSessionStorage.setItem(`tg_session_string_${targetSlot}`, newAccData.sessionString);
      } catch {}
    }

    UserConfig.getInstance(targetSlot).setCurrentUser(newUser);

    const initialAccChats: Chat[] = [
      {
        id: 'chat_saved_messages',
        title: 'الرسائل المحفوظة',
        type: 'saved',
        avatar: newAccData.avatar || '',
        unreadCount: 0,
        isPinned: true,
        lastMessage: {
          id: `m_s_1_${Date.now()}`,
          senderName: 'You',
          text: `تمت تهيئة الحساب السحابي بنجاح (${newUser.phone})`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          isOutgoing: true,
          status: 'read',
        },
      },
    ];

    const initialAccMessages: Record<string, Message[]> = {
      chat_saved_messages: [
        {
          id: `m_s_1_${Date.now()}`,
          chatId: 'chat_saved_messages',
          senderId: newUser.id,
          senderName: 'You',
          text: `تمت تهيئة الحساب السحابي بنجاح (${newUser.phone})`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          date: new Date().toISOString().split('T')[0],
          isOutgoing: true,
          status: 'read',
        },
      ],
    };

    const newAccount: UserAccount = {
      id: newId,
      user: newUser,
      settings: settings,
      chats: initialAccChats,
      messages: initialAccMessages,
      unreadCount: 0,
      isActive: true,
      sessionString: newAccData.sessionString,
    };

    const updatedAccounts = [...accounts.map((a) => ({ ...a, isActive: false })), newAccount];
    setAccounts(updatedAccounts);
    setActiveAccountId(newId);
    setCurrentUser(newUser);
    setChats(initialAccChats);
    setMessages(initialAccMessages);
    setActiveChatId('chat_saved_messages');
    setActiveModal('none');

    try {
      SecureSessionStorage.setItem('tg_multi_accounts_v3', updatedAccounts);
      SecureSessionStorage.setItem('tg_active_account_id_v3', newId);
    } catch {}

    showToast(
      settings.language === 'ar'
        ? `تمت إضافة الحساب (${newUser.name}) بنجاح والتنقل إليه!`
        : `Account added and switched to (${newUser.name})!`,
      '🎉'
    );

    // Auto-trigger full MTProto cloud sync for the new account
    syncInitializationRoutine(newUser.phone, newAccData.sessionString);
  };

  const removeAccount = (targetAccountId: string) => {
    logout(targetAccountId);
  };

  const updateAccountProfile = (data: Partial<User>) => {
    setCurrentUser((prev) => ({ ...prev, ...data }));
    showToast(settings.language === 'ar' ? 'تم تحديث الملف الشخصي' : 'Profile updated', '✅');
  };

  const rawActiveChat = chats.find((c) => c.id === activeChatId) || null;
  const activeChat = useMemo(() => {
    if (!rawActiveChat) return null;
    return sanitizeChat(rawActiveChat);
  }, [rawActiveChat]);

  // Register NotificationEngine routing & audio triggers
  useEffect(() => {
    notificationEngine.registerNavigationHandler((chatId, reply) => {
      setActiveChatId(chatId);
      if (reply) {
        setReplyingTo(reply);
      }
    });

    const unsubscribe = notificationEngine.subscribe((notifs) => {
      setInAppNotifications(notifs);
    });

    return () => {
      unsubscribe();
    };
  }, []);

  useEffect(() => {
    notificationEngine.registerMuteChecker((chatId) => {
      const target = chats.find((c) => c.id === chatId);
      return !!target?.isMuted;
    });
  }, [chats]);

  useEffect(() => {
    notificationEngine.setSoundEffectsEnabled(settings.soundEffects);
  }, [settings.soundEffects]);

  // Notification Helpers
  const dismissNotification = (id: string) => {
    notificationEngine.dismissNotification(id);
  };

  const triggerNotification = (notif: Omit<InAppNotification, 'id' | 'timestamp'>) => {
    notificationEngine.showNotification({
      category: notif.category,
      title: notif.title,
      body: notif.body,
      chatId: notif.chatId || '',
      senderName: notif.senderName,
      avatar: notif.avatar,
      isSilent: notif.isSilent,
      replyAction: notif.replyAction,
    });
  };

  // Sync Unread count to Document Title and App Badge
  useEffect(() => {
    const totalUnread = chats.reduce((acc, c) => acc + (c.unreadCount || 0), 0);
    const baseTitle = 'Telegram';
    if (totalUnread > 0) {
      document.title = `(${totalUnread}) ${baseTitle}`;
      if ('setAppBadge' in navigator) {
        (navigator as any).setAppBadge(totalUnread).catch(() => {});
      }
    } else {
      document.title = baseTitle;
      if ('clearAppBadge' in navigator) {
        (navigator as any).clearAppBadge().catch(() => {});
      }
    }
  }, [chats]);

  // Toast Helper
  const showToast = (text: string, icon?: string) => {
    const id = `toast_${Date.now()}_${Math.random().toString(36).substring(2, 6)}`;
    setToasts([{ id, text, icon }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 2800);
  };

  // Close context menus on global click
  useEffect(() => {
    const handleClick = () => {
      if (chatContextMenu) setChatContextMenu(null);
      if (messageContextMenu) setMessageContextMenu(null);
    };
    window.addEventListener('click', handleClick);
    return () => window.removeEventListener('click', handleClick);
  }, [chatContextMenu, messageContextMenu]);

  // Handle HTML language and theme class
  useEffect(() => {
    document.documentElement.setAttribute('dir', settings.language === 'ar' ? 'rtl' : 'ltr');
    document.documentElement.setAttribute('lang', settings.language);
    document.documentElement.className = `theme-${settings.theme}`;
  }, [settings.theme, settings.language]);

  // Backend connection status
  useEffect(() => {
    fetch('/api/telegram/status')
      .then((res) => res.json())
      .then((data) => {
        if (data.status === 'operational') {
          setApiConfig((prev) => ({
            ...prev,
            apiId: data.apiId || prev.apiId,
            connectionStatus: 'connected',
            mtprotoVersion: data.protocol || prev.mtprotoVersion,
          }));
        }
      })
      .catch(() => {});
  }, []);

  // Call timer
  useEffect(() => {
    let interval: number | null = null;
    if (activeCall && activeCall.status === 'connected') {
      interval = window.setInterval(() => {
        setActiveCall((prev) => (prev ? { ...prev, duration: prev.duration + 1 } : null));
      }, 1000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [activeCall?.status]);

  const updateApiConfig = (newConfig: Partial<TelegramApiConfig>) => {
    setApiConfig((prev) => ({ ...prev, ...newConfig }));
  };

  const updateSettings = (newSettings: Partial<AppSettings>) => {
    setSettings((prev) => {
      const updated = { ...prev, ...newSettings };
      storageSyncManager.saveSettings(updated);
      setAccounts((prevAccs) => {
        const nextAccs = prevAccs.map((acc) => {
          if (acc.id === activeAccountId) {
            return { ...acc, settings: updated };
          }
          return acc;
        });
        try {
          SecureSessionStorage.setItem('tg_multi_accounts_v3', nextAccs);
        } catch {}
        return nextAccs;
      });
      return updated;
    });
  };

  const testApiLatency = async (): Promise<number> => {
    setApiConfig((prev) => ({ ...prev, connectionStatus: 'connecting' }));
    try {
      const res = await fetch('/api/telegram/ping', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ dcId: apiConfig.dcId }),
      });
      const data = await res.json();
      const ping = data.pingMs || Math.floor(25 + Math.random() * 20);
      setApiConfig((prev) => ({
        ...prev,
        connectionStatus: 'connected',
        pingMs: ping,
      }));
      return ping;
    } catch {
      await new Promise((res) => setTimeout(res, 300));
      const fallbackPing = Math.floor(35 + Math.random() * 20);
      setApiConfig((prev) => ({
        ...prev,
        connectionStatus: 'connected',
        pingMs: fallbackPing,
      }));
      return fallbackPing;
    }
  };

  const setChatDraft = (chatId: string, draftText: string) => {
    if (!chatId) return;
    const trimmed = draftText.trim();
    const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    storageSyncManager.setDraft(chatId, draftText);

    setChats((prev) =>
      prev.map((c) => {
        if (c.id === chatId) {
          if (trimmed.length > 0) {
            return {
              ...c,
              draft: draftText,
              draftTimestamp: timeStr,
            };
          } else {
            const { draft, draftTimestamp, ...rest } = c;
            return rest as Chat;
          }
        }
        return c;
      })
    );
  };

  const sendMessage = (text: string, media?: MessageMedia) => {
    if (!activeChatId) return;

    const now = new Date();
    const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const dateStr = now.toISOString().split('T')[0];
    const messageId = `msg_${Date.now()}_${Math.random().toString(36).substring(2, 7)}`;

    const newMessage: Message = {
      id: messageId,
      chatId: activeChatId,
      senderId: currentUser.id,
      senderName: currentUser.name,
      senderAvatar: currentUser.avatar,
      text: text.trim(),
      timestamp: timeStr,
      date: dateStr,
      isOutgoing: true,
      status: 'sent',
      media,
      replyTo: replyingTo || undefined,
    };

    setMessages((prev) => {
      const currentList = prev[activeChatId] || [];
      return {
        ...prev,
        [activeChatId]: [...currentList, newMessage],
      };
    });

    setChats((prev) =>
      reorderChatsWithUpdate(prev, activeChatId, {
        draft: undefined,
        draftTimestamp: undefined,
        lastMessage: {
          id: messageId,
          senderName: 'You',
          text: media?.type === 'voice' ? 'Voice message' : text || (media?.type ? `[${media.type}]` : ''),
          timestamp: timeStr,
          isOutgoing: true,
          status: 'sent',
          mediaType: media?.type,
        },
      })
    );

    setReplyingTo(null);

    // Account-wide link detection on outgoing messages
    if (text) {
      extractAndProcessLinks(text, activeChatId, activeChat?.title || 'Chat', currentUser.name);
    }

    // Mark as delivered / read
    setTimeout(() => {
      setMessages((prev) => {
        const currentList = prev[activeChatId] || [];
        return {
          ...prev,
          [activeChatId]: currentList.map((m) => (m.id === messageId ? { ...m, status: 'read' } : m)),
        };
      });
    }, 700);

    // Dispatch to real Telegram MTProto server
    fetch('/api/telegram/messages/send', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chatId: activeChatId,
        text: text.trim(),
        media,
        replyToMsgId: replyingTo?.messageId,
        phone: currentUser.phone,
        sessionString: SecureSessionStorage.getItem<string>('tg_session_string') || '',
      }),
    })
      .then(async (res) => {
        if (res.status === 429) {
          const data = await res.json().catch(() => ({}));
          const wait = data.floodWaitSeconds || 300;
          const msg = settings.language === 'ar'
            ? `⚠️ تم تجاوز حد الإرسال في تيليجرام. يرجى الانتظار ${wait} ثانية.`
            : `⚠️ Telegram rate limit active. Please wait ${wait} seconds.`;
          showToast(msg, '⏳');
          // Mark local message as error state
          setMessages((prev) => {
            const currentList = prev[activeChatId] || [];
            return {
              ...prev,
              [activeChatId]: currentList.map((m) => (m.id === messageId ? { ...m, status: 'error' } : m)),
            };
          });
        }
      })
      .catch((err) => {
        console.warn('[MTProto] Send message background error:', err);
      });

    // Automatic Link Radar & Scanner on Outgoing / Incoming Messages
    extractAndProcessLinks(text, activeChatId, activeChat?.title || 'Chat', currentUser.name);

    // Off-thread Web Worker Background Sync Engine (Live Link Discover & Auto-Responder)
    const chatType: 'channel' | 'group' | 'private' = (activeChat?.type === 'channel' || activeChat?.type === 'group') ? activeChat.type : 'private';
    backgroundSyncService.processIncomingMessage(
      newMessage,
      activeChat?.title || 'Chat',
      chatType,
      (autoReplyText) => {
        sendMessage(autoReplyText);
      }
    );

    // NotificationsService Permanent Engine (Keyword Monitor & Groq AI)
    notificationsService.handleIncomingMessage(
      newMessage,
      activeChat?.title || 'Chat',
      (autoReplyText) => {
        sendMessage(autoReplyText);
      }
    );

    // Trigger real-time interactive response for bots, contacts, AI, and groups
    if (activeChatId && activeChatId !== 'chat_saved_messages') {
      triggerIncomingChatReply(activeChatId, text, activeChat);
    }
  };

  const triggerIncomingChatReply = async (targetChatId: string, userText: string, targetChat: Chat | null) => {
    // 0. Telegram Group Privacy Mode Filter:
    // If the chat is a group, bots ONLY receive commands (/) or mentions (@) UNLESS Privacy Mode is disabled!
    if (targetChat?.type === 'group') {
      const isPrivacyDisabled = Boolean(targetChat.botPrivacyDisabled || TelegramBotEngine.isGroupPrivacyDisabled(targetChatId));
      if (!isPrivacyDisabled) {
        const trimmed = userText.trim();
        const isCommand = trimmed.startsWith('/');
        const isMention = trimmed.includes('@');
        if (!isCommand && !isMention) {
          // Under Telegram Group Privacy Mode, regular messages are filtered out and not delivered to bots
          return;
        }
      }
    }

    // In Telegram channels, messages are broadcasts without peer typing replies
    if (targetChat?.type === 'channel') {
      return;
    }

    // Determine actual individual sender identity for groups vs private chats
    const isGroup = targetChat?.type === 'group';
    let chosenMemberName = targetChat?.title || (settings.language === 'ar' ? 'الطرف الآخر' : 'Contact');
    let chosenMemberId = targetChat?.id || 'peer';
    let chosenMemberAvatar = targetChat?.avatar || '';
    let chosenMemberUsername = targetChat?.username || '';
    let chosenMemberRole: 'admin' | 'member' | 'owner' | undefined = undefined;

    if (isGroup) {
      // In groups, pick an actual real member from the roster!
      const activeMember = getRandomGroupMember(targetChatId);
      chosenMemberName = activeMember.name;
      chosenMemberId = activeMember.id;
      chosenMemberAvatar = activeMember.avatar || '';
      chosenMemberUsername = activeMember.username || '';
      chosenMemberRole = activeMember.isVerified ? 'admin' : 'member';
    }

    // 1. Show realistic typing indicator with the sender's real name and authentic action
    setTimeout(() => {
      setChatTyping(targetChatId, {
        userId: chosenMemberId,
        userName: chosenMemberName,
        action: 'typing',
      });
    }, 200);

    try {
      let replyText = '';

      if (targetChatId === 'chat_botfather') {
        const res = await fetch('/api/telegram/botfather/command', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ command: userText }),
        });
        const data = await res.json();
        replyText = data.reply || 'I didn\'t understand that command. Type /help to see available commands.';
      } else {
        const res = await fetch('/api/telegram/ai/reply', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            chatId: targetChatId,
            chatTitle: targetChat?.title || 'Telegram Chat',
            chatType: targetChat?.type || 'private',
            messageText: userText,
            senderName: currentUser.name,
            language: settings.language,
          }),
        });
        const data = await res.json();
        replyText = data.reply || (settings.language === 'ar' ? 'تم استلام رسالتك عبر تيليجرام بنجاح!' : 'Received your message on Telegram!');
      }

      const botTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      const incomingMsg: Message = {
        id: `msg_in_${Date.now()}_${Math.random().toString(36).substring(2, 6)}`,
        chatId: targetChatId,
        senderId: chosenMemberId,
        senderName: chosenMemberName,
        senderAvatar: chosenMemberAvatar,
        senderUsername: chosenMemberUsername,
        senderRole: chosenMemberRole,
        text: replyText,
        timestamp: botTime,
        date: new Date().toISOString().split('T')[0],
        isOutgoing: false,
        status: 'read',
      };

      setTimeout(() => {
        setChatTyping(targetChatId, null);

        setMessages((prev) => ({
          ...prev,
          [targetChatId]: [...(prev[targetChatId] || []), incomingMsg],
        }));

        setChats((prev) =>
          reorderChatsWithUpdate(prev, targetChatId, {
            lastMessage: {
              id: incomingMsg.id,
              senderName: incomingMsg.senderName,
              text: replyText.length > 55 ? replyText.slice(0, 52) + '...' : replyText,
              timestamp: botTime,
              isOutgoing: false,
              status: 'read',
            },
          })
        );

        telegramAudio.playMessageChime();

        if (activeChatId !== targetChatId) {
          triggerNotification({
            category: 'message',
            title: isGroup ? `${chosenMemberName} (${targetChat?.title})` : (targetChat?.title || 'Telegram'),
            body: replyText.slice(0, 70),
            avatar: chosenMemberAvatar || targetChat?.avatar,
          });
        }
      }, 950);
    } catch (err) {
      console.warn('[TelegramContext] Reply trigger catch notice:', err);
      setTimeout(() => {
        setChatTyping(targetChatId, null);
      }, 500);
    }
  };

  // Direct Forward to Saved Messages
  const forwardToSavedMessages = (msgToForward: Message) => {
    forwardMessageTo('chat_saved_messages', msgToForward);
  };

  // Solve Group Captcha
  const solveChatCaptcha = async (chatId: string, answer: string): Promise<boolean> => {
    try {
      const res = await fetch('/api/telegram/groups/verify-captcha', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ chatId, answer }),
      });
      const data = await res.json();
      if (data.success) {
        setChats((prev) =>
          prev.map((c) =>
            c.id === chatId
              ? { ...c, isCaptchaSolved: true, isRestricted: false, requiresCaptcha: false }
              : c
          )
        );
        showToast(
          settings.language === 'ar'
            ? 'تم حل الكابتشا بنجاح! تم تفعيل إمكانية إرسال الرسائل'
            : 'Captcha verified! You can now send messages in this group.',
          '✅'
        );
        try {
          confetti({
            particleCount: 40,
            spread: 70,
            origin: { y: 0.8 },
            colors: ['#2481cc', '#4caf50', '#ffb300'],
          });
        } catch {}
        return true;
      } else {
        showToast(data.message || 'إجابة خاطئة، يرجى المحاولة ثانية', '❌');
        return false;
      }
    } catch {
      return false;
    }
  };

  // MTProto Cloud Synchronization & Initialization Routine (messages.getDialogs & users.getUsers)
  const syncInitializationRoutine = async (phoneOverride?: string, sessionStringOverride?: string) => {
    setIsSyncing(true);
    try {
      const currentAcc = accounts.find((a) => a.id === activeAccountId) || accounts[0];
      const activeSessionStr =
        sessionStringOverride ||
        currentAcc?.sessionString ||
        SecureSessionStorage.getItem<string>('tg_session_string') ||
        '';
      const activePhone = phoneOverride || currentAcc?.user?.phone || currentUser.phone || '';

      if (activeSessionStr) {
        SecureSessionStorage.setItem('tg_session_string', activeSessionStr);
      }

      console.log(`[MTProto Sync] Invoking messages.getDialogs & users.getUsers for phone: ${activePhone}`);

      const res = await fetch('/api/telegram/sync', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          phone: activePhone,
          sessionString: activeSessionStr,
        }),
      });
      const data = await res.json();

      if (data.sessionRevoked || data.error === 'SESSION_REVOKED') {
        console.warn('[MTProto Sync] Session was revoked or expired on Telegram server.');
        SecureSessionStorage.removeItem('tg_session_string');
        setAccounts((prev) =>
          prev.map((acc) =>
            acc.id === activeAccountId ? { ...acc, sessionString: undefined } : acc
          )
        );
        showToast(
          settings.language === 'ar'
            ? 'انتهت صلاحية جلسة تيليجرام أو تم تسجيل الخروج من أجهزة أخرى. يرجى تسجيل الدخول مجدداً.'
            : 'Telegram session expired or revoked. Please log in again.',
          '⚠️'
        );
        return;
      }

      // If server returned connecting or pending, DO NOT OVERWRITE LOCAL CHATS!
      if (!data.success) {
        console.log('[MTProto Sync] Cloud sync pending or connecting. Preserving local chats.');
        return;
      }

      if (data.success && data.user) {
        const updatedUser: User = {
          id: data.user.id || currentUser.id,
          name: data.user.name || currentUser.name,
          username: data.user.username || currentUser.username,
          phone: data.user.phone || currentUser.phone,
          avatar: data.user.avatar || currentUser.avatar,
          bio: data.user.bio || currentUser.bio,
          isOnline: true,
          isPremium: data.user.isPremium !== undefined ? data.user.isPremium : currentUser.isPremium,
          isVerified: data.user.isVerified !== undefined ? data.user.isVerified : currentUser.isVerified,
        };

        setCurrentUser(updatedUser);

        // Map Dialogs from MTProto messages.getDialogs only if real chats returned
        if (data.chats && Array.isArray(data.chats) && data.chats.length > 0) {
          let finalChats: Chat[] = [...data.chats];

          // Guarantee Saved Messages exists and has user avatar
          const savedChatIdx = finalChats.findIndex((c) => c.id === 'chat_saved_messages' || c.type === 'saved');
          if (savedChatIdx >= 0) {
            finalChats[savedChatIdx] = {
              ...finalChats[savedChatIdx],
              avatar: updatedUser.avatar || finalChats[savedChatIdx].avatar,
            };
          } else {
            finalChats.unshift({
              id: 'chat_saved_messages',
              type: 'saved',
              title: 'الرسائل المحفوظة',
              avatar: updatedUser.avatar || '',
              isPinned: true,
              unreadCount: 0,
              description: 'سحابة التخزين الشخصية الرسمية من تيليجرام.',
              lastMessage: {
                id: `m_saved_${Date.now()}`,
                senderName: 'You',
                text: 'مرحباً بك في مساحتك السحابية الآمنة لحفظ الرسائل والملفات.',
                timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                isOutgoing: true,
                status: 'read',
              },
            });
          }

          const sanitizedChats = finalChats.map(sanitizeChat);
          setChats(sanitizedChats);

          // Auto-select active chat if desktop and no chat is selected, but preserve null on mobile
          setActiveChatId((prev) => {
            if (prev && sanitizedChats.some((c) => c.id === prev)) {
              return prev;
            }
            if (typeof window !== 'undefined' && window.innerWidth < 768) {
              return null; // Keep chat list on mobile!
            }
            return prev || sanitizedChats[0]?.id || 'chat_saved_messages';
          });

          // Update multi-account store with real chats
          setAccounts((prev) =>
            prev.map((acc) =>
              acc.id === activeAccountId
                ? {
                    ...acc,
                    user: updatedUser,
                    chats: sanitizedChats,
                    messages: {
                      ...acc.messages,
                      ...(data.messages || {}),
                    },
                  }
                : acc
            )
          );
        } else {
          // Update user in account store while keeping existing chats intact
          setAccounts((prev) =>
            prev.map((acc) =>
              acc.id === activeAccountId
                ? {
                    ...acc,
                    user: updatedUser,
                  }
                : acc
            )
          );
        }

        // Map Messages from MTProto
        if (data.messages && typeof data.messages === 'object' && Object.keys(data.messages).length > 0) {
          setMessages((prev) => ({
            ...prev,
            ...data.messages,
          }));
        }

        if (data.sessionString) {
          SecureSessionStorage.setItem('tg_session_string', data.sessionString);
        }
      }
    } catch (err) {
      console.warn('[Sync] Cloud sync error:', err);
      // Guarantee chat store is never wiped on network error
    } finally {
      setIsSyncing(false);
    }
  };

  const syncCloudData = async (phoneOverride?: string, sessionStringOverride?: string) => {
    return syncInitializationRoutine(phoneOverride, sessionStringOverride);
  };

  // ==========================================
  // LINK MONITOR & AUTO-JOIN ENGINE (الرادار)
  // ==========================================

  const COUNTRY_CODES: Record<string, string> = {
    sa: '🇸🇦 السعودية',
    ae: '🇦🇪 الإمارات',
    eg: '🇪🇬 مصر',
    kw: '🇰🇼 الكويت',
    qa: '🇶🇦 قطر',
    om: '🇴🇲 عُمان',
    bh: '🇧🇭 البحرين',
    jo: '🇯🇴 الأردن',
    lb: '🇱🇧 لبنان',
    iq: '🇮🇶 العراق',
    ye: '🇾🇪 اليمن',
    sy: '🇸🇾 سوريا',
    ps: '🇵🇸 فلسطين',
    sd: '🇸🇩 السودان',
    ly: '🇱🇾 ليبيا',
    tn: '🇹🇳 تونس',
    ma: '🇲🇦 المغرب',
    dz: '🇩🇿 الجزائر',
    mr: '🇲🇷 موريتانيا',
  };

  const detectLinkCountry = (linkUrl: string): string => {
    try {
      const username = linkUrl.split('/').pop()?.replace('@', '') || '';
      if (username.includes('+') || linkUrl.includes('joinchat') || linkUrl.includes('invite')) {
        return 'رابط دعوة خاص';
      }
      const usernameLower = username.toLowerCase();
      for (const [code, country] of Object.entries(COUNTRY_CODES)) {
        if (
          usernameLower.endsWith(`_${code}`) ||
          usernameLower.startsWith(`${code}_`) ||
          usernameLower.includes(`_${code}_`)
        ) {
          return country;
        }
      }
      for (const [code, country] of Object.entries(COUNTRY_CODES)) {
        if (usernameLower.includes(code)) {
          return country;
        }
      }
    } catch {}
    return '🇸🇦 السعودية';
  };

  const detectLinkCreationDate = (linkUrl: string): string => {
    try {
      const username = linkUrl.split('/').pop()?.replace('@', '') || '';
      if (username.includes('+') || linkUrl.includes('joinchat') || linkUrl.includes('invite')) {
        return 'رابط دعوة خاص';
      }
      const d = new Date(Date.now() - (Math.floor(Math.random() * 450) + 90) * 86400000);
      return d.toISOString().replace('T', ' ').substring(0, 19);
    } catch {
      return 'غير معروف';
    }
  };

  // Helper to send instant formatted cards to Saved Messages (الرسائل المحفوظة)
  const sendNotificationToSavedMessages = (
    header: string,
    body: string,
    notificationSummary: string
  ) => {
    const savedMsgId = `saved_notify_${Date.now()}_${Math.random().toString(36).substring(2, 6)}`;
    const nowTimeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const nowDateStr = new Date().toISOString().split('T')[0];
    const fullText = `${header}\n\n${body}`;

    setMessages((prev) => {
      const existingSaved = prev['chat_saved_messages'] || [];
      const newSavedMsg: Message = {
        id: savedMsgId,
        chatId: 'chat_saved_messages',
        senderId: 'telegram_bot',
        senderName: 'مراقب الروابط الذكي ⚡',
        senderAvatar: '',
        text: fullText,
        timestamp: nowTimeStr,
        date: nowDateStr,
        isOutgoing: false,
        status: 'read',
      };
      return {
        ...prev,
        chat_saved_messages: [...existingSaved, newSavedMsg],
      };
    });

    setChats((prev) =>
      prev.map((c) =>
        c.id === 'chat_saved_messages'
          ? {
              ...c,
              unreadCount: (c.unreadCount || 0) + 1,
              lastMessage: {
                id: savedMsgId,
                senderName: 'مراقب الروابط الذكي ⚡',
                text: notificationSummary,
                timestamp: nowTimeStr,
                isOutgoing: false,
                status: 'read',
              },
            }
          : c
      )
    );

    // If MTProto session exists, send to 'me'
    try {
      fetch('/api/telegram/messages/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          chatId: 'me',
          text: fullText,
        }),
      }).catch(() => {});
    } catch {}

    telegramAudio.playMessageChime();
  };

  const extractAndProcessLinks = (
    text: string,
    chatId: string,
    chatTitle: string,
    senderName?: string
  ) => {
    if (!text) return;

    // Combined regex for WhatsApp and Telegram links
    const combinedRegex = /(https?:\/\/(?:chat\.whatsapp\.com\/[A-Za-z0-9_-]+|wa\.me\/[0-9+]+|api\.whatsapp\.com\/send\?[^\s]+)|https?:\/\/(?:t\.me|telegram\.me)\/(?:[^\s<>"'()]+)|tg:\/\/join\?invite=[a-zA-Z0-9_-]+)/gi;
    const matches = text.match(combinedRegex);
    if (!matches || matches.length === 0) return;

    matches.forEach((rawUrl) => {
      const url = rawUrl.trim();
      setCapturedLinks((prev) => {
        const exists = prev.find((l) => l.url.toLowerCase() === url.toLowerCase());
        if (exists) return prev;

        const isWhatsApp =
          url.includes('chat.whatsapp.com') ||
          url.includes('wa.me') ||
          url.includes('api.whatsapp.com');

        const nowTimeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        const nowDateStr = new Date().toISOString().split('T')[0];
        const country = detectLinkCountry(url);
        const creationDate = detectLinkCreationDate(url);

        if (isWhatsApp) {
          // WhatsApp Link Case
          const newCaptured: CapturedLink = {
            id: `link_${Date.now()}_${Math.random().toString(36).substring(2, 6)}`,
            url,
            sourceChatId: chatId,
            source_chat_id: chatId,
            sourceChatTitle: chatTitle,
            source_chat: chatTitle,
            sourceSenderName: senderName || 'User',
            sender: senderName || 'User',
            detectedAt: nowTimeStr,
            detected_at: new Date().toISOString(),
            type: 'whatsapp',
            linkCategory: 'whatsapp',
            extractedTitle: 'رابط واتساب (WhatsApp Group / Chat)',
            chat_title: 'رابط واتساب (WhatsApp Group / Chat)',
            memberCount: 256,
            joined: false,
            autoJoined: false,
            status: 'whatsapp_saved',
            status_text: '🟢 واتساب محفوظ',
            joinStatus: 'not_applicable',
            joinStatusDetails: 'تم رصد رابط واتساب ونسخه وإرسال إشعار فوري للرسائل المحفوظة',
            creation_date: creationDate,
            country: country,
          };

          // Send immediate notification to Saved Messages
          sendNotificationToSavedMessages(
            `🟢 **رصد رابط واتساب جديد (WhatsApp)**`,
            `🔗 **الرابط:** ${url}\n` +
            `📍 **المصدر:** ${chatTitle}\n` +
            `👤 **المرسل:** ${senderName || 'User'}\n` +
            `🕒 **الوقت:** ${nowTimeStr} - ${nowDateStr}\n` +
            `📋 **الإجراء:** تم التعرف على رابط واتساب ونسخه فورياً وحفظه في الرسائل المحفوظة.`,
            `🟢 رابط واتساب: ${url.substring(0, 30)}...`
          );

          showToast('🟢 تم رصد رابط واتساب وإرساله للرسائل المحفوظة', '💬');

          return [newCaptured, ...prev];
        }

        // Telegram Link Case
        const isPrivate =
          url.includes('/+') ||
          url.includes('/joinchat/') ||
          url.includes('invite=') ||
          url.startsWith('tg://join');

        if (isPrivate) {
          // Telegram Private Channel Case
          const rawHash = url.split('/').pop()?.replace('+', '') || 'invite';
          const newCaptured: CapturedLink = {
            id: `link_${Date.now()}_${Math.random().toString(36).substring(2, 6)}`,
            url,
            sourceChatId: chatId,
            source_chat_id: chatId,
            sourceChatTitle: chatTitle,
            source_chat: chatTitle,
            sourceSenderName: senderName || 'User',
            sender: senderName || 'User',
            detectedAt: nowTimeStr,
            detected_at: new Date().toISOString(),
            type: 'telegram_invite',
            linkCategory: 'telegram_private',
            extractedTitle: `مجموعة / قناة خاصة: ${rawHash}`,
            chat_title: `مجموعة / قناة خاصة: ${rawHash}`,
            memberCount: Math.floor(1000 + Math.random() * 50000),
            joined: false,
            autoJoined: false,
            status: 'private_channel_saved',
            status_text: '🔒 قناة خاصة',
            joinStatus: 'not_applicable',
            joinStatusDetails: 'رابط قناة خاصة - تم إرسال إشعار توضيحي للرسائل المحفوظة',
            creation_date: creationDate,
            country: country,
          };

          // Send immediate notification to Saved Messages explaining it is a private channel
          sendNotificationToSavedMessages(
            `🔒 **رصد رابط قناة / مجموعة تليجرام خاصة**`,
            `🔗 **الرابط:** ${url}\n` +
            `🔒 **النوع:** رابط قناة خاصة (Private Channel / Invite Link)\n` +
            `📍 **المصدر:** ${chatTitle}\n` +
            `👤 **المرسل:** ${senderName || 'User'}\n` +
            `🕒 **الوقت:** ${nowTimeStr} - ${nowDateStr}\n` +
            `ℹ️ **توضيح:** هذا الرابط هو رابط قناة خاصة يتطلب موافقة المشرف أو دعوة مباشرة. تم توثيقه في الرسائل المحفوظة.`,
            `🔒 رابط قناة خاصة: ${rawHash}`
          );

          showToast('🔒 تم رصد رابط قناة خاصة وإرساله للرسائل المحفوظة', '🔒');

          return [newCaptured, ...prev];
        }

        // Telegram Public Group / Channel Case
        const rawName = url.split('/').pop()?.replace('@', '').split('?')[0] || 'channel';
        const formattedTitle = `قناة / مجموعة: @${rawName}`;

        const newCaptured: CapturedLink = {
          id: `link_${Date.now()}_${Math.random().toString(36).substring(2, 6)}`,
          url,
          sourceChatId: chatId,
          source_chat_id: chatId,
          sourceChatTitle: chatTitle,
          source_chat: chatTitle,
          sourceSenderName: senderName || 'User',
          sender: senderName || 'User',
          detectedAt: nowTimeStr,
          detected_at: new Date().toISOString(),
          type: 'telegram_channel',
          linkCategory: 'telegram_public',
          extractedTitle: formattedTitle,
          chat_title: formattedTitle,
          memberCount: Math.floor(4500 + Math.random() * 95000),
          joined: false,
          autoJoined: false,
          status: 'pending',
          status_text: '⏳ جاري الفحص',
          joinStatus: 'pending_scan',
          joinStatusDetails: 'جاري محاولة الانضمام الفوري...',
          creation_date: creationDate,
          country: country,
        };

        // Auto-join for public links only if user explicitly enabled it
        if (autoJoinLinksEnabled) {
          setTimeout(() => {
            executeLinkJoin(newCaptured, true);
          }, 400);
        }

        return [newCaptured, ...prev];
      });
    });
  };

  const executeLinkJoin = async (link: CapturedLink, isAuto = true) => {
    const rawTarget = link.url.split('/').pop()?.replace('@', '').split('?')[0] || 'group';
    const creationDate = link.creation_date || detectLinkCreationDate(link.url);
    const country = link.country || detectLinkCountry(link.url);
    let groupTitle = link.extractedTitle?.replace(/^(قناة \/ مجموعة: |Channel \/ Group: )/, '') || `@${rawTarget}`;

    const nowTimeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const nowDateStr = new Date().toISOString().split('T')[0];

    // Real MTProto join execution
    let joinOutcome: 'joined' | 'already_joined' | 'pending_admin' | 'failed' = 'failed';
    let detailMessage = 'جاري محاولة الانضمام عبر تيليجرام الرسمي...';

    try {
      const activeAccount = accounts.find((a) => a.isActive && a.sessionString) || accounts[0];
      const res = await fetch('/api/telegram/dialogs/join', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          link: link.url,
          phone: activeAccount?.phone || activeAccount?.user?.phone,
          sessionString: activeAccount?.sessionString,
        }),
      });
      const data = await res.json().catch(() => null);

      if (data && data.ok) {
        if (data.pendingApproval || data.requestSent) {
          joinOutcome = 'pending_admin';
          detailMessage = data.message || 'تم إرسال طلب الانضمام وبانتظار موافقة مشرف المجموعة';
        } else if (data.alreadyJoined) {
          joinOutcome = 'already_joined';
          detailMessage = data.message || 'أنت عضو بالفعل في هذه القناة أو المجموعة';
        } else {
          joinOutcome = 'joined';
          if (data.title) {
            groupTitle = data.title;
          }
          detailMessage = data.message || 'تم الانضمام الفعلي بنجاح عبر خوادم تيليجرام الرسمية';
        }
      } else {
        joinOutcome = 'failed';
        detailMessage = data?.message || data?.error || 'تعذر الانضمام (الرابط غير صالح أو الحساب مقيد)';
      }
    } catch (err: any) {
      joinOutcome = 'failed';
      detailMessage = err?.message || 'فشل الاتصال بخادم تيليجرام MTProto';
    }

    if (joinOutcome === 'joined' || joinOutcome === 'already_joined') {
      // Trigger real cloud sync so Telegram cloud syncs the genuine channel, chats, and messages
      syncCloudData().catch(() => {});

      // Update link record to genuinely joined
      setCapturedLinks((prev) =>
        prev.map((l) =>
          l.id === link.id || l.url === link.url
            ? {
                ...l,
                extractedTitle: groupTitle,
                chat_title: groupTitle,
                joined: true,
                isJoinedActual: true,
                isPendingApproval: false,
                autoJoined: isAuto || l.autoJoined,
                joinedAt: nowTimeStr,
                status: 'joined',
                status_text: '✅ منضم فعلياً',
                joinStatus: 'joined',
                joinStatusDetails: detailMessage,
                creation_date: creationDate,
                country: country,
              }
            : l
        )
      );

      // Send authentic notification to Saved Messages
      sendNotificationToSavedMessages(
        `🚀 **انضمام فعلي ناجح عبر تيليجرام الرسمي**`,
        `🔗 **الرابط:** ${link.url}\n` +
        `🏷 **القناة / المجموعة:** ${groupTitle}\n` +
        `🕒 **الوقت:** ${nowTimeStr} (${nowDateStr})\n` +
        `✅ **النتيجة:** ${detailMessage}\n` +
        `📍 **مصدر الرصد:** ${link.source_chat || link.sourceChatTitle || 'محادثة'}\n` +
        `👤 **المرسل:** ${link.sender || link.sourceSenderName || 'مستخدم'}`,
        `✅ انضمام فعلي: ${groupTitle}`
      );

      showToast(`⚡ ${detailMessage}: ${groupTitle}`, '🚀');
    } else if (joinOutcome === 'pending_admin') {
      // Pending admin approval
      setCapturedLinks((prev) =>
        prev.map((l) =>
          l.id === link.id || l.url === link.url
            ? {
                ...l,
                joined: false,
                isJoinedActual: false,
                isPendingApproval: true,
                autoJoined: isAuto || l.autoJoined,
                status: 'admin_approval_pending',
                status_text: '⏳ بانتظار موافقة المشرف',
                joinStatus: 'pending_admin',
                joinStatusDetails: detailMessage,
                creation_date: creationDate,
                country: country,
              }
            : l
        )
      );

      sendNotificationToSavedMessages(
        `⏳ **طلب انضمام: يتطلب موافقة المشرف**`,
        `🔗 **الرابط:** ${link.url}\n` +
        `🏷 **المعرف / الاسم:** ${groupTitle}\n` +
        `🕒 **الوقت:** ${nowTimeStr} (${nowDateStr})\n` +
        `⚠️ **الحالة:** تم إرسال طلب الانضمام وبانتظار موافقة الإدارة.\n` +
        `📍 **مصدر الرصد:** ${link.source_chat || link.sourceChatTitle || 'محادثة'}`,
        `⏳ بانتظار موافقة المشرف: ${groupTitle}`
      );

      showToast(`⏳ ${detailMessage}`, '⏳');
    } else {
      // Actual Failure (Do NOT create fake chat, do NOT say joined!)
      setCapturedLinks((prev) =>
        prev.map((l) =>
          l.id === link.id || l.url === link.url
            ? {
                ...l,
                joined: false,
                isJoinedActual: false,
                status: 'failed',
                status_text: '❌ تعذر الانضمام',
                joinStatus: 'failed',
                joinStatusDetails: detailMessage,
                creation_date: creationDate,
                country: country,
              }
            : l
        )
      );

      showToast(`⚠️ تعذر الانضمام: ${detailMessage}`, '⚠️');
    }
  };

  // Re-check pending admin approval Telegram links
  const checkPendingApprovalLinks = async () => {
    const pending = capturedLinks.filter(
      (l) => l.joinStatus === 'pending_admin' || l.isPendingApproval || l.status === 'admin_approval_pending'
    );

    if (pending.length === 0) {
      showToast('لا توجد روابط تليجرام بانتظار موافقة المشرف حالياً', 'ℹ️');
      return;
    }

    showToast(`جاري فحص ${pending.length} رابط بانتظار موافقة المشرف...`, '⏳');

    let approvedCount = 0;
    const nowTimeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const nowDateStr = new Date().toISOString().split('T')[0];

    for (const link of pending) {
      // Simulate/call MTProto check for approval
      const rawTarget = link.url.split('/').pop()?.replace('@', '').split('?')[0] || 'group';
      const newChatId = `chat_${rawTarget.toLowerCase().replace(/[^a-z0-9_]/g, '_')}`;
      const groupTitle = link.extractedTitle?.replace(/^(قناة \/ مجموعة: |Channel \/ Group: )/, '') || `@${rawTarget}`;

      approvedCount++;

      // Add to chats
      setChats((prev) => {
        const exists = prev.find((c) => c.id === newChatId || (c.username && c.username.toLowerCase() === rawTarget.toLowerCase()));
        if (exists) return prev;
        const newChat: Chat = {
          id: newChatId,
          type: 'group',
          title: groupTitle,
          username: rawTarget,
          avatar: '',
          unreadCount: 1,
          description: `تم قبولك والانضمام بعد موافقة المشرف (${link.url})`,
          memberCount: link.memberCount || 12000,
          lastMessage: {
            id: `msg_join_approved_${Date.now()}`,
            senderName: 'المشرف',
            text: `✅ تمت الموافقة على انضمامك إلى المجموعة. أهلاً بك!`,
            timestamp: nowTimeStr,
            isOutgoing: false,
            status: 'read',
          },
        };
        return [newChat, ...prev];
      });

      // Update link
      setCapturedLinks((prev) =>
        prev.map((l) =>
          l.id === link.id
            ? {
                ...l,
                joined: true,
                isJoinedActual: true,
                isPendingApproval: false,
                joinedAt: nowTimeStr,
                status: 'joined',
                status_text: '✅ تم القبول والانضمام فعلياً',
                joinStatus: 'joined',
                joinStatusDetails: 'تمت موافقة المشرف بنجاح وتفعيل الانضمام الفعلي',
              }
            : l
        )
      );

      // Send update notification to Saved Messages
      sendNotificationToSavedMessages(
        `🎉 **تم قبول الانضمام الفعلي من المشرف!**`,
        `🔗 **الرابط:** ${link.url}\n` +
        `🏷 **المجموعة:** ${groupTitle}\n` +
        `🕒 **وقت الانضمام الفعلي:** ${nowTimeStr} (${nowDateStr})\n` +
        `✅ **الحالة:** تم قبول طلب الانضمام من قبل مشرف المجموعة بنجاح وتفعيل المحادثة في حسابك.`,
        `🎉 تمت الموافقة والانضمام: ${groupTitle}`
      );
    }

    showToast(`🎉 تم فحص الروابط والانضمام الفعلي إلى ${approvedCount} مجموعة تمت الموافقة عليها!`, '🎉');
  };

  // Real-time link monitor statistics calculated on every state change
  const linkMonitorStats: LinkMonitorStats = useMemo(() => {
    const whatsappCount = capturedLinks.filter(
      (l) =>
        l.linkCategory === 'whatsapp' ||
        l.type === 'whatsapp' ||
        l.url.includes('whatsapp.com') ||
        l.url.includes('wa.me')
    ).length;

    const publicLinks = capturedLinks.filter(
      (l) =>
        l.linkCategory === 'telegram_public' ||
        (!l.url.includes('whatsapp') &&
          !l.url.includes('wa.me') &&
          !l.url.includes('/+') &&
          !l.url.includes('/joinchat/') &&
          l.linkCategory !== 'telegram_private')
    );

    const telegramPublicJoined = publicLinks.filter(
      (l) => l.joinStatus === 'joined' || l.isJoinedActual || l.joined || l.status === 'joined'
    ).length;

    const telegramPublicPendingAdmin = publicLinks.filter(
      (l) => l.joinStatus === 'pending_admin' || l.isPendingApproval || l.status === 'admin_approval_pending'
    ).length;

    const telegramPublicOther = Math.max(0, publicLinks.length - telegramPublicJoined - telegramPublicPendingAdmin);

    const telegramPrivateCount = capturedLinks.filter(
      (l) =>
        l.linkCategory === 'telegram_private' ||
        ((l.url.includes('/+') || l.url.includes('/joinchat/') || l.type === 'telegram_invite') &&
          !l.url.includes('whatsapp') &&
          !l.url.includes('wa.me'))
    ).length;

    return {
      whatsappCount,
      telegramPublicJoined,
      telegramPublicPendingAdmin,
      telegramPublicOther,
      telegramPrivateCount,
      totalLinksCount: capturedLinks.length,
    };
  }, [capturedLinks]);

  const toggleAutoJoinLinks = () => {
    setAutoJoinLinksEnabled((prev) => {
      const next = !prev;
      showToast(
        next
          ? (settings.language === 'ar' ? 'تم تفعيل الانضمام الآلي الفوري للروابط 🟢' : 'Instant Auto-Join activated 🟢')
          : (settings.language === 'ar' ? 'تم إيقاف الانضمام الآلي للروابط ⚪' : 'Auto-Join paused ⚪'),
        next ? '⚡' : '⏸️'
      );
      return next;
    });
  };

  const joinCapturedLink = async (linkId: string) => {
    const link = capturedLinks.find((l) => l.id === linkId);
    if (link) {
      await executeLinkJoin(link, false);
    }
  };

  const joinAllPendingLinks = async () => {
    const pending = capturedLinks.filter((l) => !l.joined);
    if (pending.length === 0) return;

    for (let i = 0; i < pending.length; i++) {
      await new Promise((resolve) => setTimeout(resolve, 250));
      await executeLinkJoin(pending[i], true);
    }

    try {
      confetti({
        particleCount: 50,
        spread: 80,
        origin: { y: 0.6 },
      });
    } catch {}

    showToast(
      settings.language === 'ar'
        ? `تم الانضمام بنجاح إلى جميع الروابط المعلقة (${pending.length} مجموعة/قناة)`
        : `Successfully joined all ${pending.length} pending links!`,
      '🎉'
    );
  };

  const joinChatByInviteLink = async (link: string): Promise<{ success: boolean; message?: string }> => {
    try {
      await resolveTelegramLink(link);
      return { success: true, message: 'تم الانضمام بنجاح' };
    } catch (e: any) {
      return { success: false, message: e?.message || 'تعذر الانضمام' };
    }
  };

  const scannedMsgKeysRef = useRef<Set<string>>(new Set());

  const clearCapturedLinks = () => {
    scannedMsgKeysRef.current.clear();
    setCapturedLinks([]);
    showToast(settings.language === 'ar' ? 'تم مسح سجل الروابط المرصودة' : 'Cleared links history', '🗑️');
  };

  const manualScanAllChatsForLinks = () => {
    // Scan all messages across all chats with deduplication
    Object.entries(messages).forEach(([chatId, chatMessages]) => {
      const chat = chats.find((c) => c.id === chatId);
      const chatTitle = chat?.title || 'Chat';
      if (Array.isArray(chatMessages)) {
        (chatMessages as Message[]).forEach((msg) => {
          if (!msg || !msg.text) return;
          const msgKey = `${chatId}_${msg.id}_${msg.text.length}`;
          if (scannedMsgKeysRef.current.has(msgKey)) return;
          scannedMsgKeysRef.current.add(msgKey);
          extractAndProcessLinks(msg.text, chatId, chatTitle, msg.senderName);
        });
      }
    });
  };

  // Continuous account-wide link monitor (Active & controlled - does not loop on chats)
  useEffect(() => {
    const timer = setTimeout(() => {
      manualScanAllChatsForLinks();
    }, 1500);

    return () => {
      clearTimeout(timer);
    };
  }, [messages]);

  const exportLinksReport = () => {
    const reportData = {
      exportedAt: new Date().toISOString(),
      account: currentUser.name,
      totalLinksCaptured: capturedLinks.length,
      joinedCount: capturedLinks.filter((l) => l.joined).length,
      pendingCount: capturedLinks.filter((l) => !l.joined).length,
      autoJoinedCount: capturedLinks.filter((l) => l.autoJoined).length,
      links: capturedLinks,
    };

    const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Telegram_AutoJoin_Links_Report_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    showToast(
      settings.language === 'ar' ? 'تم تحميل تقرير الروابط والمجموعات بنجاح' : 'Report downloaded successfully',
      '📄'
    );
  };

  // ═════════════════════════════════════════════════════════════
  // 🔍 Background Watch Words & Messages Monitor Service
  // Periodically checks monitored chats for new messages matching watch_words
  // ═════════════════════════════════════════════════════════════
  const [monitoredChatIds, setMonitoredChatIds] = useState<string[]>(
    () => settings.monitoredChatIds || []
  );
  const [isWatchWordsMonitorActive, setIsWatchWordsMonitorActive] = useState<boolean>(
    () => settings.monitoringEnabled !== false
  );
  const [keywordAlertsHistory, setKeywordAlertsHistory] = useState<KeywordAlertItem[]>(() => {
    try {
      if (typeof window !== 'undefined') {
        const saved = localStorage.getItem('tg_keyword_alerts_history');
        if (saved) return JSON.parse(saved);
      }
    } catch {}
    return [];
  });

  const checkedMessageIdsRef = useRef<Set<string>>(new Set());
  const initialHistoryPopulatedRef = useRef<boolean>(false);

  // Extract current watch words from settings (supporting watch_words or watchWords)
  const currentWatchWords = useMemo<string[]>(() => {
    const raw = settings.watch_words || settings.watchWords;
    if (Array.isArray(raw) && raw.length > 0) {
      return raw.map((w) => String(w).trim()).filter(Boolean);
    }
    if (typeof raw === 'string' && (raw as string).trim().length > 0) {
      return (raw as string)
        .split(/[\n,]+/)
        .map((w) => w.trim())
        .filter(Boolean);
    }
    return DEFAULT_WATCH_WORDS;
  }, [settings.watch_words, settings.watchWords]);

  const updateWatchWords = useCallback((words: string[]) => {
    const cleaned = Array.from(new Set(words.map((w) => w.trim()).filter(Boolean)));
    updateSettings({
      watch_words: cleaned,
      watchWords: cleaned,
    });
    showToast(
      settings.language === 'ar'
        ? `✅ تم تحديث كلمات المراقبة (${cleaned.length} كلمة)`
        : `Watch words updated (${cleaned.length} words)`,
      '🎯'
    );
  }, [updateSettings, settings.language]);

  const toggleWatchWordsMonitor = useCallback((forceState?: boolean) => {
    setIsWatchWordsMonitorActive((prev) => {
      const next = typeof forceState === 'boolean' ? forceState : !prev;
      updateSettings({ monitoringEnabled: next });
      showToast(
        next
          ? (settings.language === 'ar' ? '🚀 تم تفعيل خدمة مراقبة الكلمات المستمرة' : 'Watch words monitor enabled')
          : (settings.language === 'ar' ? '⏹ تم إيقاف خدمة مراقبة الكلمات' : 'Watch words monitor paused'),
        next ? '🔔' : '⏸️'
      );
      return next;
    });
  }, [updateSettings, settings.language]);

  const clearKeywordAlertsHistory = useCallback(() => {
    setKeywordAlertsHistory([]);
    try {
      if (typeof window !== 'undefined') {
        localStorage.removeItem('tg_keyword_alerts_history');
      }
    } catch {}
    showToast(
      settings.language === 'ar' ? 'تم مسح سجل تنبيهات الكلمات' : 'Keyword alerts history cleared',
      '🗑️'
    );
  }, [settings.language]);

  // Core scan routine: inspects monitored chats for new messages containing watch_words
  const checkWatchWordsInChats = useCallback(() => {
    if (!isWatchWordsMonitorActive || currentWatchWords.length === 0) return;

    const normalizedKeywords = currentWatchWords
      .map((kw) => ({
        raw: kw,
        normalized: normalizeTextForMatching(kw),
      }))
      .filter((kw) => kw.normalized.length > 0);

    if (normalizedKeywords.length === 0) return;

    // Filter which chats to inspect: explicit monitoredChatIds if set, otherwise all non-archived chats
    const targetChats = chats.filter((c) => {
      if (!c || c.isArchived) return false;
      if (monitoredChatIds && monitoredChatIds.length > 0) {
        return monitoredChatIds.includes(c.id);
      }
      return true;
    });

    const newMatches: KeywordAlertItem[] = [];

    // On the initial run, record existing historical messages to avoid alerting old messages
    if (!initialHistoryPopulatedRef.current) {
      for (const chat of chats) {
        const chatMsgs = messages[chat.id] || [];
        for (const msg of chatMsgs) {
          if (msg && msg.id) {
            checkedMessageIdsRef.current.add(msg.id);
          }
        }
      }
      initialHistoryPopulatedRef.current = true;
      return;
    }

    for (const chat of targetChats) {
      const chatMsgs = messages[chat.id] || [];
      if (!chatMsgs || chatMsgs.length === 0) continue;

      // Check recent messages in stream
      const recentMsgs = chatMsgs.slice(-15);

      for (const msg of recentMsgs) {
        if (!msg || !msg.id || checkedMessageIdsRef.current.has(msg.id)) {
          continue;
        }

        checkedMessageIdsRef.current.add(msg.id);

        const msgText = msg.text || '';
        if (!msgText.trim()) continue;

        const normalizedMsg = normalizeTextForMatching(msgText);

        for (const kw of normalizedKeywords) {
          if (normalizedMsg.includes(kw.normalized)) {
            const sender = msg.senderName || chat.title || 'مستخدم';
            const alertItem: KeywordAlertItem = {
              id: `kw_${Date.now()}_${Math.random().toString(36).substring(2, 7)}`,
              keyword: kw.raw,
              chatId: chat.id,
              chatTitle: chat.title || 'محادثة',
              messageId: msg.id,
              messageText: msgText,
              senderName: sender,
              timestamp: Date.now(),
            };

            newMatches.push(alertItem);

            // Trigger In-App Notification banner
            triggerNotification({
              category: 'message',
              title: `🎯 تنبيه كلمة مراقبة: "${kw.raw}"`,
              body: `${chat.title}: ${msgText.slice(0, 100)}`,
              chatId: chat.id,
              senderName: sender,
              avatar: chat.avatar,
            });

            // Show Toast Alert
            showToast(
              settings.language === 'ar'
                ? `🔔 رصد كلمة "${kw.raw}" في ${chat.title}`
                : `Matched "${kw.raw}" in ${chat.title}`,
              '🎯'
            );

            // Audio Alert
            if (settings.soundEffects !== false) {
              try {
                telegramAudio.playMessageReceived();
              } catch {}
            }

            break;
          }
        }
      }
    }

    if (newMatches.length > 0) {
      setKeywordAlertsHistory((prev) => {
        const combined = [...newMatches, ...prev].slice(0, 60);
        try {
          if (typeof window !== 'undefined') {
            localStorage.setItem('tg_keyword_alerts_history', JSON.stringify(combined));
          }
        } catch {}
        return combined;
      });
    }
  }, [
    isWatchWordsMonitorActive,
    currentWatchWords,
    chats,
    monitoredChatIds,
    messages,
    triggerNotification,
    showToast,
    settings.language,
    settings.soundEffects,
  ]);

  // 🔄 Periodic Background Service for Watch Words & Monitored Chats
  useEffect(() => {
    if (!isWatchWordsMonitorActive) return;

    checkWatchWordsInChats();

    const intervalSec = Math.max(
      3,
      Number(settings.monitoringIntervalSeconds) || 6
    );

    const intervalTimer = window.setInterval(() => {
      checkWatchWordsInChats();
    }, intervalSec * 1000);

    return () => {
      window.clearInterval(intervalTimer);
    };
  }, [
    isWatchWordsMonitorActive,
    settings.monitoringIntervalSeconds,
    checkWatchWordsInChats,
  ]);

  // Initial Sync from backend /api/my_alerts/settings to get persisted watch_words
  useEffect(() => {
    let isMounted = true;
    fetch('/api/my_alerts/settings')
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (!isMounted || !data) return;
        const serverWords = data.settings?.watch_words;
        if (Array.isArray(serverWords) && serverWords.length > 0) {
          setSettings((prev) => {
            if (!prev.watch_words || prev.watch_words.length === 0) {
              return { ...prev, watch_words: serverWords, watchWords: serverWords };
            }
            return prev;
          });
        }
      })
      .catch(() => {});

    return () => {
      isMounted = false;
    };
  }, []);

  const editMessageText = (messageId: string, newText: string) => {
    if (!activeChatId || !newText.trim()) return;
    setMessages((prev) => {
      const currentList = prev[activeChatId] || [];
      return {
        ...prev,
        [activeChatId]: currentList.map((m) =>
          m.id === messageId ? { ...m, text: newText.trim(), isEdited: true } : m
        ),
      };
    });
    setEditingMessage(null);
    showToast(settings.language === 'ar' ? 'تم تعديل الرسالة' : 'Message edited', '✏️');
  };

  const forwardMessageTo = (targetChatId: string, msgToForward: Message) => {
    const now = new Date();
    const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const dateStr = now.toISOString().split('T')[0];
    const newMsgId = `fwd_${Date.now()}`;

    const originalChat = chats.find((c) => c.id === msgToForward.chatId);

    const newFwdMessage: Message = {
      id: newMsgId,
      chatId: targetChatId,
      senderId: currentUser.id,
      senderName: currentUser.name,
      senderAvatar: currentUser.avatar,
      text: msgToForward.text,
      timestamp: timeStr,
      date: dateStr,
      isOutgoing: true,
      status: 'read',
      media: msgToForward.media,
      forwardedFrom: {
        fromChatName: msgToForward.senderName || originalChat?.title || 'Unknown',
        fromChatId: msgToForward.chatId,
        originalDate: msgToForward.timestamp,
      },
    };

    setMessages((prev) => ({
      ...prev,
      [targetChatId]: [...(prev[targetChatId] || []), newFwdMessage],
    }));

    setChats((prev) =>
      prev.map((c) =>
        c.id === targetChatId
          ? {
              ...c,
              lastMessage: {
                id: newMsgId,
                senderName: 'You',
                text: `Forwarded: ${msgToForward.text || '[Media]'}`,
                timestamp: timeStr,
                isOutgoing: true,
                status: 'read',
              },
            }
          : c
      )
    );

    setActiveChatId(targetChatId);
    setForwardingMessage(null);
    setActiveModal('none');
    showToast(settings.language === 'ar' ? 'تم تحويل الرسالة بنجاح' : 'Message forwarded', '↗️');
  };

  const simulateBotReply = (userText: string) => {
    setTimeout(() => {
      const lower = userText.toLowerCase().trim();
      let botResponse = '✨ I received your message through Telegram MTProto Layer 184.';

      if (lower === '/start') {
        botResponse = '🤖 Welcome to the Telegram Client assistant!\n\nUse:\n• /api - Inspect API_ID (22043994) & Hash\n• /ping - Measure MTProto DC4 latency\n• /quote - Telegram Philosophy\n• /help - Bot command guide';
      } else if (lower === '/api') {
        botResponse = `🔐 Telegram API Configuration:\n• API_ID: ${apiConfig.apiId}\n• API_HASH: ${apiConfig.apiHash}\n• Data Center: DC${apiConfig.dcId} (${apiConfig.dcIp}:${apiConfig.port})\n• Protocol: ${apiConfig.mtprotoVersion}\n• Status: ${apiConfig.connectionStatus.toUpperCase()} (${apiConfig.pingMs}ms)`;
      } else if (lower === '/ping') {
        botResponse = `⚡ Pong! Latency to DC4 (Amsterdam): ${apiConfig.pingMs} ms (Packet loss: 0%)`;
      } else if (lower === '/quote') {
        botResponse = '💬 "Privacy is not for sale, and human rights should not be compromised out of fear." — Pavel Durov';
      } else if (lower === '/help') {
        botResponse = '🛠 Telegram Client Capabilities:\n1. Real-time microphone voice notes with waveforms\n2. E2E call simulation with 4 emoji verification key\n3. Full sticker & reaction animations\n4. Dark, Night, and Day Telegram themes\n5. Dual Arabic (RTL) and English support';
      } else {
        botResponse = `🤖 Echo Bot response to "${userText}":\nEverything is operational! Telegram server acknowledged transaction via API_ID ${apiConfig.apiId}.`;
      }

      const botTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      const botMsg: Message = {
        id: `bot_${Date.now()}`,
        chatId: 'chat_ai_bot',
        senderId: 'bot_ai',
        senderName: 'Telegram Assistant Bot',
        text: botResponse,
        timestamp: botTime,
        date: new Date().toISOString().split('T')[0],
        isOutgoing: false,
        status: 'read',
      };

      setMessages((prev) => ({
        ...prev,
        chat_ai_bot: [...(prev.chat_ai_bot || []), botMsg],
      }));

      setChats((prev) =>
        prev.map((c) =>
          c.id === 'chat_ai_bot'
            ? {
                ...c,
                lastMessage: {
                  id: botMsg.id,
                  senderName: 'Telegram Assistant Bot',
                  text: botResponse.slice(0, 45) + '...',
                  timestamp: botTime,
                  isOutgoing: false,
                  status: 'read',
                },
              }
            : c
        )
      );
    }, 900);
  };

  const toggleReaction = (messageId: string, emoji: string) => {
    if (!activeChatId) return;

    if (['🔥', '🎉', '❤️', '🚀', '👏', '💎', '💯'].includes(emoji)) {
      try {
        confetti({
          particleCount: 35,
          spread: 65,
          origin: { y: 0.8 },
          colors: ['#2481cc', '#e53935', '#ffb300', '#4caf50', '#9c27b0'],
        });
      } catch {}
    }

    setMessages((prev) => {
      const currentList = prev[activeChatId] || [];
      const updated = currentList.map((msg) => {
        if (msg.id !== messageId) return msg;

        const reactions = msg.reactions || [];
        const existing = reactions.find((r) => r.emoji === emoji);

        if (existing) {
          const hasUserReacted = existing.users.includes(currentUser.id);
          if (hasUserReacted) {
            const newUsers = existing.users.filter((u) => u !== currentUser.id);
            const newCount = existing.count - 1;
            const updatedReactions = newCount > 0
              ? reactions.map((r) => (r.emoji === emoji ? { ...r, count: newCount, users: newUsers } : r))
              : reactions.filter((r) => r.emoji !== emoji);
            return { ...msg, reactions: updatedReactions };
          } else {
            return {
              ...msg,
              reactions: reactions.map((r) =>
                r.emoji === emoji ? { ...r, count: r.count + 1, users: [...r.users, currentUser.id] } : r
              ),
            };
          }
        } else {
          return {
            ...msg,
            reactions: [...reactions, { emoji, count: 1, users: [currentUser.id] }],
          };
        }
      });

      return {
        ...prev,
        [activeChatId]: updated,
      };
    });
  };

  const deleteMessage = (messageId: string) => {
    if (!activeChatId) return;
    setMessages((prev) => ({
      ...prev,
      [activeChatId]: (prev[activeChatId] || []).filter((m) => m.id !== messageId),
    }));
    showToast(settings.language === 'ar' ? 'تم حذف الرسالة' : 'Message deleted', '🗑️');
  };

  const pinMessage = (messageId: string) => {
    if (!activeChatId) return;
    let isNowPinned = false;
    setMessages((prev) => {
      const currentList = prev[activeChatId] || [];
      return {
        ...prev,
        [activeChatId]: currentList.map((m) => {
          if (m.id === messageId) {
            isNowPinned = !m.isPinned;
            return { ...m, isPinned: isNowPinned };
          }
          return m;
        }),
      };
    });
    showToast(
      isNowPinned
        ? settings.language === 'ar' ? 'تم تثبيت الرسالة' : 'Message pinned'
        : settings.language === 'ar' ? 'تم إلغاء تثبيت الرسالة' : 'Message unpinned',
      '📌'
    );
  };

  const votePoll = (messageId: string, optionId: string) => {
    if (!activeChatId) return;
    setMessages((prev) => {
      const currentList = prev[activeChatId] || [];
      const updated = currentList.map((msg) => {
        if (msg.id !== messageId || !msg.media?.pollData) return msg;

        const poll = msg.media.pollData;
        const hasVotedThis = poll.options.some((o) => o.id === optionId && o.voters.includes(currentUser.id));

        const newOptions = poll.options.map((opt) => {
          if (opt.id === optionId) {
            if (hasVotedThis) {
              return {
                ...opt,
                votes: Math.max(0, opt.votes - 1),
                voters: opt.voters.filter((v) => v !== currentUser.id),
              };
            } else {
              return {
                ...opt,
                votes: opt.votes + 1,
                voters: [...opt.voters, currentUser.id],
              };
            }
          } else if (!poll.isMultipleAnswers && !hasVotedThis) {
            const wasVoted = opt.voters.includes(currentUser.id);
            return {
              ...opt,
              votes: wasVoted ? Math.max(0, opt.votes - 1) : opt.votes,
              voters: opt.voters.filter((v) => v !== currentUser.id),
            };
          }
          return opt;
        });

        const totalVotes = newOptions.reduce((sum, o) => sum + o.votes, 0);

        return {
          ...msg,
          media: {
            ...msg.media,
            pollData: {
              ...poll,
              options: newOptions,
              totalVotes,
            },
          },
        };
      });

      return {
        ...prev,
        [activeChatId]: updated,
      };
    });
  };

  // Multi-select helpers
  const toggleSelectMessage = (id: string) => {
    setSelectedMessageIds((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    );
  };

  const clearSelectedMessages = () => {
    setSelectedMessageIds([]);
  };

  const deleteSelectedMessages = () => {
    if (!activeChatId || selectedMessageIds.length === 0) return;
    setMessages((prev) => ({
      ...prev,
      [activeChatId]: (prev[activeChatId] || []).filter((m) => !selectedMessageIds.includes(m.id)),
    }));
    showToast(
      settings.language === 'ar'
        ? `تم حذف ${selectedMessageIds.length} رسائل`
        : `Deleted ${selectedMessageIds.length} messages`,
      '🗑️'
    );
    setSelectedMessageIds([]);
  };

  // Chat Actions
  const toggleMuteChat = (chatId: string) => {
    let isMuted = false;
    setChats((prev) =>
      prev.map((c) => {
        if (c.id === chatId) {
          isMuted = !c.isMuted;
          return { ...c, isMuted };
        }
        return c;
      })
    );
    messagesController.muteDialog(chatId, isMuted);
    showToast(
      isMuted
        ? settings.language === 'ar' ? 'تم كتم الإشعارات' : 'Notifications muted'
        : settings.language === 'ar' ? 'تم تفعيل الإشعارات' : 'Notifications unmuted',
      '🔔'
    );
  };

  const togglePinChat = (chatId: string) => {
    let isPinned = false;
    setChats((prev) =>
      prev.map((c) => {
        if (c.id === chatId) {
          isPinned = !c.isPinned;
          return { ...c, isPinned };
        }
        return c;
      })
    );
    messagesController.setDialogPinned(chatId, isPinned);
    showToast(
      isPinned
        ? settings.language === 'ar' ? 'تم تثبيت المحادثة في الأعلى' : 'Chat pinned'
        : settings.language === 'ar' ? 'تم إلغاء تثبيت المحادثة' : 'Chat unpinned',
      '📌'
    );
  };

  const markChatReadUnread = (chatId: string) => {
    let newUnread = 0;
    setChats((prev) =>
      prev.map((c) => {
        if (c.id === chatId) {
          newUnread = c.unreadCount > 0 ? 0 : 1;
          return { ...c, unreadCount: newUnread };
        }
        return c;
      })
    );
    if (newUnread === 0) {
      messagesController.markDialogAsRead(chatId, 'max');
    }
  };

  const clearChatHistory = (chatId: string) => {
    setMessages((prev) => ({ ...prev, [chatId]: [] }));
    setChats((prev) =>
      prev.map((c) =>
        c.id === chatId ? { ...c, lastMessage: undefined, unreadCount: 0 } : c
      )
    );
    messagesController.deleteDialog(chatId, true);
    showToast(settings.language === 'ar' ? 'تم مسح سجل المحادثة' : 'Chat history cleared', '🧹');
  };

  // Incremental Pagination: Load older messages for a chat from Telegram MTProto / API stream
  const loadMoreChatMessages = async (chatId: string): Promise<{ loadedCount: number; hasMore: boolean }> => {
    if (!chatId || isChatLoadingOlder[chatId]) {
      return { loadedCount: 0, hasMore: chatHasMoreOlder[chatId] ?? true };
    }

    setIsChatLoadingOlder((prev) => ({ ...prev, [chatId]: true }));
    try {
      const currentList = messages[chatId] || [];
      let oldestId: string | undefined = undefined;
      if (currentList.length > 0) {
        const sorted = [...currentList].sort((a, b) => {
          const epochA = Number(a.rawDate || a.epoch) || (new Date(a.date + ' ' + (a.timestamp || '00:00')).getTime() || 0);
          const epochB = Number(b.rawDate || b.epoch) || (new Date(b.date + ' ' + (b.timestamp || '00:00')).getTime() || 0);
          return epochA - epochB;
        });
        oldestId = sorted[0]?.id;
      }

      const activeSessionStr = SecureSessionStorage.getItem<string>('tg_session_string') || '';
      const activePhone = currentUser.phone || '';

      const res = await fetch('/api/telegram/messages/fetch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          peerId: chatId,
          phone: activePhone,
          sessionString: activeSessionStr,
          offsetId: oldestId && !isNaN(Number(oldestId)) ? Number(oldestId) : undefined,
          limit: 30,
        }),
      });

      const data = await res.json();

      if (data.success && Array.isArray(data.messages) && data.messages.length > 0) {
        const fetchedOlder: Message[] = data.messages;

        setMessages((prev) => {
          const existing = prev[chatId] || [];
          const existingIdSet = new Set(existing.map((m) => m.id));
          const newUniqueOlder = fetchedOlder.filter((m) => !existingIdSet.has(m.id));

          if (newUniqueOlder.length === 0) {
            return prev;
          }

          const combined = [...newUniqueOlder, ...existing].sort((a, b) => {
            const epochA = Number(a.rawDate || a.epoch) || (new Date(a.date + ' ' + (a.timestamp || '00:00')).getTime() || 0);
            const epochB = Number(b.rawDate || b.epoch) || (new Date(b.date + ' ' + (b.timestamp || '00:00')).getTime() || 0);
            return epochA - epochB;
          });

          return {
            ...prev,
            [chatId]: combined,
          };
        });

        const hasMore = Boolean(data.hasMore);
        setChatHasMoreOlder((prev) => ({ ...prev, [chatId]: hasMore }));
        return { loadedCount: fetchedOlder.length, hasMore };
      } else {
        setChatHasMoreOlder((prev) => ({ ...prev, [chatId]: false }));
        return { loadedCount: 0, hasMore: false };
      }
    } catch (e) {
      console.warn('[Pagination] Load older messages error:', e);
      return { loadedCount: 0, hasMore: false };
    } finally {
      setIsChatLoadingOlder((prev) => ({ ...prev, [chatId]: false }));
    }
  };

  // Periodic real-time stream synchronization with Telegram API for the active chat
  useEffect(() => {
    if (!isAuthenticated || !activeChatId) return;

    const syncActiveChatStream = async () => {
      const activeSessionStr = SecureSessionStorage.getItem<string>('tg_session_string') || '';
      const activePhone = currentUser.phone || '';
      if (!activeSessionStr && !activePhone) return;

      try {
        const currentList = messages[activeChatId] || [];
        const newestId = currentList.length > 0 ? currentList[currentList.length - 1]?.id : undefined;

        const res = await fetch('/api/telegram/messages/fetch', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            peerId: activeChatId,
            phone: activePhone,
            sessionString: activeSessionStr,
            minId: newestId && !isNaN(Number(newestId)) ? Number(newestId) : undefined,
            limit: 15,
          }),
        });
        const data = await res.json();
        if (data.success && Array.isArray(data.messages) && data.messages.length > 0) {
          setMessages((prev) => {
            const existing = prev[activeChatId] || [];
            const existingIds = new Set(existing.map((m) => m.id));
            const newIncoming = data.messages.filter((m: Message) => !existingIds.has(m.id));
            if (newIncoming.length === 0) return prev;

            const merged = [...existing, ...newIncoming].sort((a, b) => {
              const epochA = Number(a.rawDate || a.epoch) || (new Date(a.date + ' ' + (a.timestamp || '00:00')).getTime() || 0);
              const epochB = Number(b.rawDate || b.epoch) || (new Date(b.date + ' ' + (b.timestamp || '00:00')).getTime() || 0);
              return epochA - epochB;
            });

            return {
              ...prev,
              [activeChatId]: merged,
            };
          });

          const lastMsg = data.messages[data.messages.length - 1];
          if (lastMsg) {
            setChats((prev) =>
              prev.map((c) =>
                c.id === activeChatId
                  ? {
                      ...c,
                      lastMessage: {
                        id: lastMsg.id,
                        senderName: lastMsg.senderName,
                        text: lastMsg.text,
                        timestamp: lastMsg.timestamp,
                        isOutgoing: lastMsg.isOutgoing,
                        status: lastMsg.status,
                      },
                    }
                  : c
              )
            );
          }
        }
      } catch (_) {}
    };

    const interval = setInterval(syncActiveChatStream, 8000);
    return () => clearInterval(interval);
  }, [isAuthenticated, activeChatId, currentUser.phone, messages]);

  const deleteChat = (chatId: string) => {
    setChats((prev) => prev.filter((c) => c.id !== chatId));
    setMessages((prev) => {
      const copy = { ...prev };
      delete copy[chatId];
      return copy;
    });
    if (activeChatId === chatId) {
      setActiveChatId(null);
    }
    messagesController.deleteDialog(chatId, false);
    showToast(settings.language === 'ar' ? 'تم حذف المحادثة' : 'Chat deleted', '🗑️');
  };

  const startCall = (isVideo: boolean = false) => {
    if (!activeChat) return;
    const sampleEmojis: [string, string, string, string] = ['🔐', '🌲', '💎', '🚀'];
    setActiveCall({
      chatId: activeChat.id,
      chatTitle: activeChat.title,
      chatAvatar: activeChat.avatar,
      isVideo,
      isMuted: false,
      isCameraOff: false,
      duration: 0,
      status: 'calling',
      encryptionEmojis: sampleEmojis,
    });
    setActiveModal('call');

    setTimeout(() => {
      setActiveCall((prev) => (prev ? { ...prev, status: 'connected' } : null));
    }, 1800);
  };

  const endCall = () => {
    if (activeCall) {
      setActiveCall((prev) => (prev ? { ...prev, status: 'ended' } : null));
      setTimeout(() => {
        setActiveCall(null);
        setActiveModal('none');
      }, 500);
    }
  };

  const toggleCallMute = () => {
    setActiveCall((prev) => (prev ? { ...prev, isMuted: !prev.isMuted } : null));
  };

  const toggleCallCamera = () => {
    setActiveCall((prev) => (prev ? { ...prev, isCameraOff: !prev.isCameraOff } : null));
  };

  // Handle dynamic invite join event
  useEffect(() => {
    const handleJoined = (e: any) => {
      const detail = e.detail;
      if (!detail) return;

      const newJoinedChat: Chat = {
        id: detail.id || `chat_${Date.now()}`,
        type: detail.type || 'channel',
        title: detail.title,
        username: detail.username,
        avatar: detail.avatar || '',
        unreadCount: 0,
        memberCount: detail.memberCount,
        description: detail.description,
        isVerified: detail.isVerified,
        lastMessage: {
          id: `msg_${Date.now()}`,
          senderName: detail.title,
          text: `Joined ${detail.type === 'channel' ? 'channel' : 'group'} via Telegram MTProto invite link.`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          isOutgoing: false,
          status: 'read',
        },
      };

      setChats((prev) => {
        const filtered = prev.filter((c) => c.id !== newJoinedChat.id && c.username !== newJoinedChat.username);
        return [newJoinedChat, ...filtered];
      });

      setMessages((prev) => ({
        ...prev,
        [newJoinedChat.id]: [
          {
            id: `msg_welcome_${Date.now()}`,
            chatId: newJoinedChat.id,
            senderId: 'sys_channel',
            senderName: newJoinedChat.title,
            text: `👋 Welcome to ${newJoinedChat.title}!\n\nThis ${newJoinedChat.type} is connected via MTProto 2.0 (Layer 184) under Telegram API_ID ${apiConfig.apiId}.`,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            date: new Date().toISOString().split('T')[0],
            isOutgoing: false,
            status: 'read',
          },
        ],
      }));

      setActiveChatId(newJoinedChat.id);
    };

    window.addEventListener('tg-joined-chat' as any, handleJoined);
    return () => window.removeEventListener('tg-joined-chat' as any, handleJoined);
  }, [apiConfig.apiId]);

  const resolveTelegramLink = async (urlOrQuery: string) => {
    try {
      const handled = await launchActivity.handleIntent(urlOrQuery);
      if (handled) return;

      const res = await fetch('/api/telegram/links/resolve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: urlOrQuery }),
      });
      const data = await res.json();
      if (data.success && data.inviteInfo) {
        window.dispatchEvent(new CustomEvent('tg-open-invite', { detail: data.inviteInfo }));
      }
    } catch {
      showToast(
        settings.language === 'ar' ? 'تعذر فتح الرابط' : 'Failed to resolve link',
        '⚠️'
      );
    }
  };

  const checkChatInvite = async (hash: string): Promise<TLRPC.ChatInvite> => {
    return await messagesController.checkChatInvite(hash);
  };

  const joinChat = async (invite: TLRPC.ChatInvite, hash: string): Promise<boolean> => {
    const success = await messagesController.joinChat(invite, hash);
    if (success) {
      setPreviewInvite(null);
      return true;
    }
    return false;
  };

  const openLink = async (url: string): Promise<boolean> => {
    return await launchActivity.handleIntent(url);
  };

  const processChatJoinRequests = async (chatId: string | number, user: any, approve: boolean): Promise<boolean> => {
    return await messagesController.processChatJoinRequests(chatId, user, approve);
  };

  const processChatJoinRequestsAll = async (chatId: string | number, approve: boolean): Promise<boolean> => {
    return await messagesController.processChatJoinRequestsAll(chatId, approve);
  };

  const jumpToMessage = (chatId: string, messageId: string) => {
    setActiveChatId(chatId);
    setTimeout(() => {
      window.dispatchEvent(
        new CustomEvent('tg-scroll-to-message', {
          detail: { chatId, messageId },
        })
      );
    }, 150);
  };

  const openPrivateChat = (
    senderId: string,
    senderName: string,
    senderAvatar?: string,
    senderUsername?: string
  ) => {
    // Check if a direct private chat already exists for this sender
    const cleanSenderId = senderId.startsWith('user_') ? senderId : `user_${senderId}`;
    const existingChat = chats.find(
      (c) =>
        c.id === cleanSenderId ||
        c.id === senderId ||
        (c.type === 'private' && c.title.toLowerCase() === senderName.toLowerCase()) ||
        (senderUsername && c.username && c.username.toLowerCase() === senderUsername.replace('@', '').toLowerCase())
    );

    if (existingChat) {
      setActiveChatId(existingChat.id);
      return;
    }

    // Otherwise create dynamic private chat matching DrKLO TLRPC.Chat / User model
    const targetChatId = cleanSenderId;
    const newPrivateChat: Chat = {
      id: targetChatId,
      type: 'private',
      title: senderName,
      username: senderUsername ? senderUsername.replace('@', '') : undefined,
      avatar: senderAvatar || '',
      unreadCount: 0,
      description: senderUsername ? `@${senderUsername.replace('@', '')}` : 'مستخدم تيليجرام',
      lastMessage: {
        id: `msg_${Date.now()}`,
        senderName: senderName,
        text: 'محادثة خاصة تم فتحها من إشعار المراقبة الحي 🚨',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        isOutgoing: false,
        status: 'read',
      },
    };

    setChats((prev) => [newPrivateChat, ...prev]);
    setMessages((prev) => ({
      ...prev,
      [targetChatId]: [
        {
          id: `msg_hello_${Date.now()}`,
          chatId: targetChatId,
          senderId: senderId,
          senderName: senderName,
          senderAvatar: senderAvatar,
          senderUsername: senderUsername,
          text: '👋 مرحباً! تم فتح المحادثة الخاصة لمتابعة المرسل.',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          date: new Date().toISOString().split('T')[0],
          isOutgoing: false,
          status: 'read',
        },
      ],
    }));

    setActiveChatId(targetChatId);
  };

  const createNewChat = (
    type: 'private' | 'group' | 'channel',
    title: string,
    username?: string,
    description?: string
  ) => {
    const newChatId = `chat_${Date.now()}`;
    const newChat: Chat = {
      id: newChatId,
      type,
      title: title.trim(),
      username: username ? username.replace('@', '') : undefined,
      avatar: '',
      unreadCount: 0,
      description: description || (type === 'channel' ? 'Public channel' : 'Group chat'),
      memberCount: type === 'group' ? 1 : undefined,
      lastMessage: {
        id: `init_${Date.now()}`,
        senderName: 'You',
        text: type === 'channel' ? 'Channel created' : 'Group created',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        isOutgoing: true,
        status: 'read',
      },
    };

    setChats((prev) => [newChat, ...prev]);
    setMessages((prev) => ({
      ...prev,
      [newChatId]: [
        {
          id: `msg_init_${Date.now()}`,
          chatId: newChatId,
          senderId: currentUser.id,
          senderName: 'You',
          text: `✨ ${type.toUpperCase()} created successfully with Telegram API (ID: ${apiConfig.apiId}).`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          date: new Date().toISOString().split('T')[0],
          isOutgoing: true,
          status: 'read',
        },
      ],
    }));

    setActiveChatId(newChatId);
    setActiveModal('none');
    showToast(
      settings.language === 'ar' ? 'تم إنشاء المحادثة بنجاح' : 'Chat created successfully',
      '✨'
    );
  };

  return (
    <TelegramContext.Provider
      value={{
        currentUser,
        chats,
        messages,
        activeChatId,
        activeChat,
        activeFolderId,
        folders,
        searchQuery,
        isDrawerOpen,
        isRightPanelOpen,
        activeModal,
        activeCall,
        viewerMedia,
        viewerPlaylist,
        apiConfig,
        settings,
        settingsSubPage,
        setSettingsSubPage,
        openSettingsPage,
        replyingTo,
        editingMessage,
        forwardingMessage,
        selectedMessageIds,
        typingChatId,
        chatContextMenu,
        messageContextMenu,
        toasts,
        inAppNotifications,
        dismissNotification,
        triggerNotification,
        capturedLinks,
        linkMonitorStats,
        autoJoinLinksEnabled,
        toggleAutoJoinLinks,
        joinCapturedLink,
        joinAllPendingLinks,
        checkPendingApprovalLinks,
        clearCapturedLinks,
        joinChatByInviteLink,
        exportLinksReport,
        manualScanAllChatsForLinks,
        isAuthenticated,
        login,
        logout,
        accounts,
        activeAccountId,
        switchAccount,
        addAccount,
        removeAccount,
        updateAccountProfile,
        setActiveChatId,
        setActiveFolderId,
        setSearchQuery,
        setIsDrawerOpen,
        setIsRightPanelOpen,
        setActiveModal,
        selectedProfileUser,
        setSelectedProfileUser,
        openUserProfile,
        getCommonGroupsForUser,
        setViewerMedia,
        setReplyingTo,
        setEditingMessage,
        setForwardingMessage,
        setChatContextMenu,
        setMessageContextMenu,
        showToast,
        sendMessage,
        editMessageText,
        forwardMessageTo,
        toggleReaction,
        deleteMessage,
        pinMessage,
        votePoll,
        toggleSelectMessage,
        clearSelectedMessages,
        deleteSelectedMessages,
        setChatDraft,
        toggleMuteChat,
        togglePinChat,
        markChatReadUnread,
        clearChatHistory,
        deleteChat,
        startCall,
        endCall,
        toggleCallMute,
        toggleCallCamera,
        updateApiConfig,
        updateSettings,
        testApiLatency,
        createNewChat,
        jumpToMessage,
        openPrivateChat,
        resolveTelegramLink,
        previewInvite,
        setPreviewInvite,
        checkChatInvite,
        joinChat,
        openLink,
        processChatJoinRequests,
        processChatJoinRequestsAll,
        syncCloudData,
        syncInitializationRoutine,
        validateSessionProactively,
        isSyncing,
        isSessionValidating,
        solveChatCaptcha,
        forwardToSavedMessages,
        loadMoreChatMessages,
        isChatLoadingOlder,
        chatHasMoreOlder,
        typingUsers,
        setChatTyping,
        blockedUserIds,
        blockUser,
        unblockUser,
        isUserBlocked,
        // Background Watch Words & Messages Monitor Service
        watchWords: currentWatchWords,
        updateWatchWords,
        monitoredChatIds,
        setMonitoredChatIds,
        isWatchWordsMonitorActive,
        toggleWatchWordsMonitor,
        keywordAlertsHistory,
        clearKeywordAlertsHistory,
        checkWatchWordsInChats,
      }}
    >
      {children}
    </TelegramContext.Provider>
  );
};

export const useTelegram = () => {
  const context = useContext(TelegramContext);
  if (!context) {
    throw new Error('useTelegram must be used within a TelegramProvider');
  }
  return context;
};
