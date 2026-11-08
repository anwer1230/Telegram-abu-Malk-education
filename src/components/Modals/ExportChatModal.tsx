import React, { useState } from 'react';
import {
  Download,
  X,
  FileText,
  FileCode,
  CheckCircle2,
  Calendar,
  Image,
  MessageSquare,
  ShieldCheck,
  Sparkles,
  ArrowDownToLine,
} from 'lucide-react';
import { useTelegram } from '../../context/TelegramContext';
import confetti from 'canvas-confetti';

interface ExportChatModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const ExportChatModal: React.FC<ExportChatModalProps> = ({ isOpen, onClose }) => {
  const { activeChat, messages, activeChatId, settings, showToast } = useTelegram();
  const isArabic = settings.language === 'ar';

  const [exportFormat, setExportFormat] = useState<'html' | 'json'>('html');
  const [includeMedia, setIncludeMedia] = useState<boolean>(true);
  const [isExporting, setIsExporting] = useState<boolean>(false);

  if (!isOpen || !activeChat || !activeChatId) return null;

  const currentChatMessages = messages[activeChatId] || [];

  const handleStartExport = () => {
    setIsExporting(true);

    setTimeout(() => {
      let fileContent = '';
      let mimeType = 'text/plain';
      let fileName = `Telegram_Export_${activeChat.title.replace(/\s+/g, '_')}_${new Date().toISOString().slice(0, 10)}`;

      if (exportFormat === 'json') {
        mimeType = 'application/json';
        fileName += '.json';
        const exportData = {
          exportType: 'DrKLO_Telegram_Chat_Export',
          chatTitle: activeChat.title,
          chatType: activeChat.type,
          chatId: activeChat.id,
          exportedAt: new Date().toISOString(),
          totalMessages: currentChatMessages.length,
          messages: currentChatMessages.map((m) => ({
            id: m.id,
            date: m.date,
            time: m.timestamp,
            from: m.senderName || 'Anonymous',
            text: m.text,
            isOutgoing: m.isOutgoing,
            media: includeMedia ? m.media : undefined,
          })),
        };
        fileContent = JSON.stringify(exportData, null, 2);
      } else {
        mimeType = 'text/html';
        fileName += '.html';
        fileContent = `<!DOCTYPE html>
<html lang="${isArabic ? 'ar' : 'en'}" dir="${isArabic ? 'rtl' : 'ltr'}">
<head>
  <meta charset="utf-8">
  <title>Telegram Chat History - ${activeChat.title}</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background-color: #0e1621; color: #ffffff; padding: 20px; max-width: 800px; margin: 0 auto; }
    .header { background: #17212b; padding: 16px 20px; border-radius: 16px; margin-bottom: 20px; border: 1px solid #2b394a; }
    .title { font-size: 18px; font-weight: bold; color: #5288c1; }
    .meta { font-size: 12px; color: #8292a1; margin-top: 4px; }
    .message { display: flex; flex-direction: column; margin-bottom: 12px; }
    .bubble { max-width: 75%; padding: 10px 14px; border-radius: 14px; font-size: 14px; line-height: 1.4; }
    .outgoing { align-self: flex-end; background-color: #2b5278; color: #fff; }
    .incoming { align-self: flex-start; background-color: #182533; color: #fff; }
    .sender { font-size: 11px; font-weight: bold; color: #5288c1; margin-bottom: 4px; }
    .time { font-size: 10px; color: #8292a1; text-align: right; margin-top: 4px; }
  </style>
</head>
<body>
  <div class="header">
    <div class="title">Telegram Export: ${activeChat.title}</div>
    <div class="meta">Exported on ${new Date().toLocaleString()} | Protocol: MTProto 2.0 | Total: ${currentChatMessages.length} messages</div>
  </div>
  <div class="chat-container">
    ${currentChatMessages
      .map(
        (m) => `
      <div class="message">
        <div class="bubble ${m.isOutgoing ? 'outgoing' : 'incoming'}">
          ${!m.isOutgoing ? `<div class="sender">${m.senderName || 'Contact'}</div>` : ''}
          <div class="text">${m.text || (m.media ? `[${m.media.type}]` : '')}</div>
          <div class="time">${m.timestamp}</div>
        </div>
      </div>`
      )
      .join('\n')}
  </div>
</body>
</html>`;
      }

      // Trigger download
      const blob = new Blob([fileContent], { type: mimeType });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = fileName;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      setIsExporting(false);
      onClose();

      try {
        confetti({
          particleCount: 45,
          spread: 70,
          origin: { y: 0.6 },
        });
      } catch {}

      showToast(
        isArabic
          ? `تم تصدير محادثة "${activeChat.title}" بنجاح!`
          : `Chat "${activeChat.title}" exported successfully!`,
        '📥'
      );
    }, 800);
  };

