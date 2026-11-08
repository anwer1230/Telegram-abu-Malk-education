import React from 'react';
import { useTelegram } from '../../context/TelegramContext';
import { Bell, X } from 'lucide-react';
import { InAppNotification } from '../../types';

interface InAppNotificationBannerProps {
  notifications?: InAppNotification[];
  onDismiss?: (id: string) => void;
}

export const InAppNotificationBanner: React.FC<InAppNotificationBannerProps> = ({
  notifications,
  onDismiss,
}) => {
  const context = useTelegram();
  const list = notifications || context.inAppNotifications;
  const dismiss = onDismiss || context.dismissNotification;

  if (!list || list.length === 0) return null;
  const current = list[0];

  return (
    <div className="fixed top-4 right-4 z-50 max-w-sm w-full bg-[#242f3d] text-white p-3 rounded-lg shadow-xl border border-[#2b5278] flex items-center gap-3">
      <Bell className="w-5 h-5 text-[#2481cc] shrink-0" />
      <div className="flex-1 min-w-0">
        <p className="text-xs font-semibold truncate">{current.title}</p>
        <p className="text-xs text-gray-300 truncate">{current.body}</p>
      </div>
      <button onClick={() => dismiss(current.id)} className="text-gray-400 hover:text-white">
        <X className="w-4 h-4" />
      </button>
    </div>
  );
};
