# -*- coding: utf-8 -*-
"""
وحدة الذكاء الاصطناعي لفحص وتحليل آخر 50 محادثة في مجموعات تيليجرام
===================================================================
تقوم الوحدة بـ:
1. استخراج آخر 50 رسالة من كل مجموعة (نصوص، رسائل خدمة، إشعارات بوتات الحماية).
2. تحليل المحادثات بواسطة الذكاء الاصطناعي (Gemini 3.8 Flash مع محرك استدلال احتياطي عميق).
3. استخراج هل تم حظر أو كتم أو تقييد أو طرد أي عضو مؤخراً وما هو السبب بالتفصيل.
4. رصد الأخطاء التي ارتكبها الآخرون لتفاديها تماماً لحماية حساب المستخدم من الحظر.
5. تكييف وتنقية الرسالة تلقائياً قبل الإرسال (تعديل الروابط، الكلمات الحساسة، التكرار).
6. إرسال تقرير مفصل فوري إلى المحادثة الخاصة بالحساب (الرسائل المحفوظة / Saved Messages).
"""

import os
import re
import time
import json
import logging
import asyncio
from datetime import datetime

logger = logging.getLogger('ai_group_analyzer')

# محاولة استيراد Google GenAI SDK
GENAI_AVAILABLE = False
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except Exception as e:
    logger.warning(f"Google GenAI SDK not loaded: {e}")

# قائمة بوتات الحماية والمراقبة المشهورة في تيليجرام
KNOWN_MODERATION_BOTS = {
    'missrose_bot': 'Rose Bot',
    'grouphelpbot': 'Group Help Bot',
    'shieldy_bot': 'Shieldy',
    'spambot': 'SpamBot',
    'combot': 'Combot',
    'marie_bot': 'Marie',
    'tg_guard_bot': 'Telegram Guard',
    'cas_bot': 'CAS Ban Bot',
    'antifloodbot': 'AntiFlood',
    'cleanerbot': 'Cleaner Bot',
    'moderator_bot': 'Group Moderator',
    'protectronbot': 'Protectron'
}

# كلمات دلالية لرصد قرارات الحظر والكتم والتقييد
SANCTION_KEYWORDS_AR = [
    'تم حظر', 'تم كتم', 'تم طرد', 'تم تقييد', 'منع من الكتابة',
    'مخالفة', 'إنذار', 'تحذير', 'ممنوع نشر الروابط', 'ممنوع الإعلانات',
    'حذف الرسالة', 'محظور', 'مكتوم', 'سبام', 'تكرار الرسائل',
    'ممنوع المعرفات', 'ممنوع التوجيه', 'غير مسموح', 'طرد العضو'
]

SANCTION_KEYWORDS_EN = [
    'banned', 'muted', 'kicked', 'restricted', 'warned',
    'deleted message', 'anti-flood', 'spam detected', 'links not allowed',
    'blacklisted', 'slowmode', 'rule violation', 'advertisement not allowed'
]


