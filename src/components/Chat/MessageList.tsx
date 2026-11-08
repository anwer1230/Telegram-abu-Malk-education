import React, { useEffect, useLayoutEffect, useRef, useState, useCallback } from 'react';
import { ArrowDown, Pin, X, Loader2, Shield, Lock, ChevronUp } from 'lucide-react';
import { useTelegram } from '../../context/TelegramContext';
import { MessageBubble } from './MessageBubble';
import { messagesController } from '../../core/MessagesController';

const PAGE_CHUNK_SIZE = 30;

export const MessageList: React.FC = () => {
  const {
    activeChatId,
    activeChat,
    messages,
    pinMessage,
    settings,
    loadMoreChatMessages,
    isChatLoadingOlder,
    chatHasMoreOlder,
  } = useTelegram();

  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const scrollContainerRef = useRef<HTMLDivElement | null>(null);
  const topSentinelRef = useRef<HTMLDivElement | null>(null);

  // Pagination Windowing state for incremental rendering
  const [visibleCount, setVisibleCount] = useState<number>(PAGE_CHUNK_SIZE);
  const [showScrollBottom, setShowScrollBottom] = useState<boolean>(false);
  const [unreadStreamCount, setUnreadStreamCount] = useState<number>(0);
  const [highlightedMessageId, setHighlightedMessageId] = useState<string | null>(null);

  // Scroll anchor preservation state
  const scrollAnchorRef = useRef<{
    previousScrollHeight: number;
    previousScrollTop: number;
    shouldRestore: boolean;
  }>({
    previousScrollHeight: 0,
    previousScrollTop: 0,
    shouldRestore: false,
  });

  const prevMessagesLengthRef = useRef<number>(0);
  const isUserNearBottomRef = useRef<boolean>(true);

  const currentMessages = (activeChatId && messages[activeChatId]) || [];
  const pinnedMessages = currentMessages.filter((m) => m.isPinned);
  const isArabic = settings.language === 'ar';
  const isLoadingOlder = activeChatId ? Boolean(isChatLoadingOlder[activeChatId]) : false;
  const hasMoreOnServer = activeChatId ? (chatHasMoreOlder[activeChatId] ?? true) : true;

  // Reset pagination slice when switching chats
  useEffect(() => {
    setVisibleCount(PAGE_CHUNK_SIZE);
    setShowScrollBottom(false);
    setUnreadStreamCount(0);
    prevMessagesLengthRef.current = currentMessages.length;
    isUserNearBottomRef.current = true;

    // Scroll to bottom on initial chat load
    const timeout = setTimeout(() => {
      if (scrollContainerRef.current) {
        scrollContainerRef.current.scrollTop = scrollContainerRef.current.scrollHeight;
      }
    }, 50);
    return () => clearTimeout(timeout);
  }, [activeChatId]);

  // Determine slice of messages to display
  const totalMessagesCount = currentMessages.length;
  const startIndex = Math.max(0, totalMessagesCount - visibleCount);
  const visibleMessages = currentMessages.slice(startIndex);
  const hasMoreLocally = startIndex > 0;
  const hasMore = hasMoreLocally || hasMoreOnServer;

  // Load more older messages (both from local memory and from MTProto API stream)
  const handleLoadOlder = useCallback(async () => {
    if (!activeChatId || isLoadingOlder) return;

    // Save current scroll metrics before state change for anchor restoration
    if (scrollContainerRef.current) {
      scrollAnchorRef.current = {
        previousScrollHeight: scrollContainerRef.current.scrollHeight,
        previousScrollTop: scrollContainerRef.current.scrollTop,
        shouldRestore: true,
      };
    }

    if (hasMoreLocally) {
      // Expand local visible window
      setVisibleCount((prev) => prev + PAGE_CHUNK_SIZE);
    } else if (hasMoreOnServer) {
      // Fetch older history from Telegram API
      const result = await loadMoreChatMessages(activeChatId);
      if (result.loadedCount > 0) {
        setVisibleCount((prev) => prev + result.loadedCount);
      }
    }
  }, [activeChatId, isLoadingOlder, hasMoreLocally, hasMoreOnServer, loadMoreChatMessages]);

  // Restore scroll anchor smoothly without jumping
  useLayoutEffect(() => {
    if (scrollAnchorRef.current.shouldRestore && scrollContainerRef.current) {
      const container = scrollContainerRef.current;
      const heightDifference = container.scrollHeight - scrollAnchorRef.current.previousScrollHeight;
      container.scrollTop = scrollAnchorRef.current.previousScrollTop + heightDifference;
      scrollAnchorRef.current.shouldRestore = false;
    }
  }, [visibleMessages.length]);

  // Handle incoming stream updates & outgoing messages
  useEffect(() => {
    const prevCount = prevMessagesLengthRef.current;
    const currentCount = currentMessages.length;
    prevMessagesLengthRef.current = currentCount;

    if (currentCount > prevCount) {
      const addedCount = currentCount - prevCount;
      // Auto-expand visible slice so newest messages are always rendered
      setVisibleCount((prev) => prev + addedCount);

      if (isUserNearBottomRef.current) {
        // User was at the bottom -> auto scroll to bottom smoothly
        setTimeout(() => {
          messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
        }, 60);
      } else {
        // User was looking at history -> notify via floating unread badge
        setUnreadStreamCount((prev) => prev + addedCount);
      }
    }
  }, [currentMessages.length]);

  // Top Sentinel IntersectionObserver for auto-loading older messages on scroll
  useEffect(() => {
    if (!topSentinelRef.current || !hasMore) return;

    const observer = new IntersectionObserver(
      (entries) => {
        const first = entries[0];
        if (first.isIntersecting && !isLoadingOlder) {
          handleLoadOlder();
        }
      },
      {
        root: scrollContainerRef.current,
        threshold: 0.1,
        rootMargin: '120px 0px 0px 0px',
      }
    );

    observer.observe(topSentinelRef.current);
    return () => observer.disconnect();
  }, [handleLoadOlder, hasMore, isLoadingOlder]);

  // Track scroll position to update bottom button & near-bottom state
  const handleScroll = () => {
    if (!scrollContainerRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = scrollContainerRef.current;
    const distanceToBottom = scrollHeight - scrollTop - clientHeight;
    const isNearBottom = distanceToBottom < 100;
    isUserNearBottomRef.current = isNearBottom;

    setShowScrollBottom(!isNearBottom);

    if (isNearBottom && unreadStreamCount > 0) {
      setUnreadStreamCount(0);
    }

    // Secondary fallback for fast mouse wheeling near top
    if (scrollTop < 80 && !isLoadingOlder && hasMore) {
      handleLoadOlder();
    }
  };

  const scrollToBottom = (behavior: ScrollBehavior = 'smooth') => {
    messagesEndRef.current?.scrollIntoView({ behavior });
    setUnreadStreamCount(0);
  };

  // Jump to specific message handler (e.g. from search or reply click)
  useEffect(() => {
    const handleScrollToMessage = (e: any) => {
      const detail = e.detail;
      if (!detail || !detail.messageId) return;

      const targetMsgId = detail.messageId;
      // If target message is outside current visible slice, expand visible window
      const targetIndex = currentMessages.findIndex((m) => m.id === targetMsgId);
      if (targetIndex !== -1 && targetIndex < startIndex) {
        setVisibleCount(totalMessagesCount - targetIndex + 10);
      }

      setHighlightedMessageId(targetMsgId);

      setTimeout(() => {
        const el = document.getElementById(`msg-bubble-container-${targetMsgId}`);
        if (el) {
          el.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      }, 150);

      setTimeout(() => {
        setHighlightedMessageId((prev) => (prev === targetMsgId ? null : prev));
      }, 2500);
    };

    window.addEventListener('tg-scroll-to-message', handleScrollToMessage);
    return () => window.removeEventListener('tg-scroll-to-message', handleScrollToMessage);
  }, [currentMessages, startIndex, totalMessagesCount]);

  // DrKLO MessagesAdapter precise grouping algorithm on the visible slice
  const groupedItems = messagesController.sortAndGroupMessages(visibleMessages);

  return (
    <div id="tg-message-list-root" className="relative flex-1 flex flex-col min-h-0 overflow-hidden">
      {/* Messages Scroll Container */}
      <div
        id="tg-messages-scroll-area"
        ref={scrollContainerRef}
        onScroll={handleScroll}
        className="flex-1 overflow-y-auto px-3 sm:px-6 py-3 space-y-2 tg-wallpaper-pattern overscroll-contain"
        style={{
          backgroundColor: 'var(--tg-theme-chat-bg)',
        }}
      >
        {/* Top Sentinel & Loader for Pagination */}
        <div ref={topSentinelRef} className="h-1 w-full" />

        {/* Top Pagination Status Indicator */}
        {isLoadingOlder && (
          <div className="flex justify-center py-2 select-none animate-in fade-in zoom-in-95">
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold bg-[#17212b]/90 text-sky-300 backdrop-blur-md border border-white/10 shadow-md">
              <Loader2 className="w-3.5 h-3.5 animate-spin text-[#2481cc]" />
              <span>{isArabic ? 'جاري مزامنة الرسائل السابقة...' : 'Loading earlier messages...'}</span>
            </div>
          </div>
        )}

        {/* Manual Load Earlier Button fallback */}
        {!isLoadingOlder && hasMore && (
          <div className="flex justify-center py-1 select-none">
            <button
              onClick={handleLoadOlder}
              className="flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-[#17212b]/80 hover:bg-[#17212b] text-[#708499] hover:text-white backdrop-blur-md border border-white/10 transition-all active:scale-95"
            >
              <ChevronUp className="w-3.5 h-3.5" />
              <span>{isArabic ? 'تحميل المزيد من الرسائل السابقة' : 'Load earlier messages'}</span>
            </button>
          </div>
        )}

        {/* Chat Origin Encrypted Badge when at the very beginning of history */}
        {!hasMore && groupedItems.length > 0 && (
          <div className="flex flex-col items-center justify-center my-4 select-none animate-in fade-in">
            <div className="p-3.5 rounded-2xl max-w-xs text-center backdrop-blur-md bg-[#17212b]/80 border border-white/10 shadow-sm">
              <div className="w-8 h-8 rounded-full bg-[#2481cc]/20 text-[#2481cc] flex items-center justify-center mx-auto mb-1.5">
                <Lock className="w-4 h-4" />
              </div>
              <div className="text-xs font-bold text-gray-200 mb-0.5">
                {isArabic ? 'بداية سجل المحادثة' : 'Beginning of Chat History'}
              </div>
              <div className="text-[10px] text-gray-400">
                {isArabic
                  ? 'تم تشفير جميع الرسائل بنجاح عبر MTProto 2.0 (Layer 184).'
                  : 'All messages are end-to-end encrypted via MTProto 2.0.'}
              </div>
            </div>
          </div>
        )}

        {/* Empty State */}
        {groupedItems.length === 0 ? (
          <div className="h-full flex items-center justify-center text-center p-6 select-none">
            <div
              className="p-6 rounded-3xl max-w-sm backdrop-blur-md border shadow-lg"
              style={{
                backgroundColor: 'var(--tg-theme-surface)',
                borderColor: 'var(--tg-theme-border)',
              }}
            >
              <div className="w-12 h-12 rounded-full bg-[#2481cc]/20 text-[#2481cc] flex items-center justify-center mx-auto mb-3">
                <Shield className="w-6 h-6" />
              </div>
              <div className="font-bold text-base mb-1" style={{ color: 'var(--tg-theme-bubble-in-text)' }}>
                {activeChat?.title}
              </div>
              <p className="text-xs text-gray-400 leading-relaxed">
                {isArabic
                  ? 'لا توجد رسائل سابقة في هذه المحادثة. ابدأ بالتراسل الآن مع مزامنة سحابية فورية!'
                  : 'No messages yet in this chat. Start messaging now with instant cloud synchronization!'}
              </p>
            </div>
          </div>
        ) : (
          groupedItems.map((item) => {
            if (item.type === 'date_divider') {
              return (
                <div key={item.id} className="flex justify-center my-3 select-none sticky top-2 z-10">
                  <span className="px-3 py-0.5 rounded-full text-[12px] font-medium bg-[#182533]/85 text-gray-200 backdrop-blur-xs shadow-xs border border-white/5">
                    {item.dateText}
                  </span>
                </div>
              );
            }

            if (item.type === 'unread_divider') {
              return (
                <div key={item.id} className="flex items-center gap-3 my-3 select-none">
                  <div className="flex-1 h-[1px] bg-[#2481cc]/40" />
                  <span className="px-3 py-0.5 rounded-full text-[11px] font-bold bg-[#2481cc]/20 text-[#2481cc] border border-[#2481cc]/30">
                    {item.dateText}
                  </span>
                  <div className="flex-1 h-[1px] bg-[#2481cc]/40" />
                </div>
              );
            }

            if (item.message) {
              const msg = item.message;
              return (
                <div
                  key={item.id}
                  className={`transition-all duration-500 rounded-2xl ${
                    highlightedMessageId === msg.id
                      ? 'ring-2 ring-amber-400 bg-amber-500/20 p-1 shadow-lg shadow-amber-500/20 animate-pulse'
                      : ''
                  }`}
                >
                  <MessageBubble
                    message={msg}
                    grouping={{
                      isGroupStart: item.isGroupStart,
                      isGroupMiddle: item.isGroupMiddle,
                      isGroupEnd: item.isGroupEnd,
                      isSingle: item.isSingle,
                    }}
                  />
                </div>
              );
            }

            return null;
          })
        )}

        <div ref={messagesEndRef} className="h-1 w-full" />
      </div>

      {/* Floating Scroll to Bottom Button with Unread Incoming Stream Badge */}
      {showScrollBottom && (
        <button
          id="tg-scroll-bottom-button"
          onClick={() => scrollToBottom('smooth')}
          className="absolute bottom-4 right-4 rtl:right-auto rtl:left-4 z-20 h-11 w-11 rounded-full bg-[#17212b] hover:bg-[#202b36] text-[#708499] hover:text-white shadow-xl flex items-center justify-center border border-[#242f3d] active:scale-95 transition-all animate-in fade-in zoom-in-75"
          title={isArabic ? 'الانتقال إلى أحدث الرسائل' : 'Scroll to bottom'}
        >
          <ArrowDown className="w-5 h-5" />
          {unreadStreamCount > 0 && (
            <span className="absolute -top-1.5 -right-1.5 rtl:-right-auto rtl:-left-1.5 px-1.5 py-0.2 rounded-full text-[10px] font-bold bg-[#2481cc] text-white min-w-[18px] text-center shadow-xs">
              {unreadStreamCount}
            </span>
          )}
        </button>
      )}
    </div>
  );
};
