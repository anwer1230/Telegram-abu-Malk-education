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

logger = logging.getLogger("GroupAiAnalyzer")

# قائمة النماذج المفضلة للاستدعاء بالترتيب
GEMINI_MODELS = [
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash",
    "gemini-flash-latest",
    "gemini-3-flash-preview"
]

async def fetch_group_recent_messages(client, entity_obj, limit=50):
    """
    استخراج آخر 50 رسالة من المجموعة مع فحص القيود وبوتات الإشراف والتحقق المسبق من طبيعة المحادثة
    """
    messages_data = []
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
        "accessible": True
    }


def _heuristic_analysis(group_data):
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
    punishments = []
    causes = []
    mistakes = []
    prohibited = set()
    keywords_avoid = []
    risk = "low"

    bot_keywords = [
        "تم كتم", "تم طرد", "تم حظر", "حظر", "كتم", "طرد", "ممنوع نشر", "ممنوع الروابط",
        "ممنوع الإعلانات", "ممنوع التوجيه", "warned", "muted", "banned", "kicked", "antispam"
    ]

    for m in messages:
        text = m.get("text", "")
        # service actions
        action = m.get("action")
        if action in ("MessageActionChatDeleteUser", "MessageActionChatJoinedByLink"):
            if action == "MessageActionChatDeleteUser":
                punishments.append("طرد/مغادرة عضو من المجموعة (Service Action)")
                risk = "medium"

        # bot or admin warnings
        if any(bw in text for bw in bot_keywords):
            punishments.append(f"تنبيه/عقوبة رصدت: {text[:100]}")
            if any(k in text for k in ["رابط", "روابط", "link", "t.me", "http"]):
                causes.append("نشر روابط خارجية أو دعوات")
                prohibited.add("no_links")
                mistakes.append("نشر روابط أدى لكتم أو طرد صاحبها فوراً")
            if any(k in text for k in ["رقم", "هاتف", "phone", "واتس", "whatsapp"]):
                causes.append("نشر أرقام هواتف أو واتساب")
                prohibited.add("no_phones")
                mistakes.append("نشر أرقام التواصل تسبب في تدخل البوت")
            if any(k in text for k in ["تكرار", "سبام", "flood", "spam"]):
                causes.append("تكرار الرسائل بسرعة (سبام)")
                prohibited.add("slow_down")
                mistakes.append("الإرسال المتتالي والسريع تسبب في الحظر التلقائي")
            if any(k in text for k in ["توجيه", "forward"]):
                causes.append("تحويل الرسائل من قنوات أخرى")
                prohibited.add("no_forwards")
                mistakes.append("إرسال رسائل محولة مسبقاً")

    if not perms.get("can_embed_links", True):
        prohibited.add("no_links")
        causes.append("المجموعة معطل بها ميزة تضمين الروابط")

    if punishments:
        risk = "high" if len(punishments) >= 2 else "medium"

    return {
        "has_recent_punishments": len(punishments) > 0,
        "punished_count": len(punishments),
        "details_of_punishments": punishments[:5],
        "causes": list(set(causes)),
        "mistakes_by_others": list(set(mistakes)),
        "prohibited_actions": list(prohibited),
        "keywords_to_avoid": keywords_avoid,
        "risk_assessment": risk,
        "summary_ar": f"تم رصد {len(punishments)} حالة عقوبة أو تنبيه في آخر {len(messages)} رسالة." if punishments else "لم يُرصد نشاط حظر صارم حديث في آخر 50 رسالة.",
        "recommended_action": "تطبيق الحماية التلقائية وتنقية الروابط والأرقام لتجنب أي عقوبة."
    }


def analyze_group_conversations_with_ai(group_data):
    """
    تحليل محادثات المجموعة بواسطة Gemini مع fallback للتحليل الذاتي
    """
    if not group_data.get("accessible", True) or not group_data.get("permissions", {}).get("can_send_messages", True):
        return _heuristic_analysis(group_data)

    messages = group_data.get("messages", [])
    if not messages:
        return _heuristic_analysis(group_data)

    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        return _heuristic_analysis(group_data)

    # تجهيز ملخص المحادثات للذكاء
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
1. هل تعرض أي عضو مؤخراً للحظر أو الطرد أو الكتم أو تقييد الكتابة من الإدارة أو بوتات الحماية (مثل Rose, GroupHelp, Shield...)؟
2. ما هي الأسباب التفصيلية للعقوبات؟ (مثل: نشر روابط تليجرام/واتساب، إعلانات، تكرار، توجيه، سبام، كلمات محددة).
3. ما هي الأخطاء التي ارتكبها الآخرون وتسببت لهم بالعقوبة؟
4. ما هي الإجراءات الوقائية الفورية التي يجب أن نطبقها آلياً على رسالتنا لتجنب مصيرهم وتلافي الحظر تماماً؟
5. قيّم مستوى الخطورة (low, medium, high, critical).

