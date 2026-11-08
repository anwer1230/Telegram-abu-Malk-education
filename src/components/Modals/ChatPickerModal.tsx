import React, { useState, useMemo, useEffect } from 'react';
import {
  X,
  Check,
  Search,
  Users,
  Megaphone,
  BadgeCheck,
  RefreshCw,
  CheckSquare,
  Square,
  Sparkles,
  Layers,
  ArrowRight,
  ArrowLeft,
} from 'lucide-react';
import { useTelegram } from '../../context/TelegramContext';
import { Chat } from '../../types';

interface ChatPickerModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (selectedLinks: string[]) => void;
  alreadySelectedLinks?: string[];
}

interface DisplayItem {
  id: string;
  title: string;
  username?: string;
  type: 'group' | 'channel' | 'supergroup';
  avatar?: string;
  memberCount?: number;
  unreadCount?: number;
  isVerified?: boolean;
  link: string;
}

// Telegram 7-Peer Color Palettes for default avatars
const PEER_GRADIENTS = [
  'from-[#e17076] to-[#f0858a]', // coral red
  'from-[#faa774] to-[#fbb88c]', // orange
  'from-[#a695e7] to-[#b8a9ec]', // violet
  'from-[#7bc862] to-[#8ed676]', // green
  'from-[#6ec9cb] to-[#80d7d9]', // cyan
  'from-[#65aadd] to-[#7bb9e3]', // blue
  'from-[#ee7aae] to-[#f58ebc]', // pink
];

function getPeerGradient(name: string = '') {
  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = (hash * 31 + name.charCodeAt(i)) % PEER_GRADIENTS.length;
  }
  return PEER_GRADIENTS[Math.abs(hash)] || PEER_GRADIENTS[0];
}

