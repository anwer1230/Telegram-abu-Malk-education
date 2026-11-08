import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import {
  X,
  UserPlus,
  Phone,
  User as UserIcon,
  AtSign,
  FileText,
  Check,
  ShieldCheck,
  Sparkles,
  Smartphone,
  MessageSquare,
  Radio,
  ArrowRight,
  ArrowLeft,
  RotateCw,
  Copy,
  AlertCircle,
  Clock,
  Send,
  Lock,
  Search,
  ChevronDown,
} from 'lucide-react';
import { useTelegram } from '../../context/TelegramContext';
import { COUNTRIES, Country, searchCountries } from '../../data/countries';

const AVATAR_PRESETS = [
  { id: 'grad_blue', name: 'Blue', color: 'from-blue-500 to-indigo-600', icon: '👤' },
  { id: 'grad_green', name: 'Green', color: 'from-emerald-500 to-teal-600', icon: '🌟' },
  { id: 'grad_purple', name: 'Purple', color: 'from-purple-500 to-indigo-700', icon: '🚀' },
  { id: 'grad_amber', name: 'Orange', color: 'from-amber-500 to-orange-600', icon: '⚡' },
  { id: 'grad_rose', name: 'Rose', color: 'from-rose-500 to-pink-600', icon: '💎' },
  { id: 'grad_cyan', name: 'Cyan', color: 'from-cyan-500 to-blue-600', icon: '🛡️' },
];

type AuthStep = 'phone' | 'code' | 'profile';
type DeliveryType = 'app' | 'sms' | 'call';

