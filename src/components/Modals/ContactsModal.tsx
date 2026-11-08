import React, { useState } from 'react';
import {
  Users,
  X,
  UserPlus,
  Search,
  Phone,
  MessageSquare,
  Upload,
  Download,
  Share2,
  CheckCircle2,
  Trash2,
  Sparkles,
} from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { useTelegram } from '../../context/TelegramContext';
import confetti from 'canvas-confetti';

interface ContactEntry {
  id: string;
  name: string;
  phone: string;
  username?: string;
  avatar: string;
  isOnline?: boolean;
}

const INITIAL_SAVED_CONTACTS: ContactEntry[] = [];

interface ContactsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const ContactsModal: React.FC<ContactsModalProps> = ({ isOpen, onClose }) => {
  const { settings, setActiveChatId, setActiveModal, showToast } = useTelegram();
  const isArabic = settings.language === 'ar';

  const [contactsList, setContactsList] = useState<ContactEntry[]>(() => {
    const saved = localStorage.getItem('tg_saved_contacts_v1');
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch {}
    }
    return INITIAL_SAVED_CONTACTS;
  });

  const [search, setSearch] = useState<string>('');
  const [showAddForm, setShowAddForm] = useState<boolean>(false);
  const [newName, setNewName] = useState<string>('');
  const [newPhone, setNewPhone] = useState<string>('');
  const [newUsername, setNewUsername] = useState<string>('');

  const handleSaveContact = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newName.trim() || !newPhone.trim()) return;

    const newContact: ContactEntry = {
      id: `contact_${Date.now()}`,
      name: newName.trim(),
      phone: newPhone.trim(),
      username: newUsername.trim() ? newUsername.replace('@', '') : undefined,
      avatar: '',
      isOnline: Math.random() > 0.5,
    };

    const updated = [newContact, ...contactsList];
    setContactsList(updated);
    localStorage.setItem('tg_saved_contacts_v1', JSON.stringify(updated));

    setNewName('');
    setNewPhone('');
    setNewUsername('');
    setShowAddForm(false);

    try {
      confetti({
        particleCount: 40,
        spread: 60,
        origin: { y: 0.6 },
      });
    } catch {}

    showToast(
      isArabic
        ? `تمت إضافة جهة الاتصال "${newContact.name}" ومزامنتها!`
        : `Contact "${newContact.name}" added & synced!`,
      '👤'
    );
  };

  const handleExportVCard = () => {
    let vcardData = '';
    contactsList.forEach((c) => {
      vcardData += `BEGIN:VCARD\nVERSION:3.0\nFN:${c.name}\nTEL;TYPE=CELL:${c.phone}\nNOTE:Telegram Contact\nEND:VCARD\n\n`;
    });

    const blob = new Blob([vcardData], { type: 'text/vcard' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Telegram_Contacts_${new Date().toISOString().slice(0, 10)}.vcf`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    showToast(
      isArabic ? 'تم تصدير جهات الاتصال بصيغة VCard (.vcf)' : 'Contacts exported to VCard (.vcf)',
      '📥'
    );
  };

  const filtered = contactsList.filter(
    (c) =>
      c.name.toLowerCase().includes(search.toLowerCase()) ||
      c.phone.includes(search) ||
      (c.username && c.username.toLowerCase().includes(search.toLowerCase()))
  );

  return (
    <AnimatePresence>
      {isOpen && (
        <div
          id="modal-telegram-contacts-manager"
          className="fixed inset-0 z-[9990] flex items-center justify-center p-3 sm:p-4 bg-black/80 backdrop-blur-md select-none"
          dir={isArabic ? 'rtl' : 'ltr'}
        >
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            onClick={onClose}
            className="absolute inset-0 cursor-pointer"
          />

          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 15 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 15 }}
            transition={{ type: 'spring', damping: 28, stiffness: 320 }}
            className="relative z-10 w-full max-w-lg bg-[#17212b] border border-white/10 text-white rounded-3xl shadow-2xl overflow-hidden flex flex-col max-h-[85vh]"
          >
            {/* Header */}
            <div className="h-14 px-4 border-b border-white/10 flex items-center justify-between bg-[#1e2c3a]/80 shrink-0">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-[#2481cc] to-sky-400 flex items-center justify-center shadow">
                  <Users className="w-4 h-4 text-white" />
                </div>
                <div>
                  <h3 className="font-bold text-sm text-white">
                    {isArabic ? 'جهات الاتصال (Contacts Sync)' : 'Contacts & VCard Sync'}
                  </h3>
                  <p className="text-[11px] text-gray-400">
                    {isArabic ? 'DrKLO contacts.importContacts' : 'Manage, import & export phone contacts'}
                  </p>
                </div>
              </div>

              <button
                onClick={onClose}
                className="p-2 rounded-xl text-gray-400 hover:text-white hover:bg-white/10 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Content */}
            <div className="p-4 flex-1 overflow-y-auto space-y-4">
              {/* Action Row */}
              <div className="flex items-center justify-between gap-2">
                {/* Search Input */}
                <div className="relative flex-1">
                  <Search className="w-4 h-4 text-gray-400 absolute left-3 rtl:left-auto rtl:right-3 top-1/2 -translate-y-1/2" />
                  <input
                    type="text"
                    placeholder={isArabic ? 'بحث في جهات الاتصال...' : 'Search contacts...'}
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    className="w-full pl-9 pr-3 rtl:pl-3 rtl:pr-9 py-2 rounded-xl bg-white/5 border border-white/5 text-xs text-white placeholder:text-gray-400 focus:outline-none focus:border-sky-400"
                  />
                </div>

                <button
                  onClick={() => setShowAddForm(!showAddForm)}
                  className="px-3 py-2 rounded-xl bg-[#2481cc] hover:bg-[#1c6fad] text-white text-xs font-bold flex items-center gap-1.5 shrink-0 transition-colors"
                >
                  <UserPlus className="w-3.5 h-3.5" />
                  <span>{isArabic ? 'إضافة' : 'Add'}</span>
                </button>

                <button
                  onClick={handleExportVCard}
                  className="p-2 rounded-xl bg-white/5 hover:bg-white/10 text-gray-300 hover:text-white text-xs border border-white/5 shrink-0 transition-colors"
                  title={isArabic ? 'تصدير VCF' : 'Export VCF'}
                >
                  <Download className="w-4 h-4" />
                </button>
              </div>

              {/* Add Contact Collapsible Form */}
              {showAddForm && (
                <form
                  onSubmit={handleSaveContact}
                  className="p-3.5 rounded-2xl bg-[#0e1621] border border-white/10 space-y-2.5 animate-in slide-in-from-top-2"
                >
                  <div className="text-xs font-bold text-sky-400">
                    {isArabic ? 'إضافة جهة اتصال جديدة' : 'Add New Contact'}
                  </div>
                  <input
                    type="text"
                    placeholder={isArabic ? 'الاسم الكامل' : 'Full Name'}
                    value={newName}
                    onChange={(e) => setNewName(e.target.value)}
                    required
                    className="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/5 text-xs text-white focus:outline-none focus:border-sky-400"
                  />
                  <input
                    type="tel"
                    placeholder={isArabic ? 'رقم الهاتف (مثال: +966...)' : 'Phone Number (+...)'}
                    value={newPhone}
                    onChange={(e) => setNewPhone(e.target.value)}
                    required
                    className="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/5 text-xs text-white focus:outline-none focus:border-sky-400"
                  />
                  <input
                    type="text"
                    placeholder={isArabic ? 'اسم المستخدم (اختياري)' : 'Username (optional)'}
                    value={newUsername}
                    onChange={(e) => setNewUsername(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/5 text-xs text-white focus:outline-none focus:border-sky-400"
                  />
                  <div className="flex justify-end gap-2 pt-1">
                    <button
                      type="button"
                      onClick={() => setShowAddForm(false)}
                      className="px-3 py-1.5 rounded-xl bg-white/5 text-gray-300 text-xs font-semibold"
                    >
                      {isArabic ? 'إلغاء' : 'Cancel'}
                    </button>
                    <button
                      type="submit"
                      className="px-4 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold"
                    >
                      {isArabic ? 'حفظ المزامنة' : 'Save & Sync'}
                    </button>
                  </div>
                </form>
              )}

              {/* Contacts List */}
              <div className="space-y-1 divide-y divide-white/5">
                {filtered.length === 0 ? (
                  <div className="py-8 text-center text-xs text-gray-400">
                    {isArabic ? 'لا توجد جهات اتصال مطابقة' : 'No contacts found'}
                  </div>
                ) : (
                  filtered.map((contact) => (
                    <div
                      key={contact.id}
                      className="pt-2 pb-2 first:pt-0 flex items-center justify-between gap-3 hover:bg-white/5 px-2 rounded-xl transition-colors group"
                    >
                      <div className="flex items-center gap-3 min-w-0 flex-1">
                        <div className="relative w-10 h-10 rounded-full overflow-hidden shrink-0 border border-white/10">
                          {contact.avatar ? (
                            <img
                              src={contact.avatar}
                              alt={contact.name}
                              className="w-full h-full object-cover"
                            />
                          ) : (
                            <div className="w-full h-full bg-[#5288c1] flex items-center justify-center text-white font-bold text-sm">
                              {contact.name.charAt(0).toUpperCase()}
                            </div>
                          )}
                          {contact.isOnline && (
                            <div className="absolute bottom-0 right-0 w-3 h-3 rounded-full bg-emerald-500 border-2 border-[#17212b]" />
                          )}
                        </div>
                        <div className="min-w-0 flex-1">
                          <div className="text-xs font-bold text-white truncate flex items-center gap-1.5">
                            <span className="truncate">{contact.name}</span>
                            {contact.username && (
                              <span className="text-[10px] text-sky-400 font-mono">@{contact.username}</span>
                            )}
                          </div>
                          <div className="text-[11px] text-gray-400 font-mono truncate">{contact.phone}</div>
                        </div>
                      </div>

                      <div className="flex items-center gap-1">
                        <button
                          onClick={() => {
                            setActiveChatId('chat_sarah');
                            onClose();
                          }}
                          className="p-2 rounded-xl text-sky-400 hover:bg-sky-500/10 transition-colors"
                          title={isArabic ? 'بدء محادثة' : 'Start chat'}
                        >
                          <MessageSquare className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => {
                            setActiveModal('call');
                            onClose();
                          }}
                          className="p-2 rounded-xl text-emerald-400 hover:bg-emerald-500/10 transition-colors"
                          title={isArabic ? 'مكالمة صوتية' : 'Voice call'}
                        >
                          <Phone className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
};
