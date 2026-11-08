import React, { useState } from 'react';
import { X, Search, Send, Bookmark, BadgeCheck, Users, Megaphone, Bot } from 'lucide-react';
import { useTelegram } from '../../context/TelegramContext';

export const ForwardModal: React.FC = () => {
  const {
    activeModal,
    setActiveModal,
    forwardingMessage,
    setForwardingMessage,
    chats,
    forwardMessageTo,
    settings,
  } = useTelegram();

  const [search, setSearch] = useState('');

  if (activeModal !== 'forward' || !forwardingMessage) return null;

  const isArabic = settings.language === 'ar';

  const filteredChats = chats.filter((c) =>
    c.title.toLowerCase().includes(search.toLowerCase()) ||
    c.username?.toLowerCase().includes(search.toLowerCase())
  );

  const handleSelectChat = (chatId: string) => {
    forwardMessageTo(chatId, forwardingMessage);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 select-none">
      {/* Backdrop */}
      <div
        onClick={() => {
          setActiveModal('none');
          setForwardingMessage(null);
        }}
        className="fixed inset-0 bg-black/75 backdrop-blur-xs transition-opacity animate-in fade-in"
      />

      {/* Dialog */}
      <div
        className="relative w-full max-w-md rounded-2xl shadow-2xl overflow-hidden border z-10 animate-in zoom-in-95 duration-150 flex flex-col max-h-[85vh]"
        style={{
          backgroundColor: 'var(--tg-theme-surface)',
          borderColor: 'var(--tg-theme-border)',
          color: 'var(--tg-theme-bubble-in-text)',
        }}
      >
        {/* Header */}
        <div className="p-4 bg-gradient-to-r from-[#2481cc] to-[#1c6fad] text-white flex items-center justify-between">
          <div>
            <div className="font-bold text-base">
              {isArabic ? 'تحويل الرسالة إلى...' : 'Forward message to...'}
            </div>
            <div className="text-xs text-white/80 truncate max-w-xs">
              "{forwardingMessage.text || forwardingMessage.media?.type || 'Media'}"
            </div>
          </div>
          <button
            onClick={() => {
              setActiveModal('none');
              setForwardingMessage(null);
            }}
            className="p-1 rounded-full hover:bg-white/20 text-white"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Search */}
        <div className="p-3 border-b border-white/10">
          <div className="relative flex items-center">
            <Search className="absolute left-3 w-4 h-4 text-gray-400 rtl:left-auto rtl:right-3" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder={isArabic ? 'البحث عن محادثة...' : 'Search recipient...'}
              className="w-full py-1.5 pl-9 pr-3 rounded-full bg-black/20 border border-white/10 text-xs focus:border-[#2481cc] focus:outline-none rtl:pl-3 rtl:pr-9"
            />
          </div>
        </div>

        {/* Chat List */}
        <div className="flex-1 overflow-y-auto p-2 divide-y divide-white/5">
          {filteredChats.map((chat) => (
            <button
              key={chat.id}
              onClick={() => handleSelectChat(chat.id)}
              className="w-full flex items-center gap-3 p-2.5 rounded-xl hover:bg-white/5 transition-colors text-left rtl:text-right"
            >
              <div className="w-10 h-10 rounded-full overflow-hidden flex items-center justify-center bg-gradient-to-tr from-sky-600 to-cyan-500 text-white font-bold text-sm shrink-0">
                {chat.type === 'saved' ? (
                  <Bookmark className="w-5 h-5 fill-white text-white" />
                ) : chat.avatar ? (
                  <img
                    src={chat.avatar}
                    alt={chat.title}
                    className="w-full h-full object-cover"
                    referrerPolicy="no-referrer"
                  />
                ) : (
                  <span>{chat.title.charAt(0)}</span>
                )}
              </div>

              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-1 font-semibold text-xs truncate">
                  <span>{chat.title}</span>
                  {chat.isVerified && (
                    <BadgeCheck className="w-3.5 h-3.5 text-[#2481cc] shrink-0 fill-[#2481cc]/20" />
                  )}
                </div>
                <div className="text-[10px] text-gray-400 truncate">
                  {chat.username ? `@${chat.username}` : chat.type}
                </div>
              </div>

              <Send className="w-4 h-4 text-[#2481cc] shrink-0 opacity-0 group-hover:opacity-100" />
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
