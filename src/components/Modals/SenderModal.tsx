import React, { useState, useEffect, useRef } from 'react';
import {
  X,
  Send,
  Radio,
  Clock,
  Shield,
  Layers,
  Activity,
  CheckCircle2,
  AlertTriangle,
  Play,
  Square,
  Pause,
  RotateCw,
  Image as ImageIcon,
  Sparkles,
  Search,
  ExternalLink,
  Copy,
  Users,
  MessageSquare,
  ListPlus,
  Trash2,
  Bell,
  Check,
} from 'lucide-react';
import { io, Socket } from 'socket.io-client';
import { useTelegram } from '../../context/TelegramContext';
import { ChatPickerModal } from './ChatPickerModal';

interface PreCheckItem {
  rawInput: string;
  normalizedPeer: string;
  title: string;
  isMember: boolean;
  isChannel: boolean;
  isProtected: boolean;
  protectionBotName?: string;
  chosenMode: 'off' | 'skip' | 'smart' | 'convert_links' | 'salam';
  status: 'valid' | 'invalid' | 'not_member' | 'protected';
  error?: string;
}

interface BatchReport {
  batchId: string;
  timestamp: string;
  totalGroups: number;
  successCount: number;
  failCount: number;
  skippedCount: number;
  details: Array<{
    target: string;
    title: string;
    status: 'success' | 'failed' | 'skipped';
    modeApplied: string;
    note?: string;
  }>;
}

interface KeywordAlert {
  id: string;
  keyword: string;
  chatTitle: string;
  chatId: string;
  senderName: string;
  senderUsername?: string;
  timestamp: string;
  text: string;
}