export const AddAccountModal: React.FC = () => {
  const { activeModal, setActiveModal, addAccount, settings, showToast, apiConfig } = useTelegram();
  const isArabic = settings.language === 'ar';

  // Step management
  const [step, setStep] = useState<AuthStep>('phone');
  const [selectedCountry, setSelectedCountry] = useState<Country>(COUNTRIES[0]);
  const selectedCountryCode = selectedCountry.code;
  const setSelectedCountryCode = (code: string) => {
    const found = COUNTRIES.find((c) => c.code === code);
    if (found) setSelectedCountry(found);
  };
  const [countryDropdownOpen, setCountryDropdownOpen] = useState(false);
  const [countrySearch, setCountrySearch] = useState('');
  const [rawPhone, setRawPhone] = useState('');
  const [deliveryType, setDeliveryType] = useState<DeliveryType>('app');
  const [isLoading, setIsLoading] = useState(false);
  const [phoneCodeHash, setPhoneCodeHash] = useState('');
  
  // Verification code inputs (5 boxes)
  const [codeDigits, setCodeDigits] = useState(['', '', '', '', '']);
  const [codeError, setCodeError] = useState('');
  const [timerSeconds, setTimerSeconds] = useState(60);
  const [canResend, setCanResend] = useState(false);
  const [serviceNotification, setServiceNotification] = useState<any>(null);
  const [isRealTelegram, setIsRealTelegram] = useState(false);
  const [requires2FA, setRequires2FA] = useState(false);
  const [twoFaPassword, setTwoFaPassword] = useState('');
  const [accountSessionString, setAccountSessionString] = useState('');
  const [userAvatar, setUserAvatar] = useState('');

  // Profile Step Data
  const [name, setName] = useState('');
  const [username, setUsername] = useState('');
  const [bio, setBio] = useState('Telegram MTProto 2.0 Client');
  const [selectedAvatar, setSelectedAvatar] = useState('grad_blue');

  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

  const fullPhoneNumber = `${selectedCountryCode} ${rawPhone}`.trim();

  // Reset when modal opens
  useEffect(() => {
    if (activeModal === 'add-account') {
      setStep('phone');
      setCodeDigits(['', '', '', '', '']);
      setCodeError('');
      setServiceNotification(null);
      setTimerSeconds(60);
      setCanResend(false);
    }
  }, [activeModal]);

  // Countdown timer for code resend
  useEffect(() => {
    let interval: any = null;
    if (step === 'code' && timerSeconds > 0) {
      interval = setInterval(() => {
        setTimerSeconds((prev) => {
          if (prev <= 1) {
            setCanResend(true);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [step, timerSeconds]);

  // فحص الكود التلقائي فور وصوله للجهاز الآخر وللبريد الإلكتروني معاً
  useEffect(() => {
    if (step !== 'code') return;
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`/api/latest_verification_code?phone=${encodeURIComponent(phone)}`);
        const data = await res.json();
        if (data && data.has_code && data.data?.code) {
          const digits = String(data.data.code).split('').slice(0, 5);
          if (digits.length === 5) {
            setCodeDigits(digits);
            showToast(
              isArabic
                ? `🔑 تم استلام الكود (${data.data.code}) مترافقاً على بريدك الإلكتروني والجهاز الآخر!`
                : `Code (${data.data.code}) arrived to your email and other device!`,
              '✨'
            );
          }
        }
      } catch (_) {}
    }, 2500);

    return () => clearInterval(interval);
  }, [step, phone, isArabic, showToast]);

  if (activeModal !== 'add-account') return null;

  // Handle Step 1: Request Code (auth.sendCode)
  const handleRequestCode = async (e?: React.FormEvent, customDelivery?: DeliveryType) => {
    if (e) e.preventDefault();
    if (!rawPhone.trim()) {
      showToast(isArabic ? 'يرجى إدخال رقم الهاتف' : 'Please enter phone number', '⚠️');
      return;
    }

    const type = customDelivery || deliveryType;
    setIsLoading(true);
    setCodeError('');

    try {
      const response = await fetch('/api/telegram/auth/send-code', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          phone: fullPhoneNumber,
          deliveryType: type,
          apiId: apiConfig.apiId,
          apiHash: apiConfig.apiHash,
        }),
      });

      const data = await response.json();

      if (data.success) {
        setPhoneCodeHash(data.phoneCodeHash || '');
        setServiceNotification(data.serviceNotification || null);
        setIsRealTelegram(Boolean(data.isRealTelegramMTProto));
        setStep('code');
        setTimerSeconds(data.timeout || 60);
        setCanResend(false);

        showToast(
          data.message ||
            (type === 'app'
              ? isArabic
                ? '📲 تم إرسال الرمز كإشعار رسمي إلى تطبيق تيليجرام في أجهزتك الأخرى'
                : '📲 Code sent to your active Telegram devices'
              : isArabic
              ? '📩 تم إرسال الرمز عبر رسالة SMS'
              : '📩 Code sent via SMS'),
          '⚡'
        );

        // Auto focus first digit input
        setTimeout(() => {
          inputRefs.current[0]?.focus();
        }, 150);
      } else {
        showToast(data.message || 'فشل إرسال الرمز من تيليجرام', '❌');
      }
    } catch (err: any) {
      console.error('Send code error:', err);
      showToast(isArabic ? 'خطأ في الاتصال بالخادم' : 'Server connection error', '❌');
    } finally {
      setIsLoading(false);
    }
  };

  // Handle 2FA Password Submission
  const handleVerify2FA = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!twoFaPassword.trim()) {
      setCodeError(isArabic ? 'يرجى إدخال كلمة مرور 2FA' : 'Please enter 2FA password');
      return;
    }

    setIsLoading(true);
    setCodeError('');

    try {
      const resp = await fetch('/api/telegram/auth/verify-code', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          phone: fullPhoneNumber,
          code: codeDigits.join(''),
          phoneCodeHash,
          password: twoFaPassword.trim(),
        }),
      });

      const data = await resp.json();

      if (data.success) {
        showToast(isArabic ? '✅ تم التحقق وتوثيق الحساب بنجاح' : '✅ Account verified', '🎉');
        if (data.sessionString) {
          setAccountSessionString(data.sessionString);
        }
        if (data.user) {
          const fetchedName = [data.user.firstName, data.user.lastName].filter(Boolean).join(' ');
          setName(fetchedName || (isArabic ? `حساب (${selectedCountryCode})` : `Account (${selectedCountryCode})`));
          if (data.user.username) {
            setUsername(data.user.username);
          }
          if (data.user.avatar) {
            setUserAvatar(data.user.avatar);
          }
        }
        setStep('profile');
      } else {
        setCodeError(data.message || (isArabic ? 'كلمة المرور غير صحيحة' : 'Invalid password'));
      }
    } catch {
      setCodeError(isArabic ? 'خطأ في الاتصال أثناء التحقق' : 'Network error');
    } finally {
      setIsLoading(false);
    }
  };

  // Handle Resend Code (SMS vs In-App)
  const handleResend = async (type: DeliveryType) => {
    setIsLoading(true);
    setDeliveryType(type);
    setCodeError('');
    try {
      const resp = await fetch('/api/telegram/auth/resend-code', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          phone: fullPhoneNumber,
          phoneCodeHash,
          deliveryType: type,
        }),
      });
      const data = await resp.json();
      if (data.success) {
        setServiceNotification(data.serviceNotification || null);
        setTimerSeconds(60);
        setCanResend(false);
        showToast(data.message || (isArabic ? 'تمت إعادة إرسال الرمز' : 'Code resent'), '🔄');
      }
    } catch {
      showToast(isArabic ? 'خطأ في إعادة الإرسال' : 'Error resending code', '❌');
    } finally {
      setIsLoading(false);
    }
  };

  // Handle Code Input Box Change
  const handleDigitChange = (index: number, value: string) => {
    const clean = value.replace(/[^0-9]/g, '');
    
    // Handle pasting complete 5-digit code
    if (clean.length > 1) {
      const digits = clean.slice(0, 5).split('');
      const newDigits = [...codeDigits];
      digits.forEach((d, i) => {
        if (i < 5) newDigits[i] = d;
      });
      setCodeDigits(newDigits);
      if (digits.length === 5) {
        verifyCode(newDigits.join(''));
      }
      return;
    }

    const newDigits = [...codeDigits];
    newDigits[index] = clean;
    setCodeDigits(newDigits);

    // Auto-advance to next box
    if (clean && index < 4) {
      inputRefs.current[index + 1]?.focus();
    }

    // Auto-verify when 5 digits are filled
    if (newDigits.every((d) => d !== '')) {
      verifyCode(newDigits.join(''));
    }
  };

  // Handle Backspace navigation
  const handleKeyDown = (index: number, e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Backspace' && !codeDigits[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
  };

  // Verify Code Submission
  const verifyCode = async (enteredCode: string) => {
    setIsLoading(true);
    setCodeError('');

    try {
      const resp = await fetch('/api/telegram/auth/verify-code', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          phone: fullPhoneNumber,
          code: enteredCode,
          phoneCodeHash,
        }),
      });

      const data = await resp.json();

      if (data.success) {
        showToast(isArabic ? '✅ تم التحقق من الرمز بنجاح واكتمال المصادقة' : '✅ Code verified successfully', '🎉');
        if (data.sessionString) {
          setAccountSessionString(data.sessionString);
        }
        // Populate profile with real user details from Telegram if available
        if (data.user) {
          const fetchedName = [data.user.firstName, data.user.lastName].filter(Boolean).join(' ');
          setName(fetchedName || (isArabic ? `حساب (${selectedCountryCode})` : `Account (${selectedCountryCode})`));
          if (data.user.username) {
            setUsername(data.user.username);
          }
          if (data.user.avatar) {
            setUserAvatar(data.user.avatar);
          }
        } else {
          setName(isArabic ? `حساب (${selectedCountryCode})` : `Account (${selectedCountryCode})`);
        }
        setStep('profile');
      } else if (data.requiresPassword) {
        setRequires2FA(true);
        setCodeError(data.message || (isArabic ? 'يتطلب الحساب كلمة مرور التحقق بخطوتين (2FA)' : '2FA Password Required'));
      } else {
        setCodeError(data.message || (isArabic ? 'رمز التحقق غير صحيح' : 'Invalid code'));
        showToast(data.message || (isArabic ? 'رمز التحقق غير صحيح' : 'Invalid code'), '❌');
      }
    } catch {
      setCodeError(isArabic ? 'خطأ في الاتصال بالخادم أثناء التحقق' : 'Verification network error');
    } finally {
      setIsLoading(false);
    }
  };

  // Final Step: Complete Account Creation
  const handleFinalSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    setIsLoading(true);
    setTimeout(() => {
      addAccount({
        name: name.trim(),
        phone: fullPhoneNumber,
        username: username.trim(),
        avatar: userAvatar || selectedAvatar,
        bio: bio.trim(),
        sessionString: accountSessionString,
      });
      setIsLoading(false);
      setActiveModal('none');
    }, 400);
  };

  return (
    <AnimatePresence>
      <div
        id="add-account-modal-backdrop"
        className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-black/75 backdrop-blur-md select-none overflow-y-auto"
        onClick={() => setActiveModal('none')}
        dir={isArabic ? 'rtl' : 'ltr'}
      >
        <motion.div
          id="add-account-modal-container"
          initial={{ opacity: 0, scale: 0.95, y: 15 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 15 }}
          transition={{ duration: 0.2 }}
          onClick={(e) => e.stopPropagation()}
          className="w-full max-w-md bg-[#17212b] border border-[#2b394a] rounded-2xl shadow-2xl overflow-hidden flex flex-col my-auto text-white"
        >
          {/* Header with Step indicator */}
          <div className="flex items-center justify-between px-5 py-4 border-b border-[#242f3d] bg-[#242f3d]/70">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-[#5288c1]/20 flex items-center justify-center text-[#5288c1]">
                <UserPlus size={20} />
              </div>
              <div>
                <h3 className="text-base font-semibold text-white">
                  {step === 'phone'
                    ? isArabic ? 'تسجيل الدخول / إضافة حساب' : 'Log In / Add Account'
                    : step === 'code'
                    ? isArabic ? 'رمز التحقق (MTProto)' : 'Verification Code'
                    : isArabic ? 'إعداد الملف الشخصي' : 'Profile Setup'}
                </h3>
                <p className="text-xs text-gray-400">
                  {step === 'phone'
                    ? isArabic ? 'استلام كود التحقق عبر أجهزتك الأخرى أو SMS' : 'Receive code via active devices or SMS'
                    : step === 'code'
                    ? isArabic ? `تم الإرسال إلى ${fullPhoneNumber}` : `Sent to ${fullPhoneNumber}`
                    : isArabic ? 'اكتمل التحقق بنجاح' : 'Verification completed'}
                </p>
              </div>
            </div>
            <button
              id="btn-close-add-account-modal"
              onClick={() => setActiveModal('none')}
              className="p-1.5 text-gray-400 hover:text-white rounded-lg hover:bg-white/5 transition-colors"
            >
              <X size={18} />
            </button>
          </div>

          {/* Stepper Progress Bar */}
          <div className="grid grid-cols-3 h-1 bg-white/5">
            <div className={`h-full transition-all ${step === 'phone' ? 'bg-[#5288c1]' : 'bg-emerald-500'}`} />
            <div className={`h-full transition-all ${step === 'code' ? 'bg-[#5288c1]' : step === 'profile' ? 'bg-emerald-500' : 'bg-transparent'}`} />
            <div className={`h-full transition-all ${step === 'profile' ? 'bg-[#5288c1]' : 'bg-transparent'}`} />
          </div>

          {/* Body Content by Step */}
          <div className="p-5">
            {/* STEP 1: PHONE & DELIVERY CHANNEL */}
            {step === 'phone' && (
              <form onSubmit={(e) => handleRequestCode(e)} className="space-y-4">
                <div className="text-center py-2">
                  <div className="w-14 h-14 rounded-full bg-[#5288c1]/15 text-[#5288c1] flex items-center justify-center mx-auto mb-2 border border-[#5288c1]/30">
                    <Smartphone size={28} />
                  </div>
                  <h4 className="font-bold text-sm text-white">
                    {isArabic ? 'أدخل رقم هاتفك لاستلام رمز الدخول' : 'Enter phone to receive login code'}
                  </h4>
                  <p className="text-xs text-gray-400 mt-0.5">
                    {isArabic
                      ? 'سيصلك كود التحقق مباشرة إلى جهازك الآخر النشط أو عبر رسالة SMS'
                      : 'Code will arrive directly on your other active device or SMS'}
                  </p>
                </div>

                {/* Country Code & Phone Input */}
                <div className="space-y-1.5">
                  <label className="block text-xs font-semibold text-gray-300">
                    {isArabic ? 'الدولة ورقم الهاتف *' : 'Country & Phone Number *'}
                  </label>
                  <div className="flex gap-2">
                    {/* Country Selector */}
                    <select
                      value={selectedCountryCode}
                      onChange={(e) => setSelectedCountryCode(e.target.value)}
                      className="bg-[#0e1621] border border-[#2b394a] focus:border-[#5288c1] text-white text-xs rounded-xl px-2.5 py-2.5 outline-none font-mono max-w-[140px] sm:max-w-[180px]"
                    >
                      {COUNTRIES.map((c) => (
                        <option key={c.iso || `${c.code}-${c.name}`} value={c.code} className="bg-[#17212b] text-white">
                          {c.flag} {c.code} ({isArabic ? c.nameAr : c.name})
                        </option>
                      ))}
                    </select>

                    {/* Phone Number Field */}
                    <div className="relative flex-1">
                      <input
                        type="tel"
                        required
                        dir="ltr"
                        value={rawPhone}
                        onChange={(e) => setRawPhone(e.target.value)}
                        placeholder="770 000 000"
                        className="w-full bg-[#0e1621] border border-[#2b394a] focus:border-[#5288c1] text-white text-sm rounded-xl py-2.5 px-3 outline-none font-mono text-left"
                      />
                    </div>
                  </div>
                </div>

                {/* Delivery Channel Selection (أين تريد استلام الرمز؟) */}
                <div className="space-y-2 pt-1">
                  <label className="block text-xs font-semibold text-gray-300">
                    {isArabic ? 'طريقة وصول رمز التحقق:' : 'Code Delivery Method:'}
                  </label>

                  <div className="space-y-1.5">
                    {/* Option 1: In-App Telegram Notification to other active devices (Recommended / Default) */}
                    <label
                      onClick={() => setDeliveryType('app')}
                      className={`flex items-start gap-3 p-3 rounded-xl border cursor-pointer transition-all ${
                        deliveryType === 'app'
                          ? 'bg-[#5288c1]/20 border-[#5288c1] text-white ring-1 ring-[#5288c1]/40'
                          : 'bg-[#0e1621] border-[#2b394a] text-gray-300 hover:bg-white/5'
                      }`}
                    >
                      <input
                        type="radio"
                        name="delivery"
                        checked={deliveryType === 'app'}
                        onChange={() => setDeliveryType('app')}
                        className="mt-0.5 text-[#5288c1] focus:ring-0"
                      />
                      <div className="flex-1 text-xs">
                        <div className="font-bold flex items-center gap-1.5 text-white">
                          <Smartphone size={14} className="text-[#5288c1]" />
                          <span>{isArabic ? 'إشعار تيليجرام للأجهزة الأخرى النشطة (فوري وموصى به)' : 'Telegram Notification to Active Devices'}</span>
                        </div>
                        <p className="text-gray-400 mt-0.5 leading-relaxed text-[11px]">
                          {isArabic
                            ? 'يصلك الرمز فوراً كرسالة خدمة رسمية من Telegram (777000) في جهازك الآخر المفتوح.'
                            : 'Receive code instantly from official Telegram (777000) on your other logged-in device.'}
                        </p>
                      </div>
                    </label>

                    {/* Option 2: SMS */}
                    <label
                      onClick={() => setDeliveryType('sms')}
                      className={`flex items-start gap-3 p-3 rounded-xl border cursor-pointer transition-all ${
                        deliveryType === 'sms'
                          ? 'bg-[#5288c1]/20 border-[#5288c1] text-white ring-1 ring-[#5288c1]/40'
                          : 'bg-[#0e1621] border-[#2b394a] text-gray-300 hover:bg-white/5'
                      }`}
                    >
                      <input
                        type="radio"
                        name="delivery"
                        checked={deliveryType === 'sms'}
                        onChange={() => setDeliveryType('sms')}
                        className="mt-0.5 text-[#5288c1] focus:ring-0"
                      />
                      <div className="flex-1 text-xs">
                        <div className="font-bold flex items-center gap-1.5 text-white">
                          <MessageSquare size={14} className="text-emerald-400" />
                          <span>{isArabic ? 'رسالة نصية قصيرة SMS' : 'SMS Text Message'}</span>
                        </div>
                        <p className="text-gray-400 mt-0.5 text-[11px]">
                          {isArabic
                            ? 'إرسال الرمز مباشرة إلى شريحة الهاتف SIM الخاصة بك.'
                            : 'Send verification code via SMS to your phone SIM.'}
                        </p>
                      </div>
                    </label>
                  </div>
                </div>

                {/* Submit button */}
                <div className="pt-2">
                  <button
                    type="submit"
                    disabled={isLoading || !rawPhone.trim()}
                    className="w-full flex items-center justify-center gap-2 py-3 bg-[#5288c1] hover:bg-[#4374a8] disabled:opacity-50 text-white text-sm font-bold rounded-xl shadow-lg shadow-[#5288c1]/25 transition-all"
                  >
                    {isLoading ? (
                      <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    ) : (
                      <>
                        <span>{isArabic ? 'طلب كود التحقق ⚡' : 'Request Verification Code'}</span>
                        {isArabic ? <ArrowLeft size={16} /> : <ArrowRight size={16} />}
                      </>
                    )}
                  </button>
                </div>
              </form>
            )}

            {/* STEP 2: CODE VERIFICATION INPUT & TELEGRAM NOTIFICATION */}
            {step === 'code' && (
              <div className="space-y-4">
                <div className="text-center py-1">
                  <div className="w-12 h-12 rounded-full bg-emerald-500/15 text-emerald-400 flex items-center justify-center mx-auto mb-2 border border-emerald-500/30">
                    <ShieldCheck size={26} />
                  </div>
                  <h4 className="font-bold text-sm text-white">
                    {isArabic ? 'أدخل رمز التحقق (5 أرقام)' : 'Enter 5-digit verification code'}
                  </h4>
                  <div className="text-xs text-gray-300 font-mono mt-0.5 flex items-center justify-center gap-1.5">
                    <span>{fullPhoneNumber}</span>
                    <button
                      onClick={() => setStep('phone')}
                      className="text-[#5288c1] hover:underline text-[11px] font-sans"
                    >
                      ({isArabic ? 'تعديل الرقم' : 'Edit'})
                    </button>
                  </div>
                  <p className="text-[11px] text-gray-400 mt-1">
                    {deliveryType === 'app'
                      ? isArabic
                        ? 'تم إرسال الرمز كإشعار خدمة تيليجرام الرسمي إلى جهازك الآخر النشط.'
                        : 'Sent via Telegram service notification to your active devices.'
                      : isArabic
                      ? 'تم إرسال الرمز عبر رسالة نصية قصيرة SMS.'
                      : 'Sent via SMS text message.'}
                  </p>
                </div>

                {/* 5-Box PIN Code Inputs */}
                <div className="flex justify-center gap-2.5 my-3" dir="ltr">
                  {codeDigits.map((digit, idx) => (
                    <input
                      key={idx}
                      ref={(el) => {
                        inputRefs.current[idx] = el;
                      }}
                      type="text"
                      inputMode="numeric"
                      maxLength={1}
                      value={digit}
                      onChange={(e) => handleDigitChange(idx, e.target.value)}
                      onKeyDown={(e) => handleKeyDown(idx, e)}
                      className={`w-11 h-13 sm:w-12 sm:h-14 text-center text-xl sm:text-2xl font-bold font-mono rounded-xl border outline-none transition-all ${
                        digit
                          ? 'bg-[#5288c1]/20 border-[#5288c1] text-white shadow-md shadow-[#5288c1]/20 ring-1 ring-[#5288c1]'
                          : 'bg-[#0e1621] border-[#2b394a] text-white focus:border-[#5288c1]'
                      } ${codeError ? 'border-rose-500 ring-rose-500/50' : ''}`}
                    />
                  ))}
                </div>

                {/* Error Message */}
                {codeError && (
                  <div className="flex items-center gap-1.5 p-2.5 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs justify-center">
                    <AlertCircle size={14} />
                    <span>{codeError}</span>
                  </div>
                )}

                {/* Official Telegram MTProto Notice Banner */}
                {isRealTelegram && (
                  <div className="p-3 rounded-xl bg-[#5288c1]/15 border border-[#5288c1]/40 text-xs space-y-1 text-right">
                    <div className="flex items-center gap-2 font-bold text-[#68a0dc]">
                      <Sparkles size={15} />
                      <span>{isArabic ? 'تم الإرسال لجهازك الآخر ولبريدك الإلكتروني معاً' : 'Delivered to other device & email'}</span>
                    </div>
                    <p className="text-gray-300 text-[11px] leading-relaxed">
                      {isArabic
                        ? 'يصلك الرمز الآن كإشعار خدمة رسمي من Telegram (777000) في تطبيق تيليجرام على أجهزتك الأخرى، ومترافقاً فوراً إلى بريدك الإلكتروني (anwrfwad178@gmail.com) بشكل دائم.'
                        : 'Your code is delivered instantly to your other Telegram device (777000) and simultaneously to your email (anwrfwad178@gmail.com).'}
                    </p>
                  </div>
                )}

                {/* 2FA Password Field if Required */}
                {requires2FA && (
                  <div className="p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/30 text-xs space-y-2.5">
                    <div className="font-bold text-amber-400 flex items-center gap-1.5">
                      <ShieldCheck size={16} />
                      <span>{isArabic ? 'كلمة مرور التحقق بخطوتين (2FA)' : '2-Step Verification Password'}</span>
                    </div>
                    <div className="flex gap-2">
                      <input
                        type="password"
                        placeholder={isArabic ? 'أدخل كلمة مرور الحساب...' : 'Enter your 2FA password...'}
                        value={twoFaPassword}
                        onChange={(e) => setTwoFaPassword(e.target.value)}
                        className="flex-1 bg-[#0e1621] border border-amber-500/40 rounded-xl px-3 py-2 text-white text-xs outline-none focus:border-amber-400"
                      />
                      <button
                        type="button"
                        onClick={handleVerify2FA}
                        disabled={isLoading || !twoFaPassword.trim()}
                        className="px-4 py-2 bg-amber-500 hover:bg-amber-600 disabled:opacity-50 text-black font-bold text-xs rounded-xl shadow transition-all flex items-center gap-1"
                      >
                        {isLoading ? <RotateCw size={13} className="animate-spin" /> : null}
                        <span>{isArabic ? 'تأكيد' : 'Verify'}</span>
                      </button>
                    </div>
                  </div>
                )}

                {/* Resend Actions & Countdown Timer */}
                <div className="pt-2 space-y-2 border-t border-white/10">
                  <div className="flex items-center justify-between text-xs text-gray-400">
                    <span className="flex items-center gap-1">
                      <Clock size={14} />
                      <span>{canResend ? (isArabic ? 'يمكنك إعادة الإرسال الآن' : 'You can resend now') : (isArabic ? `إعادة الإرسال بعد: ${timerSeconds} ثانية` : `Resend in: ${timerSeconds}s`)}</span>
                    </span>

                    <button
                      type="button"
                      disabled={!canResend || isLoading}
                      onClick={() => handleResend(deliveryType === 'app' ? 'sms' : 'app')}
                      className="text-[#5288c1] hover:underline font-semibold disabled:opacity-40 disabled:hover:no-underline flex items-center gap-1"
                    >
                      <RotateCw size={13} className={isLoading ? 'animate-spin' : ''} />
                      <span>
                        {deliveryType === 'app'
                          ? isArabic ? 'إرسال الرمز عبر رسالة SMS' : 'Send code via SMS'
                          : isArabic ? 'إرسال كإشعار إلى أجهزتي الأخرى' : 'Send to other devices'}
                      </span>
                    </button>
                  </div>

                  <div className="flex gap-2 pt-1">
                    <button
                      type="button"
                      onClick={() => setStep('phone')}
                      className="flex-1 py-2.5 rounded-xl border border-white/10 hover:bg-white/5 text-xs text-gray-300 transition-colors"
                    >
                      {isArabic ? 'رجوع لتغيير الرقم' : 'Back'}
                    </button>
                    <button
                      type="button"
                      disabled={isLoading || codeDigits.some((d) => !d)}
                      onClick={() => verifyCode(codeDigits.join(''))}
                      className="flex-1 py-2.5 bg-[#5288c1] hover:bg-[#4374a8] disabled:opacity-50 text-white text-xs font-bold rounded-xl shadow transition-all flex items-center justify-center gap-1.5"
                    >
                      {isLoading ? (
                        <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      ) : (
                        <>
                          <Check size={14} />
                          <span>{isArabic ? 'تأكيد الرمز' : 'Verify'}</span>
                        </>
                      )}
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* STEP 3: PROFILE SETUP & ACCOUNT ACTIVATION */}
            {step === 'profile' && (
              <form onSubmit={handleFinalSubmit} className="space-y-4">
                <div className="text-center py-1">
                  <div className="w-12 h-12 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center mx-auto mb-1 border border-emerald-500/30">
                    <Check size={24} />
                  </div>
                  <h4 className="font-bold text-sm text-white">
                    {isArabic ? 'تم تأكيد الرقم بنجاح!' : 'Phone verified successfully!'}
                  </h4>
                  <p className="text-xs text-gray-400">
                    {isArabic ? 'أكمل بيانات الحساب الشخصية للانتقال فوراً' : 'Complete profile info to switch account'}
                  </p>
                </div>

                {/* Avatar Selector */}
                <div>
                  <label className="block text-xs font-medium text-gray-300 mb-2">
                    {isArabic ? 'اختر صورة الحساب الشخصية' : 'Choose Account Avatar'}
                  </label>
                  <div className="flex items-center gap-2 overflow-x-auto pb-1">
                    {AVATAR_PRESETS.map((preset) => (
                      <button
                        key={preset.id}
                        type="button"
                        onClick={() => setSelectedAvatar(preset.id)}
                        className={`relative w-11 h-11 rounded-full bg-gradient-to-tr ${preset.color} flex items-center justify-center flex-shrink-0 transition-transform ${
                          selectedAvatar === preset.id
                            ? 'border-2 border-white scale-110 ring-2 ring-[#5288c1]/60'
                            : 'border border-white/20 opacity-80 hover:opacity-100'
                        }`}
                      >
                        <span className="text-sm select-none">{preset.icon}</span>
                        {selectedAvatar === preset.id && (
                          <div className="absolute inset-0 bg-black/30 rounded-full flex items-center justify-center">
                            <Check size={14} className="text-white" />
                          </div>
                        )}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Name */}
                <div>
                  <label className="block text-xs font-medium text-gray-300 mb-1.5">
                    {isArabic ? 'الاسم الكامل *' : 'Full Name *'}
                  </label>
                  <div className="relative">
                    <span className="absolute inset-y-0 start-0 flex items-center ps-3 text-gray-400 pointer-events-none">
                      <UserIcon size={16} />
                    </span>
                    <input
                      type="text"
                      required
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      placeholder={isArabic ? 'مثال: أنور فؤاد' : 'e.g. Anwar Fouad'}
                      className="w-full bg-[#0e1621] border border-[#2b394a] focus:border-[#5288c1] text-white text-sm rounded-xl py-2.5 ps-10 pe-4 outline-none transition-colors"
                    >
                    </input>
                  </div>
                </div>

                {/* Username */}
                <div>
                  <label className="block text-xs font-medium text-gray-300 mb-1.5">
                    {isArabic ? 'اسم المستخدم (اختياري)' : 'Username (Optional)'}
                  </label>
                  <div className="relative">
                    <span className="absolute inset-y-0 start-0 flex items-center ps-3 text-gray-400 pointer-events-none">
                      <AtSign size={16} />
                    </span>
                    <input
                      type="text"
                      dir="ltr"
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                      placeholder="username"
                      className="w-full bg-[#0e1621] border border-[#2b394a] focus:border-[#5288c1] text-white text-sm rounded-xl py-2.5 ps-10 pe-4 outline-none transition-colors text-left"
                    />
                  </div>
                </div>

                {/* Bio */}
                <div>
                  <label className="block text-xs font-medium text-gray-300 mb-1.5">
                    {isArabic ? 'النبذة التعريفية (Bio)' : 'Bio'}
                  </label>
                  <div className="relative">
                    <span className="absolute top-3 start-0 flex items-center ps-3 text-gray-400 pointer-events-none">
                      <FileText size={16} />
                    </span>
                    <textarea
                      rows={2}
                      value={bio}
                      onChange={(e) => setBio(e.target.value)}
                      placeholder={isArabic ? 'نبذة قصيرة...' : 'Short bio...'}
                      className="w-full bg-[#0e1621] border border-[#2b394a] focus:border-[#5288c1] text-white text-sm rounded-xl py-2.5 ps-10 pe-4 outline-none transition-colors resize-none"
                    />
                  </div>
                </div>

                {/* Security Token Status */}
                <div className="flex items-center gap-2 p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-xs text-emerald-400">
                  <ShieldCheck size={16} className="shrink-0" />
                  <span>
                    {isArabic
                      ? 'تم توليد مفتاح AuthKey مشفر وجلسة MTProto 2.0 آمنة بنجاح.'
                      : 'Encrypted AuthKey & MTProto 2.0 session generated securely.'}
                  </span>
                </div>

                {/* Submit Action */}
                <div className="pt-2">
                  <button
                    type="submit"
                    disabled={isLoading || !name.trim()}
                    className="w-full flex items-center justify-center gap-2 py-3 bg-[#5288c1] hover:bg-[#4374a8] disabled:opacity-50 text-white text-sm font-bold rounded-xl shadow-lg shadow-[#5288c1]/25 transition-all"
                  >
                    {isLoading ? (
                      <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    ) : (
                      <>
                        <Sparkles size={16} />
                        <span>{isArabic ? 'حفظ الحساب والتنقل الفوري 🚀' : 'Save & Switch Account'}</span>
                      </>
                    )}
                  </button>
                </div>
              </form>
            )}
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
};