المحادثات الأخيرة (50 رسالة):
{chat_corpus}

أجب بصيغة JSON حصراً بهذا الهيكل الدقيق:
{{
  "has_recent_punishments": true/false,
  "punished_count": 0,
  "details_of_punishments": ["تفاصيل حالات الكتم أو الحظر المرصودة"],
  "causes": ["الأسباب التي أدت للعقوبات"],
  "mistakes_by_others": ["الأخطاء المحددة التي ارتكبها الآخرون"],
  "prohibited_actions": ["no_links", "no_phones", "no_forwards", "no_media", "slow_down", "skip_group"],
  "keywords_to_avoid": ["كلمات ممنوعة إن وُجدت"],
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
                    # تنظيف markdown if present
                    if txt.startswith("```json"):
                        txt = txt[7:]
                    if txt.endswith("```"):
                        txt = txt[:-3]
                    parsed = json.loads(txt.strip())
                    logger.info(f"✅ AI Analysis succeeded using {model} for group: {group_data.get('group_title')}")
                    return parsed
            else:
                logger.warning(f"Model {model} returned status {resp.status_code}")
        except Exception as ex:
            logger.warning(f"Error calling model {model}: {ex}")

    # Fallback to heuristic
    logger.info("Using heuristic analysis fallback for group")
    return _heuristic_analysis(group_data)


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
    delay_seconds = 3

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

    # 2. تنقية أو إزالة الروابط إذا كانت سبباً لعقوبات الآخرين
    if "no_links" in prohibited or any("رابط" in c for c in analysis.get("causes", [])):
        # تحويل روابط واتساب إلى نص مقروء بدون رابط تشعبي
        wa_match = re.search(r'(?:https?://)?(?:wa\.me|api\.whatsapp\.com/send\?phone=)/?(\+?\d+)', adapted_message)
        if wa_match:
            phone_num = wa_match.group(1)
            adapted_message = re.sub(r'https?://(?:wa\.me|api\.whatsapp\.com/send\?phone=)[^\s]+', f'واتساب: {phone_num}', adapted_message)
            actions_taken.append("🔗 تحويل رابط واتساب إلى نص مباشر بدون رابط تشعبي")

        # إزالة باقي الروابط العامة الخارجية لحمايته كما حدث للآخرين
        if re.search(r'https?://[^\s]+', adapted_message):
            adapted_message = re.sub(r'https?://[^\s]+', '', adapted_message).strip()
            actions_taken.append("🚫 إزالة الروابط الخارجية لتفادي كتم/طرد البوتات الحارسة")

        # إزالة معرفات قنوات تليجرام t.me
        if re.search(r't\.me/[^\s]+', adapted_message):
            adapted_message = re.sub(r't\.me/[^\s]+', '', adapted_message).strip()
            actions_taken.append("📢 إزالة روابط قنوات تليجرام تجنباً لكشف الترويج")

    # 3. تعديل صيغة أرقام الهواتف إذا كانت ممنوعة
    if "no_phones" in prohibited or any("رقم" in c for c in analysis.get("causes", [])):
        # كتابة الأرقام بصيغة متباعدة غير نمطية لتجاوز regex البوتات
        def _mask_phone(m):
            num = m.group(0)
            return " ".join(list(num.replace(" ", "")))
        adapted_message = re.sub(r'\+?\d{8,15}', _mask_phone, adapted_message)
        actions_taken.append("📱 تمويه تنسيق رقم الهاتف لمنع اصطياده من بوتات منع الأرقام")

    # 4. فحص الوسائط
    if "no_media" in prohibited and has_media:
        can_send_media = False
        actions_taken.append("🖼️ تحويل الإرسال إلى نصي فقط لأن المجموعة تحظر إرسال الصور/الوسائط")

    # 5. تنقية الكلمات المحظورة المحددة
    keywords_avoid = analysis.get("keywords_to_avoid", [])
    for kw in keywords_avoid:
        if kw and kw in adapted_message:
            # استبدال الكلمة بنقاط أو مرادف لطيف
            adapted_message = adapted_message.replace(kw, f"[{kw[0]}..{kw[-1]}]")
            actions_taken.append(f"🔤 استبدال الكلمة الحساسة '{kw}' التي سببت كتم أعضاء آخرين")

    # 6. فرض فاصل أمان زمني لتجنب Flood / Spam Detection
    if "slow_down" in prohibited or risk in ("high", "medium"):
        delay_seconds = 8
        actions_taken.append("⏳ تمديد فاصل الانتظار لتفادي الرصد السريع وتجاوز حد الإرسال")

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
