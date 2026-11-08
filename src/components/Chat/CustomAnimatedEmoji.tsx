import React, { useState } from 'react';
import { Lottie } from 'lottie-react';
import { CUSTOM_EMOJIS_MAP, CustomEmojiItem } from '../../data/lottieStickerData';

interface CustomAnimatedEmojiProps {
  code: string;
  size?: number;
  inline?: boolean;
  onClick?: () => void;
  className?: string;
}

export const CustomAnimatedEmoji: React.FC<CustomAnimatedEmojiProps> = ({
  code,
  size = 22,
  inline = true,
  onClick,
  className = '',
}) => {
  const [isHovered, setIsHovered] = useState(false);
  const emojiData: CustomEmojiItem | undefined = CUSTOM_EMOJIS_MAP[code];

  if (!emojiData) {
    // Fallback if not recognized as custom emoji code
    return <span className={className}>{code}</span>;
  }

  const dimension = inline ? size : size * 1.8;

  return (
    <span
      id={`custom-emoji-${code.replace(/:/g, '')}`}
      onClick={onClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className={`relative inline-flex items-center justify-center align-middle mx-0.5 cursor-pointer select-none group/c-emoji transition-transform active:scale-90 ${
        isHovered ? 'scale-125 z-20' : 'scale-100'
      } ${className}`}
      style={{
        width: dimension,
        height: dimension,
        minWidth: dimension,
        minHeight: dimension,
      }}
      title={`${emojiData.name} • ${emojiData.packName}`}
    >
      {emojiData.lottieData ? (
        <span className="w-full h-full flex items-center justify-center pointer-events-none">
          <Lottie
            src={emojiData.lottieData}
            autoplay={true}
            loop={true}
            style={{ width: '100%', height: '100%' }}
          />
        </span>
      ) : (
        <span
          className="text-base leading-none drop-shadow-sm flex items-center justify-center"
          style={{ fontSize: dimension * 0.9 }}
        >
          {emojiData.svgIcon || emojiData.emojiFallback}
        </span>
      )}

      {/* Floating Tooltip displaying Custom Emoji Pack Info */}
      {isHovered && (
        <span className="absolute -top-7 left-1/2 -translate-x-1/2 bg-[#17212b] text-white text-[10px] px-2 py-0.5 rounded-md border border-[#2b394a] shadow-xl whitespace-nowrap pointer-events-none z-30 animate-in fade-in zoom-in-95 duration-100">
          <strong className="text-sky-400">{emojiData.name}</strong>
          <span className="opacity-60 text-[9px] ms-1">({emojiData.packName})</span>
        </span>
      )}
    </span>
  );
};
