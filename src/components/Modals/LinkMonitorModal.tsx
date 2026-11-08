import React, { useState, useEffect, useMemo } from 'react';
import {
  Link2,
  RotateCw,
  Trash2,
  Calendar,
  Globe,
  User,
  Users,
  Hash,
  ArrowRight,
  X,
  ExternalLink,
  CheckCircle2,
  AlertCircle,
  Clock,
  LogIn,
  MessageCircle,
  Lock,
  Send,
  Search,
  Copy,
  Info,
  ChevronRight,
  Check,
  ShieldCheck,
  Zap,
} from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { useTelegram } from '../../context/TelegramContext';
import { CapturedLink } from '../../types';

interface LinkMonitorModalProps {
  isOpen: boolean;
  onClose: () => void;
}

type FilterCategory = 'all' | 'whatsapp' | 'telegram_joined' | 'telegram_pending' | 'telegram_private';

export const LinkMonitorModal: React.FC<LinkMonitorModalProps> = ({ isOpen, onClose }) => {
  const {
    capturedLinks,
    linkMonitorStats,
    autoJoinLinksEnabled,
    toggleAutoJoinLinks,
    joinCapturedLink,
    checkPendingApprovalLinks,
    clearCapturedLinks,
    manualScanAllChatsForLinks,
    showToast,
    forwardToSavedMessages,
    resolveTelegramLink,
  } = useTelegram();

  const [activeFilter, setActiveFilter] = useState<FilterCategory>('all');
  const [searchFilter, setSearchFilter] = useState('');
  const [selectedLink, setSelectedLink] = useState<CapturedLink | null>(null);
  const [isCheckingPending, setIsCheckingPending] = useState(false);
  const [isJoiningId, setIsJoiningId] = useState<string | null>(null);
  const [copiedUrl, setCopiedUrl] = useState<string | null>(null);

  // Auto-select latest link details when active if none selected
  useEffect(() => {
    if (selectedLink) {
      const refreshed = capturedLinks.find((l) => l.id === selectedLink.id || l.url === selectedLink.url);
      if (refreshed) {
        setSelectedLink(refreshed);
      }
    }
  }, [capturedLinks]);

  // Filtered links list
  const filteredLinks = useMemo(() => {
    return capturedLinks.filter((l) => {
      // Category filter
      if (activeFilter === 'whatsapp') {
        const isWa =
          l.linkCategory === 'whatsapp' ||
          l.type === 'whatsapp' ||
          l.url.includes('whatsapp.com') ||
          l.url.includes('wa.me');
        if (!isWa) return false;
      } else if (activeFilter === 'telegram_joined') {
        const isJoined = l.joinStatus === 'joined' || l.isJoinedActual || l.joined;
        if (!isJoined) return false;
      } else if (activeFilter === 'telegram_pending') {
        const isPending =
          l.joinStatus === 'pending_admin' || l.isPendingApproval || l.status === 'admin_approval_pending';
        if (!isPending) return false;
      } else if (activeFilter === 'telegram_private') {
        const isPrivate =
          l.linkCategory === 'telegram_private' ||
          l.url.includes('/+') ||
          l.url.includes('/joinchat/') ||
          l.type === 'telegram_invite';
        if (!isPrivate) return false;
      }

      // Text search
      if (searchFilter.trim()) {
        const q = searchFilter.toLowerCase();
        const urlMatch = l.url.toLowerCase().includes(q);
        const titleMatch = (l.chat_title || l.extractedTitle || '').toLowerCase().includes(q);
        const sourceMatch = (l.source_chat || l.sourceChatTitle || '').toLowerCase().includes(q);
        const senderMatch = (l.sender || l.sourceSenderName || '').toLowerCase().includes(q);
        if (!urlMatch && !titleMatch && !sourceMatch && !senderMatch) return false;
      }

      return true;
    });
  }, [capturedLinks, activeFilter, searchFilter]);

  const handleCopy = (url: string) => {
    navigator.clipboard.writeText(url).catch(() => {});
    setCopiedUrl(url);
    showToast('تم نسخ الرابط إلى الحافظة', '📋');
    setTimeout(() => setCopiedUrl(null), 2000);
  };

  const handleCheckPending = async () => {
    setIsCheckingPending(true);
    try {
      await checkPendingApprovalLinks();
    } finally {
      setIsCheckingPending(false);
    }
  };

  const handleManualJoin = async (link: CapturedLink) => {
    setIsJoiningId(link.id);
    try {
      await joinCapturedLink(link.id);
    } finally {
      setIsJoiningId(null);
    }
  };

  const handleSendDetailsToSaved = (link: CapturedLink) => {
    forwardToSavedMessages({
      id: `manual_saved_${Date.now()}`,
      chatId: 'chat_saved_messages',
      senderId: 'link_monitor',
      senderName: 'رادار الروابط الذكي ⚡',
      text:
        `📌 **توثيق رابط من رادار الروابط**\n\n` +
        `🔗 **الرابط:** ${link.url}\n` +
        `🏷 **المجموعة / القناة:** ${link.chat_title || link.extractedTitle || 'بدون اسم'}\n` +
        `📊 **النوع:** ${
          link.linkCategory === 'whatsapp'
            ? 'رابط واتساب'
            : link.linkCategory === 'telegram_private'
            ? 'قناة/مجموعة خاصة'
            : 'مجموعة تليجرام عامة'
        }\n` +
        `📍 **المصدر:** ${link.source_chat || link.sourceChatTitle || 'محادثة'}\n` +
        `👤 **المرسل:** ${link.sender || link.sourceSenderName || 'مستخدم'}\n` +
        `🕒 **التاريخ والوقت:** ${link.detectedAt || 'الآن'}`,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      date: new Date().toISOString().split('T')[0],
      isOutgoing: false,
      status: 'read',
    });
    showToast('تم إرسال تفاصيل الرابط إلى الرسائل المحفوظة!', '📨');
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <div
        id="modal-link-monitor-view"
        className="fixed inset-0 z-[9999] flex items-center justify-center p-2 sm:p-4 bg-black/80 backdrop-blur-md select-none overflow-hidden"
        dir="rtl"
      >
        {/* Backdrop */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.2 }}
          onClick={onClose}
          className="fixed inset-0 cursor-pointer"
        />

        {/* Modal Window Container */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 16 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 16 }}
          transition={{ type: 'spring', damping: 26, stiffness: 300 }}
          className="relative z-10 w-full max-w-5xl bg-[#17212b] text-white rounded-2xl shadow-2xl overflow-hidden border border-[#242f3d] flex flex-col max-h-[94vh]"
          style={{ fontFamily: "'Cairo', system-ui, sans-serif" }}
        >
          {/* Header */}
          <div className="px-4 py-3 bg-[#1e2a38] border-b border-[#242f3d] flex items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <button
                onClick={onClose}
                className="p-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-gray-300 hover:text-white transition-colors"
                title="إغلاق"
              >
                <ArrowRight className="w-4 h-4" />
              </button>
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-xl bg-[#2481cc]/20 border border-[#2481cc]/40 flex items-center justify-center text-[#2481cc]">
                  <Link2 className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-base font-bold leading-tight flex items-center gap-2">
                    <span>رادار مراقبة الروابط والانضمام الذكي</span>
                    <span className="text-[10px] bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 px-2 py-0.5 rounded-full font-medium flex items-center gap-1">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                      نشط دائماً
                    </span>
                  </h3>
                  <p className="text-xs text-gray-400">
                    مراقبة شاملة لكافة محادثات الحساب، كشف فوري لروابط الواتساب والتليجرام، وتوثيق تلقائي بالرسائل المحفوظة
                  </p>
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="flex items-center gap-2">
              <button
                onClick={manualScanAllChatsForLinks}
                className="px-2.5 py-1.5 rounded-lg bg-[#242f3d] hover:bg-[#2b394a] text-xs text-gray-200 hover:text-white flex items-center gap-1.5 border border-white/5 transition-colors"
                title="إعادة فحص كافة الرسائل والمحادثات"
              >
                <RotateCw className="w-3.5 h-3.5 text-[#2481cc]" />
                <span className="hidden sm:inline">فحص المحادثات الآن</span>
              </button>

              <button
                onClick={onClose}
                className="p-1.5 rounded-lg hover:bg-white/10 text-gray-400 hover:text-white transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Real-Time Interactive Statistics Cards (Numbered Metrics) */}
          <div className="p-3.5 bg-[#121b22] border-b border-[#242f3d]">
            <div className="text-xs text-gray-400 mb-2 font-medium flex items-center justify-between">
              <span>📊 إحصائيات تفصيلية بالروابط التي تم التعرف عليها ومتابعتها:</span>
              <span className="text-[11px] text-[#2481cc]">
                إجمالي الروابط المرصودة: {linkMonitorStats.totalLinksCount}
              </span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
              {/* WhatsApp Links Card */}
              <div
                onClick={() => setActiveFilter('whatsapp')}
                className={`p-3 rounded-xl border cursor-pointer transition-all ${
                  activeFilter === 'whatsapp'
                    ? 'bg-emerald-500/15 border-emerald-500/60 shadow-lg shadow-emerald-500/10'
                    : 'bg-[#1a2530] border-[#242f3d] hover:border-emerald-500/30'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs text-emerald-300 font-semibold flex items-center gap-1.5">
                    <MessageCircle className="w-3.5 h-3.5 text-emerald-400" />
                    روابط الواتساب
                  </span>
                  <span className="text-[10px] bg-emerald-500/20 text-emerald-300 px-1.5 py-0.5 rounded-full">
                    إشعار فوري
                  </span>
                </div>
                <div className="text-2xl font-bold text-white font-mono">
                  {linkMonitorStats.whatsappCount}
                </div>
                <div className="text-[10px] text-gray-400 mt-1 truncate">
                  أُرسلت للرسائل المحفوظة
                </div>
              </div>

              {/* Telegram Public Actual Joined Card */}
              <div
                onClick={() => setActiveFilter('telegram_joined')}
                className={`p-3 rounded-xl border cursor-pointer transition-all ${
                  activeFilter === 'telegram_joined'
                    ? 'bg-[#2481cc]/20 border-[#2481cc] shadow-lg shadow-[#2481cc]/10'
                    : 'bg-[#1a2530] border-[#242f3d] hover:border-[#2481cc]/40'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs text-[#50a7ea] font-semibold flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5 text-[#50a7ea]" />
                    تليجرام: منضم فعلياً
                  </span>
                  <span className="text-[10px] bg-[#2481cc]/20 text-[#50a7ea] px-1.5 py-0.5 rounded-full">
                    انضمام فوري
                  </span>
                </div>
                <div className="text-2xl font-bold text-white font-mono">
                  {linkMonitorStats.telegramPublicJoined}
                </div>
                <div className="text-[10px] text-gray-400 mt-1 truncate">
                  مجموعات عامة تم الانضمام لها
                </div>
              </div>

              {/* Telegram Public Pending Admin Approval Card */}
              <div
                onClick={() => setActiveFilter('telegram_pending')}
                className={`p-3 rounded-xl border cursor-pointer transition-all ${
                  activeFilter === 'telegram_pending'
                    ? 'bg-amber-500/15 border-amber-500/60 shadow-lg shadow-amber-500/10'
                    : 'bg-[#1a2530] border-[#242f3d] hover:border-amber-500/30'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs text-amber-300 font-semibold flex items-center gap-1.5">
                    <Clock className="w-3.5 h-3.5 text-amber-400" />
                    بانتظار موافقة المشرف
                  </span>
                  <span className="text-[10px] bg-amber-500/20 text-amber-300 px-1.5 py-0.5 rounded-full">
                    طلب انضمام
                  </span>
                </div>
                <div className="text-2xl font-bold text-white font-mono">
                  {linkMonitorStats.telegramPublicPendingAdmin}
                </div>
                <div className="text-[10px] text-gray-400 mt-1 truncate">
                  تتطلب موافقة إدارة المجموعة
                </div>
              </div>

              {/* Telegram Private Channels Card */}
              <div
                onClick={() => setActiveFilter('telegram_private')}
                className={`p-3 rounded-xl border cursor-pointer transition-all ${
                  activeFilter === 'telegram_private'
                    ? 'bg-purple-500/15 border-purple-500/60 shadow-lg shadow-purple-500/10'
                    : 'bg-[#1a2530] border-[#242f3d] hover:border-purple-500/30'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs text-purple-300 font-semibold flex items-center gap-1.5">
                    <Lock className="w-3.5 h-3.5 text-purple-400" />
                    قنوات ومجموعات خاصة
                  </span>
                  <span className="text-[10px] bg-purple-500/20 text-purple-300 px-1.5 py-0.5 rounded-full">
                    دعوة خاصة
                  </span>
                </div>
                <div className="text-2xl font-bold text-white font-mono">
                  {linkMonitorStats.telegramPrivateCount}
                </div>
                <div className="text-[10px] text-gray-400 mt-1 truncate">
                  موثقة بالرسائل المحفوظة
                </div>
              </div>
            </div>
          </div>

          {/* Search & Tabs Filter Bar */}
          <div className="px-4 py-2.5 bg-[#17212b] border-b border-[#242f3d] flex items-center justify-between gap-3 flex-wrap">
            {/* Filter Tabs */}
            <div className="flex items-center gap-1.5 overflow-x-auto text-xs py-0.5">
              <button
                onClick={() => setActiveFilter('all')}
                className={`px-3 py-1.5 rounded-lg font-medium transition-colors whitespace-nowrap ${
                  activeFilter === 'all'
                    ? 'bg-[#2481cc] text-white shadow-sm'
                    : 'bg-[#242f3d] text-gray-300 hover:text-white'
                }`}
              >
                الكل ({capturedLinks.length})
              </button>

              <button
                onClick={() => setActiveFilter('whatsapp')}
                className={`px-3 py-1.5 rounded-lg font-medium transition-colors whitespace-nowrap flex items-center gap-1.5 ${
                  activeFilter === 'whatsapp'
                    ? 'bg-emerald-600 text-white shadow-sm'
                    : 'bg-[#242f3d] text-gray-300 hover:text-white'
                }`}
              >
                <MessageCircle className="w-3 h-3" />
                واتساب ({linkMonitorStats.whatsappCount})
              </button>

              <button
                onClick={() => setActiveFilter('telegram_joined')}
                className={`px-3 py-1.5 rounded-lg font-medium transition-colors whitespace-nowrap flex items-center gap-1.5 ${
                  activeFilter === 'telegram_joined'
                    ? 'bg-[#2481cc] text-white shadow-sm'
                    : 'bg-[#242f3d] text-gray-300 hover:text-white'
                }`}
              >
                <CheckCircle2 className="w-3 h-3" />
                منضم فعلياً ({linkMonitorStats.telegramPublicJoined})
              </button>

              <button
                onClick={() => setActiveFilter('telegram_pending')}
                className={`px-3 py-1.5 rounded-lg font-medium transition-colors whitespace-nowrap flex items-center gap-1.5 ${
                  activeFilter === 'telegram_pending'
                    ? 'bg-amber-600 text-white shadow-sm'
                    : 'bg-[#242f3d] text-gray-300 hover:text-white'
                }`}
              >
                <Clock className="w-3 h-3" />
                بانتظار المشرف ({linkMonitorStats.telegramPublicPendingAdmin})
              </button>

              <button
                onClick={() => setActiveFilter('telegram_private')}
                className={`px-3 py-1.5 rounded-lg font-medium transition-colors whitespace-nowrap flex items-center gap-1.5 ${
                  activeFilter === 'telegram_private'
                    ? 'bg-purple-600 text-white shadow-sm'
                    : 'bg-[#242f3d] text-gray-300 hover:text-white'
                }`}
              >
                <Lock className="w-3 h-3" />
                قنوات خاصة ({linkMonitorStats.telegramPrivateCount})
              </button>
            </div>

            {/* Search Input */}
            <div className="relative flex-1 sm:max-w-xs">
              <Search className="w-3.5 h-3.5 text-gray-400 absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none" />
              <input
                type="text"
                value={searchFilter}
                onChange={(e) => setSearchFilter(e.target.value)}
                placeholder="بحث في الروابط أو المصدر..."
                className="w-full bg-[#242f3d] border border-transparent focus:border-[#2481cc]/60 rounded-lg pr-8 pl-3 py-1 text-xs text-white placeholder-gray-400 focus:outline-none"
              />
            </div>
          </div>

          {/* Main Area: Split View between List and Selected Link Details */}
          <div className="flex-1 overflow-hidden grid grid-cols-1 md:grid-cols-12 min-h-0">
            {/* Links List Column */}
            <div
              className={`overflow-y-auto p-3 space-y-2 border-l border-[#242f3d] ${
                selectedLink ? 'hidden md:block md:col-span-6 lg:col-span-7' : 'col-span-12'
              }`}
            >
              {filteredLinks.length === 0 ? (
                <div className="text-center py-16 text-gray-400">
                  <Link2 className="w-12 h-12 mx-auto mb-3 opacity-30 text-[#2481cc]" />
                  <p className="font-semibold text-sm text-gray-300">لا توجد روابط مسجلة في هذا القسم حالياً</p>
                  <p className="text-xs text-gray-500 mt-1">
                    يقوم الرادار بمراقبة كافة المحادثات والرسائل الواردة والصادرة تلقائياً
                  </p>
                </div>
              ) : (
                filteredLinks.map((link) => {
                  const isSelected = selectedLink?.id === link.id || selectedLink?.url === link.url;
                  const isWhatsApp =
                    link.linkCategory === 'whatsapp' ||
                    link.type === 'whatsapp' ||
                    link.url.includes('whatsapp') ||
                    link.url.includes('wa.me');
                  const isPrivate =
                    link.linkCategory === 'telegram_private' ||
                    link.url.includes('/+') ||
                    link.url.includes('/joinchat/');
                  const isJoined = link.joinStatus === 'joined' || link.isJoinedActual || link.joined;
                  const isPending =
                    link.joinStatus === 'pending_admin' || link.isPendingApproval || link.status === 'admin_approval_pending';

                  let badgeColor = 'bg-gray-500/20 text-gray-300 border-gray-500/30';
                  let badgeLabel = 'فحص';
                  let borderAccent = 'border-r-gray-500';

                  if (isWhatsApp) {
                    badgeColor = 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40';
                    badgeLabel = 'واتساب (إشعار فوري)';
                    borderAccent = 'border-r-emerald-500';
                  } else if (isJoined) {
                    badgeColor = 'bg-[#2481cc]/20 text-[#50a7ea] border-[#2481cc]/40';
                    badgeLabel = 'منضم فعلياً ✅';
                    borderAccent = 'border-r-[#2481cc]';
                  } else if (isPending) {
                    badgeColor = 'bg-amber-500/20 text-amber-300 border-amber-500/40';
                    badgeLabel = 'بانتظار موافقة المشرف ⏳';
                    borderAccent = 'border-r-amber-500';
                  } else if (isPrivate) {
                    badgeColor = 'bg-purple-500/20 text-purple-300 border-purple-500/40';
                    badgeLabel = 'قناة خاصة 🔒';
                    borderAccent = 'border-r-purple-500';
                  }

                  return (
                    <div
                      key={link.id || link.url}
                      onClick={() => setSelectedLink(link)}
                      className={`p-3 rounded-xl border border-r-4 ${borderAccent} cursor-pointer transition-all text-xs select-text ${
                        isSelected
                          ? 'bg-[#242f3d] border-[#2481cc] shadow-md'
                          : 'bg-[#1c2733] border-[#242f3d] hover:bg-[#202c3a]'
                      }`}
                    >
                      <div className="flex items-start justify-between gap-2">
                        <div className="min-w-0 flex-1">
                          <div className="flex items-center gap-2 flex-wrap mb-1">
                            <span className={`px-2 py-0.5 rounded-full font-semibold text-[10px] border ${badgeColor}`}>
                              {badgeLabel}
                            </span>
                            <span className="font-medium text-white truncate max-w-[200px]">
                              {link.chat_title || link.extractedTitle || 'رابط دردشة'}
                            </span>
                          </div>

                          <div className="font-mono text-[11px] text-[#50a7ea] break-all hover:underline line-clamp-1">
                            {link.url}
                          </div>

                          <div className="flex items-center gap-3 text-[10px] text-gray-400 mt-1.5 flex-wrap">
                            <span className="flex items-center gap-1">
                              <Hash className="w-3 h-3 text-gray-500" />
                              <span className="truncate max-w-[120px]">
                                {link.source_chat || link.sourceChatTitle || 'محادثة'}
                              </span>
                            </span>
                            <span className="flex items-center gap-1">
                              <User className="w-3 h-3 text-gray-500" />
                              <span className="truncate max-w-[100px]">
                                {link.sender || link.sourceSenderName || 'عضو'}
                              </span>
                            </span>
                            <span className="flex items-center gap-1 text-gray-500">
                              <Clock className="w-3 h-3" />
                              <span>{link.detectedAt || 'مؤخراً'}</span>
                            </span>
                          </div>
                        </div>

                        {/* Arrow indicator */}
                        <div className="flex items-center gap-1 shrink-0 self-center">
                          <ChevronRight className="w-4 h-4 text-gray-400 rtl:rotate-180" />
                        </div>
                      </div>
                    </div>
                  );
                })
              )}
            </div>

            {/* Selected Link Detailed View (وتضهر تفاصيل الروابط عند الضغط عليها) */}
            {selectedLink && (
              <div className="col-span-12 md:col-span-6 lg:col-span-5 bg-[#151e27] p-4 overflow-y-auto flex flex-col justify-between">
                <div className="space-y-4">
                  {/* Top Bar with Close Mobile */}
                  <div className="flex items-center justify-between border-b border-[#242f3d] pb-2">
                    <h4 className="text-sm font-bold text-white flex items-center gap-2">
                      <Info className="w-4 h-4 text-[#2481cc]" />
                      <span>تفاصيل الرابط الكاملة</span>
                    </h4>
                    <button
                      onClick={() => setSelectedLink(null)}
                      className="p-1 rounded-md hover:bg-white/10 text-gray-400 hover:text-white"
                      title="إغلاق التفاصيل"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>

                  {/* Classification Card */}
                  <div className="p-3 bg-[#1e2a38] rounded-xl border border-[#242f3d] space-y-2">
                    <div className="text-xs text-gray-400">تصنيف الرابط:</div>
                    <div className="text-sm font-bold text-white flex items-center gap-2">
                      {selectedLink.linkCategory === 'whatsapp' ? (
                        <>
                          <MessageCircle className="w-4 h-4 text-emerald-400" />
                          <span className="text-emerald-300">رابط واتساب (WhatsApp Link)</span>
                        </>
                      ) : selectedLink.linkCategory === 'telegram_private' ? (
                        <>
                          <Lock className="w-4 h-4 text-purple-400" />
                          <span className="text-purple-300">رابط قناة أو مجموعة تليجرام خاصة (Private Channel)</span>
                        </>
                      ) : (
                        <>
                          <Link2 className="w-4 h-4 text-[#50a7ea]" />
                          <span className="text-[#50a7ea]">رابط مجموعة / قناة تليجرام عامة (Public Channel/Group)</span>
                        </>
                      )}
                    </div>
                    <div className="text-xs text-gray-300 leading-relaxed bg-[#17212b] p-2.5 rounded-lg border border-white/5">
                      {selectedLink.linkCategory === 'whatsapp' && (
                        <span>
                          ⚡ تم التعرف على رابط واتساب وإرسال إشعار تفصيلي فوري إلى "الرسائل المحفوظة" لحسابك مع الوقت واسم المرسل.
                        </span>
                      )}
                      {selectedLink.linkCategory === 'telegram_private' && (
                        <span>
                          🔒 هذا الرابط لقناة/مجموعة خاصة يتطلب دعوة مباشرة أو موافقة مسبقة. تم حفظه وتوثيقه في الرسائل المحفوظة.
                        </span>
                      )}
                      {selectedLink.linkCategory !== 'whatsapp' && selectedLink.linkCategory !== 'telegram_private' && (
                        <span>
                          {selectedLink.joinStatus === 'joined' || selectedLink.isJoinedActual || selectedLink.joined
                            ? '✅ تم الانضمام الفعلي بنجاح إلى هذه المجموعة وتفعيلها في حسابك، وإرسال إشعار توثيق للرسائل المحفوظة.'
                            : selectedLink.joinStatus === 'pending_admin' || selectedLink.isPendingApproval
                            ? '⏳ رابط مجموعة عامة يتطلب موافقة المشرف. تم إرسال طلب الانضمام وتوثيقه، ويمكن فحصه لاحقاً.'
                            : '⏳ جاري متابعة حالة الرابط ومعالجة الانضمام.'}
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Link URL with Direct Copy & Open */}
                  <div className="p-3 bg-[#1e2a38] rounded-xl border border-[#242f3d] space-y-2">
                    <div className="flex items-center justify-between text-xs text-gray-400">
                      <span>الرابط المكتشف:</span>
                      <div className="flex items-center gap-1">
                        <button
                          onClick={() => handleCopy(selectedLink.url)}
                          className="px-2 py-0.5 rounded bg-[#2481cc]/20 hover:bg-[#2481cc]/30 text-[#50a7ea] text-[11px] flex items-center gap-1 transition-colors"
                        >
                          {copiedUrl === selectedLink.url ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                          <span>نسخ</span>
                        </button>
                        <a
                          href={selectedLink.url}
                          target="_blank"
                          rel="noreferrer"
                          className="px-2 py-0.5 rounded bg-white/10 hover:bg-white/20 text-gray-200 text-[11px] flex items-center gap-1 transition-colors"
                        >
                          <ExternalLink className="w-3 h-3" />
                          <span>فتح</span>
                        </a>
                      </div>
                    </div>
                    <div className="font-mono text-xs text-[#50a7ea] break-all select-all bg-[#17212b] p-2 rounded-lg border border-white/5">
                      {selectedLink.url}
                    </div>
                  </div>

                  {/* Metadata Grid */}
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div className="p-2.5 bg-[#1e2a38] rounded-xl border border-[#242f3d]">
                      <div className="text-[10px] text-gray-400 mb-1 flex items-center gap-1">
                        <Hash className="w-3 h-3 text-[#2481cc]" />
                        <span>محادثة المصدر:</span>
                      </div>
                      <div className="font-semibold text-white truncate">
                        {selectedLink.source_chat || selectedLink.sourceChatTitle || 'محادثة عامة'}
                      </div>
                    </div>

                    <div className="p-2.5 bg-[#1e2a38] rounded-xl border border-[#242f3d]">
                      <div className="text-[10px] text-gray-400 mb-1 flex items-center gap-1">
                        <User className="w-3 h-3 text-[#2481cc]" />
                        <span>مرسل الرابط:</span>
                      </div>
                      <div className="font-semibold text-white truncate">
                        {selectedLink.sender || selectedLink.sourceSenderName || 'عضو تليجرام'}
                      </div>
                    </div>

                    <div className="p-2.5 bg-[#1e2a38] rounded-xl border border-[#242f3d]">
                      <div className="text-[10px] text-gray-400 mb-1 flex items-center gap-1">
                        <Clock className="w-3 h-3 text-[#2481cc]" />
                        <span>وقت الرصد الدقيق:</span>
                      </div>
                      <div className="font-semibold text-white font-mono">
                        {selectedLink.detectedAt || selectedLink.detected_at || 'الآن'}
                      </div>
                    </div>

                    <div className="p-2.5 bg-[#1e2a38] rounded-xl border border-[#242f3d]">
                      <div className="text-[10px] text-gray-400 mb-1 flex items-center gap-1">
                        <Globe className="w-3 h-3 text-[#2481cc]" />
                        <span>الدولة التقديرية:</span>
                      </div>
                      <div className="font-semibold text-white truncate">
                        {selectedLink.country || '🇸🇦 السعودية'}
                      </div>
                    </div>
                  </div>

                  {/* Saved Messages Confirmation Banner */}
                  <div className="p-2.5 rounded-xl bg-[#2481cc]/10 border border-[#2481cc]/30 flex items-center gap-2.5 text-xs text-[#50a7ea]">
                    <ShieldCheck className="w-4 h-4 shrink-0" />
                    <span>تم توثيق هذا الحدث تلقائياً في حسابك داخل "الرسائل المحفوظة".</span>
                  </div>
                </div>

                {/* Bottom Actions for Selected Link */}
                <div className="pt-4 border-t border-[#242f3d] flex items-center gap-2 mt-4">
                  {/* Join Action if not already joined and not WhatsApp */}
                  {selectedLink.linkCategory !== 'whatsapp' &&
                    !selectedLink.joined &&
                    !selectedLink.isJoinedActual && (
                      <button
                        onClick={() => handleManualJoin(selectedLink)}
                        disabled={isJoiningId === selectedLink.id}
                        className="flex-1 py-2 px-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs flex items-center justify-center gap-1.5 transition-colors disabled:opacity-50"
                      >
                        {isJoiningId === selectedLink.id ? (
                          <RotateCw className="w-3.5 h-3.5 animate-spin" />
                        ) : (
                          <LogIn className="w-3.5 h-3.5" />
                        )}
                        <span>انضمام فوري للمجموعة</span>
                      </button>
                    )}

                  <button
                    onClick={() => {
                      resolveTelegramLink(selectedLink.url);
                      onClose();
                    }}
                    className="py-2 px-3 rounded-xl bg-[#2481cc] hover:bg-[#1f73b7] text-white text-xs font-medium flex items-center justify-center gap-1.5 transition-colors"
                    title="فتح شاشة المعاينة الرسمية (MTProto Preview) وزر الانضمام الأزرق"
                  >
                    <ExternalLink className="w-3.5 h-3.5" />
                    <span>معاينة وزر الانضمام</span>
                  </button>

                  <button
                    onClick={() => handleSendDetailsToSaved(selectedLink)}
                    className="py-2 px-3 rounded-xl bg-[#242f3d] hover:bg-[#2c3a4a] text-gray-200 text-xs font-medium flex items-center justify-center gap-1.5 transition-colors"
                    title="إرسال نسخة تفصيلية للرسائل المحفوظة"
                  >
                    <Send className="w-3.5 h-3.5 text-[#2481cc]" />
                    <span>إرسال للرسائل المحفوظة</span>
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Persistent Bottom Action Bar (الزر الإضافي بالأسفل لفحص روابط المشرف) */}
          <div className="p-3 bg-[#1e2a38] border-t border-[#242f3d] flex items-center justify-between gap-3 flex-wrap">
            <div className="text-xs text-gray-400 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
              <span>
                الحالة: <strong className="text-white">المراقبة قيد التشغيل التلقائي دائماً</strong> عبر كافة محادثات الحساب
              </span>
            </div>

            <div className="flex items-center gap-2.5 flex-wrap">
              {/* Extra Bottom Button Requested: "ويكون هناك زر اضافي بالاسفل في شاشة الوضيفة يقوم بفحص روابط التليجرام التي بانتظار موافقة المشرف ان كانت انقبلت فيقوم بالانظمام لها فعليا وتحديث الاحصائيات وتحديث حالت الرابط واشعار الرسائل المحفوضة." */}
              <button
                id="btn-check-pending-links"
                onClick={handleCheckPending}
                disabled={isCheckingPending}
                className="py-2 px-4 rounded-xl bg-gradient-to-r from-amber-600 to-amber-500 hover:from-amber-500 hover:to-amber-400 text-white font-bold text-xs flex items-center gap-2 shadow-lg shadow-amber-600/20 transition-all active:scale-95 disabled:opacity-50 cursor-pointer"
              >
                {isCheckingPending ? (
                  <RotateCw className="w-4 h-4 animate-spin" />
                ) : (
                  <Zap className="w-4 h-4" />
                )}
                <span>
                  فحص روابط المشرف والانضمام الفعلي{' '}
                  {linkMonitorStats.telegramPublicPendingAdmin > 0 &&
                    `(${linkMonitorStats.telegramPublicPendingAdmin})`}
                </span>
              </button>

              <button
                onClick={clearCapturedLinks}
                className="py-2 px-3 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/20 text-xs font-medium flex items-center gap-1.5 transition-colors"
                title="مسح سجل الروابط"
              >
                <Trash2 className="w-3.5 h-3.5" />
                <span>مسح السجل</span>
              </button>
            </div>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
};
