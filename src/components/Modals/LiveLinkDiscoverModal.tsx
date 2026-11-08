import React, { useState, useEffect } from 'react';
import {
  Search,
  Radio,
  ToggleLeft,
  ToggleRight,
  Download,
  Trash2,
  CheckCircle2,
  XCircle,
  Clock,
  ExternalLink,
  ShieldCheck,
  X,
  Filter,
  UserPlus,
  RefreshCw,
  Cpu,
} from 'lucide-react';
import { useTelegram } from '../../context/TelegramContext';
import { backgroundSyncService, BackgroundWorkerStatus } from '../../core/BackgroundSyncService';
import { LiveDiscoveredLink } from '../../types';

export const LiveLinkDiscoverModal: React.FC = () => {
  const { activeModal, setActiveModal, showToast } = useTelegram();
  const [links, setLinks] = useState<LiveDiscoveredLink[]>([]);
  const [isInstantJoin, setIsInstantJoin] = useState(false);
  const [isScannerActive, setIsScannerActive] = useState(true);
  const [filterStatus, setFilterStatus] = useState<'all' | 'joined' | 'failed' | 'pending'>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [isJoiningId, setIsJoiningId] = useState<string | null>(null);
  const [workerStatus, setWorkerStatus] = useState<BackgroundWorkerStatus>(backgroundSyncService.getWorkerStatus());

  useEffect(() => {
    const unsub = backgroundSyncService.subscribe(() => {
      setLinks([...backgroundSyncService.getDiscoveredLinks()]);
      setIsInstantJoin(backgroundSyncService.isInstantJoinEnabled());
      setIsScannerActive(backgroundSyncService.isLiveDiscoverActive());
      setWorkerStatus(backgroundSyncService.getWorkerStatus());
    });
    setLinks([...backgroundSyncService.getDiscoveredLinks()]);
    setIsInstantJoin(backgroundSyncService.isInstantJoinEnabled());
    setIsScannerActive(backgroundSyncService.isLiveDiscoverActive());
    setWorkerStatus(backgroundSyncService.getWorkerStatus());
    return () => unsub();
  }, []);

  if (activeModal !== ('live-link-discover' as any) && activeModal !== ('link-monitor' as any))
    return null;

  const handleToggleScanner = () => {
    const next = !isScannerActive;
    backgroundSyncService.toggleLiveDiscover(next);
    setIsScannerActive(next);
    showToast(next ? 'تم تفعيل رادار البحث اللحظي 🔍' : 'تم إيقاف الرادار ⏹️', '✨');
  };

  const handleToggleInstantJoin = () => {
    const next = !isInstantJoin;
    backgroundSyncService.toggleInstantAutoJoin(next);
    setIsInstantJoin(next);
    showToast(
      next
        ? 'تم تفعيل الانضمام التلقائي الفوري لكافة الروابط 🚀'
        : 'تم إيقاف الانضمام التلقائي الفوري 🛑',
      '✨'
    );
  };

  const handleManualJoin = async (linkId: string) => {
    setIsJoiningId(linkId);
    const success = await backgroundSyncService.manualJoinDiscoveredLink(linkId);
    setIsJoiningId(null);
    if (success) {
      showToast('تم الانضمام للرابط بنجاح 🎉', '✅');
    } else {
      showToast('تعذر الانضمام (الرابط تالف أو القناة خاصة)', '⚠️');
    }
  };

  const handleExportReport = () => {
    if (links.length === 0) {
      showToast('لا توجد روابط لتصديرها', '⚠️');
      return;
    }
    const csvContent =
      'data:text/csv;charset=utf-8,' +
      'URL,Source Chat,Sender,Timestamp,Status\n' +
      links
        .map(
          (l) =>
            `"${l.url}","${l.sourceChatTitle}","${l.senderName}","${l.timestamp}","${l.status}"`
        )
        .join('\n');

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `telegram_links_report_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    showToast('تم تصدير تقرير الروابط بنجاح 📥', '✨');
  };

  const filteredLinks = links.filter((l) => {
    if (filterStatus !== 'all' && l.status !== filterStatus) return false;
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      return (
        l.url.toLowerCase().includes(q) ||
        l.sourceChatTitle.toLowerCase().includes(q) ||
        l.senderName.toLowerCase().includes(q)
      );
    }
    return true;
  });

  const totalJoined = links.filter((l) => l.status === 'joined').length;
  const totalFailed = links.filter((l) => l.status === 'failed').length;
  const totalPending = links.filter((l) => l.status === 'pending').length;

  return (
    <div
      id="modal-live-link-discover-activity"
      className="fixed inset-0 z-[9999] flex items-center justify-center p-3 sm:p-4 bg-black/85 backdrop-blur-md select-none"
      dir="rtl"
    >
      <div
        className="w-full max-w-3xl text-[#e8eaf6] rounded-3xl shadow-2xl overflow-hidden border border-teal-500/30 my-auto animate-in zoom-in-95 duration-200 max-h-[90vh] flex flex-col"
        style={{
          background: 'linear-gradient(145deg, #041619, #0a2d32, #020c0e)',
        }}
      >
        {/* Header */}
        <div className="p-4 sm:p-5 border-b border-white/10 flex items-center justify-between bg-black/40">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-teal-500/20 text-teal-400 flex items-center justify-center border border-teal-400/30">
              <Search className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-sm text-white flex items-center gap-2">
                <span>وظيفة البحث والانضمام الفوري</span>
                <span className="px-2 py-0.5 rounded-full text-[9px] font-mono font-bold bg-teal-500/20 text-teal-300 border border-teal-400/30 flex items-center gap-1">
                  <Cpu className="w-2.5 h-2.5 text-teal-400" />
                  {workerStatus.workerType === 'web-worker' ? 'Web Worker Radar' : 'Fallback Engine'}
                </span>
              </h3>
              <p className="text-[11px] text-teal-300/80">رصد وحفظ الروابط المنشورة مع الانضمام الفوري التلقائي في الخلفية</p>
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
          {/* Quick Metrics Bar */}
          <div className="grid grid-cols-4 gap-2 text-center">
            <div className="p-2.5 rounded-2xl bg-black/40 border border-white/5">
              <span className="text-[10px] text-gray-400 block">إجمالي الروابط</span>
              <span className="text-base font-bold text-white font-mono">{links.length}</span>
            </div>
            <div className="p-2.5 rounded-2xl bg-emerald-500/10 border border-emerald-500/20">
              <span className="text-[10px] text-emerald-400 block">تم الانضمام</span>
              <span className="text-base font-bold text-emerald-300 font-mono">{totalJoined}</span>
            </div>
            <div className="p-2.5 rounded-2xl bg-amber-500/10 border border-amber-500/20">
              <span className="text-[10px] text-amber-400 block">قيد الانتظار</span>
              <span className="text-base font-bold text-amber-300 font-mono">{totalPending}</span>
            </div>
            <div className="p-2.5 rounded-2xl bg-rose-500/10 border border-rose-500/20">
              <span className="text-[10px] text-rose-400 block">فشل / تالف</span>
              <span className="text-base font-bold text-rose-300 font-mono">{totalFailed}</span>
            </div>
          </div>

          {/* Toggle Switches Panel */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {/* Live Scanner Toggle */}
            <div className="p-3.5 rounded-2xl bg-black/30 border border-white/10 flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <Radio className={`w-4 h-4 ${isScannerActive ? 'text-teal-400 animate-pulse' : 'text-gray-500'}`} />
                <div>
                  <span className="font-bold text-xs block text-white">رادار البحث اللحظي</span>
                  <span className="text-[10px] text-gray-400">استخراج الروابط من كل رسالة</span>
                </div>
              </div>
              <button onClick={handleToggleScanner} className="p-1">
                {isScannerActive ? (
                  <ToggleRight className="w-8 h-8 text-teal-400" />
                ) : (
                  <ToggleLeft className="w-8 h-8 text-gray-500" />
                )}
              </button>
            </div>

            {/* Instant Auto-Join Toggle (Requested in Prompt) */}
            <div className="p-3.5 rounded-2xl bg-teal-500/15 border border-teal-500/30 flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <ShieldCheck className="w-4 h-4 text-teal-300" />
                <div>
                  <span className="font-bold text-xs block text-teal-200">الانضمام التلقائي الفوري</span>
                  <span className="text-[10px] text-teal-400">انضمام فوري بدون تدخل يدوي</span>
                </div>
              </div>
              <button onClick={handleToggleInstantJoin} className="p-1">
                {isInstantJoin ? (
                  <ToggleRight className="w-8 h-8 text-teal-300" />
                ) : (
                  <ToggleLeft className="w-8 h-8 text-gray-500" />
                )}
              </button>
            </div>
          </div>

          {/* Filter & Search Bar */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-2 pt-1">
            <div className="relative w-full sm:w-64">
              <Search className="w-3.5 h-3.5 text-gray-400 absolute right-3 top-2.5" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="بحث في الروابط أو المجموعات..."
                className="w-full bg-black/40 border border-white/10 rounded-xl pr-9 pl-3 py-1.5 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-teal-400"
              />
            </div>

            <div className="flex items-center gap-1.5 w-full sm:w-auto justify-between sm:justify-end">
              <div className="flex items-center gap-1 bg-black/40 p-1 rounded-xl border border-white/5 text-[11px]">
                {(['all', 'joined', 'pending', 'failed'] as const).map((st) => (
                  <button
                    key={st}
                    onClick={() => setFilterStatus(st)}
                    className={`px-2.5 py-1 rounded-lg font-bold transition-colors ${
                      filterStatus === st
                        ? 'bg-teal-500 text-black'
                        : 'text-gray-400 hover:text-white'
                    }`}
                  >
                    {st === 'all'
                      ? 'الكل'
                      : st === 'joined'
                      ? 'منضم'
                      : st === 'pending'
                      ? 'انتظار'
                      : 'فشل'}
                  </button>
                ))}
              </div>

              <button
                onClick={handleExportReport}
                className="p-2 rounded-xl bg-white/10 hover:bg-white/20 text-white text-xs font-bold transition-colors flex items-center gap-1 shrink-0"
                title="تصدير CSV"
              >
                <Download className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">تصدير</span>
              </button>
            </div>
          </div>

          {/* Captured Links Feed */}
          <div className="space-y-2">
            {filteredLinks.length === 0 ? (
              <div className="p-8 rounded-2xl bg-black/20 border border-white/5 text-center text-xs text-gray-500">
                لا يوجد روابط مطابقة لخيارات البحث الحالية
              </div>
            ) : (
              <div className="space-y-1.5 max-h-56 overflow-y-auto">
                {filteredLinks.map((item) => (
                  <div
                    key={item.id}
                    className="p-3 rounded-2xl bg-black/40 border border-white/5 flex items-center justify-between text-xs hover:border-teal-500/30 transition-all"
                  >
                    <div className="flex items-center gap-3 overflow-hidden">
                      <div className="w-8 h-8 rounded-xl bg-teal-500/10 text-teal-400 flex items-center justify-center shrink-0 border border-teal-500/20">
                        {item.status === 'joined' ? (
                          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                        ) : item.status === 'failed' ? (
                          <XCircle className="w-4 h-4 text-rose-400" />
                        ) : (
                          <Clock className="w-4 h-4 text-amber-400" />
                        )}
                      </div>

                      <div className="overflow-hidden">
                        <div className="flex items-center gap-2">
                          <span className="font-mono font-bold text-teal-300 truncate">
                            {item.url}
                          </span>
                        </div>
                        <div className="text-[10px] text-gray-400 flex items-center gap-2">
                          <span>في: {item.sourceChatTitle}</span>
                          <span>•</span>
                          <span>بواسطة: {item.senderName}</span>
                          <span>•</span>
                          <span className="font-mono">{item.timestamp}</span>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 shrink-0">
                      {item.status === 'pending' && (
                        <button
                          onClick={() => handleManualJoin(item.id)}
                          disabled={isJoiningId === item.id}
                          className="px-3 py-1 rounded-xl bg-teal-600 hover:bg-teal-500 text-white text-[11px] font-bold shadow flex items-center gap-1"
                        >
                          <UserPlus className="w-3 h-3" />
                          <span>{isJoiningId === item.id ? 'جاري...' : 'انضمام'}</span>
                        </button>
                      )}
                      {item.status === 'joined' && (
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300">
                          {item.autoJoined ? 'انضمام فوري' : 'تم الانضمام'}
                        </span>
                      )}
                      {item.status === 'failed' && (
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-rose-500/20 text-rose-300">
                          {item.failReason || 'فشل'}
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 bg-black/40 border-t border-white/10 flex items-center justify-between">
          <button
            onClick={() => backgroundSyncService.clearDiscoveredLinks()}
            className="text-xs text-rose-400 hover:text-rose-300 font-bold flex items-center gap-1"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span>مسح الروابط</span>
          </button>

          <button
            onClick={() => setActiveModal('none')}
            className="px-5 py-2 rounded-xl bg-white/10 hover:bg-white/20 text-white text-xs font-bold transition-colors"
          >
            إغلاق
          </button>
        </div>
      </div>
    </div>
  );
};
