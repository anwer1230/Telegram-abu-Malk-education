import React, { useState, useEffect } from 'react';
import { ExternalLink, Copy, Check, ShieldAlert, X } from 'lucide-react';
import { useTelegram } from '../../context/TelegramContext';

export interface UrlConfirmData {
  url: string;
  display?: string;
}

export const UrlConfirmModal: React.FC = () => {
  const { settings, showToast } = useTelegram();
  const [data, setData] = useState<UrlConfirmData | null>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    const handleOpen = (e: CustomEvent<UrlConfirmData>) => {
      setData(e.detail);
      setCopied(false);
    };

    window.addEventListener('tg-open-url-confirm' as any, handleOpen);
    return () => window.removeEventListener('tg-open-url-confirm' as any, handleOpen);
  }, []);

  if (!data) return null;

  const isArabic = settings.language === 'ar';

  const handleCopy = () => {
    if (navigator.clipboard) {
      navigator.clipboard.writeText(data.url);
      setCopied(true);
      showToast(isArabic ? 'تم نسخ الرابط إلى الحافظة' : 'Link copied to clipboard', '📋');
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleProceed = () => {
    window.open(data.url, '_blank', 'noopener,noreferrer');
    setData(null);
  };

  let hostname = '';
  try {
    hostname = new URL(data.url).hostname;
  } catch {
    hostname = data.url;
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 select-none">
      {/* Backdrop */}
      <div
        onClick={() => setData(null)}
        className="fixed inset-0 bg-black/75 backdrop-blur-xs transition-opacity animate-in fade-in"
      />

      {/* Modal Card */}
      <div
        className="relative w-full max-w-md rounded-2xl shadow-2xl overflow-hidden border z-10 animate-in zoom-in-95 duration-150 flex flex-col p-6 text-center"
        style={{
          backgroundColor: 'var(--tg-theme-surface, #17212b)',
          borderColor: 'var(--tg-theme-border, #242f3d)',
          color: 'var(--tg-theme-bubble-in-text, #ffffff)',
        }}
      >
        {/* Header Icon */}
        <div className="mx-auto w-14 h-14 rounded-2xl bg-amber-500/15 border border-amber-500/30 flex items-center justify-center text-amber-400 mb-4 shadow-inner">
          <ShieldAlert className="w-8 h-8" />
        </div>

        {/* Title */}
        <h3 className="font-bold text-lg mb-1.5">
          {isArabic ? 'تأكيد فتح الرابط الخارجي' : 'Open External Link'}
        </h3>

        {/* Warning text */}
        <p className="text-xs text-gray-300 leading-relaxed mb-4">
          {isArabic
            ? 'هذا الرابط مخفي خلف نص أو زر. تأكد من أنك تثق في الوجهة قبل المتابعة وفقاً لمعايير أمان تليجرام.'
            : 'This link is masked behind text. Please verify the destination before proceeding according to Telegram security standards.'}
        </p>

        {/* Display Text if different */}
        {data.display && data.display !== data.url && (
          <div className="mb-2 text-xs text-left rtl:text-right">
            <span className="text-gray-400">{isArabic ? 'النص المعروض:' : 'Displayed text:'} </span>
            <span className="font-semibold text-white bg-white/10 px-1.5 py-0.5 rounded">
              {data.display}
            </span>
          </div>
        )}

        {/* Target Destination Box */}
        <div className="p-3 rounded-xl bg-black/40 border border-white/10 mb-5 text-left rtl:text-right">
          <div className="text-[10px] text-amber-400 font-bold uppercase tracking-wider mb-1 flex items-center justify-between">
            <span>{hostname}</span>
            <span className="text-gray-400 font-mono">HTTPS</span>
          </div>
          <div className="text-xs font-mono text-sky-300 break-all select-all leading-normal">
            {data.url}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => setData(null)}
            className="flex-1 py-2.5 rounded-xl border border-white/10 bg-white/5 hover:bg-white/10 text-xs font-semibold text-gray-300 transition-colors"
          >
            {isArabic ? 'إلغاء' : 'Cancel'}
          </button>

          <button
            onClick={handleCopy}
            className="p-2.5 rounded-xl border border-white/10 bg-white/5 hover:bg-white/10 text-gray-300 transition-colors"
            title={isArabic ? 'نسخ الرابط' : 'Copy link'}
          >
            {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
          </button>

          <button
            onClick={handleProceed}
            className="flex-1 py-2.5 rounded-xl bg-[#2481cc] hover:bg-[#1c6fad] text-white text-xs font-bold shadow-md flex items-center justify-center gap-1.5 transition-transform active:scale-98"
          >
            <span>{isArabic ? 'فتح الرابط' : 'Open Link'}</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
};
