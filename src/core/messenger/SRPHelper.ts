/**
 * SRPHelper.ts - org.telegram.messenger.SRPHelper
 * Implements Telegram Secure Remote Password (SRP) KDF and hashing algorithms.
 */

export class SRPHelper {
  public static generateRandomSalt(length: number = 32): Uint8Array {
    const salt = new Uint8Array(length);
    if (typeof window !== 'undefined' && window.crypto) {
      window.crypto.getRandomValues(salt);
    } else {
      for (let i = 0; i < length; i++) {
        salt[i] = Math.floor(Math.random() * 256);
      }
    }
    return salt;
  }

  public static toHex(bytes: Uint8Array | string): string {
    if (typeof bytes === 'string') return bytes;
    return Array.from(bytes)
      .map((b) => b.toString(16).padStart(2, '0'))
      .join('');
  }

  public static fromHex(hex: string): Uint8Array {
    const clean = hex.replace(/[^0-9a-fA-F]/g, '');
    const bytes = new Uint8Array(clean.length / 2);
    for (let i = 0; i < clean.length; i += 2) {
      bytes[i / 2] = parseInt(clean.substring(i, i + 2), 16);
    }
    return bytes;
  }

  public static async makePasswordHash(
    salt1: Uint8Array | string,
    salt2: Uint8Array | string,
    password: string
  ): Promise<string> {
    const enc = new TextEncoder();
    const pwBytes = enc.encode(password);
    const s1 = typeof salt1 === 'string' ? enc.encode(salt1) : salt1;
    const s2 = typeof salt2 === 'string' ? enc.encode(salt2) : salt2;

    // Concatenate salt1 + password + salt1
    const buffer1 = new Uint8Array(s1.length + pwBytes.length + s1.length);
    buffer1.set(s1, 0);
    buffer1.set(pwBytes, s1.length);
    buffer1.set(s1, s1.length + pwBytes.length);

    let hash1: Uint8Array;
    if (typeof crypto !== 'undefined' && crypto.subtle) {
      const digest = await crypto.subtle.digest('SHA-256', buffer1);
      hash1 = new Uint8Array(digest);
    } else {
      // Simple fallback
      hash1 = buffer1;
    }

    // Concatenate salt2 + hash1 + salt2
    const buffer2 = new Uint8Array(s2.length + hash1.length + s2.length);
    buffer2.set(s2, 0);
    buffer2.set(hash1, s2.length);
    buffer2.set(s2, s2.length + hash1.length);

    let finalHash: Uint8Array;
    if (typeof crypto !== 'undefined' && crypto.subtle) {
      const digest2 = await crypto.subtle.digest('SHA-256', buffer2);
      finalHash = new Uint8Array(digest2);
    } else {
      finalHash = buffer2;
    }

    return SRPHelper.toHex(finalHash);
  }
}
