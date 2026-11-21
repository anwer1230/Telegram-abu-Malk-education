# -*- coding: utf-8 -*-
"""
وحدة الذكاء الاصطناعي لفحص المجموعات وتحليل آخر 50 محادثة وحماية الحساب من الحظر.
- استخراج آخر 50 رسالة من كل مجموعة
- تحليل حالات الحظر والكتم والتقييد والأسباب
- استخراج أخطاء الآخرين وتجنبها آلياً وتلقائياً
- إرسال تقرير مفصل إلى "الرسائل المحفوظة" (Saved Messages / 'me')
"""

import os
import re
import time
import json
import logging
import asyncio
import requests
from datetime import datetime
from config import get_gemini_api_key

logger = logging.getLogger("GroupAiAnalyzer")

# قائمة النماذج المفضلة للاستدعاء بالترتيب
GEMINI_MODELS = [
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash",
    "gemini-flash-latest",
    "gemini-3-flash-preview"
]

# قاموس تحويل الكلمات المحظورة الشائعة إلى الإنجليزية / الإنجليزية المعرّبة
FORBIDDEN_KEYWORD_ENGLISH_MAP = {
    "سكاليف": "skalive",
    "سكليف": "skalive",
    "سكلـيف": "skalive",
    "اسكاليف": "skalive",
    "اعذار طبية": "medical excuses",
    "اعذار طبيه": "medical excuses",
    "عذر طبي": "medical excuse",
    "اعذار": "excuses",
    "عذر": "excuse",
    "اجازه مرضيه": "sick leave",
    "صحتي": "sehaty",
    "تقرير طبي": "medical report",
    "تقارير طبيه": "medical reports",
    "واجبات": "assignments",
    "واجب": "assignment",
    "كويزات": "quizzes",
    "كويز": "quiz",
    "اختبارات": "exams",
    "اختبار": "exam",
    "امتحانات": "exams",
    "امتحان": "exam",
    "بحوث": "research",
    "بحث": "research",
    "ابحاث": "research",
    "تقارير": "reports",
    "تقرير": "report",
    "مشاريع تخرج": "graduation projects",
    "مشروع تخرج": "graduation project",
    "مشاريع": "projects",
    "مشروع": "project",
    "تكليفات": "tasks",
    "تكاليف": "tasks",
    "تكليف": "task",
    "اسايمنت": "assignment",
    "حلول": "solutions",
    "ملخصات": "summaries",
    "ملخص": "summary",
    "عروض تقديميه": "presentations",
    "بوربوينت": "powerpoint",
    "ترجمه": "translation",
    "تخرج": "graduation",
    "اعلانات": "announcements",
    "اعلان": "announcement",
    "ترويج": "promotion",
    "تسويق": "marketing",
    "تخفيضات": "offers",
    "تخفيض": "discount",
    "خصومات": "discounts",
    "خصم": "discount",
    "عروض": "offers",
    "عرض": "offer",
    "للتواصل": "contact",
    "راسلني": "dm me",
    "واتساب": "whatsapp",
    "واتس": "whats",
    "تليجرام": "telegram",
    "تليقرام": "telegram",
    "تيليجرام": "telegram",
    "خدمات": "services",
    "خدمه": "service",
    "بيع": "sale",
    "شراء": "buy",
    "استثمار": "investment",
    "تداول": "trading",
    "ارباح": "profits",
    "ربح": "profit",
    "اشتراك": "subscription",
    "دورات": "courses",
    "كورسات": "courses",
    "اسعار": "prices",
    "سعر": "price",
    "عموله": "commission",
    "كاش": "cash",
    "تحويل": "transfer",
    "سحب": "withdraw",
    "ايداع": "deposit",
    "اطلب": "order",
    "انضموا": "join",
    "انضم": "join",
    "قناتي": "channel",
    "قناه": "channel",
    "سارع": "hurry",
    "مدفوع": "paid",
    "مقابل": "paid",
}

_ARABIC_DIACRITICS_RE = re.compile(r"[\u064B-\u065F\u0670\u0640]")


def _normalize_ar_token(text):
    """تطبيع النص العربي للمطابقة دون المساس بالنص الأصلي عند عدم الحاجة."""
    s = _ARABIC_DIACRITICS_RE.sub("", str(text or "").strip())
    s = s.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
    s = s.replace("ى", "ي").replace("ة", "ه")
    s = re.sub(r"\s+", " ", s)
    return s.lower()


_NORMALIZED_EN_MAP = {_normalize_ar_token(k): v for k, v in FORBIDDEN_KEYWORD_ENGLISH_MAP.items()}
_COMMON_HIGH_RISK_WORDS = sorted(FORBIDDEN_KEYWORD_ENGLISH_MAP.keys(), key=len, reverse=True)


def space_word_with_ellipsis(word):
    """
    مباعدة أحرف الكلمة باستخدام المسافات والنقاط لتفادي فلاتر البوتات:
    مثال: سكاليف -> س ك...ال...يف
    """
    clean = _ARABIC_DIACRITICS_RE.sub("", str(word or "").strip())
    if not clean:
        return word

    if " " in clean:
        return " ".join(space_word_with_ellipsis(part) for part in clean.split() if part)

    n = len(clean)
    if n <= 1:
        return clean
    if n == 2:
        return f"{clean[0]}...{clean[1]}"
    if n == 3:
        return f"{clean[0]} {clean[1]}...{clean[2]}"
    if n == 4:
        return f"{clean[0]} {clean[1]}...{clean[2:]}"
    if n == 5:
        return f"{clean[0]} {clean[1]}...{clean[2]}...{clean[3:]}"
    if n == 6:
        return f"{clean[0]} {clean[1]}...{clean[2:4]}...{clean[4:]}"

    chunks = [f"{clean[0]} {clean[1]}"]
    idx = 2
    while idx < n - 2:
        step = 2 if (n - idx) > 3 else (n - idx - 2)
        if step <= 0:
            break
        chunks.append(clean[idx:idx + step])
        idx += step
    chunks.append(clean[idx:])
    return "...".join(c for c in chunks if c)


