/**
 * Types definition for the Telegram Broadcast & Monitoring Automation System
 */

export type DispatchType = 'manual' | 'scheduled' | 'sequential';

export type ProtectionMode = 'off' | 'skip' | 'smart' | 'convert_links' | 'salam';

export interface AutomationConfig {
  userId: string;
  messageText: string;
  groups: string[];
  images: string[]; // Base64 data URLs or temp paths
  dispatchType: DispatchType;
  intervalMinutes: number;
  totalHours: number; // 0 = unlimited
  protectionMode: ProtectionMode;
  requiredMemberMessages: number; // For 'salam' mode
  sendToAllGroups: boolean;
  sequentialMessages: string[];
  keywords: string[];
  advancedJoinLinks: string[];
  isMonitoring: boolean;
  isDispatching: boolean;
  lastDispatchedAt: number;
  startedAt: number;
  currentSequentialIndex: number;
}

export interface PreCheckItem {
  rawInput: string;
  normalizedPeer: string;
  title: string;
  isMember: boolean;
  isChannel: boolean;
  isProtected: boolean;
  protectionBotName?: string;
  chosenMode: ProtectionMode;
  status: 'valid' | 'invalid' | 'not_member' | 'protected';
  error?: string;
}

export interface BatchReport {
  batchId: string;
  userId: string;
  timestamp: string;
  totalGroups: number;
  successCount: number;
  failCount: number;
  skippedCount: number;
  details: Array<{
    target: string;
    title: string;
    status: 'success' | 'failed' | 'skipped';
    modeApplied: ProtectionMode;
    note?: string;
  }>;
}

export interface KeywordAlert {
  id: string;
  userId: string;
  keyword: string;
  chatTitle: string;
  chatId: string;
  senderName: string;
  senderUsername?: string;
  senderId: string;
  timestamp: string;
  text: string;
}

export interface JoinProgress {
  total: number;
  joined: number;
  skipped: number;
  failed: number;
  status: 'idle' | 'running' | 'paused' | 'stopped' | 'completed';
  currentLink?: string;
  logs: string[];
}

export interface AutoReplyRule {
  id: string;
  keyword: string;
  replyText: string;
  matchType: 'contains' | 'exact' | 'regex';
  scope: 'all' | 'private' | 'groups';
  isEnabled: boolean;
  timesTriggered?: number;
  createdAt?: string;
  lastUsed?: string;
}
