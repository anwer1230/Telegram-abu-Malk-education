import React from 'react';
import {
  Reply,
  Edit3,
  Share2,
  Copy,
  Pin,
  CheckSquare,
  Trash2,
  SmilePlus,
} from 'lucide-react';
import { useTelegram } from '../../context/TelegramContext';
import { POPULAR_REACTIONS } from '../../data/mockTelegramData';

export const MessageContextMenuView: React.FC = () => {
  const {
    messageContextMenu,
    setMessageContextMenu,
    currentUser,
    setReplyingTo,
    setEditingMessage,
    setForwardingMessage,
    setActiveModal,
    deleteMessage,
    pinMessage,
    toggleReaction,
    toggleSelectMessage,
    showToast,
    settings,
  } = useTelegram();

  if (!messageContextMenu) return null;

  const msg = messageContextMenu.message;
  const isOutgoing = msg.isOutgoing;
  const isArabic = settings.language === 'ar';

  const posX = Math.min(messageContextMenu.x, window.innerWidth - 240);
  const posY = Math.min(messageContextMenu.y, window.innerHeight - 340);

  return (
    <div
      id="tg-msg-context-menu"
      style={{
        left: `${posX}px`,
        top: `${posY}px`,
        backgroundColor: 'var(--tg-theme-surface)',
        borderColor: 'var(--tg-theme-border)',
        color: 'var(--tg-theme-bubble-in-text)',
      }}
      onClick={(e) => e.stopPropagation()}
      className="fixed z-50 w-56 py-2 rounded-2xl shadow-2xl border backdrop-blur-xl animate-in fade-in zoom-in-95 duration-100 text-xs font-semibold select-none"
    >
      {/* Quick Reaction Bar at top of menu */}
      <div className="flex items-center justify-between px-2.5 pb-2 mb-1 border-b border-white/10 overflow-x-auto no-scrollbar">
        {POPULAR_REACTIONS.slice(0, 6).map((emoji) => (
          <button
            key={emoji}
            onClick={() => {
              toggleReaction(msg.id, emoji);
              setMessageContextMenu(null);
            }}
            className="w-7 h-7 flex items-center justify-center text-base hover:scale-130 transition-transform active:scale-95"
          >
            {emoji}
          </button>
        ))}
      </div>

      {/* Reply */}
      <button
        onClick={() => {
          setReplyingTo({
            messageId: msg.id,
            senderName: msg.senderName || (isOutgoing ? currentUser.name : 'User'),
            textSnippet: msg.text || (msg.media ? `[${msg.media.type}]` : ''),
            mediaType: msg.media?.type as 'photo' | 'audio' | 'document' | 'video' | undefined,
          });
          setMessageContextMenu(null);
        }}
        className="w-full flex items-center gap-3 px-3.5 py-2 hover:bg-white/10 text-left rtl:text-right transition-colors"
      >
        <Reply className="w-4 h-4 text-sky-400" />
        <span>{isArabic ? 'رد على الرسالة' : 'Reply'}</span>
      </button>

      {/* Edit (if outgoing) */}
      {isOutgoing && (
        <button
          onClick={() => {
            setEditingMessage({ id: msg.id, text: msg.text });
            setMessageContextMenu(null);
          }}
          className="w-full flex items-center gap-3 px-3.5 py-2 hover:bg-white/10 text-left rtl:text-right transition-colors"
        >
          <Edit3 className="w-4 h-4 text-amber-400" />
          <span>{isArabic ? 'تعديل الرسالة' : 'Edit'}</span>
        </button>
      )}

      {/* Forward */}
      <button
        onClick={() => {
          setForwardingMessage(msg);
          setActiveModal('forward');
          setMessageContextMenu(null);
        }}
        className="w-full flex items-center gap-3 px-3.5 py-2 hover:bg-white/10 text-left rtl:text-right transition-colors"
      >
        <Share2 className="w-4 h-4 text-emerald-400" />
        <span>{isArabic ? 'تحويل الرسالة' : 'Forward'}</span>
      </button>

      {/* Copy */}
      <button
        onClick={() => {
          navigator.clipboard.writeText(msg.text || msg.media?.fileName || '');
          showToast(isArabic ? 'تم نسخ النص إلى الحافظة' : 'Text copied to clipboard', '📋');
          setMessageContextMenu(null);
        }}
        className="w-full flex items-center gap-3 px-3.5 py-2 hover:bg-white/10 text-left rtl:text-right transition-colors"
      >
        <Copy className="w-4 h-4 text-gray-400" />
        <span>{isArabic ? 'نسخ النص' : 'Copy Text'}</span>
      </button>

      {/* Pin */}
      <button
        onClick={() => {
          pinMessage(msg.id);
          setMessageContextMenu(null);
        }}
        className="w-full flex items-center gap-3 px-3.5 py-2 hover:bg-white/10 text-left rtl:text-right transition-colors"
      >
        <Pin className="w-4 h-4 text-sky-400" />
        <span>
          {msg.isPinned
            ? isArabic ? 'إلغاء التثبيت' : 'Unpin Message'
            : isArabic ? 'تثبيت الرسالة' : 'Pin Message'}
        </span>
      </button>

      {/* Select */}
      <button
        onClick={() => {
          toggleSelectMessage(msg.id);
          setMessageContextMenu(null);
        }}
        className="w-full flex items-center gap-3 px-3.5 py-2 hover:bg-white/10 text-left rtl:text-right transition-colors"
      >
        <CheckSquare className="w-4 h-4 text-indigo-400" />
        <span>{isArabic ? 'تحديد' : 'Select'}</span>
      </button>

      <div className="my-1 border-t border-white/10" />

      {/* Delete */}
      <button
        onClick={() => {
          deleteMessage(msg.id);
          setMessageContextMenu(null);
        }}
        className="w-full flex items-center gap-3 px-3.5 py-2 hover:bg-white/10 text-rose-400 text-left rtl:text-right transition-colors"
      >
        <Trash2 className="w-4 h-4" />
        <span>{isArabic ? 'حذف الرسالة' : 'Delete'}</span>
      </button>
    </div>
  );
};
