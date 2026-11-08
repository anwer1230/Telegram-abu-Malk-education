import React from 'react';
import { Pin, X } from 'lucide-react';
import { useTelegram } from '../../context/TelegramContext';

export const PinnedMessageBar: React.FC = () => {
  const { activeChat, activeChatId, messages, pinMessage, settings } = useTelegram();

  if (!activeChatId || !activeChat) return null;

  const currentMessages = messages[activeChatId] || [];
  const pinnedMessages = currentMessages.filter((m) => m.isPinned);

  if (pinnedMessages.length === 0) return null;

  // Most recent pinned message
  const pinned = pinnedMessages[pinnedMessages.length - 1];
  const isArabic = settings.language === 'ar';

  const handleScrollToMessage = () => {
    const el = document.getElementById(`msg-bubble-container-${pinned.id}`);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'center' });
      el.classList.add('ring-2', 'ring-[#2481cc]', 'bg-[#2481cc]/20');
      setTimeout(() => {
        el.classList.remove('ring-2', 'ring-[#2481cc]', 'bg-[#2481cc]/20');
      }, 1500);
    }
  };

  return (
    <div
      id="tg-pinned-message-bar"
      onClick={handleScrollToMessage}
      className="h-10 px-3 flex items-center justify-between border-b cursor-pointer transition-colors hover:bg-black/5 select-none z-10 shrink-0"
      style={{
        backgroundColor: 'var(--tg-theme-surface)',
        borderColor: 'var(--tg-theme-border)',
      }}
    >
      <div className="flex items-center gap-2.5 min-w-0 flex-1">
        {/* Accent Bar */}
        <div className="w-0.5 h-6 rounded-full bg-[#2481cc] shrink-0" />

        <Pin className="w-3.5 h-3.5 text-[#2481cc] shrink-0" />

        <div className="min-w-0 flex-1 text-xs">
          <div className="font-bold text-[#2481cc] text-[11px] leading-none mb-0.5 truncate">
            {isArabic ? 'رسالة مثبتة' : 'Pinned Message'}
          </div>
          <div className="text-gray-400 text-[11px] truncate leading-tight">
            {pinned.text || (pinned.media ? `[${pinned.media.type}]` : 'Media')}
          </div>
        </div>
      </div>

      <button
        onClick={(e) => {
          e.stopPropagation();
          pinMessage(pinned.id);
        }}
        className="p-1 rounded-full text-gray-400 hover:text-white hover:bg-white/10 shrink-0 transition-colors"
        title={isArabic ? 'إلغاء التثبيت' : 'Unpin'}
      >
        <X className="w-3.5 h-3.5" />
      </button>
    </div>
  );
};
