import React, { useState } from 'react';
import {
  X,
  Users,
  Megaphone,
  Lock,
  ArrowLeft,
  ArrowRight,
  Sparkles,
  ShieldCheck,
  Globe,
  LockKeyhole,
} from 'lucide-react';
import { useTelegram } from '../../context/TelegramContext';

export const NewChatModal: React.FC = () => {
  const { activeModal, setActiveModal, settings, createNewChat, showToast } = useTelegram();

  const [step, setStep] = useState<'select' | 'create_group' | 'create_channel' | 'create_secret'>('select');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [username, setUsername] = useState('');
  const [isPublic, setIsPublic] = useState(true);

  if (activeModal !== ('new-chat' as any)) return null;

  const isArabic = settings.language === 'ar';

  const handleClose = () => {
    setStep('select');
    setTitle('');
    setDescription('');
    setUsername('');
    setActiveModal('none');
  };

  const handleCreateChat = (type: 'group' | 'channel' | 'private') => {
    const cleanTitle = title.trim();
    if (!cleanTitle) {
      showToast(isArabic ? 'يرجى إدخال اسم المحادثة' : 'Please enter chat name', '⚠️');
      return;
    }

    const cleanUser = isPublic && username.trim() ? username.trim().replace(/^@/, '') : undefined;
    createNewChat(type, cleanTitle, cleanUser, description.trim());

    showToast(
      type === 'channel'
        ? isArabic ? `تم إنشاء القناة "${cleanTitle}" بنجاح 📢` : `Channel "${cleanTitle}" created! 📢`
        : type === 'group'
        ? isArabic ? `تم إنشاء المجموعة "${cleanTitle}" بنجاح 👥` : `Group "${cleanTitle}" created! 👥`
        : isArabic ? `تم إنشاء المحادثة السرية بنجاح 🔒` : `Secret chat initialized! 🔒`,
      '✨'
    );

    handleClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-xs select-none">
      <div className="bg-[#17212b] text-white rounded-2xl max-w-md w-full shadow-2xl border border-[#242f3d] overflow-hidden animate-in zoom-in-95">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-[#242f3d]">
          <div className="flex items-center gap-2">
            {step !== 'select' && (
              <button
                onClick={() => setStep('select')}
                className="p-1 rounded-lg hover:bg-white/10 text-gray-400 hover:text-white"
              >
                {isArabic ? <ArrowRight className="w-5 h-5" /> : <ArrowLeft className="w-5 h-5" />}
              </button>
            )}
            <h3 className="font-semibold text-base">
              {step === 'select'
                ? isArabic ? 'محادثة جديدة' : 'New Chat'
                : step === 'create_group'
                ? isArabic ? 'إنشاء مجموعة جديدة' : 'New Group'
                : step === 'create_channel'
                ? isArabic ? 'إنشاء قناة جديدة' : 'New Channel'
                : isArabic ? 'محادثة سرية جديدة' : 'New Secret Chat'}
            </h3>
          </div>
          <button onClick={handleClose} className="text-gray-400 hover:text-white p-1 rounded-lg">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Step 1: Type Selection with Official Telegram Definitions */}
        {step === 'select' && (
          <div className="p-3 space-y-2">
            {/* New Group */}
            <button
              onClick={() => {
                setTitle('');
                setDescription('');
                setUsername('');
                setStep('create_group');
              }}
              className="w-full flex items-start gap-3.5 p-3.5 rounded-xl hover:bg-white/5 border border-transparent hover:border-white/10 transition-all text-left rtl:text-right group"
            >
              <div className="w-10 h-10 rounded-xl bg-sky-500/15 border border-sky-500/30 flex items-center justify-center shrink-0 text-sky-400 group-hover:scale-105 transition-transform">
                <Users className="w-5 h-5" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="font-bold text-sm text-white group-hover:text-sky-300 transition-colors">
                  {isArabic ? 'مجموعة جديدة' : 'New Group'}
                </div>
                <div className="text-xs text-gray-400 leading-relaxed mt-0.5">
                  {isArabic
                    ? 'حتى 200,000 عضو، سجل محادثات دائم، وتبادل رسائل تفاعلي بين كافة الأعضاء.'
                    : 'Up to 200,000 members, persistent chat history, interactive discussions.'}
                </div>
              </div>
            </button>

            {/* New Channel */}
            <button
              onClick={() => {
                setTitle('');
                setDescription('');
                setUsername('');
                setStep('create_channel');
              }}
              className="w-full flex items-start gap-3.5 p-3.5 rounded-xl hover:bg-white/5 border border-transparent hover:border-white/10 transition-all text-left rtl:text-right group"
            >
              <div className="w-10 h-10 rounded-xl bg-amber-500/15 border border-amber-500/30 flex items-center justify-center shrink-0 text-amber-400 group-hover:scale-105 transition-transform">
                <Megaphone className="w-5 h-5" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="font-bold text-sm text-white group-hover:text-amber-300 transition-colors">
                  {isArabic ? 'قناة جديدة' : 'New Channel'}
                </div>
                <div className="text-xs text-gray-400 leading-relaxed mt-0.5">
                  {isArabic
                    ? 'أداة لبث الرسائل والوسائط لجمهور غير محدود. المنشورات تظهر باسم القناة فقط.'
                    : 'Tool for broadcasting messages to unlimited audiences. Posts appear with channel identity.'}
                </div>
              </div>
            </button>

            {/* New Secret Chat */}
            <button
              onClick={() => {
                setTitle('');
                setDescription('');
                setUsername('');
                setStep('create_secret');
              }}
              className="w-full flex items-start gap-3.5 p-3.5 rounded-xl hover:bg-white/5 border border-transparent hover:border-white/10 transition-all text-left rtl:text-right group"
            >
              <div className="w-10 h-10 rounded-xl bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center shrink-0 text-emerald-400 group-hover:scale-105 transition-transform">
                <Lock className="w-5 h-5" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="font-bold text-sm text-white group-hover:text-emerald-300 transition-colors">
                  {isArabic ? 'محادثة سرية جديدة' : 'New Secret Chat'}
                </div>
                <div className="text-xs text-gray-400 leading-relaxed mt-0.5">
                  {isArabic
                    ? 'تشفير تام E2EE من النهاية للنهاية، لا تترك أثراً في خوادم السحابة، مؤقت للتدمير الذاتي.'
                    : 'End-to-end encryption, zero server traces, self-destruct timers.'}
                </div>
              </div>
            </button>
          </div>
        )}

        {/* Step 2: Create Group Form */}
        {step === 'create_group' && (
          <div className="p-5 space-y-4">
            <div className="p-3 rounded-xl bg-sky-500/10 border border-sky-500/20 text-xs text-sky-300 leading-relaxed">
              {isArabic
                ? '👥 تنبيه المجموعة: جميع الأعضاء في المجموعة يمكنهم إرسال واستقبال الرسائل والوسائط.'
                : '👥 Group Notice: All members can send messages, participate in voice chats, and share files.'}
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-300 mb-1.5">
                {isArabic ? 'اسم المجموعة *' : 'Group Name *'}
              </label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder={isArabic ? 'مثال: عشاق البرمجة والتقنية' : 'e.g. Tech Pioneers'}
                className="w-full p-2.5 rounded-xl bg-black/30 border border-white/10 text-white text-sm focus:border-sky-500 focus:outline-none"
                autoFocus
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-300 mb-1.5">
                {isArabic ? 'الوصف (اختياري)' : 'Description (optional)'}
              </label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder={isArabic ? 'أهداف وقواعد المجموعة...' : 'Group rules & purpose...'}
                className="w-full p-2.5 rounded-xl bg-black/30 border border-white/10 text-white text-xs focus:border-sky-500 focus:outline-none resize-none h-20"
              />
            </div>

            <button
              onClick={() => handleCreateChat('group')}
              disabled={!title.trim()}
              className="w-full py-3 rounded-xl bg-[#2481cc] hover:bg-[#1c6fad] disabled:opacity-50 text-white font-bold text-sm shadow-md transition-all flex items-center justify-center gap-2"
            >
              <span>{isArabic ? 'إنشاء المجموعة' : 'Create Group'}</span>
              <Sparkles className="w-4 h-4" />
            </button>
          </div>
        )}

        {/* Step 3: Create Channel Form */}
        {step === 'create_channel' && (
          <div className="p-5 space-y-4">
            <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/20 text-xs text-amber-300 leading-relaxed">
              {isArabic
                ? '📢 تنبيه القناة: القناة مخصصة للبث في اتجاه واحد فقط. المشتركون لا يملكون صلاحية إرسال الرسائل.'
                : '📢 Channel Notice: Channels are for one-way broadcasting. Subscribers cannot post messages directly.'}
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-300 mb-1.5">
                {isArabic ? 'اسم القناة *' : 'Channel Name *'}
              </label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder={isArabic ? 'مثال: قناة الأخبار التقنية' : 'e.g. Daily Tech News'}
                className="w-full p-2.5 rounded-xl bg-black/30 border border-white/10 text-white text-sm focus:border-amber-500 focus:outline-none"
                autoFocus
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-300 mb-1.5">
                {isArabic ? 'معرّف القناة العام (@username)' : 'Channel Public Link (@username)'}
              </label>
              <div className="relative flex items-center">
                <span className="absolute left-3 rtl:left-auto rtl:right-3 text-gray-400 font-mono text-sm">@</span>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value.replace(/[^a-zA-Z0-9_]/g, ''))}
                  placeholder={isArabic ? 'اختر_اسم_مستخدم' : 'channel_handle'}
                  className="w-full py-2.5 px-8 rounded-xl bg-black/30 border border-white/10 text-sky-400 font-mono text-sm focus:border-amber-500 focus:outline-none"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-300 mb-1.5">
                {isArabic ? 'الوصف (اختياري)' : 'Description (optional)'}
              </label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder={isArabic ? 'وصف القناة ومحتواها...' : 'Channel topic and updates...'}
                className="w-full p-2.5 rounded-xl bg-black/30 border border-white/10 text-white text-xs focus:border-amber-500 focus:outline-none resize-none h-20"
              />
            </div>

            <button
              onClick={() => handleCreateChat('channel')}
              disabled={!title.trim()}
              className="w-full py-3 rounded-xl bg-[#2481cc] hover:bg-[#1c6fad] disabled:opacity-50 text-white font-bold text-sm shadow-md transition-all flex items-center justify-center gap-2"
            >
              <span>{isArabic ? 'إنشاء القناة' : 'Create Channel'}</span>
              <Sparkles className="w-4 h-4" />
            </button>
          </div>
        )}

        {/* Step 4: Create Secret Chat Form */}
        {step === 'create_secret' && (
          <div className="p-5 space-y-4">
            <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-xs text-emerald-300 leading-relaxed">
              {isArabic
                ? '🔒 تنبيه المحادثة السرية: محادثة مشفرة تشفيراً تاماً بين جهازين فقط ولا يمكن إعادة توجيه رسائلها.'
                : '🔒 Secret Chat Notice: End-to-end encrypted chat between two devices. Messages cannot be forwarded.'}
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-300 mb-1.5">
                {isArabic ? 'اسم جهة الاتصال *' : 'Contact Name *'}
              </label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder={isArabic ? 'اسم الشخص' : 'Contact name'}
                className="w-full p-2.5 rounded-xl bg-black/30 border border-white/10 text-white text-sm focus:border-emerald-500 focus:outline-none"
                autoFocus
              />
            </div>

            <button
              onClick={() => handleCreateChat('private')}
              disabled={!title.trim()}
              className="w-full py-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white font-bold text-sm shadow-md transition-all flex items-center justify-center gap-2"
            >
              <span>{isArabic ? 'بدء المحادثة المشفرة' : 'Start Secret Chat'}</span>
              <ShieldCheck className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
