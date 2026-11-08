export type ChatType = 'private' | 'group' | 'channel' | 'bot' | 'saved';

export interface User {
  id: string;
  name: string;
  first_name?: string;
  last_name?: string;
  username?: string;
  phone?: string;
  avatar: string;
  isOnline: boolean;
  lastSeen?: string;
  bio?: string;
  isVerified?: boolean;
  isBot?: boolean;
  isPremium?: boolean;
  premiumBadges?: string[];
  sessionString?: string;
}

export interface ProfileUserInfo {
  id: string;
  name: string;
  username?: string;
  phone?: string;
  avatar?: string;
  bio?: string;
  isVerified?: boolean;
  isBot?: boolean;
  isOnline?: boolean;
  lastSeen?: string;
  isPremium?: boolean;
  isBlocked?: boolean;
  isContact?: boolean;
  isMuted?: boolean;
  sourceChatId?: string;
  sourceChatTitle?: string;
  senderRole?: 'owner' | 'admin' | 'member' | 'banned' | 'restricted';
  senderRank?: string;
}

export interface TypingUser {
  userId: string;
  userName: string;
  action?: 'typing' | 'record_audio' | 'upload_photo' | 'upload_document';
  timestamp: number;
}

export interface Story {
  id: string;
  userId: string;
  userName: string;
  userAvatar: string;
  mediaUrl: string;
  mediaType: 'image' | 'video';
  caption?: string;
  timestamp: string;
  expiresAt: number;
  viewsCount: number;
  isViewed: boolean;
  isMyStory?: boolean;
}

export interface Reaction {
  emoji: string;
  count: number;
  users: string[]; // user IDs who reacted
  isLottie?: boolean;
}

export interface ReplyInfo {
  messageId: string;
  senderName: string;
  textSnippet: string;
  mediaType?: 'photo' | 'audio' | 'document' | 'video';
}

export interface ForwardInfo {
  fromChatName: string;
  fromChatId?: string;
  originalDate?: string;
}

export interface MessageMedia {
  type: 'photo' | 'video' | 'audio' | 'voice' | 'document' | 'sticker' | 'poll' | 'video_note';
  url?: string;
  fileName?: string;
  fileSize?: string;
  duration?: number; // for audio/voice/video in seconds
  waveform?: number[]; // waveform amplitudes (0..100)
  aspectRatio?: number;
  thumbnailUrl?: string;
  width?: number;
  height?: number;
  isLottie?: boolean;
  lottieData?: any;
  stickerId?: string;
  packName?: string;
  pollData?: {
    question: string;
    options: { id: string; text: string; votes: number; voters: string[] }[];
    totalVotes: number;
    isClosed?: boolean;
    isMultipleAnswers?: boolean;
  };
}

export interface ViewerMediaItem {
  url: string;
  type?: 'photo' | 'video' | 'gif' | 'video_note';
  title?: string;
  caption?: string;
  sender?: string;
  senderAvatar?: string;
  timestamp?: string;
  duration?: number;
  fileName?: string;
  fileSize?: string;
  messageId?: string;
  chatId?: string;
  aspectRatio?: number;
  thumbnailUrl?: string;
  width?: number;
  height?: number;
}

export interface LinkPreviewData {
  url: string;
  displayUrl: string;
  siteName?: string;
  title: string;
  description?: string;
  image?: string;
  type?: 'telegram_channel' | 'telegram_message' | 'telegram_invite' | 'article' | 'video' | 'website';
  channelUsername?: string;
  memberCount?: number;
}

export interface MessageEntity {
  type:
    | 'messageEntityUrl'
    | 'messageEntityTextUrl'
    | 'messageEntityMention'
    | 'messageEntityHashtag'
    | 'messageEntityBotCommand'
    | 'messageEntityBold'
    | 'messageEntityItalic'
    | 'messageEntityCode'
    | 'messageEntityPre'
    | 'messageEntityStrike'
    | 'messageEntityUnderline'
    | 'messageEntitySpoiler'
    | 'messageEntityCustomEmoji'
    | 'messageEntityBankCard'
    | 'messageEntityPhone'
    | 'messageEntityEmail';
  offset: number; // UTF-16 code units offset
  length: number; // UTF-16 code units length
  url?: string; // For messageEntityTextUrl
  customEmojiId?: string; // For messageEntityCustomEmoji
  language?: string; // For messageEntityPre
}

export interface InlineKeyboardButton {
  text: string;
  url?: string;
  callback_data?: string;
  style?: 'primary' | 'danger' | 'success' | 'default';
  icon_custom_emoji_id?: string;
}

export interface InlineKeyboardMarkup {
  inline_keyboard: InlineKeyboardButton[][];
}

export interface KeyboardButton {
  text: string;
  request_contact?: boolean;
  request_location?: boolean;
}