def obfuscate_forbidden_word(word, banned_set=None, mode="auto"):
    """
    تحويل الكلمة المحظورة إلى الإنجليزية إن وُجد مقابل آمن (مثل سكاليف -> skalive)،
    أو تطبيق مباعدة الأحرف بالنقاط (مثل س ك...ال...يف) على أي كلمة محظورة أخرى.
    """
    raw = str(word or "").strip()
    if not raw:
        return raw

    norm = _normalize_ar_token(raw)
    banned_norm = {_normalize_ar_token(x) for x in (banned_set or []) if x}

    if mode != "space":
        en_val = _NORMALIZED_EN_MAP.get(norm)
        if not en_val and norm.startswith("ال") and len(norm) > 4:
            en_val = _NORMALIZED_EN_MAP.get(norm[2:])
        if en_val and _normalize_ar_token(en_val) not in banned_norm:
            return en_val

    return space_word_with_ellipsis(raw)


def extract_forbidden_keywords_from_texts(texts, extra_keywords=None):
    """
    استخراج قائمة شاملة بكل الكلمات المحظورة المكتشفة من رسائل المجموعة أو التحذيرات أو تقارير الأمان.
    """
    discovered = []
    seen = set()

    def _add_kw(kw):
        cleaned = str(kw or "").strip(" \t\n\r\"'«»()[]{}.,،:؛!؟*_-")
        if not cleaned or len(cleaned) < 2 or len(cleaned) > 40:
            return
        norm = _normalize_ar_token(cleaned)
        if norm in ("تم", "من", "في", "على", "الى", "عن", "مع", "هذا", "هذه", "ممنوع", "محظور", "محضور", "حظر", "كتم", "طرد", "تحذير", "انذار", "مخالفة", "رابط", "روابط", "رسالة", "رسائل", "الرسالة", "المجموعة", "القروب"):
            return
        if norm not in seen:
            seen.add(norm)
            discovered.append(cleaned)

    for ek in (extra_keywords or []):
        _add_kw(ek)

    combined = "\n".join(str(t) for t in (texts or []) if t)
    if not combined.strip():
        return discovered

    # 1. استخراج الكلمات المذكورة بين علامات تنصيص أو بعد عبارات المنع/الكلمات المحظورة
    for q_match in re.finditer(r'(?:كلمة|كلمات|عبارة|عبارات|ممنوع|محظور|محضور|blacklist(?:ed)?|forbidden|banned\s+word)[^\n:]*[:\-]?\s*["\'«(\[]([^"\'»)\]\n]{2,35})["\'»)\]]', combined, flags=re.IGNORECASE):
        _add_kw(q_match.group(1))

    for q_match in re.finditer(r'(?:ممنوع|محظور|محضور)\s+(?:ذكر|كتابة|استخدام|نشر)?\s*(?:كلمة|عبارة)?\s*([^\s،,.!؟\n]{3,25})', combined, flags=re.IGNORECASE):
        _add_kw(q_match.group(1))

    # 2. مطابقة الكلمات الحساسة المعروفة داخل رسائل التحذير أو قواعد المجموعة
    norm_combined = _normalize_ar_token(combined)
    for raw_kw in _COMMON_HIGH_RISK_WORDS:
        norm_kw = _normalize_ar_token(raw_kw)
        if re.search(rf'(?<![\w\u0600-\u06FF])(?:ال)?{re.escape(norm_kw)}(?![\w\u0600-\u06FF])', norm_combined):
            _add_kw(raw_kw)

    return discovered


def _build_flexible_arabic_pattern(keyword):
    """بناء تعبير نمطي يطابق الكلمة رغم التشكيل أو التطويل أو تباين الهمزات/التاء المربوطة."""
    norm = _normalize_ar_token(keyword)
    if not norm:
        return None
    char_map = {
        "ا": "[اأإآ]",
        "ه": "[هة]",
        "ي": "[يى]",
        " ": r"\s+",
    }
    parts = []
    for ch in norm:
        if ch == " ":
            parts.append(r"\s+")
        else:
            parts.append(char_map.get(ch, re.escape(ch)) + r"[\u064B-\u065F\u0670\u0640]*")
    return "".join(parts)