export const SenderModal: React.FC = () => {
  const { activeModal, setActiveModal, settings, currentUser, chats, showToast } = useTelegram();
  const isArabic = settings.language === 'ar';

  const [activeTab, setActiveTab] = useState<'broadcast' | 'monitor' | 'joiner' | 'reports'>('broadcast');

  // Broadcast State
  const [dispatchType, setDispatchType] = useState<'manual' | 'scheduled' | 'sequential'>('manual');
  const [messageText, setMessageText] = useState('');
  const [groupsInput, setGroupsInput] = useState('');
  const [sendToAllGroups, setSendToAllGroups] = useState(false);
  const [images, setImages] = useState<string[]>([]);
  const [intervalMinutes, setIntervalMinutes] = useState(60);
  const [totalHours, setTotalHours] = useState(0);
  const [protectionMode, setProtectionMode] = useState<'off' | 'skip' | 'smart' | 'convert_links' | 'salam'>('salam');
  const [requiredMemberMessages, setRequiredMemberMessages] = useState(5);
  const [sequentialMessages, setSequentialMessages] = useState<string[]>(['']);
  const [isDispatching, setIsDispatching] = useState(false);
  const [countdownSeconds, setCountdownSeconds] = useState<number | null>(null);
  const [isChatPickerOpen, setIsChatPickerOpen] = useState(false);

  // Monitoring State
  const [isMonitoring, setIsMonitoring] = useState(false);
  const [keywordsInput, setKeywordsInput] = useState('');
  const [alerts, setAlerts] = useState<KeywordAlert[]>([]);
  const [browserNotificationsEnabled, setBrowserNotificationsEnabled] = useState(false);

  // Pre-Check State
  const [preCheckResults, setPreCheckResults] = useState<PreCheckItem[]>([]);
  const [isPreChecking, setIsPreChecking] = useState(false);

  // Joiner State
  const [joinerInput, setJoinerInput] = useState('');
  const [joinerState, setJoinerState] = useState<{
    status: string;
    total: number;
    joined: number;
    skipped: number;
    failed: number;
    currentLink?: string;
    logs: string[];
  }>({
    status: 'idle',
    total: 0,
    joined: 0,
    skipped: 0,
    failed: 0,
    logs: [],
  });

  // Reports & Logs State
  const [reports, setReports] = useState<BatchReport[]>([]);
  const [liveLogs, setLiveLogs] = useState<string[]>([]);

  // Socket reference
  const socketRef = useRef<Socket | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Current session/phone
  const sessionString = (currentUser as any)?.sessionString || '';
  const phone = currentUser?.phone || '';
  const userId = phone || (currentUser as any)?.id || 'user_default';

  // Request browser notifications permission
  const requestNotificationPermission = async () => {
    if ('Notification' in window) {
      const perm = await Notification.requestPermission();
      setBrowserNotificationsEnabled(perm === 'granted');
      if (perm === 'granted') {
        showToast(isArabic ? 'تم تفعيل إشعارات المتصفح بنجاح' : 'Browser notifications enabled', 'success');
      }
    }
  };

  // Connect Socket.IO on mount
  useEffect(() => {
    const socket = io({
      path: '/socket.io',
      reconnectionAttempts: 5,
    });
    socketRef.current = socket;

    socket.on('connect', () => {
      addLog('🌐 متصل بخادم الأتمتة المباشر (Socket.IO Connected)');
    });

    socket.on('keyword_alert', (alert: KeywordAlert) => {
      setAlerts((prev) => [alert, ...prev.slice(0, 49)]);
      addLog(`🚨 رصد كلمة مفتاحية: [${alert.keyword}] في ${alert.chatTitle}`);
      showToast(`🚨 رصد كلمة [${alert.keyword}] في: ${alert.chatTitle}`, 'info');

      if ('Notification' in window && Notification.permission === 'granted') {
        new Notification(`رصد كلمة: ${alert.keyword}`, {
          body: `المجموعة: ${alert.chatTitle}\nالمرسل: ${alert.senderName}`,
          icon: '/public/icon.svg',
        });
      }
    });

    socket.on('countdown_tick', (data: { remainingSeconds: number }) => {
      setCountdownSeconds(data.remainingSeconds);
    });

    socket.on('batch_report', (report: BatchReport) => {
      setReports((prev) => [report, ...prev]);
      addLog(`📊 اكتملت دفعة الإرسال ${report.batchId}: ${report.successCount} نجاح، ${report.skippedCount} مستثنى`);
      showToast(isArabic ? `اكتملت الدفعة: ${report.successCount} تم إرسالها بنجاح` : 'Batch completed', 'success');
    });

    socket.on('dispatch_progress', (data: any) => {
      addLog(`🚀 إرسال (${data.current}/${data.total}): ${data.groupTitle} - ${data.status === 'success' ? '✅ تم' : '❌ فشل'}`);
    });

    socket.on('joiner_progress', (data: any) => {
      if (data.progress) {
        setJoinerState(data.progress);
      }
    });

    // Load initial config
    fetch(`/api/automation/config?userId=${encodeURIComponent(userId)}`)
      .then((res) => res.json())
      .then((data) => {
        if (data.ok && data.config) {
          const cfg = data.config;
          setMessageText(cfg.messageText || '');
          setGroupsInput((cfg.groups || []).join('\n'));
          setKeywordsInput((cfg.keywords || []).join('\n'));
          setDispatchType(cfg.dispatchType || 'manual');
          setIntervalMinutes(cfg.intervalMinutes || 60);
          setTotalHours(cfg.totalHours || 0);
          setProtectionMode(cfg.protectionMode || 'salam');
          setRequiredMemberMessages(cfg.requiredMemberMessages || 5);
          setSendToAllGroups(Boolean(cfg.sendToAllGroups));
          if (cfg.sequentialMessages && cfg.sequentialMessages.length > 0) {
            setSequentialMessages(cfg.sequentialMessages);
          }
          setIsMonitoring(Boolean(cfg.isMonitoring));
          setIsDispatching(Boolean(cfg.isDispatching));
        }
      })
      .catch(() => {});

    return () => {
      socket.disconnect();
    };
  }, [userId]);

  const addLog = (msg: string) => {
    const time = new Date().toLocaleTimeString('ar-SA');
    setLiveLogs((prev) => [`[${time}] ${msg}`, ...prev.slice(0, 99)]);
  };

  if (activeModal !== ('sender' as any) && activeModal !== ('monitor' as any)) return null;

  // Clean and deduplicate groups input
  const handleCleanGroups = () => {
    const lines = groupsInput.split('\n');
    const cleaned = Array.from(
      new Set(
        lines
          .map((l) => l.replace(/^[\s•\-\*\d\.\)\(\[\]:،,]+/u, '').trim())
          .filter(Boolean)
      )
    );
    setGroupsInput(cleaned.join('\n'));
    showToast(isArabic ? `تم تنظيف وتوحيد ${cleaned.length} مجموعة` : 'Groups sanitized', 'info');
  };

  // Handle picked chats from miniature chat picker modal
  const handleChatsPicked = (selectedLinks: string[]) => {
    if (!selectedLinks || selectedLinks.length === 0) return;
    const existing = groupsInput
      .split('\n')
      .map((s) => s.trim())
      .filter(Boolean);
    const merged = Array.from(new Set([...existing, ...selectedLinks]));
    setGroupsInput(merged.join('\n'));
    showToast(
      isArabic
        ? `تم نقل وتنسيق روابط ${selectedLinks.length} مجموعة بنجاح إلى خانة الإرسال ✅`
        : `Transferred ${selectedLinks.length} group links to targets ✅`,
      'success'
    );
  };

  // Handle Image Upload
  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      const reader = new FileReader();
      reader.onload = () => {
        if (reader.result) {
          setImages((prev) => [...prev, reader.result as string]);
        }
      };
      reader.readAsDataURL(file);
    }
  };

  // Run Pre-Check on groups
  const handlePreCheck = async () => {
    const targets = groupsInput.split('\n').map((l) => l.trim()).filter(Boolean);
    if (targets.length === 0 && !sendToAllGroups) {
      showToast(isArabic ? 'الرجاء إدخال قائمة المجموعات أولاً' : 'Enter groups first', 'error');
      return;
    }

    setIsPreChecking(true);
    try {
      const res = await fetch('/api/automation/pre-check', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-telegram-session': sessionString,
          'x-telegram-phone': phone,
          'x-user-id': userId,
        },
        body: JSON.stringify({ groups: targets }),
      });
      const data = await res.json();
      if (data.ok) {
        setPreCheckResults(data.results || []);
        showToast(isArabic ? `تم فحص ${data.results.length} مجموعة بنجاح` : 'Pre-check completed', 'success');
      } else {
        showToast(data.error || 'فشل الفحص المسبق', 'error');
      }
    } catch (e: any) {
      showToast(e.message || 'خطأ في الاتصال', 'error');
    } finally {
      setIsPreChecking(false);
    }
  };

  // Save current configuration to backend
  const saveCurrentConfig = async () => {
    const groups = groupsInput.split('\n').map((l) => l.trim()).filter(Boolean);
    const keywords = keywordsInput.split('\n').map((l) => l.trim()).filter(Boolean);

    await fetch('/api/automation/config', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        userId,
        messageText,
        groups,
        images,
        dispatchType,
        intervalMinutes,
        totalHours,
        protectionMode,
        requiredMemberMessages,
        sendToAllGroups,
        sequentialMessages,
        keywords,
      }),
    });
  };

  // Start Broadcast Dispatch
  const handleStartDispatch = async () => {
    if (!sendToAllGroups && !groupsInput.trim()) {
      showToast(isArabic ? 'الرجاء إدخال قائمة المجموعات أو تفعيل الإرسال للكل' : 'Provide groups', 'error');
      return;
    }
    if (dispatchType !== 'sequential' && !messageText.trim() && images.length === 0) {
      showToast(isArabic ? 'الرجاء كتابة نص الرسالة أو إرفاق صورة' : 'Provide message text or image', 'error');
      return;
    }

    await saveCurrentConfig();

    try {
      const groups = groupsInput.split('\n').map((l) => l.trim()).filter(Boolean);
      const res = await fetch('/api/automation/start-dispatch', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-telegram-session': sessionString,
          'x-telegram-phone': phone,
          'x-user-id': userId,
        },
        body: JSON.stringify({
          config: {
            userId,
            messageText,
            groups,
            images,
            dispatchType,
            intervalMinutes,
            totalHours,
            protectionMode,
            requiredMemberMessages,
            sendToAllGroups,
            sequentialMessages: sequentialMessages.filter((m) => m.trim()),
            keywords: keywordsInput.split('\n').map((l) => l.trim()).filter(Boolean),
          },
        }),
      });

      const data = await res.json();
      if (data.ok) {
        if (dispatchType === 'manual') {
          showToast(isArabic ? 'تم إطلاق دفعة الإرسال الفوري بنجاح' : 'Instant batch launched', 'success');
        } else {
          setIsDispatching(true);
          showToast(isArabic ? `تم بدء الإرسال ${dispatchType === 'scheduled' ? 'المجدول' : 'المتسلسل'} المستمر` : 'Automation started', 'success');
        }
      } else {
        showToast(data.error || 'فشل تشغيل الإرسال', 'error');
      }
    } catch (e: any) {
      showToast(e.message || 'خطأ في الاتصال', 'error');
    }
  };

  // Stop Broadcast Dispatch
  const handleStopDispatch = async () => {
    try {
      const res = await fetch('/api/automation/stop-dispatch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ userId }),
      });
      const data = await res.json();
      if (data.ok) {
        setIsDispatching(false);
        setCountdownSeconds(null);
        showToast(isArabic ? 'تم إيقاف مهمة الإرسال التلقائي' : 'Dispatch stopped', 'info');
      }
    } catch (e: any) {
      showToast(e.message, 'error');
    }
  };

  // Toggle Keyword Monitoring
  const handleToggleMonitor = async () => {
    const nextState = !isMonitoring;
    const keywords = keywordsInput.split('\n').map((l) => l.trim()).filter(Boolean);

    if (nextState && keywords.length === 0) {
      showToast(isArabic ? 'الرجاء إدخال كلمة مفتاحية واحدة على الأقل' : 'Enter keywords first', 'error');
      return;
    }

    try {
      const res = await fetch('/api/automation/toggle-monitor', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-telegram-session': sessionString,
          'x-telegram-phone': phone,
          'x-user-id': userId,
        },
        body: JSON.stringify({
          enable: nextState,
          keywords,
        }),
      });
      const data = await res.json();
      if (data.ok) {
        setIsMonitoring(data.isMonitoring);
        if (data.isMonitoring) {
          showToast(isArabic ? '✅ تم تفعيل مراقبة الحساب بالكامل على مدار الساعة' : 'Monitoring active', 'success');
        } else {
          showToast(isArabic ? '⏹ تم إيقاف المراقبة' : 'Monitoring stopped', 'info');
        }
      }
    } catch (e: any) {
      showToast(e.message, 'error');
    }
  };

  // Joiner Actions
  const handleStartJoiner = async () => {
    if (!joinerInput.trim()) {
      showToast(isArabic ? 'الرجاء إدخال روابط أو مصادر الانضمام' : 'Enter join sources', 'error');
      return;
    }

    try {
      const res = await fetch('/api/automation/joiner/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-telegram-session': sessionString,
          'x-telegram-phone': phone,
          'x-user-id': userId,
        },
        body: JSON.stringify({
          rawInput: joinerInput,
          delaySeconds: 12,
        }),
      });
      const data = await res.json();
      if (data.ok) {
        setJoinerState(data.state);
        showToast(isArabic ? 'بدأت عملية استخراج الروابط والانضمام' : 'Joiner started', 'success');
      }
    } catch (e: any) {
      showToast(e.message, 'error');
    }
  };

  const handleJoinerControl = async (action: 'pause' | 'resume' | 'stop') => {
    await fetch(`/api/automation/joiner/${action}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ userId }),
    });
    showToast(isArabic ? `تم تنفيذ: ${action}` : `Action ${action} executed`, 'info');
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-2 sm:p-4 bg-black/75 backdrop-blur-xs animate-in fade-in duration-150">
      <div
        id="modal-sender-monitor-hub"
        className="bg-[#17212b] border border-[#242f3d] text-white rounded-2xl w-full max-w-4xl max-h-[92vh] flex flex-col shadow-2xl overflow-hidden font-sans"
      >
        {/* Header Bar */}
        <div className="p-4 bg-[#202b36] border-b border-[#242f3d] flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-[#2481cc]/20 border border-[#2481cc]/30 flex items-center justify-center text-[#2481cc]">
              <Radio className="w-5 h-5 animate-pulse" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="font-bold text-base sm:text-lg">
                  {isArabic ? 'نظام الإرسال والمراقبة الشامل' : 'Broadcast & Monitoring Hub'}
                </h2>
                <span className="text-[10px] bg-[#2481cc] text-white font-mono px-2 py-0.5 rounded-full font-bold">
                  PRO
                </span>
              </div>
              <p className="text-xs text-gray-400">
                {isArabic
                  ? 'إرسال فوري ومجدول، رصد الكلمات المفتاحية، وفحص بوتات الحماية'
                  : 'Automated dispatch, keyword alerts & protection shields'}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {countdownSeconds !== null && isDispatching && (
              <div className="hidden sm:flex items-center gap-1.5 px-3 py-1 bg-[#2481cc]/15 border border-[#2481cc]/40 rounded-lg text-xs font-mono text-[#2481cc]">
                <Clock className="w-3.5 h-3.5 animate-spin" />
                <span>الدفعة القادمة: {Math.floor(countdownSeconds / 60)}:{('0' + (countdownSeconds % 60)).slice(-2)}</span>
              </div>
            )}
            <button
              onClick={() => setActiveModal('none')}
              className="p-1.5 rounded-lg text-gray-400 hover:text-white hover:bg-white/10 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex items-center px-4 bg-[#1b2530] border-b border-[#242f3d] overflow-x-auto no-scrollbar text-xs sm:text-sm">
          <button
            onClick={() => setActiveTab('broadcast')}
            className={`flex items-center gap-2 py-3 px-4 border-b-2 font-medium transition-colors shrink-0 ${
              activeTab === 'broadcast'
                ? 'border-[#2481cc] text-[#2481cc]'
                : 'border-transparent text-gray-400 hover:text-gray-200'
            }`}
          >
            <Send className="w-4 h-4" />
            <span>{isArabic ? 'الإرسال الآلي' : 'Broadcast'}</span>
          </button>

          <button
            onClick={() => setActiveTab('monitor')}
            className={`flex items-center gap-2 py-3 px-4 border-b-2 font-medium transition-colors shrink-0 ${
              activeTab === 'monitor'
                ? 'border-[#2481cc] text-[#2481cc]'
                : 'border-transparent text-gray-400 hover:text-gray-200'
            }`}
          >
            <Activity className="w-4 h-4" />
            <span>{isArabic ? 'رصد الكلمات المفتاحية' : 'Keyword Monitor'}</span>
            {isMonitoring && <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />}
          </button>

          <button
            onClick={() => setActiveTab('joiner')}
            className={`flex items-center gap-2 py-3 px-4 border-b-2 font-medium transition-colors shrink-0 ${
              activeTab === 'joiner'
                ? 'border-[#2481cc] text-[#2481cc]'
                : 'border-transparent text-gray-400 hover:text-gray-200'
            }`}
          >
            <Users className="w-4 h-4" />
            <span>{isArabic ? 'الانضمام وفحص المجموعات' : 'Joiner & Pre-Check'}</span>
          </button>

          <button
            onClick={() => setActiveTab('reports')}
            className={`flex items-center gap-2 py-3 px-4 border-b-2 font-medium transition-colors shrink-0 ${
              activeTab === 'reports'
                ? 'border-[#2481cc] text-[#2481cc]'
                : 'border-transparent text-gray-400 hover:text-gray-200'
            }`}
          >
            <Layers className="w-4 h-4" />
            <span>{isArabic ? 'السجلات والتقارير' : 'Reports & Logs'}</span>
            {reports.length > 0 && (
              <span className="text-[10px] bg-emerald-500/20 text-emerald-400 px-1.5 py-0.2 rounded-full">
                {reports.length}
              </span>
            )}
          </button>
        </div>

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6">
          {/* ==================================================== */}
          {/* TAB 1: BROADCAST SENDER */}
          {/* ==================================================== */}
          {activeTab === 'broadcast' && (
            <div className="space-y-6">
              {/* Dispatch Type Selector */}
              <div className="bg-[#202b36] p-4 rounded-xl border border-[#242f3d]">
                <label className="block text-xs font-semibold text-gray-300 mb-2">
                  {isArabic ? 'نوع الإرسال المطلوب:' : 'Dispatch Mode:'}
                </label>
                <div className="grid grid-cols-3 gap-2">
                  {[
                    { id: 'manual', titleAr: 'يدوي (فوري)', titleEn: 'Instant', desc: 'إرسال دفعة واحدة لمرة واحدة' },
                    { id: 'scheduled', titleAr: 'مجدول (دوري)', titleEn: 'Scheduled', desc: 'إعادة إرسال كل X دقيقة' },
                    { id: 'sequential', titleAr: 'متسلسل (دوري)', titleEn: 'Sequential', desc: 'رسائل مختلفة بالتناوب' },
                  ].map((opt) => (
                    <button
                      key={opt.id}
                      type="button"
                      onClick={() => setDispatchType(opt.id as any)}
                      className={`p-3 rounded-xl border text-start transition-all ${
                        dispatchType === opt.id
                          ? 'bg-[#2481cc]/20 border-[#2481cc] text-white'
                          : 'bg-[#17212b] border-[#242f3d] text-gray-400 hover:border-gray-600'
                      }`}
                    >
                      <div className="font-semibold text-xs sm:text-sm text-white">
                        {isArabic ? opt.titleAr : opt.titleEn}
                      </div>
                      <div className="text-[10px] text-gray-400 mt-1 leading-tight">{opt.desc}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Message Content (Instant & Scheduled) */}
              {dispatchType !== 'sequential' ? (
                <div className="bg-[#202b36] p-4 rounded-xl border border-[#242f3d] space-y-3">
                  <div className="flex items-center justify-between">
                    <label className="text-xs font-semibold text-gray-300">
                      {isArabic ? 'نص الرسالة الموحدة:' : 'Message Content:'}
                    </label>
                    <button
                      type="button"
                      onClick={() => fileInputRef.current?.click()}
                      className="flex items-center gap-1 text-xs text-[#2481cc] hover:underline"
                    >
                      <ImageIcon className="w-3.5 h-3.5" />
                      <span>{isArabic ? 'إرفاق صورة مؤقتة' : 'Attach Image'}</span>
                    </button>
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept="image/*"
                      multiple
                      className="hidden"
                      onChange={handleImageUpload}
                    />
                  </div>

                  <textarea
                    rows={4}
                    value={messageText}
                    onChange={(e) => setMessageText(e.target.value)}
                    placeholder={isArabic ? 'اكتب الرسالة التي تريد إرسالها إلى المجموعات...' : 'Type broadcast message...'}
                    className="w-full bg-[#17212b] border border-[#242f3d] rounded-xl p-3 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-[#2481cc]"
                  />

                  {/* Image Previews */}
                  {images.length > 0 && (
                    <div className="flex items-center gap-3 overflow-x-auto py-2">
                      {images.map((img, idx) => (
                        <div key={idx} className="relative w-16 h-16 rounded-lg overflow-hidden border border-[#242f3d] shrink-0">
                          <img src={img} alt="preview" className="w-full h-full object-cover" />
                          <button
                            type="button"
                            onClick={() => setImages((prev) => prev.filter((_, i) => i !== idx))}
                            className="absolute top-1 right-1 bg-red-600/80 p-0.5 rounded-full text-white"
                          >
                            <X className="w-3 h-3" />
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ) : (
                /* Sequential Multiple Messages */
                <div className="bg-[#202b36] p-4 rounded-xl border border-[#242f3d] space-y-3">
                  <div className="flex items-center justify-between">
                    <label className="text-xs font-semibold text-gray-300">
                      {isArabic ? 'قائمة الرسائل المتسلسلة (تُرسل بالتناوب):' : 'Sequential Messages Cycle:'}
                    </label>
                    <button
                      type="button"
                      onClick={() => setSequentialMessages((prev) => [...prev, ''])}
                      className="flex items-center gap-1 text-xs text-[#2481cc] hover:underline"
                    >
                      <ListPlus className="w-3.5 h-3.5" />
                      <span>{isArabic ? 'إضافة رسالة أخرى' : 'Add Message'}</span>
                    </button>
                  </div>

                  {sequentialMessages.map((msg, idx) => (
                    <div key={idx} className="flex gap-2 items-start">
                      <span className="text-xs text-gray-400 font-mono mt-2">{idx + 1}.</span>
                      <textarea
                        rows={2}
                        value={msg}
                        onChange={(e) => {
                          const val = e.target.value;
                          setSequentialMessages((prev) => prev.map((m, i) => (i === idx ? val : m)));
                        }}
                        placeholder={`نص الرسالة رقم ${idx + 1}...`}
                        className="flex-1 bg-[#17212b] border border-[#242f3d] rounded-xl p-2.5 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-[#2481cc]"
                      />
                      {sequentialMessages.length > 1 && (
                        <button
                          type="button"
                          onClick={() => setSequentialMessages((prev) => prev.filter((_, i) => i !== idx))}
                          className="p-1.5 text-gray-500 hover:text-red-400"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              )}

              {/* Intervals & Run Duration (For Scheduled / Sequential) */}
              {dispatchType !== 'manual' && (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 bg-[#202b36] p-4 rounded-xl border border-[#242f3d]">
                  <div>
                    <label className="block text-xs font-semibold text-gray-300 mb-1">
                      {isArabic ? 'الفاصل الزمني بين كل دفعة (بالدقائق):' : 'Interval (Minutes):'}
                    </label>
                    <input
                      type="number"
                      min={1}
                      value={intervalMinutes}
                      onChange={(e) => setIntervalMinutes(Math.max(1, parseInt(e.target.value, 10) || 1))}
                      className="w-full bg-[#17212b] border border-[#242f3d] rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-[#2481cc]"
                    />
                    <p className="text-[11px] text-gray-400 mt-1">يُوصى بـ 60 دقيقة فأكثر لتجنب قيود تيليجرام</p>
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-gray-300 mb-1">
                      {isArabic ? 'مدة التشغيل الكلية (بالساعات):' : 'Total Duration (Hours):'}
                    </label>
                    <input
                      type="number"
                      min={0}
                      value={totalHours}
                      onChange={(e) => setTotalHours(Math.max(0, parseInt(e.target.value, 10) || 0))}
                      className="w-full bg-[#17212b] border border-[#242f3d] rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-[#2481cc]"
                    />
                    <p className="text-[11px] text-gray-400 mt-1">0 تعني العمل باستمرار دون توقف</p>
                  </div>
                </div>
              )}

              {/* Protection Shield Mode */}
              <div className="bg-[#202b36] p-4 rounded-xl border border-[#242f3d] space-y-3">
                <div className="flex items-center gap-2">
                  <Shield className="w-4 h-4 text-emerald-400" />
                  <label className="text-xs font-semibold text-gray-300">
                    {isArabic ? 'وضع الحماية والذكاء السلوكي:' : 'Protection & Behavior Mode:'}
                  </label>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
                  {[
                    { id: 'salam', title: 'السلام عليكم (افتراضي)', desc: 'إرسال تحية، انتظار تفاعل الأعضاء، ثم تعديل النص' },
                    { id: 'smart', title: 'الوضع الذكي', desc: 'حذف الروابط والإعلانات تلقائياً في القروبات المحمية' },
                    { id: 'convert_links', title: 'تحويل الروابط', desc: 'استبدال روابط واتساب بنصوص واضحة آمنة' },
                    { id: 'skip', title: 'تخطي المحمي', desc: 'استبعاد المجموعات التي تحتوي على بوتات حماية' },
                    { id: 'off', title: 'إيقاف الفحص', desc: 'إرسال النص كما هو دون أي فحص أو تعديل' },
                  ].map((p) => (
                    <button
                      key={p.id}
                      type="button"
                      onClick={() => setProtectionMode(p.id as any)}
                      className={`p-3 rounded-xl border text-start transition-all ${
                        protectionMode === p.id
                          ? 'bg-emerald-500/15 border-emerald-500 text-white'
                          : 'bg-[#17212b] border-[#242f3d] text-gray-400 hover:border-gray-600'
                      }`}
                    >
                      <div className="font-semibold text-xs text-white">{p.title}</div>
                      <div className="text-[10px] text-gray-400 mt-1 leading-tight">{p.desc}</div>
                    </button>
                  ))}
                </div>

                {protectionMode === 'salam' && (
                  <div className="pt-2 border-t border-[#242f3d] flex items-center justify-between">
                    <span className="text-xs text-gray-400">
                      {isArabic ? 'عدد رسائل الأعضاء المطلوبة قبل تعديل السلام إلى النص الكامل:' : 'Member messages before text edit:'}
                    </span>
                    <input
                      type="number"
                      min={1}
                      max={50}
                      value={requiredMemberMessages}
                      onChange={(e) => setRequiredMemberMessages(Math.max(1, parseInt(e.target.value, 10) || 1))}
                      className="w-20 bg-[#17212b] border border-[#242f3d] rounded-lg px-2 py-1 text-xs text-center text-white"
                    />
                  </div>
                )}
              </div>

              {/* Target Groups Input */}
              <div className="bg-[#202b36] p-4 rounded-xl border border-[#242f3d] space-y-3">
                <div className="flex items-center justify-between flex-wrap gap-2">
                  <div className="flex items-center gap-2">
                    <Users className="w-4 h-4 text-[#2481cc]" />
                    <label className="text-xs font-semibold text-gray-300">
                      {isArabic ? 'قائمة المجموعات المستهدفة:' : 'Target Groups:'}
                    </label>
                  </div>

                  <div className="flex items-center gap-2 flex-wrap">
                    {!sendToAllGroups && (
                      <button
                        type="button"
                        onClick={() => setIsChatPickerOpen(true)}
                        className="px-2.5 py-1.5 bg-[#2481cc]/20 hover:bg-[#2481cc]/30 text-[#2481cc] border border-[#2481cc]/40 rounded-xl text-xs font-bold flex items-center gap-1.5 transition-all shadow-sm active:scale-95"
                        title={isArabic ? 'فتح نافذة مصغرة للواجهة الرئيسية للدردشات لاختيار وتأكيد المجموعات' : 'Open chat picker'}
                      >
                        <Layers className="w-3.5 h-3.5 text-[#2481cc]" />
                        <span>{isArabic ? 'جلب كل المجموعات (نافذة الدردشات)' : 'Fetch All Groups'}</span>
                      </button>
                    )}

                    <label className="flex items-center gap-1.5 cursor-pointer text-xs text-gray-300">
                      <input
                        type="checkbox"
                        checked={sendToAllGroups}
                        onChange={(e) => setSendToAllGroups(e.target.checked)}
                        className="rounded bg-[#17212b] border-[#242f3d] text-[#2481cc]"
                      />
                      <span>{isArabic ? 'الإرسال لكل مجموعاتي بالحساب' : 'Send to all account chats'}</span>
                    </label>

                    {!sendToAllGroups && (
                      <button
                        type="button"
                        onClick={handleCleanGroups}
                        className="text-xs text-[#2481cc] hover:underline"
                      >
                        {isArabic ? 'تنظيف وحذف التكرار' : 'Sanitize & Deduplicate'}
                      </button>
                    )}
                  </div>
                </div>

                {!sendToAllGroups && (
                  <textarea
                    rows={4}
                    value={groupsInput}
                    onChange={(e) => setGroupsInput(e.target.value)}
                    placeholder={
                      isArabic
                        ? 'ضع رابط كل مجموعة أو معرفها في سطر منفصل...\nمثال:\nhttps://t.me/group_example\n@my_group_name'
                        : 'Enter one group link or username per line...'
                    }
                    className="w-full bg-[#17212b] border border-[#242f3d] rounded-xl p-3 text-xs sm:text-sm text-white placeholder-gray-500 focus:outline-none focus:border-[#2481cc] font-mono"
                  />
                )}
              </div>

              {/* Action Buttons */}
              <div className="flex items-center gap-3 pt-2">
                {!isDispatching ? (
                  <button
                    type="button"
                    onClick={handleStartDispatch}
                    className="flex-1 bg-[#2481cc] hover:bg-[#2074b8] text-white py-3 px-4 rounded-xl text-sm font-semibold flex items-center justify-center gap-2 shadow-lg transition-all"
                  >
                    <Play className="w-4 h-4" />
                    <span>
                      {dispatchType === 'manual'
                        ? (isArabic ? 'إرسال الدفعة فوراً' : 'Dispatch Now')
                        : (isArabic ? 'بدء الإرسال المستمر والجدولة' : 'Start Scheduled Dispatch')}
                    </span>
                  </button>
                ) : (
                  <button
                    type="button"
                    onClick={handleStopDispatch}
                    className="flex-1 bg-red-600 hover:bg-red-700 text-white py-3 px-4 rounded-xl text-sm font-semibold flex items-center justify-center gap-2 shadow-lg transition-all"
                  >
                    <Square className="w-4 h-4" />
                    <span>{isArabic ? 'إيقاف الإرسال التلقائي' : 'Stop Automation'}</span>
                  </button>
                )}

                <button
                  type="button"
                  onClick={handlePreCheck}
                  disabled={isPreChecking}
                  className="bg-[#202b36] hover:bg-[#253240] border border-[#242f3d] text-gray-200 py-3 px-4 rounded-xl text-sm font-medium flex items-center gap-2 transition-colors disabled:opacity-50"
                >
                  <RotateCw className={`w-4 h-4 ${isPreChecking ? 'animate-spin' : ''}`} />
                  <span>{isArabic ? 'فحص المجموعات مسبقاً' : 'Pre-Check'}</span>
                </button>
              </div>
            </div>
          )}

          {/* ==================================================== */}
          {/* TAB 2: KEYWORD MONITORING */}
          {/* ==================================================== */}
          {activeTab === 'monitor' && (
            <div className="space-y-6">
              {/* Monitor Status Header */}
              <div className="bg-[#202b36] p-4 rounded-xl border border-[#242f3d] flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <span className={`w-3 h-3 rounded-full ${isMonitoring ? 'bg-emerald-500 animate-pulse' : 'bg-gray-500'}`} />
                    <h3 className="font-bold text-sm">
                      {isMonitoring ? (isArabic ? 'المراقبة الآلية نشطة' : 'Monitoring Active') : (isArabic ? 'المراقبة متوقفة' : 'Monitoring Stopped')}
                    </h3>
                  </div>
                  <p className="text-xs text-gray-400 mt-1">
                    {isArabic
                      ? 'يتم الاستماع لجميع الرسائل في الحساب، والتنبيه بالنافذة والرسائل المحفوظة'
                      : 'Listening account-wide, alerts sent to Saved Messages & UI'}
                  </p>
                </div>

                <button
                  type="button"
                  onClick={handleToggleMonitor}
                  className={`px-5 py-2.5 rounded-xl text-xs font-semibold transition-all ${
                    isMonitoring
                      ? 'bg-red-600 hover:bg-red-700 text-white'
                      : 'bg-emerald-600 hover:bg-emerald-700 text-white'
                  }`}
                >
                  {isMonitoring ? (isArabic ? 'إيقاف المراقبة' : 'Stop') : (isArabic ? 'بدء المراقبة الآن' : 'Start Monitor')}
                </button>
              </div>

              {/* Keywords Input */}
              <div className="bg-[#202b36] p-4 rounded-xl border border-[#242f3d] space-y-2">
                <div className="flex items-center justify-between">
                  <label className="text-xs font-semibold text-gray-300">
                    {isArabic ? 'الكلمات المفتاحية للرصد (كل كلمة في سطر):' : 'Monitored Keywords (one per line):'}
                  </label>
                  <button
                    type="button"
                    onClick={saveCurrentConfig}
                    className="text-xs text-[#2481cc] hover:underline"
                  >
                    {isArabic ? 'حفظ فوري' : 'Save'}
                  </button>
                </div>

                <textarea
                  rows={4}
                  value={keywordsInput}
                  onChange={(e) => setKeywordsInput(e.target.value)}
                  placeholder={isArabic ? 'وظيفة\nمطلوب\nإيجار\nخدمات\nتواصل' : 'hiring\nproject\nurgent'}
                  className="w-full bg-[#17212b] border border-[#242f3d] rounded-xl p-3 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-[#2481cc]"
                />
                <p className="text-[11px] text-gray-400">
                  {isArabic
                    ? '✨ يتم تطبيع الحروف تلقائياً (إزالة التشكيل، توحيد الهمزات والتاء المربوطة)'
                    : 'Diacritics stripped and Arabic letters normalized automatically'}
                </p>
              </div>

              {/* Browser Web Notifications Button */}
              <div className="flex items-center justify-between bg-[#1b2530] p-3 rounded-xl border border-[#242f3d]">
                <div className="flex items-center gap-2">
                  <Bell className="w-4 h-4 text-yellow-400" />
                  <span className="text-xs text-gray-300">
                    {isArabic ? 'إشعارات الويب للمتصفح والهاتف:' : 'Web browser notifications:'}
                  </span>
                </div>
                <button
                  type="button"
                  onClick={requestNotificationPermission}
                  className="text-xs bg-[#2481cc]/20 border border-[#2481cc]/40 text-[#2481cc] px-3 py-1 rounded-lg"
                >
                  {browserNotificationsEnabled ? (isArabic ? 'مفعلة ✅' : 'Enabled ✅') : (isArabic ? 'تفعيل الإشعارات' : 'Enable')}
                </button>
              </div>

              {/* Monitored Alerts Stream */}
              <div className="space-y-3">
                <h4 className="text-xs font-semibold text-gray-300 flex items-center justify-between">
                  <span>{isArabic ? 'الرسائل المرصودة لحظياً:' : 'Real-Time Captured Alerts:'}</span>
                  <span className="text-gray-500">{alerts.length} تنبيه</span>
                </h4>

                {alerts.length === 0 ? (
                  <div className="p-8 text-center text-xs text-gray-500 bg-[#202b36]/50 rounded-xl border border-dashed border-[#242f3d]">
                    {isArabic ? 'لم يتم رصد رسائل بعد. شغّل المراقبة وانتظر وصول الرسائل المطابقة.' : 'No alerts captured yet.'}
                  </div>
                ) : (
                  <div className="space-y-2 max-h-64 overflow-y-auto pr-1">
                    {alerts.map((a) => (
                      <div
                        key={a.id}
                        className="bg-[#202b36] border border-[#242f3d] p-3 rounded-xl flex flex-col gap-1 text-xs"
                      >
                        <div className="flex items-center justify-between">
                          <span className="bg-[#2481cc]/20 text-[#2481cc] font-semibold px-2 py-0.5 rounded-md">
                            {a.keyword}
                          </span>
                          <span className="text-gray-400 font-mono text-[10px]">{a.timestamp}</span>
                        </div>
                        <div className="flex items-center gap-2 text-gray-300 font-medium">
                          <span>📍 {a.chatTitle}</span>
                          <span>•</span>
                          <span>👤 {a.senderName}</span>
                        </div>
                        <p className="text-gray-300 bg-[#17212b] p-2 rounded-lg mt-1 whitespace-pre-wrap">
                          {a.text}
                        </p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* ==================================================== */}
          {/* TAB 3: ADVANCED JOINER & PRE-CHECK */}
          {/* ==================================================== */}
          {activeTab === 'joiner' && (
            <div className="space-y-6">
              {/* Pre-Check Results Section */}
              <div className="bg-[#202b36] p-4 rounded-xl border border-[#242f3d] space-y-3">
                <div className="flex items-center justify-between">
                  <h3 className="text-xs font-semibold text-gray-300">
                    {isArabic ? 'نتائج الفحص المسبق للمجموعات وبوتات الحماية:' : 'Pre-Check Analysis Results:'}
                  </h3>
                  <button
                    type="button"
                    onClick={handlePreCheck}
                    disabled={isPreChecking}
                    className="text-xs text-[#2481cc] hover:underline"
                  >
                    {isArabic ? 'إعادة الفحص' : 'Re-check'}
                  </button>
                </div>

                {preCheckResults.length === 0 ? (
                  <p className="text-xs text-gray-500 py-3 text-center">
                    {isArabic
                      ? 'اضغط زر "فحص المجموعات مسبقاً" في تبويب الإرسال لتحليل وجود بوتات الحماية والعضوية.'
                      : 'Click Pre-Check to test target groups for protection bots.'}
                  </p>
                ) : (
                  <div className="space-y-2 max-h-56 overflow-y-auto">
                    {preCheckResults.map((item, idx) => (
                      <div
                        key={idx}
                        className="bg-[#17212b] p-3 rounded-xl border border-[#242f3d] flex items-center justify-between text-xs"
                      >
                        <div>
                          <div className="font-semibold text-white">{item.title}</div>
                          <div className="text-[11px] text-gray-400 font-mono">{item.normalizedPeer}</div>
                        </div>

                        <div className="flex items-center gap-2">
                          <span
                            className={`px-2 py-0.5 rounded-full text-[10px] font-medium ${
                              item.isMember
                                ? 'bg-emerald-500/20 text-emerald-400'
                                : 'bg-yellow-500/20 text-yellow-400'
                            }`}
                          >
                            {item.isMember ? (isArabic ? 'عضو ✅' : 'Member') : (isArabic ? 'غير منضم ⚠️' : 'Not Member')}
                          </span>

                          <span
                            className={`px-2 py-0.5 rounded-full text-[10px] font-medium ${
                              item.isProtected
                                ? 'bg-red-500/20 text-red-400'
                                : 'bg-emerald-500/20 text-emerald-400'
                            }`}
                          >
                            {item.isProtected
                              ? (isArabic ? `محمي (${item.protectionBotName || 'بوت'}) 🛡️` : 'Protected 🛡️')
                              : (isArabic ? 'آمن بدون بوتات' : 'Safe')}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Advanced Multi-Source Auto-Joiner */}
              <div className="bg-[#202b36] p-4 rounded-xl border border-[#242f3d] space-y-3">
                <div className="flex items-center justify-between">
                  <h3 className="text-xs font-semibold text-gray-300">
                    {isArabic ? 'الانضمام المتقدم (روابط مباشرة، صفحات ويب خارجية، وأسماء):' : 'Advanced Multi-Source Auto-Joiner:'}
                  </h3>
                  {joinerState.status !== 'idle' && (
                    <span className="text-xs text-[#2481cc] font-mono font-semibold">
                      الحالة: {joinerState.status}
                    </span>
                  )}
                </div>

                <textarea
                  rows={4}
                  value={joinerInput}
                  onChange={(e) => setJoinerInput(e.target.value)}
                  placeholder={
                    isArabic
                      ? 'ضع نصوصاً مختلطة، روابط تيليجرام، روابط دعوة، أو حتى روابط صفحات خارجية تحتوي على روابط تيليجرام...\nسيقوم النظام باستخراج الروابط تلقائياً والانضمام بفاصل زمني آمن.'
                      : 'Enter direct links, invite links, or external websites containing Telegram channels...'
                  }
                  className="w-full bg-[#17212b] border border-[#242f3d] rounded-xl p-3 text-xs sm:text-sm text-white placeholder-gray-500 focus:outline-none focus:border-[#2481cc] font-mono"
                />

                <div className="flex items-center gap-2 flex-wrap">
                  <button
                    type="button"
                    onClick={handleStartJoiner}
                    className="bg-[#2481cc] hover:bg-[#2074b8] text-white py-2 px-4 rounded-xl text-xs font-semibold flex items-center gap-1.5"
                  >
                    <Play className="w-3.5 h-3.5" />
                    <span>{isArabic ? 'بدء الانضمام الذكي' : 'Start Joining'}</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => handleJoinerControl('pause')}
                    className="bg-[#17212b] border border-[#242f3d] text-gray-300 hover:text-white py-2 px-3 rounded-xl text-xs flex items-center gap-1"
                  >
                    <Pause className="w-3.5 h-3.5" />
                    <span>{isArabic ? 'إيقاف مؤقت' : 'Pause'}</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => handleJoinerControl('resume')}
                    className="bg-[#17212b] border border-[#242f3d] text-gray-300 hover:text-white py-2 px-3 rounded-xl text-xs flex items-center gap-1"
                  >
                    <RotateCw className="w-3.5 h-3.5" />
                    <span>{isArabic ? 'استئناف' : 'Resume'}</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => handleJoinerControl('stop')}
                    className="bg-red-600/20 border border-red-500/40 text-red-400 hover:bg-red-600/30 py-2 px-3 rounded-xl text-xs flex items-center gap-1"
                  >
                    <Square className="w-3.5 h-3.5" />
                    <span>{isArabic ? 'إلغاء نهائي' : 'Stop'}</span>
                  </button>
                </div>

                {/* Joiner Progress Stats */}
                {joinerState.total > 0 && (
                  <div className="grid grid-cols-4 gap-2 pt-2 text-center text-xs">
                    <div className="bg-[#17212b] p-2 rounded-lg border border-[#242f3d]">
                      <span className="text-gray-400 block text-[10px]">الإجمالي</span>
                      <span className="font-bold text-white">{joinerState.total}</span>
                    </div>
                    <div className="bg-[#17212b] p-2 rounded-lg border border-[#242f3d]">
                      <span className="text-emerald-400 block text-[10px]">ناجح</span>
                      <span className="font-bold text-emerald-400">{joinerState.joined}</span>
                    </div>
                    <div className="bg-[#17212b] p-2 rounded-lg border border-[#242f3d]">
                      <span className="text-yellow-400 block text-[10px]">مستثنى</span>
                      <span className="font-bold text-yellow-400">{joinerState.skipped}</span>
                    </div>
                    <div className="bg-[#17212b] p-2 rounded-lg border border-[#242f3d]">
                      <span className="text-red-400 block text-[10px]">فشل</span>
                      <span className="font-bold text-red-400">{joinerState.failed}</span>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* ==================================================== */}
          {/* TAB 4: REPORTS & LIVE LOGS */}
          {/* ==================================================== */}
          {activeTab === 'reports' && (
            <div className="space-y-6">
              {/* Batch Reports Summary */}
              <div className="space-y-3">
                <h3 className="text-xs font-semibold text-gray-300">
                  {isArabic ? 'تقارير الدفعات المنفذة (المحفوظة في الرسائل الخاصة):' : 'Batch Reports History:'}
                </h3>

                {reports.length === 0 ? (
                  <p className="text-xs text-gray-500 p-4 text-center bg-[#202b36] rounded-xl border border-[#242f3d]">
                    {isArabic ? 'لا توجد دفعات مكتملة حتى الآن. أطلق دفعة إرسال وستظهر النتائج هنا وفي رسائلك المحفوظة.' : 'No completed batches yet.'}
                  </p>
                ) : (
                  <div className="space-y-3">
                    {reports.map((r) => (
                      <div key={r.batchId} className="bg-[#202b36] border border-[#242f3d] p-4 rounded-xl text-xs space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-[#2481cc] font-mono">{r.batchId}</span>
                          <span className="text-gray-400 font-mono">{r.timestamp}</span>
                        </div>
                        <div className="grid grid-cols-4 gap-2 text-center text-[11px] pt-1">
                          <div className="bg-[#17212b] p-1.5 rounded-md">المجموع: {r.totalGroups}</div>
                          <div className="bg-[#17212b] p-1.5 rounded-md text-emerald-400">ناجح: {r.successCount}</div>
                          <div className="bg-[#17212b] p-1.5 rounded-md text-yellow-400">مستثنى: {r.skippedCount}</div>
                          <div className="bg-[#17212b] p-1.5 rounded-md text-red-400">فشل: {r.failCount}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Real-Time Live Logs */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <h3 className="text-xs font-semibold text-gray-300">
                    {isArabic ? 'سجل العمليات والنبضات الحية (Real-Time Console):' : 'Live Activity Console:'}
                  </h3>
                  <button
                    type="button"
                    onClick={() => setLiveLogs([])}
                    className="text-xs text-gray-400 hover:text-white"
                  >
                    {isArabic ? 'مسح السجل' : 'Clear'}
                  </button>
                </div>

                <div className="bg-[#101921] border border-[#242f3d] rounded-xl p-3 h-52 overflow-y-auto font-mono text-[11px] text-gray-300 space-y-1">
                  {liveLogs.length === 0 ? (
                    <span className="text-gray-600">لا توجد عمليات جارية حالياً...</span>
                  ) : (
                    liveLogs.map((log, idx) => (
                      <div key={idx} className="leading-relaxed">
                        {log}
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer Bar */}
        <div className="p-3 bg-[#17212b] border-t border-[#242f3d] flex items-center justify-between text-xs text-gray-400">
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span>{isArabic ? 'الخادم متصل ومستقر (MTProto 2.0 Layer 184)' : 'MTProto Connected'}</span>
          </span>
          <button
            onClick={() => setActiveModal('none')}
            className="px-4 py-1.5 bg-[#202b36] hover:bg-[#253240] rounded-lg text-white transition-colors"
          >
            {isArabic ? 'إغلاق' : 'Close'}
          </button>
        </div>
      </div>

      {/* Miniature Chat Picker Modal (الواجهة المصغرة للدردشات لاختيار المجموعات) */}
      <ChatPickerModal
        isOpen={isChatPickerOpen}
        onClose={() => setIsChatPickerOpen(false)}
        onConfirm={handleChatsPicked}
        alreadySelectedLinks={groupsInput.split('\n').map((s) => s.trim()).filter(Boolean)}
      />
    </div>
  );
};
