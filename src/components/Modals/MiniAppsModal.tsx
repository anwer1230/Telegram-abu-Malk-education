import React, { useState } from 'react';
import {
  Sparkles,
  X,
  ExternalLink,
  Maximize2,
  Minimize2,
  RefreshCw,
  Share2,
  ShieldCheck,
  Zap,
  Bot,
  Gamepad2,
  Wallet,
  Globe,
  Coins,
  CheckCircle2,
} from 'lucide-react';
import { useTelegram } from '../../context/TelegramContext';
import confetti from 'canvas-confetti';

interface MiniAppItem {
  id: string;
  name: string;
  nameAr: string;
  botUsername: string;
  category: 'game' | 'utility' | 'crypto' | 'ai';
  icon: string;
  description: string;
  descriptionAr: string;
  url: string;
  starsPrice?: number;
  featured?: boolean;
}

const FEATURED_MINI_APPS: MiniAppItem[] = [
  {
    id: 'app_notcoin',
    name: 'Notcoin Clicker',
    nameAr: 'نوت كوين (Notcoin)',
    botUsername: '@notcoin_bot',
    category: 'crypto',
    icon: '🟡',
    description: 'Tap-to-earn game & Web3 gateway with millions of players.',
    descriptionAr: 'لعبة الضغط للربح وبوابة Web3 الشهيرة على شبكة TON.',
    url: 'https://notcoin.com',
    starsPrice: 0,
    featured: true,
  },
  {
    id: 'app_major',
    name: 'Major Stars & Games',
    nameAr: 'ماجور للنجوم والألعاب',
    botUsername: '@major_official_bot',
    category: 'game',
    icon: '⭐',
    description: 'Compete for Telegram Stars rankings and mini-game bonuses.',
    descriptionAr: 'تنافس في تصنيفات نجوم تيليجرام واكسب مكافآت يومية.',
    url: 'https://telegram.org/blog/stars',
    starsPrice: 50,
    featured: true,
  },
  {
    id: 'app_wallet',
    name: 'TON Space Wallet',
    nameAr: 'محفظة TON الرسمية',
    botUsername: '@wallet',
    category: 'crypto',
    icon: '💎',
    description: 'Non-custodial cryptocurrency wallet built directly into Telegram.',
    descriptionAr: 'المحفظة الرقمية اللامركزية المدمجة في تيليجرام لإدارة وتداول TON.',
    url: 'https://wallet.tg',
    starsPrice: 0,
    featured: true,
  },
  {
    id: 'app_ai_studio',
    name: 'AI Studio Assistant',
    nameAr: 'مساعد AI Studio الذكي',
    botUsername: '@aistudio_bot',
    category: 'ai',
    icon: '🤖',
    description: 'Next-gen Gemini Multimodal Assistant embedded in Telegram.',
    descriptionAr: 'مساعد الذكاء الاصطناعي التوليدي والترجمة الفورية من Google Gemini.',
    url: 'https://ai.google.dev',
    starsPrice: 0,
    featured: true,
  },
  {
    id: 'app_catizen',
    name: 'Catizen Game Center',
    nameAr: 'كاتيزين - مركز ألعاب القطط',
    botUsername: '@catizen_bot',
    category: 'game',
    icon: '🐱',
    description: 'Playful Web3 swipe-and-merge game ecosystem on TON.',
    descriptionAr: 'لعبة دمج القطط التفاعلية مع خيارات الشراء بنجوم تيليجرام.',
    url: 'https://catizen.ai',
    starsPrice: 20,
  },
];

interface MiniAppsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const MiniAppsModal: React.FC<MiniAppsModalProps> = ({ isOpen, onClose }) => {
  const { currentUser, settings, showToast } = useTelegram();
  const isArabic = settings.language === 'ar';

