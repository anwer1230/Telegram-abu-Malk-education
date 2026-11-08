import React, { useState, useEffect } from 'react';
import {
  UserPlus,
  Link,
  Globe,
  Search,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Play,
  Square,
  X,
  FileText,
  Loader2,
  Clock,
} from 'lucide-react';
import { useTelegram } from '../../context/TelegramContext';
import { notificationsService } from '../../core/NotificationsService';
import { AutoJoinerTask } from '../../types';

export const AutoJoinerModal: React.FC = () => {
  const { activeModal, setActiveModal, showToast } = useTelegram();
  const [rawText, setRawText] = useState(
    'انضم إلى مجتمعنا التقني:\nhttps://t.me/tech_innovators_hub\nأو عبر الرابط الخاص: https://t.me/+Vip_Channel_2026\nتابعنا أيضاً على @flutter_devs_group'
  );
  const [tasks, setTasks] = useState<AutoJoinerTask[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [fetchWebLinks, setFetchWebLinks] = useState(false);
  const [searchByName, setSearchByName] = useState(false);
  const [progress, setProgress] = useState({ processed: 0, total: 0 });

  useEffect(() => {
    const unsub = notificationsService.subscribe(() => {
      setTasks([...notificationsService.getAutoJoinTasks()]);
    });
    setTasks([...notificationsService.getAutoJoinTasks()]);
    return () => unsub();
  }, []);

  if (activeModal !== ('auto-joiner' as any)) return null;

  const handleStartJoin = async () => {
    const links = notificationsService.extractLinksFromRawText(rawText);
    if (links.length === 0) {
      showToast('لم يتم العثور على أي روابط تيليجرام صالحة في النص', '⚠️');
      return;
    }

    setIsProcessing(true);
    setProgress({ processed: 0, total: links.length });

    await notificationsService.startAutoJoinTasks(links, (processed, total) => {
      setProgress({ processed, total });
    });

    setIsProcessing(false);
    showToast('اكتملت مهمة الانضمام التلقائي بنجاح ✨', '🎉');
  };

  const handleStopJoin = () => {
    notificationsService.stopAutoJoin();
    setIsProcessing(false);
    showToast('تم إيقاف عملية الانضمام ⏹️', '⚠️');
  };

  return (
    <div
      id="modal-auto-joiner-activity"
      className="fixed inset-0 z-[9999] flex items-center justify-center p-3 sm:p-4 bg-black/85 backdrop-blur-md select-none"
      dir="rtl"
    >
      <div
        className="w-full max-w-2xl text-[#e8eaf6] rounded-3xl shadow-2xl overflow-hidden border border-emerald-500/30 my-auto animate-in zoom-in-95 duration-200 max-h-[90vh] flex flex-col"
        style={{
          background: 'linear-gradient(145deg, #071912, #0d2a1f, #040e0a)',
        }}
      >
        {/* Header */}
        <div className="p-4 sm:p-5 border-b border-white/10 flex items-center justify-between bg-black/40">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center border border-emerald-400/30">
              <UserPlus className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-sm text-white">الانضمام التلقائي المتقدم</h3>
              <p className="text-[11px] text-emerald-300/80">استخراج الروابط بالـ Regex والانضمام المباشر للقنوات والمجموعات</p>
            </div>
          </div>
          <button
            onClick={() => setActiveModal('none')}
            className="p-2 rounded-xl text-gray-400 hover:text-white hover:bg-white/10 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Body */}
        <div className="p-4 sm:p-6 overflow-y-auto space-y-4 flex-1">
          {/* Input text */}
          <div className="space-y-1.5">
            <label className="text-xs font-bold text-gray-200 flex items-center justify-between">
              <span>الصق النص أو الروابط المراد استخراجها والانضمام إليها:</span>
              <span className="text-[10px] text-emerald-400 font-mono">
                {notificationsService.extractLinksFromRawText(rawText).length} روابط مكتشفة
              </span>
            </label>
            <textarea
              value={rawText}
              onChange={(e) => setRawText(e.target.value)}
              rows={4}
              placeholder="الصق نصوصاً طويلة، رسائل، أو روابط تيليجرام عامة وخاصة..."
              className="w-full bg-black/40 border border-white/10 rounded-2xl p-3 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-emerald-400 resize-none font-mono"
            />
          </div>

          {/* Options */}
          <div className="grid grid-cols-2 gap-3">
            <label className="p-3 rounded-2xl bg-black/30 border border-white/5 flex items-center justify-between cursor-pointer">
              <span className="text-xs font-medium text-gray-200 flex items-center gap-2">
                <Globe className="w-4 h-4 text-emerald-400" />
                <span>جلب الروابط من مواقع ويب</span>
              </span>
              <input
                type="checkbox"
                checked={fetchWebLinks}
                onChange={(e) => setFetchWebLinks(e.target.checked)}
                className="w-4 h-4 rounded accent-emerald-500 cursor-pointer"
              />
            </label>

            <label className="p-3 rounded-2xl bg-black/30 border border-white/5 flex items-center justify-between cursor-pointer">
              <span className="text-xs font-medium text-gray-200 flex items-center gap-2">
                <Search className="w-4 h-4 text-emerald-400" />
                <span>البحث عن أسماء المجموعات</span>
              </span>
              <input
                type="checkbox"
                checked={searchByName}
                onChange={(e) => setSearchByName(e.target.checked)}
                className="w-4 h-4 rounded accent-emerald-500 cursor-pointer"
              />
            </label>
          </div>

          {/* Progress Bar */}
          {isProcessing && (
            <div className="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 space-y-2">
              <div className="flex items-center justify-between text-xs text-emerald-300 font-bold">
                <span className="flex items-center gap-2">
                  <Loader2 className="w-4 h-4 animate-spin text-emerald-400" />
                  <span>جاري معالجة الروابط والانضمام...</span>
                </span>
                <span>
                  {progress.processed} من {progress.total}
                </span>
              </div>
              <div className="w-full h-2 rounded-full bg-black/40 overflow-hidden">
                <div
                  className="h-full bg-emerald-400 transition-all duration-300 rounded-full"
                  style={{
                    width: `${progress.total ? (progress.processed / progress.total) * 100 : 0}%`,
                  }}
                />
              </div>
            </div>
          )}

          {/* Tasks Results List */}
          <div className="space-y-2">
            <span className="text-xs font-bold text-gray-200 block">
              سجل الروابط المعالجة ({tasks.length}):
            </span>

            {tasks.length === 0 ? (
              <div className="p-6 rounded-2xl bg-black/20 border border-white/5 text-center text-xs text-gray-500">
                لم يتم تشغيل أي مهمة انضمام بعد
              </div>
            ) : (
              <div className="space-y-1.5 max-h-48 overflow-y-auto">
                {tasks.map((task) => (
                  <div
                    key={task.id}
                    className="p-3 rounded-2xl bg-black/40 border border-white/5 flex items-center justify-between text-xs"
                  >
                    <div className="flex items-center gap-2 overflow-hidden">
                      {task.status === 'joined' && (
                        <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                      )}
                      {task.status === 'joining' && (
                        <Loader2 className="w-4 h-4 text-amber-400 animate-spin shrink-0" />
                      )}
                      {task.status === 'invalid' && (
                        <XCircle className="w-4 h-4 text-rose-400 shrink-0" />
                      )}
                      {task.status === 'pending' && (
                        <Clock className="w-4 h-4 text-gray-400 shrink-0" />
                      )}
                      <span className="font-mono text-gray-200 truncate">{task.url}</span>
                    </div>

                    <div className="flex items-center gap-2 shrink-0">
                      <span
                        className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                          task.status === 'joined'
                            ? 'bg-emerald-500/20 text-emerald-300'
                            : task.status === 'joining'
                            ? 'bg-amber-500/20 text-amber-300'
                            : task.status === 'invalid'
                            ? 'bg-rose-500/20 text-rose-300'
                            : 'bg-gray-500/20 text-gray-300'
                        }`}
                      >
                        {task.status === 'joined'
                          ? 'تم الانضمام'
                          : task.status === 'joining'
                          ? 'جاري الانضمام'
                          : task.status === 'invalid'
                          ? task.errorReason || 'فشل'
                          : 'في الانتظار'}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Footer Actions */}
        <div className="p-4 bg-black/40 border-t border-white/10 flex items-center justify-between">
          <button
            onClick={() => setActiveModal('none')}
            className="px-4 py-2 rounded-xl text-gray-400 hover:text-white text-xs font-bold transition-colors"
          >
            إغلاق
          </button>

          {isProcessing ? (
            <button
              onClick={handleStopJoin}
              className="px-6 py-2.5 rounded-xl bg-rose-600 hover:bg-rose-500 text-white text-xs font-bold transition-all shadow flex items-center gap-2"
            >
              <Square className="w-4 h-4" />
              <span>إيقاف الانضمام</span>
            </button>
          ) : (
            <button
              onClick={handleStartJoin}
              className="px-6 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold transition-all shadow flex items-center gap-2"
            >
              <Play className="w-4 h-4" />
              <span>بدء الانضمام للروابط</span>
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