def obfuscate_forbidden_words_detailed(text, keywords_to_avoid=None, include_common_ads=False, mode="auto"):
    """
    نسخة مفصلة تُرجع (النص_المعدل, الإجراءات, قائمة_الاستبدالات_المهيكلة)
    حيث يحتوي كل عنصر في قائمة الاستبدالات على: original و matched_text و replacement و method ('english' | 'spaced').
    """
    if not text:
        return text, [], []

    working = str(text)
    placeholders = {}

    def _stash(match):
        token = f"__HF_SAFE_TOK_{len(placeholders)}__"
        placeholders[token] = match.group(0)
        return token

    working = re.sub(
        r'(?:https?://[^\s<>]+|(?:t\.me|telegram\.me|wa\.me)/[^\s<>]+|www\.[^\s<>]+|@[A-Za-z0-9_]{3,})',
        _stash,
        working,
        flags=re.IGNORECASE,
    )

    candidate_list = []
    seen_norm = set()
    for kw in (keywords_to_avoid or []):
        clean_kw = str(kw or "").strip()
        n = _normalize_ar_token(clean_kw)
        if clean_kw and len(clean_kw) >= 2 and n not in seen_norm:
            seen_norm.add(n)
            candidate_list.append(clean_kw)

    if include_common_ads:
        for kw in _COMMON_HIGH_RISK_WORDS:
            n = _normalize_ar_token(kw)
            if n not in seen_norm:
                seen_norm.add(n)
                candidate_list.append(kw)

    candidate_list.sort(key=lambda s: len(_normalize_ar_token(s)), reverse=True)
    banned_set = list(keywords_to_avoid or [])
    actions = []
    replacements = []

    for kw in candidate_list:
        core_pat = _build_flexible_arabic_pattern(kw)
        if not core_pat:
            continue

        allow_prefix = len(_normalize_ar_token(kw)) >= 3
        if allow_prefix:
            full_pat = rf'(?<![\w\u0600-\u06FF])(?P<conj>[وفبكل])?(?P<def>ال)?(?P<stem>{core_pat})(?![\w\u0600-\u06FF])'
        else:
            full_pat = rf'(?<![\w\u0600-\u06FF])(?P<conj>)(?P<def>)(?P<stem>{core_pat})(?![\w\u0600-\u06FF])'

        replacement_core = obfuscate_forbidden_word(kw, banned_set=banned_set, mode=mode)
        if not replacement_core or _normalize_ar_token(replacement_core) == _normalize_ar_token(kw):
            continue

        is_english = bool(re.search(r'[A-Za-z]', replacement_core) and "..." not in replacement_core)
        matched_samples = []

        def _replacer(m):
            matched_samples.append(m.group(0))
            conj = m.group("conj") or ""
            def_art = m.group("def") or ""
            if re.search(r'[A-Za-z]', replacement_core):
                prefix = f"{conj} " if conj else ""
                return f"{prefix}{replacement_core}"
            return f"{conj}{def_art}{replacement_core}"

        new_working = re.sub(full_pat, _replacer, working, flags=re.IGNORECASE)
        if matched_samples and new_working != working:
            working = new_working
            actions.append(f"🔤 تحويل الكلمة المحظورة '{kw}' ← '{replacement_core}'")
            replacements.append({
                "original": kw,
                "matched_text": matched_samples[0],
                "replacement": replacement_core,
                "method": "english" if is_english else "spaced",
                "count": len(matched_samples),
            })

    for token, original in placeholders.items():
        working = working.replace(token, original)

    return working, actions, replacements


def obfuscate_forbidden_words_in_text(text, keywords_to_avoid=None, include_common_ads=False, mode="auto"):
    """
    تطبيق آلية تحويل الكلمات المحظورة إلى الإنجليزية (مثل skalive) أو مباعدة أحرفها (مثل س ك...ال...يف)
    على كافة الكلمات المحظورة المكتشفة داخل نص الرسالة مع الحفاظ على الروابط والمعرفات دون تشويه.
    """
    working, actions, _ = obfuscate_forbidden_words_detailed(
        text,
        keywords_to_avoid=keywords_to_avoid,
        include_common_ads=include_common_ads,
        mode=mode,
    )
    return working, actions


_ARABIC_INDIC_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789")


def strip_phone_numbers_and_links(text, strip_phones=True, strip_links=True):
    """
    حذف فعلي ونظيف لأرقام الهواتف والروابط المحظورة من النص مع تنظيف العبارات اليتيمة المرتبطة بها.
    تُرجع (النص_النظيف, قائمة_الإجراءات).
    """
    if not text:
        return text, []

    working = str(text)
    actions = []

    if strip_links:
        before_links = working
        working = re.sub(r'https?://(?:wa\.me|api\.whatsapp\.com|chat\.whatsapp\.com|whatsapp\.com)[^\s<>]*', '', working, flags=re.IGNORECASE)
        working = re.sub(r'(?:https?://)?(?:t\.me|telegram\.me)/[^\s<>]+', '', working, flags=re.IGNORECASE)
        working = re.sub(r'https?://[^\s<>]+|www\.[^\s<>]+', '', working, flags=re.IGNORECASE)
        working = re.sub(r'(?<![\w.])wa\.me/[^\s<>]+', '', working, flags=re.IGNORECASE)
        if working != before_links:
            actions.append("🚫 حذف الروابط الخارجية وروابط تيليجرام/واتساب")

    if strip_phones:
        before_phones = working
        # تطبيع الأرقام العربية الهندية داخل نسخة مطابقة للحذف بدقة
        norm_working = working.translate(_ARABIC_INDIC_DIGITS)
        phone_patterns = [
            # أرقام دولية أو محلية مع فواصل/مسافات/أقواس مثل +966 55 123 4567 أو 055-123-4567 أو 01012345678
            r'(?<!\d)(?:\+|00)?\d{1,4}[\s\-\.]*\(?\d{2,4}\)?[\s\-\.]*\d{3,4}[\s\-\.]*\d{3,4}(?!\d)',
            # سلاسل رقمية متصلة من 7 إلى 15 خانة (تشمل أرقام الجوال والواتساب بدون كود دولي)
            r'(?<!\d)(?:\+|00)?\d{7,15}(?!\d)',
        ]
        # إيجاد النطاقات المطابقة في norm_working وتطبيقها على working حتى نحافظ على بقية النص كما هو
        spans = []
        for pat in phone_patterns:
            for m in re.finditer(pat, norm_working):
                spans.append((m.start(), m.end()))
        if spans:
            # دمج النطاقات المتداخلة
            spans.sort()
            merged_spans = []
            for s, e in spans:
                if merged_spans and s <= merged_spans[-1][1]:
                    merged_spans[-1] = (merged_spans[-1][0], max(merged_spans[-1][1], e))
                else:
                    merged_spans.append((s, e))
            pieces = []
            last_idx = 0
            for s, e in merged_spans:
                pieces.append(working[last_idx:s])
                last_idx = e
            pieces.append(working[last_idx:])
            working = "".join(pieces)

        if working != before_phones:
            actions.append("📵 حذف أرقام الهواتف بالكامل لتوافق شروط المجموعة")

    # تنظيف الأسطر والفواصل المتبقية الفارغة أو عبارات التواصل اليتيمة بعد الحذف
    cleaned_lines = []
    orphan_contact_re = re.compile(
        r'^(?:للتواصل|تواصل|واتساب|واتس|رقم|جوال|هاتف|موبايل|اتصال|تليفون|فون|whatsapp|whats|contact|call)\s*[:\-–—•\|]*$',
        re.IGNORECASE
    )
    for raw_line in working.splitlines():
        line = re.sub(r'[ \t]{2,}', ' ', raw_line).strip()
        line = re.sub(r'[:\-–—•\|]+\s*$', '', line).strip() if orphan_contact_re.match(line) else line
        if not line:
            continue
        if orphan_contact_re.match(line):
            continue
        # إزالة أسطر الرموز الفارغة فقط (مثل 📱 أو 📞 المتبقية وحدها بعد حذف الرقم)
        if not re.search(r'[\w\u0600-\u06FF]', line):
            continue
        cleaned_lines.append(line)

    working = "\n".join(cleaned_lines).strip()
    return working, actions