  const [activeApp, setActiveApp] = useState<MiniAppItem | null>(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [activeCategory, setActiveCategory] = useState<string>('all');
  const [userStars, setUserStars] = useState<number>(() => {
    return Number(localStorage.getItem('tg_user_stars_balance') || 250);
  });
  const [isSimulatingLaunch, setIsSimulatingLaunch] = useState(false);

  if (!isOpen) return null;

  const handleLaunchApp = (app: MiniAppItem) => {
    setIsSimulatingLaunch(true);
    setTimeout(() => {
      setActiveApp(app);
      setIsSimulatingLaunch(false);
      try {
        confetti({
          particleCount: 30,
          spread: 60,
          origin: { y: 0.6 },
        });
      } catch {}
    }, 400);
  };

  const handleSpendStars = (amount: number, appName: string) => {
    if (userStars < amount) {
      showToast(
        isArabic ? 'رصيدك من نجوم Telegram غير كافٍ!' : 'Insufficient Telegram Stars balance!',
        '⚠️'
      );
      return;
    }
    const newBal = userStars - amount;
    setUserStars(newBal);
    localStorage.setItem('tg_user_stars_balance', String(newBal));
    try {
      confetti({
        particleCount: 50,
        spread: 70,
        origin: { y: 0.5 },
      });
    } catch {}
    showToast(
      isArabic
        ? `تم دفع ${amount} ⭐ بنجاح داخل ${appName}`
        : `Paid ${amount} ⭐ successfully in ${appName}`,
      '✨'
    );
  };

  const filteredApps =
    activeCategory === 'all'
      ? FEATURED_MINI_APPS
      : FEATURED_MINI_APPS.filter((a) => a.category === activeCategory);

  return (
    <div
      id="modal-telegram-mini-apps"
      className="fixed inset-0 z-[9990] flex items-center justify-center p-2 sm:p-4 bg-black/80 backdrop-blur-md animate-in fade-in select-none"
      dir={isArabic ? 'rtl' : 'ltr'}
    >
      <div
        className={`w-full bg-[#17212b] border border-white/10 text-white rounded-3xl shadow-2xl flex flex-col overflow-hidden transition-all duration-300 ${
          activeApp && isFullscreen
            ? 'h-[98vh] max-w-5xl'
            : activeApp
            ? 'h-[85vh] max-w-4xl'
            : 'max-h-[85vh] max-w-2xl'
        }`}
      >
        {/* Header */}
        <div className="h-14 px-4 border-b border-white/10 flex items-center justify-between bg-[#1e2c3a]/80 shrink-0">
          <div className="flex items-center gap-3 min-w-0">
            {activeApp ? (
              <>
                <button
                  onClick={() => setActiveApp(null)}
                  className="px-2.5 py-1 rounded-xl bg-white/10 hover:bg-white/15 text-xs font-semibold text-sky-400"
                >
                  {isArabic ? '← العودة' : '← Back'}
                </button>
                <div className="text-2xl">{activeApp.icon}</div>
                <div className="min-w-0">
                  <div className="text-sm font-bold text-white truncate flex items-center gap-1.5">
                    <span>{isArabic ? activeApp.nameAr : activeApp.name}</span>
                    <span className="px-1.5 py-0.5 rounded-full text-[9px] bg-emerald-500/20 text-emerald-300 font-mono">
                      bot API
                    </span>
                  </div>
                  <div className="text-[11px] text-gray-400 font-mono truncate">
                    {activeApp.botUsername}
                  </div>
                </div>
              </>
            ) : (
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-[#2481cc] to-sky-400 flex items-center justify-center shadow">
                  <Sparkles className="w-4 h-4 text-white" />
                </div>
                <div>
                  <h3 className="font-bold text-sm text-white">
                    {isArabic ? 'تطبيقات تيليجرام المصغرة (TMA)' : 'Telegram Mini Apps (TMA)'}
                  </h3>
                  <p className="text-[11px] text-gray-400">
                    {isArabic ? 'DrKLO bots.invokeWebView & SDK' : 'Embedded WebApps & Stars SDK'}
                  </p>
                </div>
              </div>
            )}
          </div>

          <div className="flex items-center gap-2">
            {/* Stars Balance Badge */}
            <div
              onClick={() => {
                const add = userStars + 100;
                setUserStars(add);
                localStorage.setItem('tg_user_stars_balance', String(add));
                showToast(isArabic ? 'تم شحن 100 نجمة ⭐' : 'Added 100 Stars ⭐', '⭐');
              }}
              className="flex items-center gap-1.5 px-3 py-1 rounded-xl bg-amber-500/15 border border-amber-500/30 text-amber-300 text-xs font-bold cursor-pointer hover:bg-amber-500/25 transition-colors"
              title={isArabic ? 'انقر لشحن رصيد النجوم' : 'Click to top-up stars'}
            >
              <Coins className="w-3.5 h-3.5 text-amber-400" />
              <span>{userStars} ⭐</span>
            </div>

            {activeApp && (
              <button
                onClick={() => setIsFullscreen(!isFullscreen)}
                className="p-2 rounded-xl text-gray-400 hover:text-white hover:bg-white/10 transition-colors"
                title={isFullscreen ? 'Exit Fullscreen' : 'Fullscreen'}
              >
                {isFullscreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
              </button>
            )}

            <button
              onClick={onClose}
              className="p-2 rounded-xl text-gray-400 hover:text-white hover:bg-white/10 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Content Body */}
        {activeApp ? (
          /* Active Mini App Webview Sandbox Container */
          <div className="flex-1 flex flex-col bg-[#0e1621] relative overflow-hidden">
            {/* MiniApp Mock Bar */}
            <div className="px-3 py-1.5 bg-[#17212b] border-b border-white/5 flex items-center justify-between text-[11px] text-gray-400">
              <div className="flex items-center gap-2 truncate">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                <span className="font-mono truncate">tg://webapp?initData=user_{currentUser.id}</span>
              </div>
              <div className="flex items-center gap-2">
                {activeApp.starsPrice && activeApp.starsPrice > 0 ? (
                  <button
                    onClick={() => handleSpendStars(activeApp.starsPrice!, activeApp.name)}
                    className="px-2.5 py-1 rounded-lg bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 font-bold border border-amber-500/30 flex items-center gap-1 transition-colors"
                  >
                    <span>{isArabic ? 'دفع بالنجوم' : 'Pay with Stars'}</span>
                    <span className="font-mono">({activeApp.starsPrice} ⭐)</span>
                  </button>
                ) : null}
              </div>
            </div>

            {/* Embedded Live Container Interface */}
            <div className="flex-1 flex flex-col items-center justify-center p-6 text-center space-y-4">
              <div className="w-20 h-20 rounded-3xl bg-gradient-to-tr from-[#2481cc] to-sky-400 flex items-center justify-center text-4xl shadow-xl animate-bounce">
                {activeApp.icon}
              </div>
              <div className="space-y-1 max-w-md">
                <h4 className="text-xl font-bold text-white">
                  {isArabic ? activeApp.nameAr : activeApp.name}
                </h4>
                <p className="text-xs text-gray-400">
                  {isArabic ? activeApp.descriptionAr : activeApp.description}
                </p>
              </div>

              {/* WebApp Simulated View */}
              <div className="w-full max-w-md p-4 rounded-2xl bg-[#17212b] border border-white/10 text-left rtl:text-right space-y-3 shadow-inner">
                <div className="flex items-center justify-between text-xs pb-2 border-b border-white/5">
                  <span className="text-gray-400">{isArabic ? 'المستخدم الموثق' : 'Authenticated Peer'}</span>
                  <span className="font-bold text-sky-400">{currentUser.name} (@{currentUser.username || 'user'})</span>
                </div>
                <div className="flex items-center justify-between text-xs pb-2 border-b border-white/5">
                  <span className="text-gray-400">{isArabic ? 'بروتوكول الويب' : 'SDK Bridge'}</span>
                  <span className="font-mono text-emerald-400">Telegram.WebApp v7.10</span>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-gray-400">{isArabic ? 'رصيد النجوم' : 'Stars Available'}</span>
                  <span className="font-bold text-amber-400">{userStars} ⭐</span>
                </div>

                <a
                  href={activeApp.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-full mt-2 py-2.5 px-4 rounded-xl bg-[#2481cc] hover:bg-[#1c6fad] text-white font-bold text-xs flex items-center justify-center gap-2 transition-transform active:scale-98"
                >
                  <ExternalLink className="w-4 h-4" />
                  <span>{isArabic ? 'فتح التطبيق في نافذة خارجية' : 'Open in External Window'}</span>
                </a>
              </div>
            </div>
          </div>
        ) : (
          /* Mini Apps Directory Catalog */
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {/* Category Filter Pills */}
            <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-none">
              {[
                { id: 'all', label: isArabic ? 'الكل' : 'All', icon: Sparkles },
                { id: 'game', label: isArabic ? 'ألعاب' : 'Games', icon: Gamepad2 },
                { id: 'crypto', label: isArabic ? 'Web3 & TON' : 'Web3 & TON', icon: Wallet },
                { id: 'ai', label: isArabic ? 'ذكاء اصطناعي' : 'AI Bots', icon: Bot },
              ].map((cat) => {
                const Icon = cat.icon;
                const isActive = activeCategory === cat.id;
                return (
                  <button
                    key={cat.id}
                    onClick={() => setActiveCategory(cat.id)}
                    className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold shrink-0 transition-all ${
                      isActive
                        ? 'bg-[#2481cc] text-white shadow-md'
                        : 'bg-white/5 text-gray-300 hover:bg-white/10'
                    }`}
                  >
                    <Icon className="w-3.5 h-3.5" />
                    <span>{cat.label}</span>
                  </button>
                );
              })}
            </div>

            {/* Apps Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {filteredApps.map((app) => (
                <div
                  key={app.id}
                  onClick={() => handleLaunchApp(app)}
                  className="p-3.5 rounded-2xl bg-[#1e2c3a]/50 hover:bg-[#1e2c3a] border border-white/5 hover:border-sky-500/30 transition-all cursor-pointer flex items-start gap-3.5 group relative"
                >
                  <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-black/40 to-white/5 border border-white/10 flex items-center justify-center text-2xl shrink-0 group-hover:scale-105 transition-transform">
                    {app.icon}
                  </div>
                  <div className="min-w-0 flex-1 space-y-1">
                    <div className="flex items-center justify-between">
                      <div className="font-bold text-sm text-white group-hover:text-sky-300 transition-colors truncate">
                        {isArabic ? app.nameAr : app.name}
                      </div>
                      {app.starsPrice && app.starsPrice > 0 ? (
                        <span className="text-[10px] font-bold px-1.5 py-0.5 rounded-md bg-amber-500/20 text-amber-300 border border-amber-500/30">
                          {app.starsPrice} ⭐
                        </span>
                      ) : (
                        <span className="text-[10px] font-bold px-1.5 py-0.5 rounded-md bg-emerald-500/20 text-emerald-300">
                          FREE
                        </span>
                      )}
                    </div>
                    <p className="text-[11px] text-gray-400 line-clamp-2 leading-relaxed">
                      {isArabic ? app.descriptionAr : app.description}
                    </p>
                    <div className="text-[10px] text-sky-400 font-mono flex items-center gap-1 pt-0.5">
                      <Zap className="w-3 h-3 text-sky-400" />
                      <span>{app.botUsername}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