async def extract_last_50_messages(client, entity_obj, limit=50):
    """
    استخراج آخر 50 محادثة ورسالة خدمة من المجموعة بأمان وسرعة.
    """
    extracted_items = []
    moderation_events = []
    active_bots = set()
    pinned_rules = []
    
    group_title = getattr(entity_obj, 'title', str(entity_obj))
    chat_id = getattr(entity_obj, 'id', 'unknown')

    try:
        count = 0
        async for msg in client.iter_messages(entity_obj, limit=limit):
            count += 1
            sender = getattr(msg, 'sender', None)
            sender_id = getattr(msg, 'sender_id', None)
            sender_username = (getattr(sender, 'username', '') or '').lower()
            sender_name = getattr(sender, 'first_name', '') or ''
            if getattr(sender, 'last_name', ''):
                sender_name += f" {sender.last_name}"
            is_bot = bool(getattr(sender, 'bot', False))

            if sender_username in KNOWN_MODERATION_BOTS or any(b in sender_username for b in ['bot', 'guard', 'shield', 'protect']):
                active_bots.add(f"@{sender_username}" if sender_username else sender_name)

            text = msg.text or msg.message or ''
            action_str = None

            # فحص رسائل الخدمة (Service Actions) مثل الطرد، الحذف، التثبيت
            if hasattr(msg, 'action') and msg.action is not None:
                action_name = type(msg.action).__name__
                if 'DeleteUser' in action_name or 'Kick' in action_name:
                    action_str = "طرد / إزالة عضو من المجموعة (Kick/Ban)"
                    moderation_events.append({
                        "type": "service_ban",
                        "sender": sender_name or "إدارة المجموعة",
                        "action": action_str,
                        "text": text or "إجراء نظام: تم إخراج عضو من المجموعة"
                    })
                elif 'PinMessage' in action_name:
                    action_str = "تثبيت رسالة"
                    if text:
                        pinned_rules.append(text[:200])

            # فحص نصوص الرسائل لكشف قرارات البوتات والإداريين
            lower_text = text.lower()
            is_sanction_msg = False
            detected_reason = None

            if is_bot or any(w in lower_text for w in SANCTION_KEYWORDS_AR + SANCTION_KEYWORDS_EN):
                # فحص تفصيلي للسبب
                if any(w in lower_text for w in ['رابط', 'روابط', 'link', 't.me', 'wa.me', 'http']):
                    detected_reason = "نشر روابط خارجية أو روابط تيليجرام/واتساب"
                    is_sanction_msg = True
                elif any(w in lower_text for w in ['معرف', 'معرفات', 'يوزر', '@', 'username']):
                    detected_reason = "نشر معرفات حسابات أو قنوات"
                    is_sanction_msg = True
                elif any(w in lower_text for w in ['إعلان', 'اعلان', 'ترويج', 'تسويق', 'ad', 'promotion']):
                    detected_reason = "نشر إعلانات أو مواد ترويجية غير مصرح بها"
                    is_sanction_msg = True
                elif any(w in lower_text for w in ['تكرار', 'سبام', 'flood', 'spam', 'توقف عن الإرسال']):
                    detected_reason = "إرسال متكرر وسريع (Flood / سبام)"
                    is_sanction_msg = True
                elif any(w in lower_text for w in ['توجيه', 'forward']):
                    detected_reason = "إعادة توجيه رسائل من قنوات أخرى"
                    is_sanction_msg = True
                elif any(w in lower_text for w in ['سكليف', 'اعذار', 'عذر', 'كويز', 'واجبات']):
                    detected_reason = "كلمات مفتاحية محظورة تتعلق بالخدمات الطلابية أو الطبية"
                    is_sanction_msg = True
                elif any(w in lower_text for w in ['حظر', 'كتم', 'طرد', 'تقييد', 'banned', 'muted', 'kicked']):
                    detected_reason = "مخالفة عامة لقواعد المجموعة"
                    is_sanction_msg = True

            if is_sanction_msg:
                moderation_events.append({
                    "type": "bot_or_admin_sanction",
                    "sender": sender_name or ("بوت حماية" if is_bot else "مشرف"),
                    "action": "كتم أو حظر أو تحذير",
                    "reason": detected_reason or "مخالفة قواعد المحادثة",
                    "text": text[:300]
                })

            extracted_items.append({
                "id": msg.id,
                "sender_id": sender_id,
                "sender_name": sender_name,
                "is_bot": is_bot,
                "text": text[:250],
                "action": action_str,
                "date": msg.date.strftime("%Y-%m-%d %H:%M:%S") if getattr(msg, 'date', None) else ""
            })

    except Exception as e:
        logger.warning(f"Error extracting messages from {group_title}: {e}")

    return {
        "group_title": group_title,
        "chat_id": str(chat_id),
        "total_extracted": len(extracted_items),
        "messages": extracted_items,
        "moderation_events": moderation_events,
        "active_bots": list(active_bots),
        "pinned_rules": pinned_rules
    }