export interface ReplyKeyboardMarkup {
  keyboard: KeyboardButton[][];
  resize_keyboard?: boolean;
  one_time_keyboard?: boolean;
}

export interface ReplyKeyboardRemove {
  remove_keyboard: true;
}

export interface ForceReply {
  force_reply: true;
}

export type ReplyMarkup =
  | InlineKeyboardMarkup
  | ReplyKeyboardMarkup
  | ReplyKeyboardRemove
  | ForceReply;

// Official Telegram Bot Commands & Scope Architecture
export interface BotCommand {
  command: string; // 1-32 lowercase characters [a-z0-9_]
  description: string; // 1-256 characters description
}

export type BotCommandScopeType =
  | 'default'
  | 'all_private_chats'
  | 'all_group_chats'
  | 'all_chat_administrators'
  | 'chat'
  | 'chat_administrators'
  | 'chat_member';

export interface BotCommandScope {
  type: BotCommandScopeType;
  chat_id?: string | number;
  user_id?: string | number;
}

export interface BotCommandEntry {
  scope: BotCommandScope;
  commands: BotCommand[];
}

export interface BotEntity {
  id: string;
  name: string;
  username: string;
  avatar?: string;
  token?: string;
  is_bot: true;
  flags: {
    bot: true; // MTProto user flags.14
    bot_chat_history: boolean; // flags.15: can_read_all_group_messages
    bot_nochats: boolean; // flags.16: cannot be added to groups
    bot_inline_geo?: boolean; // flags.21: inline mode asks for location
    bot_info_version?: number;
    bot_inline_placeholder?: string;
  };
  privacyMode: boolean; // default: true (Privacy Mode ON)
  can_read_all_group_messages: boolean;
  canReadAllGroupMessages?: boolean;
  can_join_groups: boolean;
  supports_inline_queries: boolean;
  inline_placeholder?: string;
  commandsByScope: BotCommandEntry[];
}

export interface InlineQueryResult {
  id: string;
  type: 'article' | 'photo' | 'gif' | 'video';
  title: string;
  description?: string;
  thumb_url?: string;
  input_message_content: {
    message_text: string;
    parse_mode?: 'HTML' | 'MarkdownV2';
  };
  reply_markup?: ReplyMarkup;
}

export interface Message {
  id: string;
  chatId: string;
  senderId: string;
  senderName?: string;
  senderAvatar?: string;
  senderUsername?: string;
  senderRole?: 'owner' | 'admin' | 'member' | 'restricted' | 'banned';
  senderRank?: string;
  text: string;
  timestamp: string; // e.g. "10:42 AM"
  date: string; // e.g. "2026-08-19"
  isOutgoing: boolean;
  status: 'sending' | 'sent' | 'delivered' | 'read' | 'error';
  media?: MessageMedia;
  replyTo?: ReplyInfo;
  forwardedFrom?: ForwardInfo;
  reactions?: Reaction[];
  isPinned?: boolean;
  isEdited?: boolean;
  views?: number;
  linkPreview?: LinkPreviewData;
  isSecret?: boolean;
  ttlSeconds?: number;
  expiresAt?: number;
  isScheduled?: boolean;
  scheduledDate?: string;
  rawDate?: number;
  epoch?: number;
  entities?: MessageEntity[];
  replyMarkup?: ReplyMarkup;
}

export interface Chat {
  id: string;
  accountNum?: number;
  type: ChatType;
  title: string;
  name?: string;
  inviteHash?: string;
  username?: string;
  avatar: string;
  bio?: string;
  isOnline?: boolean;
  isVerified?: boolean;
  isMuted?: boolean;
  isPinned?: boolean;
  pinnedIndex?: number;
  isArchived?: boolean;
  adminOnly?: boolean;
  unreadCount: number;
  isMember?: boolean;
  pinnedMessageId?: string;
  lastMessage?: {
    id: string;
    senderName?: string;
    text: string;
    timestamp: string;
    isOutgoing: boolean;
    status?: 'sending' | 'sent' | 'delivered' | 'read';
    mediaType?: string;
  };
  memberCount?: number;
  onlineCount?: number;
  description?: string;
  inviteLink?: string;
  folderIds?: string[];
  customWallpaper?: string;
  draft?: string;
  draftTimestamp?: string;
  isRestricted?: boolean;
  restrictionReason?: string;
  requiresCaptcha?: boolean;
  captchaQuestion?: string;
  captchaAnswer?: string;
  captchaOptions?: string[];
  isCaptchaSolved?: boolean;
  isReadOnly?: boolean;
  slowModeSeconds?: number;
  botPrivacyDisabled?: boolean;
  // Authentic Telegram MTProto flags
  isBroadcast?: boolean;
  broadcast?: boolean;
  isMegagroup?: boolean;
  megagroup?: boolean;
  isCreator?: boolean;
  creator?: boolean;
  left?: boolean;
  adminRights?: any;
  admin_rights?: any;
  defaultBannedRights?: any;
  default_banned_rights?: any;
  bannedRights?: any;
  banned_rights?: any;
  linked_chat_id?: string | number;
  canSendMessages?: boolean;
  // Secret Chat Specifics
  isSecret?: boolean;
  ttlSeconds?: number;
  secretFingerprint?: string;
}