async def fetch_group_recent_messages(client, entity_obj, limit=50):
    """
    استخراج آخر 50 رسالة + الرسالة المثبتة (إن وجدت) من المجموعة مع فحص القيود وبوتات الإشراف
    """
    messages_data = []
    pinned_rules = []
    detected_bots = []
    group_title = getattr(entity_obj, 'title', str(getattr(entity_obj, 'id', 'مجموعة')))
    group_id = getattr(entity_obj, 'id', 0)
    username = getattr(entity_obj, 'username', '')
    slowmode_seconds = getattr(entity_obj, 'slowmode_seconds', 0) or 0

    permissions = {
        "can_send_messages": True,
        "can_send_media": True,
        "can_embed_links": True,
        "slowmode_seconds": slowmode_seconds
    }

    # 1. التحقق المسبق: هل المحادثة قناة بث (Broadcast Channel) وليست مجموعة تفاعلية؟
    is_broadcast = getattr(entity_obj, 'broadcast', False)
    is_admin = bool(getattr(entity_obj, 'admin_rights', None) or getattr(entity_obj, 'creator', False))
    if is_broadcast and not is_admin:
        permissions["can_send_messages"] = False
        return {
            "group_id": group_id,
            "group_title": group_title,
            "username": username,
            "permissions": permissions,
            "messages_count": 0,
            "messages": [],
            "accessible": False,
            "is_broadcast": True,
            "error": "قناة للبث والمشرفين فقط (ممنوع نشر الأعضاء)"
        }

    # 2. التحقق المسبق: هل الحساب غير منضم للمجموعة أو يتطلب موافقة المشرف؟
    is_left = getattr(entity_obj, 'left', False)
    join_request = getattr(entity_obj, 'join_request', False)
    if is_left and not is_admin:
        permissions["can_send_messages"] = False
        return {
            "group_id": group_id,
            "group_title": group_title,
            "username": username,
            "permissions": permissions,
            "messages_count": 0,
            "messages": [],
            "accessible": False,
            "is_left": True,
            "join_request": join_request,
            "error": "الانضمام يتطلب موافقة يدوية من المشرفين (Join Request)" if join_request else "الحساب غير منضم لهذه المحادثة"
        }

    # 3. فحص صلاحيات المجموعة الافتراضية وصلاحيات الحساب الفردية
    try:
        banned_rights = getattr(entity_obj, 'default_banned_rights', None)
        if banned_rights:
            if getattr(banned_rights, 'send_messages', False):
                permissions["can_send_messages"] = False
            if getattr(banned_rights, 'send_media', False):
                permissions["can_send_media"] = False
            if getattr(banned_rights, 'embed_links', False):
                permissions["can_embed_links"] = False

        user_banned = getattr(entity_obj, 'banned_rights', None)
        if user_banned and getattr(user_banned, 'send_messages', False):
            permissions["can_send_messages"] = False
            return {
                "group_id": group_id,
                "group_title": group_title,
                "username": username,
                "permissions": permissions,
                "messages_count": 0,
                "messages": [],
                "accessible": False,
                "is_banned": True,
                "error": "الحساب مقيد ومكتوم داخل هذه المجموعة بواسطة الإدارة"
            }
    except Exception as e:
        logger.debug(f"Error checking banned_rights: {e}")

    if not permissions["can_send_messages"]:
        return {
            "group_id": group_id,
            "group_title": group_title,
            "username": username,
            "permissions": permissions,
            "messages_count": 0,
            "messages": [],
            "accessible": False,
            "error": "المجموعة مقفلة تماماً وتمنع إرسال الرسائل لجميع الأعضاء"
        }

    try:
        async for msg in client.iter_messages(entity_obj, limit=limit):
            sender = getattr(msg, 'sender', None)
            sender_name = ""
            is_bot = False
            if sender:
                fname = getattr(sender, 'first_name', '') or ''
                lname = getattr(sender, 'last_name', '') or ''
                s_uname = getattr(sender, 'username', '') or ''
                sender_name = f"{fname} {lname}".strip() or s_uname or str(getattr(sender, 'id', ''))
                is_bot = getattr(sender, 'bot', False)

            # التحقق من وجود روابط أو هواتف في الرسالة
            raw_text = msg.raw_text or getattr(msg, 'message', '') or ''
            has_link = bool(re.search(r'(https?://|t\.me/|wa\.me/|@[a-zA-Z0-9_]{4,})', raw_text))
            has_phone = bool(re.search(r'(\+?\d[\d\s\-]{7,}\d)', raw_text))

            action_type = None
            if getattr(msg, 'action', None):
                action_type = type(msg.action).__name__

            if sender and is_bot:
                b_uname = (getattr(sender, 'username', '') or '').strip().lower()
                if b_uname and f"@{b_uname}" not in detected_bots:
                    detected_bots.append(f"@{b_uname}")

            messages_data.append({
                "id": msg.id,
                "sender_id": msg.sender_id,
                "sender_name": sender_name,
                "is_bot": is_bot,
                "text": raw_text[:350],  # اختصار النص للحفاظ على الرموز
                "action": action_type,
                "has_link": has_link,
                "has_phone": has_phone,
                "is_forward": bool(getattr(msg, 'forward', None)),
                "has_media": bool(getattr(msg, 'media', None))
            })

        # فحص الرسائل المثبتة لاستخلاص قواعد المجموعة (مثل منع الأرقام أو الكلمات أو الروابط)
        try:
            from telethon.tl.types import InputMessagesFilterPinned
            pinned_msgs = await client.get_messages(entity_obj, filter=InputMessagesFilterPinned, limit=2)
            for pm in (pinned_msgs or []):
                p_txt = (getattr(pm, 'raw_text', None) or getattr(pm, 'message', '') or '').strip()
                if p_txt:
                    pinned_rules.append(p_txt[:600])
        except Exception:
            pass
    except Exception as e:
        err_msg = str(e)
        logger.warning(f"Error fetching messages for group {group_title}: {err_msg}")
        permissions["can_send_messages"] = False
        return {
            "group_id": group_id,
            "group_title": group_title,
            "username": username,
            "permissions": permissions,
            "messages_count": 0,
            "messages": [],
            "pinned_rules": [],
            "detected_bots": [],
            "accessible": False,
            "error": f"تعذر قراءة رسائل المحادثة ({err_msg})"
        }

    return {
        "group_id": group_id,
        "group_title": group_title,
        "username": username,
        "permissions": permissions,
        "messages_count": len(messages_data),
        "messages": messages_data,
        "pinned_rules": pinned_rules,
        "detected_bots": detected_bots,
        "accessible": True
    }


