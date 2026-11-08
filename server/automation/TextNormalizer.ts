/**
 * TextNormalizer.ts - Advanced Arabic Text Normalization & Link Sanitizer
 * Conforms strictly to requirements:
 * 1. Diacritics stripping & character unification (أ/إ/آ -> ا, ة -> ه, ى -> ي)
 * 2. Group links parsing, bullet stripping, and deduplication
 * 3. Link conversion (WhatsApp conversion, smart strip)
 */

export class TextNormalizer {
  /**
   * Normalizes Arabic text by removing tashkeel, kashida, and unifying letters
   */
  public static normalizeArabic(text: string): string {
    if (!text) return '';

    return text
      // Remove Arabic diacritics (Harakat / Tashkeel)
      .replace(/[\u064B-\u065F\u0670]/g, '')
      // Remove Kashida / Tatweel
      .replace(/\u0640/g, '')
      // Normalize Alef variations (أ, إ, آ, ٱ -> ا)
      .replace(/[أإآٱ]/g, 'ا')
      // Normalize Taa Marbuta (ة -> ه)
      .replace(/ة/g, 'ه')
      // Normalize Alef Maksura (ى -> ي)
      .replace(/ى/g, 'ي')
      // Normalize Hamza on Waw / Yaa (ؤ -> و, ئ -> ي)
      .replace(/ؤ/g, 'و')
      .replace(/ئ/g, 'ي')
      // Normalize multiple whitespaces into a single space
      .replace(/\s+/g, ' ')
      .trim()
      .toLowerCase();
  }

  /**
   * Checks whether the normalized haystack contains the normalized needle (keyword)
   */
  public static matchKeyword(haystack: string, keyword: string): boolean {
    const normHaystack = this.normalizeArabic(haystack);
    const normKeyword = this.normalizeArabic(keyword);
    if (!normKeyword) return false;

    // Direct inclusion check on normalized strings
    return normHaystack.includes(normKeyword);
  }

  /**
   * Parses, cleans, and deduplicates group links from user multiline input
   * Removes bullets (-, •, *, 1., etc.), trims URLs, and unifies formats
   */
  public static cleanGroupLinks(rawInput: string | string[]): string[] {
    const lines = Array.isArray(rawInput)
      ? rawInput
      : rawInput.split(/[\r\n]+/);

    const results = new Set<string>();

    for (const rawLine of lines) {
      let line = rawLine.trim();
      if (!line) continue;

      // Remove leading bullets, numbers, dashes, dashes, emojis
      line = line.replace(/^[\s•\-\*\d\.\)\(\[\]:،,]+/u, '').trim();
      if (!line) continue;

      // Unify telegram.me -> t.me
      line = line.replace(/^https?:\/\/telegram\.me\//i, 'https://t.me/');
      line = line.replace(/^telegram\.me\//i, 'https://t.me/');
      line = line.replace(/^http:\/\/t\.me\//i, 'https://t.me/');

      // Ensure https if starts with t.me
      if (/^t\.me\//i.test(line)) {
        line = `https://${line}`;
      }

      // If user typed @username or just username, keep clean
      if (line.startsWith('@')) {
        results.add(line);
      } else if (/^https:\/\/t\.me\//i.test(line)) {
        // Remove trailing queries and slashes
        line = line.replace(/[?#].*$/, '').replace(/\/+$/, '');
        results.add(line);
      } else if (/^[a-zA-Z0-9_]{4,32}$/.test(line)) {
        // Simple username
        results.add(`@${line}`);
      } else if (/^-?\d+$/.test(line)) {
        // Numeric chat ID
        results.add(line);
      } else {
        // Check if there is an embedded t.me link inside the string
        const match = line.match(/https?:\/\/t\.me\/(?:\+|joinchat\/|[a-zA-Z0-9_]{4,32})/i);
        if (match) {
          results.add(match[0]);
        }
      }
    }

    return Array.from(results);
  }

  /**
   * Removes external links, promotional tags, and domains for 'smart' protection mode
   */
  public static sanitizeSmartMessage(text: string): string {
    if (!text) return '';

    return text
      // Remove URLs (http, https, t.me, bit.ly, etc.)
      .replace(/https?:\/\/[^\s]+/gi, '')
      .replace(/t\.me\/[^\s]+/gi, '')
      .replace(/wa\.me\/[^\s]+/gi, '')
      // Remove usernames and promotional mentions
      .replace(/@[a-zA-Z0-9_]{4,32}/g, '')
      // Clean multiple empty lines
      .replace(/\n{3,}/g, '\n\n')
      .trim();
  }

  /**
   * Converts WhatsApp links to readable text format for 'convert_links' protection mode
   */
  public static convertWhatsAppLinks(text: string): string {
    if (!text) return '';

    // Match wa.me/NUMBER or api.whatsapp.com/send?phone=NUMBER
    let result = text.replace(
      /https?:\/\/(?:wa\.me|api\.whatsapp\.com\/send\?phone=)(\+?\d+)[^\s]*/gi,
      (_match, phone) => `[تواصل واتساب: ${phone}]`
    );

    // Also sanitize other high-risk URLs
    result = result.replace(/https?:\/\/(?!(?:wa\.me))[^\s]+/gi, '');
    return result.trim();
  }
}