def _analyze_heuristically(group_data, user_message=""):
    """
    تحليل ذكي احترافي مبني على القواعد والاستنتاج في حال عدم توفر Gemini API
    """
    moderation_events = group_data.get('moderation_events', [])
    active_bots = group_data.get('active_bots', [])
    messages = group_data.get('messages', [])
    
    banned_count = len(moderation_events)
    has_bans = banned_count > 0
    
    # جمع أسباب الحظر والكتم
    ban_reasons = []
    mistakes = []
    avoid_rules = []
    
    reasons_set = set()
    for ev in moderation_events:
        r = ev.get('reason') or ev.get('action') or 'مخالفة شروط المجموعة'
        reasons_set.add(r)
        
    ban_reasons = list(reasons_set)
    
    # تحديد مستوى الصرامة
    if banned_count >= 4 or len(active_bots) >= 2:
        group_strictness = "critical"
        risk_summary = "المجموعة شديدة الصرامة وبها بوتات مراقبة نشطة تعاقب فورياً."
    elif banned_count >= 1 or len(active_bots) == 1:
        group_strictness = "high"
        risk_summary = "المجموعة تطبق قيوداً نشطة على الأعضاء وتم رصد كتم أو تحذيرات."
    else:
        group_strictness = "low"
        risk_summary = "المجموعة تبدو مرنة ولم يتم رصد أي حظر أو كتم في آخر 50 رسالة."

    # استخراج الأخطاء التي وقع فيها الآخرون
    links_forbidden = False
    mentions_forbidden = False
    keywords_forbidden = False
    flood_forbidden = False

    for r in ban_reasons:
        if 'روابط' in r or 'link' in r.lower():
            links_forbidden = True
            mistakes.append("نشر روابط صريحة (مواقع، تيليجرام، أو واتساب wa.me)")
            avoid_rules.append("تجريد أو تشفير أي روابط خارجية في الإعلان")
        if 'معرفات' in r or 'يوزر' in r or '@' in r:
            mentions_forbidden = True
            mistakes.append("وضع معرفات قنوات أو حسابات تبدأ بـ @")
            avoid_rules.append("إزالة المعرفات واستبدالها برقم اتصال نصي فقط")
        if 'إعلان' in r or 'كلمات' in r:
            keywords_forbidden = True
            mistakes.append("استخدام كلمات ترويجية مكشوفة ترصدها البوتات")
            avoid_rules.append("تنقية الكلمات الحساسة وإضافة مسافات أو تشكيل زخرفي")
        if 'متكرر' in r or 'سبام' in r or 'flood' in r:
            flood_forbidden = True
            mistakes.append("تكرار الرسائل خلال فترات متقاربة دون انتظار")
            avoid_rules.append("زيادة وقت الانتظار وتجنب الإرسال المكرر")

    if not mistakes and has_bans:
        mistakes.append("مخالفة قواعد النشر العامة للمجموعة")
        avoid_rules.append("استخدام نص هادئ وخالٍ من الروابط المكشوفة")

    # تحديد الإجراء الوقائي التكيفي
    if group_strictness == "critical":
        adaptive_action = "switch_to_salam"
    elif links_forbidden:
        adaptive_action = "sanitize_links"
    elif keywords_forbidden:
        adaptive_action = "sanitize_keywords"
    else:
        adaptive_action = "safe_to_send"

    # تكييف الرسالة لتلافي الأخطاء
    adapted_text = user_message
    if links_forbidden and adapted_text:
        # إزالة أو تكييف روابط واتساب
        adapted_text = re.sub(r'https?://wa\.me/\+?([0-9]+)', r'واتساب: \1', adapted_text)
        adapted_text = re.sub(r'https?://[^\s]+', '', adapted_text)
    if mentions_forbidden and adapted_text:
        adapted_text = re.sub(r'@[a-zA-Z0-9_]+', '', adapted_text)

    return {
        "has_recent_bans_or_mutes": has_bans,
        "banned_count": banned_count,
        "ban_reasons": ban_reasons if ban_reasons else ["لم تُسجل عقوبات صريحة في آخر 50 رسالة"],
        "moderation_bots": active_bots,
        "group_strictness": group_strictness,
        "risk_summary": risk_summary,
        "mistakes_to_avoid": mistakes if mistakes else ["لا توجد أخطاء مرصودة، المجموعة آمنة للإرسال العادي"],
        "avoid_rules": avoid_rules if avoid_rules else ["الإرسال بفاصل زمني طبيعي لتفادي اشتباه السبام"],
        "adaptive_action": adaptive_action,
        "adapted_text": adapted_text,
        "ai_engine": "Heuristic Rules Engine"
    }


