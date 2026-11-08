import React, { useState } from 'react';
import {
  ShieldCheck,
  Server,
  Key,
  Lock,
  Eye,
  EyeOff,
  RefreshCw,
  X,
  Radio,
  Code2,
  Copy,
  Check,
} from 'lucide-react';
import { useTelegram } from '../../context/TelegramContext';

export const ApiConfigModal: React.FC = () => {
  const {
    activeModal,
    setActiveModal,
    apiConfig,
    updateApiConfig,
    testApiLatency,
    settings,
  } = useTelegram();

  const [apiId, setApiId] = useState(apiConfig.apiId);
  const [apiHash, setApiHash] = useState(apiConfig.apiHash);
  const [dcId, setDcId] = useState(apiConfig.dcId);
  const [isTesting, setIsTesting] = useState(false);
  const [showKeys, setShowKeys] = useState(false);
  const [copiedKey, setCopiedKey] = useState(false);

  if (activeModal !== 'api-config') return null;

  const isArabic = settings.language === 'ar';

  const handleTestConnection = async () => {
    setIsTesting(true);
    await testApiLatency();
    setIsTesting(false);
  };

  const handleSave = () => {
    updateApiConfig({
      apiId,
      apiHash,
      dcId,
      dcIp: dcId === 4 ? '149.154.167.91' : dcId === 2 ? '149.154.167.50' : '149.154.175.100',
    });
    setActiveModal('none');
  };

  const copySession = () => {
    navigator.clipboard.writeText(apiConfig.sessionString);
    setCopiedKey(true);
    setTimeout(() => setCopiedKey(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 select-none">
      {/* Backdrop */}
      <div
        id="api-modal-backdrop"
        onClick={() => setActiveModal('none')}
        className="fixed inset-0 bg-black/75 backdrop-blur-xs transition-opacity animate-in fade-in"
      />

      {/* Modal Dialog */}
      <div
        id="api-modal-dialog"
        className="relative w-full max-w-lg rounded-2xl shadow-2xl overflow-hidden border z-10 animate-in zoom-in-95 duration-150 flex flex-col max-h-[90vh]"
        style={{
          backgroundColor: 'var(--tg-theme-surface)',
          borderColor: 'var(--tg-theme-border)',
          color: 'var(--tg-theme-bubble-in-text)',
        }}
      >
        {/* Header */}
        <div className="p-4 bg-gradient-to-r from-[#2481cc] to-[#1c6fad] text-white flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <ShieldCheck className="w-6 h-6 text-emerald-300" />
            <div>
              <div className="font-bold text-base">
                {isArabic ? 'إعدادات اتصال Telegram السحابي' : 'Telegram MTProto Cloud Config'}
              </div>
              <div className="text-xs text-white/80 font-mono">
                MTProto 2.0 Security Layer (Layer 184)
              </div>
            </div>
          </div>
          <button
            onClick={() => setActiveModal('none')}
            className="p-1 rounded-full hover:bg-white/20 text-white"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-5 overflow-y-auto space-y-4 text-xs sm:text-sm">
          {/* Active Connection Banner */}
          <div className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="relative">
                <Server className="w-5 h-5 text-emerald-400" />
                <span className="absolute -top-1 -right-1 w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
              </div>
              <div>
                <div className="font-bold text-emerald-400">
                  {isArabic ? 'متصل بخوادم تيليجرام (DC4)' : 'Connected to Telegram DC4 (Amsterdam)'}
                </div>
                <div className="text-xs text-gray-400 font-mono">
                  {apiConfig.mtprotoVersion} • Ping: {apiConfig.pingMs}ms
                </div>
              </div>
            </div>

            <button
              onClick={handleTestConnection}
              disabled={isTesting}
              className="px-3 py-1.5 rounded-lg bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 font-semibold text-xs flex items-center gap-1.5 transition-all"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isTesting ? 'animate-spin' : ''}`} />
              <span>{isArabic ? 'اختبار' : 'Ping'}</span>
            </button>
          </div>

          {/* Privacy Toggle */}
          <div className="flex items-center justify-between p-2.5 rounded-xl bg-black/20 border border-white/5">
            <div className="flex items-center gap-2 text-xs text-gray-300">
              <Lock className="w-4 h-4 text-sky-400" />
              <span>{isArabic ? 'حماية وإخفاء بيانات الاعتماد السرية' : 'Mask sensitive credentials'}</span>
            </div>
            <button
              type="button"
              onClick={() => setShowKeys(!showKeys)}
              className="flex items-center gap-1 text-xs text-sky-400 hover:text-sky-300 font-medium"
            >
              {showKeys ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
              <span>{showKeys ? (isArabic ? 'إخفاء' : 'Hide') : (isArabic ? 'إظهار' : 'Reveal')}</span>
            </button>
          </div>

          {/* API_ID Input */}
          <div className="space-y-1.5">
            <label className="font-semibold flex items-center gap-1.5 text-sky-400">
              <Key className="w-4 h-4" />
              <span>API_ID</span>
            </label>
            <input
              type={showKeys ? 'text' : 'password'}
              value={apiId}
              onChange={(e) => setApiId(e.target.value)}
              placeholder="e.g. 22043994"
              className="w-full px-3 py-2 rounded-xl bg-black/20 border border-white/10 font-mono text-sm focus:border-[#2481cc] focus:outline-none"
            />
            <span className="text-[11px] text-gray-400">
              {isArabic ? 'معرف التطبيق الداخلي المسجل' : 'Registered App ID'}
            </span>
          </div>

          {/* API_HASH Input */}
          <div className="space-y-1.5">
            <label className="font-semibold flex items-center gap-1.5 text-sky-400">
              <Lock className="w-4 h-4" />
              <span>API_HASH</span>
            </label>
            <input
              type={showKeys ? 'text' : 'password'}
              value={apiHash}
              onChange={(e) => setApiHash(e.target.value)}
              placeholder="e.g. 56f64582b363d367280db96586b97801"
              className="w-full px-3 py-2 rounded-xl bg-black/20 border border-white/10 font-mono text-sm focus:border-[#2481cc] focus:outline-none"
            />
            <span className="text-[11px] text-gray-400">
              {isArabic ? 'المفتاح السري المشفر لمصادقة جلسات MTProto' : 'Secret hash token for MTProto sessions'}
            </span>
          </div>

          {/* Data Center Selector */}
          <div className="space-y-1.5">
            <label className="font-semibold flex items-center gap-1.5">
              <Radio className="w-4 h-4 text-purple-400" />
              <span>{isArabic ? 'مركز البيانات (Data Center)' : 'Telegram Data Center (DC)'}</span>
            </label>
            <div className="grid grid-cols-3 gap-2">
              {[
                { id: 2, name: 'DC2 Amsterdam', ip: '149.154.167.50' },
                { id: 4, name: 'DC4 Amsterdam (Default)', ip: '149.154.167.91' },
                { id: 5, name: 'DC5 Singapore', ip: '91.108.56.100' },
              ].map((dc) => (
                <button
                  key={dc.id}
                  onClick={() => setDcId(dc.id)}
                  className={`p-2 rounded-xl border text-left rtl:text-right text-xs transition-all ${
                    dcId === dc.id
                      ? 'border-[#2481cc] bg-[#2481cc]/20 font-bold'
                      : 'border-white/10 bg-black/10 hover:bg-white/5'
                  }`}
                >
                  <div className="truncate">{dc.name}</div>
                  <div className="text-[10px] font-mono opacity-60 truncate">{dc.ip}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Session String & Auth Key */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <label className="font-semibold flex items-center gap-1.5 text-gray-300">
                <Code2 className="w-4 h-4 text-amber-400" />
                <span>{isArabic ? 'مفتاح الجلسة المشفر (MTProto 2.0)' : 'MTProto 2.0 AuthKey Session'}</span>
              </label>
              <button
                onClick={copySession}
                className="text-xs text-sky-400 hover:text-sky-300 flex items-center gap-1"
              >
                {copiedKey ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                <span>{copiedKey ? (isArabic ? 'تم النسخ' : 'Copied') : (isArabic ? 'نسخ' : 'Copy')}</span>
              </button>
            </div>
            <div className="p-2.5 rounded-xl bg-black/30 border border-white/10 font-mono text-[11px] text-gray-400 break-all select-all">
              {showKeys ? apiConfig.sessionString : '•••••••••••••••••••••••••••••••••••••••• (Encrypted AuthKey)'}
            </div>
          </div>
        </div>

        {/* Footer Actions */}
        <div
          className="p-3 border-t flex items-center justify-end gap-2"
          style={{ borderColor: 'var(--tg-theme-border)' }}
        >
          <button
            onClick={() => setActiveModal('none')}
            className="px-4 py-2 rounded-xl hover:bg-white/10 text-gray-300 text-xs font-semibold"
          >
            {isArabic ? 'إلغاء' : 'Cancel'}
          </button>
          <button
            onClick={handleSave}
            className="px-5 py-2 rounded-xl bg-[#2481cc] hover:bg-[#1c6fad] text-white text-xs font-bold shadow-md transition-all active:scale-95"
          >
            {isArabic ? 'حفظ وتحديث الاتصال' : 'Save & Connect'}
          </button>
        </div>
      </div>
    </div>
  );
};
