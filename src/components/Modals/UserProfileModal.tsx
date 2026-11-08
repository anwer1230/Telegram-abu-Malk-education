import React, { useState, useMemo } from 'react';
import {
  X,
  MessageCircle,
  Phone,
  Lock,
  Share2,
  Copy,
  Check,
  BadgeCheck,
  Sparkles,
  Users,
  ShieldAlert,
  ExternalLink,
  ChevronRight,
  MoreVertical,
  Bell,
  BellOff,
  Ban,
  Bot,
  AtSign,
  Flag,
  Image as ImageIcon,
  ShieldCheck,
} from 'lucide-react';
import { useTelegram } from '../../context/TelegramContext';

const PEER_COLORS = [
  '#e17076',
  '#faa774',
  '#a695e7',
  '#7bc862',
  '#6ec9cb',
  '#65aadd',
  '#ee7aae',
];

function getPeerColor(nameOrId: string = '') {
  let hash = 0;
  for (let i = 0; i < nameOrId.length; i++) {
    hash = nameOrId.charCodeAt(i) + ((hash << 5) - hash);
  }
  return PEER_COLORS[Math.abs(hash) % PEER_COLORS.length];
}

export const UserProfileModal: React.FC = () => {
  const {
    activeModal,
    setActiveModal,
    selectedProfileUser,
    currentUser,
    settings,
    openPrivateChat,
    startCall,
    getCommonGroupsForUser,
    activeChatId,
    activeChat,
    setChatDraft,
    setActiveChatId,
    showToast,
    setViewerMedia,
    isUserBlocked,
    blockUser,
    unblockUser,
    messages,
  } = useTelegram();

  const [copiedUsername, setCopiedUsername] = useState(false);
  const [copiedPhone, setCopiedPhone] = useState(false);
  const [isContactMuted, setIsContactMuted] = useState(false);

  const isArabic = settings.language === 'ar';
  const user = selectedProfileUser || {
    id: currentUser.id,
    name: currentUser.name || 'Telegram User',
    username: currentUser.username,
    phone: currentUser.phone,
    avatar: currentUser.avatar,
    bio: currentUser.bio || (isArabic ? 'الحساب الشخصي' : 'Personal Profile'),
    isVerified: currentUser.isVerified,
    isPremium: currentUser.isPremium,
    isOnline: true,
  };

  // Shared media from this user in the active chat
  const userSharedMedia = useMemo(() => {
    if (!activeChatId || !messages[activeChatId]) return [];
    const chatMsgs = messages[activeChatId];
    return chatMsgs.filter(
      (m) =>
        (m.senderId === user.id || m.senderName === user.name) &&
        m.media &&
        (m.media.type === 'photo' || m.media.type === 'video') &&
        m.media.url
    );
  }, [activeChatId, messages, user.id, user.name]);

  if (activeModal !== ('user-profile' as any)) return null;

  const isMe = user.id === currentUser.id || user.id === 'user_me';
  const isBot =
    (user as any).is_bot === true ||
    Boolean(user.username && user.username.toLowerCase().endsWith('bot')) ||
    user.id === 'user_botfather' ||
    user.id === 'user_telegramaibot';

  const commonGroups = getCommonGroupsForUser(user.id, user.name);

  const handleCopyUsername = () => {
    if (user.username && navigator.clipboard) {
      navigator.clipboard.writeText(`@${user.username.replace(/^@/, '')}`);
      setCopiedUsername(true);
      showToast(isArabic ? 'تم نسخ اسم المستخدم' : 'Username copied', '📋');
      setTimeout(() => setCopiedUsername(false), 2000);
    }
  };

  const handleCopyPhone = () => {
    if (user.phone && navigator.clipboard) {
      navigator.clipboard.writeText(user.phone);
      setCopiedPhone(true);
      showToast(isArabic ? 'تم نسخ رقم الهاتف' : 'Phone number copied', '📋');
      setTimeout(() => setCopiedPhone(false), 2000);
    }
  };

  const handleStartChat = () => {
    setActiveModal('none');
    if (isMe) {
      setActiveChatId('chat_saved_messages');
    } else {
      openPrivateChat(user.id, user.name, user.avatar, user.username);
    }
  };

  const handleCall = () => {
    setActiveModal('none');
    startCall(false);
  };

  const handleMention = () => {
    const mentionTag = user.username
      ? `@${user.username.replace(/^@/, '')} `
      : `@${user.name} `;
    if (activeChatId) {
      setChatDraft(activeChatId, (activeChat?.draft ? `${activeChat.draft} ` : '') + mentionTag);
    }
    setActiveModal('none');
    showToast(isArabic ? `تمت الإشارة إلى ${user.name}` : `Mentioned ${user.name}`, '✍️');
  };

  const handleToggleNotifications = () => {
    setIsContactMuted(!isContactMuted);
    showToast(
      !isContactMuted
        ? (isArabic ? `تم كتم إشعارات ${user.name}` : `Muted notifications for ${user.name}`)
        : (isArabic ? `تم تفعيل إشعارات ${user.name}` : `Unmuted notifications for ${user.name}`),
      !isContactMuted ? '🔕' : '🔔'
    );
  };

  const handleViewAvatar = () => {
    if (user.avatar) {
      setViewerMedia({
        url: user.avatar,
        title: user.name,
        sender: user.name,
        timestamp: user.isOnline ? (isArabic ? 'متصل الآن' : 'online') : undefined,
      });
      setActiveModal('media-viewer');
    }
  };

  const handleReport = () => {
    showToast(
      isArabic
        ? 'تم إرسال البلاغ لفريق مشرفي تيليجرام لمراجعته 🛡️'
        : 'Report submitted to Telegram moderation team 🛡️',
      '✅'
    );
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 select-none animate-in fade-in duration-200">
      {/* Backdrop */}
      <div
        id="tg-profile-backdrop"
        onClick={() => setActiveModal('none')}
        className="fixed inset-0 bg-black/75 backdrop-blur-xs transition-opacity"
      />

      {/* Modal Dialog */}
      <div
        id="tg-profile-sheet"
        className="relative w-full max-w-md rounded-3xl shadow-2xl overflow-hidden border z-10 animate-in zoom-in-95 duration-150 flex flex-col max-h-[92vh]"
        style={{
          backgroundColor: 'var(--tg-theme-surface, #17212b)',
          borderColor: 'var(--tg-theme-border, #242f3d)',
          color: 'var(--tg-theme-bubble-in-text, #ffffff)',
        }}
      >
        {/* Header Bar */}
        <div className="flex items-center justify-between p-4 border-b border-white/10 shrink-0">
          <div className="flex items-center gap-2">
            <span className="font-bold text-base">
              {isArabic ? 'الملف التعريفي' : 'User Info'}
            </span>
            {user.isBot && (
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-sky-500/20 text-sky-400 border border-sky-500/30 font-semibold uppercase">
                {isArabic ? 'بوت رسمي' : 'BOT'}
              </span>
            )}
          </div>
          <div className="flex items-center gap-1">
            <button
              onClick={() => {
                if (user.username && navigator.clipboard) {
                  navigator.clipboard.writeText(`https://t.me/${user.username.replace(/^@/, '')}`);
                  showToast(isArabic ? 'تم نسخ رابط الحساب' : 'Profile link copied', '🔗');
                }
              }}
              className="p-2 rounded-full hover:bg-white/10 text-gray-400 hover:text-white transition-colors"
              title={isArabic ? 'مشاركة الحساب' : 'Share profile'}
            >
              <Share2 className="w-4 h-4" />
            </button>
            <button
              onClick={() => setActiveModal('none')}
              className="p-2 rounded-full hover:bg-white/10 text-gray-400 hover:text-white transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Scrollable Content */}
        <div className="overflow-y-auto flex-1 p-5 space-y-4">
          {/* Avatar & Core Identity */}
          <div className="flex flex-col items-center text-center">
            <div
              onClick={handleViewAvatar}
              className={`relative w-24 h-24 rounded-full overflow-hidden mb-3.5 shadow-xl border-2 border-sky-400/30 shrink-0 ${
                user.avatar ? 'cursor-pointer hover:opacity-90 active:scale-95 transition-transform' : ''
              }`}
            >
              {user.avatar ? (
                <img
                  src={user.avatar}
                  alt={user.name}
                  className="w-full h-full object-cover"
                  referrerPolicy="no-referrer"
                />
              ) : (
                <div
                  className="w-full h-full flex items-center justify-center text-white font-bold text-3xl shadow-inner"
                  style={{
                    backgroundColor: getPeerColor(user.id || user.name),
                  }}
                >
                  {user.name.charAt(0).toUpperCase()}
                </div>
              )}
            </div>

            {/* Real Name & Badges */}
            <div className="flex items-center justify-center gap-1.5 mb-1 max-w-full px-2">
              <h2 className="font-bold text-xl leading-tight truncate">{user.name}</h2>
              {user.isVerified && (
                <span title={isArabic ? 'حساب موثق رسمياً' : 'Verified account'}>
                  <BadgeCheck
                    className="w-5 h-5 text-[#2481cc] fill-[#2481cc]/20 shrink-0"
                  />
                </span>
              )}
              {user.isPremium && (
                <span className="p-0.5 rounded-full bg-gradient-to-tr from-purple-500 to-indigo-500 text-white shrink-0 shadow-sm" title="Telegram Premium">
                  <Sparkles className="w-3.5 h-3.5" />
                </span>
              )}
              {isBot && (
                <span className="px-1.5 py-0.5 rounded-md bg-[#2481cc]/20 text-[#2481cc] text-[10px] font-bold font-mono uppercase tracking-wider shrink-0">
                  {isArabic ? 'بوت' : 'bot'}
                </span>
              )}
            </div>

            {/* Online / Bot Status */}
            <div className="text-xs font-medium flex items-center gap-1.5">
              {isBot ? (
                <span className="text-sky-400 font-medium">
                  {isArabic ? 'بوت' : 'bot'}
                </span>
              ) : user.isOnline ? (
                <>
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                  <span className="text-sky-400 font-semibold">
                    {isArabic ? 'متصل الآن' : 'online'}
                  </span>
                </>
              ) : (
                <span className="text-gray-400">
                  {user.lastSeen || (isArabic ? 'آخر ظهور حديثاً' : 'last seen recently')}
                </span>
              )}
            </div>
          </div>

          {/* Quick Actions Row */}
          {!isMe && (
            <div className="grid grid-cols-4 gap-2 pt-1">
              <button
                onClick={handleStartChat}
                className="flex flex-col items-center justify-center gap-1.5 py-2.5 px-1 rounded-2xl bg-[#2481cc]/15 hover:bg-[#2481cc]/25 text-[#2481cc] border border-[#2481cc]/30 transition-all active:scale-95"
                title={isArabic ? 'مراسلة خاصة' : 'Direct Message'}
              >
                <MessageCircle className="w-4 h-4" />
                <span className="text-[11px] font-bold">{isArabic ? 'مراسلة' : 'Message'}</span>
              </button>

              <button
                onClick={handleCall}
                className="flex flex-col items-center justify-center gap-1.5 py-2.5 px-1 rounded-2xl bg-white/5 hover:bg-white/10 text-white border border-white/10 transition-all active:scale-95"
                title={isArabic ? 'اتصال صوتي' : 'Audio Call'}
              >
                <Phone className="w-4 h-4 text-emerald-400" />
                <span className="text-[11px] font-bold">{isArabic ? 'اتصال' : 'Call'}</span>
              </button>

              <button
                onClick={handleMention}
                className="flex flex-col items-center justify-center gap-1.5 py-2.5 px-1 rounded-2xl bg-white/5 hover:bg-white/10 text-white border border-white/10 transition-all active:scale-95"
                title={isArabic ? 'إشارة في الدردشة' : 'Mention in Chat'}
              >
                <AtSign className="w-4 h-4 text-sky-400" />
                <span className="text-[11px] font-bold">{isArabic ? 'إشارة' : 'Mention'}</span>
              </button>

              <button
                onClick={() => {
                  setActiveModal('none');
                  showToast(
                    isArabic
                      ? `تم بدء محادثة سرية مشفرة مع ${user.name}`
                      : `Started secret chat with ${user.name}`,
                    '🔒'
                  );
                }}
                className="flex flex-col items-center justify-center gap-1.5 py-2.5 px-1 rounded-2xl bg-white/5 hover:bg-white/10 text-white border border-white/10 transition-all active:scale-95"
                title={isArabic ? 'محادثة سرية' : 'Secret Chat'}
              >
                <Lock className="w-4 h-4 text-amber-400" />
                <span className="text-[11px] font-bold">{isArabic ? 'سرية' : 'Secret'}</span>
              </button>
            </div>
          )}

          {/* Group Context Badge (if clicked from a group) */}
          {user.sourceChatTitle && (
            <div className="rounded-2xl bg-sky-500/10 border border-sky-500/20 p-3 flex items-center justify-between">
              <div className="flex items-center gap-2 min-w-0">
                <Users className="w-4 h-4 text-sky-400 shrink-0" />
                <div className="truncate">
                  <div className="text-[10px] text-gray-400">{isArabic ? 'مصدر الرسالة في المجموعة' : 'Member in group'}</div>
                  <div className="text-xs font-semibold text-white truncate">{user.sourceChatTitle}</div>
                </div>
              </div>
              <span className={`text-[10px] px-2 py-0.5 rounded font-semibold shrink-0 ${
                user.senderRole === 'owner'
                  ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                  : user.senderRole === 'admin'
                  ? 'bg-sky-500/20 text-sky-300 border border-sky-500/30'
                  : 'bg-white/10 text-gray-300'
              }`}>
                {user.senderRank || (user.senderRole === 'owner' ? (isArabic ? '👑 مالك' : 'Owner') : user.senderRole === 'admin' ? (isArabic ? '🛡️ مشرف' : 'Admin') : (isArabic ? 'عضو' : 'Member'))}
              </span>
            </div>
          )}

          {/* Contact Details Card */}
          <div className="rounded-2xl bg-black/20 border border-white/5 divide-y divide-white/5 overflow-hidden">
            {/* Phone (if available) */}
            {user.phone && (
              <div
                onClick={handleCopyPhone}
                className="p-3.5 flex items-center justify-between hover:bg-white/5 transition-colors cursor-pointer"
              >
                <div>
                  <div className="text-xs text-gray-400 mb-0.5">{isArabic ? 'رقم الهاتف' : 'Phone'}</div>
                  <div className="text-sm font-semibold font-mono text-white">{user.phone}</div>
                </div>
                <button className="text-gray-400 hover:text-white p-1">
                  {copiedPhone ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
                </button>
              </div>
            )}

            {/* Username */}
            {user.username && (
              <div
                onClick={handleCopyUsername}
                className="p-3.5 flex items-center justify-between hover:bg-white/5 transition-colors cursor-pointer"
              >
                <div>
                  <div className="text-xs text-gray-400 mb-0.5">{isArabic ? 'اسم المستخدم' : 'Username'}</div>
                  <div className="text-sm font-semibold font-mono text-sky-400">
                    @{user.username.replace(/^@/, '')}
                  </div>
                </div>
                <button className="text-gray-400 hover:text-white p-1">
                  {copiedUsername ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
                </button>
              </div>
            )}

            {/* Bio / About */}
            {user.bio && (
              <div className="p-3.5">
                <div className="text-xs text-gray-400 mb-0.5">{isArabic ? 'النبذة التعريفية' : 'Bio'}</div>
                <div className="text-xs text-gray-200 leading-relaxed break-words whitespace-pre-wrap">
                  {user.bio}
                </div>
              </div>
            )}

            {/* Notifications Toggle */}
            {!isMe && (
              <div
                onClick={handleToggleNotifications}
                className="p-3.5 flex items-center justify-between hover:bg-white/5 transition-colors cursor-pointer"
              >
                <div className="flex items-center gap-2.5">
                  {isContactMuted ? (
                    <BellOff className="w-4 h-4 text-rose-400" />
                  ) : (
                    <Bell className="w-4 h-4 text-sky-400" />
                  )}
                  <div>
                    <div className="text-xs font-semibold text-white">
                      {isArabic ? 'إشعارات هذا المستخدم' : 'Notifications'}
                    </div>
                    <div className="text-[10px] text-gray-400">
                      {isContactMuted
                        ? isArabic ? 'مكتومة' : 'Muted'
                        : isArabic ? 'مفعلة' : 'Enabled'}
                    </div>
                  </div>
                </div>
                <div className={`w-9 h-5 rounded-full transition-colors relative ${isContactMuted ? 'bg-gray-700' : 'bg-[#2481cc]'}`}>
                  <div className={`w-3.5 h-3.5 rounded-full bg-white absolute top-0.75 transition-all ${isContactMuted ? 'left-0.75' : 'right-0.75'}`} />
                </div>
              </div>
            )}

            {/* What can this bot do? (ماذا يمكن لهذا البوت أن يفعل؟) */}
            {isBot && (
              <div className="p-3.5 bg-sky-500/10 border-t border-white/5">
                <div className="text-xs font-bold text-sky-400 mb-1 flex items-center gap-1.5">
                  <Bot className="w-3.5 h-3.5" />
                  <span>{isArabic ? 'ماذا يمكن لهذا البوت أن يفعل؟' : 'What can this bot do?'}</span>
                </div>
                <p className="text-xs text-gray-300 leading-relaxed">
                  {user.bio || (isArabic ? 'بوت تيليجرام تفاعلي متصل بسحابة MTProto لدعم الأوامر الرسمية، والاستعلام المضمن، ولوحات المفاتيح التفاعلية.' : 'Interactive Telegram Bot connected via MTProto supporting custom commands, inline queries, and keyboards.')}
                </p>
              </div>
            )}
          </div>

          {/* Shared Media Strip (if available) */}
          {userSharedMedia.length > 0 && (
            <div className="rounded-2xl bg-black/20 border border-white/5 p-3.5">
              <div className="flex items-center justify-between mb-2.5">
                <div className="text-xs font-bold text-gray-300 flex items-center gap-1.5">
                  <ImageIcon className="w-4 h-4 text-emerald-400" />
                  <span>{isArabic ? 'الوسائط المرسلة من العضو' : 'Shared Media in Chat'}</span>
                </div>
                <span className="text-[11px] font-mono text-gray-400">
                  {userSharedMedia.length} {isArabic ? 'عنصر' : 'items'}
                </span>
              </div>
              <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-thin">
                {userSharedMedia.slice(0, 8).map((mediaMsg) => (
                  <div
                    key={mediaMsg.id}
                    onClick={() => {
                      if (mediaMsg.media?.url) {
                        setViewerMedia({
                          url: mediaMsg.media.url,
                          title: mediaMsg.media.fileName || user.name,
                          sender: user.name,
                          timestamp: mediaMsg.timestamp,
                        });
                        setActiveModal('media-viewer');
                      }
                    }}
                    className="w-16 h-16 rounded-xl overflow-hidden shrink-0 border border-white/10 hover:border-sky-400 cursor-pointer transition-all hover:scale-105 relative"
                  >
                    <img
                      src={mediaMsg.media?.url}
                      alt="media"
                      className="w-full h-full object-cover"
                      referrerPolicy="no-referrer"
                    />
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Common Groups (المجموعات المشتركة) */}
          <div className="rounded-2xl bg-black/20 border border-white/5 p-3.5">
            <div className="flex items-center justify-between mb-2.5">
              <div className="text-xs font-bold text-gray-300 flex items-center gap-1.5">
                <Users className="w-4 h-4 text-sky-400" />
                <span>{isArabic ? 'المجموعات المشتركة' : 'Common Groups'}</span>
              </div>
              <span className="text-[11px] font-mono text-gray-400">
                {commonGroups.length} {isArabic ? 'مجموعة' : 'groups'}
              </span>
            </div>

            {commonGroups.length > 0 ? (
              <div className="space-y-1.5">
                {commonGroups.map((group) => (
                  <div
                    key={group.id}
                    onClick={() => {
                      setActiveModal('none');
                      setActiveChatId(group.id);
                    }}
                    className="flex items-center justify-between p-2 rounded-xl hover:bg-white/5 transition-colors cursor-pointer group"
                  >
                    <div className="flex items-center gap-2.5 min-w-0">
                      <div className="w-8 h-8 rounded-full overflow-hidden bg-sky-600/30 flex items-center justify-center text-xs font-bold shrink-0">
                        {group.avatar ? (
                          <img src={group.avatar} alt={group.title} className="w-full h-full object-cover" />
                        ) : (
                          group.title.charAt(0)
                        )}
                      </div>
                      <div className="truncate">
                        <div className="text-xs font-semibold text-white group-hover:text-sky-300 transition-colors truncate">
                          {group.title}
                        </div>
                        <div className="text-[10px] text-gray-400">
                          {group.memberCount || 150} {isArabic ? 'عضو' : 'members'}
                        </div>
                      </div>
                    </div>
                    <ChevronRight className="w-4 h-4 text-gray-400 group-hover:text-white transition-colors shrink-0 rtl:rotate-180" />
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-xs text-gray-400 text-center py-2">
                {isArabic ? 'لا توجد مجموعات مشتركة حالياً' : 'No common groups found'}
              </div>
            )}
          </div>

          {/* Privacy & Safety Actions */}
          {!isMe && (
            <div className="space-y-2 pt-1">
              <button
                onClick={() => {
                  const blocked = isUserBlocked(user.id);
                  if (blocked) {
                    unblockUser(user.id);
                    showToast(isArabic ? `تم إلغاء حظر ${user.name}` : `Unblocked ${user.name}`, '✅');
                  } else {
                    blockUser(user.id);
                    showToast(isArabic ? `تم حظر ${user.name} بنجاح` : `Blocked ${user.name}`, '🚫');
                  }
                }}
                className={`w-full p-3 rounded-xl text-xs font-semibold flex items-center justify-center gap-2 transition-all ${
                  isUserBlocked(user.id)
                    ? 'bg-emerald-500/15 hover:bg-emerald-500/25 text-emerald-400 border border-emerald-500/30'
                    : 'hover:bg-rose-500/10 text-rose-400 hover:text-rose-300 border border-rose-500/20'
                }`}
              >
                <Ban className="w-4 h-4" />
                <span>
                  {isUserBlocked(user.id)
                    ? isArabic ? 'إلغاء حظر المستخدم' : 'Unblock User'
                    : isArabic ? 'حظر المستخدم' : 'Block User'}
                </span>
              </button>

              <button
                onClick={handleReport}
                className="w-full p-2.5 rounded-xl text-xs font-medium text-gray-400 hover:text-amber-300 hover:bg-amber-500/10 transition-colors flex items-center justify-center gap-2"
              >
                <Flag className="w-3.5 h-3.5" />
                <span>{isArabic ? 'إبلاغ عن محتوى غير لائق' : 'Report user'}</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
