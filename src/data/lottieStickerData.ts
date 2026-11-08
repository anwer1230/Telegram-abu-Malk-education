/**
 * lottieStickerData.ts - Sticker & Animated Emoji Dataset
 */

export interface LottieStickerItem {
  id: string;
  name: string;
  nameAr?: string;
  packName?: string;
  emoji: string;
  lottieData?: any;
  previewUrl?: string;
}

export interface CustomEmojiItem {
  id: string;
  code: string;
  emoji: string;
  name: string;
  packName?: string;
  category?: string;
  lottieData?: any;
  svgIcon?: string;
  emojiFallback?: string;
}

export interface CustomEmojiSet {
  packId: string;
  packName: string;
  packNameAr: string;
  icon: string;
  emojis: CustomEmojiItem[];
}

export const LOTTIE_TON_GEM = null;
export const LOTTIE_DUCK_WINK = null;
export const LOTTIE_HEART_PULSE = null;
export const LOTTIE_FIRE_FLAME = null;
export const LOTTIE_PARTY_POPPER = null;
export const LOTTIE_ROCKET_BOOST = null;

export const ANIMATED_TELEGRAM_STICKERS: LottieStickerItem[] = [
  { id: 'duck_wink', name: 'Duck Wink', nameAr: 'بطة تغمز', packName: 'Animated Duck', emoji: '😉', previewUrl: 'https://telegram.org/img/t_logo.png' },
  { id: 'heart_pulse', name: 'Heart', nameAr: 'قلب ينبض', packName: 'Animated Hearts', emoji: '❤️', previewUrl: 'https://telegram.org/img/t_logo.png' },
  { id: 'fire_flame', name: 'Fire', nameAr: 'شعلة نار', packName: 'Telegram Fire', emoji: '🔥', previewUrl: 'https://telegram.org/img/t_logo.png' },
  { id: 'party_popper', name: 'Party', nameAr: 'احتفال', packName: 'Party Pack', emoji: '🎉', previewUrl: 'https://telegram.org/img/t_logo.png' },
  { id: 'rocket_boost', name: 'Rocket', nameAr: 'صاروخ', packName: 'Space Rocket', emoji: '🚀', previewUrl: 'https://telegram.org/img/t_logo.png' },
];

export const TELEGRAM_CUSTOM_EMOJI_SETS: CustomEmojiSet[] = [
  {
    packId: 'pack_premium',
    packName: 'Telegram Premium',
    packNameAr: 'تيليجرام بريميوم',
    icon: '⭐',
    emojis: [
      { id: 'e1', code: ':tg_star:', emoji: '🌟', name: 'Star', packName: 'Telegram Premium', emojiFallback: '🌟' },
      { id: 'e2', code: ':tg_gem:', emoji: '💎', name: 'Gem', packName: 'Telegram Premium', emojiFallback: '💎' },
      { id: 'e3', code: ':tg_fire:', emoji: '🔥', name: 'Fire', packName: 'Telegram Premium', emojiFallback: '🔥' },
      { id: 'e4', code: ':tg_crown:', emoji: '👑', name: 'Crown', packName: 'Telegram Premium', emojiFallback: '👑' },
    ],
  },
];

export const CUSTOM_EMOJIS_MAP: Record<string, CustomEmojiItem> = {
  ':tg_star:': { id: 'e1', code: ':tg_star:', emoji: '🌟', name: 'Star', packName: 'Telegram Premium', emojiFallback: '🌟' },
  ':tg_gem:': { id: 'e2', code: ':tg_gem:', emoji: '💎', name: 'Gem', packName: 'Telegram Premium', emojiFallback: '💎' },
  ':tg_fire:': { id: 'e3', code: ':tg_fire:', emoji: '🔥', name: 'Fire', packName: 'Telegram Premium', emojiFallback: '🔥' },
  ':tg_crown:': { id: 'e4', code: ':tg_crown:', emoji: '👑', name: 'Crown', packName: 'Telegram Premium', emojiFallback: '👑' },
};
