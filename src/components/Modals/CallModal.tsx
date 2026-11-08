import React, { useState, useEffect, useRef } from 'react';
import {
  PhoneOff,
  Mic,
  MicOff,
  Video,
  VideoOff,
  Shield,
  Volume2,
  Lock,
  Camera,
  RotateCcw,
  Sparkles,
} from 'lucide-react';
import { useTelegram } from '../../context/TelegramContext';

export const CallModal: React.FC = () => {
  const {
    activeModal,
    activeCall,
    endCall,
    toggleCallMute,
    toggleCallCamera,
    settings,
  } = useTelegram();

  const [localStream, setLocalStream] = useState<MediaStream | null>(null);
  const localVideoRef = useRef<HTMLVideoElement | null>(null);

  const isArabic = settings.language === 'ar';

  useEffect(() => {
    if (activeModal === 'call' && activeCall?.isVideo && !activeCall.isCameraOff) {
      navigator.mediaDevices
        ?.getUserMedia({ video: true, audio: true })
        .then((stream) => {
          setLocalStream(stream);
          if (localVideoRef.current) {
            localVideoRef.current.srcObject = stream;
          }
        })
        .catch((err) => {
          console.warn('WebRTC camera preview error/permission skipped:', err);
        });
    } else {
      if (localStream) {
        localStream.getTracks().forEach((track) => track.stop());
        setLocalStream(null);
      }
    }

    return () => {
      if (localStream) {
        localStream.getTracks().forEach((track) => track.stop());
      }
    };
  }, [activeModal, activeCall?.isVideo, activeCall?.isCameraOff]);

  if (activeModal !== 'call' || !activeCall) return null;

  const formatDuration = (secs: number) => {
    const m = Math.floor(secs / 60);
    const s = Math.floor(secs % 60);
    return `${m}:${s < 10 ? '0' : ''}${s}`;
  };

  return (
    <div
      id="modal-telegram-webrtc-call"
      className="fixed inset-0 z-[9999] flex items-center justify-center p-3 sm:p-4 select-none"
    >
      {/* Backdrop */}
      <div className="fixed inset-0 bg-gradient-to-b from-[#0b141d]/90 via-[#101b26]/95 to-[#070c12] backdrop-blur-xl animate-in fade-in duration-200" />

      {/* Main Call Container */}
      <div className="relative w-full max-w-md h-[580px] max-h-[92vh] rounded-3xl flex flex-col justify-between p-6 shadow-2xl z-10 border border-white/10 text-white overflow-hidden bg-black/40 backdrop-blur-xl">
        {/* WebRTC Video Background Stream if Active */}
        {activeCall.isVideo && !activeCall.isCameraOff && (
          <div className="absolute inset-0 z-0 overflow-hidden">
            <video
              ref={localVideoRef}
              autoPlay
              playsInline
              muted
              className="w-full h-full object-cover scale-x-[-1] opacity-70"
            />
            <div className="absolute inset-0 bg-gradient-to-b from-black/60 via-transparent to-black/80" />
          </div>
        )}

        {/* Top Bar: E2E 4-Emoji Verification Key (DrKLO Protocol) */}
        <div className="relative z-10 flex flex-col items-center gap-1.5">
          <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/10 border border-white/10 backdrop-blur-md">
            <Lock className="w-3.5 h-3.5 text-emerald-400" />
            <div className="flex items-center gap-2 text-lg tracking-wider">
              {activeCall.encryptionEmojis.map((emoji, i) => (
                <span key={i} className="hover:scale-125 transition-transform cursor-default">
                  {emoji}
                </span>
              ))}
            </div>
          </div>
          <span className="text-[10px] text-gray-300 text-center max-w-xs drop-shadow">
            {isArabic
              ? 'تشفير تام WebRTC E2E (تطابق الرموز التعبيرية الأربعة)'
              : 'WebRTC E2E Encrypted. If emojis match on both screens, call is 100% secure.'}
          </span>
        </div>

        {/* Center: Avatar & Ripple Animation */}
        <div className="relative z-10 flex flex-col items-center justify-center my-auto">
          {(!activeCall.isVideo || activeCall.isCameraOff) && (
            <div className="relative flex items-center justify-center">
              {/* Animated Pulses */}
              {activeCall.status === 'connected' && (
                <>
                  <div className="absolute w-36 h-36 rounded-full bg-sky-500/20 animate-ping duration-1000" />
                  <div className="absolute w-48 h-48 rounded-full bg-sky-500/10 animate-pulse duration-700" />
                </>
              )}

              <div className="relative w-28 h-28 rounded-full overflow-hidden border-4 border-[#2481cc]/60 shadow-2xl z-10 bg-slate-800 flex items-center justify-center text-3xl font-bold">
                {activeCall.chatAvatar ? (
                  <img
                    src={activeCall.chatAvatar}
                    alt={activeCall.chatTitle}
                    className="w-full h-full object-cover"
                    referrerPolicy="no-referrer"
                  />
                ) : (
                  <span>{activeCall.chatTitle.charAt(0)}</span>
                )}
              </div>
            </div>
          )}

          <div className="font-bold text-xl mt-4 drop-shadow">{activeCall.chatTitle}</div>
          <div className="text-sm text-sky-400 font-medium mt-1 drop-shadow">
            {activeCall.status === 'calling'
              ? isArabic
                ? 'جارٍ الرنين والاتصال (Signaling)...'
                : 'Calling & Signaling...'
              : formatDuration(activeCall.duration)}
          </div>
          <div className="text-[11px] text-gray-300 mt-1 font-mono flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span>WebRTC P2P • Opus 48kHz • DC4</span>
          </div>
        </div>

        {/* Bottom Control Actions */}
        <div className="relative z-10 flex items-center justify-center gap-5 mt-auto">
          {/* Mute Button */}
          <button
            onClick={toggleCallMute}
            className={`w-13 h-13 rounded-full flex items-center justify-center transition-all shadow-lg active:scale-95 ${
              activeCall.isMuted
                ? 'bg-rose-500 text-white'
                : 'bg-white/20 hover:bg-white/30 text-white'
            }`}
            title={isArabic ? 'كتم الصوت' : 'Mute'}
          >
            {activeCall.isMuted ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
          </button>

          {/* End Call Button */}
          <button
            onClick={() => {
              if (localStream) {
                localStream.getTracks().forEach((track) => track.stop());
              }
              endCall();
            }}
            className="w-16 h-16 rounded-full bg-rose-600 hover:bg-rose-700 text-white flex items-center justify-center shadow-xl transition-all active:scale-90"
            title={isArabic ? 'إنهاء المكالمة' : 'End Call'}
          >
            <PhoneOff className="w-7 h-7" />
          </button>

          {/* Camera / Video Button */}
          <button
            onClick={toggleCallCamera}
            className={`w-13 h-13 rounded-full flex items-center justify-center transition-all shadow-lg active:scale-95 ${
              activeCall.isCameraOff
                ? 'bg-rose-500 text-white'
                : 'bg-white/20 hover:bg-white/30 text-white'
            }`}
            title={isArabic ? 'الكاميرا' : 'Camera'}
          >
            {activeCall.isCameraOff ? <VideoOff className="w-5 h-5" /> : <Video className="w-5 h-5" />}
          </button>
        </div>
      </div>
    </div>
  );
};
