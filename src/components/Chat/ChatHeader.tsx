import React, { useState } from 'react';
import {
  ArrowLeft,
  Phone,
  Video,
  Search,
  MoreVertical,
  BadgeCheck,
  Bookmark,
  Bot,
  Megaphone,
  Users,
  PanelRight,
  Download,
  Sparkles,
  Lock,
  ShieldCheck,
  Layers,
} from 'lucide-react';
import { useTelegram } from '../../context/TelegramContext';

// Authentic Telegram 7-Peer Color Palettes for default avatars
const PEER_GRADIENTS = [
  'from-[#e17076] to-[#f0858a]', // coral red
  'from-[#faa774] to-[#fbb88c]', // orange
  'from-[#a695e7] to-[#b8a9ec]', // violet
  'from-[#7bc862] to-[#8ed676]', // green
  'from-[#6ec9cb] to-[#80d7d9]', // cyan
  'from-[#65aadd] to-[#7bb9e3]', // blue
  'from-[#ee7aae] to-[#f58ebc]', // pink
];

function getPeerGradient(name: string = '') {
  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = (hash * 31 + name.charCodeAt(i)) % PEER_GRADIENTS.length;
  }
  return PEER_GRADIENTS[Math.abs(hash)] || PEER_GRADIENTS[0];
}