def _heuristic_analysis(group_data, sample_message=""):
    """تحليل بديل فوري ودقيق في حال عدم توفر أو تأخر واجهة الذكاء الاصطناعي"""
    perms = group_data.get("permissions", {})

    # إذا كانت المجموعة غير متاحة أو مقفلة أو الحساب غير منضم
    if not group_data.get("accessible", True) or not perms.get("can_send_messages", True):
        err_msg = group_data.get("error") or "المجموعة مقفلة تماماً وتمنع إرسال الرسائل للأعضاء"
        return {
            "has_recent_punishments": True,
            "punished_count": 1,
            "details_of_punishments": [err_msg],
            "causes": [err_msg],
            "mistakes_by_others": ["محاولة الإرسال في قناة بث أو مجموعة مقيدة/غير منضم لها"],
            "prohibited_actions": ["skip_group"],
            "keywords_to_avoid": [],
            "risk_assessment": "critical",
            "summary_ar": f"⛔ تخطي فوري: {err_msg}",
            "recommended_action": "تخطي المحادثة تلقائياً لحماية الحساب من الحظر والتقييد."
        }

    messages = group_data.get("messages", [])
    pinned_rules = group_data.get("pinned_rules", []) or []
    detected_bots = group_data.get("detected_bots", []) or []
    punishments = []
    causes = []
    mistakes = []
    prohibited = set()
    keywords_avoid = []
    sanction_texts = list(pinned_rules)
    risk = "low"

    bot_keywords = [
        "تم كتم", "تم طرد", "تم حظر", "حظر", "كتم", "طرد", "ممنوع نشر", "ممنوع الروابط",
        "ممنوع الإعلانات", "ممنوع الاعلانات", "ممنوع الأرقام", "ممنوع الارقام", "ممنوع التوجيه",
        "ممنوع", "محظور", "محضور", "حذف الرسالة", "عدم نشر", "يمنع نشر",
        "warned", "muted", "banned", "kicked", "antispam", "forbidden", "blacklisted"
    ]

    # فحص القوانين المثبتة في المجموعة (إن وجدت)
    for pr in pinned_rules:
        pr_l = pr.lower()
        if any(k in pr_l for k in ["رابط", "روابط", "link", "t.me", "http"]):
            prohibited.add("no_links")
            causes.append("قواعد المجموعة المثبتة تمنع الروابط")
        if any(k in pr_l for k in ["رقم", "ارقام", "أرقام", "هاتف", "جوال", "واتس", "phone", "whatsapp"]):
            prohibited.add("no_phones")
            causes.append("قواعد المجموعة المثبتة تمنع أرقام الهواتف والواتساب")
        if any(k in pr_l for k in ["اعلان", "إعلان", "ترويج", "دعاية", "تسويق", "ads", "spam"]):
            prohibited.add("no_ads")
            causes.append("قواعد المجموعة المثبتة تمنع الإعلانات")

    for m in messages:
        text = m.get("text", "")
        text_l = text.lower()
        action = m.get("action")
        if action in ("MessageActionChatDeleteUser", "MessageActionChatJoinedByLink"):
            if action == "MessageActionChatDeleteUser":
                punishments.append("طرد/مغادرة عضو من المجموعة (Service Action)")
                risk = "medium"

        if any(bw in text_l for bw in bot_keywords) or (m.get("is_bot") and any(w in text_l for w in ["⚠️", "🚫", "❌", "warn", "mute", "ban", "delete", "مخالفة", "تحذير", "إنذار"])):
            sanction_texts.append(text)
            punishments.append(f"تنبيه/عقوبة رصدت: {text[:100]}")
            if any(k in text_l for k in ["رابط", "روابط", "link", "t.me", "http"]):
                causes.append("نشر روابط خارجية أو دعوات")
                prohibited.add("no_links")
                mistakes.append("نشر روابط أدى لكتم أو طرد صاحبها فوراً")
            if any(k in text_l for k in ["رقم", "ارقام", "أرقام", "هاتف", "جوال", "phone", "واتس", "whatsapp"]):
                causes.append("نشر أرقام هواتف أو واتساب")
                prohibited.add("no_phones")
                mistakes.append("نشر أرقام التواصل تسبب في تدخل البوت")
            if any(k in text_l for k in ["تكرار", "سبام", "flood", "spam"]):
                causes.append("تكرار الرسائل بسرعة (سبام)")
                prohibited.add("slow_down")
                mistakes.append("الإرسال المتتالي والسريع تسبب في الحظر التلقائي")
            if any(k in text_l for k in ["توجيه", "forward"]):
                causes.append("تحويل الرسائل من قنوات أخرى")
                prohibited.add("no_forwards")
                mistakes.append("إرسال رسائل محولة مسبقاً")
            if any(k in text_l for k in ["اعلان", "إعلان", "ترويج", "كلمات", "محظور", "محضور", "ممنوع", "سكاليف", "سكليف", "عذر", "اعذار", "واجب", "اختبار", "كويز", "بحث", "صحتي"]):
                causes.append("استخدام كلمات محظورة أو ترويجية ترصدها فلاتر البوتات")
                prohibited.add("no_ads")
                mistakes.append("استخدام كلمات محظورة أدى لحذف الرسالة أو كتم المرسل")

    if not perms.get("can_embed_links", True):
        prohibited.add("no_links")
        causes.append("المجموعة معطل بها ميزة تضمين الروابط")

    # استخراج كافة الكلمات المحظورة من رسائل التحذير والبوتات والقوانين المثبتة
    keywords_avoid = extract_forbidden_keywords_from_texts(sanction_texts)
    if (punishments or "no_ads" in prohibited or detected_bots or any(m.get("is_bot") for m in messages)) and sample_message:
        msg_risk_kws = extract_forbidden_keywords_from_texts([sample_message])
        seen_norm = {_normalize_ar_token(k) for k in keywords_avoid}
        for mk in msg_risk_kws:
            if _normalize_ar_token(mk) not in seen_norm:
                seen_norm.add(_normalize_ar_token(mk))
                keywords_avoid.append(mk)

    if keywords_avoid:
        prohibited.add("keyword_filter")
        prohibited.add("no_ads")

    if punishments:
        risk = "high" if len(punishments) >= 2 else "medium"
    elif detected_bots or pinned_rules:
        if prohibited:
            risk = "medium"

    return {
        "has_recent_punishments": len(punishments) > 0,
        "punished_count": len(punishments),
        "details_of_punishments": punishments[:5],
        "causes": list(set(causes)),
        "mistakes_by_others": list(set(mistakes)),
        "prohibited_actions": list(prohibited),
        "keywords_to_avoid": keywords_avoid,
        "detected_bots": detected_bots,
        "pinned_rules": pinned_rules,
        "risk_assessment": risk,
        "summary_ar": f"تم رصد {len(punishments)} حالة عقوبة أو تنبيه في آخر {len(messages)} رسالة." if punishments else ("تم رصد قواعد/بوتات تنظيمية للمجموعة." if (detected_bots or prohibited) else "لم يُرصد نشاط حظر صارم حديث في آخر 50 رسالة."),
        "recommended_action": "تطبيق الحماية المناسبة لطبيعة المجموعة (السلام عليكم والتعديل، حذف الأرقام/الروابط، أو استبدال الكلمات المحظورة)."
    }


