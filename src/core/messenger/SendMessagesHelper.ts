/**
 * SendMessagesHelper.ts - org.telegram.messenger.SendMessagesHelper
 */

export class SendMessagesHelper {
  private static instance: SendMessagesHelper;

  public static getInstance(): SendMessagesHelper {
    if (!SendMessagesHelper.instance) {
      SendMessagesHelper.instance = new SendMessagesHelper();
    }
    return SendMessagesHelper.instance;
  }
}
