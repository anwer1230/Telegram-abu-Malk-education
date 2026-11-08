import React from 'react';
import {
  Pin,
  VolumeX,
  Volume2,
  CheckCheck,
  Mail,
  Trash2,
  Eraser,
  Bookmark,
  Share2,
} from 'lucide-react';
import { useTelegram } from '../../context/TelegramContext';

export const ChatContextMenuView: React.FC = () => {
  const {
    chatContextMenu,
    setChatContextMenu,
    chats,
    togglePinChat,
    toggleMuteChat,
    markChatReadUnread,
    clearChatHistory,
    deleteChat,
    showToast,
    settings,
  } = useTelegram();

  if (!chatContextMenu) return null;

  const chat = chats.find((c) => c.id === chatContextMenu.chatId);
  if (!chat) return null;

  const isArabic = settings.language === 'ar';

  // Constrain position to screen viewport
  const posX = Math.min(chatContextMenu.x, window.innerWidth - 220);
  const posY = Math.min(chatContextMenu.y, window.innerHeight - 260);

  return (
    <div
      id="tg-chat-context-menu"
      style={{
        left: `${posX}px`,
        top: `${posY}px`,
        backgroundColor: 'var(--tg-theme-surface)',
        borderColor: 'var(--tg-theme-border)',
        color: 'var(--tg-theme-bubble-in-text)',
      }}
      onClick={(e) => e.stopPropagation()}
      className="fixed z-50 w-52 py-1.5 rounded-2xl shadow-2xl border backdrop-blur-xl animate-in fade-in zoom-in-95 duration-100 text-xs font-semibold select-none"
    >
      {/* Pin / Unpin */}
      <button
        onClick={() => {
          togglePinChat(chat.id);
          setChatContextMenu(null);
        }}
        className="w-full flex items-center gap-3 px-3.5 py-2 hover:bg-white/10 text-left rtl:text-right transition-colors"
      >
        <Pin className="w-4 h-4 text-sky-400" />
        <span>
          {chat.isPinned
            ? isArabic ? 'إلغاء التثبيت' : 'Unpin from Top'
            : isArabic ? 'تثبيت في الأعلى' : 'Pin to Top'}
        </span>
      </button>

      {/* Mute / Unmute */}
      <button
        onClick={() => {
          toggleMuteChat(chat.id);
          setChatContextMenu(null);
        }}
        className="w-full flex items-center gap-3 px-3.5 py-2 hover:bg-white/10 text-left rtl:text-right transition-colors"
      >
        {chat.isMuted ? (
          <>
            <Volume2 className="w-4 h-4 text-emerald-400" />
            <span>{isArabic ? 'إلغاء كتم الصوت' : 'Unmute Notifications'}</span>
          </>
        ) : (
          <>
            <VolumeX className="w-4 h-4 text-amber-400" />
            <span>{isArabic ? 'كتم الإشعارات' : 'Mute Notifications'}</span>
          </>
        )}
      </button>

      {/* Mark as read / unread */}
      <button
        onClick={() => {
          markChatReadUnread(chat.id);
          setChatContextMenu(null);
        }}
        className="w-full flex items-center gap-3 px-3.5 py-2 hover:bg-white/10 text-left rtl:text-right transition-colors"
      >
        {chat.unreadCount > 0 ? (
          <>
            <CheckCheck className="w-4 h-4 text-sky-400" />
            <span>{isArabic ? 'تحديد كمقروء' : 'Mark as Read'}</span>
          </>
        ) : (
          <>
            <Mail className="w-4 h-4 text-sky-400" />
            <span>{isArabic ? 'تحديد كغير مقروء' : 'Mark as Unread'}</span>
          </>
        )}
      </button>

      {/* Copy link */}
      {chat.username && (
        <button
          onClick={() => {
            navigator.clipboard.writeText(`https://t.me/${chat.username}`);
            showToast(isArabic ? 'تم نسخ رابط المحادثة' : 'Chat link copied', '🔗');
            setChatContextMenu(null);
          }}
          className="w-full flex items-center gap-3 px-3.5 py-2 hover:bg-white/10 text-left rtl:text-right transition-colors"
        >
          <Share2 className="w-4 h-4 text-gray-400" />
          <span>{isArabic ? 'نسخ الرابط' : 'Copy Link'}</span>
        </button>
      )}

      <div className="my-1 border-t border-white/10" />

      {/* Clear History */}
      <button
        onClick={() => {
          clearChatHistory(chat.id);
          setChatContextMenu(null);
        }}
        className="w-full flex items-center gap-3 px-3.5 py-2 hover:bg-white/10 text-amber-400 text-left rtl:text-right transition-colors"
      >
        <Eraser className="w-4 h-4" />
        <span>{isArabic ? 'مسح سجل الرسائل' : 'Clear History'}</span>
      </button>

      {/* Delete Chat */}
      <button
        onClick={() => {
          deleteChat(chat.id);
          setChatContextMenu(null);
        }}
        className="w-full flex items-center gap-3 px-3.5 py-2 hover:bg-white/10 text-rose-400 text-left rtl:text-right transition-colors"
      >
        <Trash2 className="w-4 h-4" />
        <span>{isArabic ? 'حذف المحادثة' : 'Delete Chat'}</span>
      </button>
    </div>
  );
};