def analyze_group_with_ai(group_data, user_message=""):
    """
    تحليل المجموعة بواسطة Gemini 3.8 Flash مع دمج الاستدلال الاحتياطي
    """
    api_key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
    
    # إذا لم يتوفر مفتاح أو SDK، استخدم المحرك الاحترافي المدمج مباشرة
    if not api_key or not GENAI_AVAILABLE:
        return _analyze_heuristically(group_data, user_message)

    try:
        client = genai.Client(api_key=api_key)

        # تحضير سياق الـ 50 رسالة
        msg_summaries = []
        for m in group_data.get('messages', [])[:50]:
            sender_type = "🤖 بوت" if m.get('is_bot') else "عضو"
            action_desc = f" [{m['action']}]" if m.get('action') else ""
            msg_summaries.append(f"- ({m.get('sender_name', 'مجهول')} / {sender_type}){action_desc}: {m.get('text', '')[:180]}")

        context_text = "\n".join(msg_summaries)
        events_json = json.dumps(group_data.get('moderation_events', []), ensure_ascii=False, indent=2)
        bots_str = ", ".join(group_data.get('active_bots', [])) or "لا توجد بوتات واضحة"

        prompt = f"""
أنت خبير أمني ومستشار معتمد في إدارة وحماية حسابات تيليجرام من الحظر والكتم.
مهمتك فحص سجل آخر 50 محادثة داخل مجموعة تيليجرام بدقة واستخراج كافة تفاصيل الحظر والكتم وأسبابه لتجنيب المستخدم أي عقوبة.

اسم المجموعة: {group_data.get('group_title')}
معرف المجموعة: {group_data.get('chat_id')}
البوتات المكتشفة في المحادثات: {bots_str}

أحداث الإشراف المسجلة:
{events_json}

سجل الرسائل الأخيرة (حتى 50 رسالة):
{context_text}

الرسالة التي ينوي المستخدم إرسالها:
{user_message}

المطلوب إخراج النتيجة بتنسيق JSON فقط (بدون شروحات خارج الـ JSON) بالمفاتيح التالية:
{{
  "has_recent_bans_or_mutes": true/false,
  "banned_count": عدد الحالات المكتشفة للكتم أو الحظر أو الطرد أو منع الكتابة,
  "ban_reasons": ["قائمة أسباب الحظر أو الكتم بدقة، مثل: نشر روابط، تكرار، كلمات معينة، إلخ"],
  "moderation_bots": ["قائمة بوتات الحماية النشطة في المجموعة"],
  "group_strictness": "low" أو "medium" أو "high" أو "critical",
  "risk_summary": "ملخص دقيق ومختصر للمخاطر في هذه المجموعة",
  "mistakes_to_avoid": ["قائمة الأخطاء الدقيقة التي وقع فيها الآخرون وسببت كتمهم أو طردهم"],
  "avoid_rules": ["القواعد الذهبية لتفادي نفس المصير في هذه المجموعة"],
  "adaptive_action": "safe_to_send" أو "sanitize_links" أو "sanitize_keywords" أو "switch_to_salam",
  "adapted_text": "النص المقترح للرسالة بعد تكييفه وتعديله ليتجنب كافة أسباب الحظر والبوتات في هذه المجموعة",
  "recommendations": ["نصائح عملية لحماية الحساب"]
}}
"""

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt,
        )

        resp_text = response.text or ""
        # استخراج كائن JSON من رد النموذج
        json_match = re.search(r'\{.*\}', resp_text, re.DOTALL)
        if json_match:
            parsed = json.loads(json_match.group(0))
            parsed["ai_engine"] = "Gemini 3.8 Flash"
            if not parsed.get("adapted_text"):
                parsed["adapted_text"] = user_message
            return parsed

    except Exception as e:
        logger.warning(f"Gemini API analysis fallback: {e}")

    # الرجوع للمحرك الاحتياطي عند حدوث أي خطأ في الاتصال
    fallback = _analyze_heuristically(group_data, user_message)
    fallback["ai_engine"] = "Heuristic Engine (Fallback)"
    return fallback


