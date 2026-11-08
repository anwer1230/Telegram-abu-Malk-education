package org.telegram.tgnet;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.DataInputStream;
import java.io.DataOutputStream;

/**
 * SerializedData.java - Official DrKLO/Telegram Android Implementation
 * Path: TMessagesProj/src/main/java/org/telegram/tgnet/SerializedData.java
 *
 * MTProto Type-Length-Value binary serializer and deserializer.
 */
public class SerializedData {

    private ByteArrayOutputStream out;
    private DataOutputStream dataOut;
    private ByteArrayInputStream in;
    private DataInputStream dataIn;

    public SerializedData() {
        out = new ByteArrayOutputStream();
        dataOut = new DataOutputStream(out);
    }

    public SerializedData(byte[] bytes) {
        in = new ByteArrayInputStream(bytes);
        dataIn = new DataInputStream(in);
    }

    public void writeInt32(int x) {
        try {
            dataOut.writeInt(Integer.reverseBytes(x));
        } catch (Exception ignored) {}
    }

    public void writeInt64(long x) {
        try {
            dataOut.writeLong(Long.reverseBytes(x));
        } catch (Exception ignored) {}
    }

    public void writeString(String s) {
        try {
            byte[] b = s.getBytes("UTF-8");
            writeInt32(b.length);
            dataOut.write(b);
        } catch (Exception ignored) {}
    }

    public void writeByteArray(byte[] b) {
        try {
            if (b == null) {
                writeInt32(0);
                return;
            }
            writeInt32(b.length);
            dataOut.write(b);
        } catch (Exception ignored) {}
    }

    public int readInt32(boolean exception) {
        try {
            return Integer.reverseBytes(dataIn.readInt());
        } catch (Exception e) {
            return 0;
        }
    }

    public long readInt64(boolean exception) {
        try {
            return Long.reverseBytes(dataIn.readLong());
        } catch (Exception e) {
            return 0;
        }
    }

    public String readString(boolean exception) {
        try {
            int len = readInt32(exception);
            byte[] b = new byte[len];
            dataIn.readFully(b);
            return new String(b, "UTF-8");
        } catch (Exception e) {
            return "";
        }
    }

    public byte[] readByteArray(boolean exception) {
        try {
            int len = readInt32(exception);
            byte[] b = new byte[len];
            dataIn.readFully(b);
            return b;
        } catch (Exception e) {
            return new byte[0];
        }
    }

    public byte[] toByteArray() {
        return out != null ? out.toByteArray() : new byte[0];
    }

    public void cleanup() {
        try {
            if (out != null) out.close();
            if (in != null) in.close();
        } catch (Exception ignored) {}
    }
}
