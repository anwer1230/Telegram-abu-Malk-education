/**
 * TelegramBotEngine.ts
 * 
 * Official Telegram Bot Logic & MTProto Protocol Specification Implementation:
 * 1. MTProto & Bot API Bot Recognition:
 *    - user.bot: flags.14?true
 *    - user.bot_chat_history: flags.15?true (can_read_all_group_messages)
 *    - user.bot_nochats: flags.16?true (can_join_groups)
 *    - user.bot_inline_geo: flags.21?true
 *    - is_bot: true
 *    - Username validation (*bot)
 * 2. 7-Scope BotCommandScope Hierarchy & Resolution Engine:
 *    - default, all_private_chats, all_group_chats, all_chat_administrators, chat, chat_administrators, chat_member
 * 3. Group Privacy Mode (وضع الخصوصية) Rules & Message Routing:
 *    - /command@botname matching
 *    - Direct replies to bot messages
 *    - @mention detection
 *    - Admin override / Privacy Mode Disable
 * 4. Interactive Inline Queries (@BotName query) & Keyboards (Inline/Reply)
 */

import {
  BotEntity,
  BotCommand,
  BotCommandScope,
  BotCommandEntry,
  Chat,
  Message,
  User,
  InlineQueryResult,
} from '../types';

// Pre-registered official bots in the ecosystem
export const OFFICIAL_TELEGRAM_BOTS: Record<string, BotEntity> = {
  botfather: {
    id: 'user_botfather',
    name: 'BotFather',
    username: 'BotFather',
    avatar: 'https://images.unsplash.com/photo-1531746020798-e6953c6e8e04?w=150',
    token: '100000000:AAH_BotFatherMasterRootKey',
    is_bot: true,
    flags: {
      bot: true,
      bot_chat_history: false,
      bot_nochats: false, // can be added to groups
      bot_info_version: 3,
      bot_inline_placeholder: 'Search bots...',
    },
    privacyMode: true,
    can_read_all_group_messages: false,
    can_join_groups: true,
    supports_inline_queries: false,
    commandsByScope: [
      {
        scope: { type: 'default' },
        commands: [
          { command: 'newbot', description: 'Create a new bot' },
          { command: 'mybots', description: 'Edit your bots and configure settings' },
          { command: 'token', description: 'Generate or view HTTP Bot API token' },
          { command: 'revoke', description: 'Revoke current bot access token' },
          { command: 'setcommands', description: 'Change the list of bot commands & scopes' },
          { command: 'setprivacy', description: 'Toggle group privacy mode (Enable / Disable)' },
          { command: 'setinline', description: 'Toggle inline query mode and placeholder' },
          { command: 'setinlinegeo', description: 'Toggle inline location requests' },
          { command: 'setname', description: 'Change bot display name' },
          { command: 'setdescription', description: 'Change bot description shown on profile' },
          { command: 'setabouttext', description: 'Change bot about text' },
          { command: 'setuserpic', description: 'Change bot profile photo' },
          { command: 'deletebot', description: 'Delete a bot permanently' },
          { command: 'help', description: 'Help manual and API documentation' },
        ],
      },
    ],
  },
  telegramaibot: {
    id: 'user_telegramaibot',
    name: 'Telegram AI Assistant',
    username: 'TelegramAIBot',
    avatar: 'https://images.unsplash.com/photo-1614680376593-902f749f7ffc?w=150',
    token: '7892149801:AAH_TelegramAIFlashGenAIKey',
    is_bot: true,
    flags: {
      bot: true,
      bot_chat_history: true, // Has access to group messages
      bot_nochats: false,
      bot_inline_geo: false,
      bot_info_version: 4,
      bot_inline_placeholder: 'Ask AI anything...',
    },
    privacyMode: false,
    can_read_all_group_messages: true,
    can_join_groups: true,
    supports_inline_queries: true,
    inline_placeholder: 'Ask Telegram AI anything...',
    commandsByScope: [
      {
        scope: { type: 'default' },
        commands: [
          { command: 'start', description: 'Start the AI assistant and view features' },
          { command: 'help', description: 'Detailed guidance and capabilities' },
          { command: 'settings', description: 'Adjust response style, tone, and language' },
          { command: 'summarize', description: 'Summarize recent discussion or article' },
          { command: 'code', description: 'Inspect, debug, or write code snippets' },
        ],
      },
      {
        scope: { type: 'all_chat_administrators' },
        commands: [
          { command: 'start', description: 'Start AI assistant' },
          { command: 'modstats', description: 'Show group moderation & AI audit report' },
          { command: 'banspam', description: 'Scan and remove automated spam' },
          { command: 'rules', description: 'Generate or review group guidelines' },
        ],
      },
    ],
  },
  cryptobot: {
    id: 'user_cryptobot',
    name: 'Crypto & Stars Bot',
    username: 'CryptoBot',
    avatar: 'https://images.unsplash.com/photo-1622979135225-d2ba269bc1df?w=150',
    token: '5566778899:AAH_CryptoStarsPaymentKey',
    is_bot: true,
    flags: {
      bot: true,
      bot_chat_history: false,
      bot_nochats: false,
      bot_info_version: 2,
      bot_inline_placeholder: 'Pay or transfer stars...',
    },
    privacyMode: true,
    can_read_all_group_messages: false,
    can_join_groups: true,
    supports_inline_queries: true,
    inline_placeholder: 'Send stars or crypto...',
    commandsByScope: [
      {
        scope: { type: 'default' },
        commands: [
          { command: 'start', description: 'Open your Telegram Star & Crypto Wallet' },
          { command: 'balance', description: 'View current star and token balance' },
          { command: 'pay', description: 'Initiate a peer-to-peer tip or payment' },
          { command: 'invoice', description: 'Create an invoice for goods or services' },
        ],
      },
    ],
  },
};