  return (
    <div
      id="modal-telegram-export-chat"
      className="fixed inset-0 z-[9990] flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in select-none"
      dir={isArabic ? 'rtl' : 'ltr'}
    >
      <div className="w-full max-w-md bg-[#17212b] border border-white/10 text-white rounded-3xl shadow-2xl overflow-hidden flex flex-col">
        {/* Header */}
        <div className="h-14 px-4 border-b border-white/10 flex items-center justify-between bg-[#1e2c3a]/80 shrink-0">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-sky-500 to-indigo-500 flex items-center justify-center shadow">
              <Download className="w-4 h-4 text-white" />
            </div>
            <div>
              <h3 className="font-bold text-sm text-white">
                {isArabic ? 'تصدير سجل المحادثة (Export Chat)' : 'Export Chat History'}
              </h3>
              <p className="text-[11px] text-gray-400">
                {isArabic ? 'DrKLO messages.exportHistory' : 'JSON, HTML and media backup'}
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-2 rounded-xl text-gray-400 hover:text-white hover:bg-white/10 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-5 space-y-4">
          <div className="p-3 rounded-2xl bg-white/5 border border-white/5 flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-[#2481cc]/20 text-sky-400 flex items-center justify-center font-bold">
              <MessageSquare className="w-5 h-5" />
            </div>
            <div className="min-w-0 flex-1">
              <div className="text-xs font-bold text-white truncate">{activeChat.title}</div>
              <div className="text-[11px] text-gray-400 font-mono">
                {currentChatMessages.length} {isArabic ? 'رسائل متوفرة' : 'messages available'}
              </div>
            </div>
          </div>

          {/* Format selection */}
          <div className="space-y-2">
            <label className="text-xs font-bold text-gray-300">
              {isArabic ? 'صيغة التصدير المطلوبة' : 'Export File Format'}
            </label>
            <div className="grid grid-cols-2 gap-2.5">
              <button
                onClick={() => setExportFormat('html')}
                className={`p-3 rounded-2xl border text-left rtl:text-right flex items-center gap-2.5 transition-all ${
                  exportFormat === 'html'
                    ? 'bg-[#2481cc]/20 border-sky-400 text-white'
                    : 'bg-white/5 border-white/5 text-gray-300 hover:bg-white/10'
                }`}
              >
                <FileText className="w-4 h-4 text-sky-400 shrink-0" />
                <div>
                  <div className="text-xs font-bold">HTML Web Page</div>
                  <div className="text-[10px] text-gray-400">Interactive viewer</div>
                </div>
              </button>

              <button
                onClick={() => setExportFormat('json')}
                className={`p-3 rounded-2xl border text-left rtl:text-right flex items-center gap-2.5 transition-all ${
                  exportFormat === 'json'
                    ? 'bg-[#2481cc]/20 border-sky-400 text-white'
                    : 'bg-white/5 border-white/5 text-gray-300 hover:bg-white/10'
                }`}
              >
                <FileCode className="w-4 h-4 text-emerald-400 shrink-0" />
                <div>
                  <div className="text-xs font-bold">JSON Raw Data</div>
                  <div className="text-[10px] text-gray-400">Machine readable</div>
                </div>
              </button>
            </div>
          </div>

          {/* Options */}
          <div className="space-y-2 pt-1">
            <label className="flex items-center gap-2.5 p-3 rounded-2xl bg-white/5 border border-white/5 cursor-pointer hover:bg-white/10 transition-colors">
              <input
                type="checkbox"
                checked={includeMedia}
                onChange={(e) => setIncludeMedia(e.target.checked)}
                className="w-4 h-4 rounded text-[#2481cc] accent-[#2481cc]"
              />
              <div className="text-xs text-gray-200">
                <span className="font-semibold">
                  {isArabic ? 'تضمين روابط الوسائط والصور' : 'Include media files and attachments metadata'}
                </span>
              </div>
            </label>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-white/10 bg-[#1e2c3a]/80 flex items-center justify-end gap-2.5 shrink-0">
          <button
            onClick={onClose}
            className="px-4 py-2.5 rounded-xl bg-white/5 hover:bg-white/10 text-gray-300 text-xs font-semibold"
          >
            {isArabic ? 'إلغاء' : 'Cancel'}
          </button>
          <button
            onClick={handleStartExport}
            disabled={isExporting}
            className="px-5 py-2.5 rounded-xl bg-[#2481cc] hover:bg-[#1c6fad] text-white text-xs font-bold shadow-lg flex items-center gap-2 transition-transform active:scale-95"
          >
            {isExporting ? (
              <span>{isArabic ? 'جاري المعالجة والتصدير...' : 'Exporting history...'}</span>
            ) : (
              <>
                <ArrowDownToLine className="w-4 h-4" />
                <span>{isArabic ? 'تنزيل السجل الآن' : 'Download History'}</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};
