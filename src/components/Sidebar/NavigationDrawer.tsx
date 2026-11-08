import React from 'react';
import {
  User,
  Settings,
  Bookmark,
  Moon,
  Sun,
  LogOut,
  UserPlus,
  X,
  ChevronDown,
  Download,
  Users,
  Phone,
  HelpCircle,
  Radio,
  Link2,
  MessageSquare,
  RotateCw,
} from 'lucide-react';
import { useTelegram } from '../../context/TelegramContext';

const PEER_GRADIENTS = [
  'from-[#e17076] to-[#f0858a]',
  'from-[#faa774] to-[#fbb88c]',
  'from-[#a695e7] to-[#b8a9ec]',
  'from-[#7bc862] to-[#8ed676]',
  'from-[#6ec9cb] to-[#539ec2]',
  'from-[#65aadd] to-[#a6ccf5]',
  'from-[#ee7aae] to-[#f4a1c5]',
];

function getPeerGradient(name: string = '') {
  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = (hash * 31 + name.charCodeAt(i)) % PEER_GRADIENTS.length;
  }
  return PEER_GRADIENTS[Math.abs(hash)] || PEER_GRADIENTS[0];
}

export const NavigationDrawer: React.FC = () => {
  const {
    isDrawerOpen,
    setIsDrawerOpen,
    currentUser,
    accounts,
    activeAccountId,
    switchAccount,
    setActiveModal,
    settings,
    updateSettings,
    logout,
    setActiveChatId,
    openSettingsPage,
  } = useTelegram();

  const [showAccounts, setShowAccounts] = React.useState(false);
  const [avatarError, setAvatarError] = React.useState(false);
  const isArabic = settings.language === 'ar';

  React.useEffect(() => {
    setAvatarError(false);
  }, [currentUser.avatar]);

  if (!isDrawerOpen) return null;

  const displayName = currentUser.name || [currentUser.first_name, currentUser.last_name].filter(Boolean).join(' ') || 'Telegram User';

  return (
    <div className="fixed inset-0 z-50 flex">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/60 transition-opacity"
        onClick={() => setIsDrawerOpen(false)}
      />

      {/* Drawer */}
      <div className="relative w-72 max-w-[80vw] h-full bg-[#17212b] text-white flex flex-col shadow-2xl z-10 animate-in slide-in-from-left duration-200">
        {/* User Profile Header */}
        <div className="p-4 bg-[#202b36] border-b border-[#242f3d]">
          <div className="flex items-center justify-between mb-3">
            <div className={`w-14 h-14 rounded-full flex items-center justify-center font-bold text-xl overflow-hidden border-2 border-white/20 ${
              currentUser.avatar && !avatarError ? 'bg-[#202b36]' : `bg-gradient-to-tr ${getPeerGradient(displayName)}`
            }`}>
              {currentUser.avatar && !avatarError ? (
                <img
                  src={currentUser.avatar}
                  alt={displayName}
                  className="w-full h-full object-cover"
                  loading="lazy"
                  referrerPolicy="no-referrer"
                  onError={() => setAvatarError(true)}
                />
              ) : (
                (displayName || 'U').charAt(0).toUpperCase()
              )}
            </div>
            <button
              onClick={() => setIsDrawerOpen(false)}
              className="p-1 rounded-full text-gray-400 hover:text-white"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          <div
            className="flex items-center justify-between cursor-pointer"
            onClick={() => setShowAccounts(!showAccounts)}
          >
            <div className="min-w-0 flex-1">
              <h3 className="font-semibold text-sm truncate">
                {displayName}
              </h3>
              <p className="text-xs text-gray-400 truncate">{currentUser.phone || (currentUser.username ? '@' + currentUser.username : '')}</p>
            </div>
            <ChevronDown
              className={`w-4 h-4 text-gray-400 transition-transform ${showAccounts ? 'rotate-180' : ''}`}
            />
          </div>
        </div>

        {/* Multi-Account Drawer Dropdown */}
        {showAccounts && (
          <div className="bg-[#1c2733] border-b border-[#242f3d] py-1 max-h-40 overflow-y-auto">
            {accounts.map((acc) => {
              const accName = acc.user.name || [acc.user.first_name, acc.user.last_name].filter(Boolean).join(' ') || 'Account';
              return (
                <div
                  key={acc.id}
                  onClick={() => {
                    switchAccount(acc.id);
                    setShowAccounts(false);
                  }}
                  className={`flex items-center gap-3 px-4 py-2 cursor-pointer hover:bg-white/5 ${
                    acc.id === activeAccountId ? 'text-[#2481cc] font-medium' : 'text-gray-300'
                  }`}
                >
                  <div className="w-7 h-7 rounded-full bg-[#2481cc]/20 flex items-center justify-center text-xs">
                    {accName.charAt(0)}
                  </div>
                  <span className="text-xs truncate flex-1">{accName}</span>
                </div>
              );
            })}
            <button
              onClick={() => {
                setActiveModal('add-account');
                setIsDrawerOpen(false);
              }}
              className="w-full flex items-center gap-3 px-4 py-2 text-xs text-[#2481cc] hover:bg-white/5 font-medium"
            >
              <UserPlus className="w-4 h-4" />
              <span>{isArabic ? 'إضافة حساب جديد' : 'Add Account'}</span>
            </button>
          </div>
        )}

        {/* Navigation Items */}
        <div className="flex-1 overflow-y-auto py-2">
          {/* New Group */}
          <button
            onClick={() => {
              setActiveModal('new-chat');
              setIsDrawerOpen(false);
            }}
            className="w-full flex items-center gap-4 px-4 py-3 hover:bg-white/5 text-sm text-gray-200 transition-colors"
          >
            <Users className="w-5 h-5 text-gray-400" />
            <span>{isArabic ? 'مجموعة جديدة' : 'New Group'}</span>
          </button>

          {/* Contacts */}
          <button
            onClick={() => {
              setActiveModal('contacts');
              setIsDrawerOpen(false);
            }}
            className="w-full flex items-center gap-4 px-4 py-3 hover:bg-white/5 text-sm text-gray-200 transition-colors"
          >
            <User className="w-5 h-5 text-gray-400" />
            <span>{isArabic ? 'جهات الاتصال' : 'Contacts'}</span>
          </button>

          {/* Calls */}
          <button
            onClick={() => {
              openSettingsPage('privacy_control');
              setIsDrawerOpen(false);
            }}
            className="w-full flex items-center gap-4 px-4 py-3 hover:bg-white/5 text-sm text-gray-200 transition-colors"
          >
            <Phone className="w-5 h-5 text-gray-400" />
            <span>{isArabic ? 'المكالمات' : 'Calls'}</span>
          </button>

          {/* Saved Messages */}
          <button
            onClick={() => {
              setActiveChatId('chat_saved_messages');
              setIsDrawerOpen(false);
            }}
            className="w-full flex items-center gap-4 px-4 py-3 hover:bg-white/5 text-sm text-gray-200 transition-colors"
          >
            <Bookmark className="w-5 h-5 text-gray-400" />
            <span>{isArabic ? 'الرسائل المحفوظة' : 'Saved Messages'}</span>
          </button>

          {/* Link Monitor & Instant Auto-Join System */}
          <button
            onClick={() => {
              setActiveModal('link-monitor');
              setIsDrawerOpen(false);
            }}
            className="w-full flex items-center justify-between px-4 py-3 hover:bg-white/5 text-sm text-gray-200 transition-colors group"
          >
            <div className="flex items-center gap-4">
              <Link2 className="w-5 h-5 text-[#2481cc] group-hover:scale-110 transition-transform" />
              <span className="font-medium text-white">
                {isArabic ? 'رادار مراقبة الروابط والانضمام' : 'Link Monitor & Auto-Join'}
              </span>
            </div>
            <span className="text-[10px] bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 font-medium px-2 py-0.5 rounded-full flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
              {isArabic ? 'نشط' : 'Active'}
            </span>
          </button>

          {/* Broadcast & Monitoring Automation System */}
          <button
            onClick={() => {
              setActiveModal('sender');
              setIsDrawerOpen(false);
            }}
            className="w-full flex items-center justify-between px-4 py-3 hover:bg-white/5 text-sm text-gray-200 transition-colors group"
          >
            <div className="flex items-center gap-4">
              <Radio className="w-5 h-5 text-[#2481cc] group-hover:scale-110 transition-transform animate-pulse" />
              <span className="font-medium text-white">
                {isArabic ? 'نظام الإرسال والمراقبة' : 'Broadcast & Monitoring'}
              </span>
            </div>
            <span className="text-[10px] bg-[#2481cc]/20 text-[#2481cc] border border-[#2481cc]/40 font-mono px-2 py-0.5 rounded-full font-bold">
              PRO
            </span>
          </button>

          {/* Auto Responder System */}
          <button
            onClick={() => {
              setActiveModal('auto-responder');
              setIsDrawerOpen(false);
            }}
            className="w-full flex items-center justify-between px-4 py-3 hover:bg-white/5 text-sm text-gray-200 transition-colors group"
          >
            <div className="flex items-center gap-4">
              <MessageSquare className="w-5 h-5 text-emerald-400 group-hover:scale-110 transition-transform" />
              <span className="font-medium text-white">
                {isArabic ? 'الردود التلقائية الذكية' : 'Auto Replies'}
              </span>
            </div>
            <span className="text-[10px] bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 font-medium px-2 py-0.5 rounded-full">
              {isArabic ? 'ذكي' : 'Smart'}
            </span>
          </button>

          {/* Rotating Broadcast System */}
          <button
            onClick={() => {
              setActiveModal('sender');
              setIsDrawerOpen(false);
            }}
            className="w-full flex items-center justify-between px-4 py-3 hover:bg-white/5 text-sm text-gray-200 transition-colors group"
          >
            <div className="flex items-center gap-4">
              <RotateCw className="w-5 h-5 text-amber-400 group-hover:rotate-90 transition-transform" />
              <span className="font-medium text-white">
                {isArabic ? 'النشر الدوري المتسلسل' : 'Rotating Broadcast'}
              </span>
            </div>
            <span className="text-[10px] bg-amber-500/20 text-amber-400 border border-amber-500/40 font-mono px-2 py-0.5 rounded-full font-bold">
              5X
            </span>
          </button>

          {/* Settings */}
          <button
            onClick={() => {
              openSettingsPage('main');
              setIsDrawerOpen(false);
            }}
            className="w-full flex items-center gap-4 px-4 py-3 hover:bg-white/5 text-sm text-gray-200 transition-colors"
          >
            <Settings className="w-5 h-5 text-gray-400" />
            <span>{isArabic ? 'الإعدادات' : 'Settings'}</span>
          </button>

          <div className="border-t border-[#242f3d] my-1" />

          {/* Telegram Features */}
          <button
            onClick={() => {
              openSettingsPage('features');
              setIsDrawerOpen(false);
            }}
            className="w-full flex items-center gap-4 px-4 py-3 hover:bg-white/5 text-sm text-gray-200 transition-colors"
          >
            <HelpCircle className="w-5 h-5 text-gray-400" />
            <span>{isArabic ? 'ميزات تيليجرام' : 'Telegram Features'}</span>
          </button>

          {/* Install App */}
          <button
            onClick={() => {
              setActiveModal('apk-installer');
              setIsDrawerOpen(false);
            }}
            className="w-full flex items-center gap-4 px-4 py-3 hover:bg-white/5 text-sm text-gray-200 transition-colors"
          >
            <Download className="w-5 h-5 text-gray-400" />
            <span>{isArabic ? 'تثبيت التطبيق' : 'Install App'}</span>
          </button>

          {/* Day / Night Mode Toggle */}
          <button
            onClick={() => {
              updateSettings({ theme: settings.theme === 'dark' ? 'light' : 'dark' });
            }}
            className="w-full flex items-center gap-4 px-4 py-3 hover:bg-white/5 text-sm text-gray-200 transition-colors"
          >
            {settings.theme === 'dark' ? (
              <Sun className="w-5 h-5 text-yellow-400" />
            ) : (
              <Moon className="w-5 h-5 text-gray-400" />
            )}
            <span>
              {settings.theme === 'dark'
                ? isArabic ? 'الوضع النهاري' : 'Day Mode'
                : isArabic ? 'الوضع الليلي' : 'Night Mode'}
            </span>
          </button>

          <div className="border-t border-[#242f3d] my-2" />

          {/* Logout Trigger */}
          <button
            onClick={() => {
              setIsDrawerOpen(false);
              logout();
            }}
            className="w-full flex items-center gap-4 px-4 py-3 hover:bg-red-500/10 text-sm text-red-400 transition-colors"
          >
            <LogOut className="w-5 h-5" />
            <span>{isArabic ? 'تسجيل الخروج' : 'Log Out'}</span>
          </button>
        </div>
      </div>
    </div>
  );
};
