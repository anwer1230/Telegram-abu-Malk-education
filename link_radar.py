# -*- coding: utf-8 -*-
"""
وحدة رادار الروابط والانضمام الذكي (Link Radar & Smart Auto-Joiner)
- تراقب كامل الحساب وجميع الدردشات فورياً بوضع افتراضي نشط دائماً.
- تتعرف بدقة على روابط الواتساب وروابط التيليجرام العامة والخاصة باستخدام مكتبات واستدعاءات Telethon الأصلية.
- روابط الواتساب: ترسل إشعاراً فورياً للرسائل المحفوظة.
- روابط المجموعات العامة المفتوحة: تنضم إليها تلقائياً وآلياً وترسل إشعاراً بنتيجة الانضمام (تم / انتظار موافقة المشرف / الصلاحية / الوقت).
- روابط القنوات الخاصة: ترسل إشعاراً فورياً يوضح أنها قناة خاصة وتفاصيلها.
- ترسل جميع الروابط الملتقطة إلى وظيفة الروابط المحفوظة لتخزينها في قاعدة البيانات بشكل دائم.
- توفر إحصائيات فورية ثابتة ودائمة لعدد روابط الواتس، التيليجرام العامة، والتيليجرام الخاصة.
"""

import os
import re
import json
import time
import uuid
import logging
import asyncio
from datetime import datetime
from threading import Lock

logger = logging.getLogger("link_radar")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
RADAR_DATA_FILE = os.path.join(DATA_DIR, "link_radar_data.json")

# قفل لمنع التضارب في قراءة/كتابة البيانات
_RADAR_LOCK = Lock()

# قفل لمنع تكرار معالجة نفس الرابط خلال فترة زمنية قصيرة (Deduplication)
_PROCESSED_LINKS_CACHE = {}  # {url: timestamp}
_CACHE_TTL_SECONDS = 900  # 15 دقيقة


