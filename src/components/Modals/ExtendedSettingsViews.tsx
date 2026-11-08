import React, { useState, useEffect } from 'react';
import {
  ArrowLeft,
  ArrowRight,
  Sparkles,
  Camera,
  Eye,
  EyeOff,
  Sliders,
  MessageSquare,
  Hash,
  FileText,
  Image,
  Film,
  Music,
  Download,
  Trash2,
  Megaphone,
  Cloud,
  CloudRain,
  UploadCloud,
  DownloadCloud,
  Check,
  RefreshCw,
  Layers,
  CornerDownRight,
  Type,
  Share2,
  Star,
  Zap,
  Shield,
  Gift,
  HelpCircle,
  Settings,
  Users,
  Menu,
  User,
  Phone,
  Folder,
  CheckCheck,
  Bell,
  Volume2,
  Lock,
  Smartphone,
  HardDrive,
} from 'lucide-react';
import { useTelegram } from '../../context/TelegramContext';
import { AccountInstance } from '../../core/messenger/AccountInstance';
import { TLRPC } from '../../core/TLRPC';

interface SubViewProps {
  onBack: () => void;
}

// ============================================================================
// 1. STORIES SETTINGS VIEW (إعدادات القصص)
// ============================================================================
export const StoriesSettingsView: React.FC<SubViewProps> = ({ onBack }) => {
  const { settings, showToast, activeAccountId } = useTelegram();
  const isArabic = settings.language === 'ar';
  const BackIcon = isArabic ? ArrowRight : ArrowLeft;

  const rawAccId = activeAccountId ?? 0;
  const accountNum = typeof rawAccId === 'number' ? rawAccId : (parseInt(String(rawAccId).replace(/\D/g, '') || '0', 10) % 4);
  const storiesCtrl = AccountInstance.getInstance(accountNum).getStoriesController();

  const [enabled, setEnabled] = useState(storiesCtrl.storiesEnabled);
  const [qualityFull, setQualityFull] = useState(storiesCtrl.storyQualityFull);
  const [stealthMode, setStealthMode] = useState(storiesCtrl.stealthMode);
  const [saveToGallery, setSaveToGallery] = useState(false);

  const handleToggleEnabled = (val: boolean) => {
    setEnabled(val);
    storiesCtrl.storiesEnabled = val;
    storiesCtrl.saveSettings();
    showToast(isArabic ? 'تم تحديث إعدادات القصص' : 'Stories settings updated');
  };

  const handleToggleQuality = (val: boolean) => {
    setQualityFull(val);
    storiesCtrl.storyQualityFull = val;
    storiesCtrl.saveSettings();
    showToast(isArabic ? 'تم تحديث جودة رفع القصص' : 'Story upload quality updated');
  };

  const handleToggleStealth = (val: boolean) => {
    setStealthMode(val);
    storiesCtrl.stealthMode = val;
    storiesCtrl.saveSettings();
    showToast(isArabic ? 'تم تحديث وضع التخفي' : 'Stealth mode updated');
  };

  return (
    <div className="flex flex-col h-full bg-[#0e1621] text-white">
      <div className="flex items-center gap-3 px-4 py-3 bg-[#17212b] border-b border-white/10 shrink-0">
        <button onClick={onBack} className="p-1 hover:bg-white/10 rounded-full transition-colors">
          <BackIcon className="w-5 h-5 text-gray-300" />
        </button>
        <div className="text-base font-semibold">{isArabic ? 'القصص' : 'Stories'}</div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Info Header */}
        <div className="p-4 bg-[#17212b] rounded-2xl border border-white/5 flex items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-amber-500 to-rose-500 flex items-center justify-center shrink-0 shadow-lg shadow-rose-500/20">
            <Camera className="w-6 h-6 text-white" />
          </div>
          <div>
            <div className="font-semibold text-sm">{isArabic ? 'مشاركة اللحظات والقصص' : 'Share Moments & Stories'}</div>
            <div className="text-xs text-gray-400 mt-0.5">
              {isArabic ? 'إدارة دقة القصص، الخصوصية، ووضع التخفي' : 'Manage story resolution, privacy and stealth mode'}
            </div>
          </div>
        </div>

        {/* Toggles */}
        <div className="bg-[#17212b] rounded-2xl border border-white/5 divide-y divide-white/5">
          <div className="flex items-center justify-between p-4">
            <div>
              <div className="text-sm font-medium">{isArabic ? 'تفعيل شريط القصص' : 'Enable Stories Bar'}</div>
              <div className="text-xs text-gray-400 mt-0.5">
                {isArabic ? 'إظهار شريط القصص أعلى قائمة المحادثات' : 'Display stories avatar row above dialogs'}
              </div>
            </div>
            <input
              type="checkbox"
              checked={enabled}
              onChange={(e) => handleToggleEnabled(e.target.checked)}
              className="w-5 h-5 accent-[#5288c1] rounded cursor-pointer"
            />
          </div>

          <div className="flex items-center justify-between p-4">
            <div>
              <div className="text-sm font-medium">{isArabic ? 'جودة فائقة (Full HD)' : 'High Quality (Full HD)'}</div>
              <div className="text-xs text-gray-400 mt-0.5">
                {isArabic ? 'رفع وعرض القصص بأعلى دقة ممكنة' : 'Upload and view stories at maximum clarity'}
              </div>
            </div>
            <input
              type="checkbox"
              checked={qualityFull}
              onChange={(e) => handleToggleQuality(e.target.checked)}
              className="w-5 h-5 accent-[#5288c1] rounded cursor-pointer"
            />
          </div>

          <div className="flex items-center justify-between p-4">
            <div>
              <div className="text-sm font-medium">{isArabic ? 'وضع التخفي (Stealth Mode)' : 'Stealth Mode'}</div>
              <div className="text-xs text-gray-400 mt-0.5">
                {isArabic ? 'إخفاء مشاهدتك لقصص الآخرين لمدة 25 دقيقة' : 'Hide your view footprint on stories'}
              </div>
            </div>
            <input
              type="checkbox"
              checked={stealthMode}
              onChange={(e) => handleToggleStealth(e.target.checked)}
              className="w-5 h-5 accent-[#5288c1] rounded cursor-pointer"
            />
          </div>

          <div className="flex items-center justify-between p-4">
            <div>
              <div className="text-sm font-medium">{isArabic ? 'حفظ تلقائي في المعرض' : 'Save to Gallery'}</div>
              <div className="text-xs text-gray-400 mt-0.5">
                {isArabic ? 'حفظ القصص المنشورة في ألبوم الصور' : 'Save your posted stories to local gallery'}
              </div>
            </div>
            <input
              type="checkbox"
              checked={saveToGallery}
              onChange={(e) => setSaveToGallery(e.target.checked)}
              className="w-5 h-5 accent-[#5288c1] rounded cursor-pointer"
            />
          </div>
        </div>
      </div>
    </div>
  );
};

