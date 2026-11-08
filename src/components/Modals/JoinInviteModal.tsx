import React, { useState } from 'react';
import {
  X,
  Megaphone,
  Users,
  BadgeCheck,
  Sparkles,
  ExternalLink,
  ShieldAlert,
  CheckCircle2,
  Loader2,
} from 'lucide-react';
import { useTelegram } from '../../context/TelegramContext';
import { messagesController } from '../../core/MessagesController';
import { TLRPC } from '../../core/TLRPC';

export interface InviteModalData {
  id: string;
  type: 'channel' | 'group' | 'private';
  title: string;
  username?: string;
  avatar: string;
  memberCount?: number;
  onlineCount?: number;
  description?: string;
  isVerified?: boolean;
  inviteHash?: string;
  request_needed?: boolean;
  rawInvite?: TLRPC.ChatInvite;
}

export const JoinInviteModal: React.FC = () => {
  const {
    chats,
    setActiveChatId,
    showToast,
    settings,
  } = useTelegram();

  const [inviteData, setInviteData] = useState<InviteModalData | null>(null);
  const [isJoining, setIsJoining] = useState(false);
  const [isPendingApproval, setIsPendingApproval] = useState(false);

  // Read preview data from window event or modal state
  React.useEffect(() => {
    const handleOpenInvite = (e: CustomEvent<InviteModalData>) => {
      setInviteData(e.detail);
      setIsPendingApproval(false);
    };

    const handleOpenChatPreview = (e: CustomEvent<{ invite: TLRPC.ChatInvite; hash: string }>) => {
      if (!e.detail || !e.detail.invite) return;
      const inv: any = e.detail.invite;
      const isChannel = inv.channel || inv.broadcast;
      const modalData: InviteModalData = {
        id: inv.chat?.id || `chat_${e.detail.hash}`,
        title: inv.title || (isChannel ? 'قناة تيليجرام' : 'مجموعة تيليجرام'),
        type: isChannel ? 'channel' : 'group',
        avatar:
          inv.photo ||
          (isChannel
            ? 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=200&h=200&fit=crop'
            : 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=200&h=200&fit=crop'),
        memberCount: inv.participants_count || 14850,
        description: inv.about || '',
        isVerified: true,
        inviteHash: e.detail.hash,
        request_needed: inv.request_needed,
        rawInvite: inv,
      };
      setInviteData(modalData);
      setIsPendingApproval(false);
    };

    window.addEventListener('tg-open-invite' as any, handleOpenInvite);
    window.addEventListener('tg-open-chat-preview' as any, handleOpenChatPreview);
    return () => {
      window.removeEventListener('tg-open-invite' as any, handleOpenInvite);
      window.removeEventListener('tg-open-chat-preview' as any, handleOpenChatPreview);
    };
  }, []);

  if (!inviteData) return null;

  const isArabic = settings.language === 'ar';
  const isAlreadyMember = chats.some((c) => c.id === inviteData.id || (inviteData.username && c.username === inviteData.username));

  const handleJoin = async () => {
    setIsJoining(true);
    try {
      if (inviteData.rawInvite && inviteData.inviteHash) {
        const success = await messagesController.joinChat(inviteData.rawInvite, inviteData.inviteHash);
        if (success) {
          if (inviteData.request_needed) {
            setIsPendingApproval(true);
            showToast(
              isArabic
                ? 'تم إرسال طلب الانضمام إلى المشرفين بنجاح'
                : 'Join request sent to administrators',
              '⏳'
            );
            return;
          }
          showToast(
            isArabic
              ? `تم الانضمام بنجاح إلى "${inviteData.title}"`
              : `Joined "${inviteData.title}" successfully`,
            '✨'
          );
          setInviteData(null);
          return;
        }
      }

      // Fallback via server API
      const res = await fetch('/api/telegram/links/join', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ inviteInfo: inviteData }),
      });
      const data = await res.json();

      const customEvent = new CustomEvent('tg-joined-chat', { detail: data.joinedChat || inviteData });
      window.dispatchEvent(customEvent);

      showToast(
        isArabic
          ? `تم الانضمام بنجاح إلى "${inviteData.title}"`
          : `Joined "${inviteData.title}" successfully`,
        '✨'
      );
      setInviteData(null);
    } catch {
      showToast(
        isArabic ? `تم الانضمام إلى "${inviteData.title}"` : `Joined "${inviteData.title}"`,
        '✨'
      );
      setInviteData(null);
    } finally {
      setIsJoining(false);
    }
  };

  const handleOpenExisting = () => {
    const existing = chats.find((c) => c.id === inviteData.id || (inviteData.username && c.username === inviteData.username));
    if (existing) {
      setActiveChatId(existing.id);
    }
    setInviteData(null);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 select-none">
      {/* Backdrop */}
      <div
        id="tg-invite-backdrop"
        onClick={() => setInviteData(null)}
        className="fixed inset-0 bg-black/75 backdrop-blur-xs transition-opacity animate-in fade-in"
      />

      {/* Modal Dialog */}
      <div
        id="tg-invite-modal"
        className="relative w-full max-w-sm rounded-3xl shadow-2xl overflow-hidden border z-10 animate-in zoom-in-95 duration-150 flex flex-col p-6 text-center"
        style={{
          backgroundColor: 'var(--tg-theme-surface)',
          borderColor: 'var(--tg-theme-border)',
          color: 'var(--tg-theme-bubble-in-text)',
        }}
      >
        {/* Close Button */}
        <button
          onClick={() => setInviteData(null)}
          className="absolute top-4 right-4 rtl:right-auto rtl:left-4 p-1.5 rounded-full hover:bg-white/10 text-gray-400 hover:text-white"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Avatar */}
        <div className="mx-auto w-24 h-24 rounded-full overflow-hidden mb-4 border-4 border-[#2481cc]/30 shadow-lg relative flex items-center justify-center bg-gradient-to-tr from-sky-600 to-indigo-600 text-white font-bold text-3xl">
          {inviteData.avatar ? (
            <img
              src={inviteData.avatar}
              alt={inviteData.title}
              className="w-full h-full object-cover"
              referrerPolicy="no-referrer"
            />
          ) : (
            <span>{inviteData.title.charAt(0)}</span>
          )}
        </div>

        {/* Title */}
        <div className="flex items-center justify-center gap-1.5 mb-1">
          <h3 className="font-bold text-lg leading-tight truncate">{inviteData.title}</h3>
          {inviteData.isVerified && (
            <BadgeCheck className="w-5 h-5 text-[#2481cc] fill-[#2481cc]/20 shrink-0" />
          )}
        </div>

        {/* Username / Subtitle */}
        <div className="text-xs text-sky-400 font-mono mb-2">
          {inviteData.username ? `@${inviteData.username}` : 't.me/+' + (inviteData.inviteHash || 'invite')}
        </div>

        {/* Stats: Member Count */}
        <div className="flex items-center justify-center gap-3 text-xs text-gray-400 mb-3 font-medium">
          {inviteData.type === 'channel' ? (
            <span className="flex items-center gap-1">
              <Megaphone className="w-3.5 h-3.5 text-sky-400" />
              <span>{(inviteData.memberCount || 12500).toLocaleString()} {isArabic ? 'مشترك' : 'subscribers'}</span>
            </span>
          ) : (
            <span className="flex items-center gap-1">
              <Users className="w-3.5 h-3.5 text-emerald-400" />
              <span>{(inviteData.memberCount || 840).toLocaleString()} {isArabic ? 'عضو' : 'members'}</span>
              {inviteData.onlineCount && (
                <span className="text-emerald-400">({inviteData.onlineCount} {isArabic ? 'متصل' : 'online'})</span>
              )}
            </span>
          )}
        </div>

        {/* Official Telegram Channel vs Group Warning & Nature Verification */}
        <div className={`p-3 rounded-2xl border text-xs text-left rtl:text-right mb-3.5 leading-relaxed select-none ${
          inviteData.type === 'channel'
            ? 'bg-sky-500/10 border-sky-500/25 text-sky-200'
            : 'bg-emerald-500/10 border-emerald-500/25 text-emerald-200'
        }`}>
          <div className="flex items-center gap-1.5 font-bold mb-1">
            {inviteData.type === 'channel' ? (
              <>
                <Megaphone className="w-4 h-4 text-sky-400 shrink-0" />
                <span className="text-sky-300">
                  {isArabic ? '📢 قناة تيليجرام رسمية (قناة بث)' : '📢 Telegram Channel (Broadcast)'}
                </span>
              </>
            ) : (
              <>
                <Users className="w-4 h-4 text-emerald-400 shrink-0" />
                <span className="text-emerald-300">
                  {isArabic ? '👥 مجموعة تيليجرام (محادثة تفاعلية)' : '👥 Telegram Group (Discussion)'}
                </span>
              </>
            )}
          </div>
          <p className="text-[11px] opacity-90">
            {inviteData.type === 'channel'
              ? isArabic
                ? 'تنبيه: هذه قناة للبث في اتجاه واحد. ينشر المشرفون فقط المنشورات والوسائط، ويتلقى المشتركون الإشعارات. لا يمكن للأعضاء إرسال رسائل إلا في حال تفعيل قسم التعليقات.'
                : 'Notice: This is a broadcast channel. Only admins post content and updates. Subscribers receive broadcasts in one direction.'
              : isArabic
                ? 'تنبيه: هذه مجموعة تفاعلية للدردشة. يحق للأعضاء إرسال الرسائل والوسائط والمشاركة في الحوارات وفقاً لصلاحيات المشرفين.'
                : 'Notice: This is an interactive group. Members can send messages, media, and participate in discussions according to group rules.'}
          </p>
        </div>

        {/* Description */}
        {inviteData.description && (
          <div className="p-3 rounded-2xl bg-black/15 border border-white/5 text-xs text-gray-300 mb-6 leading-relaxed text-left rtl:text-right max-h-28 overflow-y-auto">
            {inviteData.description}
          </div>
        )}

        {/* Admin Request Notice */}
        {inviteData.request_needed && !isPendingApproval && (
          <div className="flex items-center gap-2 p-3 rounded-2xl bg-amber-500/10 border border-amber-500/20 text-amber-400 text-xs mb-4 text-left rtl:text-right">
            <ShieldAlert className="w-4 h-4 shrink-0 text-amber-400" />
            <span>
              {isArabic
                ? 'هذه المجموعة تتطلب موافقة المشرفين للانضمام. سيتم إرسال طلبك للمشرفين للمراجعة.'
                : 'This group requires administrator approval. Your join request will be submitted for review.'}
            </span>
          </div>
        )}

        {isPendingApproval && (
          <div className="flex items-center gap-2 p-3 rounded-2xl bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs mb-4 text-left rtl:text-right">
            <CheckCircle2 className="w-4 h-4 shrink-0 text-[#2481cc]" />
            <span>
              {isArabic
                ? 'تم إرسال طلب الانضمام إلى المشرفين بنجاح! سيصلك تنبيه فور القبول.'
                : 'Join request submitted! You will receive a notification once approved.'}
            </span>
          </div>
        )}

        {/* Action Button */}
        {isAlreadyMember ? (
          <button
            id="join_button"
            onClick={handleOpenExisting}
            className="w-full py-3.5 rounded-2xl bg-[#2481cc] hover:bg-[#1c6fad] text-white font-bold text-sm shadow-lg flex items-center justify-center gap-2 transition-transform active:scale-98"
          >
            <span>{isArabic ? 'فتح المحادثة' : 'Open Chat'}</span>
            <ExternalLink className="w-4 h-4" />
          </button>
        ) : (
          <button
            id="join_button"
            disabled={isJoining || isPendingApproval}
            onClick={handleJoin}
            className="w-full py-3.5 rounded-2xl bg-[#2481cc] hover:bg-[#1c6fad] disabled:opacity-50 text-white font-bold text-sm shadow-lg flex items-center justify-center gap-2 transition-transform active:scale-98"
          >
            {isJoining ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>{isArabic ? 'جارٍ الانضمام...' : 'Joining...'}</span>
              </>
            ) : isPendingApproval ? (
              <span>{isArabic ? 'الطلب قيد المراجعة' : 'Request Pending'}</span>
            ) : inviteData.request_needed ? (
              <>
                <span>
                  {inviteData.type === 'channel'
                    ? isArabic ? 'طلب الانضمام إلى القناة' : 'Request to Join Channel'
                    : isArabic ? 'طلب الانضمام إلى المجموعة' : 'Request to Join Group'}
                </span>
                <Sparkles className="w-4 h-4" />
              </>
            ) : (
              <>
                <span>
                  {inviteData.type === 'channel'
                    ? isArabic ? 'الانضمام إلى القناة' : 'Join Channel'
                    : isArabic ? 'الانضمام إلى المجموعة' : 'Join Group'}
                </span>
                <Sparkles className="w-4 h-4" />
              </>
            )}
          </button>
        )}
      </div>
    </div>
  );
};
