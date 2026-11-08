/**
 * useTouchGestures.ts - Swipe to reply & long press handlers
 */

import { useState, useRef } from 'react';

export function useSwipeToReply(onTrigger: () => void, isArabic: boolean = false) {
  const [swipeOffset, setSwipeOffset] = useState(0);
  const startX = useRef(0);

  const touchHandlers = {
    onTouchStart: (e: React.TouchEvent) => {
      startX.current = e.touches[0].clientX;
    },
    onTouchMove: (e: React.TouchEvent) => {
      const diff = e.touches[0].clientX - startX.current;
      const validDiff = isArabic ? Math.max(0, diff) : Math.min(0, diff);
      if (Math.abs(validDiff) < 80) {
        setSwipeOffset(validDiff);
      }
    },
    onTouchEnd: () => {
      if (Math.abs(swipeOffset) > 40) {
        onTrigger();
      }
      setSwipeOffset(0);
    },
  };

  return { swipeOffset, touchHandlers };
}

export function useLongPress(
  onLongPress: (e: any) => void,
  onClick?: (e: any) => void,
  ms: number = 420
) {
  const timer = useRef<any>(null);
  const isLong = useRef(false);

  const start = (e: any) => {
    isLong.current = false;
    timer.current = setTimeout(() => {
      isLong.current = true;
      onLongPress(e);
    }, ms);
  };

  const cancel = (e: any, wasClick: boolean = false) => {
    if (timer.current) {
      clearTimeout(timer.current);
      timer.current = null;
    }
    if (wasClick && !isLong.current && onClick) {
      onClick(e);
    }
  };

  return {
    onTouchStart: (e: React.TouchEvent) => start(e),
    onTouchMove: (e: React.TouchEvent) => cancel(e),
    onTouchEnd: (e: React.TouchEvent) => cancel(e, true),
    onMouseDown: (e: React.MouseEvent) => start(e),
    onMouseMove: (e: React.MouseEvent) => cancel(e),
    onMouseUp: (e: React.MouseEvent) => cancel(e, true),
    onMouseLeave: (e: React.MouseEvent) => cancel(e),
  };
}
