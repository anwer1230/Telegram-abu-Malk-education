import React from 'react';
import { Send } from 'lucide-react';
import { useTelegram } from '../../context/TelegramContext';
import { ChatHeader } from './ChatHeader';
import { PinnedMessageBar } from './PinnedMessageBar';
import { MessageList } from './MessageList';
import { ChatInput } from './ChatInput';
import { ChatInvitePreview } from './ChatInvitePreview';

export const ChatView: React.FC = () => {
  const { activeChat, activeChatId, settings, previewInvite, setPreviewInvite } = useTelegram();

  const isArabic = settings.language === 'ar';

  if (previewInvite) {
    return (
      <ChatInvitePreview
        invite={previewInvite.invite}
        hash={previewInvite.hash}
        onClose={() => setPreviewInvite(null)}
        onJoined={() => setPreviewInvite(null)}
      />
    );
  }

  if (!activeChatId || !activeChat) {
    return (
      <div
        id="tg-chat-empty-view"
        className="flex-1 hidden md:flex flex-col items-center justify-center p-6 text-center select-none tg-wallpaper-pattern"
        style={{
          backgroundColor: 'var(--tg-theme-chat-bg)',
        }}
      >
        <div
          className="p-8 rounded-3xl max-w-md backdrop-blur-md border shadow-xl flex flex-col items-center gap-3"
          style={{
            backgroundColor: 'var(--tg-theme-surface)',
            borderColor: 'var(--tg-theme-border)',
          }}
        >
          <div className="w-16 h-16 rounded-full bg-[#2481cc]/20 text-[#2481cc] flex items-center justify-center">
            <Send className="w-8 h-8 ml-1 rtl:ml-0 rtl:mr-1" />
          </div>
          <div className="font-bold text-lg" style={{ color: 'var(--tg-theme-bubble-in-text)' }}>
            {isArabic ? 'تيليجرام ويب' : 'Telegram Web Client'}
          </div>
          <p className="text-xs text-gray-400 leading-relaxed">
            {isArabic
              ? 'اختر محادثة من القائمة للبدء بالتراسل، الاستماع للتسجيلات الصوتية، ومشاركة الملفات مع تشفير كامل عبر بروتوكول MTProto 2.0.'
              : 'Select a chat to start messaging, listen to voice notes, and share files with full MTProto 2.0 end-to-end encryption.'}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div
      id="tg-chat-view"
      className="flex-1 flex flex-col h-full overflow-hidden min-w-0"
      style={{
        fontSize: `${settings.fontSize}px`,
      }}
    >
      <ChatHeader />
      <PinnedMessageBar />
      <MessageList />
      <ChatInput />
    </div>
  );
};
