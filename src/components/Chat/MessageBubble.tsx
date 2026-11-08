import React, { useState } from 'react';
import {
  Check,
  CheckCheck,
  Pin,
  Reply,
  Share2,
  Smile,
  FileText,
  Download,
  CheckSquare,
  Square,
  Sparkles,
  ExternalLink,
  Megaphone,
  Lock,
  Clock,
  AlertCircle,
  Play,
  BadgeCheck,
} from 'lucide-react';
import { Message, InlineKeyboardButton, ViewerMediaItem } from '../../types';
import { useTelegram } from '../../context/TelegramContext';
import { resolveTelegramUser } from '../../data/telegramUsers';
import { AudioPlayerWaveform } from './AudioPlayerWaveform';
import { LottieSticker } from './LottieSticker';
import { POPULAR_REACTIONS } from '../../data/mockTelegramData';
import {
  renderInteractiveMessageText,
  ParsedLinkResult,
  isOnlyBigEmojis,
  renderBigAnimatedEmojis,
  extractLinkPreview,
  isWhitelistedTelegramDomain,
  parseTelegramDeepLink,
} from '../../utils/linkParser';
import { useSwipeToReply, useLongPress } from '../../hooks/useTouchGestures';

import { themeController } from '../../core/ThemeController';
import { MessageObject } from '../../core/MessageObject';
import { ChatObject } from '../../core/ChatObject';
import { UserObject } from '../../core/UserObject';

// Authentic Telegram Peer Colors (Red, Orange, Violet, Green, Cyan, Blue, Pink)
const PEER_COLORS = [
  '#e17076',
  '#faa774',
  '#a695e7',
  '#7bc862',
  '#6ec9cb',
  '#65aadd',
  '#ee7aae',
];

function getPeerColor(nameOrId: string = '') {
  let hash = 0;
  for (let i = 0; i < nameOrId.length; i++) {
    hash = (hash * 31 + nameOrId.charCodeAt(i)) % PEER_COLORS.length;
  }
  return PEER_COLORS[Math.abs(hash)] || PEER_COLORS[0];
}

