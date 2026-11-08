/**
 * ChatInvitePreview.tsx - Official DrKLO/Telegram Android ChatActivity Invite Preview
 * Replicated from org.telegram.ui.ChatActivity.java
 *
 * Implements:
 * - Preview banner with group/channel avatar, title, verified badge
 * - Member count and description
 * - Admin approval notice when request_needed == true
 * - The authentic Telegram Blue Join Button (id="join_button") styled with btn_blue_selector
 * - Loading state with animated spinner
 * - Instant transition to full chat view after successful join
 */

import React, { useState } from 'react';
import {
  Users,
  Megaphone,
  BadgeCheck,
  ShieldAlert,
  Loader2,
  X,
  Share2,
  CheckCircle2,
  ArrowRight,
  ArrowLeft,
} from 'lucide-react';
import { TLRPC } from '../../core/TLRPC';
import { useTelegram } from '../../context/TelegramContext';

export interface ChatInvitePreviewProps {
  invite: TLRPC.ChatInvite;
  hash: string;
  onClose?: () => void;
  onJoined?: (chatId?: string) => void;
}

export const ChatInvitePreview: React.FC<ChatInvitePreviewProps> = ({
  invite,
  hash,
  onClose,
  onJoined,
}) => {
  const { settings, joinChat, showToast, chats, setActiveChatId } = useTelegram();
  const [isJoining, setIsJoining] = useState(false);
  const [isPendingApproval, setIsPendingApproval] = useState(false);

  const isArabic = settings.language === 'ar';
  const isAlreadyMember =
    invite._ === 'chatInviteAlready' ||
    chats.some(
      (c) =>
        c.inviteHash === hash ||
        (invite.title && c.name.toLowerCase() === invite.title.toLowerCase())
    );

  const isChannel = (invite as any).channel || (invite as any).broadcast;
  const requestNeeded = (invite as any).request_needed;
  const memberCount = (invite as any).participants_count || 14850;
  const description =
    (invite as any).about ||
    (isArabic
      ? 'مجموعة أو قناة رسمية في تيليجرام لمشاركة الأخبار والملفات والتحديثات.'
      : 'Official Telegram group or channel for community updates and sharing.');

  const handleJoin = async () => {
    if (isAlreadyMember) {
      const existing = chats.find(
        (c) =>
          c.inviteHash === hash ||
          (invite.title && c.name.toLowerCase() === invite.title.toLowerCase())
      );
      if (existing) {
        setActiveChatId(existing.id);
        if (onJoined) onJoined(existing.id);
        if (onClose) onClose();
      }
      return;
    }

    setIsJoining(true);
    try {
      const success = await joinChat(invite, hash);
      if (success) {
        if (requestNeeded) {
          setIsPendingApproval(true);
          showToast(
            isArabic
              ? 'تم إرسال طلب الانضمام إلى المشرفين بنجاح'
              : 'Join request sent to administrators',
            '⏳'
          );
        } else {
          showToast(
            isArabic
              ? `انضممت بنجاح إلى "${invite.title}"`
              : `Joined "${invite.title}" successfully`,
            '✨'
          );
          if (onJoined) onJoined();
          if (onClose) onClose();
        }
      } else {
        showToast(
          isArabic ? 'تعذر الانضمام، حاول مرة أخرى' : 'Failed to join, please try again',
          '⚠️'
        );
      }
    } catch {
      showToast(
        isArabic ? 'حدث خطأ أثناء الانضمام' : 'Error during joining',
        '⚠️'
      );
    } finally {
      setIsJoining(false);
    }
  };

  const formattedCount = new Intl.NumberFormat(isArabic ? 'ar-EG' : 'en-US').format(
    memberCount
  );

  return (
    <div
      id="tg-chat-invite-preview"
      className="flex-1 flex flex-col h-full overflow-hidden select-none"
      style={{
        backgroundColor: 'var(--tg-theme-chat-bg)',
      }}
    >
      {/* Header Bar */}
      <div
        className="h-14 px-4 border-b flex items-center justify-between backdrop-blur-md z-10"
        style={{
          backgroundColor: 'var(--tg-theme-surface)',
          borderColor: 'var(--tg-theme-border)',
        }}
      >
        <div className="flex items-center gap-3">
          {onClose && (
            <button
              onClick={onClose}
              className="p-2 rounded-full hover:bg-black/5 dark:hover:bg-white/5 transition-colors"
              title={isArabic ? 'رجوع' : 'Back'}
            >
              {isArabic ? (
                <ArrowRight className="w-5 h-5 text-gray-500" />
              ) : (
                <ArrowLeft className="w-5 h-5 text-gray-500" />
              )}
            </button>
          )}
          <div className="flex flex-col">
            <span
              className="font-bold text-sm truncate max-w-[200px] sm:max-w-xs"
              style={{ color: 'var(--tg-theme-text)' }}
            >
              {invite.title || (isArabic ? 'معاينة الرابط' : 'Link Preview')}
            </span>
            <span className="text-xs text-gray-400">
              {isChannel
                ? isArabic
                  ? 'قناة تيليجرام'
                  : 'Telegram Channel'
                : isArabic
                ? 'مجموعة تيليجرام'
                : 'Telegram Group'}
            </span>
          </div>
        </div>

        {onClose && (
          <button
            onClick={onClose}
            className="p-2 rounded-full hover:bg-black/5 dark:hover:bg-white/5 transition-colors text-gray-400 hover:text-gray-600"
          >
            <X className="w-5 h-5" />
          </button>
        )}
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col items-center justify-center p-6 overflow-y-auto">
        <div
          className="w-full max-w-md rounded-3xl p-6 sm:p-8 border shadow-xl flex flex-col items-center text-center relative overflow-hidden backdrop-blur-md"
          style={{
            backgroundColor: 'var(--tg-theme-surface)',
            borderColor: 'var(--tg-theme-border)',
          }}
        >
          {/* Channel / Group Large Avatar */}
          <div className="relative mb-5">
            <div className="w-24 h-24 sm:w-28 sm:h-28 rounded-full overflow-hidden shadow-lg border-2 border-white/20 flex items-center justify-center bg-gradient-to-tr from-[#2481cc] to-[#3ca0ef] text-white">
              {(invite as any).photo ? (
                <img
                  src={(invite as any).photo}
                  alt={invite.title}
                  className="w-full h-full object-cover"
                  referrerPolicy="no-referrer"
                />
              ) : isChannel ? (
                <Megaphone className="w-12 h-12" />
              ) : (
                <Users className="w-12 h-12" />
              )}
            </div>

            <div className="absolute -bottom-1 -right-1 p-1.5 rounded-full bg-[#2481cc] text-white shadow-md">
              {isChannel ? (
                <Megaphone className="w-4 h-4" />
              ) : (
                <Users className="w-4 h-4" />
              )}
            </div>
          </div>

          {/* Title and Badges */}
          <div className="flex items-center justify-center gap-1.5 mb-1.5">
            <h2
              className="text-xl sm:text-2xl font-bold tracking-tight"
              style={{ color: 'var(--tg-theme-text)' }}
            >
              {invite.title || (isArabic ? 'محادثة تيليجرام' : 'Telegram Chat')}
            </h2>
            <BadgeCheck className="w-5 h-5 text-[#2481cc] fill-[#2481cc]/20 shrink-0" />
          </div>

          {/* Type and Subscriber Count */}
          <div className="flex items-center gap-2 text-xs sm:text-sm text-gray-400 font-medium mb-4">
            <span>
              {isChannel
                ? isArabic
                  ? 'قناة عامة'
                  : 'Public Channel'
                : isArabic
                ? 'مجموعة عامة'
                : 'Public Group'}
            </span>
            <span>•</span>
            <span>
              {formattedCount}{' '}
              {isChannel
                ? isArabic
                  ? 'مشترك'
                  : 'subscribers'
                : isArabic
                ? 'عضو'
                : 'members'}
            </span>
          </div>

          {/* About / Description Box */}
          <div
            className="w-full text-xs sm:text-sm text-gray-500 dark:text-gray-300 leading-relaxed p-4 rounded-2xl border mb-6 text-right rtl:text-right ltr:text-left break-words"
            style={{
              backgroundColor: 'var(--tg-theme-chat-bg)',
              borderColor: 'var(--tg-theme-border)',
            }}
          >
            {description}
          </div>

          {/* Admin Approval Notice if request_needed */}
          {requestNeeded && !isPendingApproval && (
            <div className="w-full flex items-center gap-2.5 p-3 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-500 text-xs text-right rtl:text-right ltr:text-left mb-5">
              <ShieldAlert className="w-5 h-5 shrink-0" />
              <span>
                {isArabic
                  ? 'هذه المجموعة تتطلب موافقة المشرفين للانضمام. سيتم مراجعة طلبك فور إرساله.'
                  : 'This chat requires administrator approval before you can join.'}
              </span>
            </div>
          )}

          {isPendingApproval && (
            <div className="w-full flex items-center gap-2.5 p-3 rounded-xl bg-blue-500/10 border border-blue-500/20 text-[#2481cc] text-xs text-right rtl:text-right ltr:text-left mb-5">
              <CheckCircle2 className="w-5 h-5 shrink-0" />
              <span>
                {isArabic
                  ? 'تم إرسال طلب الانضمام بنجاح! سيصلك إشعار فور موافقة المشرفين.'
                  : 'Request sent successfully! You will be notified when an admin approves.'}
              </span>
            </div>
          )}

          {/* The Official Blue Join Button (id="join_button") */}
          <div className="w-full">
            <button
              id="join_button"
              onClick={handleJoin}
              disabled={isJoining || isPendingApproval}
              className={`w-full py-3.5 px-6 rounded-2xl font-bold text-white shadow-lg transition-all duration-200 flex items-center justify-center gap-2 ${
                isPendingApproval
                  ? 'bg-gray-400 cursor-not-allowed opacity-80'
                  : 'bg-[#2481cc] hover:bg-[#1f73b7] active:scale-[0.99] hover:shadow-blue-500/25'
              }`}
              style={{
                backgroundColor: isPendingApproval ? undefined : '#2481cc',
              }}
            >
              {isJoining ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>{isArabic ? 'جارِ التحقق والانضمام...' : 'Joining...'}</span>
                </>
              ) : isPendingApproval ? (
                <span>{isArabic ? 'الطلب قيد المراجعة' : 'Request Pending Approval'}</span>
              ) : isAlreadyMember ? (
                <span>{isArabic ? 'فتح المحادثة' : 'Open Chat'}</span>
              ) : requestNeeded ? (
                <span>
                  {isChannel
                    ? isArabic
                      ? 'طلب الانضمام إلى القناة'
                      : 'Request to Join Channel'
                    : isArabic
                    ? 'طلب الانضمام إلى المجموعة'
                    : 'Request to Join Group'}
                </span>
              ) : (
                <span>
                  {isChannel
                    ? isArabic
                      ? 'الانضمام إلى القناة'
                      : 'Join Channel'
                    : isArabic
                    ? 'الانضمام إلى المجموعة'
                    : 'Join Group'}
                </span>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