def analyze_group_conversations_with_ai(group_data, sample_message=""):
    """
    تحليل محادثات المجموعة بواسطة Gemini مع fallback للتحليل الذاتي واستخراج كل الكلمات المحظورة
    """
    if not group_data.get("accessible", True) or not group_data.get("permissions", {}).get("can_send_messages", True):
        return _heuristic_analysis(group_data, sample_message=sample_message)

    messages = group_data.get("messages", [])
    if not messages:
        return _heuristic_analysis(group_data, sample_message=sample_message)

    heuristic_res = _heuristic_analysis(group_data, sample_message=sample_message)
    api_key = get_gemini_api_key()
    if not api_key:
        return heuristic_res

    msgs_summary = []
    for idx, m in enumerate(messages[:50], 1):
        sender = f"[{'بوت' if m['is_bot'] else 'عضو'}: {m['sender_name']}]"
        flags = []
        if m.get("action"): flags.append(f"إجراء: {m['action']}")
        if m.get("has_link"): flags.append("يحتوي رابط")
        if m.get("has_phone"): flags.append("يحتوي رقم")
        if m.get("is_forward"): flags.append("محول")
        flag_str = f" ({', '.join(flags)})" if flags else ""
        text_clean = m['text'].replace('\n', ' ').strip()
        msgs_summary.append(f"{idx}. {sender}{flag_str}: {text_clean}")

    chat_corpus = "\n".join(msgs_summary)

    prompt = f"""
أنت خبير محترف في أمان تيليجرام وحماية حسابات النشر والتسويق من الحظر والكتم والقيود.
قم بتحليل آخر 50 رسالة ومحادثة في هذه المجموعة المرفقة:
اسم المجموعة: {group_data.get('group_title')}
صلاحيات النشر العامة: {group_data.get('permissions')}

المطلوب استخراجه وتحليله بدقة:
1. هل تعرض أي عضو مؤخراً للحظر أو الطرد أو الكتم أو تقييد الكتابة من الإدارة أو بوتات الحماية (مثل Rose, GroupHelp, Shield, جبل...)؟
2. ما هي الأسباب التفصيلية للعقوبات؟ (مثل: نشر روابط تليجرام/واتساب، إعلانات، تكرار، توجيه، سبام، أو كلمات محددة محظورة مثل سكاليف/أعذار/واجبات/كويزات/إعلان/ترويج).
3. استخرج كل الكلمات أو العبارات المحظورة أو الحساسة التي تمنعها الإدارة أو البوتات في هذه المجموعة داخل مصفوفة `keywords_to_avoid`.
4. ما هي الإجراءات الوقائية الفورية التي يجب أن نطبقها آلياً على رسالتنا لتجنب مصيرهم وتلافي الحظر تماماً؟
5. قيّم مستوى الخطورة (low, medium, high, critical).

المحادثات الأخيرة (50 رسالة):
{chat_corpus}

الرسالة المزمع إرسالها (إن وجدت لفحص الكلمات التي قد تستفز البوتات):
{sample_message or 'غير محددة'}

أجب بصيغة JSON حصراً بهذا الهيكل الدقيق:
{{
  "has_recent_punishments": true/false,
  "punished_count": 0,
  "details_of_punishments": ["تفاصيل حالات الكتم أو الحظر المرصودة"],
  "causes": ["الأسباب التي أدت للعقوبات"],
  "mistakes_by_others": ["الأخطاء المحددة التي ارتكبها الآخرون"],
  "prohibited_actions": ["no_links", "no_phones", "no_forwards", "no_media", "no_ads", "slow_down", "skip_group"],
  "keywords_to_avoid": ["كل كلمة محظورة أو حساسة تم اكتشافها في المجموعة"],
  "risk_assessment": "low" أو "medium" أو "high" أو "critical",
  "summary_ar": "ملخص شامل باللغة العربية",
  "recommended_action": "توصية الإرسال والوقاية الذكية"
}}
"""

    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.2
        }
    }

    for model in GEMINI_MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=14)
            if resp.status_code == 200:
                res_data = resp.json()
                cand = res_data.get('candidates', [])
                if cand and cand[0].get('content', {}).get('parts'):
                    txt = cand[0]['content']['parts'][0].get('text', '').strip()
                    if txt.startswith("```json"):
                        txt = txt[7:]
                    if txt.endswith("```"):
                        txt = txt[:-3]
                    parsed = json.loads(txt.strip())
                    # دمج الكلمات المحظورة المستخرجة محلياً مع مخرجات Gemini لضمان عدم ضياع أي كلمة
                    merged_kws = extract_forbidden_keywords_from_texts(
                        (parsed.get("causes") or []) + (parsed.get("mistakes_by_others") or []) + (parsed.get("details_of_punishments") or []),
                        extra_keywords=(parsed.get("keywords_to_avoid") or []) + (heuristic_res.get("keywords_to_avoid") or []),
                    )
                    parsed["keywords_to_avoid"] = merged_kws
                    parsed["pinned_rules"] = group_data.get("pinned_rules", []) or []
                    parsed["detected_bots"] = group_data.get("detected_bots", []) or []
                    for extra_act in (heuristic_res.get("prohibited_actions") or []):
                        if extra_act not in (parsed.get("prohibited_actions") or []):
                            parsed.setdefault("prohibited_actions", []).append(extra_act)
                    if merged_kws and "no_ads" not in (parsed.get("prohibited_actions") or []):
                        parsed.setdefault("prohibited_actions", []).append("no_ads")
                    logger.info(f"✅ AI Analysis succeeded using {model} for group: {group_data.get('group_title')}")
                    return parsed
            else:
                logger.warning(f"Model {model} returned status {resp.status_code}")
        except Exception as ex:
            logger.warning(f"Error calling model {model}: {ex}")

    logger.info("Using heuristic analysis fallback for group")
    return heuristic_res