// ============================================================================
// 2. MESSAGES SETTINGS VIEW (إعدادات الرسائل)
// ============================================================================
export const MessagesSettingsView: React.FC<SubViewProps> = ({ onBack }) => {
  const { settings, updateSettings, showToast } = useTelegram();
  const isArabic = settings.language === 'ar';
  const BackIcon = isArabic ? ArrowRight : ArrowLeft;

  const [cornerRadius, setCornerRadius] = useState(16);
  const [swipeAction, setSwipeAction] = useState('reply');

  return (
    <div className="flex flex-col h-full bg-[#0e1621] text-white">
      <div className="flex items-center gap-3 px-4 py-3 bg-[#17212b] border-b border-white/10 shrink-0">
        <button onClick={onBack} className="p-1 hover:bg-white/10 rounded-full transition-colors">
          <BackIcon className="w-5 h-5 text-gray-300" />
        </button>
        <div className="text-base font-semibold">{isArabic ? 'الرسائل' : 'Messages'}</div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Preview Bubbles */}
        <div className="p-4 bg-[#17212b] rounded-2xl border border-white/5 space-y-3">
          <div className="text-xs font-bold text-[#5288c1] uppercase">{isArabic ? 'معاينة الفقاعات' : 'Bubble Preview'}</div>
          <div className="space-y-2">
            <div
              style={{ borderRadius: `${cornerRadius}px` }}
              className="p-3 bg-[#2b5278] text-white text-xs max-w-[80%] mr-auto rounded-tl-sm shadow"
            >
              {isArabic ? 'مرحباً! هذه معاينة لحجم وشكل فقاعات الرسائل.' : 'Hello! This is a preview of your message bubble styling.'}
            </div>
            <div
              style={{ borderRadius: `${cornerRadius}px` }}
              className="p-3 bg-[#182533] text-gray-200 text-xs max-w-[80%] ml-auto rounded-tr-sm border border-white/5 shadow"
            >
              {isArabic ? 'تبدو ممتازة وأنيقة ومريحة للقراءة.' : 'Looks crisp, clear and comfortable to read.'}
            </div>
          </div>
        </div>

        {/* Sliders */}
        <div className="bg-[#17212b] rounded-2xl border border-white/5 p-4 space-y-4">
          <div>
            <div className="flex justify-between text-xs mb-1">
              <span>{isArabic ? 'حجم الخط' : 'Text Size'}</span>
              <span className="font-mono text-[#5288c1]">{settings.fontSize || 16}px</span>
            </div>
            <input
              type="range"
              min="12"
              max="24"
              value={settings.fontSize || 16}
              onChange={(e) => updateSettings({ fontSize: Number(e.target.value) })}
              className="w-full accent-[#5288c1] cursor-pointer"
            />
          </div>

          <div>
            <div className="flex justify-between text-xs mb-1">
              <span>{isArabic ? 'انحناء حواف الفقاعات' : 'Corner Radius'}</span>
              <span className="font-mono text-[#5288c1]">{cornerRadius}px</span>
            </div>
            <input
              type="range"
              min="4"
              max="24"
              value={cornerRadius}
              onChange={(e) => setCornerRadius(Number(e.target.value))}
              className="w-full accent-[#5288c1] cursor-pointer"
            />
          </div>
        </div>

        {/* Message Options */}
        <div className="bg-[#17212b] rounded-2xl border border-white/5 divide-y divide-white/5">
          <div className="flex items-center justify-between p-4">
            <div>
              <div className="text-sm font-medium">{isArabic ? 'إرسال بضغطة Enter' : 'Send by Enter'}</div>
              <div className="text-xs text-gray-400 mt-0.5">{isArabic ? 'استخدم زر Enter للإرسال السريع' : 'Send immediately with Enter key'}</div>
            </div>
            <input
              type="checkbox"
              checked={settings.sendByEnter}
              onChange={(e) => updateSettings({ sendByEnter: e.target.checked })}
              className="w-5 h-5 accent-[#5288c1] rounded cursor-pointer"
            />
          </div>

          <div className="flex items-center justify-between p-4">
            <div>
              <div className="text-sm font-medium">{isArabic ? 'مؤثرات الأصوات' : 'Sound Effects'}</div>
              <div className="text-xs text-gray-400 mt-0.5">{isArabic ? 'صوت إرسال واستقبال الرسائل' : 'Play sounds on send and receive'}</div>
            </div>
            <input
              type="checkbox"
              checked={settings.soundEffects}
              onChange={(e) => updateSettings({ soundEffects: e.target.checked })}
              className="w-5 h-5 accent-[#5288c1] rounded cursor-pointer"
            />
          </div>
        </div>
      </div>
    </div>
  );
};

// ============================================================================
// 3. TOPICS & FORUMS VIEW (إعدادات المنتديات والمواضيع)
// ============================================================================
export const TopicsSettingsView: React.FC<SubViewProps> = ({ onBack }) => {
  const { settings, showToast, activeAccountId } = useTelegram();
  const isArabic = settings.language === 'ar';
  const BackIcon = isArabic ? ArrowRight : ArrowLeft;

  const [viewAsTopics, setViewAsTopics] = useState(true);
  const [hideClosed, setHideClosed] = useState(false);
  const [unreadOnly, setUnreadOnly] = useState(false);

  return (
    <div className="flex flex-col h-full bg-[#0e1621] text-white">
      <div className="flex items-center gap-3 px-4 py-3 bg-[#17212b] border-b border-white/10 shrink-0">
        <button onClick={onBack} className="p-1 hover:bg-white/10 rounded-full transition-colors">
          <BackIcon className="w-5 h-5 text-gray-300" />
        </button>
        <div className="text-base font-semibold">{isArabic ? 'المواضيع والمنتديات' : 'Forum Topics'}</div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <div className="p-4 bg-[#17212b] rounded-2xl border border-white/5 flex items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center shrink-0 shadow-lg shadow-blue-500/20">
            <Hash className="w-6 h-6 text-white" />
          </div>
          <div>
            <div className="font-semibold text-sm">{isArabic ? 'تنظيم المجموعات الخارقة' : 'Supergroup Organization'}</div>
            <div className="text-xs text-gray-400 mt-0.5">
              {isArabic ? 'تخصيص نمط عرض مواضيع المنتديات والأقسام' : 'Customize how forum topics and threads appear'}
            </div>
          </div>
        </div>

        <div className="bg-[#17212b] rounded-2xl border border-white/5 divide-y divide-white/5">
          <div className="flex items-center justify-between p-4">
            <div>
              <div className="text-sm font-medium">{isArabic ? 'عرض كمواضيع منفصلة' : 'View as Separate Topics'}</div>
              <div className="text-xs text-gray-400 mt-0.5">{isArabic ? 'تجميع الرسائل تحت كل موضوع' : 'Keep chats organized in distinct tabs'}</div>
            </div>
            <input
              type="checkbox"
              checked={viewAsTopics}
              onChange={(e) => setViewAsTopics(e.target.checked)}
              className="w-5 h-5 accent-[#5288c1] rounded cursor-pointer"
            />
          </div>

          <div className="flex items-center justify-between p-4">
            <div>
              <div className="text-sm font-medium">{isArabic ? 'إخفاء المواضيع المغلقة' : 'Hide Closed Topics'}</div>
              <div className="text-xs text-gray-400 mt-0.5">{isArabic ? 'إخفاء المواضيع المقفلة من قبل المشرفين' : 'Auto-hide topics marked as resolved'}</div>
            </div>
            <input
              type="checkbox"
              checked={hideClosed}
              onChange={(e) => setHideClosed(e.target.checked)}
              className="w-5 h-5 accent-[#5288c1] rounded cursor-pointer"
            />
          </div>

          <div className="flex items-center justify-between p-4">
            <div>
              <div className="text-sm font-medium">{isArabic ? 'إظهار غير المقروءة أولاً' : 'Show Unread First'}</div>
              <div className="text-xs text-gray-400 mt-0.5">{isArabic ? 'ترتيب المواضيع حسب النشاط الأحدث' : 'Sort topics by latest activity'}</div>
            </div>
            <input
              type="checkbox"
              checked={unreadOnly}
              onChange={(e) => setUnreadOnly(e.target.checked)}
              className="w-5 h-5 accent-[#5288c1] rounded cursor-pointer"
            />
          </div>
        </div>
      </div>
    </div>
  );
};

