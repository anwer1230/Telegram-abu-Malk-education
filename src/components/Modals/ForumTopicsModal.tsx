import React, { useState, useEffect } from 'react';
import {
  MessageSquare,
  Plus,
  Pin,
  Trash2,
  X,
  Sparkles,
  Hash,
  Layers,
  ChevronRight,
} from 'lucide-react';
import { useTelegram } from '../../context/TelegramContext';
import { topicsController, ForumTopic } from '../../core/messenger/TopicsController';

export const ForumTopicsModal: React.FC = () => {
  const { activeModal, setActiveModal, activeChat, showToast, settings } = useTelegram();
  const [topics, setTopics] = useState<ForumTopic[]>([]);
  const [newTopicTitle, setNewTopicTitle] = useState('');
  const [isCreating, setIsCreating] = useState(false);
  const isArabic = settings.language === 'ar';

  useEffect(() => {
    if (activeChat && activeModal === ('forum-topics' as any)) {
      topicsController.loadTopics(activeChat.id);
      setTopics(topicsController.getTopics(activeChat.id));
    }
  }, [activeChat, activeModal]);

  if (activeModal !== ('forum-topics' as any) || !activeChat) return null;

  const handleCreateTopic = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTopicTitle.trim()) return;

    const created = topicsController.createTopic(activeChat.id, newTopicTitle.trim());
    setTopics(topicsController.getTopics(activeChat.id));
    setNewTopicTitle('');
    setIsCreating(false);
    showToast(
      isArabic
        ? `تم إنشاء الموضوع "${created.title}" بنجاح 📌`
        : `Topic "${created.title}" created successfully 📌`,
      '✨'
    );
  };

  const handleDeleteTopic = (topicId: number, title: string) => {
    topicsController.deleteTopic(activeChat.id, topicId);
    setTopics(topicsController.getTopics(activeChat.id));
    showToast(
      isArabic ? `تم حذف الموضوع "${title}"` : `Deleted topic "${title}"`,
      '🗑️'
    );
  };

  const handleTogglePin = (topicId: number) => {
    topicsController.togglePinTopic(activeChat.id, topicId);
    setTopics(topicsController.getTopics(activeChat.id));
  };

  return (
    <div
      id="modal-forum-topics"
      className="fixed inset-0 z-[9999] flex items-center justify-center p-3 sm:p-4 bg-black/80 backdrop-blur-md select-none"
      dir={isArabic ? 'rtl' : 'ltr'}
    >
      <div
        className="w-full max-w-lg text-[#e8eaf6] rounded-3xl shadow-2xl overflow-hidden border border-sky-500/30 my-auto animate-in zoom-in-95 duration-200"
        style={{
          background: 'linear-gradient(145deg, #111a2e, #17213b, #0c1220)',
        }}
      >
        {/* Header */}
        <div className="p-5 border-b border-white/10 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-sky-500/20 text-sky-400 flex items-center justify-center border border-sky-400/30">
              <Layers className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-sm text-white">
                {isArabic ? 'مواضيع المنتدى (Forum Topics)' : 'Forum Topics'}
              </h3>
              <p className="text-[11px] text-sky-300/80">{activeChat.title}</p>
            </div>
          </div>
          <button
            onClick={() => setActiveModal('none')}
            className="p-1.5 rounded-lg text-gray-400 hover:text-white hover:bg-white/10"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content */}
        <div className="p-4 space-y-4 max-h-[60vh] overflow-y-auto">
          {/* Create Button / Input Form */}
          {!isCreating ? (
            <button
              onClick={() => setIsCreating(true)}
              className="w-full py-3 px-4 rounded-2xl bg-sky-600/25 hover:bg-sky-600/35 border border-sky-500/30 text-sky-300 flex items-center justify-center gap-2 font-bold text-xs transition-all shadow"
            >
              <Plus className="w-4 h-4" />
              <span>{isArabic ? 'إنشاء موضوع جديد' : 'Create New Topic'}</span>
            </button>
          ) : (
            <form onSubmit={handleCreateTopic} className="p-3.5 rounded-2xl bg-black/40 border border-sky-500/40 space-y-3">
              <div className="flex items-center gap-2">
                <Hash className="w-4 h-4 text-sky-400" />
                <span className="font-bold text-xs text-white">
                  {isArabic ? 'عنوان الموضوع الجديد' : 'New Topic Title'}
                </span>
              </div>
              <input
                type="text"
                value={newTopicTitle}
                onChange={(e) => setNewTopicTitle(e.target.value)}
                placeholder={isArabic ? 'مثال: أسئلة واستفسارات برمجية...' : 'e.g. Developer Discussions...'}
                autoFocus
                className="w-full px-3.5 py-2.5 rounded-xl bg-black/50 border border-white/15 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-sky-400"
              />
              <div className="flex items-center justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setIsCreating(false)}
                  className="px-3 py-1.5 rounded-xl text-xs text-gray-400 hover:text-white"
                >
                  {isArabic ? 'إلغاء' : 'Cancel'}
                </button>
                <button
                  type="submit"
                  disabled={!newTopicTitle.trim()}
                  className="px-4 py-1.5 rounded-xl bg-sky-600 hover:bg-sky-500 disabled:opacity-50 text-white text-xs font-bold transition-all shadow"
                >
                  {isArabic ? 'إنشاء' : 'Create'}
                </button>
              </div>
            </form>
          )}

          {/* Topics List */}
          <div className="space-y-2">
            {topics.map((topic) => (
              <div
                key={topic.id}
                className="flex items-center justify-between p-3.5 rounded-2xl bg-black/30 border border-white/5 hover:border-sky-400/30 transition-all group"
              >
                <div className="flex items-center gap-3">
                  <div
                    className="w-9 h-9 rounded-xl flex items-center justify-center font-bold text-xs text-white shadow"
                    style={{
                      backgroundColor: `#${(topic.iconColor || 0x65aadd).toString(16).padStart(6, '0')}`,
                    }}
                  >
                    <MessageSquare className="w-4 h-4" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-xs text-white">{topic.title}</span>
                      {topic.pinned && (
                        <span className="p-0.5 rounded text-sky-400 bg-sky-500/10">
                          <Pin className="w-3 h-3" />
                        </span>
                      )}
                    </div>
                    <span className="text-[10px] text-gray-400">
                      ID: #{topic.id} • {isArabic ? 'نشط' : 'Active'}
                    </span>
                  </div>
                </div>

                <div className="flex items-center gap-1.5">
                  <button
                    onClick={() => handleTogglePin(topic.id)}
                    className={`p-1.5 rounded-xl transition-colors ${
                      topic.pinned
                        ? 'text-sky-400 bg-sky-500/20'
                        : 'text-gray-400 hover:text-white hover:bg-white/10'
                    }`}
                    title={isArabic ? 'تثبيت الموضوع' : 'Pin Topic'}
                  >
                    <Pin className="w-3.5 h-3.5" />
                  </button>

                  <button
                    onClick={() => handleDeleteTopic(topic.id, topic.title)}
                    className="p-1.5 rounded-xl text-gray-400 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
                    title={isArabic ? 'حذف الموضوع' : 'Delete Topic'}
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 bg-black/40 border-t border-white/10 flex justify-end">
          <button
            onClick={() => setActiveModal('none')}
            className="px-5 py-2 rounded-xl bg-sky-600 hover:bg-sky-500 text-white text-xs font-bold transition-colors"
          >
            {isArabic ? 'إغلاق' : 'Close'}
          </button>
        </div>
      </div>
    </div>
  );
};
