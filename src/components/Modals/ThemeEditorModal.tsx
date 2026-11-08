import React from 'react';
import { X, Palette, Check } from 'lucide-react';
import { useTelegram } from '../../context/TelegramContext';

interface ThemeEditorModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const ThemeEditorModal: React.FC<ThemeEditorModalProps> = ({ isOpen, onClose }) => {
  const { settings, updateSettings } = useTelegram();
  const isArabic = settings.language === 'ar';

  if (!isOpen) return null;

  const colors = ['#2481cc', '#4fae4e', '#e53935', '#8e24aa', '#fb8c00', '#00acc1'];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60">
      <div className="bg-[#17212b] text-white rounded-xl max-w-sm w-full shadow-2xl border border-[#242f3d] overflow-hidden">
        <div className="flex items-center justify-between p-4 border-b border-[#242f3d]">
          <h3 className="font-semibold text-base">{isArabic ? 'محرر المظهر' : 'Theme Editor'}</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-white">
            <X className="w-5 h-5" />
          </button>
        </div>
        <div className="p-6">
          <p className="text-xs text-gray-400 mb-3">{isArabic ? 'اختر لون التمييز' : 'Select Accent Color'}</p>
          <div className="flex items-center gap-3">
            {colors.map((c) => (
              <button
                key={c}
                onClick={() => updateSettings({ accentColor: c })}
                style={{ backgroundColor: c }}
                className="w-9 h-9 rounded-full flex items-center justify-center shadow transition-transform hover:scale-110"
              >
                {settings.accentColor === c && <Check className="w-5 h-5 text-white" />}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
