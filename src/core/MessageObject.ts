/**
 * MessageObject.ts - org.telegram.messenger.MessageObject
 */

import { Message, Chat } from '../types';

export class MessageObject {
  public message: Message;
  public currentAccount: number;
  public chat?: Chat;
  public isChannelPostVal: boolean;
  public isPostAuthorVisible: boolean;
  public postAuthor?: string;

  constructor(message: Message, currentAccount: number = 0, chat?: Chat) {
    this.message = message;
    this.currentAccount = currentAccount;
    this.chat = chat;
    this.isChannelPostVal = chat?.type === 'channel';
    this.isPostAuthorVisible = false;
    this.postAuthor = message.senderName;
  }

  public getSenderTitle(): string {
    return this.message.senderName || 'Telegram User';
  }
}
