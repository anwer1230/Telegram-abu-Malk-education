import React, { useState } from 'react';
import { ArrowLeft, Check, Smartphone, Trash2, UserX, Lock } from 'lucide-react';
import { useTelegram } from '../../context/TelegramContext';
import { PrivacyTarget } from '../../core/messenger/PrivacySettingsController';

interface SubViewProps {
  onBack: () => void;
}

export const PrivacyControlView: React.FC<SubViewProps & { target: PrivacyTarget }> = ({ onBack, target }) => {
  const { settings, showToast } = useTelegram();
  const isArabic = settings.language === 'ar';
  const [rule, setRule] = useState<'everybody' | 'contacts' | 'nobody'>('everybody');

  return (
    <div className="flex flex-col h-full bg-[#17212b] text-white">
      <div className="flex items-center gap-3 p-4 border-b border-[#242f3d]">
        <button onClick={onBack} className="p-1 rounded-full hover:bg-white/10 transition-colors">
          <ArrowLeft className="w-5 h-5 text-gray-300" />
        </button>
        <h2 className="text-lg font-medium capitalize">{target.replace('_', ' ')}</h2>
      </div>
      <div className="p-4 space-y-2">
        <p className="text-xs text-gray-400 mb-2">
          {isArabic ? 'من يستطيع رؤية هذه المعلومة؟' : 'Who can see this information?'}
        </p>
        {(['everybody', 'contacts', 'nobody'] as const).map((opt) => (
          <button
            key={opt}
            onClick={() => {
              setRule(opt);
              showToast(isArabic ? 'تم تحديث الإعداد' : 'Setting updated', 'success');
            }}
            className="w-full flex items-center justify-between p-3 rounded-lg bg-[#242f3d]/40 hover:bg-[#242f3d] transition-colors"
          >
            <span className="capitalize">{opt}</span>
            {rule === opt && <Check className="w-4 h-4 text-[#2481cc]" />}
          </button>
        ))}
      </div>
    </div>
  );
};

export const PasscodeLockView: React.FC<SubViewProps> = ({ onBack }) => {
  const { settings, showToast } = useTelegram();
  const isArabic = settings.language === 'ar';
  const [passcode, setPasscode] = useState('');

  return (
    <div className="flex flex-col h-full bg-[#17212b] text-white">
      <div className="flex items-center gap-3 p-4 border-b border-[#242f3d]">
        <button onClick={onBack} className="p-1 rounded-full hover:bg-white/10 transition-colors">
          <ArrowLeft className="w-5 h-5 text-gray-300" />
        </button>
        <h2 className="text-lg font-medium">{isArabic ? 'قفل الرمز السري' : 'Passcode Lock'}</h2>
      </div>
      <div className="p-6 max-w-sm mx-auto w-full text-center">
        <Lock className="w-12 h-12 mx-auto mb-4 text-[#2481cc]" />
        <p className="text-sm text-gray-400 mb-4">
          {isArabic ? 'عيّن رمز قفل لحماية التطبيق عند تركه' : 'Set a passcode to lock the app when left unattended'}
        </p>
        <input
          type="password"
          maxLength={6}
          value={passcode}
          onChange={(e) => setPasscode(e.target.value)}
          placeholder="••••"
          className="w-full text-center tracking-widest text-2xl bg-[#0e1621] border border-[#242f3d] rounded-lg py-3 text-white mb-4 focus:outline-none focus:border-[#2481cc]"
        />
        <button
          onClick={() => {
            if (passcode.length >= 4) {
              showToast(isArabic ? 'تم حفظ الرمز السري' : 'Passcode saved', 'success');
              onBack();
            }
          }}
          className="w-full bg-[#2481cc] py-2.5 rounded-lg font-medium text-white hover:bg-[#1d6fa5] transition-colors"
        >
          {isArabic ? 'حفظ الرمز' : 'Save Passcode'}
        </button>
      </div>
    </div>
  );
};