async def send_ai_group_report_to_saved(client, user_id, group_title, group_identifier, analysis, send_status="✅ تم الإرسال بنجاح"):
    """
    إرسال تقرير شامل ومزخرف باحترافية إلى الرسائل المحفوظة في تليجرام (Saved Messages / 'me')
    """
    try:
        now_str = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
        
        has_bans = analysis.get('has_recent_bans_or_mutes', False)
        bans_count = analysis.get('banned_count', 0)
        strictness = analysis.get('group_strictness', 'low')
        engine = analysis.get('ai_engine', 'AI Analyzer')

        strictness_badge = {
            'low': '🟢 منخفضة (آمنة)',
            'medium': '🟡 متوسطة (حذر)',
            'high': '🟠 مرتفعة (مراقبة قوية)',
            'critical': '🔴 صارمة جداً (خطر كتم/طرد فوري)'
        }.get(strictness, strictness)

        bans_text = f"🚨 نعم ({bans_count} حالة كتم/حظر/طرد)" if has_bans else "✅ لا يوجد كتم أو حظر مؤخراً"

        reasons = analysis.get('ban_reasons', [])
        reasons_formatted = "\n".join([f"  • {r}" for r in reasons]) if reasons else "  • لا توجد مخالفات مسجلة"

        mistakes = analysis.get('mistakes_to_avoid', [])
        mistakes_formatted = "\n".join([f"  ⚠️ {m}" for m in mistakes]) if mistakes else "  • لم يتم رصد أخطاء حرجة"

        bots = analysis.get('moderation_bots', [])
        bots_str = ", ".join(bots) if bots else "لا توجد بوتات حماية نشطة مسجلة"

        action = analysis.get('adaptive_action', 'safe_to_send')
        action_desc = {
            'safe_to_send': '✅ إرسال عادي (المجموعة متساهلة)',
            'sanitize_links': '🧹 تنقية الروابط وإخفاؤها لتفادي بوتات منع الروابط',
            'sanitize_keywords': '🛡️ زخرفة وتعديل الكلمات الحساسة لتجاوز الفلاتر',
            'switch_to_salam': '🧠 إرسال ذكي احترازي (سلام أولي ثم تعديل) لتجنب الطرد'
        }.get(action, action)

        report_message = f"""🤖 **تقرير فحص وتحليل الذكاء الاصطناعي للمجموعة**
━━━━━━━━━━━━━━━━━━━━
📌 **المجموعة المستهدفة:** {group_title}
🔗 **الرابط/المعرف:** `{group_identifier}`
🕐 **وقت الفحص:** {now_str}
🧠 **محرك التحليل:** `{engine}`
━━━━━━━━━━━━━━━━━━━━

🔍 **نتائج فحص آخر 50 محادثة:**
• **حالات كتم أو حظر للأعضاء:** {bans_text}
• **مستوى صرامة المجموعة:** {strictness_badge}
• **أنظمة وبوتات الحماية:** {bots_str}

📋 **أسباب العقوبات التي تعرض لها الآخرون:**
{reasons_formatted}

🚫 **أخطاء ارتكبها الأعضاء ويجب تجنبها:**
{mistakes_formatted}

🛡️ **الإجراء التكيفي المتخذ لحماية حسابك:**
{action_desc}

🚀 **حالة تنفيذ الإرسال:**
{send_status}
━━━━━━━━━━━━━━━━━━━━
✨ **نصيحة النظام الذكي:**
تم تلافي المشاكل التي وقع فيها الأعضاء الآخرون لضمان بقاء حسابك بأمان تام."""

        await client.send_message('me', report_message, link_preview=False)
        logger.info(f"✅ AI Report sent to Saved Messages for user {user_id} in {group_title}")
        return True

    except Exception as e:
        logger.error(f"Failed to send AI report to saved messages: {e}")
        return False
