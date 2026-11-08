/**
 * SecretChatHelper.ts - org.telegram.messenger.SecretChatHelper
 */

export class SecretChatHelper {
  private static instance: SecretChatHelper;

  public static getInstance(): SecretChatHelper {
    if (!SecretChatHelper.instance) {
      SecretChatHelper.instance = new SecretChatHelper();
    }
    return SecretChatHelper.instance;
  }
}
