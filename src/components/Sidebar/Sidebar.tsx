import React, { useMemo } from 'react';
import { Menu, Search, Plus, Bookmark, Check, CheckCheck, Pin, VolumeX, BadgeCheck, Lock, X, Radio, Link2, MessageSquare } from 'lucide-react';
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

/**
 * Avatar with onError fallback to Telegram peer gradient & initial letter
 */
function ChatAvatarItem({ chat, isSaved }: { chat: any; isSaved: boolean }) {
  const [imgError, setImgError] = React.useState(false);

  React.useEffect(() => {
    setImgError(false);
  }, [chat.avatar]);

  if (isSaved) {
    return (
      <div className="w-12 h-12 rounded-full flex items-center justify-center font-bold text-base text-white overflow-hidden shadow-xs bg-[#2481cc]">
        <Bookmark className="w-5 h-5 fill-white text-white" />
      </div>
    );
  }

  const showAvatar = Boolean(chat.avatar && !imgError);

  return (
    <div
      className={`w-12 h-12 rounded-full flex items-center justify-center font-bold text-base text-white overflow-hidden shadow-xs ${
        showAvatar ? 'bg-[#242f3d]' : `bg-gradient-to-tr ${getPeerGradient(chat.title)}`
      }`}
    >
      {showAvatar ? (
        <img
          src={chat.avatar}
          alt={chat.title}
          className="w-full h-full object-cover"
          loading="lazy"
          referrerPolicy="no-referrer"
          onError={() => setImgError(true)}
        />
      ) : (
        (chat.title || 'U').charAt(0).toUpperCase()
      )}
    </div>
  );
}

/**
 * Renders text with search query matches highlighted
 */
function HighlightMatch({ text, query }: { text: string; query: string }) {
  const q = query.trim();
  if (!q || !text) return <>{text}</>;

  const escaped = q.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const regex = new RegExp(`(${escaped})`, 'gi');
  const parts = text.split(regex);

  return (
    <>
      {parts.map((part, index) =>
        regex.test(part) ? (
          <mark
            key={index}
            className="bg-[#2481cc]/40 text-white rounded-xs px-0.5 font-medium not-italic"
          >
            {part}
          </mark>
        ) : (
          part
        )
      )}
    </>
  );
}

