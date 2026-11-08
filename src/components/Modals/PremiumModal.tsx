import React from 'react';
import { X, Star, Check } from 'lucide-react';
import { useTelegram } from '../../context/TelegramContext';

export const PremiumModal: React.FC = () => {
  const { activeModal, setActiveModal, settings } = useTelegram();
  const isArabic = settings.language === 'ar';

  if (activeModal !== ('premium' as any)) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60">
      <div className="bg-[#17212b] text-white rounded-xl max-w-md w-full shadow-2xl border border-[#242f3d] overflow-hidden p-6 text-center">
        <div className="flex justify-end">
          <button onClick={() => setActiveModal('none')} className="text-gray-400 hover:text-white">
            <X className="w-5 h-5" />
          </button>
        </div>
        <div className="w-16 h-16 rounded-full bg-amber-500/20 text-amber-400 flex items-center justify-center mx-auto mb-4">
          <Star className="w-8 h-8 fill-current" />
        </div>
        <h3 className="text-xl font-bold mb-2">Telegram Premium</h3>
        <p className="text-sm text-gray-400 mb-6">
          {isArabic ? 'ضاعف حدودك، سرعة تنزيل فائقة، ملصقات تفاعلية والمزيد' : 'Double your limits, ultra-fast downloads, interactive stickers & more'}
        </p>
        <button
          onClick={() => setActiveModal('none')}
          className="w-full bg-[#2481cc] py-2.5 rounded-lg text-sm font-semibold hover:bg-[#1d6fa5] transition-colors"
        >
          {isArabic ? 'حسناً' : 'Got it'}
        </button>
      </div>
    </div>
  );
};
