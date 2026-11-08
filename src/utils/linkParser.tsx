/**
 * linkParser.ts - Official Telegram Message Entities, UTF-16 offset/length parsing,
 * link security verification, deep links & interactive text formatter.
 */

import React, { useState } from 'react';
import { LinkPreviewData, MessageEntity } from '../types';

export interface ParsedLinkResult {
  type:
    | 'telegram_invite'
    | 'telegram_username'
    | 'telegram_scheme'
    | 'external_url'
    | 'external_text_url'
    | 'bot_command'
    | 'other';
  value: string;
  display?: string;
  isHiddenUrl?: boolean;
  botStartParam?: string;
}

/**
 * Official Telegram Whitelisted Domains
 * Telegram skips the external hidden URL warning confirmation for these domains.
 */
export const TELEGRAM_WHITELISTED_DOMAINS = [
  'telegram.org',
  't.me',
  'telegram.me',
  'telegram.dog',
  'telegra.ph',
  'telesco.pe',
];

/**
 * Checks if a destination URL belongs to Telegram's trusted whitelist
 */
export function isWhitelistedTelegramDomain(urlString: string): boolean {
  try {
    const parsed = new URL(urlString.startsWith('http') ? urlString : `https://${urlString}`);
    const host = parsed.hostname.toLowerCase();
    return TELEGRAM_WHITELISTED_DOMAINS.some(
      (domain) => host === domain || host.endsWith(`.${domain}`)
    );
  } catch {
    return false;
  }
}

/**
 * Reserved Telegram URI paths that are not usernames
 */
export const TELEGRAM_RESERVED_PATHS = new Set([
  'addstickers',
  'joinchat',
  'addtheme',
  'share',
  'login',
  'setlanguage',
  'socks',
  'proxy',
  'confirmphone',
  'invoice',
  'bg',
  'c',
  's',
]);

/**
 * Parses official Telegram Deep Links:
 * Supports:
 * - t.me/<username>
 * - t.me/<username>?start=<param>
 * - t.me/+<invite_hash>
 * - t.me/joinchat/<invite_hash>
 * - tg://resolve?domain=<username>&start=<param>
 * - tg://join?invite=<invite_hash>
 * 
 * Note: Following Telegram MTProto specification, the `#fragment` is always ignored.
 */