export const AutoDeleteView: React.FC<SubViewProps> = ({ onBack }) => {
  const { settings, showToast } = useTelegram();
  const isArabic = settings.language === 'ar';

  return (
    <div className="flex flex-col h-full bg-[#17212b] text-white">
      <div className="flex items-center gap-3 p-4 border-b border-[#242f3d]">
        <button onClick={onBack} className="p-1 rounded-full hover:bg-white/10 transition-colors">
          <ArrowLeft className="w-5 h-5 text-gray-300" />
        </button>
        <h2 className="text-lg font-medium">{isArabic ? 'الحذف التلقائي للرسائل' : 'Auto-Delete Messages'}</h2>
      </div>
      <div className="p-4 space-y-2">
        {['Off', '1 Day', '1 Week', '1 Month'].map((period) => (
          <button
            key={period}
            onClick={() => {
              showToast(isArabic ? `تم ضبط الحذف التلقائي: ${period}` : `Auto-delete set to: ${period}`, 'success');
              onBack();
            }}
            className="w-full flex items-center justify-between p-3 rounded-lg bg-[#242f3d]/40 hover:bg-[#242f3d] transition-colors"
          >
            <span>{period}</span>
          </button>
        ))}
      </div>
    </div>
  );
};

export const SessionsView: React.FC<SubViewProps> = ({ onBack }) => {
  const { settings, showToast } = useTelegram();
  const isArabic = settings.language === 'ar';

  return (
    <div className="flex flex-col h-full bg-[#17212b] text-white">
      <div className="flex items-center gap-3 p-4 border-b border-[#242f3d]">
        <button onClick={onBack} className="p-1 rounded-full hover:bg-white/10 transition-colors">
          <ArrowLeft className="w-5 h-5 text-gray-300" />
        </button>
        <h2 className="text-lg font-medium">{isArabic ? 'الأجهزة والجلسات النشطة' : 'Active Devices & Sessions'}</h2>
      </div>
      <div className="p-4 space-y-4">
        <div className="p-4 rounded-lg bg-[#242f3d]/60 border border-[#242f3d]">
          <div className="flex items-center gap-3">
            <Smartphone className="w-6 h-6 text-[#4fae4e]" />
            <div>
              <p className="text-sm font-medium">{isArabic ? 'هذا الجهاز (الجلسة الحالية)' : 'This Device (Current Session)'}</p>
              <p className="text-xs text-gray-400">Web / Android Client • IP: Online</p>
            </div>
          </div>
        </div>
        <button
          onClick={() => showToast(isArabic ? 'تم إنهاء جميع الجلسات الأخرى' : 'All other sessions terminated', 'info')}
          className="w-full p-3 rounded-lg bg-red-500/20 text-red-400 hover:bg-red-500/30 flex items-center justify-center gap-2 transition-colors font-medium text-sm"
        >
          <Trash2 className="w-4 h-4" />
          {isArabic ? 'إنهاء كافة الجلسات الأخرى' : 'Terminate All Other Sessions'}
        </button>
      </div>
    </div>
  );
};

export const BlockedUsersView: React.FC<SubViewProps> = ({ onBack }) => {
  const { settings } = useTelegram();
  const isArabic = settings.language === 'ar';

  return (
    <div className="flex flex-col h-full bg-[#17212b] text-white">
      <div className="flex items-center gap-3 p-4 border-b border-[#242f3d]">
        <button onClick={onBack} className="p-1 rounded-full hover:bg-white/10 transition-colors">
          <ArrowLeft className="w-5 h-5 text-gray-300" />
        </button>
        <h2 className="text-lg font-medium">{isArabic ? 'المستخدمون المحظورون' : 'Blocked Users'}</h2>
      </div>
      <div className="p-8 text-center text-gray-400 flex flex-col items-center">
        <UserX className="w-12 h-12 mb-3 opacity-40" />
        <p className="text-sm">{isArabic ? 'لا توجد حسابات محظورة' : 'No blocked users found'}</p>
      </div>
    </div>
  );
};