export interface Folder {
  id: string;
  name: string;
  nameAr: string;
  icon: string;
  chatTypes?: ChatType[];
  includedChatIds?: string[];
  unreadCount?: number;
}

export interface TelegramApiConfig {
  apiId: string;
  apiHash: string;
  dcId: number;
  dcIp: string;
  port: number;
  connectionStatus: 'connected' | 'connecting' | 'disconnected';
  sessionString: string;
  mtprotoVersion: string;
  pingMs: number;
}

export type SettingsSubPage =
  | 'main'
  | 'account'
  | 'plus_settings'
  | 'theme_coloring'
  | 'chat_settings'
  | 'privacy_security'
  | 'privacy_control'
  | 'two_step_verification'
  | 'passcode_lock'
  | 'auto_delete'
  | 'sessions'
  | 'blocked_users'
  | 'notifications_sounds'
  | 'data_storage'
  | 'folders'
  | 'devices'
  | 'power_saving'
  | 'language'
  | 'themes_browser'
  | 'faq'
  | 'features'
  | 'apk_installer'
  | 'support_group'
  | 'stories'
  | 'messages'
  | 'topics'
  | 'shared_media'
  | 'ads_settings'
  | 'backup_restore'
  | 'premium'
  | 'plus_general'
  | 'plus_chats'
  | 'plus_drawer'
  | 'plus_profile'
  | 'plus_downloads';

export interface AppSettings {
  theme: 'dark' | 'light' | 'night' | 'day';
  accentColor: string;
  fontSize: number; // 12 .. 30
  language: 'ar' | 'en';
  sendByEnter: boolean;
  soundEffects: boolean;
  autoDownloadMedia: boolean;
  chatWallpaper: string;
  bubbleCornerRadius?: number;
  chatListViewMode?: 'two_lines' | 'three_lines';
  appIcon?: string;
  autoNightMode?: boolean;
  inAppBrowser?: boolean;
  powerSavingThreshold?: number;
  enableAnimations?: boolean;
  swipeAction?: string;
  showTranslateButton?: boolean;
  inAppSounds?: boolean;
  inAppVibrate?: boolean;
  inAppPreview?: boolean;
  inChatSounds?: boolean;
  inAppPop?: boolean;
  autoDownloadMobile?: boolean;
  autoDownloadWifi?: boolean;
  autoDownloadRoaming?: boolean;
  streamingEnabled?: boolean;
  callDataSaving?: string;
  plusThemeEnabled?: boolean;
  useSQLiteMMAP?: boolean;
  biometricLock?: boolean;
  watch_words?: string[];
  watchWords?: string[];
  monitoredChatIds?: string[];
  monitoringIntervalSeconds?: number;
  monitoringEnabled?: boolean;
}

export interface KeywordAlertItem {
  id: string;
  keyword: string;
  chatId: string;
  chatTitle: string;
  messageId: string;
  messageText: string;
  senderName: string;
  timestamp: number;
}

export interface ActiveCall {
  chatId: string;
  chatTitle: string;
  chatAvatar: string;
  isVideo: boolean;
  isMuted: boolean;
  isCameraOff: boolean;
  isScreenSharing?: boolean;
  isNoiseSuppressed?: boolean;
  duration: number;
  status: 'calling' | 'connected' | 'ended';
  encryptionEmojis: [string, string, string, string];
  audioLevel?: number;
}

export interface ToastItem {
  id: string;
  text: string;
  icon?: string;
}

export interface ChatContextMenu {
  chatId: string;
  x: number;
  y: number;
}

export interface MessageContextMenu {
  message: Message;
  x: number;
  y: number;
}

export type NotificationCategory =
  | 'message'
  | 'channel_post'
  | 'mention'
  | 'reply'
  | 'call'
  | 'system_security'
  | 'reaction'
  | 'pinned'
  | 'keyword_alert';

export interface InAppNotification {
  id: string;
  category: NotificationCategory;
  title: string;
  body: string;
  avatar?: string;
  chatId?: string;
  chatTitle?: string;
  chatUsername?: string;
  messageId?: string;
  senderId?: string;
  senderName?: string;
  senderUsername?: string;
  timestamp: string;
  isSilent?: boolean;
  isPinned?: boolean;
  replyAction?: boolean;
  keyword?: string;
  messageText?: string;
}

