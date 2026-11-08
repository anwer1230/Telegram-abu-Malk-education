/**
 * useMobileNavigation.ts - Mobile hardware back button & routing hook
 */

import { useEffect } from 'react';
import { useTelegram } from '../context/TelegramContext';

export function useMobileNavigation() {
  const { activeModal, setActiveModal, activeChatId, setActiveChatId } = useTelegram();

  useEffect(() => {
    const handlePopState = (e: PopStateEvent) => {
      if (activeModal && activeModal !== 'none') {
        setActiveModal('none');
        return;
      }
      if (activeChatId) {
        setActiveChatId(null);
      }
    };

    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, [activeModal, activeChatId, setActiveModal, setActiveChatId]);
}
