import React, { useState, useEffect } from 'react';
import {
  ShieldCheck,
  Users,
  Lock,
  Clock,
  UserX,
  UserCheck,
  Sparkles,
  X,
  Check,
  AlertTriangle,
  Crown,
  Ban,
  Sliders,
  MessageSquare,
  Image,
  Smile,
  Link,
  Pin,
  VolumeX,
  Bot,
  Globe,
  CheckCircle2,
  XCircle,
  HelpCircle,
  Loader2,
  RefreshCw,
  Send,
} from 'lucide-react';
import { useTelegram } from '../../context/TelegramContext';
import { messagesController, ChatParticipantInfo } from '../../core/MessagesController';
import { TLRPC } from '../../core/TLRPC';
import { TelegramBotEngine, OFFICIAL_TELEGRAM_BOTS } from '../../core/TelegramBotEngine';

export const GroupAdminModal: React.FC = () => {
  const { activeModal, setActiveModal, activeChat, showToast } = useTelegram();
  const [participants, setParticipants] = useState<ChatParticipantInfo[]>([]);
  const [selectedUser, setSelectedUser] = useState<ChatParticipantInfo | null>(null);
  const [adminOnlyPosting, setAdminOnlyPosting] = useState<boolean>(false);
  const [slowmodeSeconds, setSlowmodeSeconds] = useState<number>(0);
  const [activeTab, setActiveTab] = useState<'members' | 'permissions' | 'bots' | 'slowmode'>('permissions');

  // Bot Privacy Mode State
  const [disablePrivacyMode, setDisablePrivacyMode] = useState<boolean>(false);
  const [isUpdatingPrivacy, setIsUpdatingPrivacy] = useState<boolean>(false);
  const [selectedBotUsername, setSelectedBotUsername] = useState<string>('all');
  const [testMessage, setTestMessage] = useState<string>('مرحباً بالجميع في المجموعة');
  const [testResult, setTestResult] = useState<{ canReceive: boolean; reason: string } | null>(null);

  useEffect(() => {
    if (activeChat && activeModal === ('group-admin' as any)) {
      const initialDisabled = activeChat.botPrivacyDisabled ?? messagesController.isGroupBotPrivacyDisabled(activeChat.id);
      setDisablePrivacyMode(initialDisabled);
      setParticipants(messagesController.getParticipants(activeChat.id));
      setAdminOnlyPosting(messagesController.isAdminOnlyPosting(activeChat.id));

      // Query the official Telegram API for real-time group privacy state
      fetch(`/api/telegram/bot/group-privacy-mode?chatId=${encodeURIComponent(activeChat.id)}`)
        .then((res) => res.json())
        .then((data) => {
          if (data && typeof data.privacyModeDisabled === 'boolean') {
            setDisablePrivacyMode(data.privacyModeDisabled);
            activeChat.botPrivacyDisabled = data.privacyModeDisabled;
            messagesController.setGroupBotPrivacyDisabled(activeChat.id, data.privacyModeDisabled);
          }
        })
        .catch((err) => console.warn('Could not sync Telegram Group Privacy Mode:', err));
    }
  }, [activeChat, activeModal]);

  if (activeModal !== ('group-admin' as any) || !activeChat) return null;

  const handleToggleAdminOnly = (enabled: boolean) => {
    setAdminOnlyPosting(enabled);
    messagesController.setAdminOnlyPosting(activeChat.id, enabled);
    showToast(
      enabled
        ? 'تم تفعيل وضع "المشرفون فقط يكتبون" في المجموعة 🔒'
        : 'تم السماح لجميع الأعضاء بالكتابة في المجموعة 💬',
      '🛡️'
    );
  };

  const handleSetSlowMode = (seconds: number) => {
    setSlowmodeSeconds(seconds);
    messagesController.setSlowMode(activeChat.id, seconds);
    showToast(
      seconds > 0
        ? `تم تفعيل الوضع البطيء: ${seconds} ثانية بين كل رسالة ⏳`
        : 'تم إيقاف الوضع البطيء',
      '⏱️'
    );
  };

  /**
   * Official Telegram API Call: Toggle Group Bot Privacy Mode
   * When Privacy Mode is DISABLED:
   * - Sets can_read_all_group_messages = true
   * - Sets bot_chat_history = true (flags.15)
   * - Grants bot access to read and receive ALL messages in this group
   */
  const handleTogglePrivacyMode = async (disable: boolean) => {
    setIsUpdatingPrivacy(true);
    try {
      const result = await TelegramBotEngine.toggleGroupPrivacyApi(
        activeChat.id,
        disable,
        selectedBotUsername === 'all' ? undefined : selectedBotUsername
      );

      setDisablePrivacyMode(disable);
      activeChat.botPrivacyDisabled = disable;
      messagesController.setGroupBotPrivacyDisabled(activeChat.id, disable);

      // Update in-memory participant list with updated bot permissions
      const currentParticipants = messagesController.getParticipants(activeChat.id);
      const updated = currentParticipants.map((p) => {
        if (p.is_bot || p.username?.toLowerCase().endsWith('bot')) {
          return {
            ...p,
            bot_chat_history: disable,
            canReadAllGroupMessages: disable,
          };
        }
        return p;
      });
      setParticipants(updated);

      // Re-run test message if populated
      if (testMessage) {
        runPrivacyTest(testMessage, disable);
      }

      showToast(
        disable
          ? 'تم استدعاء Telegram API: تم تعطيل وضع الخصوصية وتحديث الصلاحيات لتلقي جميع رسائل المجموعة 🌐'
          : 'تم استدعاء Telegram API: تم تفعيل وضع الخصوصية (البوتات تستقبل الأوامر والردود فقط) 🔒',
        disable ? '🌐' : '🔒'
      );
    } catch (err) {
      console.error('Failed to update group privacy mode:', err);
      showToast('فشل تحديث وضع الخصوصية عبر Telegram API', '⚠️');
    } finally {
      setIsUpdatingPrivacy(false);
    }
  };

  const runPrivacyTest = (msg: string, isPrivacyDisabled = disablePrivacyMode) => {
    const mockBot = OFFICIAL_TELEGRAM_BOTS['telegramaibot'];
    const dummyChat = { ...activeChat, botPrivacyDisabled: isPrivacyDisabled };
    const res = TelegramBotEngine.shouldBotReceiveGroupMessage(
      mockBot,
      msg,
      undefined,
      false,
      dummyChat
    );
    setTestResult(res);
  };

  const handlePromoteToAdmin = async (user: ChatParticipantInfo) => {
    await messagesController.editAdminRights(activeChat.id, user.userId, TLRPC.DEFAULT_ADMIN_RIGHTS);
    setParticipants([...messagesController.getParticipants(activeChat.id)]);
    showToast(`تمت ترقية "${user.name}" إلى مشرف بنجاح ⭐`, '👑');
  };

  const handleRestrictUser = async (user: ChatParticipantInfo) => {
    await messagesController.editBannedRights(activeChat.id, user.userId, {
      ...TLRPC.DEFAULT_USER_BANNED_RIGHTS,
      send_messages: false,
      send_media: false,
      send_stickers: false,
    });
    setParticipants([...messagesController.getParticipants(activeChat.id)]);
    showToast(`تم تقييد صلاحيات "${user.name}" بنجاح 🚫`, '⚠️');
  };

  const handleBanUser = async (user: ChatParticipantInfo) => {
    await messagesController.editBannedRights(activeChat.id, user.userId, {
      ...TLRPC.DEFAULT_USER_BANNED_RIGHTS,
      view_messages: true,
      send_messages: false,
      send_media: false,
    });
    setParticipants([...messagesController.getParticipants(activeChat.id)]);
    showToast(`تم حظر "${user.name}" من المجموعة ❌`, '🚫');
  };

  const handleUnbanUser = async (user: ChatParticipantInfo) => {
    await messagesController.unbanUser(activeChat.id, user.userId);
    setParticipants([...messagesController.getParticipants(activeChat.id)]);
    showToast(`تم إلغاء القيود عن "${user.name}" بنجاح ✅`, '✨');
  };

  const botCount = participants.filter((p) => p.is_bot || p.username?.toLowerCase().endsWith('bot')).length;

  return (
    <div
      id="modal-group-admin"
      className="fixed inset-0 z-[9999] flex items-center justify-center p-3 sm:p-4 bg-black/85 backdrop-blur-md select-none"
      dir="rtl"
    >
      <div
        className="w-full max-w-lg text-[#e8eaf6] rounded-3xl shadow-2xl overflow-hidden border border-sky-500/30 my-auto animate-in zoom-in-95 duration-200"
        style={{
          background: 'linear-gradient(145deg, #111a2e, #17213b, #0c1220)',
        }}
      >
        {/* Header */}
        <div className="p-5 border-b border-white/10 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-sky-500/20 text-sky-400 flex items-center justify-center border border-sky-400/30">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-sm text-white">إدارة المجموعة والصلاحيات</h3>
              <p className="text-[11px] text-sky-300/80">{activeChat.title} (Telegram Bot API & TLRPC)</p>
            </div>
          </div>
          <button
            onClick={() => setActiveModal('none')}
            className="p-1.5 rounded-lg text-gray-400 hover:text-white hover:bg-white/10"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Tab Selector */}
        <div className="flex items-center border-b border-white/10 bg-black/20 text-xs font-semibold">
          <button
            onClick={() => setActiveTab('members')}
            className={`flex-1 py-3 border-b-2 text-center transition-colors flex items-center justify-center gap-1.5 ${
              activeTab === 'members'
                ? 'border-sky-400 text-sky-400'
                : 'border-transparent text-gray-400 hover:text-gray-200'
            }`}
          >
            <Users className="w-4 h-4" />
            <span>الأعضاء ({participants.length})</span>
          </button>

          <button
            onClick={() => setActiveTab('permissions')}
            className={`flex-1 py-3 border-b-2 text-center transition-colors flex items-center justify-center gap-1.5 ${
              activeTab === 'permissions'
                ? 'border-sky-400 text-sky-400'
                : 'border-transparent text-gray-400 hover:text-gray-200'
            }`}
          >
            <Lock className="w-4 h-4" />
            <span>الصلاحيات</span>
          </button>

          <button
            onClick={() => setActiveTab('bots')}
            className={`flex-1 py-3 border-b-2 text-center transition-colors flex items-center justify-center gap-1.5 relative ${
              activeTab === 'bots'
                ? 'border-emerald-400 text-emerald-400'
                : 'border-transparent text-gray-400 hover:text-gray-200'
            }`}
          >
            <Bot className="w-4 h-4" />
            <span>البوتات والخصوصية</span>
            {disablePrivacyMode && (
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            )}
          </button>

          <button
            onClick={() => setActiveTab('slowmode')}
            className={`flex-1 py-3 border-b-2 text-center transition-colors flex items-center justify-center gap-1.5 ${
              activeTab === 'slowmode'
                ? 'border-sky-400 text-sky-400'
                : 'border-transparent text-gray-400 hover:text-gray-200'
            }`}
          >
            <Clock className="w-4 h-4" />
            <span>الوضع البطيء</span>
          </button>
        </div>

        {/* Tab 1: Members List & Moderation */}
        {activeTab === 'members' && (
          <div className="p-4 max-h-[50vh] overflow-y-auto space-y-2.5">
            {participants.map((user) => {
              const isBot = user.is_bot || user.username?.toLowerCase().endsWith('bot');
              const hasMessageAccess = isBot
                ? disablePrivacyMode || user.role === 'admin' || user.role === 'creator'
                : true;

              return (
                <div
                  key={user.userId}
                  className="flex items-center justify-between p-3 rounded-2xl bg-black/30 border border-white/5 hover:border-white/15 transition-all"
                >
                  <div className="flex items-center gap-3">
                    <div className="relative">
                      {user.avatar ? (
                        <img
                          src={user.avatar}
                          alt={user.name}
                          className="w-10 h-10 rounded-full object-cover border border-white/20"
                        />
                      ) : (
                        <div className="w-10 h-10 rounded-full bg-[#5288c1] flex items-center justify-center text-white font-bold text-sm border border-white/20">
                          {user.name.charAt(0).toUpperCase()}
                        </div>
                      )}
                      {user.role === 'creator' && (
                        <span className="absolute -bottom-1 -right-1 p-0.5 rounded-full bg-amber-500 text-white shadow">
                          <Crown className="w-3 h-3" />
                        </span>
                      )}
                    </div>
                    <div>
                      <div className="flex items-center gap-1.5">
                        <span className="font-bold text-xs text-white">{user.name}</span>
                        {isBot && (
                          <span className="px-1.5 py-0.2 rounded text-[9px] bg-sky-500/20 text-sky-300 font-bold border border-sky-500/30 flex items-center gap-0.5">
                            <Bot className="w-2.5 h-2.5" />
                            بوت
                          </span>
                        )}
                        {user.role === 'creator' && (
                          <span className="px-1.5 py-0.2 rounded text-[9px] bg-amber-500/20 text-amber-300 font-bold border border-amber-500/30">
                            المالك
                          </span>
                        )}
                        {user.role === 'admin' && (
                          <span className="px-1.5 py-0.2 rounded text-[9px] bg-sky-500/20 text-sky-300 font-bold border border-sky-500/30">
                            مشرف
                          </span>
                        )}
                        {user.role === 'restricted' && (
                          <span className="px-1.5 py-0.2 rounded text-[9px] bg-rose-500/20 text-rose-300 font-bold border border-rose-500/30">
                            مقيد
                          </span>
                        )}
                      </div>
                      <div className="flex items-center gap-2 mt-0.5">
                        <span className="text-[10px] text-gray-400">@{user.username || 'user'}</span>
                        {isBot && (
                          <span
                            className={`text-[9px] font-semibold flex items-center gap-1 ${
                              hasMessageAccess ? 'text-emerald-400' : 'text-amber-400'
                            }`}
                          >
                            <span
                              className={`w-1.5 h-1.5 rounded-full ${
                                hasMessageAccess ? 'bg-emerald-400' : 'bg-amber-400'
                              }`}
                            />
                            {hasMessageAccess ? 'لديه حق الوصول إلى الرسائل' : 'ليس لديه وصول إلى الرسائل'}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>

                  {user.role !== 'creator' && (
                    <div className="flex items-center gap-1.5">
                      {user.role === 'member' && (
                        <button
                          onClick={() => handlePromoteToAdmin(user)}
                          className="p-1.5 rounded-xl bg-sky-500/20 hover:bg-sky-500/30 text-sky-300 text-[11px] font-bold transition-colors"
                          title="ترقية إلى مشرف"
                        >
                          <Crown className="w-3.5 h-3.5" />
                        </button>
                      )}
                      {user.role !== 'restricted' && user.role !== 'banned' ? (
                        <button
                          onClick={() => handleRestrictUser(user)}
                          className="p-1.5 rounded-xl bg-rose-500/20 hover:bg-rose-500/30 text-rose-300 text-[11px] font-bold transition-colors"
                          title="تقييد العضو"
                        >
                          <Ban className="w-3.5 h-3.5" />
                        </button>
                      ) : (
                        <button
                          onClick={() => handleUnbanUser(user)}
                          className="p-1.5 rounded-xl bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 text-[11px] font-bold transition-colors"
                          title="إلغاء القيود"
                        >
                          <UserCheck className="w-3.5 h-3.5" />
                        </button>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}

        {/* Tab 2: Group Permissions & Privacy Mode Toggle */}
        {activeTab === 'permissions' && (
          <div className="p-5 space-y-4 max-h-[50vh] overflow-y-auto">
            {/* 🌟 TELEGRAM OFFICIAL BOT PRIVACY MODE ADMIN TOGGLE 🌟 */}
            <div
              id="admin-privacy-mode-card"
              className={`p-4 rounded-2xl border transition-all duration-200 ${
                disablePrivacyMode
                  ? 'bg-emerald-950/30 border-emerald-500/40 shadow-lg shadow-emerald-950/20'
                  : 'bg-black/40 border-white/10'
              }`}
            >
              <div className="flex items-start justify-between gap-3">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="p-1 rounded-lg bg-emerald-500/20 text-emerald-400">
                      <Bot className="w-4 h-4" />
                    </span>
                    <h4 className="font-bold text-xs text-white">
                      تعطيل وضع الخصوصية للبوتات (Disable Privacy Mode)
                    </h4>
                  </div>
                  <p className="text-[11px] text-gray-300 leading-relaxed">
                    استدعاء Telegram Bot API للسماح للبوتات داخل هذه المجموعة بقراءة واستقبال كافة الرسائل
                    دون اشتراط البدء بعلامة (/) أو الإشارة إليها.
                  </p>
                  <div className="flex items-center gap-2 pt-1">
                    <span
                      className={`text-[10px] px-2 py-0.5 rounded-full font-bold flex items-center gap-1 border ${
                        disablePrivacyMode
                          ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                          : 'bg-amber-500/20 text-amber-300 border-amber-500/40'
                      }`}
                    >
                      {disablePrivacyMode ? (
                        <>
                          <CheckCircle2 className="w-3 h-3" />
                          وضع الخصوصية: معطّل (تلقي كافة الرسائل)
                        </>
                      ) : (
                        <>
                          <Lock className="w-3 h-3" />
                          وضع الخصوصية: مفعّل (أوامر وإشارات فقط)
                        </>
                      )}
                    </span>
                    <span className="text-[10px] text-gray-400">
                      MTProto: flags.15 (bot_chat_history)
                    </span>
                  </div>
                </div>

                <div className="flex flex-col items-end gap-1 shrink-0">
                  <button
                    id="tg-toggle-privacy-mode-btn"
                    disabled={isUpdatingPrivacy}
                    onClick={() => handleTogglePrivacyMode(!disablePrivacyMode)}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none ${
                      disablePrivacyMode ? 'bg-emerald-500' : 'bg-gray-700'
                    }`}
                  >
                    <span
                      className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                        disablePrivacyMode ? '-translate-x-6' : '-translate-x-1'
                      }`}
                    />
                  </button>
                  {isUpdatingPrivacy && (
                    <span className="flex items-center gap-1 text-[9px] text-sky-400">
                      <Loader2 className="w-2.5 h-2.5 animate-spin" />
                      جاري استدعاء API...
                    </span>
                  )}
                </div>
              </div>
            </div>

            {/* Admin-Only Posting */}
            <div className="p-4 rounded-2xl bg-black/40 border border-white/10 space-y-3">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="font-bold text-xs text-white">المشرفون فقط يكتبون</h4>
                  <p className="text-[10px] text-gray-400 mt-0.5">
                    تعطيل كتابة الرسائل لجميع الأعضاء وقصرها على المشرفين
                  </p>
                </div>
                <input
                  type="checkbox"
                  checked={adminOnlyPosting}
                  onChange={(e) => handleToggleAdminOnly(e.target.checked)}
                  className="w-5 h-5 rounded accent-sky-500 cursor-pointer"
                />
              </div>
            </div>

            {/* Default Member Permissions */}
            <div className="space-y-2 text-xs text-gray-300">
              <span className="font-bold text-gray-200 block text-xs">صلاحيات الأعضاء الافتراضية:</span>
              {[
                { label: 'إرسال الرسائل النصية', icon: <MessageSquare className="w-3.5 h-3.5" /> },
                { label: 'إرسال الوسائط والصور', icon: <Image className="w-3.5 h-3.5" /> },
                { label: 'إرسال الملصقات والمتحركات', icon: <Smile className="w-3.5 h-3.5" /> },
                { label: 'معاينة الروابط المضمنة', icon: <Link className="w-3.5 h-3.5" /> },
                { label: 'تثبيت الرسائل', icon: <Pin className="w-3.5 h-3.5" /> },
              ].map((perm, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-2.5 rounded-xl bg-black/20 border border-white/5"
                >
                  <div className="flex items-center gap-2">
                    {perm.icon}
                    <span>{perm.label}</span>
                  </div>
                  <Check className="w-4 h-4 text-emerald-400" />
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Tab 3: Dedicated Bot Privacy Mode & Telegram API Panel */}
        {activeTab === 'bots' && (
          <div className="p-5 space-y-4 max-h-[50vh] overflow-y-auto">
            {/* Telegram Official Bot Privacy Mode Specification Banner */}
            <div className="p-4 rounded-2xl bg-gradient-to-r from-sky-950/40 via-indigo-950/30 to-black/40 border border-sky-500/30 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-xl bg-sky-500/20 text-sky-300 flex items-center justify-center border border-sky-400/30">
                    <Globe className="w-4 h-4" />
                  </div>
                  <div>
                    <h4 className="font-bold text-xs text-white">
                      آلية وضع الخصوصية في تيليجرام (Group Privacy Mode)
                    </h4>
                    <p className="text-[10px] text-sky-300/80">
                      بروتوكول MTProto & Telegram Bot API
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => handleTogglePrivacyMode(!disablePrivacyMode)}
                  disabled={isUpdatingPrivacy}
                  className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 shadow ${
                    disablePrivacyMode
                      ? 'bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/40'
                      : 'bg-emerald-600 hover:bg-emerald-500 text-white'
                  }`}
                >
                  {isUpdatingPrivacy ? (
                    <>
                      <Loader2 className="w-3.5 h-3.5 animate-spin" />
                      جاري التحديث...
                    </>
                  ) : disablePrivacyMode ? (
                    <>
                      <Lock className="w-3.5 h-3.5" />
                      إعادة تفعيل الخصوصية
                    </>
                  ) : (
                    <>
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      تعطيل وضع الخصوصية الآن
                    </>
                  )}
                </button>
              </div>

              <div className="text-[11px] text-gray-300 space-y-1.5 leading-relaxed bg-black/30 p-3 rounded-xl border border-white/5">
                <div className="flex items-start gap-2">
                  <span className="text-amber-400 shrink-0 font-bold">🔒 الوضع الافتراضي (مفعّل):</span>
                  <span>
                    البوت لا يستلم إلا الأوامر الموجهة له (/)، والردود المباشرة على رسائله، والإشارات المعرّفة (@).
                  </span>
                </div>
                <div className="flex items-start gap-2">
                  <span className="text-emerald-400 shrink-0 font-bold">🌐 الوضع المعطّل (السماح بالكل):</span>
                  <span>
                    يستلم البوت <strong>كافة رسائل المجموعة</strong> (can_read_all_group_messages = true)، لتنفيذ
                    الردود التلقائية والذكاء الاصطناعي والإشراف الفوري.
                  </span>
                </div>
              </div>
            </div>

            {/* Active Group Bots List */}
            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs font-bold text-gray-200">
                <span>بوتات المجموعة النشطة ({botCount})</span>
                <span className="text-[10px] text-gray-400">حالة الصلاحيات الآن</span>
              </div>

              {participants
                .filter((p) => p.is_bot || p.username?.toLowerCase().endsWith('bot'))
                .map((bot) => {
                  const hasAccess = disablePrivacyMode || bot.role === 'admin' || bot.role === 'creator';
                  return (
                    <div
                      key={bot.userId}
                      className="flex items-center justify-between p-3 rounded-2xl bg-black/40 border border-white/10"
                    >
                      <div className="flex items-center gap-2.5">
                        <img
                          src={bot.avatar}
                          alt={bot.name}
                          className="w-9 h-9 rounded-full object-cover border border-white/20"
                        />
                        <div>
                          <div className="flex items-center gap-1.5">
                            <span className="text-xs font-bold text-white">{bot.name}</span>
                            <span className="px-1.5 py-0.2 rounded text-[9px] bg-sky-500/20 text-sky-300 font-bold">
                              BOT
                            </span>
                          </div>
                          <span className="text-[10px] text-gray-400">@{bot.username}</span>
                        </div>
                      </div>

                      <div className="flex items-center gap-2">
                        <span
                          className={`text-[10px] px-2 py-0.5 rounded-full font-bold border flex items-center gap-1 ${
                            hasAccess
                              ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30'
                              : 'bg-amber-500/20 text-amber-300 border-amber-500/30'
                          }`}
                        >
                          {hasAccess ? (
                            <>
                              <CheckCircle2 className="w-3 h-3" />
                              لديه حق الوصول إلى الرسائل
                            </>
                          ) : (
                            <>
                              <Lock className="w-3 h-3" />
                              ليس لديه وصول إلى الرسائل
                            </>
                          )}
                        </span>
                      </div>
                    </div>
                  );
                })}
            </div>

            {/* Interactive Message Delivery Validator */}
            <div className="p-3.5 rounded-2xl bg-black/30 border border-white/10 space-y-2.5">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-white flex items-center gap-1.5">
                  <Sparkles className="w-3.5 h-3.5 text-sky-400" />
                  فاحص استلام الرسائل في المجموعة (Telegram Privacy Live Tester)
                </span>
                <span className="text-[10px] text-gray-400">Telegram Bot Engine</span>
              </div>

              <div className="flex items-center gap-2">
                <input
                  type="text"
                  value={testMessage}
                  onChange={(e) => {
                    setTestMessage(e.target.value);
                    runPrivacyTest(e.target.value);
                  }}
                  placeholder="اكتب رسالة تجريبية لاختبار استلام البوت..."
                  className="flex-1 bg-black/50 border border-white/10 rounded-xl px-3 py-1.5 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-sky-400"
                />
                <button
                  onClick={() => runPrivacyTest(testMessage)}
                  className="px-3 py-1.5 rounded-xl bg-sky-600 hover:bg-sky-500 text-white text-xs font-bold transition-colors"
                >
                  فحص
                </button>
              </div>

              <div className="flex flex-wrap gap-1.5 text-[10px]">
                <button
                  onClick={() => {
                    setTestMessage('مرحبا بالجميع في المجموعة');
                    runPrivacyTest('مرحبا بالجميع في المجموعة');
                  }}
                  className="px-2 py-0.5 rounded-lg bg-white/5 hover:bg-white/10 text-gray-300"
                >
                  نص عادي
                </button>
                <button
                  onClick={() => {
                    setTestMessage('/help');
                    runPrivacyTest('/help');
                  }}
                  className="px-2 py-0.5 rounded-lg bg-white/5 hover:bg-white/10 text-gray-300"
                >
                  أمر: /help
                </button>
                <button
                  onClick={() => {
                    setTestMessage('@TelegramAIBot ما الجديد اليوم؟');
                    runPrivacyTest('@TelegramAIBot ما الجديد اليوم؟');
                  }}
                  className="px-2 py-0.5 rounded-lg bg-white/5 hover:bg-white/10 text-gray-300"
                >
                  إشارة: @TelegramAIBot
                </button>
              </div>

              {testResult && (
                <div
                  className={`p-2.5 rounded-xl border text-xs flex items-center justify-between gap-2 ${
                    testResult.canReceive
                      ? 'bg-emerald-950/40 border-emerald-500/40 text-emerald-200'
                      : 'bg-rose-950/40 border-rose-500/40 text-rose-200'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    {testResult.canReceive ? (
                      <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                    ) : (
                      <XCircle className="w-4 h-4 text-rose-400 shrink-0" />
                    )}
                    <div>
                      <span className="font-bold block">
                        {testResult.canReceive
                          ? '✅ ستصل الرسالة للبوت فوراً'
                          : '❌ لن تصل الرسالة للبوت (محجوبة بوضع الخصوصية)'}
                      </span>
                      <span className="text-[10px] opacity-80">{testResult.reason}</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Tab 4: Slow Mode Countdown */}
        {activeTab === 'slowmode' && (
          <div className="p-5 space-y-4">
            <div className="p-3.5 rounded-2xl bg-black/40 border border-white/10">
              <span className="text-xs font-bold text-white block">الوضع البطيء (Slow Mode)</span>
              <p className="text-[11px] text-gray-400 mt-1 leading-relaxed">
                يحدد مهلة زمنية إجبارية يجب على العضو انتظارها قبل إرسال الرسالة التالية في المجموعة.
              </p>
            </div>

            <div className="grid grid-cols-3 gap-2.5">
              {[
                { label: 'معطل', val: 0 },
                { label: '10 ثواني', val: 10 },
                { label: '30 ثانية', val: 30 },
                { label: '1 دقيقة', val: 60 },
                { label: '5 دقائق', val: 300 },
                { label: '15 دقيقة', val: 900 },
                { label: '1 ساعة', val: 3600 },
              ].map((item) => (
                <button
                  key={item.val}
                  onClick={() => handleSetSlowMode(item.val)}
                  className={`py-2.5 px-2 rounded-xl text-xs font-bold transition-all border ${
                    slowmodeSeconds === item.val
                      ? 'bg-sky-500/30 border-sky-400 text-sky-200 shadow-md'
                      : 'bg-black/20 border-white/10 text-gray-300 hover:bg-white/10'
                  }`}
                >
                  {item.label}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="p-4 bg-black/40 border-t border-white/10 flex justify-end">
          <button
            onClick={() => setActiveModal('none')}
            className="px-5 py-2 rounded-xl bg-sky-600 hover:bg-sky-500 text-white text-xs font-bold transition-colors"
          >
            إغلاق
          </button>
        </div>
      </div>
    </div>
  );
};