interface MessageBubbleProps {
  message: Message;
  isFirstInGroup?: boolean;
  isLastInGroup?: boolean;
  grouping?: {
    isGroupStart?: boolean;
    isGroupMiddle?: boolean;
    isGroupEnd?: boolean;
    isSingle?: boolean;
  };
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({
  message,
  isFirstInGroup = true,
  isLastInGroup = true,
  grouping,
}) => {
  const {
    currentUser,
    activeChat,
    activeChatId,
    messages,
    setReplyingTo,
    toggleReaction,
    setViewerMedia,
    votePoll,
    setMessageContextMenu,
    selectedMessageIds,
    toggleSelectMessage,
    resolveTelegramLink,
    openUserProfile,
    settings,
    sendMessage,
    showToast,
    isUserBlocked,
    setIsRightPanelOpen,
  } = useTelegram();

  const [showQuickReactions, setShowQuickReactions] = useState(false);
  const [showHeartBurst, setShowHeartBurst] = useState(false);
  const [avatarError, setAvatarError] = useState(false);
  const lastTouchTapRef = React.useRef<number>(0);

  const isOutgoing = message.isOutgoing;
  const isSelected = selectedMessageIds.includes(message.id);
  const isMultiSelectMode = selectedMessageIds.length > 0;
  const isArabic = settings.language === 'ar';

  const isGroupChat =
    (activeChat?.type as string) === 'group' ||
    (activeChat?.type as string) === 'supergroup' ||
    (activeChat?.type as string) === 'forum' ||
    activeChat?.type === 'channel';

  // Resolve authentic Telegram user profile for message sender
  const senderInfo = React.useMemo(() => {
    if (isOutgoing) {
      return {
        id: currentUser.id,
        name: currentUser.name,
        username: currentUser.username,
        avatar: currentUser.avatar,
        bio: currentUser.bio || (isArabic ? 'حسابي الشخصي في تيليجرام' : 'My personal Telegram account'),
        phone: currentUser.phone,
        isVerified: currentUser.isVerified,
        isPremium: currentUser.isPremium,
        isOnline: true,
        lastSeen: isArabic ? 'متصل الآن' : 'online',
        isBot: false,
      };
    }

    // Direct real sender avatar from Telegram
    const effectiveAvatar = message.senderAvatar;

    // Prevent group's title from leaking into the sender's personal name
    const effectiveName =
      isGroupChat && message.senderName && activeChat?.title && message.senderName === activeChat.title
        ? undefined
        : message.senderName;

    return resolveTelegramUser(
      message.senderId,
      effectiveName,
      effectiveAvatar,
      message.senderUsername
    );
  }, [
    isOutgoing,
    currentUser,
    message.senderId,
    message.senderName,
    message.senderAvatar,
    message.senderUsername,
    activeChat?.title,
    isGroupChat,
    isArabic,
  ]);

  // Build authentic Telegram chat media playlist for seamless navigation across all photos/videos
  const chatMediaPlaylist = React.useMemo(() => {
    const chatMsgs = (activeChatId && messages[activeChatId]) ? messages[activeChatId] : [];
    const playlist: ViewerMediaItem[] = [];
    for (const m of chatMsgs) {
      if (
        m.media &&
        (m.media.type === 'photo' || m.media.type === 'video' || m.media.type === 'video_note') &&
        m.media.url
      ) {
        playlist.push({
          url: m.media.url,
          type: m.media.type === 'video_note' ? 'video_note' : (m.media.type === 'video' ? 'video' : 'photo'),
          title: m.text,
          caption: m.text,
          sender: m.senderName || (m.isOutgoing ? currentUser.name : 'User'),
          senderAvatar: m.senderAvatar,
          timestamp: m.timestamp,
          duration: m.media.duration,
          fileName: m.media.fileName,
          fileSize: m.media.fileSize,
          messageId: m.id,
          chatId: activeChatId || undefined,
        });
      }
    }
    return playlist;
  }, [messages, activeChatId, currentUser]);

  const openMediaViewer = (mediaType: 'photo' | 'video' | 'video_note') => {
    if (!message.media?.url) return;
    const currentItem: ViewerMediaItem = {
      url: message.media.url,
      type: mediaType,
      title: message.text,
      caption: message.text,
      sender: message.senderName || (isOutgoing ? currentUser.name : 'User'),
      senderAvatar: message.senderAvatar,
      timestamp: message.timestamp,
      duration: message.media.duration,
      fileName: message.media.fileName,
      fileSize: message.media.fileSize,
      messageId: message.id,
      chatId: activeChatId || undefined,
    };
    setViewerMedia(currentItem, chatMediaPlaylist.length > 0 ? chatMediaPlaylist : [currentItem]);
  };

  const messageObject = React.useMemo(
    () => new MessageObject(message, 0, activeChat || undefined),
    [message, activeChat]
  );

  const isStandaloneSticker =
    message.media?.type === 'sticker' && !message.text && !message.replyTo && !message.forwardedFrom;
  const bigEmojiCheck =
    !message.media && !message.replyTo && !message.forwardedFrom
      ? isOnlyBigEmojis(message.text)
      : { isBig: false, emojis: [] };
  const isStandaloneBigEmoji = bigEmojiCheck.isBig;

  // Telegram Link Preview (either pre-attached or dynamically extracted)
  const linkPreview = message.linkPreview || (message.text ? extractLinkPreview(message.text) : null);
  const [clickedCallbackId, setClickedCallbackId] = useState<string | null>(null);

  const handleLinkClick = (link: ParsedLinkResult) => {
    if (link.type === 'external_text_url') {
      if (link.isHiddenUrl) {
        window.dispatchEvent(
          new CustomEvent('tg-open-url-confirm', {
            detail: { url: link.value, display: link.display },
          })
        );
        return;
      }
      window.open(link.value, '_blank', 'noopener,noreferrer');
      return;
    }

    if (link.type === 'telegram_invite') {
      resolveTelegramLink(link.value);
    } else if (link.type === 'telegram_username' || link.type === 'telegram_scheme') {
      if (link.botStartParam) {
        sendMessage(`/start ${link.botStartParam}`);
      } else {
        resolveTelegramLink(link.value);
      }
    } else if (link.type === 'bot_command') {
      sendMessage(link.value);
    } else if (link.type === 'external_url') {
      window.open(link.value, '_blank', 'noopener,noreferrer');
    } else {
      resolveTelegramLink(link.value);
    }
  };

  const handleInlineButtonClick = async (btn: InlineKeyboardButton) => {
    if (btn.url) {
      const deep = parseTelegramDeepLink(btn.url);
      if (deep.isTelegramLink) {
        resolveTelegramLink(deep.cleanUrl);
        return;
      }
      if (!isWhitelistedTelegramDomain(btn.url)) {
        window.dispatchEvent(
          new CustomEvent('tg-open-url-confirm', {
            detail: { url: btn.url, display: btn.text },
          })
        );
        return;
      }
      window.open(btn.url, '_blank', 'noopener,noreferrer');
      return;
    }

    if (btn.callback_data) {
      setClickedCallbackId(btn.callback_data);
      try {
        const res = await fetch('/api/telegram/bot/callback_query', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            messageId: message.id,
            chatId: message.chatId,
            callbackData: btn.callback_data,
            buttonText: btn.text,
          }),
        });
        const data = await res.json();
        showToast(
          data.alertMessage || data.message || (isArabic ? `تم تنفيذ: ${btn.text}` : `Executed: ${btn.text}`),
          '⚡'
        );
      } catch {
        showToast(isArabic ? `تم استلام: ${btn.text}` : `Received: ${btn.text}`, '⚡');
      } finally {
        setTimeout(() => setClickedCallbackId(null), 500);
      }
    }
  };

  const renderStatus = () => {
    if (!isOutgoing) return null;
    if (message.status === 'read') {
      return (
        <span title={isArabic ? 'مقروءة' : 'Read'} className="inline-flex items-center">
          <CheckCheck className="w-3.5 h-3.5 text-[#4fae4e]" />
        </span>
      );
    }
    if (message.status === 'delivered' || message.status === 'sent') {
      return (
        <span title={isArabic ? 'تم الإرسال والتسليم' : 'Sent'} className="inline-flex items-center">
          <Check className="w-3.5 h-3.5 text-[#7da7cf]" />
        </span>
      );
    }
    if (message.status === 'error') {
      return (
        <span
          title={isArabic ? 'فشل الإرسال، اضغط لإعادة المحاولة' : 'Failed to send, click to retry'}
          className="inline-flex items-center text-red-500 hover:text-red-400 cursor-pointer animate-bounce"
          onClick={(e) => {
            e.stopPropagation();
            sendMessage(message.text);
          }}
        >
          <AlertCircle className="w-3.5 h-3.5" />
        </span>
      );
    }
    // Sending / clock state
    return (
      <span title={isArabic ? 'جاري الإرسال...' : 'Sending...'} className="inline-flex items-center text-sky-400/80">
        <Clock className="w-3 h-3 animate-spin" />
      </span>
    );
  };

  const handleContextMenu = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setMessageContextMenu({
      message,
      x: e.clientX,
      y: e.clientY,
    });
  };

  const triggerHeartReaction = () => {
    toggleReaction(message.id, '❤️');
    setShowHeartBurst(true);
    if (typeof navigator !== 'undefined' && navigator.vibrate) {
      try {
        navigator.vibrate(30);
      } catch {}
    }
    setTimeout(() => setShowHeartBurst(false), 1000);
  };

  const handleDoubleClick = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    triggerHeartReaction();
  };

  const handleTouchTap = (e: React.TouchEvent) => {
    const now = Date.now();
    if (now - lastTouchTapRef.current < 280) {
      triggerHeartReaction();
    }
    lastTouchTapRef.current = now;
  };

  const handleBubbleClick = (e: React.MouseEvent) => {
    if (isMultiSelectMode) {
      e.stopPropagation();
      toggleSelectMessage(message.id);
    }
  };

  const handleSenderClick = (e: React.MouseEvent | React.TouchEvent) => {
    e.stopPropagation();

    openUserProfile({
      ...senderInfo,
      avatar: message.senderAvatar || senderInfo.avatar,
      sourceChatId: activeChat?.id,
      sourceChatTitle: activeChat?.title,
      isBlocked: isUserBlocked(senderInfo.id),
      senderRole: message.senderRole,
      senderRank: message.senderRank,
    });
  };

  const senderDisplayAvatar = React.useMemo(() => {
    return message.senderAvatar || senderInfo.avatar;
  }, [message.senderAvatar, senderInfo.avatar]);

  React.useEffect(() => {
    setAvatarError(false);
  }, [senderDisplayAvatar]);

  const senderDisplayName = React.useMemo(() => {
    if (isGroupChat && message.senderName && activeChat?.title && message.senderName === activeChat.title) {
      return senderInfo.name;
    }
    return message.senderName || senderInfo.name || messageObject.getSenderTitle();
  }, [isGroupChat, message.senderName, activeChat?.title, senderInfo.name, messageObject]);

  const triggerReply = () => {
    setReplyingTo({
      messageId: message.id,
      senderName: message.senderName || (isOutgoing ? currentUser.name : 'User'),
      textSnippet: message.text || (message.media ? `[${message.media.type}]` : ''),
      mediaType: message.media?.type as 'photo' | 'audio' | 'document' | 'video' | undefined,
    });
  };

  const { swipeOffset, touchHandlers } = useSwipeToReply(triggerReply, isArabic);

  const longPressHandlers = useLongPress(
    (e) => {
      const touch = 'touches' in e ? e.touches[0] || (e as any).changedTouches?.[0] : e;
      setMessageContextMenu({
        message,
        x: touch ? touch.clientX : window.innerWidth / 2,
        y: touch ? touch.clientY : window.innerHeight / 2,
      });
    },
    () => {
      if (isMultiSelectMode) {
        toggleSelectMessage(message.id);
      }
    },
    420
  );

  return (
    <div
      id={`msg-bubble-container-${message.id}`}
      onContextMenu={handleContextMenu}
      onDoubleClick={handleDoubleClick}
      onTouchStart={(e) => {
        touchHandlers.onTouchStart(e);
        longPressHandlers.onTouchStart(e);
        handleTouchTap(e);
      }}
      onTouchMove={(e) => {
        touchHandlers.onTouchMove(e);
        longPressHandlers.onTouchMove(e);
      }}
      onTouchEnd={(e) => {
        touchHandlers.onTouchEnd();
        longPressHandlers.onTouchEnd(e);
      }}
      onMouseDown={longPressHandlers.onMouseDown}
      onMouseMove={longPressHandlers.onMouseMove}
      onMouseUp={longPressHandlers.onMouseUp}
      onMouseLeave={longPressHandlers.onMouseLeave}
      style={{
        transform: swipeOffset ? `translateX(${swipeOffset}px)` : undefined,
        transition: swipeOffset ? 'none' : 'transform 0.25s cubic-bezier(0.2, 0.8, 0.2, 1)',
      }}
      className={`group relative flex items-end gap-2 px-3 py-0.5 select-none transition-colors ${
        isOutgoing ? 'justify-end' : 'justify-start'
      } ${isSelected ? 'bg-sky-500/15' : ''}`}
    >
      {/* Heart Burst Animation on Double-Tap */}
      {showHeartBurst && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none z-30 animate-in zoom-in-50 fade-in duration-300">
          <div className="text-4xl drop-shadow-xl animate-bounce">
            ❤️
          </div>
        </div>
      )}
      {/* Swipe to reply circular icon indicator */}
      {Math.abs(swipeOffset) > 10 && (
        <div
          className={`absolute self-center z-10 w-8 h-8 rounded-full bg-[#2481cc] text-white flex items-center justify-center shadow-lg transition-transform ${
            Math.abs(swipeOffset) > 40 ? 'scale-110 ring-2 ring-white/50' : 'scale-90 opacity-75'
          } ${isArabic ? 'right-2' : 'left-2'}`}
        >
          <Reply className="w-4 h-4" />
        </div>
      )}
      {/* Multi-select checkbox indicator */}
      {isMultiSelectMode && (
        <button
          onClick={(e) => {
            e.stopPropagation();
            toggleSelectMessage(message.id);
          }}
          className="self-center p-1 text-[#2481cc]"
        >
          {isSelected ? (
            <CheckSquare className="w-5 h-5 fill-[#2481cc] text-white" />
          ) : (
            <Square className="w-5 h-5 text-gray-400" />
          )}
        </button>
      )}

      {/* Sender Avatar for incoming messages - Official Telegram Standard with click to view profile */}
      {!isOutgoing && (
        <button
          type="button"
          onClick={handleSenderClick}
          title={senderDisplayName || (isArabic ? 'الملف الشخصي' : 'Profile')}
          className="w-8 h-8 rounded-full overflow-hidden shrink-0 self-end mb-1 cursor-pointer hover:scale-110 active:scale-95 transition-transform ring-1 ring-white/10 shadow-sm focus:outline-none"
        >
          {senderDisplayAvatar && !avatarError ? (
            <img
              src={senderDisplayAvatar}
              alt={senderDisplayName}
              className="w-full h-full object-cover"
              loading="lazy"
              referrerPolicy="no-referrer"
              onError={() => setAvatarError(true)}
            />
          ) : (
            <div
              className="w-full h-full text-white font-bold text-xs flex items-center justify-center shadow-inner"
              style={{
                backgroundColor: getPeerColor(senderInfo.id || senderInfo.name || senderDisplayName),
              }}
            >
              {(senderDisplayName || 'U').charAt(0).toUpperCase()}
            </div>
          )}
        </button>
      )}

      {/* Bubble Container */}
      <div className="relative max-w-[85%] sm:max-w-[70%] md:max-w-[65%] flex flex-col">
        {/* Quick Reaction popup on hover */}
        <div
          className={`absolute -top-7 ${
            isOutgoing ? 'right-2' : 'left-2'
          } z-20 hidden group-hover:flex items-center gap-1 px-2 py-1 rounded-full bg-[#182533]/90 backdrop-blur-md border border-white/10 shadow-lg text-sm`}
        >
          {POPULAR_REACTIONS.slice(0, 5).map((emoji) => (
            <button
              key={emoji}
              onClick={(e) => {
                e.stopPropagation();
                toggleReaction(message.id, emoji);
              }}
              className="hover:scale-130 transition-transform active:scale-95 px-0.5"
            >
              {emoji}
            </button>
          ))}
          <button
            onClick={(e) => {
              e.stopPropagation();
              setReplyingTo({
                messageId: message.id,
                senderName: message.senderName || (isOutgoing ? currentUser.name : 'User'),
                textSnippet: message.text || (message.media ? `[${message.media.type}]` : ''),
                mediaType: message.media?.type as 'photo' | 'audio' | 'document' | 'video' | undefined,
              });
            }}
            className="hover:text-sky-400 p-0.5 text-gray-300"
            title="Reply"
          >
            <Reply className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* The Visual Bubble or Standalone Sticker / Big Emoji Presentation */}
        {isStandaloneSticker ? (
          <div className="relative group/sticker my-1 flex flex-col items-center select-none">
            <LottieSticker
              lottieData={message.media?.lottieData}
              stickerId={message.media?.stickerId}
              url={message.media?.url}
              size={155}
              autoplay={true}
              loop={true}
            />
            {/* Native Telegram translucent floating timestamp & status badge */}
            <div
              className={`absolute bottom-1 end-1 bg-black/60 backdrop-blur-md px-2 py-0.5 rounded-full text-[10px] text-white flex items-center gap-1 shadow-md select-none pointer-events-none`}
            >
              {message.isPinned && <Pin className="w-2.5 h-2.5 text-sky-400 -rotate-45" />}
              <span>{message.timestamp}</span>
              {renderStatus()}
            </div>
          </div>
        ) : isStandaloneBigEmoji ? (
          <div className="relative group/bigemoji my-1 flex flex-col items-center select-none">
            {renderBigAnimatedEmojis(bigEmojiCheck.emojis)}
            {/* Floating timestamp badge */}
            <div
              className={`absolute -bottom-1 end-1 bg-black/60 backdrop-blur-md px-2 py-0.5 rounded-full text-[10px] text-white flex items-center gap-1 shadow-md select-none pointer-events-none`}
            >
              {message.isPinned && <Pin className="w-2.5 h-2.5 text-sky-400 -rotate-45" />}
              <span>{message.timestamp}</span>
              {renderStatus()}
            </div>
          </div>
        ) : (
          <div
            className={`relative px-3.5 py-2 text-sm shadow-sm transition-all ${
              isOutgoing
                ? 'tg-bubble-out text-[var(--tg-theme-bubble-out-text)] self-end'
                : 'tg-bubble-in text-[var(--tg-theme-bubble-in-text)] self-start'
            }`}
            style={{
              borderRadius: themeController.getBubbleRadiusStyle(
                isOutgoing,
                grouping || {
                  isGroupStart: isFirstInGroup,
                  isGroupEnd: isLastInGroup,
                  isSingle: isFirstInGroup && isLastInGroup,
                },
                isArabic
              ),
              backgroundColor: isOutgoing
                ? 'var(--tg-theme-bubble-out)'
                : 'var(--tg-theme-bubble-in)',
            }}
          >
            {/* Sender Name / Admin Post Signature for incoming messages - Telegram Peer Colors + Profile */}
            {!isOutgoing && (
              messageObject.isChannelPostVal ? (
                messageObject.isPostAuthorVisible && messageObject.postAuthor ? (
                  <button
                    type="button"
                    onClick={handleSenderClick}
                    className="font-semibold text-[11px] mb-1 flex items-center gap-1.5 text-sky-400/90 hover:underline cursor-pointer select-none text-left rtl:text-right focus:outline-none"
                  >
                    <span>✍️ {messageObject.postAuthor}</span>
                    <span className="text-[9px] px-1 py-0.2 rounded bg-sky-500/15 text-sky-300 border border-sky-500/20 font-mono">
                      {isArabic ? 'مشرف القناة' : 'Admin'}
                    </span>
                  </button>
                ) : null
              ) : (isGroupChat || message.senderName) ? (
                <button
                  type="button"
                  onClick={handleSenderClick}
                  className="font-bold text-xs mb-1 flex items-center gap-1.5 hover:underline cursor-pointer transition-opacity active:opacity-75 text-left rtl:text-right focus:outline-none flex-wrap"
                  style={{
                    color: getPeerColor(senderInfo.id || senderInfo.name || senderDisplayName),
                  }}
                >
                  <span>{senderDisplayName}</span>
                  {senderInfo.isVerified && (
                    <BadgeCheck className="w-3.5 h-3.5 text-[#2481cc] fill-[#2481cc] text-white shrink-0" />
                  )}
                  {senderInfo.isPremium && (
                    <span className="text-[10px] text-amber-400 font-bold shrink-0">★</span>
                  )}
                  {(senderInfo.username || message.senderUsername) && (
                    <span className="text-[10px] font-normal text-gray-400 font-mono">
                      @{((senderInfo.username || message.senderUsername) as string).replace(/^@/, '')}
                    </span>
                  )}
                  {/* Telegram Group Role / Custom Rank Badge */}
                  {(message.senderRole === 'owner' || message.senderRole === 'admin' || message.senderRank) && (
                    <span
                      className={`text-[9px] px-1.5 py-0.2 rounded font-semibold tracking-wider flex items-center gap-0.5 select-none ${
                        message.senderRole === 'owner'
                          ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                          : message.senderRole === 'admin'
                          ? 'bg-sky-500/20 text-sky-300 border border-sky-500/30'
                          : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                      }`}
                    >
                      {message.senderRole === 'owner' ? '👑 ' : message.senderRole === 'admin' ? '🛡️ ' : ''}
                      {message.senderRank || (message.senderRole === 'owner' ? (isArabic ? 'مالك' : 'owner') : isArabic ? 'مشرف' : 'admin')}
                    </span>
                  )}
                </button>
              ) : null
            )}

            {/* Forwarded Header */}
            {message.forwardedFrom && (
              <div
                onClick={(e) => {
                  e.stopPropagation();
                  openUserProfile({
                    id: message.forwardedFrom?.fromChatId || `fwd_${message.forwardedFrom?.fromChatName}`,
                    name: message.forwardedFrom!.fromChatName,
                    username: message.forwardedFrom!.fromChatName.toLowerCase().replace(/[^a-z0-9_]/g, '_'),
                    bio: isArabic ? 'مصدر الرسالة المحولة 🔄' : 'Source of forwarded message 🔄',
                    isOnline: false,
                  });
                }}
                className="mb-1 text-xs text-sky-400/90 flex items-center gap-1 border-l-2 border-sky-400 pl-2 rtl:border-l-0 rtl:border-r-2 rtl:pl-0 rtl:pr-2 cursor-pointer hover:underline"
              >
                <Share2 className="w-3 h-3" />
                <span>
                  {isArabic ? 'محولة من' : 'Forwarded from'}{' '}
                  <strong>{message.forwardedFrom.fromChatName}</strong>
                </span>
              </div>
            )}

            {/* Reply Quote Header */}
            {message.replyTo && (
              <div
                className={`mb-1.5 p-1.5 rounded-lg border-l-2 text-xs flex flex-col ${
                  isOutgoing
                    ? 'bg-black/10 border-white/40'
                    : 'bg-black/15 border-sky-400'
                } rtl:border-l-0 rtl:border-r-2`}
              >
                <span className="font-bold text-[11px] text-sky-400 truncate">
                  {message.replyTo.senderName}
                </span>
                <span className="text-[11px] opacity-80 truncate">
                  {message.replyTo.textSnippet}
                </span>
              </div>
            )}

            {/* MEDIA: Photo */}
            {message.media?.type === 'photo' && message.media.url && (
              <div
                onClick={(e) => {
                  e.stopPropagation();
                  openMediaViewer('photo');
                }}
                className="my-1 rounded-xl overflow-hidden cursor-pointer relative group/media max-h-96 shadow-md"
              >
                <img
                  src={message.media.url}
                  alt="Media content"
                  className="w-full h-auto object-cover rounded-xl hover:scale-[1.01] transition-transform duration-200"
                  referrerPolicy="no-referrer"
                />
                {/* Overlay hover shimmer */}
                <div className="absolute inset-0 bg-black/0 group-hover/media:bg-black/10 transition-colors pointer-events-none" />
              </div>
            )}

            {/* MEDIA: Video */}
            {message.media?.type === 'video' && message.media.url && (
              <div
                onClick={(e) => {
                  e.stopPropagation();
                  openMediaViewer('video');
                }}
                className="my-1 rounded-xl overflow-hidden cursor-pointer relative group/video max-h-96 bg-black/40 shadow-md flex items-center justify-center"
              >
                <video
                  src={message.media.url}
                  preload="metadata"
                  playsInline
                  muted
                  className="w-full max-h-96 object-contain rounded-xl"
                />

                {/* Telegram Frosted Central Play Button */}
                <div className="absolute inset-0 m-auto w-14 h-14 rounded-full bg-black/60 hover:bg-[#2481cc] backdrop-blur-md text-white flex items-center justify-center border border-white/20 shadow-xl transition-all group-hover/video:scale-110 group-active/video:scale-95">
                  <Play className="w-6 h-6 fill-white ml-0.5" />
                </div>

                {/* Duration Badge Bottom-Left (Official Telegram Standard) */}
                <div className="absolute bottom-2 left-2 rtl:left-auto rtl:right-2 bg-black/60 backdrop-blur-md px-2 py-0.5 rounded-full text-[11px] font-mono text-white flex items-center gap-1 shadow-md pointer-events-none">
                  <Play className="w-2.5 h-2.5 fill-white" />
                  <span>
                    {message.media.duration
                      ? `${Math.floor(message.media.duration / 60)}:${(message.media.duration % 60)
                          .toString()
                          .padStart(2, '0')}`
                      : message.media.fileSize || '0:00'}
                  </span>
                </div>
              </div>
            )}

            {/* MEDIA: Video Note (Round Telegram Video Bubble) */}
            {message.media?.type === 'video_note' && message.media.url && (
              <div
                onClick={(e) => {
                  e.stopPropagation();
                  openMediaViewer('video_note');
                }}
                className="my-1.5 w-48 h-48 sm:w-56 sm:h-56 rounded-full overflow-hidden cursor-pointer relative group/roundvideo border-2 border-white/20 shadow-xl bg-black/50 self-center flex items-center justify-center"
              >
                <video
                  src={message.media.url}
                  preload="metadata"
                  playsInline
                  autoPlay
                  loop
                  muted
                  className="w-full h-full object-cover rounded-full"
                />
                <div className="absolute inset-0 bg-black/20 group-hover/roundvideo:bg-black/10 transition-colors flex items-center justify-center">
                  <div className="w-11 h-11 rounded-full bg-black/60 backdrop-blur-md text-white flex items-center justify-center shadow-lg group-hover/roundvideo:scale-110 transition-transform">
                    <Play className="w-5 h-5 fill-white ml-0.5" />
                  </div>
                </div>
                {message.media.duration && (
                  <div className="absolute bottom-3 bg-black/60 backdrop-blur-md px-2 py-0.5 rounded-full text-[10px] font-mono text-white pointer-events-none">
                    {Math.floor(message.media.duration / 60)}:
                    {(message.media.duration % 60).toString().padStart(2, '0')}
                  </div>
                )}
              </div>
            )}

            {/* MEDIA: Sticker */}
            {message.media?.type === 'sticker' && (
              <div className="my-1 flex items-center justify-center">
                <LottieSticker
                  lottieData={message.media.lottieData}
                  stickerId={message.media.stickerId}
                  url={message.media.url}
                  size={140}
                  autoplay={true}
                  loop={true}
                />
              </div>
            )}

            {/* MEDIA: Voice note with real audio waves */}
            {message.media?.type === 'voice' && (
              <AudioPlayerWaveform
                audioUrl={message.media.url}
                duration={message.media.duration || 12}
                waveform={message.media.waveform}
                isOutgoing={isOutgoing}
              />
            )}

            {/* MEDIA: Document / File */}
            {message.media?.type === 'document' && (
              <div className="my-1 p-2 rounded-xl bg-black/10 flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-[#2481cc] text-white flex items-center justify-center shrink-0">
                  <FileText className="w-5 h-5" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="font-semibold text-xs truncate">
                    {message.media.fileName || 'document.pdf'}
                  </div>
                  <div className="text-[10px] opacity-75">
                    {message.media.fileSize || '2.4 MB'}
                  </div>
                </div>
                <button className="p-1.5 rounded-full hover:bg-white/10 text-gray-300">
                  <Download className="w-4 h-4" />
                </button>
              </div>
            )}

            {/* MEDIA: Poll */}
            {message.media?.type === 'poll' && message.media.pollData && (
              <div className="my-1.5 space-y-2 min-w-[220px]">
                <div className="font-bold text-xs">
                  {message.media.pollData.question}
                </div>
                <div className="space-y-1.5">
                  {message.media.pollData.options.map((opt) => {
                    const hasVoted = opt.voters.includes(currentUser.id);
                    const total = message.media!.pollData!.totalVotes || 1;
                    const percent = Math.round((opt.votes / total) * 100) || 0;
                    return (
                      <button
                        key={opt.id}
                        onClick={(e) => {
                          e.stopPropagation();
                          votePoll(message.id, opt.id);
                        }}
                        className={`w-full p-2 rounded-xl border text-left rtl:text-right text-xs transition-all relative overflow-hidden flex items-center justify-between ${
                          hasVoted
                            ? 'border-sky-400 bg-sky-500/20 font-bold'
                            : 'border-white/10 hover:bg-white/5'
                        }`}
                      >
                        <div
                          className="absolute inset-0 bg-sky-500/15 pointer-events-none transition-all"
                          style={{ width: `${percent}%` }}
                        />
                        <span className="relative z-10">{opt.text}</span>
                        <span className="relative z-10 font-mono text-[10px] opacity-80">
                          {percent}% ({opt.votes})
                        </span>
                      </button>
                    );
                  })}
                </div>
                <div className="text-[10px] opacity-75 text-right rtl:text-left">
                  {message.media.pollData.totalVotes}{' '}
                  {isArabic ? 'صوت' : 'votes'}
                </div>
              </div>
            )}

            {/* Message Text with interactive links, mentions, and custom animated emojis */}
            {message.text && (
              <div className="whitespace-pre-wrap break-words leading-relaxed">
                {renderInteractiveMessageText(message.text, handleLinkClick, message.entities)}
              </div>
            )}

            {/* Telegram Rich Link Preview Card */}
            {linkPreview && (
              <div
                onClick={(e) => {
                  e.stopPropagation();
                  handleLinkClick({
                    type:
                      linkPreview.type === 'telegram_invite'
                        ? 'telegram_invite'
                        : linkPreview.type === 'telegram_channel'
                        ? 'telegram_username'
                        : 'external_url',
                    value: linkPreview.channelUsername || linkPreview.url,
                    display: linkPreview.displayUrl,
                  });
                }}
                className="mt-2 p-2.5 rounded-xl border border-sky-400/30 bg-sky-500/10 hover:bg-sky-500/15 transition-colors cursor-pointer border-l-2 rtl:border-l-0 rtl:border-r-2 border-l-sky-400 rtl:border-r-sky-400 space-y-1 select-none"
              >
                <div className="flex items-center justify-between text-[11px] font-bold text-sky-400">
                  <div className="flex items-center gap-1 truncate">
                    {linkPreview.type === 'telegram_channel' && (
                      <Megaphone className="w-3 h-3 text-sky-400 shrink-0" />
                    )}
                    <span>{linkPreview.siteName || 'Link'}</span>
                  </div>
                  <ExternalLink className="w-3 h-3 text-sky-400/70 shrink-0 ml-1 rtl:ml-0 rtl:mr-1" />
                </div>
                <div className="text-xs font-bold text-white line-clamp-1 leading-snug">
                  {linkPreview.title}
                </div>
                {linkPreview.description && (
                  <div className="text-[11px] text-gray-300 line-clamp-2 leading-relaxed">
                    {linkPreview.description}
                  </div>
                )}
                {linkPreview.image && (
                  <div className="mt-1.5 rounded-lg overflow-hidden max-h-36 w-full">
                    <img
                      src={linkPreview.image}
                      alt={linkPreview.title}
                      className="w-full h-full object-cover"
                      referrerPolicy="no-referrer"
                    />
                  </div>
                )}
              </div>
            )}

            {/* Metadata footer: Secret Badge + (edited) + Pinned + Time + Read status */}
            <div
              className={`flex items-center gap-1 text-[11px] mt-1 select-none justify-end ${
                isOutgoing ? 'text-[#7da7cf]' : 'text-[#708499]'
              }`}
            >
              {message.isSecret && (
                <span className="inline-flex items-center gap-0.5 text-emerald-400 text-[9px] font-bold">
                  <Lock className="w-2.5 h-2.5" />
                  {message.ttlSeconds ? (
                    <span className="flex items-center gap-0.5">
                      <Clock className="w-2.5 h-2.5" />
                      <span>{message.ttlSeconds}s</span>
                    </span>
                  ) : null}
                </span>
              )}
              {message.isPinned && (
                <Pin className="w-3 h-3 text-[#7da7cf] -rotate-45" />
              )}
              {message.isEdited && (
                <span className="text-[9px] italic opacity-80">
                  {isArabic ? 'معدلة' : 'edited'}
                </span>
              )}
              <span className="leading-none">{message.timestamp}</span>
              {renderStatus()}
            </div>
          </div>
        )}

        {/* Telegram Inline Keyboard Markup */}
        {message.replyMarkup &&
          'inline_keyboard' in message.replyMarkup &&
          Array.isArray(message.replyMarkup.inline_keyboard) &&
          message.replyMarkup.inline_keyboard.length > 0 && (
            <div className="mt-1 flex flex-col gap-1 w-full select-none max-w-sm">
              {message.replyMarkup.inline_keyboard.map((row, rowIdx) => (
                <div key={rowIdx} className="flex items-center gap-1 w-full">
                  {row.map((btn, btnIdx) => {
                    const isLoading = clickedCallbackId === btn.callback_data;
                    return (
                      <button
                        key={btnIdx}
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleInlineButtonClick(btn);
                        }}
                        disabled={isLoading}
                        className={`flex-1 min-w-0 py-2 px-3 rounded-xl text-xs font-semibold flex items-center justify-center gap-1.5 transition-all active:scale-98 border shadow-xs backdrop-blur-xs ${
                          btn.style === 'danger'
                            ? 'bg-rose-600/85 hover:bg-rose-600 text-white border-rose-500/40'
                            : btn.style === 'success'
                            ? 'bg-emerald-600/85 hover:bg-emerald-600 text-white border-emerald-500/40'
                            : btn.style === 'primary'
                            ? 'bg-[#2481cc] hover:bg-[#1c6fad] text-white border-sky-400/40'
                            : 'bg-black/40 hover:bg-black/55 text-white border-white/10'
                        }`}
                      >
                        {isLoading ? (
                          <Clock className="w-3.5 h-3.5 animate-spin text-sky-300" />
                        ) : (
                          <>
                            {btn.icon_custom_emoji_id && <span className="text-sm">⭐</span>}
                            <span className="truncate">{btn.text}</span>
                            {btn.url && <ExternalLink className="w-3 h-3 opacity-70 shrink-0" />}
                          </>
                        )}
                      </button>
                    );
                  })}
                </div>
              ))}
            </div>
          )}

        {/* Reaction Badges underneath message */}
        {message.reactions && message.reactions.length > 0 && (
          <div className={`flex flex-wrap gap-1 mt-1 ${isOutgoing ? 'justify-end' : 'justify-start'}`}>
            {message.reactions.map((reaction) => {
              const hasUserReacted = reaction.users.includes(currentUser.id);
              return (
                <button
                  key={reaction.emoji}
                  onClick={(e) => {
                    e.stopPropagation();
                    toggleReaction(message.id, reaction.emoji);
                  }}
                  className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold border transition-all ${
                    hasUserReacted
                      ? 'bg-sky-500/20 border-sky-400 text-sky-300 scale-105'
                      : 'bg-black/20 border-white/10 text-gray-300 hover:bg-white/10'
                  }`}
                >
                  <span>{reaction.emoji}</span>
                  <span className="text-[10px] font-mono">{reaction.count}</span>
                </button>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