def adapt_message_safely(original_message, analysis, has_media=False):
    """
    تجنب أخطاء الآخرين وتعديل الرسالة وسلوك الإرسال آلياً وتلقائياً:
    - إزالة/تنقية الروابط إذا كانت محظورة
    - تمويه/تعديل أرقام الهواتف إذا سببت حظراً
    - منع التحويل واستبدال الكلمات المحظورة
    - تخطي المجموعة إذا كانت مغلقة أو حظر فوري قطعي
    """
    prohibited = set(analysis.get("prohibited_actions", []))
    risk = analysis.get("risk_assessment", "low")
    actions_taken = []
    adapted_message = original_message or ""
    should_skip = False
    skip_reason = ""
    can_send_media = has_media
    delay_seconds = 7

    # 1. فحص هل المجموعة تتطلب تخطي قطعي لحماية الحساب من الحظر الفوري
    if "skip_group" in prohibited or risk == "critical":
        should_skip = True
        skip_reason = "المجموعة تمنع النشر بالكامل أو تحظر فورياً الحسابات الناشرة"
        actions_taken.append("🛡️ تخطي المجموعة تلقائياً لحماية الحساب من الحظر الدائم")
        return {
            "adapted_message": adapted_message,
            "should_skip": True,
            "skip_reason": skip_reason,
            "actions_taken": actions_taken,
            "can_send_media": False,
            "delay_seconds": delay_seconds
        }

    # 2. حذف الروابط والأرقام فعلياً عند وجود منع لها في المجموعة
    need_strip_links = "no_links" in prohibited or any("رابط" in c for c in analysis.get("causes", []))
    need_strip_phones = "no_phones" in prohibited or any("رقم" in c or "أرقام" in c or "ارقام" in c for c in analysis.get("causes", []))
    if need_strip_links or need_strip_phones:
        adapted_message, strip_acts = strip_phone_numbers_and_links(
            adapted_message,
            strip_phones=need_strip_phones,
            strip_links=need_strip_links,
        )
        actions_taken.extend(strip_acts)

    # 4. فحص الوسائط
    if "no_media" in prohibited and has_media:
        can_send_media = False
        actions_taken.append("🖼️ تحويل الإرسال إلى نصي فقط لأن المجموعة تحظر إرسال الصور/الوسائط")

    # 5. تحويل الكلمات المحظورة المكتشفة إلى الإنجليزية (مثل skalive) أو مباعدة أحرفها (مثل س ك...ال...يف)
    all_reason_texts = (
        list(analysis.get("causes", []))
        + list(analysis.get("mistakes_by_others", []))
        + list(analysis.get("details_of_punishments", []))
        + list(analysis.get("pinned_rules", []))
        + ([analysis.get("summary_ar", "")] if analysis.get("summary_ar") else [])
    )
    keywords_avoid = extract_forbidden_keywords_from_texts(
        all_reason_texts,
        extra_keywords=analysis.get("keywords_to_avoid", []),
    )
    has_keyword_or_ad_ban = (
        "no_ads" in prohibited
        or "keyword_filter" in prohibited
        or risk in ("high", "medium")
        or bool(keywords_avoid)
        or any(t in " ".join(all_reason_texts).lower() for t in ["إعلان", "اعلان", "ترويج", "كلمات", "محظور", "محضور", "ممنوع", "سبام"])
    )
    if has_keyword_or_ad_ban and adapted_message:
        adapted_message, kw_actions = obfuscate_forbidden_words_in_text(
            adapted_message,
            keywords_to_avoid=keywords_avoid,
            include_common_ads=("no_ads" in prohibited or risk in ("high", "medium")),
            mode="auto",
        )
        actions_taken.extend(kw_actions)

    # 6. فاصل الأمان الموحد بين المجموعات
    if "slow_down" in prohibited or risk in ("high", "medium"):
        delay_seconds = 7
        actions_taken.append("⏳ تطبيق فاصل أمان 7 ثوانٍ لتفادي الرصد السريع")

    if not actions_taken:
        actions_taken.append("✅ المحادثة آمنة — لم يُرصد أي مانع أو خطر يستدعي التعديل")

    return {
        "adapted_message": adapted_message,
        "should_skip": False,
        "skip_reason": "",
        "actions_taken": actions_taken,
        "can_send_media": can_send_media,
        "delay_seconds": delay_seconds
    }


