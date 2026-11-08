import React, { useState } from 'react';
import {
  ArrowLeft,
  ArrowRight,
  Search,
  MoreVertical,
  Camera,
  Settings,
  Palette,
  Paintbrush,
  Users,
  User,
  MessageSquare,
  ShieldCheck,
  Bell,
  PieChart,
  Folder,
  Laptop,
  BatteryCharging,
  Globe,
  Star,
  Store,
  Gift,
  HelpCircle,
  Lightbulb,
  Phone,
  AtSign,
  Cake,
  Megaphone,
  Sparkles,
  UserPlus,
  LogOut,
  Check,
  X,
  PlusCircle,
  PlayCircle,
  ListOrdered,
  Menu,
  Lock,
  LayoutGrid,
  Download,
  Sliders,
  Clock,
  Mail,
  Ban,
  MonitorSmartphone,
  BarChart2,
  HardDrive,
  QrCode,
  Smartphone,
  Trash2,
  Volume2,
  Vibrate,
  Eye,
  SlidersHorizontal,
  CheckCheck,
  Hash,
  Image,
  Cloud,
  Layers,
  ChevronRight,
} from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { useTelegram } from '../../context/TelegramContext';
import { SettingsSubPage } from '../../types';
import { TwoStepVerificationView } from './TwoStepVerificationView';
import { twoStepController } from '../../core/messenger/TwoStepVerificationController';
import {
  PrivacyControlView,
  PasscodeLockView,
  AutoDeleteView,
  SessionsView,
  BlockedUsersView,
} from './PrivacySubViews';
import {
  privacyController,
  PrivacyTarget,
} from '../../core/messenger/PrivacySettingsController';
import {
  StoriesSettingsView,
  MessagesSettingsView,
  TopicsSettingsView,
  SharedMediaView,
  AdsSettingsView,
  BackupRestoreView,
  PremiumSettingsView,
  PlusGeneralSettingsView,
  PlusChatsSettingsView,
  PlusDrawerSettingsView,
  PlusProfileSettingsView,
  PlusDownloadsSettingsView,
} from './ExtendedSettingsViews';