class LinkRadarManager:
    def __init__(self):
        self.state = {
            "enabled": True,  # شغال دائماً بوضع افتراضي
            "auto_join_public": True,
            "notify_saved_messages": True,
            "save_to_database": True,
            "stats": {
                "total_links": 0,
                "whatsapp_count": 0,
                "tg_public_count": 0,
                "tg_private_count": 0,
                "joined_success_count": 0,
                "joined_pending_approval": 0,
                "joined_already": 0,
                "failed_or_expired": 0
            },
            "recent_events": []
        }
        self.load_data()

    def load_data(self):
        """تحميل بيانات وإحصائيات الرادار من الملف المحلي"""
        with _RADAR_LOCK:
            try:
                if os.path.exists(RADAR_DATA_FILE):
                    with open(RADAR_DATA_FILE, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        self.state["enabled"] = data.get("enabled", True)
                        self.state["auto_join_public"] = data.get("auto_join_public", True)
                        self.state["notify_saved_messages"] = data.get("notify_saved_messages", True)
                        self.state["save_to_database"] = data.get("save_to_database", True)
                        if "stats" in data:
                            self.state["stats"].update(data["stats"])
                        self.state["recent_events"] = data.get("recent_events", [])[:200]
                else:
                    self.save_data_unlocked()
            except Exception as e:
                logger.error(f"Error loading link radar data: {e}")

    def save_data(self):
        """حفظ بيانات وإحصائيات الرادار بشكل دائم"""
        with _RADAR_LOCK:
            self.save_data_unlocked()

    def save_data_unlocked(self):
        try:
            os.makedirs(DATA_DIR, exist_ok=True)
            with open(RADAR_DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving link radar data: {e}")

    def get_stats(self):
        """الحصول على الإحصائيات الفورية الثابتة"""
        return {
            "enabled": self.state["enabled"],
            "stats": self.state["stats"],
            "total_recent": len(self.state["recent_events"]),
            "last_updated": datetime.now().isoformat()
        }

    def toggle_state(self, enabled=None):
        """تفعيل أو إيقاف المراقبة"""
        if enabled is None:
            self.state["enabled"] = not self.state["enabled"]
        else:
            self.state["enabled"] = bool(enabled)
        self.save_data()
        return self.state["enabled"]

    def clear_recent_events(self):
        """مسح سجل الأحداث الأخيرة مع الاحتفاظ بالعدادات التراكمية"""
        self.state["recent_events"] = []
        self.save_data()
        return True

    def reset_stats(self):
        """تصفير الإحصائيات"""
        for k in self.state["stats"]:
            self.state["stats"][k] = 0
        self.state["recent_events"] = []
        self.save_data()
        return self.state["stats"]

    # ─────────────────────────────────────────────────────────────
    # استخراج وتصنيف الروابط
    # ─────────────────────────────────────────────────────────────

    @staticmethod
    def extract_links_from_text(text, entities=None):
        """استخراج وتنقية كافة الروابط من النص والكيانات"""
        if not text:
            return []

        found_links = []

        # 1. الروابط المضمنة في Entities الخاصة بتيليجرام (MessageEntityTextUrl)
        if entities:
            for ent in entities:
                url_ent = getattr(ent, "url", None)
                if url_ent and url_ent.startswith("http"):
                    found_links.append(url_ent.strip())

        # 2. روابط الواتساب
        wa_patterns = [
            r'https?://chat\.whatsapp\.com/(?:invite/)?[A-Za-z0-9_-]+',
            r'https?://wa\.me/(?:message/)?[A-Za-z0-9+_-]+(?:\?[^\s\n\r<>"\'`]*)?',
            r'https?://api\.whatsapp\.com/send\?[^\s\n\r<>"\'`]+',
            r'https?://(?:www\.)?whatsapp\.com/channel/[A-Za-z0-9_-]+',
        ]
        for pat in wa_patterns:
            for m in re.finditer(pat, text, re.IGNORECASE):
                found_links.append(m.group(0).strip())

        # 3. روابط تيليجرام الخاصة (Invite hashes)
        tg_inv_patterns = [
            r'https?://(?:t(?:elegram)?\.(?:me|dog)|telegram\.org)/(?:\+|joinchat/)([A-Za-z0-9_-]+)',
            r'tg://join\?invite=([A-Za-z0-9_-]+)'
        ]
        for pat in tg_inv_patterns:
            for m in re.finditer(pat, text, re.IGNORECASE):
                found_links.append(m.group(0).strip())

        # 4. روابط تيليجرام العامة
        tg_pub_patterns = [
            r'https?://(?:t(?:elegram)?\.(?:me|dog)|telegram\.org)/([A-Za-z0-9_]{4,32})(?:/[0-9]+)?',
            r'(?:^|\s)@([A-Za-z0-9_]{4,32})(?:\s|$)'
        ]
        for pat in tg_pub_patterns:
            for m in re.finditer(pat, text, re.IGNORECASE):
                matched = m.group(0).strip()
                if matched.startswith("@"):
                    matched = f"https://t.me/{matched[1:]}"
                found_links.append(matched)

        # 5. تنظيف وتصفية الروابط الفريدة
        clean = []
        ignored_tg_paths = {
            'share', 'addstickers', 'addtheme', 'setlanguage', 'socks',
            'proxy', 'bg', 'iv', 'login', 'c', 's', 'contact', 'invoice'
        }
        for link in found_links:
            link = re.sub(r'[.,;:!?)]+$', '', link)
            if not link or link in clean:
                continue

            # استبعاد مسارات تيليجرام غير المخصصة للمجموعات/القنوات
            m_path = re.match(r'https?://(?:t(?:elegram)?\.(?:me|dog)|telegram\.org)/([A-Za-z0-9_]+)', link, re.IGNORECASE)
            if m_path:
                first_part = m_path.group(1).lower()
                if first_part in ignored_tg_paths and not link.startswith("https://t.me/+"):
                    continue

            clean.append(link)

        return clean

    @staticmethod
    def is_whatsapp_link(url):
        """فحص ما إذا كان الرابط تابعاً لواتساب"""
        url_lower = url.lower()
        return ("whatsapp.com" in url_lower or "wa.me" in url_lower)

    @staticmethod
    def is_telegram_link(url):
        """فحص ما إذا كان الرابط تابعاً لتيليجرام"""
        url_lower = url.lower()
        return ("t.me" in url_lower or "telegram.me" in url_lower or "telegram.dog" in url_lower or "tg://" in url_lower)

    @staticmethod
    def is_telegram_invite_link(url):
        """فحص ما إذا كان رابط دعوة خاص لتيليجرام (+ أو joinchat)"""
        return bool(re.search(r'(?:t\.me|telegram\.me|telegram\.dog)/(?:\+|joinchat/)([A-Za-z0-9_-]+)', url, re.IGNORECASE))

    @staticmethod
    def extract_telegram_invite_hash(url):
        """استخراج رمز الدعوة الخاصة من الرابط"""
        m = re.search(r'(?:t\.me|telegram\.me|telegram\.dog)/(?:\+|joinchat/)([A-Za-z0-9_-]+)', url, re.IGNORECASE)
        if m:
            return m.group(1)
        m2 = re.search(r'tg://join\?invite=([A-Za-z0-9_-]+)', url, re.IGNORECASE)
        if m2:
            return m2.group(1)
        return None

    @staticmethod
    def extract_telegram_username(url):
        """استخراج المعرف العام لتيليجرام من الرابط"""
        m = re.search(r'(?:t\.me|telegram\.me|telegram\.dog)/([A-Za-z0-9_]{4,32})', url, re.IGNORECASE)
        if m:
            val = m.group(1)
            if val.lower() not in ('joinchat', 'share', 'addstickers', 'addtheme', 'setlanguage', 'login'):
                return val
        if url.startswith("@"):
            return url[1:].strip()
        return None

    # ─────────────────────────────────────────────────────────────
    # معالجة الروابط الملتقطة والتفاعل الفوري معها
    # ─────────────────────────────────────────────────────────────

    async def handle_captured_link(self, client, link, chat_info, sender_info, message_text, send_to_saved_func, save_to_db_func, socketio_emit_func=None):
        """
        معالجة رابط مكتشف:
        - التحقق من تكرار الرابط في فترة قريبة.
        - التعرف على نوع الرابط (واتساب / تليجرام عامة / تليجرام خاصة).
        - تنفيذ الإجراء المناسب وإرسال الإشعار الفوري للرسائل المحفوظة.
        - حفظه في قاعدة البيانات.
        - تحديث الإحصائيات الفورية وإرسال إشعار WebSocket.
        """
        now = time.time()
        current_time_str = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")

        # فحص كاش منع التكرار
        if link in _PROCESSED_LINKS_CACHE:
            if now - _PROCESSED_LINKS_CACHE[link] < _CACHE_TTL_SECONDS:
                logger.debug(f"[LinkRadar] تم تجاهل رابط متكرر حديثاً: {link}")
                return None
        _PROCESSED_LINKS_CACHE[link] = now

        # تنظيف الكاش القديم دورياً
        if len(_PROCESSED_LINKS_CACHE) > 1500:
            expired_keys = [k for k, v in _PROCESSED_LINKS_CACHE.items() if now - v > _CACHE_TTL_SECONDS]
            for k in expired_keys:
                _PROCESSED_LINKS_CACHE.pop(k, None)

        chat_name = chat_info.get("name") or "دردشة غير معروفة"
        chat_id = chat_info.get("id") or 0
        sender_name = sender_info.get("name") or "مستخدم تيليجرام"
        msg_preview = (message_text or "").strip()
        if len(msg_preview) > 180:
            msg_preview = msg_preview[:180] + "..."

        event_record = {
            "id": str(uuid.uuid4())[:8],
            "timestamp": datetime.now().isoformat(),
            "time_display": current_time_str,
            "link": link,
            "chat_name": chat_name,
            "chat_id": chat_id,
            "sender_name": sender_name,
            "message_preview": msg_preview,
            "type": "other",
            "type_label": "رابط عام",
            "join_status": "تم الالتقاط",
            "is_valid": True,
            "notes": ""
        }

        # ═════════════════════════════════════════════════════════════
        # 1. روابط واتساب (WhatsApp)
        # ═════════════════════════════════════════════════════════════
        if self.is_whatsapp_link(link):
            event_record["type"] = "whatsapp"
            event_record["type_label"] = "واتساب 🟢"
            event_record["join_status"] = "إشعار فوري للرسائل المحفوظة"

            self.state["stats"]["whatsapp_count"] += 1
            self.state["stats"]["total_links"] += 1

            # تكوين إشعار فوري للرسائل المحفوظة
            notif_text = (
                "🟢 <b>رادار الروابط | رصد رابط واتساب جديد</b>\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                f"🔗 <b>الرابط:</b> {link}\n"
                f"📌 <b>النوع:</b> رابط مجموعة / محادثة واتساب\n"
                f"💬 <b>المصدر:</b> {chat_name}\n"
                f"👤 <b>المرسل:</b> {sender_name}\n"
                f"⏰ <b>الوقت:</b> {current_time_str}\n"
                f"📝 <b>مقتطف من الرسالة:</b>\n"
                f"<blockquote>{msg_preview or 'لا يوجد نص مرفق'}</blockquote>\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "✅ <i>تم الحفظ التلقائي في روابطي المحفوظة بقاعدة البيانات</i>"
            )

            try:
                if send_to_saved_func:
                    await send_to_saved_func(notif_text)
                elif client and client.is_connected():
                    await client.send_message('me', notif_text, parse_mode='html', link_preview=False)
            except Exception as e:
                logger.error(f"[LinkRadar] خطأ إرسال إشعار واتساب للمحفوظات: {e}")

            # الحفظ الدائم في الروابط المحفوظة
            if save_to_db_func and self.state.get("save_to_database", True):
                try:
                    save_to_db_func(
                        url=link,
                        title=f"واتساب من {chat_name}",
                        category="واتساب",
                        notes=f"المرسل: {sender_name} | المصدر: {chat_name}",
                        source="رادار الروابط"
                    )
                except Exception as e:
                    logger.error(f"[LinkRadar] خطأ حفظ رابط واتساب في قاعدة البيانات: {e}")

        # ═════════════════════════════════════════════════════════════
        # 2. روابط تيليجرام (Telegram)
        # ═════════════════════════════════════════════════════════════
        elif self.is_telegram_link(link):
            from telethon import types
            from telethon.tl.functions.messages import CheckChatInviteRequest, ImportChatInviteRequest
            from telethon.tl.functions.channels import JoinChannelRequest
            from telethon.errors import (
                UserAlreadyParticipantError,
                InviteHashExpiredError,
                InviteHashInvalidError,
                InviteRequestSentError,
                FloodWaitError,
                ChannelPrivateError
            )

            invite_hash = self.extract_telegram_invite_hash(link)
            username = self.extract_telegram_username(link)

            # ── الحالة أ: رابط دعوة خاص (t.me/+ أو t.me/joinchat/) ──
            if invite_hash:
                title = "قناة/مجموعة خاصة"
                participants = 0
                is_private_channel = False
                is_valid = True
                join_result_msg = ""

                try:
                    chk = await client(CheckChatInviteRequest(invite_hash))
                    if isinstance(chk, types.ChatInviteAlready):
                        chat = getattr(chk, 'chat', None)
                        title = getattr(chat, 'title', title)
                        is_private_channel = bool(getattr(chat, 'broadcast', False))
                        participants = getattr(chat, 'participants_count', 0)
                        join_result_msg = "منضم مسبقاً لهذا الكيان"
                        self.state["stats"]["joined_already"] += 1
                    elif isinstance(chk, types.ChatInvite):
                        title = chk.title or title
                        participants = chk.participants_count or 0
                        is_private_channel = bool(getattr(chk, 'broadcast', False))
                except InviteHashExpiredError:
                    is_valid = False
                    join_result_msg = "انتهت صلاحية الرابط فعلياً"
                    self.state["stats"]["failed_or_expired"] += 1
                except InviteHashInvalidError:
                    is_valid = False
                    join_result_msg = "رابط الدعوة غير صالح أو به نقص"
                    self.state["stats"]["failed_or_expired"] += 1
                except Exception as ce:
                    err_s = str(ce).lower()
                    if "already" in err_s or "participant" in err_s:
                        join_result_msg = "منضم مسبقاً لهذا الكيان"
                        self.state["stats"]["joined_already"] += 1
                    else:
                        join_result_msg = f"فحص الرابط: {str(ce)[:60]}"

                event_record["is_valid"] = is_valid

                # إذا تبين أنها قناة خاصة
                if is_private_channel:
                    event_record["type"] = "tg_private"
                    event_record["type_label"] = "تليجرام خاصة 🔒"
                    event_record["join_status"] = "رابط قناة خاصة (تنبيه فوري)"
                    self.state["stats"]["tg_private_count"] += 1
                    self.state["stats"]["total_links"] += 1

                    validity_badge = "صالحة ونشطة ومؤكدة ✅" if is_valid else f"❌ {join_result_msg}"
                    notif_text = (
                        "🔒 <b>رادار الروابط | رصد رابط قناة تيليجرام خاصة</b>\n"
                        "━━━━━━━━━━━━━━━━━━━━\n"
                        "📢 <b>نوع الرابط:</b> <b>قناة تيليجرام خاصة (Private Channel)</b>\n"
                        f"🏷 <b>اسم القناة:</b> {title}\n"
                        f"🔗 <b>الرابط:</b> {link}\n"
                        f"👥 <b>عدد المشتركين:</b> {participants if participants else 'غير محدد'}\n"
                        f"🔍 <b>حالة الصلاحية:</b> {validity_badge}\n"
                        f"💬 <b>المصدر:</b> {chat_name}\n"
                        f"👤 <b>المرسل:</b> {sender_name}\n"
                        f"⏰ <b>الوقت:</b> {current_time_str}\n"
                        "━━━━━━━━━━━━━━━━━━━━\n"
                        "✅ <i>تم التمييز عبر استدعاءات Telethon الأصلية وحفظ الرابط في روابطي المحفوظة</i>"
                    )

                    try:
                        if send_to_saved_func:
                            await send_to_saved_func(notif_text)
                        elif client and client.is_connected():
                            await client.send_message('me', notif_text, parse_mode='html', link_preview=False)
                    except Exception as e:
                        logger.error(f"[LinkRadar] خطأ إرسال إشعار قناة خاصة للمحفوظات: {e}")

                    if save_to_db_func and self.state.get("save_to_database", True):
                        try:
                            save_to_db_func(
                                url=link,
                                title=f"قناة خاصة: {title}",
                                category="تليجرام خاص",
                                notes=f"قناة خاصة | المصدر: {chat_name} | الصلاحية: {validity_badge}",
                                source="رادار الروابط"
                            )
                        except Exception as e:
                            logger.error(f"[LinkRadar] خطأ حفظ رابط قناة خاصة: {e}")

                # إذا كانت مجموعة خاصة (دعوة)
                else:
                    event_record["type"] = "tg_private"
                    event_record["type_label"] = "تليجرام خاصة (مجموعة) 👥"
                    self.state["stats"]["tg_private_count"] += 1
                    self.state["stats"]["total_links"] += 1

                    if is_valid and not join_result_msg:
                        try:
                            res = await client(ImportChatInviteRequest(invite_hash))
                            join_result_msg = "✅ تم الانضمام بنجاح للمجموعة"
                            self.state["stats"]["joined_success_count"] += 1
                        except UserAlreadyParticipantError:
                            join_result_msg = "ℹ️ منضم مسبقاً للمجموعة"
                            self.state["stats"]["joined_already"] += 1
                        except InviteRequestSentError:
                            join_result_msg = "⏳ ينتظر موافقة المشرف (تم إرسال طلب الانضمام)"
                            self.state["stats"]["joined_pending_approval"] += 1
                        except InviteHashExpiredError:
                            join_result_msg = "❌ انتهت صلاحية الرابط فعلياً"
                            is_valid = False
                            self.state["stats"]["failed_or_expired"] += 1
                        except InviteHashInvalidError:
                            join_result_msg = "❌ رابط الدعوة غير صالح أو به نقص"
                            is_valid = False
                            self.state["stats"]["failed_or_expired"] += 1
                        except Exception as ie:
                            err_str = str(ie).lower()
                            if "already" in err_str or "participant" in err_str:
                                join_result_msg = "ℹ️ منضم مسبقاً للمجموعة"
                                self.state["stats"]["joined_already"] += 1
                            elif "request" in err_str or "admin" in err_str or "approval" in err_str:
                                join_result_msg = "⏳ ينتظر موافقة المشرف (طلب انضمام)"
                                self.state["stats"]["joined_pending_approval"] += 1
                            elif "expired" in err_str:
                                join_result_msg = "❌ انتهت صلاحية الرابط فعلياً"
                                is_valid = False
                                self.state["stats"]["failed_or_expired"] += 1
                            else:
                                join_result_msg = f"⚠️ حالة الانضمام: {str(ie)[:50]}"

                    event_record["join_status"] = join_result_msg or "تم الفحص"
                    event_record["is_valid"] = is_valid

                    validity_badge = "صالح وشغال ✅" if is_valid else "منتهي الصلاحية أو تالف ❌"
                    notif_text = (
                        "👥 <b>رادار الروابط | نتيجة فحص وانضمام رابط مجموعة خاصة</b>\n"
                        "━━━━━━━━━━━━━━━━━━━━\n"
                        f"🏷 <b>اسم المجموعة:</b> {title}\n"
                        f"🔗 <b>الرابط:</b> {link}\n"
                        f"📊 <b>نتيجة الانضمام:</b> <b>{join_result_msg}</b>\n"
                        f"🔍 <b>صلاحية الرابط:</b> {validity_badge}\n"
                        f"💬 <b>المصدر:</b> {chat_name} ({sender_name})\n"
                        f"⏰ <b>الوقت:</b> {current_time_str}\n"
                        "━━━━━━━━━━━━━━━━━━━━\n"
                        "✅ <i>تم الحفظ التلقائي في روابطي المحفوظة بقاعدة البيانات</i>"
                    )

                    try:
                        if send_to_saved_func:
                            await send_to_saved_func(notif_text)
                        elif client and client.is_connected():
                            await client.send_message('me', notif_text, parse_mode='html', link_preview=False)
                    except Exception as e:
                        logger.error(f"[LinkRadar] خطأ إرسال إشعار مجموعة خاصة للمحفوظات: {e}")

                    if save_to_db_func and self.state.get("save_to_database", True):
                        try:
                            save_to_db_func(
                                url=link,
                                title=f"مجموعة خاصة: {title}",
                                category="تليجرام خاص",
                                notes=f"{join_result_msg} | المصدر: {chat_name}",
                                source="رادار الروابط"
                            )
                        except Exception as e:
                            logger.error(f"[LinkRadar] خطأ حفظ مجموعة خاصة: {e}")

            # ── الحالة ب: رابط عام مفتوح (t.me/username) ──
            elif username:
                title = f"@{username}"
                is_broadcast = False
                is_megagroup = False
                is_group = False
                is_valid = True
                join_result_msg = ""
                entity = None

                try:
                    entity = await client.get_entity(username)
                    title = getattr(entity, 'title', None) or getattr(entity, 'first_name', '') or f"@{username}"
                    is_broadcast = bool(getattr(entity, 'broadcast', False))
                    is_megagroup = bool(getattr(entity, 'megagroup', False))
                    is_group = is_megagroup or (not is_broadcast)
                except Exception as ee:
                    err_s = str(ee).lower()
                    if "not found" in err_s or "invalid" in err_s:
                        is_valid = False
                        join_result_msg = "❌ المعرف أو الرابط غير صالح أو به نقص"
                        self.state["stats"]["failed_or_expired"] += 1
                    else:
                        is_group = True  # محاولة اعتباره مجموعة عامة

                # إذا كانت مجموعة عامة مفتوحة
                if is_group and is_valid:
                    event_record["type"] = "tg_public"
                    event_record["type_label"] = "تليجرام عامة (مجموعة) 🌐"
                    self.state["stats"]["tg_public_count"] += 1
                    self.state["stats"]["total_links"] += 1

                    # انضمام تلقائي وآلي فوري
                    try:
                        res = await client(JoinChannelRequest(entity if entity else username))
                        join_result_msg = "✅ تم الانضمام بنجاح للمجموعة العامة"
                        self.state["stats"]["joined_success_count"] += 1
                    except UserAlreadyParticipantError:
                        join_result_msg = "ℹ️ منضم مسبقاً لهذه المجموعة"
                        self.state["stats"]["joined_already"] += 1
                    except FloodWaitError as fwe:
                        join_result_msg = f"⏳ قيود مؤقتة من تيليجرام (يرجى الانتظار {fwe.seconds} ثانية)"
                    except Exception as je:
                        err_str = str(je).lower()
                        if "request" in err_str or "approval" in err_str or "admin" in err_str:
                            join_result_msg = "⏳ ينتظر موافقة المشرف (تم إرسال طلب الانضمام)"
                            self.state["stats"]["joined_pending_approval"] += 1
                        elif "already" in err_str or "participant" in err_str:
                            join_result_msg = "ℹ️ منضم مسبقاً لهذه المجموعة"
                            self.state["stats"]["joined_already"] += 1
                        elif "expired" in err_str:
                            join_result_msg = "❌ انتهت صلاحية الرابط فعلياً"
                            is_valid = False
                            self.state["stats"]["failed_or_expired"] += 1
                        elif "banned" in err_str:
                            join_result_msg = "🚫 الحساب محظور من الانضمام لهذه المجموعة"
                            self.state["stats"]["failed_or_expired"] += 1
                        elif "invalid" in err_str or "not found" in err_str:
                            join_result_msg = "❌ الرابط غير صالح أو هناك نقص في المعرف"
                            is_valid = False
                            self.state["stats"]["failed_or_expired"] += 1
                        else:
                            join_result_msg = f"⚠️ تعذر الانضمام: {str(je)[:60]}"

                    event_record["join_status"] = join_result_msg
                    event_record["is_valid"] = is_valid

                    validity_badge = "صالح ومفتوح وشغال ✅" if is_valid else f"❌ {join_result_msg}"
                    notif_text = (
                        "🤖 <b>رادار الروابط | نتيجة انضمام آلي لمجموعة عامة مفتوحة</b>\n"
                        "━━━━━━━━━━━━━━━━━━━━\n"
                        f"👥 <b>المجموعة:</b> <b>{title}</b> (@{username})\n"
                        f"🔗 <b>الرابط:</b> {link}\n"
                        f"📊 <b>نتيجة الانضمام:</b> <b>{join_result_msg}</b>\n"
                        f"🔍 <b>صلاحية الرابط:</b> {validity_badge}\n"
                        f"💬 <b>المصدر:</b> {chat_name} ({sender_name})\n"
                        f"⏰ <b>الوقت:</b> {current_time_str}\n"
                        "━━━━━━━━━━━━━━━━━━━━\n"
                        "✅ <i>تم الانضمام الآلي وتخزين الرابط في قاعدة البيانات</i>"
                    )

                    try:
                        if send_to_saved_func:
                            await send_to_saved_func(notif_text)
                        elif client and client.is_connected():
                            await client.send_message('me', notif_text, parse_mode='html', link_preview=False)
                    except Exception as e:
                        logger.error(f"[LinkRadar] خطأ إرسال إشعار انضمام مجموعة عامة: {e}")

                    if save_to_db_func and self.state.get("save_to_database", True):
                        try:
                            save_to_db_func(
                                url=link,
                                title=f"مجموعة عامة: {title}",
                                category="تليجرام عام",
                                notes=f"{join_result_msg} | المصدر: {chat_name}",
                                source="رادار الروابط"
                            )
                        except Exception as e:
                            logger.error(f"[LinkRadar] خطأ حفظ مجموعة عامة: {e}")

                # إذا كانت قناة عامة
                elif is_broadcast and is_valid:
                    event_record["type"] = "tg_public"
                    event_record["type_label"] = "تليجرام عامة (قناة) 📢"
                    event_record["join_status"] = "رصد قناة عامة"
                    self.state["stats"]["tg_public_count"] += 1
                    self.state["stats"]["total_links"] += 1

                    notif_text = (
                        "📢 <b>رادار الروابط | تم رصد رابط قناة تيليجرام عامة</b>\n"
                        "━━━━━━━━━━━━━━━━━━━━\n"
                        f"🏷 <b>اسم القناة:</b> {title} (@{username})\n"
                        f"🔗 <b>الرابط:</b> {link}\n"
                        f"💬 <b>المصدر:</b> {chat_name} ({sender_name})\n"
                        f"⏰ <b>الوقت:</b> {current_time_str}\n"
                        "━━━━━━━━━━━━━━━━━━━━\n"
                        "✅ <i>تم الحفظ التلقائي في روابطي المحفوظة بقاعدة البيانات</i>"
                    )

                    try:
                        if send_to_saved_func:
                            await send_to_saved_func(notif_text)
                        elif client and client.is_connected():
                            await client.send_message('me', notif_text, parse_mode='html', link_preview=False)
                    except Exception as e:
                        logger.error(f"[LinkRadar] خطأ إرسال إشعار قناة عامة: {e}")

                    if save_to_db_func and self.state.get("save_to_database", True):
                        try:
                            save_to_db_func(
                                url=link,
                                title=f"قناة عامة: {title}",
                                category="تليجرام عام",
                                notes=f"قناة عامة | المصدر: {chat_name}",
                                source="رادار الروابط"
                            )
                        except Exception as e:
                            logger.error(f"[LinkRadar] خطأ حفظ قناة عامة: {e}")

                else:
                    # رابط غير صالح أو غير معروف
                    event_record["type"] = "tg_public"
                    event_record["type_label"] = "تليجرام ⚠️"
                    event_record["join_status"] = join_result_msg or "غير صالح"
                    event_record["is_valid"] = False
                    self.state["stats"]["failed_or_expired"] += 1
                    self.state["stats"]["total_links"] += 1

        else:
            # رابط خارجي آخر
            event_record["type"] = "other"
            event_record["type_label"] = "رابط ويب 🌐"
            event_record["join_status"] = "تم الرصد"
            self.state["stats"]["total_links"] += 1

            if save_to_db_func and self.state.get("save_to_database", True):
                try:
                    save_to_db_func(
                        url=link,
                        title=f"رابط من {chat_name}",
                        category="عام",
                        notes=f"المصدر: {chat_name}",
                        source="رادار الروابط"
                    )
                except Exception:
                    pass

        # حفظ الحدث في قائمة الأحداث الأخيرة
        self.state["recent_events"].insert(0, event_record)
        if len(self.state["recent_events"]) > 200:
            self.state["recent_events"] = self.state["recent_events"][:200]

        # حفظ التحديثات في الملف
        self.save_data()

        # إرسال إشعار فوري عبر WebSocket لواجهة المستخدم
        if socketio_emit_func:
            try:
                socketio_emit_func("link_radar_update", event_record)
                socketio_emit_func("link_radar_stats", self.get_stats())
            except Exception as se:
                logger.debug(f"[LinkRadar] خطأ إرسال WebSocket: {se}")

        return event_record

    # ─────────────────────────────────────────────────────────────
    # مستمع الرسائل الواردة لـ Telethon
    # ─────────────────────────────────────────────────────────────

    async def handle_new_message_event(self, client, event, user_id, send_to_saved_func, save_to_db_func, socketio_emit_func=None):
        """يتم استدعاء هذه الدالة عند وصول أي رسالة جديدة في أي محادثة أو دردشة بالحساب"""
        if not self.state.get("enabled", True):
            return

        message = getattr(event, "message", None)
        if not message:
            return

        text = getattr(message, "text", "") or getattr(message, "message", "") or ""
        entities = getattr(message, "entities", None)

        links = self.extract_links_from_text(text, entities)
        if not links:
            return

        try:
            chat = await event.get_chat()
            chat_name = getattr(chat, "title", None) or getattr(chat, "first_name", "") or str(getattr(chat, "id", ""))
            chat_id = getattr(chat, "id", 0)
        except Exception:
            chat_name = f"محادثة #{getattr(event, 'chat_id', 0)}"
            chat_id = getattr(event, 'chat_id', 0)

        try:
            sender = await event.get_sender()
            sf = getattr(sender, "first_name", "") or ""
            sl = getattr(sender, "last_name", "") or ""
            sender_name = f"{sf} {sl}".strip() or getattr(sender, "username", None) or str(getattr(sender, "id", "مجهول"))
        except Exception:
            sender_name = "مستخدم"

        chat_info = {"id": chat_id, "name": chat_name}
        sender_info = {"name": sender_name}

        # معالجة كل رابط تم اكتشافه
        for link in links:
            try:
                await self.handle_captured_link(
                    client=client,
                    link=link,
                    chat_info=chat_info,
                    sender_info=sender_info,
                    message_text=text,
                    send_to_saved_func=send_to_saved_func,
                    save_to_db_func=save_to_db_func,
                    socketio_emit_func=socketio_emit_func
                )
            except Exception as le:
                logger.error(f"[LinkRadar] خطأ معالجة الرابط {link}: {le}")


# كائن الإدارة العام للرادار
radar_manager = LinkRadarManager()
