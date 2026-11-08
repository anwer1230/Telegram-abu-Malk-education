import React from 'react';
import { X, Send } from 'lucide-react';
import { useTelegram } from '../../context/TelegramContext';

export const SendOnlyModal: React.FC = () => {
  const { activeModal, setActiveModal, settings } = useTelegram();
  const isArabic = settings.language === 'ar';

  if (activeModal !== ('send-only' as any)) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60">
      <div className="bg-[#17212b] text-white rounded-xl max-w-sm w-full shadow-2xl border border-[#242f3d] overflow-hidden p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold">{isArabic ? 'إرسال سريع' : 'Quick Send'}</h3>
          <button onClick={() => setActiveModal('none')} className="text-gray-400 hover:text-white">
            <X className="w-5 h-5" />
          </button>
        </div>
        <p className="text-sm text-gray-400 mb-4">{isArabic ? 'إرسال رسائل متعددة للقنوات' : 'Broadcast to multiple channels'}</p>
        <button
          onClick={() => setActiveModal('none')}
          className="w-full bg-[#2481cc] py-2 rounded-lg text-sm font-medium"
        >
          {isArabic ? 'تم' : 'Done'}
        </button>
      </div>
    </div>
  );
};