export const SettingsModal: React.FC = () => {
  const {
    activeModal,
    setActiveModal,
    settings,
    updateSettings,
    currentUser,
    accounts,
    activeAccountId,
    switchAccount,
    settingsSubPage,
    setSettingsSubPage,
    showToast,
    triggerNotification,
    folders,
  } = useTelegram();

  const [searchFilter, setSearchFilter] = useState('');
  const [isSearchActive, setIsSearchActive] = useState(false);
  const [selectedPrivacyTarget, setSelectedPrivacyTarget] = useState<PrivacyTarget>('phone_number');
  const [navHistory, setNavHistory] = useState<SettingsSubPage[]>([]);

  const isArabic = settings.language === 'ar';
  const BackIcon = isArabic ? ArrowRight : ArrowLeft;

  const navigateTo = (page: SettingsSubPage) => {
    setNavHistory((prev) => [...prev, settingsSubPage]);
    setSettingsSubPage(page);
  };

  const goBack = () => {
    if (navHistory.length > 0) {
      const prev = navHistory[navHistory.length - 1];
      setNavHistory((h) => h.slice(0, -1));
      setSettingsSubPage(prev);
    } else if (settingsSubPage === 'main') {
      setActiveModal('none');
    } else {
      setSettingsSubPage('main');
    }
  };

  return (
    <AnimatePresence>
      {activeModal === 'settings' && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center select-none font-sans p-0 sm:p-4"
          dir={isArabic ? 'rtl' : 'ltr'}
        >
          {/* Backdrop */}
          <motion.div
            id="settings-modal-backdrop"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            onClick={() => setActiveModal('none')}
            className="absolute inset-0 bg-black/65 backdrop-blur-xs cursor-pointer"
          />

          {/* Main Container */}
          <motion.div
            id="tg-settings-container"
            initial={{ opacity: 0, scale: 0.95, y: 15 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 15 }}
            transition={{ type: 'spring', damping: 28, stiffness: 320 }}
            className="relative w-full sm:max-w-xl h-full sm:h-[92vh] sm:rounded-2xl shadow-2xl overflow-hidden flex flex-col z-10 border border-white/10"
            style={{
              backgroundColor: 'var(--tg-theme-surface, #17212b)',
              color: 'var(--tg-theme-bubble-in-text, #ffffff)',
            }}
          >
            {/* Render View by SubPage with smooth transitions */}
            <AnimatePresence mode="wait">
              <motion.div
                key={settingsSubPage}
                initial={{ opacity: 0, x: isArabic ? -12 : 12 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: isArabic ? 12 : -12 }}
                transition={{ duration: 0.18, ease: 'easeOut' }}
                className="flex-1 flex flex-col h-full overflow-hidden"
              >
                {settingsSubPage === 'main' && (
                  <MainSettingsView
                    onNavigate={navigateTo}
                    onClose={() => setActiveModal('none')}
                    isSearchActive={isSearchActive}
                    setIsSearchActive={setIsSearchActive}
                    searchFilter={searchFilter}
                    setSearchFilter={setSearchFilter}
                  />
                )}

                {settingsSubPage === 'account' && <AccountEditView onBack={goBack} />}
                {settingsSubPage === 'plus_settings' && <PlusSettingsView onBack={goBack} onNavigate={navigateTo} />}
                {settingsSubPage === 'plus_general' && <PlusGeneralSettingsView onBack={goBack} />}
                {settingsSubPage === 'plus_chats' && <PlusChatsSettingsView onBack={goBack} />}
                {settingsSubPage === 'plus_drawer' && <PlusDrawerSettingsView onBack={goBack} />}
                {settingsSubPage === 'plus_profile' && <PlusProfileSettingsView onBack={goBack} />}
                {settingsSubPage === 'plus_downloads' && <PlusDownloadsSettingsView onBack={goBack} />}
                {settingsSubPage === 'theme_coloring' && <ThemeColoringView onBack={goBack} />}
                {settingsSubPage === 'chat_settings' && <ChatSettingsView onBack={goBack} />}
                {settingsSubPage === 'privacy_security' && (
                  <PrivacySecurityView
                    onBack={goBack}
                    onSelectPrivacyTarget={(target) => {
                      setSelectedPrivacyTarget(target);
                      navigateTo('privacy_control');
                    }}
                  />
                )}
                {settingsSubPage === 'privacy_control' && (
                  <PrivacyControlView
                    target={selectedPrivacyTarget}
                    onBack={goBack}
                  />
                )}
                {settingsSubPage === 'two_step_verification' && (
                  <TwoStepVerificationView onBack={goBack} />
                )}
                {settingsSubPage === 'passcode_lock' && (
                  <PasscodeLockView onBack={goBack} />
                )}
                {settingsSubPage === 'auto_delete' && (
                  <AutoDeleteView onBack={goBack} />
                )}
                {settingsSubPage === 'sessions' && (
                  <SessionsView onBack={goBack} />
                )}
                {settingsSubPage === 'blocked_users' && (
                  <BlockedUsersView onBack={goBack} />
                )}
                {settingsSubPage === 'notifications_sounds' && <NotificationsSoundsView onBack={goBack} />}
                {settingsSubPage === 'data_storage' && <DataStorageView onBack={goBack} />}
                {settingsSubPage === 'power_saving' && <PowerSavingView onBack={goBack} />}
                {settingsSubPage === 'language' && <LanguageView onBack={goBack} />}
                {settingsSubPage === 'devices' && <DevicesView onBack={goBack} />}
                {settingsSubPage === 'folders' && <FoldersView onBack={goBack} />}
                {settingsSubPage === 'themes_browser' && <ThemesBrowserView onBack={goBack} />}
                {settingsSubPage === 'support_group' && <SupportGroupView onBack={goBack} />}
                {settingsSubPage === 'faq' && <FaqView onBack={goBack} />}
                {settingsSubPage === 'features' && <FeaturesView onBack={goBack} />}
                {settingsSubPage === 'stories' && <StoriesSettingsView onBack={goBack} />}
                {settingsSubPage === 'messages' && <MessagesSettingsView onBack={goBack} />}
                {settingsSubPage === 'topics' && <TopicsSettingsView onBack={goBack} />}
                {settingsSubPage === 'shared_media' && <SharedMediaView onBack={goBack} />}
                {settingsSubPage === 'ads_settings' && <AdsSettingsView onBack={goBack} />}
                {settingsSubPage === 'backup_restore' && <BackupRestoreView onBack={goBack} />}
                {settingsSubPage === 'premium' && <PremiumSettingsView onBack={goBack} />}
              </motion.div>
            </AnimatePresence>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
};

// ==========================================
// 1. MAIN SETTINGS VIEW (Matches Screenshots)
// ==========================================
const MainSettingsView: React.FC<{
  onNavigate: (page: SettingsSubPage) => void;
  onClose: () => void;
  isSearchActive: boolean;
  setIsSearchActive: (v: boolean) => void;
  searchFilter: string;
  setSearchFilter: (v: string) => void;
}> = ({ onNavigate, onClose, isSearchActive, setIsSearchActive, searchFilter, setSearchFilter }) => {
  const { currentUser, accounts, activeAccountId, switchAccount, settings, showToast, setActiveModal } = useTelegram();
  const isArabic = settings.language === 'ar';
  const BackIcon = isArabic ? ArrowRight : ArrowLeft;

  const otherAccounts = accounts.filter((a) => a.id !== activeAccountId);

  return (
    <div className="flex flex-col h-full overflow-hidden">
      {/* Top App Bar */}
      <div className="flex items-center justify-between px-4 py-3.5 bg-[#2481cc] text-white shrink-0 shadow-md">
        <div className="flex items-center gap-3">
          <button
            onClick={onClose}
            className="p-1.5 rounded-full hover:bg-white/15 transition-colors"
            title={isArabic ? 'رجوع' : 'Back'}
          >
            <BackIcon className="w-5 h-5" />
          </button>
          <span className="font-bold text-lg">{isArabic ? 'الإعدادات' : 'Settings'}</span>
        </div>

        <div className="flex items-center gap-1">
          <button
            onClick={() => setIsSearchActive(!isSearchActive)}
            className="p-2 rounded-full hover:bg-white/15 transition-colors"
            title={isArabic ? 'بحث' : 'Search'}
          >
            <Search className="w-5 h-5" />
          </button>
          <button
            onClick={() => showToast(isArabic ? 'خيارات إضافية' : 'More options', '⚙️')}
            className="p-2 rounded-full hover:bg-white/15 transition-colors"
          >
            <MoreVertical className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Search Input Bar (Conditional) */}
      {isSearchActive && (
        <div className="p-3 bg-[#1e2a38] border-b border-white/10 flex items-center gap-2">
          <Search className="w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder={isArabic ? 'ابحث في الإعدادات...' : 'Search settings...'}
            value={searchFilter}
            onChange={(e) => setSearchFilter(e.target.value)}
            className="bg-transparent border-none outline-none text-sm text-white flex-1"
            autoFocus
          />
          {searchFilter && (
            <button onClick={() => setSearchFilter('')} className="text-gray-400 hover:text-white">
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      )}

      {/* Scrollable Content */}
      <div className="flex-1 overflow-y-auto divide-y divide-black/30 scrollbar-thin bg-[#0e1621]">
        {/* User Profile Card */}
        <div
          onClick={() => onNavigate('account')}
          className="p-4 bg-[#17212b] flex items-center justify-between cursor-pointer hover:bg-white/5 transition-colors"
        >
          <div className="flex items-center gap-4 min-w-0">
            <div className="relative w-16 h-16 rounded-full overflow-hidden shrink-0 border border-white/20 shadow-md">
              {currentUser.avatar ? (
                <img
                  src={currentUser.avatar}
                  alt={currentUser.name}
                  className="w-full h-full object-cover"
                  referrerPolicy="no-referrer"
                />
              ) : (
                <div className="w-full h-full bg-[#5288c1] flex items-center justify-center text-white font-bold text-xl">
                  {currentUser.name ? currentUser.name.charAt(0).toUpperCase() : 'U'}
                </div>
              )}
              <div className="absolute inset-0 bg-black/20 flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity">
                <Camera className="w-5 h-5 text-white" />
              </div>
            </div>
            <div className="min-w-0">
              <div className="font-bold text-base truncate flex items-center gap-1.5">
                <span className="truncate">{currentUser.name}</span>
                {currentUser.isVerified && (
                  <Check className="w-4 h-4 text-[#5288c1] stroke-[3]" />
                )}
              </div>
              <div className="text-xs text-gray-400 font-mono mt-0.5">{currentUser.phone}</div>
              <div className="text-xs text-[#5288c1] font-mono">@{currentUser.username || 'Seha09'}</div>
            </div>
          </div>
        </div>

        {/* Accounts Card List */}
        {otherAccounts.length > 0 && (
          <div className="p-3 bg-[#17212b] space-y-1">
            <div className="px-2 py-1 text-[11px] font-bold text-[#5288c1] uppercase tracking-wider">
              {isArabic ? 'الحسابات' : 'Accounts'}
            </div>
            {otherAccounts.map((acc) => (
              <div
                key={acc.id}
                onClick={() => switchAccount(acc.id)}
                className="flex items-center justify-between p-2.5 rounded-xl hover:bg-white/5 cursor-pointer transition-colors"
              >
                <div className="flex items-center gap-3 min-w-0">
                  <div className="w-9 h-9 rounded-full overflow-hidden shrink-0 border border-white/20">
                    {acc.user.avatar ? (
                      <img src={acc.user.avatar} alt={acc.user.name} className="w-full h-full object-cover" />
                    ) : (
                      <div className="w-full h-full bg-[#5288c1] flex items-center justify-center text-white font-bold text-xs">
                        {acc.user.name.charAt(0).toUpperCase()}
                      </div>
                    )}
                  </div>
                  <div className="min-w-0">
                    <div className="font-semibold text-xs truncate">{acc.user.name}</div>
                    <div className="text-[11px] text-gray-400 font-mono truncate">{acc.user.phone}</div>
                  </div>
                </div>

                {acc.unreadCount && acc.unreadCount > 0 ? (
                  <span className="px-2.5 py-0.5 text-xs font-bold bg-[#5288c1] text-white rounded-full">
                    {acc.unreadCount}
                  </span>
                ) : null}
              </div>
            ))}
          </div>
        )}

        {/* Plus Section (Screenshot 2) */}
        <div className="py-2 bg-[#17212b]">
          <SettingsListItem
            icon={<Settings className="w-5 h-5 text-cyan-400" />}
            iconBg="bg-cyan-500/15"
            title={isArabic ? 'إعدادات بلاس' : 'Plus Settings'}
            onClick={() => onNavigate('plus_settings')}
          />
          <SettingsListItem
            icon={<Palette className="w-5 h-5 text-orange-400" />}
            iconBg="bg-orange-500/15"
            title={isArabic ? 'تلوين النمط' : 'Theme Coloring'}
            onClick={() => onNavigate('theme_coloring')}
          />
          <SettingsListItem
            icon={<Paintbrush className="w-5 h-5 text-rose-400" />}
            iconBg="bg-rose-500/15"
            title={isArabic ? 'تنزيل أنماط' : 'Download Themes'}
            onClick={() => onNavigate('themes_browser')}
          />
          <SettingsListItem
            icon={<Users className="w-5 h-5 text-sky-400" />}
            iconBg="bg-sky-500/15"
            title={isArabic ? 'مجموعة الدعم' : 'Support Group'}
            onClick={() => onNavigate('support_group')}
          />
        </div>

        {/* Telegram Main Settings (Colored Circles) */}
        <div className="py-2 bg-[#17212b]">
          <div className="px-4 py-1.5 text-[11px] font-bold text-[#5288c1] uppercase tracking-wider">
            {isArabic ? 'إعدادات تيليجرام' : 'Telegram Settings'}
          </div>

          <SettingsListItem
            icon={<User className="w-5 h-5 text-blue-400" />}
            iconBg="bg-blue-500/20"
            title={isArabic ? 'الملف الشخصي والحساب' : 'Profile & Account'}
            subtitle={isArabic ? 'الرقم، اسم المستخدم، النبذة' : 'Phone, Username, Bio'}
            onClick={() => onNavigate('account')}
          />
          <SettingsListItem
            icon={<Camera className="w-5 h-5 text-rose-400" />}
            iconBg="bg-rose-500/20"
            title={isArabic ? 'القصص' : 'Stories'}
            subtitle={isArabic ? 'الدقة، وضع التخفي، الخصوصية' : 'Resolution, Stealth mode, Privacy'}
            onClick={() => onNavigate('stories')}
          />
          <SettingsListItem
            icon={<MessageSquare className="w-5 h-5 text-amber-400" />}
            iconBg="bg-amber-500/20"
            title={isArabic ? 'إعدادات المحادثات' : 'Chat Settings'}
            subtitle={isArabic ? 'خلفية الشاشة، الوضع الليلي، المؤثرات الحركية' : 'Wallpaper, Night Mode, Animations'}
            onClick={() => onNavigate('chat_settings')}
          />
          <SettingsListItem
            icon={<Sliders className="w-5 h-5 text-indigo-400" />}
            iconBg="bg-indigo-500/20"
            title={isArabic ? 'الرسائل' : 'Messages'}
            subtitle={isArabic ? 'فقاعات الرسائل، حجم الخط، زوايا العرض' : 'Message bubbles, Font size, Corner radius'}
            onClick={() => onNavigate('messages')}
          />
          <SettingsListItem
            icon={<Hash className="w-5 h-5 text-cyan-400" />}
            iconBg="bg-cyan-500/20"
            title={isArabic ? 'المواضيع والمنتديات' : 'Forum Topics'}
            subtitle={isArabic ? 'تنظيم المنتديات، الأقسام، والمواضيع' : 'Topics layout, Tabs and threads'}
            onClick={() => onNavigate('topics')}
          />
          <SettingsListItem
            icon={<ShieldCheck className="w-5 h-5 text-emerald-400" />}
            iconBg="bg-emerald-500/20"
            title={isArabic ? 'الخصوصية والأمان' : 'Privacy and Security'}
            subtitle={isArabic ? 'التحقق بخطوتين، آخر ظهور، الجلسات، مفاتيح المرور' : '2FA, Last Seen, Devices, Passkeys'}
            onClick={() => onNavigate('privacy_security')}
          />
          <SettingsListItem
            icon={<Bell className="w-5 h-5 text-pink-400" />}
            iconBg="bg-pink-500/20"
            title={isArabic ? 'الإشعارات والأصوات' : 'Notifications and Sounds'}
            subtitle={isArabic ? 'الأصوات، المكالمات، الشارات' : 'Sounds, Calls, Badges'}
            onClick={() => onNavigate('notifications_sounds')}
          />
          <SettingsListItem
            icon={<Image className="w-5 h-5 text-teal-400" />}
            iconBg="bg-teal-500/20"
            title={isArabic ? 'الوسائط المشتركة' : 'Shared Media'}
            subtitle={isArabic ? 'الصور، الفيديو، الملفات، والصوتيات' : 'Photos, Videos, Files and Audio'}
            onClick={() => onNavigate('shared_media')}
          />
          <SettingsListItem
            icon={<PieChart className="w-5 h-5 text-sky-400" />}
            iconBg="bg-sky-500/20"
            title={isArabic ? 'التنزيل والتخزين' : 'Data and Storage'}
            subtitle={isArabic ? 'إعدادات التنزيل التلقائي والشبكة' : 'Network usage, Auto-download media'}
            onClick={() => onNavigate('data_storage')}
          />
          <SettingsListItem
            icon={<Megaphone className="w-5 h-5 text-purple-400" />}
            iconBg="bg-purple-500/20"
            title={isArabic ? 'الإعلانات المدعومة' : 'Sponsored Messages'}
            subtitle={isArabic ? 'الرسائل الترويجية وإعلانات القنوات' : 'Promoted posts in public channels'}
            onClick={() => onNavigate('ads_settings')}
          />
          <SettingsListItem
            icon={<Cloud className="w-5 h-5 text-emerald-400" />}
            iconBg="bg-emerald-500/20"
            title={isArabic ? 'حفظ واستعادة الإعدادات' : 'Backup & Restore'}
            subtitle={isArabic ? 'المزامنة السحابية الشاملة للإعدادات' : 'Cloud sync and settings backup'}
            onClick={() => onNavigate('backup_restore')}
          />
          <SettingsListItem
            icon={<Folder className="w-5 h-5 text-cyan-400" />}
            iconBg="bg-cyan-500/20"
            title={isArabic ? 'مجلدات المحادثات' : 'Chat Folders'}
            subtitle={isArabic ? 'فرز المحادثات في مجلدات' : 'Organize chats into folders'}
            onClick={() => onNavigate('folders')}
          />
          <SettingsListItem
            icon={<Laptop className="w-5 h-5 text-teal-400" />}
            iconBg="bg-teal-500/20"
            title={isArabic ? 'الأجهزة والجلسات' : 'Devices & Sessions'}
            subtitle={isArabic ? 'إدارة الأجهزة المتصلة والجلسات النشطة' : 'Manage linked sessions & desktop'}
            onClick={() => onNavigate('devices')}
          />
          <SettingsListItem
            icon={<BatteryCharging className="w-5 h-5 text-orange-400" />}
            iconBg="bg-orange-500/20"
            title={isArabic ? 'توفير الطاقة' : 'Power Saving'}
            subtitle={isArabic ? 'تقليل استهلاك الطاقة عند انخفاض الشحن' : 'Reduce battery consumption'}
            onClick={() => onNavigate('power_saving')}
          />
          <SettingsListItem
            icon={<Globe className="w-5 h-5 text-purple-400" />}
            iconBg="bg-purple-500/20"
            title={isArabic ? 'اللغة' : 'Language'}
            subtitle={isArabic ? 'العربية' : 'English'}
            onClick={() => onNavigate('language')}
          />
        </div>

        {/* Direct Mobile App Installation */}
        <div className="py-2 bg-[#17212b]">
          <div className="px-4 py-1.5 text-[11px] font-bold text-emerald-400 uppercase tracking-wider flex items-center justify-between">
            <span>{isArabic ? 'تثبيت التطبيق على الجوال' : 'Install App on Phone'}</span>
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-mono">v12.9.2</span>
          </div>

          <SettingsListItem
            icon={<Download className="w-5 h-5 text-emerald-400" />}
            iconBg="bg-emerald-500/20"
            title={isArabic ? 'تثبيت تطبيق تيليجرام' : 'Install Telegram App'}
            subtitle={isArabic ? 'تثبيت فوري كتطبيق حقيقي على الهاتف' : 'Instant installation as real mobile app'}
            onClick={() => {
              setActiveModal('apk-installer');
            }}
            rightBadge={
              <span className="px-2 py-0.5 text-[10px] font-bold bg-emerald-500 text-white rounded-full">
                {isArabic ? 'تثبيت' : 'Install'}
              </span>
            }
          />
        </div>

        {/* Premium & Business Services */}
        <div className="py-2 bg-[#17212b]">
          <SettingsListItem
            icon={<Star className="w-5 h-5 text-purple-400" />}
            iconBg="bg-purple-500/20"
            title="Telegram Premium"
            onClick={() => onNavigate('premium')}
          />
          <SettingsListItem
            icon={<Store className="w-5 h-5 text-pink-400" />}
            iconBg="bg-pink-500/20"
            title="Telegram Business"
            onClick={() => showToast('Telegram Business Tools', '💼')}
          />
          <SettingsListItem
            icon={<Gift className="w-5 h-5 text-amber-400" />}
            iconBg="bg-amber-500/20"
            title={isArabic ? 'Send a Gift' : 'Send a Gift'}
            onClick={() => showToast('Send a Gift to friends 🎁', '🎁')}
          />
        </div>

        {/* Help & Information */}
        <div className="py-2 bg-[#17212b]">
          <div className="px-4 py-1.5 text-[11px] font-bold text-[#5288c1] uppercase tracking-wider">
            {isArabic ? 'مساعدة' : 'Help'}
          </div>

          <SettingsListItem
            icon={<MessageSquare className="w-5 h-5 text-amber-400" />}
            iconBg="bg-amber-500/20"
            title={isArabic ? 'اسأل سؤالاً' : 'Ask a Question'}
            onClick={() => onNavigate('faq')}
          />
          <SettingsListItem
            icon={<HelpCircle className="w-5 h-5 text-blue-400" />}
            iconBg="bg-blue-500/20"
            title={isArabic ? 'الأسئلة الشائعة' : 'Telegram FAQ'}
            onClick={() => onNavigate('faq')}
          />
          <SettingsListItem
            icon={<Lightbulb className="w-5 h-5 text-purple-400" />}
            iconBg="bg-purple-500/20"
            title={isArabic ? 'ميزات تيليجرام' : 'Telegram Features'}
            onClick={() => onNavigate('features')}
          />
          <SettingsListItem
            icon={<ShieldCheck className="w-5 h-5 text-emerald-400" />}
            iconBg="bg-emerald-500/20"
            title={isArabic ? 'سياسة الخصوصية' : 'Privacy Policy'}
            onClick={() => showToast('Telegram Security & Privacy Guaranteed', '🛡️')}
          />
        </div>

        {/* Version & Developer Footer */}
        <div className="p-4 bg-[#17212b] text-center text-xs text-gray-400 space-y-2 border-t border-white/5">
          <div>
            <div className="font-semibold text-gray-300">
              {isArabic ? 'تيليجرام للأندرويد' : 'Telegram for Android'}
            </div>
            <div className="font-mono text-[11px] text-gray-500">
              v12.9.2.0 (2246) universal arm64-v8a
            </div>
          </div>

          <div className="pt-2 border-t border-white/5 space-y-1 text-center">
            <div className="text-xs font-semibold text-[#5288c1]">
              {isArabic ? 'المطور:' : 'Developer:'} <span className="text-gray-200">انور فواد محمد علي سيف</span>
            </div>
            <div className="text-[10px] text-gray-400 font-mono">
              Anwer Foud Mohammed Ali Saif
            </div>
            <div className="flex items-center justify-center gap-3 text-[11px] font-mono text-emerald-400" dir="ltr">
              <a href="tel:+967772997043" className="hover:underline flex items-center gap-1">
                <span>📞</span> +967 772 997 043
              </a>
              <span>•</span>
              <a href="tel:+966562570935" className="hover:underline flex items-center gap-1">
                <span>📞</span> +966 562 570 935
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Sub-Component Helper: Settings List Item
const SettingsListItem: React.FC<{
  icon: React.ReactNode;
  iconBg: string;
  title: string;
  subtitle?: string;
  onClick: () => void;
  rightBadge?: React.ReactNode;
}> = ({ icon, iconBg, title, subtitle, onClick, rightBadge }) => {
  return (
    <button
      onClick={onClick}
      className="w-full flex items-center justify-between px-4 py-3 hover:bg-white/5 transition-colors text-left rtl:text-right"
    >
      <div className="flex items-center gap-3.5 min-w-0">
        <div className={`w-9 h-9 rounded-full flex items-center justify-center shrink-0 ${iconBg}`}>
          {icon}
        </div>
        <div className="min-w-0">
          <div className="text-[13.5px] font-medium text-white truncate">{title}</div>
          {subtitle && <div className="text-xs text-gray-400 truncate">{subtitle}</div>}
        </div>
      </div>

      {rightBadge && <div>{rightBadge}</div>}
    </button>
  );
};

// ==========================================
// 2. ACCOUNT / PROFILE EDIT VIEW (Screenshots 5, 6)
// ==========================================
const AccountEditView: React.FC<{ onBack: () => void }> = ({ onBack }) => {
  const { currentUser, updateAccountProfile, settings, accounts, switchAccount, logout, showToast } = useTelegram();
  const isArabic = settings.language === 'ar';
  const BackIcon = isArabic ? ArrowRight : ArrowLeft;

  const [name, setName] = useState(currentUser.name);
  const [username, setUsername] = useState(currentUser.username || '');
  const [bio, setBio] = useState(currentUser.bio || '');
  const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);

  const handleSave = () => {
    updateAccountProfile({ name, username, bio });
    showToast(isArabic ? 'تم حفظ التعديلات' : 'Profile updated', '✅');
  };

  return (
    <div className="flex flex-col h-full overflow-hidden bg-[#0e1621]">
      <SubPageHeader title={isArabic ? 'الحساب' : 'Account'} onBack={onBack} />

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Avatar & Name Input */}
        <div className="p-4 bg-[#17212b] rounded-2xl border border-white/10 flex flex-col items-center text-center">
          <div className="relative w-20 h-20 rounded-full overflow-hidden border-2 border-[#5288c1] mb-3">
            {currentUser.avatar ? (
              <img src={currentUser.avatar} alt={currentUser.name} className="w-full h-full object-cover" />
            ) : (
              <div className="w-full h-full bg-[#5288c1] flex items-center justify-center text-white font-bold text-2xl">
                {currentUser.name ? currentUser.name.charAt(0).toUpperCase() : 'U'}
              </div>
            )}
            <div className="absolute inset-0 bg-black/40 flex items-center justify-center cursor-pointer hover:bg-black/60">
              <Camera className="w-6 h-6 text-white" />
            </div>
          </div>

          <div className="w-full space-y-2">
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full bg-[#242f3d] border border-white/10 rounded-xl px-3 py-2 text-sm text-center font-bold text-white outline-none focus:border-[#5288c1]"
              placeholder={isArabic ? 'الاسم' : 'Name'}
            />
            <input
              type="text"
              value={bio}
              onChange={(e) => setBio(e.target.value)}
              className="w-full bg-[#242f3d] border border-white/10 rounded-xl px-3 py-2 text-xs text-center text-gray-300 outline-none focus:border-[#5288c1]"
              placeholder={isArabic ? 'النبذة: 70 بضع كلمات عنك' : 'Bio'}
            />
            <button
              onClick={handleSave}
              className="w-full py-2 bg-[#2481cc] hover:bg-[#1f6fa8] rounded-xl text-xs font-bold text-white transition-colors"
            >
              {isArabic ? 'حفظ التغييرات' : 'Save Changes'}
            </button>
          </div>
        </div>

        {/* Info Items List (Matches Screenshot 5) */}
        <div className="bg-[#17212b] rounded-2xl border border-white/10 divide-y divide-white/5 overflow-hidden">
          <div className="p-3.5 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-emerald-500/20 flex items-center justify-center text-emerald-400">
                <Phone className="w-4 h-4" />
              </div>
              <div>
                <div className="text-xs font-mono font-bold text-white">{currentUser.phone}</div>
                <div className="text-[11px] text-gray-400">{isArabic ? 'انقر لتغيير رقم الهاتف' : 'Tap to change phone'}</div>
              </div>
            </div>
          </div>

          <div className="p-3.5 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-orange-500/20 flex items-center justify-center text-orange-400">
                <AtSign className="w-4 h-4" />
              </div>
              <div>
                <div className="text-xs font-mono font-bold text-white">@{username}</div>
                <div className="text-[11px] text-gray-400">{isArabic ? 'اسم المستخدم' : 'Username'}</div>
              </div>
            </div>
          </div>

          <div className="p-3.5 flex items-center justify-between cursor-pointer hover:bg-white/5" onClick={() => showToast('Date of birth added', '🎂')}>
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-sky-500/20 flex items-center justify-center text-sky-400">
                <Cake className="w-4 h-4" />
              </div>
              <div>
                <div className="text-xs font-bold text-white">{isArabic ? 'إضافة تاريخ الميلاد' : 'Add Date of Birth'}</div>
                <div className="text-[11px] text-gray-400">{isArabic ? 'إظهار يوم ميلادك للأصدقاء' : 'Show friends your birthday'}</div>
              </div>
            </div>
          </div>

          <div className="p-3.5 flex items-center justify-between cursor-pointer hover:bg-white/5" onClick={() => showToast('Personal Channel', '📢')}>
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-amber-500/20 flex items-center justify-center text-amber-400">
                <Megaphone className="w-4 h-4" />
              </div>
              <div>
                <div className="text-xs font-bold text-white">Add Personal channel</div>
                <div className="text-[11px] text-gray-400">{isArabic ? 'ربط قناتك الشخصية بالملف' : 'Link personal channel'}</div>
              </div>
            </div>
          </div>

          <div className="p-3.5 flex items-center justify-between cursor-pointer hover:bg-white/5" onClick={() => showToast('AI Auto Reply Bot active', '🤖')}>
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-purple-500/20 flex items-center justify-center text-purple-400">
                <Sparkles className="w-4 h-4" />
              </div>
              <div>
                <div className="text-xs font-bold text-white flex items-center gap-1.5">
                  <span>{isArabic ? 'المحادثة الآلية' : 'Auto Reply Bot'}</span>
                  <span className="text-[9px] bg-purple-500 text-white px-1.5 py-0.2 rounded-full font-bold">NEW</span>
                </div>
                <div className="text-[11px] text-gray-400">{isArabic ? 'رد تلقائي بالذكاء الاصطناعي' : 'AI automated answers'}</div>
              </div>
            </div>
          </div>
        </div>

        {/* Log Out */}
        <button
          type="button"
          onClick={() => setShowLogoutConfirm(true)}
          className="w-full p-3.5 bg-red-500/15 hover:bg-red-500/25 border border-red-500/30 rounded-2xl flex items-center justify-center gap-2 text-red-400 text-xs font-bold transition-colors"
        >
          <LogOut className="w-4 h-4" />
          <span>{isArabic ? 'تسجيل الخروج من الحساب' : 'Log Out of Account'}</span>
        </button>

        {/* Logout Confirmation Dialog */}
        {showLogoutConfirm && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-xs">
            <div className="w-full max-w-xs bg-[#17212b] border border-[#2b394a] rounded-2xl p-5 shadow-2xl text-center space-y-4">
              <div className="w-12 h-12 rounded-full bg-red-500/20 text-red-400 flex items-center justify-center mx-auto">
                <LogOut className="w-6 h-6" />
              </div>
              <div>
                <h4 className="text-sm font-bold text-white mb-1">
                  {isArabic ? 'تسجيل الخروج؟' : 'Log Out?'}
                </h4>
                <p className="text-xs text-gray-400">
                  {isArabic
                    ? `هل أنت متأكد من رغبتك في تسجيل الخروج من حساب (${currentUser.name})؟`
                    : `Are you sure you want to log out of (${currentUser.name})?`}
                </p>
              </div>

              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => setShowLogoutConfirm(false)}
                  className="flex-1 py-2 rounded-xl bg-white/10 hover:bg-white/15 text-white text-xs font-semibold transition-colors"
                >
                  {isArabic ? 'إلغاء' : 'Cancel'}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowLogoutConfirm(false);
                    logout();
                  }}
                  className="flex-1 py-2 rounded-xl bg-red-500 hover:bg-red-600 text-white text-xs font-bold transition-colors"
                >
                  {isArabic ? 'تأكيد الخروج' : 'Log Out'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// ==========================================
// 3. PLUS SETTINGS VIEW (Screenshot 3)
// ==========================================
const PlusSettingsView: React.FC<{ onBack: () => void; onNavigate: (page: SettingsSubPage) => void }> = ({
  onBack,
  onNavigate,
}) => {
  const { settings, showToast } = useTelegram();
  const isArabic = settings.language === 'ar';

  const items: Array<{
    title: string;
    sub: string;
    icon: React.ReactNode;
    page: SettingsSubPage;
  }> = [
    {
      title: isArabic ? 'عام' : 'General',
      sub: isArabic ? 'المشاركة، المستشعرات، وخطوط النظام' : 'Sharing, sensors & system fonts',
      icon: <Settings className="w-5 h-5 text-cyan-400" />,
      page: 'plus_general',
    },
    {
      title: isArabic ? 'المحادثات' : 'Chats',
      sub: isArabic ? 'شريط التبويبات، التثبيت غير المحدود، والشارات' : 'Tabs bar, unlimited pins & badges',
      icon: <Users className="w-5 h-5 text-cyan-400" />,
      page: 'plus_chats',
    },
    {
      title: isArabic ? 'القصص' : 'Stories',
      sub: isArabic ? 'الدقة الفائقة، وضع التخفي، والحفظ' : 'HD quality, stealth mode & saving',
      icon: <PlayCircle className="w-5 h-5 text-cyan-400" />,
      page: 'stories',
    },
    {
      title: isArabic ? 'الرسائل' : 'Messages',
      sub: isArabic ? 'انحناء الفقاعات، حجم الخط، وتأثيرات الصوت' : 'Corner radius, font size & effects',
      icon: <MessageSquare className="w-5 h-5 text-cyan-400" />,
      page: 'messages',
    },
    {
      title: isArabic ? 'المواضيع (Topics)' : 'Topics',
      sub: isArabic ? 'تنظيم المنتديات والمجموعات الخارقة' : 'Forum threads & supergroup organization',
      icon: <ListOrdered className="w-5 h-5 text-cyan-400" />,
      page: 'topics',
    },
    {
      title: isArabic ? 'درج التصفح' : 'Navigation Drawer',
      sub: isArabic ? 'المعرف الرقمي، تبديل الحسابات، والوضع الليلي' : 'Header info, user ID & account switcher',
      icon: <Menu className="w-5 h-5 text-cyan-400" />,
      page: 'plus_drawer',
    },
    {
      title: isArabic ? 'الملف الشخصي' : 'Profile',
      sub: isArabic ? 'المعرف الرقمي، نسخ النبذة، وأزرار الاتصال' : 'Numeric ID, copy bio & quick actions',
      icon: <User className="w-5 h-5 text-cyan-400" />,
      page: 'plus_profile',
    },
    {
      title: isArabic ? 'الإشعارات والأصوات' : 'Notifications & Sounds',
      sub: isArabic ? 'نغمات الرنين، الاهتزاز، والمعاينة' : 'Alert sounds, vibrations & previews',
      icon: <Bell className="w-5 h-5 text-cyan-400" />,
      page: 'notifications_sounds',
    },
    {
      title: isArabic ? 'الخصوصية والأمان' : 'Privacy and Security',
      sub: isArabic ? 'التحقق بخطوتين، القفل، والجلسات النشطة' : '2FA, passcode lock & active sessions',
      icon: <Lock className="w-5 h-5 text-cyan-400" />,
      page: 'privacy_security',
    },
    {
      title: isArabic ? 'الوسائط المتبادلة' : 'Shared Media',
      sub: isArabic ? 'معرض الصور، الفيديوهات، والملفات' : 'Media gallery, files & audio cache',
      icon: <LayoutGrid className="w-5 h-5 text-cyan-400" />,
      page: 'shared_media',
    },
    {
      title: isArabic ? 'التحميلات' : 'Downloads',
      sub: isArabic ? 'مدير التحميلات، استئناف التنزيل، وشبكة Wi-Fi' : 'Download manager, auto-resume & Wi-Fi',
      icon: <Download className="w-5 h-5 text-cyan-400" />,
      page: 'plus_downloads',
    },
    {
      title: isArabic ? 'الرسائل المدعومة (Ads)' : 'Sponsored Messages (Ads)',
      sub: isArabic ? 'تفضيلات الرسائل المدعومة الرسمية' : 'Official channel sponsored promotions',
      icon: <Megaphone className="w-5 h-5 text-cyan-400" />,
      page: 'ads_settings',
    },
  ];

  return (
    <div className="flex flex-col h-full overflow-hidden bg-[#0e1621]">
      <SubPageHeader title={isArabic ? 'إعدادات بلاس' : 'Plus Settings'} onBack={onBack} />

      <div className="flex-1 overflow-y-auto divide-y divide-white/5 bg-[#17212b]">
        {items.map((item, idx) => (
          <div
            key={idx}
            onClick={() => onNavigate(item.page)}
            className="flex items-center justify-between px-4 py-3.5 hover:bg-white/5 cursor-pointer transition-colors"
          >
            <div className="flex items-center gap-4">
              <div className="p-2 rounded-xl bg-cyan-500/10 shrink-0">
                {item.icon}
              </div>
              <div>
                <div className="text-[13.5px] font-medium text-white">{item.title}</div>
                <div className="text-[11px] text-gray-400">{item.sub}</div>
              </div>
            </div>
            <ChevronRight className={`w-4 h-4 text-gray-500 shrink-0 ${isArabic ? 'rotate-180' : ''}`} />
          </div>
        ))}

        {/* Save & Restore Section */}
        <div className="p-4 bg-[#0e1621] space-y-3">
          <div
            onClick={() => onNavigate('backup_restore')}
            className="p-3 bg-[#17212b] rounded-xl border border-white/10 cursor-pointer hover:bg-white/5 flex items-center justify-between transition-colors"
          >
            <div>
              <div className="text-xs font-bold text-white">{isArabic ? 'حفظ واستعادة الإعدادات سحابياً' : 'Backup & Restore Settings'}</div>
              <div className="text-[11px] text-gray-400 mt-0.5">
                {isArabic ? "مزامنة كافة تفضيلات بلاس السحابية واستعادتها" : "Cloud backup and restore for all Plus settings"}
              </div>
            </div>
            <ChevronRight className={`w-4 h-4 text-gray-500 shrink-0 ${isArabic ? 'rotate-180' : ''}`} />
          </div>
        </div>
      </div>
    </div>
  );
};

// ==========================================
// 4. THEME COLORING VIEW (Screenshot 4)
// ==========================================
const ThemeColoringView: React.FC<{ onBack: () => void }> = ({ onBack }) => {
  const { settings, updateSettings, showToast } = useTelegram();
  const isArabic = settings.language === 'ar';

  const [plusThemeEnabled, setPlusThemeEnabled] = useState(true);
  const [selectedColor, setSelectedColor] = useState('#2481cc');

  const colorPresets = ['#2481cc', '#10b981', '#8b5cf6', '#f59e0b', '#ec4899', '#06b6d4', '#64748b'];

  return (
    <div className="flex flex-col h-full overflow-hidden bg-[#0e1621]">
      <SubPageHeader title={isArabic ? 'تلوين النمط' : 'Theme Coloring'} onBack={onBack} />

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Toggle Plus Theme */}
        <div className="p-3.5 bg-[#17212b] rounded-2xl border border-white/10 flex items-center justify-between">
          <span className="font-bold text-xs text-white">{isArabic ? 'تشغيل نمط بلاس' : 'Enable Plus Theme'}</span>
          <input
            type="checkbox"
            checked={plusThemeEnabled}
            onChange={(e) => setPlusThemeEnabled(e.target.checked)}
            className="w-5 h-5 accent-[#2481cc]"
          />
        </div>

        {/* Primary Color Palette */}
        <div className="p-4 bg-[#17212b] rounded-2xl border border-white/10 space-y-3">
          <div className="text-xs font-bold text-[#5288c1]">{isArabic ? 'اللون الأساسي للنمط' : 'Primary Theme Color'}</div>
          <div className="flex items-center gap-3">
            {colorPresets.map((c) => (
              <button
                key={c}
                onClick={() => {
                  setSelectedColor(c);
                  updateSettings({ accentColor: c });
                  showToast(isArabic ? 'تم تغيير اللون' : 'Theme color applied', '🎨');
                }}
                className={`w-9 h-9 rounded-full border-2 transition-transform ${
                  selectedColor === c ? 'scale-110 border-white' : 'border-transparent'
                }`}
                style={{ backgroundColor: c }}
              />
            ))}
          </div>
        </div>

        {/* Interfaces List (Matches Screenshot 4) */}
        <div className="p-3 bg-[#17212b] rounded-2xl border border-white/10 divide-y divide-white/5">
          <div className="py-1 text-[11px] font-bold text-gray-400 uppercase">{isArabic ? 'الواجهات' : 'Interfaces'}</div>
          {[
            '1 الواجهة الرئيسية',
            '2 واجهة الدردشة',
            '3 واجهة جهات الإتصال',
            '4 درج التصفح',
            '5 الملف الشخصي',
            '6 الإعدادات/واجهة تلوين النمط',
          ].map((item, idx) => (
            <div
              key={idx}
              onClick={() => showToast(item, '🎨')}
              className="py-2.5 flex items-center justify-between text-xs text-gray-200 cursor-pointer hover:text-white"
            >
              <span>{item}</span>
              <div className="w-4 h-4 rounded-full border border-white/30" style={{ backgroundColor: selectedColor }} />
            </div>
          ))}
        </div>

        {/* Themes Save & XML Options */}
        <div className="p-3 bg-[#17212b] rounded-2xl border border-white/10 space-y-2 text-xs">
          <div className="py-1 text-[11px] font-bold text-gray-400 uppercase">{isArabic ? 'الأنماط' : 'Themes'}</div>
          <button
            onClick={() => showToast(isArabic ? 'تم حفظ ملف النمط' : 'Theme saved (.xml)', '💾')}
            className="w-full py-2 bg-white/5 hover:bg-white/10 rounded-xl text-white font-medium text-center"
          >
            {isArabic ? 'حفظ النمط (/Themes)' : 'Save Theme (/Themes)'}
          </button>
          <button
            onClick={() => showToast(isArabic ? 'تم تطبيق ملف النمط .xml' : 'Theme applied from XML', '📄')}
            className="w-full py-2 bg-white/5 hover:bg-white/10 rounded-xl text-white font-medium text-center"
          >
            {isArabic ? 'تطبيق النمط من الملف' : 'Apply Theme from file'}
          </button>
        </div>
      </div>
    </div>
  );
};

// ==========================================
// 5. CHAT SETTINGS VIEW (Screenshots 7, 8, 9)
// ==========================================
const ChatSettingsView: React.FC<{ onBack: () => void }> = ({ onBack }) => {
  const { settings, updateSettings, showToast, currentUser } = useTelegram();
  const isArabic = settings.language === 'ar';

  const [fontSize, setFontSize] = useState(settings.fontSize || 16);
  const [cornerRadius, setCornerRadius] = useState(settings.bubbleCornerRadius || 17);
  const [viewMode, setViewMode] = useState<'two_lines' | 'three_lines'>('two_lines');
  const [appIcon, setAppIcon] = useState('Default');

  const themes = [
    { id: 'classic', label: isArabic ? 'كلاسيكي' : 'Classic', color: '#2481cc' },
    { id: 'night', label: isArabic ? 'ليلي' : 'Night', color: '#17212b' },
    { id: 'arctic', label: isArabic ? 'ثلجي' : 'Arctic', color: '#e0f2fe' },
    { id: 'sunset', label: isArabic ? 'غروب' : 'Sunset', color: '#f43f5e' },
  ];

  return (
    <div className="flex flex-col h-full overflow-hidden bg-[#0e1621]">
      <SubPageHeader title={isArabic ? 'إعدادات المحادثات' : 'Chat Settings'} onBack={onBack} />

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Interactive Chat Bubble Preview (Screenshot 7) */}
        <div className="p-4 bg-[#0b141a] rounded-2xl border border-white/10 space-y-3">
          <div className="text-[11px] font-bold text-gray-400 uppercase tracking-wider text-center">
            {isArabic ? 'معاينة الرسائل المباشرة' : 'Live Message Preview'}
          </div>

          <div className="space-y-2">
            {/* Incoming Bubble */}
            <div className="flex justify-start">
              <div
                className="max-w-[80%] bg-[#182533] p-3 text-white shadow-md"
                style={{
                  borderRadius: `${cornerRadius}px`,
                  fontSize: `${fontSize}px`,
                }}
              >
                <div className="text-xs font-bold text-[#5288c1] mb-1">{currentUser.name}</div>
                <div>{isArabic ? 'صباح الخير! ما هو الوقت الآن؟' : 'Good morning! What time is it?'}</div>
                <div className="text-[10px] text-gray-400 text-right mt-1">3:01 م</div>
              </div>
            </div>

            {/* Outgoing Bubble */}
            <div className="flex justify-end">
              <div
                className="max-w-[80%] bg-[#2b5278] p-3 text-white shadow-md"
                style={{
                  borderRadius: `${cornerRadius}px`,
                  fontSize: `${fontSize}px`,
                }}
              >
                <div>{isArabic ? 'الوقت صباح هنا في دبي ☀️' : 'It is morning here in Dubai ☀️'}</div>
                <div className="flex items-center justify-end gap-1 text-[10px] text-sky-200 mt-1">
                  <span>3:16 م</span>
                  <CheckCheck className="w-3.5 h-3.5 text-sky-300" />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Font Size Slider (Screenshot 7) */}
        <div className="p-4 bg-[#17212b] rounded-2xl border border-white/10 space-y-2">
          <div className="flex items-center justify-between text-xs font-bold">
            <span className="text-white">{isArabic ? 'حجم خط الرسائل' : 'Message Font Size'}</span>
            <span className="text-[#5288c1] font-mono text-sm">{fontSize} px</span>
          </div>
          <input
            type="range"
            min="12"
            max="26"
            value={fontSize}
            onChange={(e) => {
              const val = Number(e.target.value);
              setFontSize(val);
              updateSettings({ fontSize: val });
            }}
            className="w-full accent-[#2481cc] cursor-pointer"
          />
        </div>

        {/* Corner Radius Slider (Screenshot 8) */}
        <div className="p-4 bg-[#17212b] rounded-2xl border border-white/10 space-y-2">
          <div className="flex items-center justify-between text-xs font-bold">
            <span className="text-white">{isArabic ? 'زوايا الرسالة' : 'Message Corner Radius'}</span>
            <span className="text-[#5288c1] font-mono text-sm">{cornerRadius} px</span>
          </div>
          <input
            type="range"
            min="0"
            max="28"
            value={cornerRadius}
            onChange={(e) => {
              const val = Number(e.target.value);
              setCornerRadius(val);
              updateSettings({ bubbleCornerRadius: val });
            }}
            className="w-full accent-[#2481cc] cursor-pointer"
          />
        </div>

        {/* Theme Presets */}
        <div className="p-4 bg-[#17212b] rounded-2xl border border-white/10 space-y-3">
          <div className="text-xs font-bold text-white">{isArabic ? 'لون النمط' : 'Theme Presets'}</div>
          <div className="grid grid-cols-4 gap-2">
            {themes.map((t) => (
              <button
                key={t.id}
                onClick={() => {
                  updateSettings({ theme: t.id === 'classic' ? 'dark' : (t.id as any) });
                  showToast(t.label, '🎨');
                }}
                className="p-3 rounded-xl border border-white/10 flex flex-col items-center gap-1.5 hover:bg-white/5"
              >
                <div className="w-7 h-7 rounded-full" style={{ backgroundColor: t.color }} />
                <span className="text-[11px] text-gray-300 truncate">{t.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Chat List View Mode (2 lines vs 3 lines) */}
        <div className="p-4 bg-[#17212b] rounded-2xl border border-white/10 space-y-2">
          <div className="text-xs font-bold text-white">{isArabic ? 'عرض قائمة المحادثات' : 'Chat List View'}</div>
          <div className="flex items-center gap-4 text-xs">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="radio"
                name="viewMode"
                checked={viewMode === 'two_lines'}
                onChange={() => setViewMode('two_lines')}
                className="accent-[#2481cc]"
              />
              <span>{isArabic ? 'خطين اثنين (2 lines)' : 'Two lines'}</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="radio"
                name="viewMode"
                checked={viewMode === 'three_lines'}
                onChange={() => setViewMode('three_lines')}
                className="accent-[#2481cc]"
              />
              <span>{isArabic ? 'ثلاثة خطوط (3 lines)' : 'Three lines'}</span>
            </label>
          </div>
        </div>
      </div>
    </div>
  );
};

// ==========================================
// 6. PRIVACY & SECURITY VIEW (Screenshot 10)
// ==========================================
const PrivacySecurityView: React.FC<{
  onBack: () => void;
  onSelectPrivacyTarget: (target: PrivacyTarget) => void;
}> = ({ onBack, onSelectPrivacyTarget }) => {
  const { settings, showToast, setSettingsSubPage } = useTelegram();
  const isArabic = settings.language === 'ar';
  const twoStepState = twoStepController.getState();
  const privacyState = privacyController.getState();

  const getOptionLabel = (opt: string) => {
    if (opt === 'everybody') return isArabic ? 'الجميع' : 'Everybody';
    if (opt === 'contacts') return isArabic ? 'جهات اتصالي' : 'My Contacts';
    return isArabic ? 'لا أحد' : 'Nobody';
  };

  const getAutoDeleteLabel = (sec: number) => {
    if (sec === 86400) return isArabic ? 'يوم واحد' : '1 day';
    if (sec === 604800) return isArabic ? 'أسبوع واحد' : '1 week';
    if (sec === 2592000) return isArabic ? 'شهر واحد' : '1 month';
    return isArabic ? 'معطلة' : 'Off';
  };

  return (
    <div className="flex flex-col h-full overflow-hidden bg-[#0e1621]">
      <SubPageHeader title={isArabic ? 'الخصوصية والأمان' : 'Privacy and Security'} onBack={onBack} />

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Security Group */}
        <div className="bg-[#17212b] rounded-2xl border border-white/10 divide-y divide-white/5 overflow-hidden">
          <div className="p-3 text-[11px] font-bold text-[#5288c1] uppercase">{isArabic ? 'الأمان' : 'Security'}</div>

          <SecurityRow
            icon={<ShieldCheck className="w-5 h-5 text-emerald-400" />}
            title={isArabic ? 'التحقق بخطوتين' : 'Two-Step Verification'}
            value={twoStepState.hasPassword ? (isArabic ? 'مفعّل' : 'On') : (isArabic ? 'معطّل' : 'Off')}
            onClick={() => setSettingsSubPage('two_step_verification')}
          />
          <SecurityRow
            icon={<Clock className="w-5 h-5 text-cyan-400" />}
            title={isArabic ? 'الحذف التلقائي للرسائل' : 'Auto-Delete Messages'}
            value={getAutoDeleteLabel(privacyState.autoDeletePeriod)}
            onClick={() => setSettingsSubPage('auto_delete')}
          />
          <SecurityRow
            icon={<Lock className="w-5 h-5 text-cyan-400" />}
            title={isArabic ? 'رمز القفل' : 'Passcode Lock'}
            value={privacyState.passcodeEnabled ? (isArabic ? 'مفعّل' : 'On') : (isArabic ? 'معطلة' : 'Off')}
            onClick={() => setSettingsSubPage('passcode_lock')}
          />
          <SecurityRow
            icon={<Mail className="w-5 h-5 text-teal-400" />}
            title={isArabic ? 'بريد تسجيل الدخول' : 'Login Email'}
            value={privacyState.loginEmail}
            onClick={() => showToast(`${isArabic ? 'بريد تسجيل الدخول:' : 'Login email:'} ${privacyState.loginEmail}`, '📧')}
          />
          <SecurityRow
            icon={<Ban className="w-5 h-5 text-rose-400" />}
            title={isArabic ? 'المستخدمون المحظورون' : 'Blocked Users'}
            value={String(privacyState.blockedUsersCount)}
            onClick={() => setSettingsSubPage('blocked_users')}
          />
          <SecurityRow
            icon={<MonitorSmartphone className="w-5 h-5 text-sky-400" />}
            title={isArabic ? 'الجلسات النشطة' : 'Active Sessions'}
            value={String(privacyState.activeSessionsCount)}
            onClick={() => setSettingsSubPage('sessions')}
          />
        </div>

        {/* Privacy Group */}
        <div className="bg-[#17212b] rounded-2xl border border-white/10 divide-y divide-white/5 overflow-hidden">
          <div className="p-3 text-[11px] font-bold text-[#5288c1] uppercase">{isArabic ? 'الخصوصية' : 'Privacy'}</div>
          <SecurityRow
            title={isArabic ? 'رقم الهاتف' : 'Phone Number'}
            value={getOptionLabel(privacyState.phoneNumber)}
            onClick={() => onSelectPrivacyTarget('phone_number')}
          />
          <SecurityRow
            title={isArabic ? 'آخر ظهور ومتصل' : 'Last Seen & Online'}
            value={getOptionLabel(privacyState.lastSeen)}
            onClick={() => onSelectPrivacyTarget('last_seen')}
          />
          <SecurityRow
            title={isArabic ? 'الصور الشخصية' : 'Profile Photos'}
            value={getOptionLabel(privacyState.profilePhotos)}
            onClick={() => onSelectPrivacyTarget('profile_photos')}
          />
          <SecurityRow
            title={isArabic ? 'الرسائل المحوّلة' : 'Forwarded Messages'}
            value={getOptionLabel(privacyState.forwards)}
            onClick={() => onSelectPrivacyTarget('forwards')}
          />
          <SecurityRow
            title={isArabic ? 'المكالمات' : 'Calls'}
            value={getOptionLabel(privacyState.calls)}
            onClick={() => onSelectPrivacyTarget('calls')}
          />
        </div>
      </div>
    </div>
  );
};

const SecurityRow: React.FC<{
  icon?: React.ReactNode;
  title: string;
  value: string;
  onClick: () => void;
}> = ({ icon, title, value, onClick }) => (
  <div
    onClick={onClick}
    className="px-4 py-3 flex items-center justify-between hover:bg-white/5 cursor-pointer transition-colors"
  >
    <div className="flex items-center gap-3">
      {icon}
      <span className="text-xs font-semibold text-white">{title}</span>
    </div>
    <span className="text-xs text-[#5288c1] font-mono">{value}</span>
  </div>
);

// ==========================================
// 7. NOTIFICATIONS & SOUNDS VIEW (Screenshot 11)
// ==========================================
const NotificationsSoundsView: React.FC<{ onBack: () => void }> = ({ onBack }) => {
  const { settings, showToast, triggerNotification } = useTelegram();
  const isArabic = settings.language === 'ar';

  const [privateChats, setPrivateChats] = useState(true);
  const [groups, setGroups] = useState(true);
  const [channels, setChannels] = useState(true);
  const [inAppSounds, setInAppSounds] = useState(true);
  const [inAppVibrate, setInAppVibrate] = useState(true);

  return (
    <div className="flex flex-col h-full overflow-hidden bg-[#0e1621]">
      <SubPageHeader title={isArabic ? 'الإشعارات والأصوات' : 'Notifications and Sounds'} onBack={onBack} />

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Chat Notifications */}
        <div className="bg-[#17212b] rounded-2xl border border-white/10 divide-y divide-white/5 overflow-hidden">
          <div className="p-3 text-[11px] font-bold text-[#5288c1] uppercase">{isArabic ? 'إشعارات المحادثات' : 'Chat Notifications'}</div>
          <ToggleRow title={isArabic ? 'المحادثات الخاصة' : 'Private Chats'} checked={privateChats} onChange={setPrivateChats} />
          <ToggleRow title={isArabic ? 'المجموعات' : 'Groups'} checked={groups} onChange={setGroups} />
          <ToggleRow title={isArabic ? 'القنوات' : 'Channels'} checked={channels} onChange={setChannels} />
        </div>

        {/* In-App Notifications */}
        <div className="bg-[#17212b] rounded-2xl border border-white/10 divide-y divide-white/5 overflow-hidden">
          <div className="p-3 text-[11px] font-bold text-[#5288c1] uppercase">{isArabic ? 'إشعارات داخل التطبيق' : 'In-App Notifications'}</div>
          <ToggleRow title={isArabic ? 'أصوات داخل التطبيق' : 'In-App Sounds'} checked={inAppSounds} onChange={setInAppSounds} />
          <ToggleRow title={isArabic ? 'اهتزازات داخل التطبيق' : 'In-App Vibrate'} checked={inAppVibrate} onChange={setInAppVibrate} />
        </div>

        {/* Test Notification Trigger */}
        <button
          onClick={() => {
            triggerNotification({
              category: 'message',
              title: isArabic ? 'منار. العنزي' : 'Manar Al-Anzi',
              body: isArabic ? 'تم تحديث كافة الأيقونات والترتيب بنجاح 🚀' : 'All icons and order updated flawlessly 🚀',
              senderName: 'System',
              avatar: '',
            });
            showToast(isArabic ? 'تم إرسال إشعار تجريبي' : 'Test notification fired', '🔔');
          }}
          className="w-full py-3 bg-[#2481cc]/80 hover:bg-[#2481cc] rounded-xl text-xs font-bold text-white transition-colors"
        >
          {isArabic ? 'تجربة إشعار داخلي (In-App Preview)' : 'Test In-App Notification'}
        </button>
      </div>
    </div>
  );
};

const ToggleRow: React.FC<{
  title: string;
  checked: boolean;
  onChange: (v: boolean) => void;
}> = ({ title, checked, onChange }) => (
  <div className="px-4 py-3 flex items-center justify-between">
    <span className="text-xs font-semibold text-white">{title}</span>
    <input
      type="checkbox"
      checked={checked}
      onChange={(e) => onChange(e.target.checked)}
      className="w-5 h-5 accent-[#2481cc] cursor-pointer"
    />
  </div>
);

// ==========================================
// 8. DATA & STORAGE VIEW (Screenshot 12)
// ==========================================
const DataStorageView: React.FC<{ onBack: () => void }> = ({ onBack }) => {
  const { settings, showToast } = useTelegram();
  const isArabic = settings.language === 'ar';

  return (
    <div className="flex flex-col h-full overflow-hidden bg-[#0e1621]">
      <SubPageHeader title={isArabic ? 'البيانات والتخزين' : 'Data and Storage'} onBack={onBack} />

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Usage Stats (Screenshot 12) */}
        <div className="bg-[#17212b] rounded-2xl border border-white/10 divide-y divide-white/5 overflow-hidden">
          <div className="p-3 text-[11px] font-bold text-[#5288c1] uppercase">{isArabic ? 'استخدام التخزين والشبكة' : 'Disk and Network Usage'}</div>

          <div
            onClick={() => showToast('Storage usage calculated: 586.4 MB', '💾')}
            className="p-3.5 flex items-center justify-between cursor-pointer hover:bg-white/5"
          >
            <div className="flex items-center gap-3">
              <PieChart className="w-5 h-5 text-sky-400" />
              <span className="text-xs font-bold text-white">{isArabic ? 'استخدام التخزين' : 'Storage Usage'}</span>
            </div>
            <span className="text-xs font-mono text-[#5288c1]">586.4 MB</span>
          </div>

          <div
            onClick={() => showToast('Data usage: 880.9 MB', '📊')}
            className="p-3.5 flex items-center justify-between cursor-pointer hover:bg-white/5"
          >
            <div className="flex items-center gap-3">
              <BarChart2 className="w-5 h-5 text-emerald-400" />
              <span className="text-xs font-bold text-white">{isArabic ? 'استهلاك البيانات' : 'Data Usage'}</span>
            </div>
            <span className="text-xs font-mono text-emerald-400">880.9 MB</span>
          </div>
        </div>

        {/* Auto Media Download */}
        <div className="bg-[#17212b] rounded-2xl border border-white/10 divide-y divide-white/5 overflow-hidden">
          <div className="p-3 text-[11px] font-bold text-[#5288c1] uppercase">{isArabic ? 'تنزيل الوسائط تلقائيًا' : 'Automatic Media Download'}</div>
          <div className="p-3.5 text-xs text-gray-200">{isArabic ? 'عند استخدام بيانات الجوال: الصور، المقاطع (10 MB)' : 'When using mobile data: Photos, Videos (10 MB)'}</div>
          <div className="p-3.5 text-xs text-gray-200">{isArabic ? 'عند الاتصال بالواي فاي: الصور، المقاطع (15 MB)' : 'When connected to Wi-Fi: Photos, Videos (15 MB)'}</div>
        </div>
      </div>
    </div>
  );
};

// ==========================================
// 9. POWER SAVING VIEW (Screenshot 13)
// ==========================================
const PowerSavingView: React.FC<{ onBack: () => void }> = ({ onBack }) => {
  const { settings, showToast } = useTelegram();
  const isArabic = settings.language === 'ar';
  const [sliderVal, setSliderVal] = useState(10);
  const [animStickers, setAnimStickers] = useState(true);
  const [animEmoji, setAnimEmoji] = useState(true);
  const [chatEffects, setChatEffects] = useState(true);
  const [autoGifs, setAutoGifs] = useState(true);

  return (
    <div className="flex flex-col h-full overflow-hidden bg-[#0e1621]">
      <SubPageHeader title={isArabic ? 'توفير الطاقة' : 'Power Saving'} onBack={onBack} />

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Slider */}
        <div className="p-4 bg-[#17212b] rounded-2xl border border-white/10 space-y-3">
          <div className="flex items-center justify-between text-xs font-bold">
            <span className="text-white">{isArabic ? 'وضع توفير الطاقة' : 'Power Saving Mode'}</span>
            <span className="text-amber-400 font-mono">{sliderVal}%</span>
          </div>
          <input
            type="range"
            min="0"
            max="100"
            value={sliderVal}
            onChange={(e) => {
              const v = Number(e.target.value);
              setSliderVal(v);
            }}
            className="w-full accent-amber-400 cursor-pointer"
          />
          <div className="text-[11px] text-gray-400">
            {isArabic ? 'يتم تقليل الحركات وتأثيرات الملصقات عند انخفاض البطارية' : 'Reduces animations and lottie stickers when battery is low'}
          </div>
        </div>

        {/* Switches */}
        <div className="bg-[#17212b] rounded-2xl border border-white/10 divide-y divide-white/5 overflow-hidden">
          <div className="p-3 text-[11px] font-bold text-[#5288c1] uppercase">{isArabic ? 'خيارات توفير الطاقة' : 'Power Saving Options'}</div>
          <ToggleRow
            title={isArabic ? 'الملصقات المتحركة (Animated Stickers)' : 'Animated Stickers'}
            checked={animStickers}
            onChange={(v) => {
              setAnimStickers(v);
              showToast(isArabic ? 'تم تحديث خيار الملصقات المتحركة' : 'Animated stickers setting updated');
            }}
          />
          <ToggleRow
            title={isArabic ? 'الرموز التعبيرية المتحركة (Animated Emoji)' : 'Animated Emoji'}
            checked={animEmoji}
            onChange={(v) => {
              setAnimEmoji(v);
              showToast(isArabic ? 'تم تحديث خيار الرموز المتحركة' : 'Animated emoji setting updated');
            }}
          />
          <ToggleRow
            title={isArabic ? 'التأثيرات في المحادثات (Chat Effects)' : 'Chat Effects'}
            checked={chatEffects}
            onChange={(v) => {
              setChatEffects(v);
              showToast(isArabic ? 'تم تحديث تأثيرات المحادثة' : 'Chat effects setting updated');
            }}
          />
          <ToggleRow
            title={isArabic ? 'تشغيل تلقائي للصور المتحركة (Autoplay GIFs)' : 'Autoplay GIFs'}
            checked={autoGifs}
            onChange={(v) => {
              setAutoGifs(v);
              showToast(isArabic ? 'تم تحديث التشغيل التلقائي للصور المتحركة' : 'Autoplay GIFs setting updated');
            }}
          />
        </div>
      </div>
    </div>
  );
};

// ==========================================
// 10. LANGUAGE VIEW (Screenshot 14)
// ==========================================
const LanguageView: React.FC<{ onBack: () => void }> = ({ onBack }) => {
  const { settings, updateSettings, showToast } = useTelegram();
  const isArabic = settings.language === 'ar';

  const languages = [
    { code: 'ar', name: 'العربية', native: 'Arabic' },
    { code: 'en', name: 'English', native: 'English' },
    { code: 'ru', name: 'Русский', native: 'Russian' },
    { code: 'es', name: 'Español', native: 'Spanish' },
    { code: 'fr', name: 'Français', native: 'French' },
    { code: 'de', name: 'Deutsch', native: 'German' },
    { code: 'tr', name: 'Türkçe', native: 'Turkish' },
    { code: 'fa', name: 'فارسی', native: 'Persian' },
  ];

  return (
    <div className="flex flex-col h-full overflow-hidden bg-[#0e1621]">
      <SubPageHeader title={isArabic ? 'اللغة' : 'Language'} onBack={onBack} />

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Translation Settings */}
        <div className="p-4 bg-[#17212b] rounded-2xl border border-white/10 flex items-center justify-between">
          <div>
            <div className="text-xs font-bold text-white">{isArabic ? 'ترجمة الرسائل' : 'Translate Messages'}</div>
            <div className="text-[11px] text-gray-400">{isArabic ? 'إظهار زر الترجمة في المحادثات' : 'Show Translate button'}</div>
          </div>
          <input type="checkbox" defaultChecked className="w-5 h-5 accent-[#2481cc]" />
        </div>

        {/* Languages List */}
        <div className="bg-[#17212b] rounded-2xl border border-white/10 divide-y divide-white/5 overflow-hidden">
          {languages.map((lang) => (
            <div
              key={lang.code}
              onClick={() => {
                updateSettings({ language: lang.code as any });
                showToast(`Language set to ${lang.name}`, '🌐');
              }}
              className="p-3.5 flex items-center justify-between cursor-pointer hover:bg-white/5"
            >
              <div>
                <div className="text-xs font-bold text-white">{lang.name}</div>
                <div className="text-[11px] text-gray-400">{lang.native}</div>
              </div>
              {settings.language === lang.code && (
                <div className="w-5 h-5 rounded-full bg-[#2481cc] flex items-center justify-center">
                  <Check className="w-3 h-3 text-white" />
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// ==========================================
// 11. DEVICES VIEW (Screenshot 15)
// ==========================================
const DevicesView: React.FC<{ onBack: () => void }> = ({ onBack }) => {
  const { settings, showToast } = useTelegram();
  const isArabic = settings.language === 'ar';

  return (
    <div className="flex flex-col h-full overflow-hidden bg-[#0e1621]">
      <SubPageHeader title={isArabic ? 'الأجهزة' : 'Devices'} onBack={onBack} />

      <div className="flex-1 overflow-y-auto p-4 space-y-4 text-center">
        <div className="p-6 bg-[#17212b] rounded-2xl border border-white/10 flex flex-col items-center">
          <div className="w-16 h-16 rounded-full bg-[#2481cc]/20 flex items-center justify-center text-[#2481cc] mb-3">
            <QrCode className="w-8 h-8" />
          </div>
          <div className="text-sm font-bold text-white mb-1">
            {isArabic ? 'ربط جهاز حاسوب أو ويب' : 'Link Desktop or Web Device'}
          </div>
          <div className="text-xs text-gray-400 max-w-xs mb-4">
            {isArabic
              ? 'تسجيل الدخول في تيليجرام سطح المكتب أو ويب عبر مسح رمز QR'
              : 'Scan QR code to log into Telegram Desktop or Web'}
          </div>
          <button
            onClick={() => showToast('Camera QR scanner opened', '📷')}
            className="px-6 py-2.5 bg-[#2481cc] hover:bg-[#1f6fa8] text-white text-xs font-bold rounded-xl shadow-md transition-colors flex items-center gap-2"
          >
            <QrCode className="w-4 h-4" />
            <span>{isArabic ? 'إضافة جهاز' : 'Link Device'}</span>
          </button>
        </div>

        {/* Current Device */}
        <div className="bg-[#17212b] rounded-2xl border border-white/10 p-4 text-left rtl:text-right space-y-1">
          <div className="text-[11px] font-bold text-[#5288c1] uppercase">{isArabic ? 'هذا الجهاز' : 'This Device'}</div>
          <div className="flex items-center gap-3 pt-2">
            <Smartphone className="w-6 h-6 text-emerald-400" />
            <div>
              <div className="text-xs font-bold text-white">Telegram for Android 12.9.2</div>
              <div className="text-[11px] text-gray-400">Online • Universal arm64-v8a</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// ==========================================
// 12. FOLDERS / CATEGORIES VIEW
// ==========================================
const FoldersView: React.FC<{ onBack: () => void }> = ({ onBack }) => {
  const { folders, showToast, settings } = useTelegram();
  const isArabic = settings.language === 'ar';

  return (
    <div className="flex flex-col h-full overflow-hidden bg-[#0e1621]">
      <SubPageHeader title={isArabic ? 'مجلدات المحادثات' : 'Chat Folders'} onBack={onBack} />

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <div className="bg-[#17212b] rounded-2xl border border-white/10 divide-y divide-white/5 overflow-hidden">
          {folders.map((f) => (
            <div key={f.id} className="p-3.5 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Folder className="w-5 h-5 text-[#5288c1]" />
                <div>
                  <div className="text-xs font-bold text-white">{isArabic ? f.nameAr : f.name}</div>
                  <div className="text-[11px] text-gray-400">{f.id === 'all' ? 'All chats included' : 'Filtered category'}</div>
                </div>
              </div>
              <span className="text-xs text-gray-400 font-mono">Default</span>
            </div>
          ))}
        </div>

        <button
          onClick={() => showToast(isArabic ? 'إنشاء مجلد جديد' : 'Create new folder', '📁')}
          className="w-full py-3 bg-[#2481cc] hover:bg-[#1f6fa8] text-white text-xs font-bold rounded-xl"
        >
          {isArabic ? '+ إنشاء مجلد جديد' : '+ Create New Folder'}
        </button>
      </div>
    </div>
  );
};

// ==========================================
// 13. THEMES BROWSER & SUPPORT GROUP & FAQ
// ==========================================
const ThemesBrowserView: React.FC<{ onBack: () => void }> = ({ onBack }) => {
  const { showToast, settings } = useTelegram();
  const isArabic = settings.language === 'ar';

  const themes = [
    { name: 'DrKLO Official Dark', author: 'Telegram Devs', downloads: '1.2M', color: '#17212b' },
    { name: 'Plus Cyberpunk Neo', author: 'Plus Team', downloads: '840K', color: '#0f172a' },
    { name: 'Emerald Forest Clean', author: 'ThemeStudio', downloads: '420K', color: '#064e3b' },
    { name: 'Midnight Violet Glass', author: 'Apex Dev', downloads: '310K', color: '#3b0764' },
  ];

  return (
    <div className="flex flex-col h-full overflow-hidden bg-[#0e1621]">
      <SubPageHeader title={isArabic ? 'تنزيل أنماط' : 'Download Themes'} onBack={onBack} />

      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {themes.map((t, i) => (
          <div key={i} className="p-3.5 bg-[#17212b] rounded-2xl border border-white/10 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl border border-white/20" style={{ backgroundColor: t.color }} />
              <div>
                <div className="text-xs font-bold text-white">{t.name}</div>
                <div className="text-[11px] text-gray-400">{t.author} • {t.downloads} downloads</div>
              </div>
            </div>
            <button
              onClick={() => showToast(`Applied ${t.name}`, '🎨')}
              className="px-3 py-1.5 bg-[#2481cc] hover:bg-[#1f6fa8] text-white text-xs font-bold rounded-lg"
            >
              {isArabic ? 'تطبيق' : 'Apply'}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

const SupportGroupView: React.FC<{ onBack: () => void }> = ({ onBack }) => {
  const { showToast, settings } = useTelegram();
  const isArabic = settings.language === 'ar';

  return (
    <div className="flex flex-col h-full overflow-hidden bg-[#0e1621]">
      <SubPageHeader title={isArabic ? 'مجموعة الدعم' : 'Support Group'} onBack={onBack} />

      <div className="flex-1 overflow-y-auto p-6 flex flex-col items-center justify-center text-center space-y-4">
        <div className="w-16 h-16 rounded-full bg-[#2481cc]/20 flex items-center justify-center text-[#2481cc]">
          <HelpCircle className="w-8 h-8" />
        </div>
        <div className="text-base font-bold text-white">
          {isArabic ? 'مجموعة الدعم الرسمي والتطوير' : 'Official Support & Dev Group'}
        </div>
        <div className="text-xs text-gray-400 max-w-sm">
          {isArabic
            ? 'انضم لمجتمع مطوري تيليجرام لمناقشة أحدث ميزات MTProto ومستودع DrKLO/Telegram'
            : 'Join the Telegram community to discuss MTProto features and repository enhancements'}
        </div>
        <button
          onClick={() => showToast('Joined Support Group', '👥')}
          className="px-6 py-2.5 bg-[#2481cc] hover:bg-[#1f6fa8] text-white text-xs font-bold rounded-xl"
        >
          {isArabic ? 'الانضمام للمجموعة (@tg_support)' : 'Join Group (@tg_support)'}
        </button>
      </div>
    </div>
  );
};

const FaqView: React.FC<{ onBack: () => void }> = ({ onBack }) => {
  const { settings } = useTelegram();
  const isArabic = settings.language === 'ar';

  return (
    <div className="flex flex-col h-full overflow-hidden bg-[#0e1621]">
      <SubPageHeader title={isArabic ? 'الأسئلة الشائعة' : 'Telegram FAQ'} onBack={onBack} />

      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {[
          { q: 'ما هو تيليجرام؟', a: 'تيليجرام هو تطبيق مراسلة يركز على السرعة والأمان، متزامن عبر كافة الأجهزة.' },
          { q: 'ما هو بروتوكول MTProto 2.0؟', a: 'بروتوكول تشفير متقدم مخصص لسرعة نقل البيانات مع خوادم التوزيع السحابي.' },
          { q: 'كيف أقوم بتبديل الحسابات؟', a: 'انقر على سهم الحسابات في درج التصفح لاختيار أي حساب مسجل أو إضافة حساب جديد.' },
        ].map((item, i) => (
          <div key={i} className="p-3.5 bg-[#17212b] rounded-2xl border border-white/10 space-y-1">
            <div className="text-xs font-bold text-white">{item.q}</div>
            <div className="text-xs text-gray-400">{item.a}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

const FeaturesView: React.FC<{ onBack: () => void }> = ({ onBack }) => {
  const { settings } = useTelegram();
  const isArabic = settings.language === 'ar';

  return (
    <div className="flex flex-col h-full overflow-hidden bg-[#0e1621]">
      <SubPageHeader title={isArabic ? 'ميزات تيليجرام' : 'Telegram Features'} onBack={onBack} />

      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {[
          'محادثات مشفرة ومكالمات P2P فائقة النقاء',
          'مجلدات وتصنيفات غير محدودة لتنظيم جهات الاتصال',
          'دعم الملصقات المتحركة بنظام Lottie المتطور',
          'مزامنة سحابية فورية وتخزين دائم في الرسائل المحفوظة',
        ].map((feat, i) => (
          <div key={i} className="p-3.5 bg-[#17212b] rounded-2xl border border-white/10 flex items-center gap-3">
            <Sparkles className="w-4 h-4 text-amber-400 shrink-0" />
            <span className="text-xs text-gray-200 font-medium">{feat}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

// Sub-Page Header Helper
const SubPageHeader: React.FC<{ title: string; onBack: () => void }> = ({ title, onBack }) => {
  const { settings } = useTelegram();
  const isArabic = settings.language === 'ar';
  const BackIcon = isArabic ? ArrowRight : ArrowLeft;

  return (
    <div className="flex items-center gap-3 px-4 py-3.5 bg-[#2481cc] text-white shrink-0 shadow-md">
      <button
        onClick={onBack}
        className="p-1.5 rounded-full hover:bg-white/15 transition-colors"
        title={isArabic ? 'رجوع' : 'Back'}
      >
        <BackIcon className="w-5 h-5" />
      </button>
      <span className="font-bold text-base">{title}</span>
    </div>
  );
};
