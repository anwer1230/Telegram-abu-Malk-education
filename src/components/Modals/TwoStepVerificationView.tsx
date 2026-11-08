import React, { useState } from 'react';
import { ArrowLeft, ShieldCheck, Lock, Check } from 'lucide-react';
import { useTelegram } from '../../context/TelegramContext';

interface TwoStepVerificationViewProps {
  onBack: () => void;
}

export const TwoStepVerificationView: React.FC<TwoStepVerificationViewProps> = ({ onBack }) => {
  const { settings, showToast } = useTelegram();
  const isArabic = settings.language === 'ar';
  const [password, setPassword] = useState('');
  const [hint, setHint] = useState('');
  const [isSaved, setIsSaved] = useState(false);

  const handleSave = () => {
    if (!password) {
      showToast(isArabic ? 'يرجى إدخال كلمة المرور' : 'Please enter a password', 'info');
      return;
    }
    setIsSaved(true);
    showToast(isArabic ? 'تم تفعيل التحقق بخطوتين بنجاح' : 'Two-Step Verification activated', 'success');
  };

  return (
    <div className="flex flex-col h-full bg-[#17212b] text-white">
      <div className="flex items-center gap-3 p-4 border-b border-[#242f3d]">
        <button onClick={onBack} className="p-1 rounded-full hover:bg-white/10 transition-colors">
          <ArrowLeft className="w-5 h-5 text-gray-300" />
        </button>
        <h2 className="text-lg font-medium">
          {isArabic ? 'التحقق بخطوتين (2FA)' : 'Two-Step Verification'}
        </h2>
      </div>

      <div className="p-6 max-w-md mx-auto flex flex-col items-center text-center">
        <div className="w-16 h-16 rounded-full bg-[#2481cc]/20 flex items-center justify-center mb-4 text-[#2481cc]">
          <ShieldCheck className="w-8 h-8" />
        </div>
        <h3 className="text-xl font-bold mb-2">
          {isArabic ? 'حماية إضافية لحسابك' : 'Extra Protection for Your Account'}
        </h3>
        <p className="text-sm text-gray-400 mb-6">
          {isArabic
            ? 'يمكنك تعيين كلمة مرور إضافية سيطلبها التطبيق عند تسجيل الدخول من جهاز جديد.'
            : 'You can set an additional password that will be required when you log in on a new device.'}
        </p>

        <div className="w-full space-y-4 text-left">
          <div>
            <label className="text-xs text-gray-400 mb-1 block">
              {isArabic ? 'كلمة المرور الإضافية' : 'Additional Password'}
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full bg-[#0e1621] border border-[#242f3d] rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-[#2481cc]"
            />
          </div>

          <div>
            <label className="text-xs text-gray-400 mb-1 block">
              {isArabic ? 'تلميح كلمة المرور (اختياري)' : 'Password Hint (Optional)'}
            </label>
            <input
              type="text"
              value={hint}
              onChange={(e) => setHint(e.target.value)}
              placeholder={isArabic ? 'تلميح للتذكير' : 'A hint to remember'}
              className="w-full bg-[#0e1621] border border-[#242f3d] rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-[#2481cc]"
            />
          </div>

          <button
            onClick={handleSave}
            className="w-full mt-4 bg-[#2481cc] hover:bg-[#1d6fa5] text-white font-medium py-2.5 rounded-lg flex items-center justify-center gap-2 transition-colors"
          >
            {isSaved ? <Check className="w-5 h-5" /> : <Lock className="w-5 h-5" />}
            {isSaved
              ? isArabic ? 'مُفعّل' : 'Active'
              : isArabic ? 'تعيين كلمة المرور' : 'Set Password'}
          </button>
        </div>
      </div>
    </div>
  );
};
