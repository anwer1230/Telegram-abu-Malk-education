package org.telegram.messenger;

import java.security.MessageDigest;
import java.security.SecureRandom;

/**
 * Utilities.java - Official DrKLO/Telegram Android Implementation
 * Path: TMessagesProj/src/main/java/org/telegram/messenger/Utilities.java
 */
public class Utilities {

    public static final SecureRandom random = new SecureRandom();

    public interface Callback<T> {
        void run(T param);
    }

    public static byte[] computeSHA256(byte[] convertme, int offset, int len) {
        try {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            md.update(convertme, offset, len);
            return md.digest();
        } catch (Exception e) {
            FileLog.e(e);
            return new byte[32];
        }
    }

    public static String bytesToHex(byte[] bytes) {
        if (bytes == null) return "";
        StringBuilder sb = new StringBuilder(bytes.length * 2);
        for (byte b : bytes) {
            sb.append(String.format("%02x", b));
        }
        return sb.toString();
    }
}