def format_saved_messages_report(group_data, analysis, adaptation, sent_status="تم الفحص والتحليل"):
    """
    إنشاء التقرير المفصل لإرساله إلى الرسائل المحفوظة (Saved Messages)
    """
    group_title = group_data.get("group_title", "مجموعة غير معروفة")
    group_id = group_data.get("group_id", "")
    username = group_data.get("username", "")
    group_link = f"@{username}" if username else f"ID: {group_id}"
    now_str = datetime.now().strftime("%Y-%m-%d %I:%M %p")

    risk = analysis.get("risk_assessment", "low").upper()
    risk_emojis = {
        "LOW": "🟢 آمنة ومنخفضة الخطورة",
        "MEDIUM": "🟡 متوسطة الحذر",
        "HIGH": "🔴 شديدة الحراسة والمراقبة",
        "CRITICAL": "⛔ حرجة جداً (خطر حظر فوري)"
    }
    risk_label = risk_emojis.get(risk, "⚪ غير محدد")

    punishments = analysis.get("details_of_punishments", [])
    causes = analysis.get("causes", [])
    mistakes = analysis.get("mistakes_by_others", [])
    actions = adaptation.get("actions_taken", [])

    punish_text = "\n".join([f"  • {p}" for p in punishments[:4]]) if punishments else "  • لم يُرصد حظر أو كتم حديث في آخر 50 رسالة."
    causes_text = "\n".join([f"  • {c}" for c in causes[:4]]) if causes else "  • لا توجد أسباب عقوبات مسجلة."
    mistakes_text = "\n".join([f"  • {m}" for m in mistakes[:4]]) if mistakes else "  • لم يرتكب الأعضاء أخطاء مخالفة مؤخراً."
    actions_text = "\n".join([f"  • {a}" for a in actions]) if actions else "  • تم الإرسال وفق الإعدادات المعتادة."

    report = f"""🛡️ **تقرير الفحص الذكي وحماية الحساب (AI Safety)** 🛡️
━━━━━━━━━━━━━━━━━━━━━
👥 **المجموعة:** {group_title} ({group_link})
⏱️ **وقت التحليل:** {now_str}
📊 **مستوى الأمان:** {risk_label}
🔍 **حالة الإرسال:** {sent_status}

📑 **أولاً: فحص آخر 50 محادثة (العقوبات والقيود):**
{punish_text}

⚠️ **ثانياً: أسباب العقوبات وبوتات الحماية:**
{causes_text}

❌ **ثالثاً: أخطاء الآخرين لتجنبها:**
{mistakes_text}

🛡️ **رابعاً: الإجراءات الوقائية المنفذة تلقائياً لحمايتك:**
{actions_text}

💡 **الملخص الذكي والتوصية:**
{analysis.get('summary_ar', '')}
{analysis.get('recommended_action', '')}
━━━━━━━━━━━━━━━━━━━━━
🤖 *نظام الذكاء الاصطناعي لحماية حسابات التليجرام*"""

    return report


async def send_report_to_saved_messages(client, report_text):
    """إرسال التقرير مباشرة إلى الرسائل المحفوظة الخاصة بالحساب"""
    try:
        if client and client.is_connected():
            await client.send_message('me', report_text, link_preview=False)
            logger.info("✅ Successfully delivered AI group report to Telegram Saved Messages ('me')")
            return True
        else:
            logger.warning("Telegram client not connected; could not send to saved messages")
            return False
    except Exception as e:
        logger.error(f"Failed to deliver AI report to saved messages: {e}")
        return False