export const ChatHeader: React.FC = () => {
  const {
    activeChat,
    setActiveChatId,
    startCall,
    isRightPanelOpen,
    setIsRightPanelOpen,
    setActiveModal,
    typingChatId,
    typingUsers,
    settings,
  } = useTelegram();

  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  if (!activeChat) return null;

  const isSavedMessages = activeChat.type === 'saved';
  const isArabic = settings.language === 'ar';

  const isBotChat =
    activeChat.type === 'bot' ||
    Boolean(activeChat.username && activeChat.username.toLowerCase().endsWith('bot')) ||
    activeChat.id === 'chat_botfather' ||
    activeChat.id === 'chat_ai_bot' ||
    activeChat.id === 'chat_crypto_bot';

  const activeTypers = typingUsers?.[activeChat.id] || [];
  const isTyping = activeTypers.length > 0 || typingChatId === activeChat.id;

  const renderTypingStatus = () => {
    if (activeChat.type === 'group' && activeTypers.length > 0) {
      if (activeTypers.length === 1) {
        const typer = activeTypers[0];
        const actionText =
          typer.action === 'record_audio'
            ? (isArabic ? 'يسجل رسالة صوتية...' : 'is recording voice...')
            : typer.action === 'upload_photo'
            ? (isArabic ? 'يرسل صورة...' : 'is sending a photo...')
            : typer.action === 'upload_document'
            ? (isArabic ? 'يرسل ملفاً...' : 'is sending a file...')
            : (isArabic ? 'يكتب...' : 'is typing...');
        return `${typer.userName} ${actionText}`;
      } else if (activeTypers.length === 2) {
        return isArabic
          ? `${activeTypers[0].userName} و ${activeTypers[1].userName} يكتبان...`
          : `${activeTypers[0].userName}, ${activeTypers[1].userName} are typing...`;
      } else {
        return isArabic
          ? `${activeTypers.length} أشخاص يكتبون...`
          : `${activeTypers.length} people are typing...`;
      }
    }

    const singleTyper = activeTypers[0];
    if (singleTyper?.action === 'record_audio') {
      return isArabic ? 'يسجل رسالة صوتية...' : 'recording voice...';
    }
    if (singleTyper?.action === 'upload_photo') {
      return isArabic ? 'يرسل صورة...' : 'sending a photo...';
    }
    return isArabic ? 'يكتب الآن...' : 'typing...';
  };

  const getSubtitle = () => {
    if (isSavedMessages) {
      return isArabic ? 'مساحتك السحابية الخاصة' : 'Personal Cloud Storage';
    }
    if (activeChat.type === 'channel') {
      const count = activeChat.memberCount || 950000;
      const formatted =
        count >= 1000000
          ? (count / 1000000).toFixed(1) + 'M'
          : count >= 1000
          ? (count / 1000).toFixed(count >= 10000 ? 0 : 1) + 'K'
          : count.toLocaleString();
      return isArabic ? `${formatted} مشترك` : `${formatted} subscribers`;
    }
    if (activeChat.type === 'group') {
      const members = activeChat.memberCount || 14850;
      const online = activeChat.onlineCount || Math.max(1, Math.round(members * 0.085));
      const formattedMembers = members.toLocaleString(isArabic ? 'ar-EG' : 'en-US');
      const formattedOnline = online.toLocaleString(isArabic ? 'ar-EG' : 'en-US');
      return isArabic
        ? `${formattedMembers} عضواً، ${formattedOnline} متصل`
        : `${formattedMembers} members, ${formattedOnline} online`;
    }
    if (isBotChat) {
      return isArabic ? 'بوت' : 'bot';
    }
    return isArabic ? 'متصل الآن' : 'online';
  };

  return (
    <div
      id="tg-chat-header"
      className="h-14 px-3 flex items-center justify-between border-b select-none shrink-0 z-10"
      style={{
        backgroundColor: 'var(--tg-theme-surface)',
        borderColor: 'var(--tg-theme-border)',
      }}
    >
      {/* Left side: Back on mobile + Avatar + Title & Status */}
      <div className="flex items-center gap-3 min-w-0">
        {/* Back button for mobile view */}
        <button
          id="tg-header-back-button"
          onClick={() => setActiveChatId(null)}
          className="md:hidden p-1.5 -ml-1 rtl:ml-0 rtl:-mr-1 text-[#708499] hover:text-white hover:bg-white/10 rounded-full transition-colors"
        >
          <ArrowLeft className="w-5 h-5 rtl:rotate-180" />
        </button>

        {/* Avatar */}
        <div
          onClick={() => setIsRightPanelOpen(!isRightPanelOpen)}
          className={`relative w-10 h-10 rounded-full overflow-hidden flex items-center justify-center text-white font-bold text-base cursor-pointer shrink-0 shadow-xs ${
            isSavedMessages
              ? 'bg-[#2481cc]'
              : activeChat.avatar
              ? 'bg-[#242f3d]'
              : `bg-gradient-to-tr ${getPeerGradient(activeChat.title)}`
          }`}
        >
          {isSavedMessages ? (
            <Bookmark className="w-5 h-5 fill-white text-white" />
          ) : activeChat.avatar ? (
            <img
              src={activeChat.avatar}
              alt={activeChat.title}
              className="w-full h-full object-cover"
              referrerPolicy="no-referrer"
            />
          ) : (
            <span>{activeChat.title.charAt(0).toUpperCase()}</span>
          )}

          {activeChat.type === 'private' && (
            <span className="absolute bottom-0 right-0 w-2.5 h-2.5 bg-[#4fae4e] border-2 border-[#17212b] rounded-full" />
          )}
        </div>

        {/* Title & Subtitle */}
        <div
          onClick={() => setIsRightPanelOpen(!isRightPanelOpen)}
          className="min-w-0 cursor-pointer"
        >
          <div className="flex items-center gap-1">
            {activeChat.isSecret && (
              <Lock className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
            )}
            <span
              className={`font-semibold text-sm truncate ${
                activeChat.isSecret ? 'text-emerald-400' : 'text-white'
              }`}
            >
              {isSavedMessages ? (isArabic ? 'الرسائل المحفوظة' : 'Saved Messages') : activeChat.title}
            </span>
            {activeChat.isVerified && (
              <BadgeCheck className="w-4 h-4 text-[#2481cc] shrink-0 fill-[#2481cc]/20" />
            )}
            {isBotChat && (
              <span className="px-1.5 py-0.5 rounded-md bg-[#2481cc]/20 text-[#2481cc] text-[10px] font-bold font-mono uppercase tracking-wider shrink-0">
                {isArabic ? 'بوت' : 'bot'}
              </span>
            )}
          </div>
          <div className="text-xs truncate font-normal">
            {isTyping ? (
              <span className="text-[#2481cc] font-medium flex items-center gap-1.5">
                <span>{renderTypingStatus()}</span>
                <span className="inline-flex items-center gap-0.5 ml-0.5 rtl:mr-0.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#2481cc] animate-bounce [animation-delay:-0.3s]" />
                  <span className="w-1.5 h-1.5 rounded-full bg-[#2481cc] animate-bounce [animation-delay:-0.15s]" />
                  <span className="w-1.5 h-1.5 rounded-full bg-[#2481cc] animate-bounce" />
                </span>
              </span>
            ) : activeChat.isSecret ? (
              <span className="text-emerald-400 font-mono text-[11px]">
                🔒 E2EE Secret Chat {activeChat.ttlSeconds ? `(${activeChat.ttlSeconds}s TTL)` : ''}
              </span>
            ) : (
              <span className="text-[#708499]">{getSubtitle()}</span>
            )}
          </div>
        </div>
      </div>

      {/* Right side action icons */}
      <div className="flex items-center gap-0.5 text-[#708499]">
        {activeChat.isSecret && (
          <button
            id="tg-secret-chat-info-btn"
            onClick={() => setActiveModal('secret-chat-info' as any)}
            className="p-2 rounded-full bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-400 border border-emerald-400/30 transition-colors"
            title="إعدادات التشفير التام والمؤقت الذاتي"
          >
            <Lock className="w-4 h-4" />
          </button>
        )}

        {activeChat.type === 'group' && (
          <>
            <button
              id="tg-group-topics-btn"
              onClick={() => setActiveModal('forum-topics' as any)}
              className="p-2 rounded-full bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-400 border border-cyan-400/20 transition-colors"
              title={isArabic ? 'مواضيع المنتدى (Topics)' : 'Forum Topics'}
            >
              <Layers className="w-4 h-4" />
            </button>
            <button
              id="tg-group-admin-btn"
              onClick={() => setActiveModal('group-admin' as any)}
              className="p-2 rounded-full bg-sky-500/10 hover:bg-sky-500/20 text-sky-400 border border-sky-400/20 transition-colors"
              title="إدارة المجموعة والصلاحيات (TLRPC)"
            >
              <ShieldCheck className="w-4 h-4" />
            </button>
          </>
        )}

        {!isSavedMessages && activeChat.type !== 'channel' && (
          <>
            <button
              id="tg-start-audio-call"
              onClick={() => startCall(false)}
              className="p-2 rounded-full hover:bg-white/10 active:bg-white/15 hover:text-white transition-colors"
              title={isArabic ? 'مكالمة صوتية مشفرة' : 'Encrypted Voice Call'}
            >
              <Phone className="w-4 h-4" />
            </button>
            <button
              id="tg-start-video-call"
              onClick={() => startCall(true)}
              className="p-2 rounded-full hover:bg-white/10 active:bg-white/15 hover:text-white transition-colors"
              title={isArabic ? 'مكالمة فيديو مشفرة' : 'Encrypted Video Call'}
            >
              <Video className="w-4 h-4" />
            </button>
          </>
        )}

        <button
          id="tg-toggle-right-panel"
          onClick={() => setIsRightPanelOpen(!isRightPanelOpen)}
          className={`p-2 rounded-full hover:bg-white/10 active:bg-white/15 transition-colors ${
            isRightPanelOpen ? 'text-[#2481cc] bg-white/5' : 'hover:text-white'
          }`}
          title={isArabic ? 'معلومات المحادثة' : 'Chat Info'}
        >
          <PanelRight className="w-4 h-4" />
        </button>

        {/* More Options Dropdown */}
        <div className="relative">
          <button
            onClick={() => setIsDropdownOpen(!isDropdownOpen)}
            className="p-2 rounded-full hover:bg-white/10 active:bg-white/15 hover:text-white transition-colors"
          >
            <MoreVertical className="w-4 h-4" />
          </button>

          {isDropdownOpen && (
            <div
              className="absolute right-0 rtl:right-auto rtl:left-0 top-10 w-52 bg-[#17212b] border border-[#2b394a] rounded-2xl shadow-2xl py-1.5 z-50 text-xs font-semibold text-gray-200 animate-in fade-in zoom-in-95"
              onClick={() => setIsDropdownOpen(false)}
            >
              <button
                onClick={() => setActiveModal('export-chat')}
                className="w-full px-3.5 py-2.5 hover:bg-white/5 flex items-center gap-2.5 text-left rtl:text-right text-gray-200 hover:text-white"
              >
                <Download className="w-4 h-4 text-sky-400 shrink-0" />
                <span>{isArabic ? 'تصدير سجل المحادثة' : 'Export Chat History'}</span>
              </button>

              <button
                onClick={() => setActiveModal('mini-apps')}
                className="w-full px-3.5 py-2.5 hover:bg-white/5 flex items-center gap-2.5 text-left rtl:text-right text-gray-200 hover:text-white"
              >
                <Sparkles className="w-4 h-4 text-amber-400 shrink-0" />
                <span>{isArabic ? 'تطبيقات وألعاب (Mini Apps)' : 'Telegram Mini Apps'}</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
