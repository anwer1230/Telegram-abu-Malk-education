/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React from 'react';
import { TelegramProvider, useTelegram } from './context/TelegramContext';
import { GlobalErrorBoundary } from './components/Common/GlobalErrorBoundary';
import { Sidebar } from './components/Sidebar/Sidebar';
import { ChatView } from './components/Chat/ChatView';
import { ChatInfoPanel } from './components/RightPanel/ChatInfoPanel';
import { NavigationDrawer } from './components/Sidebar/NavigationDrawer';
import { ApiConfigModal } from './components/Modals/ApiConfigModal';
import { SettingsModal } from './components/Modals/SettingsModal';
import { CallModal } from './components/Modals/CallModal';
import { MediaViewerModal } from './components/Modals/MediaViewerModal';
import { NewChatModal } from './components/Modals/NewChatModal';
import { AddAccountModal } from './components/Modals/AddAccountModal';
import { JoinInviteModal } from './components/Modals/JoinInviteModal';
import { ApkInstallerModal } from './components/Modals/ApkInstallerModal';
import { MiniAppsModal } from './components/Modals/MiniAppsModal';
import { ThemeEditorModal } from './components/Modals/ThemeEditorModal';
import { ExportChatModal } from './components/Modals/ExportChatModal';
import { ContactsModal } from './components/Modals/ContactsModal';
import { LinkMonitorModal } from './components/Modals/LinkMonitorModal';
import { SendOnlyModal } from './components/Modals/SendOnlyModal';
import { PremiumModal } from './components/Modals/PremiumModal';
import { SecretChatInfoModal } from './components/Modals/SecretChatInfoModal';
import { GroupAdminModal } from './components/Modals/GroupAdminModal';
import { ForumTopicsModal } from './components/Modals/ForumTopicsModal';
import { SenderModal } from './components/Modals/SenderModal';
import { MonitorModal } from './components/Modals/MonitorModal';
import { MyMessagesModal } from './components/Modals/MyMessagesModal';
import { AutoJoinerModal } from './components/Modals/AutoJoinerModal';
import { AutoResponderModal } from './components/Modals/AutoResponderModal';
import { LiveLinkDiscoverModal } from './components/Modals/LiveLinkDiscoverModal';
import { UserProfileModal } from './components/Modals/UserProfileModal';
import { UrlConfirmModal } from './components/Modals/UrlConfirmModal';
import { ForwardModal } from './components/Interactions/ForwardModal';
import { ChatContextMenuView } from './components/Interactions/ChatContextMenu';
import { MessageContextMenuView } from './components/Interactions/MessageContextMenu';
import { ToastContainer } from './components/Interactions/ToastContainer';
import { InAppNotificationBanner } from './components/Notifications/InAppNotificationBanner';
import { TelegramAuthScreen } from './components/Auth/TelegramAuthScreen';
import { useMobileNavigation } from './hooks/useMobileNavigation';

const TelegramAppContent: React.FC = () => {
  const { isAuthenticated, inAppNotifications, dismissNotification, activeModal, setActiveModal } = useTelegram();

  // Activate mobile hardware back button, touch navigation & popstate stack
  useMobileNavigation();

  if (!isAuthenticated) {
    return (
      <div id="tg-auth-wrapper" className="w-screen h-screen min-h-screen bg-[#0e1621] text-white overflow-hidden relative select-none">
        <TelegramAuthScreen />
        <ToastContainer />
      </div>
    );
  }

  return (
    <div
      id="tg-app-root"
      className="fixed inset-0 w-full h-full h-[100dvh] flex overflow-hidden font-sans select-none"
      style={{
        backgroundColor: 'var(--tg-theme-bg)',
      }}
    >
      {/* Left Sidebar (Chats, Folders, Search) */}
      <Sidebar />

      {/* Center Chat Feed / Message View */}
      <ChatView />

      {/* Right Shared Media & Details Info Panel */}
      <ChatInfoPanel />

      {/* Drawer Slide-out Menu */}
      <NavigationDrawer />

      {/* Dialogs & Overlays */}
      <ApiConfigModal />
      <SettingsModal />
      <CallModal />
      <MediaViewerModal />
      <NewChatModal />
      <AddAccountModal />
      <JoinInviteModal />
      <ApkInstallerModal />
      <MiniAppsModal
        isOpen={activeModal === 'mini-apps'}
        onClose={() => setActiveModal('none')}
      />
      <ThemeEditorModal
        isOpen={activeModal === 'theme-editor'}
        onClose={() => setActiveModal('none')}
      />
      <ExportChatModal
        isOpen={activeModal === 'export-chat'}
        onClose={() => setActiveModal('none')}
      />
      <ContactsModal
        isOpen={activeModal === 'contacts'}
        onClose={() => setActiveModal('none')}
      />
      <LinkMonitorModal
        isOpen={activeModal === 'link-monitor'}
        onClose={() => setActiveModal('none')}
      />
      <SendOnlyModal />
      <PremiumModal />
      <SecretChatInfoModal />
      <GroupAdminModal />
      <ForumTopicsModal />
      
      {/* 7 Core Telegram Functions (Activities) */}
      <SenderModal />
      <MonitorModal />
      <MyMessagesModal />
      <AutoJoinerModal />
      <AutoResponderModal />
      <LiveLinkDiscoverModal />
      <UserProfileModal />
      <UrlConfirmModal />

      <ForwardModal />

      {/* Dynamic Context Menus */}
      <ChatContextMenuView />
      <MessageContextMenuView />

      {/* In-App Floating Heads-up Notification Banner */}
      <InAppNotificationBanner
        notifications={inAppNotifications}
        onDismiss={dismissNotification}
      />

      {/* Floating Toast Notifications */}
      <ToastContainer />
    </div>
  );
};

export default function App() {
  return (
    <GlobalErrorBoundary>
      <TelegramProvider>
        <TelegramAppContent />
      </TelegramProvider>
    </GlobalErrorBoundary>
  );
}
