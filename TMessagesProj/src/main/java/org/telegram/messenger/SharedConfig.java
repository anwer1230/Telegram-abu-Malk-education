package org.telegram.messenger;

import android.content.Context;
import android.content.SharedPreferences;

/**
 * SharedConfig.java - Official DrKLO/Telegram Android Implementation
 * Path: TMessagesProj/src/main/java/org/telegram/messenger/SharedConfig.java
 *
 * Stores global device configurations shared across all accounts:
 * - pushString: Device Push Token (FCM / HMS) used to keep connection alive
 * - Global passcode and auto-lock settings
 * - Device hardware affinity and push status
 */
public class SharedConfig {

    public static String pushString = "";
    public static String pushStringStatus = "";
    public static int pushType = 2; // 2 = Google Play Services / Firebase Cloud Messaging (FCM)
    public static boolean isAppLocked = false;
    public static String passcodeHash = "";
    public static byte[] passcodeSalt = new byte[0];
    public static int passcodeType = 0;
    public static int autoLockIn = 0;

    private static final Object sync = new Object();
    private static boolean configLoaded = false;

    public static void loadConfig() {
        synchronized (sync) {
            if (configLoaded) return;

            SharedPreferences preferences = ApplicationLoader.applicationContext.getSharedPreferences("userconfing", Context.MODE_PRIVATE);
            pushString = preferences.getString("pushString2", "");
            pushStringStatus = preferences.getString("pushStringStatus", "");
            pushType = preferences.getInt("pushType", 2);

            passcodeHash = preferences.getString("passcodeHash1", "");
            passcodeType = preferences.getInt("passcodeType", 0);
            autoLockIn = preferences.getInt("autoLockIn", 0);
            isAppLocked = preferences.getBoolean("isAppLocked", false);

            configLoaded = true;
        }
    }

    public static void saveConfig() {
        synchronized (sync) {
            SharedPreferences preferences = ApplicationLoader.applicationContext.getSharedPreferences("userconfing", Context.MODE_PRIVATE);
            SharedPreferences.Editor editor = preferences.edit();

            editor.putString("pushString2", pushString);
            editor.putString("pushStringStatus", pushStringStatus);
            editor.putInt("pushType", pushType);

            editor.putString("passcodeHash1", passcodeHash);
            editor.putInt("passcodeType", passcodeType);
            editor.putInt("autoLockIn", autoLockIn);
            editor.putBoolean("isAppLocked", isAppLocked);

            editor.apply();
        }
    }

    /**
     * Goal 3: Sets device push token from Firebase Cloud Messaging.
     * When registered, Telegram servers route background wakeup pushes directly
     * to this token, preventing user sessions from expiring or timing out.
     */
    public static void setPushString(String token) {
        synchronized (sync) {
            pushString = token != null ? token : "";
            saveConfig();
        }
    }
}
