import React, { useRef, useState } from 'react';
import { Lottie, LottieHandle } from 'lottie-react';
import { Sparkles } from 'lucide-react';
import {
  ANIMATED_TELEGRAM_STICKERS,
  LOTTIE_TON_GEM,
  LOTTIE_DUCK_WINK,
  LOTTIE_HEART_PULSE,
  LOTTIE_FIRE_FLAME,
  LOTTIE_PARTY_POPPER,
  LOTTIE_ROCKET_BOOST,
} from '../../data/lottieStickerData';

interface LottieStickerProps {
  lottieData?: any;
  stickerId?: string;
  url?: string;
  size?: number;
  autoplay?: boolean;
  loop?: boolean;
  className?: string;
  onClick?: () => void;
  showBadge?: boolean;
}

const STICKER_DATA_LOOKUP: Record<string, any> = {
  tg_st_duck_wink: LOTTIE_DUCK_WINK,
  tg_st_ton_gem: LOTTIE_TON_GEM,
  tg_st_heart_pulse: LOTTIE_HEART_PULSE,
  tg_st_fire_flame: LOTTIE_FIRE_FLAME,
  tg_st_party_popper: LOTTIE_PARTY_POPPER,
  tg_st_rocket_boost: LOTTIE_ROCKET_BOOST,
  st_duck_1: LOTTIE_DUCK_WINK,
  st_duck_2: LOTTIE_PARTY_POPPER,
  st_cat_1: LOTTIE_DUCK_WINK,
  st_cat_2: LOTTIE_HEART_PULSE,
  st_pepe_1: LOTTIE_TON_GEM,
  st_pepe_2: LOTTIE_FIRE_FLAME,
};

export const LottieSticker: React.FC<LottieStickerProps> = ({
  lottieData,
  stickerId,
  url,
  size = 140,
  autoplay = true,
  loop = true,
  className = '',
  onClick,
  showBadge = true,
}) => {
  const lottieRef = useRef<LottieHandle | null>(null);
  const [isHovered, setIsHovered] = useState(false);
  const [hasError, setHasError] = useState(false);

  // Resolve animation data
  const animationData =
    lottieData ||
    (stickerId ? STICKER_DATA_LOOKUP[stickerId] : null) ||
    (url && STICKER_DATA_LOOKUP[url]) ||
    LOTTIE_TON_GEM;

  const handleMouseEnter = () => {
    setIsHovered(true);
    if (lottieRef.current) {
      lottieRef.current.setSpeed(1.4);
      lottieRef.current.play();
    }
  };

  const handleMouseLeave = () => {
    setIsHovered(false);
    if (lottieRef.current) {
      lottieRef.current.setSpeed(1);
    }
  };

  const handleClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (lottieRef.current) {
      lottieRef.current.seek(0);
      lottieRef.current.play();
    }
    if (onClick) onClick();
  };

  return (
    <div
      id={`lottie-sticker-${stickerId || 'item'}`}
      onClick={handleClick}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      className={`relative inline-flex items-center justify-center cursor-pointer select-none transition-transform hover:scale-105 active:scale-95 ${className}`}
      style={{ width: size, height: size }}
      title="Telegram Animated Sticker (Lottie 60FPS)"
    >
      {!hasError && animationData ? (
        <Lottie
          lottieRef={lottieRef}
          src={animationData}
          autoplay={autoplay}
          loop={loop}
          style={{ width: '100%', height: '100%' }}
          onError={() => setHasError(true)}
        />
      ) : url ? (
        <img
          src={url}
          alt="Sticker fallback"
          className="w-full h-full object-contain drop-shadow-md animate-in zoom-in-90 duration-200"
          referrerPolicy="no-referrer"
        />
      ) : (
        <div className="w-full h-full rounded-2xl bg-[#2481cc]/20 flex items-center justify-center text-3xl">
          💎
        </div>
      )}

      {/* Lottie Vector 60FPS Badge indicator on hover */}
      {showBadge && isHovered && (
        <div className="absolute -top-2 -right-2 bg-gradient-to-r from-[#2481cc] to-[#00b4d8] text-white text-[9px] font-bold px-1.5 py-0.5 rounded-full shadow-lg flex items-center gap-0.5 pointer-events-none animate-in zoom-in-75 duration-100">
          <Sparkles className="w-2.5 h-2.5" />
          <span>TGS 60FPS</span>
        </div>
      )}
    </div>
  );
};
