import React, { useState, useEffect } from 'react';
import {
  MessageSquare,
  Plus,
  Trash2,
  CheckCircle2,
  Sliders,
  X,
  ToggleLeft,
  ToggleRight,
  Sparkles,
  Cpu,
} from 'lucide-react';
import { useTelegram } from '../../context/TelegramContext';
import { backgroundSyncService, BackgroundWorkerStatus } from '../../core/BackgroundSyncService';
import { AutoReplyRule } from '../../types';

export const AutoResponderModal: React.FC = () => {
  const { activeModal, setActiveModal, showToast } = useTelegram();
  const [rules, setRules] = useState<AutoReplyRule[]>([]);
  const [isGlobalActive, setIsGlobalActive] = useState(true);
  const [workerStatus, setWorkerStatus] = useState<BackgroundWorkerStatus>(backgroundSyncService.getWorkerStatus());

  // New rule form
  const [showAddForm, setShowAddForm] = useState(false);
  const [keyword, setKeyword] = useState('');
  const [replyText, setReplyText] = useState('');
  const [matchType, setMatchType] = useState<'exact' | 'contains' | 'regex'>('contains');
  const [scope, setScope] = useState<'all' | 'private' | 'groups'>('all');

  useEffect(() => {
    backgroundSyncService.syncWithBackend();
    const unsub = backgroundSyncService.subscribe(() => {
      setRules([...backgroundSyncService.getAutoReplyRules()]);
      setIsGlobalActive(backgroundSyncService.isAutoResponderActive());
      setWorkerStatus(backgroundSyncService.getWorkerStatus());
    });
    setRules([...backgroundSyncService.getAutoReplyRules()]);
    setIsGlobalActive(backgroundSyncService.isAutoResponderActive());
    setWorkerStatus(backgroundSyncService.getWorkerStatus());
    return () => unsub();
  }, []);

  if (activeModal !== ('auto-responder' as any)) return null;

  const handleCreateRule = () => {
    if (!keyword.trim() || !replyText.trim()) {
      showToast('يرجى ملء الكلمة المفتاحية ونص الرد أولاً', '⚠️');
      return;
    }

    backgroundSyncService.addAutoReplyRule({
      keyword: keyword.trim(),
      replyText: replyText.trim(),
      matchType,
      scope,
      isEnabled: true,
    });

    setKeyword('');
    setReplyText('');
    setShowAddForm(false);
    showToast('تمت إضافة قاعدة الرد التلقائي بنجاح ✨', '🎉');
  };

  const handleToggleGlobal = () => {
    const next = !isGlobalActive;
    backgroundSyncService.toggleGlobalAutoResponder(next);
    setIsGlobalActive(next);
    showToast(next ? 'تم تفعيل الردود التلقائية ✅' : 'تم تعطيل الردود التلقائية ❌', '🤖');
  };

  return (
    <div
      id="modal-auto-responder-activity"
      className="fixed inset-0 z-[9999] flex items-center justify-center p-3 sm:p-4 bg-black/85 backdrop-blur-md select-none"
      dir="rtl"
    >
      <div
        className="w-full max-w-2xl text-[#e8eaf6] rounded-3xl shadow-2xl overflow-hidden border border-cyan-500/30 my-auto animate-in zoom-in-95 duration-200 max-h-[90vh] flex flex-col"
        style={{
          background: 'linear-gradient(145deg, #051419, #0a2530, #030d11)',
        }}
      >
        {/* Header */}
        <div className="p-4 sm:p-5 border-b border-white/10 flex items-center justify-between bg-black/40">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-cyan-500/20 text-cyan-400 flex items-center justify-center border border-cyan-400/30">
              <MessageSquare className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-sm text-white flex items-center gap-2">
                <span>وظيفة الردود التلقائية</span>
                <span className="px-2 py-0.5 rounded-full text-[9px] font-mono font-bold bg-cyan-500/20 text-cyan-300 border border-cyan-400/30 flex items-center gap-1">
                  <Cpu className="w-2.5 h-2.5 text-cyan-400" />
                  {workerStatus.workerType === 'web-worker' ? 'Web Worker Thread' : 'Fallback Engine'}
                </span>
              </h3>
              <p className="text-[11px] text-cyan-300/80">استجابات فورية ذكية وغير معطلة لواجهة المستخدم في الخلفية</p>
            </div>
          </div>
          <button
            onClick={() => setActiveModal('none')}
            className="p-2 rounded-xl text-gray-400 hover:text-white hover:bg-white/10 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Body */}
        <div className="p-4 sm:p-6 overflow-y-auto space-y-4 flex-1">
          {/* Global Master Switch */}
          <div className="p-4 rounded-2xl bg-black/30 border border-white/10 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Sliders className="w-5 h-5 text-cyan-400" />
              <div>
                <span className="font-bold text-xs block text-white">المفتاح الرئيسي للردود التلقائية</span>
                <span className="text-[10px] text-gray-400">
                  {isGlobalActive ? 'النظام يستمع ويرد تلقائياً' : 'النظام متوقف حالياً'}
                </span>
              </div>
            </div>

            <button
              onClick={handleToggleGlobal}
              className={`p-1.5 rounded-2xl transition-colors ${
                isGlobalActive ? 'text-cyan-400 hover:text-cyan-300' : 'text-gray-500'
              }`}
            >
              {isGlobalActive ? (
                <ToggleRight className="w-9 h-9 fill-cyan-400/20" />
              ) : (
                <ToggleLeft className="w-9 h-9" />
              )}
            </button>
          </div>

          {/* Add Rule Button / Form */}
          {!showAddForm ? (
            <button
              onClick={() => setShowAddForm(true)}
              className="w-full py-3 rounded-2xl border border-dashed border-cyan-500/40 text-cyan-400 hover:bg-cyan-500/10 transition-all font-bold text-xs flex items-center justify-center gap-2"
            >
              <Plus className="w-4 h-4" />
              <span>إنشاء قاعدة رد تلقائي جديدة</span>
            </button>
          ) : (
            <div className="p-4 rounded-2xl bg-black/50 border border-cyan-400/30 space-y-3">
              <div className="flex items-center justify-between">
                <span className="font-bold text-xs text-cyan-300">إضافة قاعدة رد جديدة:</span>
                <button
                  onClick={() => setShowAddForm(false)}
                  className="text-gray-400 hover:text-white"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              <div className="space-y-1">
                <label className="text-[11px] text-gray-300 block">الكلمة المفتاحية أو العبارة:</label>
                <input
                  type="text"
                  value={keyword}
                  onChange={(e) => setKeyword(e.target.value)}
                  placeholder="مثال: كم السعر، السلام عليكم، تفاصيل..."
                  className="w-full bg-black/40 border border-white/10 rounded-xl px-3 py-2 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-cyan-400"
                />
              </div>

              <div className="space-y-1">
                <label className="text-[11px] text-gray-300 block">نص الرد التلقائي:</label>
                <textarea
                  value={replyText}
                  onChange={(e) => setReplyText(e.target.value)}
                  rows={2}
                  placeholder="اكتب الرد الذي سيتم إرساله للمستخدم..."
                  className="w-full bg-black/40 border border-white/10 rounded-xl p-2.5 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-cyan-400 resize-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-[11px] text-gray-300 block mb-1">نوع المطابقة:</label>
                  <select
                    value={matchType}
                    onChange={(e) => setMatchType(e.target.value as any)}
                    className="w-full bg-black/60 border border-white/10 rounded-xl px-3 py-1.5 text-xs text-white focus:outline-none"
                  >
                    <option value="contains">احتواء (تتضمن الكلمة)</option>
                    <option value="exact">مطابقة تامة</option>
                    <option value="regex">تعبير نمطي (RegEx)</option>
                  </select>
                </div>

                <div>
                  <label className="text-[11px] text-gray-300 block mb-1">النطاق:</label>
                  <select
                    value={scope}
                    onChange={(e) => setScope(e.target.value as any)}
                    className="w-full bg-black/60 border border-white/10 rounded-xl px-3 py-1.5 text-xs text-white focus:outline-none"
                  >
                    <option value="all">كافة المحادثات</option>
                    <option value="private">الخاص فقط</option>
                    <option value="groups">المجموعات فقط</option>
                  </select>
                </div>
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  onClick={() => setShowAddForm(false)}
                  className="px-3 py-1.5 rounded-xl bg-white/10 text-gray-300 text-xs font-bold"
                >
                  إلغاء
                </button>
                <button
                  onClick={handleCreateRule}
                  className="px-5 py-1.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-bold shadow"
                >
                  حفظ القاعدة
                </button>
              </div>
            </div>
          )}

          {/* Rules List */}
          <div className="space-y-2">
            <span className="text-xs font-bold text-gray-200 block">قواعد الردود النشطة ({rules.length}):</span>

            {rules.length === 0 ? (
              <div className="p-6 rounded-2xl bg-black/20 border border-white/5 text-center text-xs text-gray-500">
                لا يوجد قواعد رد مضافة حالياً
              </div>
            ) : (
              rules.map((rule) => (
                <div
                  key={rule.id}
                  className={`p-3.5 rounded-2xl border transition-all ${
                    rule.isEnabled
                      ? 'bg-black/40 border-cyan-500/20 hover:border-cyan-500/40'
                      : 'bg-black/20 border-white/5 opacity-50'
                  }`}
                >
                  <div className="flex items-center justify-between text-xs mb-1.5">
                    <div className="flex items-center gap-2">
                      <span className="px-2.5 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300 text-[10px] font-bold">
                        {rule.keyword}
                      </span>
                      <span className="text-[10px] text-gray-400">({rule.matchType})</span>
                    </div>

                    <div className="flex items-center gap-2">
                      <span className="text-[10px] text-gray-400">تم الرد: {rule.timesTriggered} مرة</span>
                      <button
                        onClick={() => backgroundSyncService.toggleRule(rule.id)}
                        className="text-gray-400 hover:text-cyan-300"
                      >
                        {rule.isEnabled ? (
                          <ToggleRight className="w-6 h-6 text-cyan-400" />
                        ) : (
                          <ToggleLeft className="w-6 h-6" />
                        )}
                      </button>
                      <button
                        onClick={() => backgroundSyncService.deleteRule(rule.id)}
                        className="text-gray-400 hover:text-rose-400 p-1"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>

                  <p className="text-xs text-gray-300 bg-white/5 p-2 rounded-xl border border-white/5">
                    "{rule.replyText}"
                  </p>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 bg-black/40 border-t border-white/10 flex items-center justify-between">
          <button
            onClick={() => setActiveModal('none')}
            className="px-5 py-2 rounded-xl bg-white/10 hover:bg-white/20 text-white text-xs font-bold transition-colors"
          >
            إغلاق
          </button>
        </div>
      </div>
    </div>
  );
};
