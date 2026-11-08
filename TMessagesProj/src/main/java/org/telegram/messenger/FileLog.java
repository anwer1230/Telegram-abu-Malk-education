package org.telegram.messenger;

import android.util.Log;

/**
 * FileLog.java - Official DrKLO/Telegram Android Implementation
 * Path: TMessagesProj/src/main/java/org/telegram/messenger/FileLog.java
 */
public class FileLog {
    private static final String TAG = "tmessages";

    public static void d(String message) {
        Log.d(TAG, message);
    }

    public static void e(String message) {
        Log.e(TAG, message);
    }

    public static void e(Throwable e) {
        Log.e(TAG, "Exception: ", e);
    }
}