export const ChatPickerModal: React.FC<ChatPickerModalProps> = ({
  isOpen,
  onClose,
  onConfirm,
  alreadySelectedLinks = [],
}) => {
  const { chats, settings, currentUser, showToast } = useTelegram();
  const isArabic = settings.language === 'ar';

  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState<'all' | 'group' | 'channel'>('all');
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [serverDialogs, setServerDialogs] = useState<DisplayItem[]>([]);
  const [isLoadingServer, setIsLoadingServer] = useState(false);

  // Load live dialogs from MTProto server endpoint if session is active
  const fetchServerDialogs = async () => {
    setIsLoadingServer(true);
    try {
      const session = localStorage.getItem('tg_mtproto_session') || '';
      const phone = currentUser?.phone || '';
      const userId = currentUser?.id || 'default_user';

      const res = await fetch(`/api/automation/dialogs?userId=${encodeURIComponent(userId)}`, {
        headers: {
          'x-telegram-session': session,
          'x-telegram-phone': phone,
          'x-user-id': userId,
        },
      });
      const data = await res.json();
      if (data.ok && Array.isArray(data.dialogs)) {
        const mapped: DisplayItem[] = data.dialogs
          .filter((d: any) => d.isGroup || d.isChannel)
          .map((d: any) => ({
            id: d.id,
            title: d.title,
            username: d.username,
            type: d.isGroup || d.megagroup ? 'group' : (d.isChannel && d.broadcast !== false ? 'channel' : 'group'),
            memberCount: d.participantsCount,
            unreadCount: d.unreadCount,
            link: d.link || (d.username ? `https://t.me/${d.username}` : `@${d.id}`),
          }));
        setServerDialogs(mapped);
      }
    } catch (e) {
      console.warn('Could not fetch server dialogs:', e);
    } finally {
      setIsLoadingServer(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchServerDialogs();
    }
  }, [isOpen]);

  // Combine and deduplicate chats from local state + server MTProto dialogs
  const allDisplayItems = useMemo<DisplayItem[]>(() => {
    const map = new Map<string, DisplayItem>();

    // 1. Local chats from TelegramContext (groups & channels)
    chats.forEach((c: Chat) => {
      if (c.type === 'group' || c.type === 'channel') {
        const link = c.username
          ? `https://t.me/${c.username}`
          : c.inviteLink || (c.id ? `https://t.me/c/${c.id.replace('-100', '').replace('-', '')}` : '');

        map.set(c.id, {
          id: c.id,
          title: c.title || (isArabic ? 'مجموعة بدون عنوان' : 'Untitled Group'),
          username: c.username,
          type: c.type,
          avatar: c.avatar,
          memberCount: c.memberCount,
          unreadCount: c.unreadCount,
          isVerified: c.isVerified,
          link: link || (c.username ? `@${c.username}` : c.title),
        });
      }
    });

    // 2. Merge server MTProto dialogs
    serverDialogs.forEach((sd) => {
      if (!map.has(sd.id)) {
        map.set(sd.id, sd);
      } else {
        const existing = map.get(sd.id)!;
        if (!existing.memberCount && sd.memberCount) existing.memberCount = sd.memberCount;
        if (!existing.username && sd.username) existing.username = sd.username;
        if (!existing.link && sd.link) existing.link = sd.link;
      }
    });

    return Array.from(map.values());
  }, [chats, serverDialogs, isArabic]);

  // Initialize selected IDs based on already entered groupsInput
  useEffect(() => {
    if (isOpen && alreadySelectedLinks.length > 0) {
      const initialSet = new Set<string>();
      const normalizedAlready = alreadySelectedLinks.map((l) =>
        l.toLowerCase().trim().replace(/^https?:\/\/t\.me\//, '').replace(/^@/, '')
      );

      allDisplayItems.forEach((item) => {
        const uname = (item.username || '').toLowerCase();
        const idClean = item.id.replace(/^-100/, '').replace(/^-/, '');
        if (
          normalizedAlready.includes(uname) ||
          normalizedAlready.includes(item.link.toLowerCase()) ||
          normalizedAlready.includes(idClean) ||
          normalizedAlready.includes(item.title.toLowerCase())
        ) {
          initialSet.add(item.id);
        }
      });

      if (initialSet.size > 0) {
        setSelectedIds(initialSet);
      }
    }
  }, [isOpen, alreadySelectedLinks, allDisplayItems]);

  // Filter items by search query & category
  const filteredItems = useMemo(() => {
    return allDisplayItems.filter((item) => {
      // Type match
      if (filterType === 'group' && item.type !== 'group' && item.type !== 'supergroup') return false;
      if (filterType === 'channel' && item.type !== 'channel') return false;

      // Query match
      if (!searchQuery.trim()) return true;
      const q = searchQuery.toLowerCase().trim();
      return (
        item.title.toLowerCase().includes(q) ||
        (item.username && item.username.toLowerCase().includes(q)) ||
        item.id.includes(q)
      );
    });
  }, [allDisplayItems, filterType, searchQuery]);

  // Toggle selection for a single chat
  const handleToggle = (id: string) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  // Select all visible filtered chats
  const handleSelectAllVisible = () => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      filteredItems.forEach((item) => next.add(item.id));
      return next;
    });
  };

  // Deselect all visible
  const handleDeselectAllVisible = () => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      filteredItems.forEach((item) => next.delete(item.id));
      return next;
    });
  };

  // Confirm selection and return links
  const handleConfirm = () => {
    const selectedLinks: string[] = [];
    allDisplayItems.forEach((item) => {
      if (selectedIds.has(item.id)) {
        // Prefer official https://t.me/ username link or clean identifier
        if (item.username) {
          selectedLinks.push(`https://t.me/${item.username}`);
        } else if (item.link && item.link.startsWith('http')) {
          selectedLinks.push(item.link);
        } else if (item.id) {
          const cleanId = item.id.replace(/^-100/, '').replace(/^-/, '');
          selectedLinks.push(`https://t.me/c/${cleanId}`);
        } else {
          selectedLinks.push(item.title);
        }
      }
    });

    onConfirm(selectedLinks);
    showToast(
      isArabic
        ? `تم نقل روابط ${selectedLinks.length} مجموعة بنجاح ✅`
        : `Transferred ${selectedLinks.length} group links successfully ✅`,
      'success'
    );
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-black/75 backdrop-blur-sm animate-fade-in">
      <div className="relative w-full max-w-lg bg-[#17212b] border border-[#242f3d] rounded-2xl shadow-2xl flex flex-col max-h-[88vh] overflow-hidden">
        {/* Top Header */}
        <div className="flex items-center justify-between px-4 py-3.5 border-b border-[#242f3d] bg-[#1d2733]/90">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-[#2481cc]/20 border border-[#2481cc]/40 flex items-center justify-center text-[#2481cc]">
              <Layers className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm sm:text-base font-bold text-white flex items-center gap-1.5">
                <span>{isArabic ? 'الواجهة الرئيسية للدردشات' : 'Chats Interface'}</span>
                <span className="text-[10px] bg-[#2481cc]/20 text-[#2481cc] border border-[#2481cc]/30 px-1.5 py-0.5 rounded font-mono">
                  {allDisplayItems.length}
                </span>
              </h3>
              <p className="text-[11px] text-gray-400">
                {isArabic
                  ? 'اختر المجموعات والقنوات التي تريد الإرسال إليها'
                  : 'Select target groups & channels for broadcast'}
              </p>
            </div>
          </div>

          {/* Top Actions: Prominent Confirm Button (موافق) and Close (X) */}
          <div className="flex items-center gap-2">
            <button
              onClick={handleConfirm}
              disabled={selectedIds.size === 0}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-[#2481cc] hover:bg-[#2074b8] active:scale-95 disabled:opacity-40 disabled:pointer-events-none text-white text-xs font-bold rounded-xl shadow-lg transition-all border border-white/10"
              title={isArabic ? 'موافق - اعتماد ونقل المجموعات المحددة' : 'Confirm Selection'}
            >
              <Check className="w-4 h-4 stroke-[3]" />
              <span>{isArabic ? 'موافق' : 'Confirm'}</span>
              <span className="bg-white/25 px-1.5 py-0.5 rounded-full text-[10px] font-mono">
                {selectedIds.size}
              </span>
            </button>

            <button
              onClick={onClose}
              className="p-1.5 rounded-xl hover:bg-white/10 text-gray-400 hover:text-white transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Search & Tabs Toolbar */}
        <div className="p-3 bg-[#17212b] border-b border-[#242f3d] space-y-2.5">
          {/* Search Box */}
          <div className="relative flex items-center">
            <Search className="absolute start-3 w-4 h-4 text-gray-400 pointer-events-none" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder={
                isArabic ? 'ابحث في محادثاتك ومجموعاتك...' : 'Search your chats & groups...'
              }
              className="w-full bg-[#0e1621] border border-[#242f3d] focus:border-[#2481cc] rounded-xl ps-9 pe-8 py-2 text-xs sm:text-sm text-white placeholder-gray-500 outline-none transition-colors"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="absolute end-2.5 text-gray-400 hover:text-white p-1"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            )}
          </div>

          {/* Filter Pills & Quick Selection Controls */}
          <div className="flex items-center justify-between flex-wrap gap-2 text-xs">
            {/* Category tabs */}
            <div className="flex items-center gap-1 bg-[#0e1621] p-1 rounded-xl border border-[#242f3d]">
              <button
                type="button"
                onClick={() => setFilterType('all')}
                className={`px-2.5 py-1 rounded-lg font-medium transition-all ${
                  filterType === 'all'
                    ? 'bg-[#2481cc] text-white shadow'
                    : 'text-gray-400 hover:text-gray-200'
                }`}
              >
                {isArabic ? 'الكل' : 'All'}
              </button>
              <button
                type="button"
                onClick={() => setFilterType('group')}
                className={`px-2.5 py-1 rounded-lg font-medium transition-all flex items-center gap-1 ${
                  filterType === 'group'
                    ? 'bg-[#2481cc] text-white shadow'
                    : 'text-gray-400 hover:text-gray-200'
                }`}
              >
                <Users className="w-3 h-3" />
                <span>{isArabic ? 'المجموعات' : 'Groups'}</span>
              </button>
              <button
                type="button"
                onClick={() => setFilterType('channel')}
                className={`px-2.5 py-1 rounded-lg font-medium transition-all flex items-center gap-1 ${
                  filterType === 'channel'
                    ? 'bg-[#2481cc] text-white shadow'
                    : 'text-gray-400 hover:text-gray-200'
                }`}
              >
                <Megaphone className="w-3 h-3" />
                <span>{isArabic ? 'القنوات' : 'Channels'}</span>
              </button>
            </div>

            {/* Quick Bulk Actions */}
            <div className="flex items-center gap-1.5">
              <button
                type="button"
                onClick={handleSelectAllVisible}
                className="px-2 py-1 rounded-lg bg-[#202b36] hover:bg-[#242f3d] text-gray-300 hover:text-white border border-[#242f3d] flex items-center gap-1 transition-colors"
                title={isArabic ? 'تحديد كل المعروض' : 'Select all shown'}
              >
                <CheckSquare className="w-3.5 h-3.5 text-[#2481cc]" />
                <span>{isArabic ? 'تحديد الكل' : 'Select All'}</span>
              </button>
              <button
                type="button"
                onClick={handleDeselectAllVisible}
                className="px-2 py-1 rounded-lg bg-[#202b36] hover:bg-[#242f3d] text-gray-300 hover:text-white border border-[#242f3d] flex items-center gap-1 transition-colors"
                title={isArabic ? 'إلغاء التحديد' : 'Deselect all'}
              >
                <Square className="w-3.5 h-3.5 text-gray-400" />
                <span>{isArabic ? 'إلغاء' : 'Clear'}</span>
              </button>
              <button
                type="button"
                onClick={fetchServerDialogs}
                disabled={isLoadingServer}
                className="p-1 rounded-lg bg-[#202b36] hover:bg-[#242f3d] text-gray-300 hover:text-white border border-[#242f3d] transition-colors"
                title={isArabic ? 'تحديث المحادثات من تيليجرام' : 'Refresh from Telegram'}
              >
                <RefreshCw className={`w-3.5 h-3.5 text-[#2481cc] ${isLoadingServer ? 'animate-spin' : ''}`} />
              </button>
            </div>
          </div>
        </div>

        {/* Scrollable Chat List (Miniature Telegram Main Chat Window) */}
        <div className="flex-1 overflow-y-auto divide-y divide-[#242f3d]/60 p-1">
          {filteredItems.length === 0 ? (
            <div className="py-12 px-4 text-center space-y-2">
              <div className="w-12 h-12 rounded-full bg-white/5 border border-white/10 flex items-center justify-center mx-auto text-gray-400">
                <Users className="w-6 h-6" />
              </div>
              <p className="text-sm font-semibold text-gray-300">
                {isArabic ? 'لا توجد مجموعات أو قنوات مطابقة' : 'No matching chats found'}
              </p>
              <p className="text-xs text-gray-500">
                {isArabic
                  ? 'تأكد من تسجيل الدخول بحساب تيليجرام يحتوي على مجموعات أو ابحث بكلمة أخرى'
                  : 'Check search query or verify your account is joined to groups'}
              </p>
            </div>
          ) : (
            filteredItems.map((item) => {
              const isSelected = selectedIds.has(item.id);
              const gradient = getPeerGradient(item.title);

              return (
                <div
                  key={item.id}
                  onClick={() => handleToggle(item.id)}
                  className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl cursor-pointer transition-all ${
                    isSelected
                      ? 'bg-[#2481cc]/15 hover:bg-[#2481cc]/25 border border-[#2481cc]/30'
                      : 'hover:bg-white/5 border border-transparent'
                  }`}
                >
                  <div className="flex items-center gap-3 min-w-0 flex-1">
                    {/* Checkbox indicator (✅) */}
                    <div
                      className={`w-5 h-5 rounded-lg flex items-center justify-center shrink-0 border transition-all ${
                        isSelected
                          ? 'bg-[#2481cc] border-[#2481cc] text-white shadow-md'
                          : 'border-gray-500 hover:border-gray-300 bg-[#0e1621]'
                      }`}
                    >
                      {isSelected ? (
                        <Check className="w-3.5 h-3.5 stroke-[3]" />
                      ) : null}
                    </div>

                    {/* Avatar */}
                    <div className="relative shrink-0">
                      {item.avatar ? (
                        <img
                          src={item.avatar}
                          alt={item.title}
                          className="w-10 h-10 rounded-full object-cover border border-white/10"
                        />
                      ) : (
                        <div
                          className={`w-10 h-10 rounded-full bg-gradient-to-tr ${gradient} flex items-center justify-center text-white font-bold text-sm shadow`}
                        >
                          {item.title ? item.title.slice(0, 1).toUpperCase() : 'G'}
                        </div>
                      )}

                      <div className="absolute -bottom-0.5 -end-0.5 w-4 h-4 rounded-full bg-[#17212b] flex items-center justify-center">
                        {item.type === 'channel' ? (
                          <Megaphone className="w-2.5 h-2.5 text-[#2481cc]" />
                        ) : (
                          <Users className="w-2.5 h-2.5 text-emerald-400" />
                        )}
                      </div>
                    </div>

                    {/* Info */}
                    <div className="min-w-0 flex-1 text-start">
                      <div className="flex items-center gap-1.5">
                        <span className="text-sm font-semibold text-white truncate">
                          {item.title}
                        </span>
                        {item.isVerified && (
                          <BadgeCheck className="w-3.5 h-3.5 text-[#2481cc] shrink-0" />
                        )}
                      </div>

                      <div className="flex items-center gap-2 text-[11px] text-gray-400 font-mono truncate">
                        {item.username ? (
                          <span className="text-[#5288c1]">@{item.username}</span>
                        ) : (
                          <span>{item.type === 'channel' ? (isArabic ? 'قناة' : 'Channel') : (isArabic ? 'مجموعة' : 'Group')}</span>
                        )}
                        {item.memberCount && (
                          <>
                            <span>•</span>
                            <span>{item.memberCount.toLocaleString()} {isArabic ? 'عضو' : 'members'}</span>
                          </>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Right: Selected Tag or unread count */}
                  <div className="shrink-0 ps-2">
                    {isSelected ? (
                      <span className="text-[11px] bg-[#2481cc] text-white px-2 py-0.5 rounded-full font-bold flex items-center gap-1">
                        <span>✅</span>
                        <span>{isArabic ? 'محدد' : 'Selected'}</span>
                      </span>
                    ) : item.unreadCount && item.unreadCount > 0 ? (
                      <span className="text-[11px] bg-white/10 text-gray-300 px-1.5 py-0.5 rounded-full">
                        {item.unreadCount}
                      </span>
                    ) : null}
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Bottom Bar with count and Confirm button */}
        <div className="p-3 border-t border-[#242f3d] bg-[#1d2733]/90 flex items-center justify-between gap-3">
          <div className="text-xs text-gray-300">
            <span>{isArabic ? 'تم اختيار:' : 'Selected:'} </span>
            <span className="font-bold text-[#2481cc] text-sm font-mono">
              {selectedIds.size}
            </span>
            <span className="text-gray-500"> / {allDisplayItems.length}</span>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={onClose}
              className="px-3 py-1.5 rounded-xl border border-[#242f3d] text-xs text-gray-300 hover:text-white hover:bg-white/5 transition-colors"
            >
              {isArabic ? 'إلغاء' : 'Cancel'}
            </button>
            <button
              type="button"
              onClick={handleConfirm}
              disabled={selectedIds.size === 0}
              className="px-4 py-2 rounded-xl bg-[#2481cc] hover:bg-[#2074b8] active:scale-95 disabled:opacity-40 disabled:pointer-events-none text-white text-xs font-bold flex items-center gap-1.5 shadow-lg transition-all"
            >
              <Check className="w-4 h-4 stroke-[3]" />
              <span>{isArabic ? 'موافق ونقل الروابط' : 'Confirm & Transfer'}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