export interface UserAccount {
  id: string;
  user: User;
  settings: AppSettings;
  chats: Chat[];
  messages: Record<string, Message[]>;
  unreadCount?: number;
  isActive?: boolean;
  sessionString?: string;
  phone?: string;
}

export type LinkCategory = 'whatsapp' | 'telegram_public' | 'telegram_private' | 'other';
export type JoinStatusType = 'joined' | 'pending_admin' | 'already_joined' | 'error_missing_info' | 'not_applicable' | 'pending_scan' | 'failed';

export interface CapturedLink {
  id: string;
  url: string;
  sourceChatId?: string;
  source_chat_id?: string;
  sourceChatTitle?: string;
  source_chat?: string;
  source_link?: string;
  sourceSenderName?: string;
  sender?: string;
  detectedAt?: string;
  detected_at?: string;
  type?: 'telegram_channel' | 'telegram_group' | 'telegram_invite' | 'whatsapp' | 'external';
  linkCategory?: LinkCategory;
  joinStatus?: JoinStatusType;
  joinStatusDetails?: string;
  joinTime?: string;
  isJoinedActual?: boolean;
  isPendingApproval?: boolean;
  extractedTitle?: string;
  chat_title?: string;
  memberCount?: number;
  joined: boolean;
  joinedAt?: string;
  autoJoined?: boolean;
  status: 'valid' | 'invalid' | 'joined' | 'already' | 'pending' | 'failed' | 'joining' | 'already_member' | 'expired' | 'admin_approval_pending' | 'whatsapp_saved' | 'private_channel_saved';
  status_text?: string;
  join_status?: string;
  username?: string;
  creation_date?: string;
  country?: string;
  rawText?: string;
}

export interface LinkMonitorStats {
  whatsappCount: number;
  telegramPublicJoined: number;
  telegramPublicPendingAdmin: number;
  telegramPublicOther: number;
  telegramPrivateCount: number;
  totalLinksCount: number;
}

// 1. Sender & Scheduler Types
export type ProtectionMode = 'salam' | 'skip' | 'smart_clean' | 'permanent_clean' | 'disabled';

export interface SenderBatch {
  id: string;
  text: string;
  images: string[];
  targetChats: { id: string; title: string; type: ChatType; status: 'sent' | 'failed' | 'skipped' | 'protected'; messageId?: string; error?: string }[];
  protectionMode: ProtectionMode;
  isScheduled: boolean;
  intervalMinutes?: number;
  durationHours?: number;
  createdAt: string;
  sentAt: string;
  totalSuccess: number;
  totalFailed: number;
  status: 'completed' | 'running' | 'paused' | 'stopped';
}

// 2. Monitor Types
export interface MonitorConfig {
  isEnabled: boolean;
  keywords: string[];
  sendAlertsToSavedMessages: boolean;
  browserPushAlerts: boolean;
  intervalMinutes?: number;
  durationHours?: number;
  startedAt?: string;
}

export interface MonitorAlert {
  id: string;
  keyword: string;
  sourceChatId: string;
  sourceChatTitle: string;
  senderName: string;
  messageText: string;
  timestamp: string;
}

// 3. My Messages (Batch Log)
export interface MyMessagesBatch {
  id: string;
  text: string;
  hasImages: boolean;
  imagesCount: number;
  groupsCount: number;
  targets: { chatId: string; chatTitle: string; messageId: string }[];
  date: string;
  timestamp: string;
}

// 4. Auto Joiner Advanced
export interface AutoJoinerTask {
  id: string;
  url: string;
  type: 'public' | 'private' | 'username';
  extractedFromText?: string;
  status: 'pending' | 'joining' | 'joined' | 'already_member' | 'invalid' | 'banned' | 'rate_limited';
  errorReason?: string;
  processedAt?: string;
}

// 5. Auto Responder
export interface AutoReplyRule {
  id: string;
  keyword: string;
  replyText: string;
  matchType: 'exact' | 'contains' | 'regex';
  scope: 'all' | 'private' | 'groups';
  isEnabled: boolean;
  timesTriggered: number;
  lastTriggeredAt?: string;
}

// 6. Smart AI Learn (Groq LLM)
export interface SmartAiService {
  id: string;
  name: string;
  description: string;
  keywords: string[];
}

export interface SmartAiPattern {
  id: string;
  triggerContext: string;
  recommendedReply: string;
  learnedDate: string;
  isAccepted: boolean;
}

// 7. Live Link Discover & Instant Auto-Join
export interface LiveDiscoveredLink {
  id: string;
  url: string;
  sourceChatTitle: string;
  sourceChatId: string;
  senderName: string;
  timestamp: string;
  status: 'pending' | 'joining' | 'joined' | 'failed' | 'already_member' | 'expired';
  failReason?: string;
  autoJoined: boolean;
}

// 8. Protocol Buffers & Diagnostics Types
export { GoogleProtobuf } from './core/ProtobufCodec';