// ============================================================================
// 4. SHARED MEDIA VIEW (الوسائط المشتركة)
// ============================================================================
export const SharedMediaView: React.FC<SubViewProps> = ({ onBack }) => {
  const { settings, showToast } = useTelegram();
  const isArabic = settings.language === 'ar';
  const BackIcon = isArabic ? ArrowRight : ArrowLeft;

  const [activeTab, setActiveTab] = useState<'media' | 'files' | 'music' | 'links'>('media');

  return (
    <div className="flex flex-col h-full bg-[#0e1621] text-white">
      <div className="flex items-center gap-3 px-4 py-3 bg-[#17212b] border-b border-white/10 shrink-0">
        <button onClick={onBack} className="p-1 hover:bg-white/10 rounded-full transition-colors">
          <BackIcon className="w-5 h-5 text-gray-300" />
        </button>
        <div className="text-base font-semibold">{isArabic ? 'الوسائط المشتركة' : 'Shared Media'}</div>
      </div>

      {/* Tabs */}
      <div className="flex items-center bg-[#17212b] px-3 border-b border-white/10 shrink-0">
        {[
          { id: 'media', label: isArabic ? 'الصور والفيديو' : 'Media', icon: Image },
          { id: 'files', label: isArabic ? 'الملفات' : 'Files', icon: FileText },
          { id: 'music', label: isArabic ? 'الصوتيات' : 'Audio', icon: Music },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex-1 py-3 text-xs font-semibold flex items-center justify-center gap-1.5 border-b-2 transition-colors ${
                isActive ? 'border-[#5288c1] text-[#5288c1]' : 'border-transparent text-gray-400 hover:text-gray-200'
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        <div className="p-8 text-center text-gray-400 space-y-3">
          <div className="w-16 h-16 rounded-full bg-white/5 flex items-center justify-center mx-auto text-[#5288c1]">
            <Download className="w-8 h-8" />
          </div>
          <div className="text-sm font-medium text-gray-200">
            {isArabic ? 'ذاكرة التخزين المؤقت للوسائط جاهزة' : 'Shared media cache is synchronized'}
          </div>
          <div className="text-xs text-gray-400 max-w-sm mx-auto">
            {isArabic
              ? 'تصفح جميع ملفات الوسائط والصور والوثائق المستلمة في محادثاتك'
              : 'Browse all images, videos, audio tracks, and docs received across your chats'}
          </div>
        </div>
      </div>
    </div>
  );
};

// ============================================================================
// 5. ADS & SPONSORED MESSAGES VIEW (الإعلانات المدعومة)
// ============================================================================
export const AdsSettingsView: React.FC<SubViewProps> = ({ onBack }) => {
  const { settings, showToast, activeAccountId } = useTelegram();
  const isArabic = settings.language === 'ar';
  const BackIcon = isArabic ? ArrowRight : ArrowLeft;

  const rawAccId = activeAccountId ?? 0;
  const accountNum = typeof rawAccId === 'number' ? rawAccId : (parseInt(String(rawAccId).replace(/\D/g, '') || '0', 10) % 4);
  const messagesCtrl = AccountInstance.getInstance(accountNum).getMessagesController();

  const [enabled, setEnabled] = useState(messagesCtrl.isSponsoredMessagesEnabled());

  const handleToggle = (val: boolean) => {
    setEnabled(val);
    messagesCtrl.toggleSponsoredMessages(val);
    showToast(isArabic ? 'تم تحديث تفضيلات الرسائل المدعومة' : 'Sponsored messages preference updated');
  };

  return (
    <div className="flex flex-col h-full bg-[#0e1621] text-white">
      <div className="flex items-center gap-3 px-4 py-3 bg-[#17212b] border-b border-white/10 shrink-0">
        <button onClick={onBack} className="p-1 hover:bg-white/10 rounded-full transition-colors">
          <BackIcon className="w-5 h-5 text-gray-300" />
        </button>
        <div className="text-base font-semibold">{isArabic ? 'الإعلانات المدعومة' : 'Sponsored Messages'}</div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <div className="p-4 bg-[#17212b] rounded-2xl border border-white/5 flex items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-purple-500 to-indigo-600 flex items-center justify-center shrink-0 shadow-lg shadow-indigo-500/20">
            <Megaphone className="w-6 h-6 text-white" />
          </div>
          <div>
            <div className="font-semibold text-sm">{isArabic ? 'الرسائل المدعومة الرسمية' : 'Official Sponsored Messages'}</div>
            <div className="text-xs text-gray-400 mt-0.5">
              {isArabic ? 'إعلانات موجزة تظهر في القنوات العامة الكبيرة' : 'Concise promotions displayed in large public channels'}
            </div>
          </div>
        </div>

        <div className="bg-[#17212b] rounded-2xl border border-white/5 divide-y divide-white/5">
          <div className="flex items-center justify-between p-4">
            <div>
              <div className="text-sm font-medium">{isArabic ? 'إظهار الرسائل المدعومة' : 'Show Sponsored Messages'}</div>
              <div className="text-xs text-gray-400 mt-0.5">
                {isArabic ? 'دعم صانعي المحتوى والمطورين عبر تيليجرام' : 'Support community creators and Telegram platform'}
              </div>
            </div>
            <input
              type="checkbox"
              checked={enabled}
              onChange={(e) => handleToggle(e.target.checked)}
              className="w-5 h-5 accent-[#5288c1] rounded cursor-pointer"
            />
          </div>
        </div>
      </div>
    </div>
  );
};

// ============================================================================
// 6. BACKUP & RESTORE VIEW (حفظ واستعادة الإعدادات)
// ============================================================================
export const BackupRestoreView: React.FC<SubViewProps> = ({ onBack }) => {
  const { settings, showToast, activeAccountId } = useTelegram();
  const isArabic = settings.language === 'ar';
  const BackIcon = isArabic ? ArrowRight : ArrowLeft;

  const rawAccId = activeAccountId ?? 0;
  const accountNum = typeof rawAccId === 'number' ? rawAccId : (parseInt(String(rawAccId).replace(/\D/g, '') || '0', 10) % 4);
  const messagesCtrl = AccountInstance.getInstance(accountNum).getMessagesController();

  const [saving, setSaving] = useState(false);
  const [restoring, setRestoring] = useState(false);
  const [lastBackupDate, setLastBackupDate] = useState<string | null>(null);

  useEffect(() => {
    try {
      const raw = localStorage.getItem(`tg_cloud_settings_backup_${accountNum}`);
      if (raw) {
        const parsed = JSON.parse(raw);
        if (parsed.timestamp) {
          setLastBackupDate(new Date(parsed.timestamp).toLocaleString(isArabic ? 'ar' : 'en'));
        }
      }
    } catch {}
  }, [accountNum, isArabic]);

  const handleSave = async () => {
    setSaving(true);
    await messagesCtrl.saveSettingsToCloud();
    setSaving(false);
    setLastBackupDate(new Date().toLocaleString(isArabic ? 'ar' : 'en'));
    showToast(isArabic ? 'تم حفظ نسخة احتياطية سحابية بنجاح' : 'Cloud backup saved successfully');
  };

  const handleRestore = async () => {
    setRestoring(true);
    const res = await messagesCtrl.restoreSettingsFromCloud();
    setRestoring(false);
    if (res) {
      showToast(isArabic ? 'تمت استعادة الإعدادات بنجاح' : 'Settings restored successfully');
    } else {
      showToast(isArabic ? 'لا توجد نسخة سحابية محفوظة' : 'No cloud backup found');
    }
  };

  return (
    <div className="flex flex-col h-full bg-[#0e1621] text-white">
      <div className="flex items-center gap-3 px-4 py-3 bg-[#17212b] border-b border-white/10 shrink-0">
        <button onClick={onBack} className="p-1 hover:bg-white/10 rounded-full transition-colors">
          <BackIcon className="w-5 h-5 text-gray-300" />
        </button>
        <div className="text-base font-semibold">{isArabic ? 'حفظ واستعادة الإعدادات' : 'Backup & Restore'}</div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <div className="p-4 bg-[#17212b] rounded-2xl border border-white/5 flex items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-emerald-500 to-teal-600 flex items-center justify-center shrink-0 shadow-lg shadow-teal-500/20">
            <Cloud className="w-6 h-6 text-white" />
          </div>
          <div>
            <div className="font-semibold text-sm">{isArabic ? 'المزامنة السحابية' : 'Cloud Synchronization'}</div>
            <div className="text-xs text-gray-400 mt-0.5">
              {isArabic ? 'حفظ إعدادات الحساب وتفضيلات الواجهة سحابياً' : 'Backup and restore all account settings to cloud storage'}
            </div>
          </div>
        </div>

        {lastBackupDate && (
          <div className="px-4 py-2 bg-white/5 rounded-xl text-xs text-gray-300 flex items-center justify-between">
            <span>{isArabic ? 'آخر نسخة احتياطية:' : 'Last backup:'}</span>
            <span className="font-mono text-emerald-400">{lastBackupDate}</span>
          </div>
        )}

        <div className="space-y-3 pt-2">
          <button
            onClick={handleSave}
            disabled={saving}
            className="w-full p-3.5 bg-[#5288c1] hover:bg-[#4375a8] text-white rounded-xl text-xs font-semibold flex items-center justify-center gap-2 transition-colors shadow"
          >
            <UploadCloud className="w-4 h-4" />
            <span>{saving ? (isArabic ? 'جارٍ الحفظ...' : 'Saving...') : (isArabic ? 'حفظ في السحابة الآن' : 'Backup to Cloud Now')}</span>
          </button>

          <button
            onClick={handleRestore}
            disabled={restoring}
            className="w-full p-3.5 bg-white/10 hover:bg-white/15 text-white rounded-xl text-xs font-semibold flex items-center justify-center gap-2 transition-colors border border-white/10"
          >
            <DownloadCloud className="w-4 h-4" />
            <span>{restoring ? (isArabic ? 'جارٍ الاستعادة...' : 'Restoring...') : (isArabic ? 'استعادة من السحابة' : 'Restore from Cloud')}</span>
          </button>
        </div>
      </div>
    </div>
  );
};

// ============================================================================
// 7. TELEGRAM PREMIUM & SUBSCRIBER VIEW (تيليجرام بريميوم)
// ============================================================================
export const PremiumSettingsView: React.FC<SubViewProps> = ({ onBack }) => {
  const { settings, showToast } = useTelegram();
  const isArabic = settings.language === 'ar';
  const BackIcon = isArabic ? ArrowRight : ArrowLeft;

  const features = [
    {
      icon: <Zap className="w-5 h-5 text-amber-400" />,
      title: isArabic ? 'سرعة تنزيل مضاعفة' : 'Double Download Speed',
      desc: isArabic ? 'تنزيل الوسائط والملفات بأقصى سرعة ممكنة' : 'No speed limits when downloading media and files',
    },
    {
      icon: <Sparkles className="w-5 h-5 text-purple-400" />,
      title: isArabic ? 'رفع ملفات بحجم 4 جيجابايت' : '4 GB Upload Size',
      desc: isArabic ? 'أرسل وثائق وفيديوهات ضخمة بحرية كاملة' : 'Share large documents and 4K videos seamlessly',
    },
    {
      icon: <Star className="w-5 h-5 text-sky-400" />,
      title: isArabic ? 'شارة بريميوم ورموز تعبيرية متحركة' : 'Premium Badge & Animated Reactions',
      desc: isArabic ? 'رمز نجمة بجانب اسمك وتفاعلات لا محدودة' : 'Special badge next to your name and exclusive reactions',
    },
    {
      icon: <Shield className="w-5 h-5 text-emerald-400" />,
      title: isArabic ? 'بدون إعلانات تماماً' : 'No Sponsored Ads',
      desc: isArabic ? 'لا تظهر أي إعلانات في القنوات العامة' : 'Clean experience without promotional channel messages',
    },
  ];

  return (
    <div className="flex flex-col h-full bg-[#0e1621] text-white">
      <div className="flex items-center gap-3 px-4 py-3 bg-[#17212b] border-b border-white/10 shrink-0">
        <button onClick={onBack} className="p-1 hover:bg-white/10 rounded-full transition-colors">
          <BackIcon className="w-5 h-5 text-gray-300" />
        </button>
        <div className="text-base font-semibold">{isArabic ? 'تيليجرام بريميوم' : 'Telegram Premium'}</div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Star Badge Card */}
        <div className="p-6 bg-gradient-to-b from-purple-900/40 via-[#17212b] to-[#17212b] rounded-2xl border border-purple-500/20 text-center space-y-3">
          <div className="w-16 h-16 rounded-full bg-gradient-to-tr from-purple-500 to-indigo-500 flex items-center justify-center mx-auto shadow-lg shadow-purple-500/30">
            <Star className="w-8 h-8 text-white fill-white" />
          </div>
          <div className="text-lg font-bold text-white">
            {isArabic ? 'تيليجرام بريميوم' : 'Telegram Premium'}
          </div>
          <p className="text-xs text-gray-300 max-w-sm mx-auto leading-relaxed">
            {isArabic
              ? 'اشترك في تيليجرام بريميوم للحصول على ميزات إضافية، وسرعة تنزيل فائقة، وسعة ملفات 4 جيجابايت، ودعم مستمر لمنصة تيليجرام.'
              : 'Subscribe to support Telegram and unlock exclusive features, 4 GB uploads, maximum download speeds, and premium badges.'}
          </p>
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-purple-500/20 text-purple-300 text-xs font-semibold">
            <Sparkles className="w-3.5 h-3.5" />
            <span>{isArabic ? 'الحساب مفعل بصلاحيات بريميوم' : 'Premium Active'}</span>
          </div>
        </div>

        {/* Features List */}
        <div className="bg-[#17212b] rounded-2xl border border-white/5 divide-y divide-white/5 overflow-hidden">
          {features.map((f, i) => (
            <div key={i} className="p-4 flex items-start gap-3.5">
              <div className="p-2 rounded-xl bg-white/5 shrink-0 mt-0.5">
                {f.icon}
              </div>
              <div>
                <div className="text-sm font-semibold text-white">{f.title}</div>
                <div className="text-xs text-gray-400 mt-0.5">{f.desc}</div>
              </div>
            </div>
          ))}
        </div>

        {/* Gift or Manage Button */}
        <button
          onClick={() => showToast(isArabic ? 'تم تفعيل ميزات بريميوم لحسابك' : 'Premium features refreshed', '⭐')}
          className="w-full py-3.5 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-semibold text-xs rounded-xl shadow-lg shadow-purple-600/20 transition-all flex items-center justify-center gap-2"
        >
          <Star className="w-4 h-4 fill-white" />
          <span>{isArabic ? 'إدارة اشتراك بريميوم' : 'Manage Subscription'}</span>
        </button>
      </div>
    </div>
  );
};

// ============================================================================
// 8. PLUS GENERAL SETTINGS VIEW (إعدادات بلاس - عام)
// ============================================================================
export const PlusGeneralSettingsView: React.FC<SubViewProps> = ({ onBack }) => {
  const { settings, showToast } = useTelegram();
  const isArabic = settings.language === 'ar';
  const BackIcon = isArabic ? ArrowRight : ArrowLeft;

  const [directShare, setDirectShare] = useState(true);
  const [systemFonts, setSystemFonts] = useState(false);
  const [proximitySensor, setProximitySensor] = useState(true);
  const [allowScreenshots, setAllowScreenshots] = useState(true);
  const [showCamera, setShowCamera] = useState(true);
  const [hidePhone, setHidePhone] = useState(false);

  return (
    <div className="flex flex-col h-full bg-[#0e1621] text-white">
      <div className="flex items-center gap-3 px-4 py-3 bg-[#17212b] border-b border-white/10 shrink-0">
        <button onClick={onBack} className="p-1 hover:bg-white/10 rounded-full transition-colors">
          <BackIcon className="w-5 h-5 text-gray-300" />
        </button>
        <div className="text-base font-semibold">{isArabic ? 'بلاس - عام' : 'Plus - General'}</div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <div className="p-4 bg-[#17212b] rounded-2xl border border-white/5 flex items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center shrink-0 shadow-lg shadow-cyan-500/20">
            <Settings className="w-6 h-6 text-white" />
          </div>
          <div>
            <div className="font-semibold text-sm">{isArabic ? 'إعدادات بلاس العامة' : 'Plus General Options'}</div>
            <div className="text-xs text-gray-400 mt-0.5">
              {isArabic ? 'خيارات النظام، الأجهزة، والمشاركة السريعة' : 'System font, hardware sensors, and quick sharing'}
            </div>
          </div>
        </div>

        <div className="bg-[#17212b] rounded-2xl border border-white/5 divide-y divide-white/5">
          <div className="flex items-center justify-between p-4">
            <div>
              <div className="text-sm font-medium">{isArabic ? 'زر المشاركة المباشرة' : 'Direct Share Button'}</div>
              <div className="text-xs text-gray-400 mt-0.5">
                {isArabic ? 'إظهار زر إعادة التوجيه السريع بجانب الرسائل' : 'Show quick forward icon next to message bubbles'}
              </div>
            </div>
            <input
              type="checkbox"
              checked={directShare}
              onChange={(e) => {
                setDirectShare(e.target.checked);
                showToast(isArabic ? 'تم تحديث خيار المشاركة المباشرة' : 'Direct share updated');
              }}
              className="w-5 h-5 accent-[#2481cc] rounded cursor-pointer"
            />
          </div>

          <div className="flex items-center justify-between p-4">
            <div>
              <div className="text-sm font-medium">{isArabic ? 'استخدام خطوط النظام' : 'Use System Font'}</div>
              <div className="text-xs text-gray-400 mt-0.5">
                {isArabic ? 'اعتماد الخط الافتراضي للنظام في كافة الواجهات' : 'Apply system default font across the app'}
              </div>
            </div>
            <input
              type="checkbox"
              checked={systemFonts}
              onChange={(e) => {
                setSystemFonts(e.target.checked);
                showToast(isArabic ? 'تم تحديث خيار الخط' : 'System font updated');
              }}
              className="w-5 h-5 accent-[#2481cc] rounded cursor-pointer"
            />
          </div>

          <div className="flex items-center justify-between p-4">
            <div>
              <div className="text-sm font-medium">{isArabic ? 'مستشعر التقريب للصوت' : 'Proximity Sensor'}</div>
              <div className="text-xs text-gray-400 mt-0.5">
                {isArabic ? 'تشغيل الصوتيات عبر سماعة الأذن تلقائياً عند التقريب' : 'Switch audio to earpiece when raised to ear'}
              </div>
            </div>
            <input
              type="checkbox"
              checked={proximitySensor}
              onChange={(e) => {
                setProximitySensor(e.target.checked);
                showToast(isArabic ? 'تم تحديث مستشعر التقريب' : 'Proximity sensor updated');
              }}
              className="w-5 h-5 accent-[#2481cc] rounded cursor-pointer"
            />
          </div>

          <div className="flex items-center justify-between p-4">
            <div>
              <div className="text-sm font-medium">{isArabic ? 'السماح بلقطات الشاشة' : 'Allow Screenshots in Secret Chats'}</div>
              <div className="text-xs text-gray-400 mt-0.5">
                {isArabic ? 'السماح بالتقاط الشاشة داخل المحادثات السرية' : 'Permit screen capture in encrypted chats'}
              </div>
            </div>
            <input
              type="checkbox"
              checked={allowScreenshots}
              onChange={(e) => {
                setAllowScreenshots(e.target.checked);
                showToast(isArabic ? 'تم تحديث إذن لقطات الشاشة' : 'Screenshot permission updated');
              }}
              className="w-5 h-5 accent-[#2481cc] rounded cursor-pointer"
            />
          </div>

          <div className="flex items-center justify-between p-4">
            <div>
              <div className="text-sm font-medium">{isArabic ? 'إظهار خيار الكاميرا في شريط الكتابة' : 'Show Camera in Input Bar'}</div>
              <div className="text-xs text-gray-400 mt-0.5">
                {isArabic ? 'وصول سريع لالتقاط الصور من شريط إدخال الرسالة' : 'Quick camera button inside the message composer'}
              </div>
            </div>
            <input
              type="checkbox"
              checked={showCamera}
              onChange={(e) => {
                setShowCamera(e.target.checked);
                showToast(isArabic ? 'تم تحديث خيار الكاميرا' : 'Camera button setting updated');
              }}
              className="w-5 h-5 accent-[#2481cc] rounded cursor-pointer"
            />
          </div>

          <div className="flex items-center justify-between p-4">
            <div>
              <div className="text-sm font-medium">{isArabic ? 'إخفاء رقم الهاتف' : 'Hide Phone Number in UI'}</div>
              <div className="text-xs text-gray-400 mt-0.5">
                {isArabic ? 'إخفاء رقم الهاتف من القوائم الجانبية لتعزيز الخصوصية' : 'Conceal mobile number from navigation headers'}
              </div>
            </div>
            <input
              type="checkbox"
              checked={hidePhone}
              onChange={(e) => {
                setHidePhone(e.target.checked);
                showToast(isArabic ? 'تم تحديث خيار إخفاء الرقم' : 'Phone display updated');
              }}
              className="w-5 h-5 accent-[#2481cc] rounded cursor-pointer"
            />
          </div>
        </div>
      </div>
    </div>
  );
};

// ============================================================================
// 9. PLUS CHATS SETTINGS VIEW (إعدادات بلاس - المحادثات)
// ============================================================================
export const PlusChatsSettingsView: React.FC<SubViewProps> = ({ onBack }) => {
  const { settings, showToast } = useTelegram();
  const isArabic = settings.language === 'ar';
  const BackIcon = isArabic ? ArrowRight : ArrowLeft;

  const [tabsPosition, setTabsPosition] = useState<'top' | 'bottom'>('top');
  const [showAvatars, setShowAvatars] = useState(true);
  const [unlimitedPin, setUnlimitedPin] = useState(true);
  const [unreadCountBadge, setUnreadCountBadge] = useState(true);
  const [confirmCall, setConfirmCall] = useState(true);
  const [stealthTyping, setStealthTyping] = useState(false);

  return (
    <div className="flex flex-col h-full bg-[#0e1621] text-white">
      <div className="flex items-center gap-3 px-4 py-3 bg-[#17212b] border-b border-white/10 shrink-0">
        <button onClick={onBack} className="p-1 hover:bg-white/10 rounded-full transition-colors">
          <BackIcon className="w-5 h-5 text-gray-300" />
        </button>
        <div className="text-base font-semibold">{isArabic ? 'بلاس - المحادثات' : 'Plus - Chats'}</div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <div className="p-4 bg-[#17212b] rounded-2xl border border-white/5 flex items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-teal-500 to-emerald-600 flex items-center justify-center shrink-0 shadow-lg shadow-teal-500/20">
            <Users className="w-6 h-6 text-white" />
          </div>
          <div>
            <div className="font-semibold text-sm">{isArabic ? 'تخصيص شاشة المحادثات' : 'Chat List Customization'}</div>
            <div className="text-xs text-gray-400 mt-0.5">
              {isArabic ? 'التبويبات، التثبيت غير المحدود، وشارات القراءة' : 'Tabs bar, unlimited pinned chats and badges'}
            </div>
          </div>
        </div>

        <div className="bg-[#17212b] rounded-2xl border border-white/5 divide-y divide-white/5">
          {/* Tabs Position */}
          <div className="p-4 flex items-center justify-between">
            <div>
              <div className="text-sm font-medium">{isArabic ? 'موضع شريط التبويبات' : 'Tabs Bar Position'}</div>
              <div className="text-xs text-gray-400 mt-0.5">
                {isArabic ? 'شريط تصنيفات المحادثات في الأعلى أو الأسفل' : 'Display chat category tabs at top or bottom'}
              </div>
            </div>
            <div className="flex rounded-lg bg-black/30 p-1 border border-white/10 text-xs">
              <button
                onClick={() => {
                  setTabsPosition('top');
                  showToast(isArabic ? 'التبويبات في الأعلى' : 'Tabs on top');
                }}
                className={`px-3 py-1 rounded-md transition-colors ${tabsPosition === 'top' ? 'bg-[#2481cc] text-white' : 'text-gray-400'}`}
              >
                {isArabic ? 'أعلى' : 'Top'}
              </button>
              <button
                onClick={() => {
                  setTabsPosition('bottom');
                  showToast(isArabic ? 'التبويبات في الأسفل' : 'Tabs at bottom');
                }}
                className={`px-3 py-1 rounded-md transition-colors ${tabsPosition === 'bottom' ? 'bg-[#2481cc] text-white' : 'text-gray-400'}`}
              >
                {isArabic ? 'أسفل' : 'Bottom'}
              </button>
            </div>
          </div>

          <div className="flex items-center justify-between p-4">
            <div>
              <div className="text-sm font-medium">{isArabic ? 'إظهار الصور الرمزية في القائمة' : 'Show Avatars in Chat List'}</div>
              <div className="text-xs text-gray-400 mt-0.5">
                {isArabic ? 'عرض صور جهات الاتصال بجانب الرسائل في القائمة' : 'Display user and channel avatars in dialogs'}
              </div>
            </div>
            <input
              type="checkbox"
              checked={showAvatars}
              onChange={(e) => {
                setShowAvatars(e.target.checked);
                showToast(isArabic ? 'تم تحديث إظهار الصور' : 'Avatars display updated');
              }}
              className="w-5 h-5 accent-[#2481cc] rounded cursor-pointer"
            />
          </div>

          <div className="flex items-center justify-between p-4">
            <div>
              <div className="text-sm font-medium">{isArabic ? 'تثبيت غير محدود للمحادثات' : 'Unlimited Pinned Chats'}</div>
              <div className="text-xs text-gray-400 mt-0.5">
                {isArabic ? 'تثبيت أكثر من 5 محادثات في أعلى القائمة بحرية' : 'Pin more than 5 chats at the top of dialogs'}
              </div>
            </div>
            <input
              type="checkbox"
              checked={unlimitedPin}
              onChange={(e) => {
                setUnlimitedPin(e.target.checked);
                showToast(isArabic ? 'تم تفعيل التثبيت غير المحدود' : 'Unlimited pins enabled');
              }}
              className="w-5 h-5 accent-[#2481cc] rounded cursor-pointer"
            />
          </div>

          <div className="flex items-center justify-between p-4">
            <div>
              <div className="text-sm font-medium">{isArabic ? 'عداد الرسائل على التبويبات' : 'Unread Counter on Tabs'}</div>
              <div className="text-xs text-gray-400 mt-0.5">
                {isArabic ? 'إظهار شارة رقمية بالرسائل غير المقروءة لكل مجلد' : 'Show badge count for each chat category tab'}
              </div>
            </div>
            <input
              type="checkbox"
              checked={unreadCountBadge}
              onChange={(e) => {
                setUnreadCountBadge(e.target.checked);
                showToast(isArabic ? 'تم تحديث عداد التبويبات' : 'Tab counter updated');
              }}
              className="w-5 h-5 accent-[#2481cc] rounded cursor-pointer"
            />
          </div>

          <div className="flex items-center justify-between p-4">
            <div>
              <div className="text-sm font-medium">{isArabic ? 'تأكيد قبل الاتصال' : 'Confirm Before Calling'}</div>
              <div className="text-xs text-gray-400 mt-0.5">
                {isArabic ? 'عرض نافذة تأكيد لتفادي الاتصال الخاطئ' : 'Prompt confirmation dialog before placing voice calls'}
              </div>
            </div>
            <input
              type="checkbox"
              checked={confirmCall}
              onChange={(e) => {
                setConfirmCall(e.target.checked);
                showToast(isArabic ? 'تم تحديث تأكيد الاتصال' : 'Call confirmation updated');
              }}
              className="w-5 h-5 accent-[#2481cc] rounded cursor-pointer"
            />
          </div>

          <div className="flex items-center justify-between p-4">
            <div>
              <div className="text-sm font-medium">{isArabic ? 'إخفاء جاري الكتابة (Stealth Typing)' : 'Hide Typing Status'}</div>
              <div className="text-xs text-gray-400 mt-0.5">
                {isArabic ? 'عدم إرسال إشعار الكتابة للطرف الآخر' : 'Do not broadcast typing status to recipient'}
              </div>
            </div>
            <input
              type="checkbox"
              checked={stealthTyping}
              onChange={(e) => {
                setStealthTyping(e.target.checked);
                showToast(isArabic ? 'تم تحديث حالة الكتابة التخفي' : 'Stealth typing updated');
              }}
              className="w-5 h-5 accent-[#2481cc] rounded cursor-pointer"
            />
          </div>
        </div>
      </div>
    </div>
  );
};

// ============================================================================
// 10. PLUS DRAWER SETTINGS VIEW (إعدادات بلاس - درج التصفح)
// ============================================================================
export const PlusDrawerSettingsView: React.FC<SubViewProps> = ({ onBack }) => {
  const { settings, showToast } = useTelegram();
  const isArabic = settings.language === 'ar';
  const BackIcon = isArabic ? ArrowRight : ArrowLeft;

  const [showAccounts, setShowAccounts] = useState(true);
  const [showUserId, setShowUserId] = useState(true);
  const [showPhone, setShowPhone] = useState(true);
  const [quickNight, setQuickNight] = useState(true);
  const [showSaved, setShowSaved] = useState(true);

  return (
    <div className="flex flex-col h-full bg-[#0e1621] text-white">
      <div className="flex items-center gap-3 px-4 py-3 bg-[#17212b] border-b border-white/10 shrink-0">
        <button onClick={onBack} className="p-1 hover:bg-white/10 rounded-full transition-colors">
          <BackIcon className="w-5 h-5 text-gray-300" />
        </button>
        <div className="text-base font-semibold">{isArabic ? 'بلاس - درج التصفح' : 'Plus - Navigation Drawer'}</div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <div className="p-4 bg-[#17212b] rounded-2xl border border-white/5 flex items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-indigo-500 to-purple-600 flex items-center justify-center shrink-0 shadow-lg shadow-indigo-500/20">
            <Menu className="w-6 h-6 text-white" />
          </div>
          <div>
            <div className="font-semibold text-sm">{isArabic ? 'تخصيص القائمة الجانبية' : 'Navigation Drawer Layout'}</div>
            <div className="text-xs text-gray-400 mt-0.5">
              {isArabic ? 'معلومات الرأس، المعرف الرقمي، والحسابات المتعددة' : 'Drawer header information, user ID and shortcuts'}
            </div>
          </div>
        </div>

        <div className="bg-[#17212b] rounded-2xl border border-white/5 divide-y divide-white/5">
          <div className="flex items-center justify-between p-4">
            <div>
              <div className="text-sm font-medium">{isArabic ? 'أيقونة تبديل الحسابات' : 'Account Switcher Arrow'}</div>
              <div className="text-xs text-gray-400 mt-0.5">
                {isArabic ? 'إظهار سهم استعراض الحسابات المتعددة في الرأس' : 'Display dropdown arrow to switch accounts in header'}
              </div>
            </div>
            <input
              type="checkbox"
              checked={showAccounts}
              onChange={(e) => {
                setShowAccounts(e.target.checked);
                showToast(isArabic ? 'تم تحديث خيار تبديل الحسابات' : 'Account switcher option updated');
              }}
              className="w-5 h-5 accent-[#2481cc] rounded cursor-pointer"
            />
          </div>

          <div className="flex items-center justify-between p-4">
            <div>
              <div className="text-sm font-medium">{isArabic ? 'إظهار المعرف الرقمي (User ID)' : 'Show User ID in Header'}</div>
              <div className="text-xs text-gray-400 mt-0.5">
                {isArabic ? 'عرض رقم الآيدي الخاص بك تحت الاسم' : 'Display numeric account ID in the drawer profile header'}
              </div>
            </div>
            <input
              type="checkbox"
              checked={showUserId}
              onChange={(e) => {
                setShowUserId(e.target.checked);
                showToast(isArabic ? 'تم تحديث إظهار الآيدي' : 'User ID display updated');
              }}
              className="w-5 h-5 accent-[#2481cc] rounded cursor-pointer"
            />
          </div>

          <div className="flex items-center justify-between p-4">
            <div>
              <div className="text-sm font-medium">{isArabic ? 'إظهار رقم الهاتف' : 'Show Phone Number'}</div>
              <div className="text-xs text-gray-400 mt-0.5">
                {isArabic ? 'عرض رقم الهاتف في الرأس' : 'Display phone number in the drawer header'}
              </div>
            </div>
            <input
              type="checkbox"
              checked={showPhone}
              onChange={(e) => {
                setShowPhone(e.target.checked);
                showToast(isArabic ? 'تم تحديث إظهار الهاتف' : 'Phone display updated');
              }}
              className="w-5 h-5 accent-[#2481cc] rounded cursor-pointer"
            />
          </div>

          <div className="flex items-center justify-between p-4">
            <div>
              <div className="text-sm font-medium">{isArabic ? 'زر التبديل السريع للوضع الليلي' : 'Quick Night Mode Toggle'}</div>
              <div className="text-xs text-gray-400 mt-0.5">
                {isArabic ? 'إظهار أيقونة القمر/الشمس في الرأس' : 'Moon icon in header for instant dark mode toggle'}
              </div>
            </div>
            <input
              type="checkbox"
              checked={quickNight}
              onChange={(e) => {
                setQuickNight(e.target.checked);
                showToast(isArabic ? 'تم تحديث خيار الوضع الليلي' : 'Night mode toggle updated');
              }}
              className="w-5 h-5 accent-[#2481cc] rounded cursor-pointer"
            />
          </div>

          <div className="flex items-center justify-between p-4">
            <div>
              <div className="text-sm font-medium">{isArabic ? 'الرسائل المحفوظة' : 'Saved Messages Item'}</div>
              <div className="text-xs text-gray-400 mt-0.5">
                {isArabic ? 'إظهار خيار الرسائل المحفوظة في القائمة' : 'Show cloud Saved Messages shortcut in menu'}
              </div>
            </div>
            <input
              type="checkbox"
              checked={showSaved}
              onChange={(e) => {
                setShowSaved(e.target.checked);
                showToast(isArabic ? 'تم تحديث خيار الرسائل المحفوظة' : 'Saved messages menu updated');
              }}
              className="w-5 h-5 accent-[#2481cc] rounded cursor-pointer"
            />
          </div>
        </div>
      </div>
    </div>
  );
};

// ============================================================================
// 11. PLUS PROFILE SETTINGS VIEW (إعدادات بلاس - الملف الشخصي)
// ============================================================================
export const PlusProfileSettingsView: React.FC<SubViewProps> = ({ onBack }) => {
  const { settings, currentUser, showToast } = useTelegram();
  const isArabic = settings.language === 'ar';
  const BackIcon = isArabic ? ArrowRight : ArrowLeft;

  const [showId, setShowId] = useState(true);
  const [copyBioOnTap, setCopyBioOnTap] = useState(true);
  const [showUsername, setShowUsername] = useState(true);
  const [directButtons, setDirectButtons] = useState(true);

  return (
    <div className="flex flex-col h-full bg-[#0e1621] text-white">
      <div className="flex items-center gap-3 px-4 py-3 bg-[#17212b] border-b border-white/10 shrink-0">
        <button onClick={onBack} className="p-1 hover:bg-white/10 rounded-full transition-colors">
          <BackIcon className="w-5 h-5 text-gray-300" />
        </button>
        <div className="text-base font-semibold">{isArabic ? 'بلاس - الملف الشخصي' : 'Plus - Profile'}</div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <div className="p-4 bg-[#17212b] rounded-2xl border border-white/5 flex items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-rose-500 to-pink-600 flex items-center justify-center shrink-0 shadow-lg shadow-rose-500/20">
            <User className="w-6 h-6 text-white" />
          </div>
          <div>
            <div className="font-semibold text-sm">{isArabic ? 'خيارات الملف الشخصي' : 'Profile Screen Customization'}</div>
            <div className="text-xs text-gray-400 mt-0.5">
              {isArabic ? 'إظهار الآيدي، نسخ النبذة، وأزرار التواصل السريع' : 'Display numeric ID, copy bio and quick action buttons'}
            </div>
          </div>
        </div>

        {/* Profile Card Preview */}
        <div className="p-4 bg-[#17212b] rounded-2xl border border-white/5 space-y-2 text-xs">
          <div className="text-[11px] font-bold text-[#5288c1] uppercase">{isArabic ? 'معاينة هوية الحساب' : 'Identity Card Preview'}</div>
          <div className="flex items-center justify-between py-1 border-b border-white/5">
            <span className="text-gray-400">{isArabic ? 'المعرف الرقمي ID:' : 'User ID:'}</span>
            <span className="font-mono text-emerald-400">{currentUser?.id || '718293041'}</span>
          </div>
          <div className="flex items-center justify-between py-1 border-b border-white/5">
            <span className="text-gray-400">{isArabic ? 'اسم المستخدم:' : 'Username:'}</span>
            <span className="text-[#2481cc]">@{currentUser?.username || 'user'}</span>
          </div>
        </div>

        <div className="bg-[#17212b] rounded-2xl border border-white/5 divide-y divide-white/5">
          <div className="flex items-center justify-between p-4">
            <div>
              <div className="text-sm font-medium">{isArabic ? 'إظهار المعرف الرقمي (User ID)' : 'Show User ID in Profile'}</div>
              <div className="text-xs text-gray-400 mt-0.5">
                {isArabic ? 'إمكانية نسخ رقم الآيدي الفريد للحساب بسهولة' : 'Quickly view and copy numeric account ID'}
              </div>
            </div>
            <input
              type="checkbox"
              checked={showId}
              onChange={(e) => {
                setShowId(e.target.checked);
                showToast(isArabic ? 'تم تحديث خيار الآيدي' : 'User ID setting updated');
              }}
              className="w-5 h-5 accent-[#2481cc] rounded cursor-pointer"
            />
          </div>

          <div className="flex items-center justify-between p-4">
            <div>
              <div className="text-sm font-medium">{isArabic ? 'نسخ النبذة بنقرة واحدة' : 'Copy Bio on Tap'}</div>
              <div className="text-xs text-gray-400 mt-0.5">
                {isArabic ? 'نسخ نص النبذة التعريفية إلى الحافظة عند النقر عليه' : 'Tap bio text to copy instantly to clipboard'}
              </div>
            </div>
            <input
              type="checkbox"
              checked={copyBioOnTap}
              onChange={(e) => {
                setCopyBioOnTap(e.target.checked);
                showToast(isArabic ? 'تم تحديث خيار نسخ النبذة' : 'Copy bio setting updated');
              }}
              className="w-5 h-5 accent-[#2481cc] rounded cursor-pointer"
            />
          </div>

          <div className="flex items-center justify-between p-4">
            <div>
              <div className="text-sm font-medium">{isArabic ? 'إظهار المعرف @username في الرأس' : 'Show Username in Header'}</div>
              <div className="text-xs text-gray-400 mt-0.5">
                {isArabic ? 'عرض اسم المستخدم تحت الاسم الكامل مباشرة' : 'Display @username right under the display name'}
              </div>
            </div>
            <input
              type="checkbox"
              checked={showUsername}
              onChange={(e) => {
                setShowUsername(e.target.checked);
                showToast(isArabic ? 'تم تحديث خيار اسم المستخدم' : 'Username setting updated');
              }}
              className="w-5 h-5 accent-[#2481cc] rounded cursor-pointer"
            />
          </div>

          <div className="flex items-center justify-between p-4">
            <div>
              <div className="text-sm font-medium">{isArabic ? 'أزرار الاتصال السريع' : 'Quick Communication Buttons'}</div>
              <div className="text-xs text-gray-400 mt-0.5">
                {isArabic ? 'أزرار اتصال صوتي وفيديو ومشاركة مباشرة في الرأس' : 'Action shortcuts for call, video and chat in profile'}
              </div>
            </div>
            <input
              type="checkbox"
              checked={directButtons}
              onChange={(e) => {
                setDirectButtons(e.target.checked);
                showToast(isArabic ? 'تم تحديث أزرار الاتصال' : 'Quick buttons updated');
              }}
              className="w-5 h-5 accent-[#2481cc] rounded cursor-pointer"
            />
          </div>
        </div>
      </div>
    </div>
  );
};

// ============================================================================
// 12. PLUS DOWNLOADS SETTINGS VIEW (إعدادات بلاس - التحميلات)
// ============================================================================
export const PlusDownloadsSettingsView: React.FC<SubViewProps> = ({ onBack }) => {
  const { settings, showToast } = useTelegram();
  const isArabic = settings.language === 'ar';
  const BackIcon = isArabic ? ArrowRight : ArrowLeft;

  const [autoResume, setAutoResume] = useState(true);
  const [maxConcurrent, setMaxConcurrent] = useState(3);
  const [wifiOnlyLarge, setWifiOnlyLarge] = useState(true);
  const [notifyComplete, setNotifyComplete] = useState(true);

  return (
    <div className="flex flex-col h-full bg-[#0e1621] text-white">
      <div className="flex items-center gap-3 px-4 py-3 bg-[#17212b] border-b border-white/10 shrink-0">
        <button onClick={onBack} className="p-1 hover:bg-white/10 rounded-full transition-colors">
          <BackIcon className="w-5 h-5 text-gray-300" />
        </button>
        <div className="text-base font-semibold">{isArabic ? 'بلاس - التحميلات' : 'Plus - Downloads'}</div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <div className="p-4 bg-[#17212b] rounded-2xl border border-white/5 flex items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-amber-500 to-orange-600 flex items-center justify-center shrink-0 shadow-lg shadow-orange-500/20">
            <Download className="w-6 h-6 text-white" />
          </div>
          <div>
            <div className="font-semibold text-sm">{isArabic ? 'مدير التحميلات المتقدم' : 'Advanced Download Manager'}</div>
            <div className="text-xs text-gray-400 mt-0.5">
              {isArabic ? 'استئناف التحميل، السرعة القصوى، وحدود التنزيل المتزامن' : 'Auto resume, concurrent limits, and download alerts'}
            </div>
          </div>
        </div>

        <div className="bg-[#17212b] rounded-2xl border border-white/5 divide-y divide-white/5">
          <div className="flex items-center justify-between p-4">
            <div>
              <div className="text-sm font-medium">{isArabic ? 'استئناف التنزيلات تلقائياً' : 'Auto-Resume Downloads'}</div>
              <div className="text-xs text-gray-400 mt-0.5">
                {isArabic ? 'استئناف تحميل الملفات المتوقفة فور توفر اتصال الإنترنت' : 'Automatically continue paused transfers on reconnect'}
              </div>
            </div>
            <input
              type="checkbox"
              checked={autoResume}
              onChange={(e) => {
                setAutoResume(e.target.checked);
                showToast(isArabic ? 'تم تحديث استئناف التنزيل' : 'Auto resume setting updated');
              }}
              className="w-5 h-5 accent-[#2481cc] rounded cursor-pointer"
            />
          </div>

          <div className="p-4 flex items-center justify-between">
            <div>
              <div className="text-sm font-medium">{isArabic ? 'أقصى عدد للتحميلات المتزامنة' : 'Max Concurrent Downloads'}</div>
              <div className="text-xs text-gray-400 mt-0.5">
                {isArabic ? 'عدد الملفات التي يتم تحميلها في نفس اللحظة' : 'Number of files downloaded in parallel'}
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className="font-mono font-bold text-[#2481cc] text-sm">{maxConcurrent}</span>
              <div className="flex rounded-lg bg-black/30 p-1 border border-white/10 text-xs">
                {[1, 3, 5].map((num) => (
                  <button
                    key={num}
                    onClick={() => {
                      setMaxConcurrent(num);
                      showToast(isArabic ? `الحد الأقصى: ${num}` : `Limit set to ${num}`);
                    }}
                    className={`px-2.5 py-1 rounded-md transition-colors ${maxConcurrent === num ? 'bg-[#2481cc] text-white' : 'text-gray-400'}`}
                  >
                    {num}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div className="flex items-center justify-between p-4">
            <div>
              <div className="text-sm font-medium">{isArabic ? 'الملفات الكبيرة عبر Wi-Fi فقط' : 'Large Files on Wi-Fi Only'}</div>
              <div className="text-xs text-gray-400 mt-0.5">
                {isArabic ? 'توفير بيانات الهاتف للملفات الأكبر من 50 ميغابايت' : 'Download files over 50 MB only when connected to Wi-Fi'}
              </div>
            </div>
            <input
              type="checkbox"
              checked={wifiOnlyLarge}
              onChange={(e) => {
                setWifiOnlyLarge(e.target.checked);
                showToast(isArabic ? 'تم تحديث تفضيلات Wi-Fi' : 'Wi-Fi rule updated');
              }}
              className="w-5 h-5 accent-[#2481cc] rounded cursor-pointer"
            />
          </div>

          <div className="flex items-center justify-between p-4">
            <div>
              <div className="text-sm font-medium">{isArabic ? 'إشعار عند اكتمال التحميل' : 'Notify on Download Complete'}</div>
              <div className="text-xs text-gray-400 mt-0.5">
                {isArabic ? 'إظهار تنبيه فور انتهاء تحميل الملف' : 'Pop an in-app banner once file transfer completes'}
              </div>
            </div>
            <input
              type="checkbox"
              checked={notifyComplete}
              onChange={(e) => {
                setNotifyComplete(e.target.checked);
                showToast(isArabic ? 'تم تحديث تنبيه التحميل' : 'Download notification updated');
              }}
              className="w-5 h-5 accent-[#2481cc] rounded cursor-pointer"
            />
          </div>
        </div>
      </div>
    </div>
  );
};