export function parseTelegramDeepLink(rawLink: string): {
  isTelegramLink: boolean;
  kind?: 'username' | 'invite' | 'bot_start' | 'reserved' | 'external';
  target?: string;
  startParam?: string;
  cleanUrl: string;
} {
  if (!rawLink) {
    return { isTelegramLink: false, cleanUrl: '' };
  }

  // Strip fragment (#fragment is always ignored in Telegram deep link processing)
  const noFragment = rawLink.split('#')[0].trim();

  // 1. tg:// scheme
  if (noFragment.startsWith('tg://')) {
    try {
      const url = new URL(noFragment);
      const action = url.hostname || url.pathname.replace(/^\/\//, '');
      const searchParams = url.searchParams;

      if (action === 'resolve' || action.includes('resolve')) {
        const domain = searchParams.get('domain') || '';
        const start = searchParams.get('start') || undefined;
        if (domain) {
          return {
            isTelegramLink: true,
            kind: start ? 'bot_start' : 'username',
            target: domain,
            startParam: start,
            cleanUrl: noFragment,
          };
        }
      }

      if (action === 'join' || action.includes('join')) {
        const invite = searchParams.get('invite') || '';
        return {
          isTelegramLink: true,
          kind: 'invite',
          target: invite,
          cleanUrl: noFragment,
        };
      }
    } catch {}
  }

  // 2. t.me / telegram.me links
  const tmeMatch = noFragment.match(/^(?:https?:\/\/)?(?:www\.)?(?:t\.me|telegram\.me)\/(.+)$/i);
  if (tmeMatch) {
    const pathAndQuery = tmeMatch[1];
    const [pathPart, queryPart] = pathAndQuery.split('?');
    const params = new URLSearchParams(queryPart || '');

    // Private invite link: t.me/+<hash> or t.me/joinchat/<hash>
    if (pathPart.startsWith('+')) {
      return {
        isTelegramLink: true,
        kind: 'invite',
        target: pathPart.slice(1),
        cleanUrl: noFragment,
      };
    }
    if (pathPart.startsWith('joinchat/')) {
      return {
        isTelegramLink: true,
        kind: 'invite',
        target: pathPart.replace('joinchat/', ''),
        cleanUrl: noFragment,
      };
    }

    const segments = pathPart.split('/').filter(Boolean);
    const firstSegment = segments[0];

    if (!firstSegment) {
      return { isTelegramLink: true, kind: 'reserved', cleanUrl: noFragment };
    }

    if (TELEGRAM_RESERVED_PATHS.has(firstSegment.toLowerCase())) {
      return { isTelegramLink: true, kind: 'reserved', target: firstSegment, cleanUrl: noFragment };
    }

    const startParam = params.get('start') || undefined;
    return {
      isTelegramLink: true,
      kind: startParam ? 'bot_start' : 'username',
      target: firstSegment,
      startParam,
      cleanUrl: noFragment,
    };
  }

  return { isTelegramLink: false, kind: 'external', cleanUrl: noFragment };
}

/**
 * Extracts preview information from text
 */
export function extractLinkPreview(text: string): LinkPreviewData | null {
  const urlMatch = text.match(/https?:\/\/[^\s]+/);
  if (!urlMatch) return null;
  const url = urlMatch[0];

  const deep = parseTelegramDeepLink(url);
  if (deep.isTelegramLink) {
    if (deep.kind === 'invite') {
      return {
        url,
        displayUrl: `t.me/+${deep.target || ''}`,
        title: 'Telegram Invite Link',
        description: 'Join this chat via official Telegram MTProto invitation.',
        siteName: 'Telegram',
        type: 'telegram_invite',
      };
    }
    if (deep.kind === 'username' || deep.kind === 'bot_start') {
      return {
        url,
        displayUrl: `t.me/${deep.target || ''}`,
        title: `@${deep.target}`,
        description: `Telegram Channel / Group / User @${deep.target}`,
        siteName: 'Telegram',
        type: 'telegram_channel',
        channelUsername: deep.target,
      };
    }
  }

  let hostname = 'Web';
  try {
    hostname = new URL(url).hostname;
  } catch {}

  return {
    url,
    displayUrl: url,
    title: url,
    description: '',
    siteName: hostname,
  };
}

export function isOnlyBigEmojis(text?: string): { isBig: boolean; emojis: string[] } {
  if (!text) return { isBig: false, emojis: [] };
  const trimmed = text.trim();
  const emojiRegex = /^(\p{Extended_Pictographic}|\p{Emoji_Presentation}){1,3}$/u;
  if (emojiRegex.test(trimmed)) {
    return { isBig: true, emojis: Array.from(trimmed) };
  }
  return { isBig: false, emojis: [] };
}

export function renderBigAnimatedEmojis(emojis: string[]): React.ReactNode {
  return React.createElement(
    'span',
    { className: 'text-4xl leading-relaxed select-none' },
    emojis.join(' ')
  );
}

/**
 * Automatically extracts Message Entities according to Telegram UTF-16 specifications
 * when no raw MTProto entities are attached to the message.
 */
export function autoExtractEntities(text: string): MessageEntity[] {
  if (!text) return [];
  const entities: MessageEntity[] = [];

  // URLs (messageEntityUrl)
  const urlRegex = /https?:\/\/[^\s<>"'{}|\\^`]+/g;
  let match: RegExpExecArray | null;
  while ((match = urlRegex.exec(text)) !== null) {
    entities.push({
      type: 'messageEntityUrl',
      offset: match.index,
      length: match[0].length,
    });
  }

  // Mentions (@username)
  const mentionRegex = /(?<=^|\s)@[a-zA-Z0-9_]{3,32}\b/g;
  while ((match = mentionRegex.exec(text)) !== null) {
    entities.push({
      type: 'messageEntityMention',
      offset: match.index,
      length: match[0].length,
    });
  }

  // Hashtags (#tag)
  const hashtagRegex = /(?<=^|\s)#[a-zA-Z0-9_\u0600-\u06FF]{2,64}\b/g;
  while ((match = hashtagRegex.exec(text)) !== null) {
    entities.push({
      type: 'messageEntityHashtag',
      offset: match.index,
      length: match[0].length,
    });
  }

  // Bot commands (/command)
  const cmdRegex = /(?<=^|\s)\/[a-zA-Z0-9_]{1,32}\b/g;
  while ((match = cmdRegex.exec(text)) !== null) {
    entities.push({
      type: 'messageEntityBotCommand',
      offset: match.index,
      length: match[0].length,
    });
  }

  // Markdown links: [title](url) -> messageEntityTextUrl
  const markdownLinkRegex = /\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g;
  while ((match = markdownLinkRegex.exec(text)) !== null) {
    // Note: for pure MTProto, text is rendered as title, but if raw text is markdown:
    entities.push({
      type: 'messageEntityTextUrl',
      offset: match.index,
      length: match[0].length,
      url: match[2],
    });
  }

  // Sort entities by offset ascending
  return entities.sort((a, b) => a.offset - b.offset);
}

/**
 * Interactive Spoiler Component for Telegram Spoilers
 */
export const TelegramSpoiler: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [revealed, setRevealed] = useState(false);
  return (
    <span
      onClick={(e) => {
        e.stopPropagation();
        setRevealed(true);
      }}
      className={`relative inline rounded px-1 transition-all cursor-pointer ${
        revealed
          ? 'bg-white/10'
          : 'bg-white/20 text-transparent select-none blur-[3px] hover:bg-white/30'
      }`}
      title={revealed ? undefined : 'اضغط لإظهار النص المخفي (Spoiler)'}
    >
      {children}
    </span>
  );
};

/**
 * Official Telegram Interactive Text Renderer using UTF-16 Message Entities:
 * Handles:
 * - messageEntityUrl
 * - messageEntityTextUrl (hidden link with target url confirmation check)
 * - messageEntityMention
 * - messageEntityHashtag
 * - messageEntityBotCommand
 * - messageEntityBold / Italic / Code / Pre / Underline / Strike / Spoiler
 */
export function renderInteractiveMessageText(
  text: string,
  onLinkClick?: (link: ParsedLinkResult) => void,
  providedEntities?: MessageEntity[]
): React.ReactNode {
  if (!text) return null;

  // If no entities provided, auto-extract
  const entities =
    providedEntities && providedEntities.length > 0
      ? [...providedEntities].sort((a, b) => a.offset - b.offset)
      : autoExtractEntities(text);

  if (entities.length === 0) {
    return text;
  }

  const nodes: React.ReactNode[] = [];
  let currentOffset = 0;
  const textLength = text.length; // UTF-16 code units length in JS

  for (let i = 0; i < entities.length; i++) {
    const entity = entities[i];
    const { offset, length, type } = entity;

    // Safety bounds
    if (offset < currentOffset || offset >= textLength) {
      continue;
    }

    // Normal plain text preceding this entity
    if (offset > currentOffset) {
      nodes.push(text.substring(currentOffset, offset));
    }

    const entityEnd = Math.min(offset + length, textLength);
    const rawContent = text.substring(offset, entityEnd);
    const key = `ent_${i}_${offset}`;

    switch (type) {
      case 'messageEntityUrl': {
        const cleanLink = rawContent.trim();
        nodes.push(
          React.createElement(
            'span',
            {
              key,
              onClick: (e: React.MouseEvent) => {
                e.stopPropagation();
                const deep = parseTelegramDeepLink(cleanLink);
                if (deep.isTelegramLink) {
                  if (deep.kind === 'invite') {
                    onLinkClick?.({ type: 'telegram_invite', value: deep.cleanUrl });
                  } else {
                    onLinkClick?.({
                      type: 'telegram_username',
                      value: deep.target || cleanLink,
                      botStartParam: deep.startParam,
                    });
                  }
                } else {
                  onLinkClick?.({
                    type: 'external_url',
                    value: cleanLink,
                    display: cleanLink,
                    isHiddenUrl: false,
                  });
                }
              },
              className:
                'text-[#2481cc] hover:underline cursor-pointer font-medium break-all select-text',
            },
            rawContent
          )
        );
        break;
      }

      case 'messageEntityTextUrl': {
        const destinationUrl = entity.url || rawContent;
        // Check if destination domain is in Telegram whitelist
        const isWhitelisted = isWhitelistedTelegramDomain(destinationUrl);

        nodes.push(
          React.createElement(
            'span',
            {
              key,
              onClick: (e: React.MouseEvent) => {
                e.stopPropagation();
                onLinkClick?.({
                  type: 'external_text_url',
                  value: destinationUrl,
                  display: rawContent,
                  isHiddenUrl: !isWhitelisted, // requires confirmation if not whitelisted!
                });
              },
              className:
                'text-[#2481cc] hover:underline cursor-pointer font-medium underline decoration-sky-400/50 select-text',
              title: isWhitelisted ? destinationUrl : `رابط خارجي: ${destinationUrl}`,
            },
            rawContent
          )
        );
        break;
      }

      case 'messageEntityMention': {
        const cleanMention = rawContent.trim().replace(/^@/, '');
        nodes.push(
          React.createElement(
            'span',
            {
              key,
              onClick: (e: React.MouseEvent) => {
                e.stopPropagation();
                onLinkClick?.({
                  type: 'telegram_username',
                  value: cleanMention,
                  display: rawContent,
                });
              },
              className: 'text-[#2481cc] hover:underline cursor-pointer font-medium',
            },
            rawContent
          )
        );
        break;
      }

      case 'messageEntityHashtag': {
        nodes.push(
          React.createElement(
            'span',
            {
              key,
              onClick: (e: React.MouseEvent) => {
                e.stopPropagation();
                onLinkClick?.({
                  type: 'other',
                  value: rawContent,
                  display: rawContent,
                });
              },
              className: 'text-[#2481cc] hover:underline cursor-pointer',
            },
            rawContent
          )
        );
        break;
      }

      case 'messageEntityBotCommand': {
        nodes.push(
          React.createElement(
            'span',
            {
              key,
              onClick: (e: React.MouseEvent) => {
                e.stopPropagation();
                onLinkClick?.({
                  type: 'bot_command',
                  value: rawContent,
                  display: rawContent,
                });
              },
              className: 'text-[#2481cc] hover:underline cursor-pointer font-mono font-medium',
            },
            rawContent
          )
        );
        break;
      }

      case 'messageEntityBold': {
        nodes.push(
          React.createElement('strong', { key, className: 'font-bold text-white' }, rawContent)
        );
        break;
      }

      case 'messageEntityItalic': {
        nodes.push(React.createElement('em', { key, className: 'italic' }, rawContent));
        break;
      }

      case 'messageEntityCode': {
        nodes.push(
          React.createElement(
            'code',
            {
              key,
              className:
                'px-1.5 py-0.5 rounded bg-black/25 text-amber-300 font-mono text-xs select-text',
            },
            rawContent
          )
        );
        break;
      }

      case 'messageEntityPre': {
        nodes.push(
          React.createElement(
            'pre',
            {
              key,
              className:
                'my-1 p-2 rounded bg-black/35 text-sky-200 font-mono text-xs overflow-x-auto select-text',
            },
            rawContent
          )
        );
        break;
      }

      case 'messageEntityUnderline': {
        nodes.push(React.createElement('u', { key, className: 'underline' }, rawContent));
        break;
      }

      case 'messageEntityStrike': {
        nodes.push(React.createElement('s', { key, className: 'line-through opacity-80' }, rawContent));
        break;
      }

      case 'messageEntitySpoiler': {
        nodes.push(
          <TelegramSpoiler key={key}>{rawContent}</TelegramSpoiler>
        );
        break;
      }

      default: {
        nodes.push(rawContent);
      }
    }

    currentOffset = entityEnd;
  }

  // Trailing plain text
  if (currentOffset < textLength) {
    nodes.push(text.substring(currentOffset));
  }

  return nodes;
}
