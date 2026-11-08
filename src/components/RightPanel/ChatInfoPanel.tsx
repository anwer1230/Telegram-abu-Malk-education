import React, { useState } from 'react';
import { X, Bell, Image, FileText, ArrowLeft, Play } from 'lucide-react';
import { useTelegram } from '../../context/TelegramContext';
import { ViewerMediaItem } from '../../types';

export const ChatInfoPanel: React.FC = () => {
  const {
    isRightPanelOpen,
    setIsRightPanelOpen,
    activeChat,
    settings,
    messages,
    currentUser,
    setViewerMedia,
  } = useTelegram();
  const isArabic = settings.language === 'ar';
  const [activeTab, setActiveTab] = useState<'info' | 'media'>('info');

  const sharedMediaList: ViewerMediaItem[] = React.useMemo(() => {
    if (!activeChat) return [];
    const chatMsgs = messages[activeChat.id] || [];
    const list: ViewerMediaItem[] = [];
    for (const m of chatMsgs) {
      if (
        m.media &&
        (m.media.type === 'photo' || m.media.type === 'video' || m.media.type === 'video_note') &&
        m.media.url
      ) {
        list.push({
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
          chatId: activeChat.id,
        });
      }
    }
    return list;
  }, [messages, activeChat, currentUser]);

  if (!isRightPanelOpen || !activeChat) return null;

  return (
    <>
      {/* Mobile Backdrop */}
      <div
        className="fixed inset-0 bg-black/60 z-30 lg:hidden"
        onClick={() => setIsRightPanelOpen(false)}
      />

      <aside
        id="tg-chat-info-panel"
        className="fixed inset-y-0 right-0 rtl:right-auto rtl:left-0 z-40 w-full sm:w-80 lg:static lg:w-80 lg:z-auto h-full border-l rtl:border-l-0 rtl:border-r border-[#242f3d] bg-[#17212b] text-white flex flex-col shrink-0 animate-in slide-in-from-right duration-200 shadow-2xl lg:shadow-none"
      >
        {/* Header */}
        <div className="p-3 flex items-center justify-between border-b border-[#242f3d]">
          <div className="flex items-center gap-2">
            {activeTab === 'media' && (
              <button
                onClick={() => setActiveTab('info')}
                className="p-1 rounded-full hover:bg-white/10 text-gray-400 hover:text-white"
                title={isArabic ? 'رجوع' : 'Back'}
              >
                <ArrowLeft className="w-5 h-5 rtl:rotate-180" />
              </button>
            )}
            <h3 className="font-medium text-sm">
              {activeTab === 'media'
                ? isArabic
                  ? 'الوسائط المشتركة'
                  : 'Shared Media'
                : isArabic
                ? 'معلومات المحادثة'
                : 'Chat Info'}
            </h3>
          </div>
          <button
            onClick={() => setIsRightPanelOpen(false)}
            className="p-1 rounded-full hover:bg-white/10 text-gray-400 hover:text-white"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {activeTab === 'info' ? (
          <>
            {/* Chat Profile */}
            <div className="p-6 flex flex-col items-center border-b border-[#242f3d] text-center">
              <div className="w-20 h-20 rounded-full bg-[#2481cc] flex items-center justify-center text-2xl font-bold mb-3 overflow-hidden shadow-lg">
                {activeChat.avatar ? (
                  <img src={activeChat.avatar} alt={activeChat.title} className="w-full h-full object-cover" />
                ) : (
                  activeChat.title.charAt(0).toUpperCase()
                )}
              </div>
              <h2 className="font-semibold text-lg">{activeChat.title}</h2>
              <p className="text-xs text-gray-400 mt-0.5">
                {activeChat.isOnline
                  ? isArabic ? 'متصل الآن' : 'online'
                  : activeChat.type === 'channel'
                  ? `${activeChat.memberCount || 0} ${isArabic ? 'مشترك' : 'subscribers'}`
                  : isArabic ? 'آخر ظهور مؤخراً' : 'last seen recently'}
              </p>
            </div>

            {/* Shared Media Tabs & Info */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {activeChat.description && (
                <div>
                  <span className="text-xs text-gray-400 block mb-1">{isArabic ? 'الوصف' : 'Description'}</span>
                  <p className="text-sm text-gray-200">{activeChat.description}</p>
                </div>
              )}

              {activeChat.username && (
                <div>
                  <span className="text-xs text-gray-400 block mb-1">{isArabic ? 'اسم المستخدم' : 'Username'}</span>
                  <p className="text-sm text-[#2481cc]">@{activeChat.username}</p>
                </div>
              )}

              <div className="border-t border-[#242f3d] pt-3 space-y-2">
                <div className="flex items-center gap-3 text-sm text-gray-300 py-2 hover:bg-white/5 rounded-lg px-2 cursor-pointer">
                  <Bell className="w-4 h-4 text-gray-400" />
                  <span>{isArabic ? 'الإشعارات' : 'Notifications'}</span>
                </div>
                <div
                  onClick={() => setActiveTab('media')}
                  className="flex items-center justify-between text-sm text-gray-300 py-2 hover:bg-white/5 rounded-lg px-2 cursor-pointer transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <Image className="w-4 h-4 text-sky-400" />
                    <span>{isArabic ? 'الصور ومقاطع الفيديو' : 'Shared Photos & Videos'}</span>
                  </div>
                  {sharedMediaList.length > 0 && (
                    <span className="text-xs text-gray-400 font-mono">
                      {sharedMediaList.length}
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-3 text-sm text-gray-300 py-2 hover:bg-white/5 rounded-lg px-2 cursor-pointer">
                  <FileText className="w-4 h-4 text-amber-400" />
                  <span>{isArabic ? 'الملفات والمستندات' : 'Files & Documents'}</span>
                </div>
              </div>
            </div>
          </>
        ) : (
          /* Shared Media Grid View */
          <div className="flex-1 overflow-y-auto p-2">
            {sharedMediaList.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-center p-6 text-gray-400">
                <Image className="w-12 h-12 stroke-[1.2] mb-2 opacity-40 text-sky-400" />
                <p className="text-sm">
                  {isArabic ? 'لا توجد صور أو مقاطع فيديو مشتركة بعد' : 'No shared media yet'}
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-3 gap-1.5">
                {sharedMediaList.map((item, idx) => {
                  const isVid =
                    item.type === 'video' ||
                    item.type === 'video_note' ||
                    item.url.toLowerCase().endsWith('.mp4') ||
                    item.url.toLowerCase().endsWith('.webm');

                  return (
                    <div
                      key={`${item.url}_${idx}`}
                      onClick={() => setViewerMedia(item, sharedMediaList)}
                      className="relative aspect-square rounded-lg overflow-hidden bg-black/40 cursor-pointer group hover:opacity-90 transition-opacity"
                    >
                      {isVid ? (
                        <>
                          <video
                            src={item.url}
                            preload="metadata"
                            muted
                            playsInline
                            className="w-full h-full object-cover"
                          />
                          <div className="absolute inset-0 bg-black/30 flex items-center justify-center group-hover:bg-black/10 transition-colors">
                            <div className="w-6 h-6 rounded-full bg-black/60 backdrop-blur-md flex items-center justify-center text-white">
                              <Play className="w-3 h-3 fill-white ml-0.5" />
                            </div>
                          </div>
                          {item.duration && (
                            <div className="absolute bottom-1 left-1 rtl:left-auto rtl:right-1 bg-black/70 px-1.5 py-0.5 rounded text-[9px] font-mono text-white">
                              {Math.floor(item.duration / 60)}:
                              {(item.duration % 60).toString().padStart(2, '0')}
                            </div>
                          )}
                        </>
                      ) : (
                        <img
                          src={item.url}
                          alt=""
                          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200"
                          referrerPolicy="no-referrer"
                        />
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}
      </aside>
    </>
  );
};