export class TelegramBotEngine {
  // In-memory group privacy mode overrides (chatId -> boolean where true = privacy mode disabled, all messages received)
  private static groupPrivacyDisabledMap: Map<string, boolean> = new Map();

  public static setGroupPrivacyDisabled(chatId: string, disabled: boolean): void {
    this.groupPrivacyDisabledMap.set(chatId, disabled);
  }

  public static isGroupPrivacyDisabled(chatId?: string): boolean {
    if (!chatId) return false;
    return this.groupPrivacyDisabledMap.get(chatId) === true;
  }

  /**
   * Calls the official Telegram API endpoint to toggle Privacy Mode for a group
   */
  public static async toggleGroupPrivacyApi(
    chatId: string,
    disablePrivacyMode: boolean,
    botUsername?: string
  ): Promise<{ success: boolean; message: string; privacyModeDisabled: boolean }> {
    try {
      const response = await fetch('/api/telegram/bot/group-privacy-mode', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          chatId,
          disablePrivacyMode,
          botUsername,
        }),
      });
      const data = await response.json();
      if (data.success) {
        this.setGroupPrivacyDisabled(chatId, disablePrivacyMode);
        if (botUsername) {
          const clean = botUsername.replace('@', '').toLowerCase();
          if (OFFICIAL_TELEGRAM_BOTS[clean]) {
            OFFICIAL_TELEGRAM_BOTS[clean].privacyMode = !disablePrivacyMode;
            OFFICIAL_TELEGRAM_BOTS[clean].can_read_all_group_messages = disablePrivacyMode;
            OFFICIAL_TELEGRAM_BOTS[clean].canReadAllGroupMessages = disablePrivacyMode;
            OFFICIAL_TELEGRAM_BOTS[clean].flags.bot_chat_history = disablePrivacyMode;
          }
        } else {
          Object.values(OFFICIAL_TELEGRAM_BOTS).forEach((b) => {
            b.privacyMode = !disablePrivacyMode;
            b.can_read_all_group_messages = disablePrivacyMode;
            b.canReadAllGroupMessages = disablePrivacyMode;
            b.flags.bot_chat_history = disablePrivacyMode;
          });
        }
      }
      return data;
    } catch (err) {
      console.warn('[TelegramBotEngine] toggleGroupPrivacyApi network error:', err);
      // Fallback local update
      this.setGroupPrivacyDisabled(chatId, disablePrivacyMode);
      return {
        success: true,
        privacyModeDisabled: disablePrivacyMode,
        message: disablePrivacyMode
          ? 'Group Privacy Mode disabled locally (can_read_all_group_messages = true)'
          : 'Group Privacy Mode enabled locally',
      };
    }
  }

  /**
   * 1. 🕵️ MTProto & Bot API Bot Recognition
   */
  public static isBotUser(user: Partial<User> | any): boolean {
    if (!user) return false;
    // MTProto Check: bit 14 in flags or bot boolean
    if (user.bot === true) return true;
    if (typeof user.flags === 'number' && (user.flags & (1 << 14)) !== 0) return true;
    // Bot API Check
    if (user.is_bot === true) return true;
    // Username ends with 'bot'
    if (user.username && user.username.toLowerCase().endsWith('bot')) return true;
    return false;
  }

  /**
   * Check if a bot has access to all messages in a group
   * In Telegram:
   * - If bot is an administrator in the group -> TRUE
   * - If Group Privacy Mode is disabled in the group settings -> TRUE
   * - If bot has Privacy Mode disabled (bot_chat_history = true) -> TRUE
   * - Otherwise -> FALSE (Privacy mode enabled)
   */
  public static botHasAccessToAllMessages(bot: BotEntity, chat?: Chat, isBotAdmin = false): boolean {
    if (isBotAdmin) return true;
    if (chat?.botPrivacyDisabled === true || (chat?.id && this.isGroupPrivacyDisabled(chat.id))) {
      return true;
    }
    if (bot.flags.bot_chat_history === true || bot.can_read_all_group_messages === true || bot.privacyMode === false) {
      return true;
    }
    return false;
  }

  /**
   * Status subtitle display for bot according to Telegram Official UI:
   * - In 1-on-1 chat: returns "bot" (or "بوت")
   * - In group member list: returns "has access to messages" or "has no access to messages"
   */
  public static getBotSubtitle(
    bot: BotEntity | null,
    isArabic: boolean,
    context: 'private' | 'group' = 'private',
    isBotAdmin = false,
    chat?: Chat
  ): string {
    if (context === 'group' && bot) {
      const hasAccess = this.botHasAccessToAllMessages(bot, chat, isBotAdmin);
      if (hasAccess) {
        return isArabic ? 'لديه حق الوصول إلى الرسائل' : 'has access to messages';
      }
      return isArabic ? 'ليس لديه وصول إلى الرسائل' : 'has no access to messages';
    }
    return isArabic ? 'بوت' : 'bot';
  }

  /**
   * 2. 📜 BotCommandScope Hierarchy Resolution Engine
   * 
   * Resolves the exact commands to show when a user types '/' in a given chat.
   * According to Telegram Bot API specification:
   * 
   * In Group / Supergroup chats:
   * 1. BotCommandScopeChatMember (for specific user in this specific chat)
   * 2. BotCommandScopeChatAdministrators (if user is admin in this specific chat)
   * 3. BotCommandScopeChat (for this specific chat)
   * 4. BotCommandScopeAllChatAdministrators (if user is admin)
   * 5. BotCommandScopeAllGroupChats (for all groups)
   * 6. BotCommandScopeDefault (fallback)
   * 
   * In Private chats:
   * 1. BotCommandScopeChat (for this specific private chat)
   * 2. BotCommandScopeAllPrivateChats (for all private chats)
   * 3. BotCommandScopeDefault (fallback)
   */
  public static resolveCommandsForUser(
    chat: Chat,
    user: User,
    bot: BotEntity,
    isUserAdmin = false
  ): BotCommand[] {
    const isGroup = chat.type === 'group';
    const isPrivate = chat.type === 'private' || chat.type === 'bot';
    const chatId = chat.id;
    const userId = user.id;

    const entries = bot.commandsByScope || [];

    if (isGroup) {
      // 1. BotCommandScopeChatMember
      const memberScope = entries.find(
        (e) =>
          e.scope.type === 'chat_member' &&
          String(e.scope.chat_id) === String(chatId) &&
          String(e.scope.user_id) === String(userId)
      );
      if (memberScope && memberScope.commands.length > 0) {
        return memberScope.commands;
      }

      // 2. BotCommandScopeChatAdministrators (if user is admin)
      if (isUserAdmin) {
        const chatAdminScope = entries.find(
          (e) =>
            e.scope.type === 'chat_administrators' &&
            String(e.scope.chat_id) === String(chatId)
        );
        if (chatAdminScope && chatAdminScope.commands.length > 0) {
          return chatAdminScope.commands;
        }
      }

      // 3. BotCommandScopeChat
      const chatScope = entries.find(
        (e) => e.scope.type === 'chat' && String(e.scope.chat_id) === String(chatId)
      );
      if (chatScope && chatScope.commands.length > 0) {
        return chatScope.commands;
      }

      // 4. BotCommandScopeAllChatAdministrators (if user is admin)
      if (isUserAdmin) {
        const allAdminScope = entries.find(
          (e) => e.scope.type === 'all_chat_administrators'
        );
        if (allAdminScope && allAdminScope.commands.length > 0) {
          return allAdminScope.commands;
        }
      }

      // 5. BotCommandScopeAllGroupChats
      const allGroupsScope = entries.find((e) => e.scope.type === 'all_group_chats');
      if (allGroupsScope && allGroupsScope.commands.length > 0) {
        return allGroupsScope.commands;
      }
    } else if (isPrivate) {
      // 1. BotCommandScopeChat
      const chatScope = entries.find(
        (e) => e.scope.type === 'chat' && String(e.scope.chat_id) === String(chatId)
      );
      if (chatScope && chatScope.commands.length > 0) {
        return chatScope.commands;
      }

      // 2. BotCommandScopeAllPrivateChats
      const allPrivateScope = entries.find((e) => e.scope.type === 'all_private_chats');
      if (allPrivateScope && allPrivateScope.commands.length > 0) {
        return allPrivateScope.commands;
      }
    }

    // 6. BotCommandScopeDefault (Universal fallback)
    const defaultScope = entries.find((e) => e.scope.type === 'default');
    if (defaultScope && defaultScope.commands.length > 0) {
      return defaultScope.commands;
    }

    return [];
  }

  /**
   * Aggregate all available commands for a chat:
   * In private chat with a bot: returns commands for that bot.
   * In a group: returns commands from all active bots present in the group.
   */
  public static getAvailableCommandsForChat(
    chat: Chat,
    user: User,
    isUserAdmin = false,
    customBots: Record<string, BotEntity> = {}
  ): { botUsername: string; command: string; description: string }[] {
    const allBots = { ...OFFICIAL_TELEGRAM_BOTS, ...customBots };
    const results: { botUsername: string; command: string; description: string }[] = [];

    if (chat.type === 'bot' || (chat.username && chat.username.toLowerCase().endsWith('bot'))) {
      const cleanUsername = (chat.username || '').replace('@', '').toLowerCase();
      const bot = allBots[cleanUsername] || OFFICIAL_TELEGRAM_BOTS.telegramaibot;
      const cmds = this.resolveCommandsForUser(chat, user, bot, isUserAdmin);
      return cmds.map((c) => ({
        botUsername: bot.username,
        command: `/${c.command}`,
        description: c.description,
      }));
    }

    if (chat.type === 'group') {
      // In groups, commands are formatted with @botname if multiple bots or standard /cmd
      Object.values(allBots).forEach((bot) => {
        const cmds = this.resolveCommandsForUser(chat, user, bot, isUserAdmin);
        cmds.forEach((c) => {
          results.push({
            botUsername: bot.username,
            command: `/${c.command}@${bot.username}`,
            description: `[${bot.name}] ${c.description}`,
          });
        });
      });
    }

    return results;
  }

  /**
   * 3. ⚙️ Privacy Mode (وضع الخصوصية) in Groups
   * 
   * When Privacy Mode is ENABLED, a bot in a group receives ONLY:
   * 1. Commands starting with '/' (e.g. /help or /help@BotName)
   *    - If specified with @OtherBot, this bot does NOT receive it!
   * 2. Direct replies to this bot's own messages
   * 3. Messages that mention this bot by @username
   * 4. Service messages (chat title change, new member joined, pin)
   * 
   * When Privacy Mode is DISABLED OR if the bot is Group Admin:
   * -> Receives ALL messages.
   */
  public static shouldBotReceiveGroupMessage(
    bot: BotEntity,
    messageText: string,
    replyToSenderId?: string,
    isBotAdmin = false,
    chat?: Chat
  ): { canReceive: boolean; reason: string } {
    // Admin or Group Privacy Mode Disabled or Bot Privacy Mode Disabled
    if (isBotAdmin) {
      return { canReceive: true, reason: 'Bot is group administrator (receives all messages)' };
    }
    if (chat?.botPrivacyDisabled === true || (chat?.id && this.isGroupPrivacyDisabled(chat.id))) {
      return {
        canReceive: true,
        reason: 'Group Privacy Mode is DISABLED by Group Admin via Telegram API (receives all group messages)',
      };
    }
    if (bot.privacyMode === false || bot.can_read_all_group_messages === true || bot.flags.bot_chat_history === true) {
      return { canReceive: true, reason: 'Privacy mode is DISABLED via @BotFather (receives all messages)' };
    }

    const trimmed = (messageText || '').trim();
    const botUsernameLower = bot.username.toLowerCase();

    // 1. Commands starting with '/'
    if (trimmed.startsWith('/')) {
      const match = trimmed.match(/^\/([a-zA-Z0-9_]+)(?:@([a-zA-Z0-9_]+))?/);
      if (match) {
        const targetBot = match[2]?.toLowerCase();
        if (!targetBot || targetBot === botUsernameLower) {
          return { canReceive: true, reason: `Targeted or general command: ${match[1]}` };
        } else {
          return {
            canReceive: false,
            reason: `Command targeted specifically to another bot: @${targetBot}`,
          };
        }
      }
    }

    // 2. Direct reply to this bot's message
    if (replyToSenderId && (replyToSenderId === bot.id || replyToSenderId === bot.username)) {
      return { canReceive: true, reason: 'Direct reply to bot message' };
    }

    // 3. Mention of this bot (@BotName)
    const mentionRegex = new RegExp(`@${botUsernameLower}\\b`, 'i');
    if (mentionRegex.test(trimmed)) {
      return { canReceive: true, reason: `Mentioned by username: @${bot.username}` };
    }

    // 4. Default: Filtered out under Privacy Mode
    return {
      canReceive: false,
      reason: 'Message filtered by Telegram Group Privacy Mode (can_read_all_group_messages = false)',
    };
  }

  /**
   * 4. 🔍 Interactive Inline Queries (@BotName query)
   */
  public static queryInlineBot(
    botUsername: string,
    query: string,
    isArabic: boolean
  ): InlineQueryResult[] {
    const cleanBot = botUsername.replace('@', '').toLowerCase();
    const q = query.trim();

    if (cleanBot === 'telegramaibot' || cleanBot === 'ai_bot') {
      return [
        {
          id: `iq_ai_1_${Date.now()}`,
          type: 'article',
          title: isArabic ? '⚡ إجابة الذكاء الاصطناعي الفورية' : '⚡ AI Instant Answer',
          description: q ? (isArabic ? `إجابة ذكية وموجزة عن: "${q}"` : `Smart summary for: "${q}"`) : (isArabic ? 'اكتب سؤالك لتوليد إجابة فورية' : 'Type your query to generate answer'),
          thumb_url: 'https://images.unsplash.com/photo-1614680376593-902f749f7ffc?w=100',
          input_message_content: {
            message_text: isArabic
              ? `🤖 **إجابة Telegram AI:**\n\nبخصوص "${q || 'استفسارك'}": تم معالجة الطلب سحابياً عبر نموذج Gemini Flash بدقة متناهية وسرعة فائقة!`
              : `🤖 **Telegram AI Answer:**\n\nRegarding "${q || 'your query'}": Processed via cloud Gemini Flash model with high accuracy and speed!`,
            parse_mode: 'MarkdownV2',
          },
        },
        {
          id: `iq_ai_2_${Date.now()}`,
          type: 'article',
          title: isArabic ? '💻 توليد كود برمجي' : '💻 Code Snippet Generation',
          description: isArabic ? `توليد كود نظيف وتوضيحي لـ: ${q || 'البرمجة'}` : `Generate clean code for: ${q || 'programming'}`,
          thumb_url: 'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=100',
          input_message_content: {
            message_text: `\`\`\`typescript\n// Generated by @TelegramAIBot\nexport function solveQuery() {\n  return "Result for: ${q || 'TypeScript'}";\n}\n\`\`\``,
            parse_mode: 'HTML',
          },
        },
      ];
    }

    if (cleanBot === 'cryptobot' || cleanBot === 'stars') {
      return [
        {
          id: `iq_crypto_1_${Date.now()}`,
          type: 'article',
          title: isArabic ? '⭐️ إهداء 50 نجمة تيليجرام' : '⭐️ Gift 50 Telegram Stars',
          description: isArabic ? 'إرسال بطاقة هدية نجوم تيليجرام في الدردشة' : 'Send Telegram Stars gift card in chat',
          thumb_url: 'https://images.unsplash.com/photo-1622979135225-d2ba269bc1df?w=100',
          input_message_content: {
            message_text: isArabic
              ? '⭐️ **هدية نجوم تيليجرام (Telegram Stars Gift):**\n\n🎁 لقد تلقيت 50 نجمة لدعم المحتوى والتفاعل!\n\n_تم الإرسال بواسطة @CryptoBot_'
              : '⭐️ **Telegram Stars Gift:**\n\n🎁 You received 50 Stars for content support and reactions!\n\n_Sent via @CryptoBot_',
            parse_mode: 'MarkdownV2',
          },
          reply_markup: {
            inline_keyboard: [
              [
                { text: isArabic ? '⭐️ استلام النجوم' : '⭐️ Claim Stars', callback_data: 'claim_stars_50' },
              ],
            ],
          },
        },
      ];
    }

    // Default inline query generator
    return [
      {
        id: `iq_default_${Date.now()}`,
        type: 'article',
        title: `@${botUsername} : ${q || (isArabic ? 'بدء استعلام مضمن' : 'Start query')}`,
        description: isArabic ? `إرسال نتيجة تفاعلية من @${botUsername}` : `Send interactive result from @${botUsername}`,
        input_message_content: {
          message_text: `⚡ [Inline Query Result from @${botUsername}]: ${q}`,
        },
      },
    ];
  }
}
