import React from 'react';
import { X, MessageSquare } from 'lucide-react';
import { useTelegram } from '../../context/TelegramContext';

export const MyMessagesModal: React.FC = () => {
  const { activeModal, setActiveModal, settings } = useTelegram();
  const isArabic = settings.language === 'ar';
  if (activeModal !== ('my-messages' as any)) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60">
      <div className="bg-[#17212b] text-white rounded-xl max-w-sm w-full p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="font-semibold">{isArabic ? 'رسائلي المجدولة' : 'Scheduled Messages'}</h3>
          <button onClick={() => setActiveModal('none')}><X className="w-5 h-5 text-gray-400" /></button>
        </div>
        <p className="text-xs text-gray-400 mb-4">{isArabic ? 'إدارة الرسائل المجدولة والتلقائية' : 'Manage scheduled & automated messages'}</p>
        <button onClick={() => setActiveModal('none')} className="w-full bg-[#2481cc] py-2 rounded-lg text-sm">{isArabic ? 'إغلاق' : 'Close'}</button>
      </div>
    </div>
  );
};
