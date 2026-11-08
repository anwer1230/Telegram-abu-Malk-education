import React from 'react';
import { X, Lock, ShieldCheck, Zap } from 'lucide-react';
import { useTelegram } from '../../context/TelegramContext';

export const SecretChatInfoModal: React.FC = () => {
  const { activeModal, setActiveModal, settings } = useTelegram();
  const isArabic = settings.language === 'ar';

  if (activeModal !== ('secret-chat-info' as any)) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60">
      <div className="bg-[#17212b] text-white rounded-xl max-w-sm w-full shadow-2xl border border-[#242f3d] p-6 text-center">
        <div className="flex justify-end">
          <button onClick={() => setActiveModal('none')} className="text-gray-400 hover:text-white">
            <X className="w-5 h-5" />
          </button>
        </div>
        <Lock className="w-12 h-12 text-[#4fae4e] mx-auto mb-3" />
        <h3 className="text-lg font-bold mb-2">{isArabic ? 'محادثة سرية مشفرة' : 'Secret Chat Encryption'}</h3>
        <p className="text-xs text-gray-400 mb-6 leading-relaxed">
          {isArabic
            ? 'تستخدم المحادثات السرية التشفير من طرف لطرف مع مفاتيح Diffie-Hellman وتدمير ذاتي للرسائل.'
            : 'Secret chats use end-to-end encryption with Diffie-Hellman keys and self-destruct timers.'}
        </p>
        <button
          onClick={() => setActiveModal('none')}
          className="w-full bg-[#2481cc] py-2 rounded-lg text-sm font-medium"
        >
          {isArabic ? 'إغلاق' : 'Close'}
        </button>
      </div>
    </div>
  );
};