export const Sidebar: React.FC = () => {
  const {
    chats,
    messages,
    activeChatId,
    setActiveChatId,
    searchQuery,
    setSearchQuery,
    folders,
    activeFolderId,
    setActiveFolderId,
    setIsDrawerOpen,
    setActiveModal,
    setChatContextMenu,
    typingChatId,
    settings,
  } = useTelegram();

  const isArabic = settings.language === 'ar';

  const normalizedQuery = searchQuery.trim().toLowerCase();

  const filteredChats = useMemo(() => {
    return chats.filter((c) => {
      // Folder filter
      if (activeFolderId !== 'all') {
        const folder = folders.find((f) => f.id === activeFolderId);
        if (folder && folder.includedChatIds && !folder.includedChatIds.includes(c.id)) {
          return false;
        }
      }

      // If no search query, show all chats in folder
      if (!normalizedQuery) {
        return true;
      }

      // Title match
      const titleMatch = c.title.toLowerCase().includes(normalizedQuery);
      if (titleMatch) return true;

      // Username match
      const usernameMatch = c.username ? c.username.toLowerCase().includes(normalizedQuery) : false;
      if (usernameMatch) return true;

      // Saved messages special localized label match
      if (c.type === 'saved') {
        const savedLabelAr = 'الرسائل المحفوظة';
        const savedLabelEn = 'saved messages';
        if (savedLabelAr.includes(normalizedQuery) || savedLabelEn.includes(normalizedQuery)) {
          return true;
        }
      }

      // Last message text match
      const lastMsgText = typeof c.lastMessage === 'string'
        ? c.lastMessage
        : c.lastMessage?.text || '';
      if (lastMsgText.toLowerCase().includes(normalizedQuery)) {
        return true;
      }

      // Draft text match
      if (c.draft && c.draft.toLowerCase().includes(normalizedQuery)) {
        return true;
      }

      // Search in chat's message history if available
      const chatMessages = messages[c.id];
      if (chatMessages && chatMessages.length > 0) {
        return chatMessages.some(
          (m) =>
            m.text &&
            m.text.toLowerCase().includes(normalizedQuery)
        );
      }

      return false;
    });
  }, [chats, messages, activeFolderId, folders, normalizedQuery]);

  return (
    <aside
      id="tg-sidebar"
      className={`relative w-full md:w-80 lg:w-96 h-full flex flex-col border-r border-[#101921] bg-[#17212b] text-white shrink-0 ${
        activeChatId ? 'hidden md:flex' : 'flex'
      }`}
    >
      {/* Header & Search */}
      <div className="p-2.5 flex items-center gap-2 border-b border-[#101921]">
        <button
          onClick={() => setIsDrawerOpen(true)}
          className="p-2 rounded-full hover:bg-white/10 text-[#708499] hover:text-white transition-colors"
          title="Open Menu"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="flex-1 relative flex items-center">
          <Search className="w-4 h-4 text-[#708499] absolute left-3 rtl:left-auto rtl:right-3 pointer-events-none" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Escape' && searchQuery) {
                e.stopPropagation();
                setSearchQuery('');
              }
            }}
            placeholder={isArabic ? 'بحث في المحادثات...' : 'Search chats...'}
            className="w-full bg-[#242f3d] border border-transparent focus:border-[#2481cc]/60 rounded-full pl-9 pr-8 rtl:pl-8 rtl:pr-9 py-1.5 text-sm text-white placeholder-[#708499] focus:outline-none transition-all"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-2.5 rtl:right-auto rtl:left-2.5 p-0.5 text-[#708499] hover:text-white rounded-full transition-colors"
              title={isArabic ? 'مسح البحث' : 'Clear search'}
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

        <button
          onClick={() => setActiveModal('link-monitor')}
          className="relative p-2 rounded-full hover:bg-white/10 text-[#708499] hover:text-[#2481cc] transition-colors shrink-0"
          title={isArabic ? 'رادار مراقبة الروابط والانضمام الفوري (نشط دائماً)' : 'Link Monitor & Auto-Join (Always Active)'}
        >
          <Link2 className="w-5 h-5 text-[#2481cc]" />
          <span className="absolute top-1 right-1 flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#5288c1] opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-[#2481cc]"></span>
          </span>
        </button>

        <button
          onClick={() => setActiveModal('sender')}
          className="p-2 rounded-full hover:bg-white/10 text-[#708499] hover:text-[#2481cc] transition-colors shrink-0"
          title={isArabic ? 'نظام الإرسال والمراقبة' : 'Broadcast & Monitoring'}
        >
          <Radio className="w-5 h-5" />
        </button>

        <button
          onClick={() => setActiveModal('auto-responder')}
          className="p-2 rounded-full hover:bg-white/10 text-[#708499] hover:text-emerald-400 transition-colors shrink-0"
          title={isArabic ? 'الردود التلقائية الذكية' : 'Auto Replies'}
        >
          <MessageSquare className="w-5 h-5" />
        </button>
      </div>

      {/* Search status bar when actively searching */}
      {searchQuery.trim() && (
        <div className="px-3 py-1.5 bg-[#202b36] border-b border-[#101921] flex items-center justify-between text-xs text-[#708499]">
          <span>
            {isArabic ? 'نتائج البحث عن:' : 'Search results for:'}{' '}
            <span className="text-white font-medium">"{searchQuery.trim()}"</span>
          </span>
          <span className="bg-[#242f3d] text-[#8daecf] px-2 py-0.5 rounded-full text-[11px] font-medium">
            {filteredChats.length}
          </span>
        </div>
      )}

      {/* Folders Bar */}
      {folders.length > 1 && (
        <div className="flex items-center gap-1 px-2.5 py-1.5 border-b border-[#101921] overflow-x-auto no-scrollbar text-xs">
          {folders.map((f) => {
            const isActive = activeFolderId === f.id;
            return (
              <button
                key={f.id}
                onClick={() => setActiveFolderId(f.id)}
                className={`px-3 py-1.5 rounded-full whitespace-nowrap font-medium transition-all ${
                  isActive
                    ? 'bg-[#2481cc] text-white shadow-xs'
                    : 'text-[#708499] hover:text-white hover:bg-white/5'
                }`}
              >
                {isArabic ? f.nameAr || f.name : f.name}
              </button>
            );
          })}
        </div>
      )}

      {/* Dialogs List */}
      <div className="flex-1 overflow-y-auto">
        {filteredChats.length === 0 ? (
          <div className="p-8 text-center text-[#708499] text-sm">
            {searchQuery
              ? isArabic ? 'لا توجد نتائج' : 'No chats found'
              : isArabic ? 'لا توجد محادثات نشطة' : 'No active conversations'}
          </div>
        ) : (
          filteredChats.map((chat) => {
            const isSelected = activeChatId === chat.id;
            const isSaved = chat.type === 'saved';
            const isTyping = typingChatId === chat.id;

            const lastMsg = typeof chat.lastMessage === 'object' ? chat.lastMessage : null;
            const lastMsgText = typeof chat.lastMessage === 'string'
              ? chat.lastMessage
              : lastMsg?.text || '';
            const lastMsgTime = lastMsg?.timestamp || '';
            const isOutgoing = lastMsg?.isOutgoing;
            const isRead = lastMsg?.status === 'read';

            return (
              <div
                key={chat.id}
                onClick={() => setActiveChatId(chat.id)}
                onContextMenu={(e) => {
                  e.preventDefault();
                  setChatContextMenu({
                    chatId: chat.id,
                    x: e.clientX,
                    y: e.clientY,
                  });
                }}
                className={`flex items-center gap-3 px-3 py-2.5 cursor-pointer transition-colors border-b border-[#101921]/60 ${
                  isSelected ? 'bg-[#2b5278]' : 'hover:bg-[#202b36]'
                }`}
              >
                {/* Avatar */}
                <div className="relative shrink-0">
                  <ChatAvatarItem chat={chat} isSaved={isSaved} />
                  {chat.isOnline && !isSaved && (
                    <span className="absolute bottom-0 right-0 rtl:right-auto rtl:left-0 w-3.5 h-3.5 bg-[#4fae4e] border-2 border-[#17212b] rounded-full" />
                  )}
                </div>

                {/* Info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-1 min-w-0 pr-1 rtl:pr-0 rtl:pl-1">
                      {chat.isSecret && (
                        <Lock className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                      )}
                      <h4 className="font-semibold text-[14.5px] truncate text-white leading-tight">
                        {isSaved ? (
                          <HighlightMatch
                            text={isArabic ? 'الرسائل المحفوظة' : 'Saved Messages'}
                            query={searchQuery}
                          />
                        ) : (
                          <HighlightMatch text={chat.title} query={searchQuery} />
                        )}
                      </h4>
                      {chat.username && searchQuery.trim() && (
                        <span className="text-[11px] text-[#2481cc] truncate font-normal">
                          @<HighlightMatch text={chat.username} query={searchQuery} />
                        </span>
                      )}
                      {chat.isVerified && (
                        <BadgeCheck className="w-3.5 h-3.5 text-[#2481cc] fill-[#2481cc]/20 shrink-0" />
                      )}
                      {chat.isMuted && (
                        <VolumeX className="w-3 h-3 text-[#708499] shrink-0" />
                      )}
                    </div>
                    <span
                      className={`text-xs shrink-0 font-normal ${
                        isSelected ? 'text-[#8daecf]' : 'text-[#708499]'
                      }`}
                    >
                      {lastMsgTime}
                    </span>
                  </div>

                  <div className="flex items-center justify-between mt-1">
                    <div className="flex items-center gap-1 min-w-0 pr-2 rtl:pr-0 rtl:pl-2">
                      {/* Outgoing read receipt */}
                      {isOutgoing && (
                        <span className="shrink-0">
                          {isRead ? (
                            <CheckCheck
                              className={`w-3.5 h-3.5 ${
                                isSelected ? 'text-[#8daecf]' : 'text-[#4fae4e]'
                              }`}
                            />
                          ) : (
                            <Check
                              className={`w-3.5 h-3.5 ${
                                isSelected ? 'text-[#8daecf]' : 'text-[#708499]'
                              }`}
                            />
                          )}
                        </span>
                      )}

                      {/* Content Preview */}
                      {isTyping ? (
                        <span className="text-xs text-[#2481cc] font-medium animate-pulse truncate">
                          {isArabic ? 'يكتب الآن...' : 'typing...'}
                        </span>
                      ) : chat.draft ? (
                        <p className="text-xs truncate">
                          <span className="text-[#e17076] font-medium">
                            {isArabic ? 'مسودة: ' : 'Draft: '}
                          </span>
                          <span className={isSelected ? 'text-[#a0b9d1]' : 'text-[#708499]'}>
                            <HighlightMatch text={chat.draft} query={searchQuery} />
                          </span>
                        </p>
                      ) : (
                        <p
                          className={`text-xs truncate ${
                            isSelected ? 'text-[#a0b9d1]' : 'text-[#708499]'
                          }`}
                        >
                          {lastMsgText ? (
                            <HighlightMatch text={lastMsgText} query={searchQuery} />
                          ) : (
                            isArabic ? 'لا توجد رسائل' : 'No messages yet'
                          )}
                        </p>
                      )}
                    </div>

                    {/* Right side indicators (Pin & Unread Badge) */}
                    <div className="flex items-center gap-1 shrink-0">
                      {chat.isPinned && (
                        <Pin
                          className={`w-3.5 h-3.5 -rotate-45 ${
                            isSelected ? 'text-[#8daecf]' : 'text-[#708499]'
                          }`}
                        />
                      )}
                      {chat.unreadCount > 0 && (
                        <span
                          className={`text-xs px-2 py-0.5 rounded-full font-bold min-w-[20px] text-center shadow-xs ${
                            chat.isMuted
                              ? 'bg-[#3d4c5c] text-gray-200'
                              : 'bg-[#2481cc] text-white'
                          }`}
                        >
                          {chat.unreadCount}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Floating Action Button for New Chat */}
      <button
        onClick={() => setActiveModal('new-chat' as any)}
        className="absolute bottom-5 right-5 rtl:right-auto rtl:left-5 z-20 w-13 h-13 rounded-full bg-[#2481cc] hover:bg-[#1d6fa5] text-white flex items-center justify-center shadow-xl shadow-black/40 transition-transform active:scale-95"
        title={isArabic ? 'محادثة جديدة' : 'New Chat'}
      >
        <Plus className="w-6 h-6" />
      </button>
    </aside>
  );
};
