# -*- coding: utf-8 -*-
"""
وحدة الانضمام التلقائي الدائم والمستمر للمجموعات
=================================================
المميزات:
1. تخزين دائم لكافة روابط المجموعات (قاعدة بيانات محلية وFirestore).
2. عند تسجيل دخول أي حساب، يقوم فورياً بفرز كافة المجموعات والقنوات المنضم إليها واستثنائها.
3. يقوم بالانضمام الفوري إلى أول رابط غير منضم، ثم يستمر كل 3 دقائق بالانضمام لرابط جديد.
4. نظام مستمر ودائم وثابت في الخلفية مع معالجة ذكية لقيود التيليجرام (FloodWait).
5. إشعارات فورية إلى الرسائل المحفوظة (Saved Messages) وسجلات النظام وSocketIO.
"""

import asyncio
import json
import logging
import os
import re
import threading
import time
from datetime import datetime

from telethon import functions, types
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest, CheckChatInviteRequest
from telethon.tl.types import ChatInviteAlready, ChatInvite
from telethon.errors import (
    UserAlreadyParticipantError,
    FloodWaitError,
    InviteHashExpiredError,
    InviteHashInvalidError,
    InviteRequestSentError,
    ChannelPrivateError,
    UserBannedInChannelError
)

logger = logging.getLogger("auto_join_daemon")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
PERMANENT_LINKS_FILE = os.path.join(DATA_DIR, "permanent_links.json")
SAVED_LINKS_FILE = os.path.join(DATA_DIR, "saved_links.json")
HISTORY_DIR = os.path.join(DATA_DIR, "join_history")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(HISTORY_DIR, exist_ok=True)

INTERVAL_SECONDS = 180  # 3 دقائق بين كل انضمام


def normalize_telegram_url(raw_url: str) -> str:
    """تنظيف وتوحيد شكل رابط التيليجرام"""
    if not raw_url:
        return ""
    clean = str(raw_url).strip()
    clean = clean.split()[0].rstrip('.,;!?:)')
    if clean.startswith("http://"):
        clean = "https://" + clean[7:]
    if not clean.startswith("https://") and not clean.startswith("tg://"):
        if clean.startswith("@"):
            clean = f"https://t.me/{clean[1:]}"
        elif clean.startswith("t.me/"):
            clean = f"https://{clean}"
    return clean


def extract_link_key(link: str):
    """
    استخراج المفتاح التعريفي للرابط:
    - إما معرف عام (username)
    - أو كود دعوة خاص (invite_hash)
    """
    clean = normalize_telegram_url(link)
    # 1. فحص كود الدعوة الخاص (+ أو joinchat/)
    m_inv = re.search(r'(?:t\.me|telegram\.me|telegram\.dog)/(?:\+|joinchat/)([A-Za-z0-9_-]+)', clean, re.IGNORECASE)
    if m_inv:
        return ("invite", m_inv.group(1))
    
    m_tg = re.search(r'tg://join\?invite=([A-Za-z0-9_-]+)', clean, re.IGNORECASE)
    if m_tg:
        return ("invite", m_tg.group(1))

    # 2. فحص المعرف العام (username)
    m_user = re.search(r'(?:t\.me|telegram\.me)/([A-Za-z0-9_]+)', clean, re.IGNORECASE)
    if m_user:
        u = m_user.group(1).lower()
        if u not in ('joinchat', 'share', 'addstickers', 'addtheme', 'setlanguage', 'login'):
            return ("username", u)

    return ("unknown", clean)


def load_permanent_links() -> list[str]:
    """تحميل قائمة الروابط الدائمة المحفوظة في النظام"""
    links = []
    # 1. من permanent_links.json
    if os.path.exists(PERMANENT_LINKS_FILE):
        try:
            with open(PERMANENT_LINKS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    links.extend(data.get("links", []))
                elif isinstance(data, list):
                    links.extend(data)
        except Exception as e:
            logger.error(f"خطأ في قراءة {PERMANENT_LINKS_FILE}: {e}")

    # 2. من saved_links.json كاحتياط
    if not links and os.path.exists(SAVED_LINKS_FILE):
        try:
            with open(SAVED_LINKS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                items = data.get("links", []) if isinstance(data, dict) else data
                for it in items:
                    u = it.get("url") if isinstance(it, dict) else it
                    if u and ("t.me" in str(u) or "telegram.me" in str(u)):
                        links.append(str(u))
        except Exception as e:
            logger.error(f"خطأ في قراءة {SAVED_LINKS_FILE}: {e}")

    # إزالة التكرار مع الحفاظ على الترتيب
    seen = set()
    cleaned_links = []
    for l in links:
        norm = normalize_telegram_url(l)
        if norm and norm not in seen and norm not in ("https://t.me", "https://t.me/"):
            seen.add(norm)
            cleaned_links.append(norm)

    return cleaned_links


def get_account_history_file(account_identifier: str) -> str:
    safe_name = re.sub(r'[^a-zA-Z0-9_\-]', '_', str(account_identifier))
    return os.path.join(HISTORY_DIR, f"history_{safe_name}.json")


def load_account_history(account_identifier: str) -> dict:
    fpath = get_account_history_file(account_identifier)
    if os.path.exists(fpath):
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"joined": {}, "failed": {}, "last_attempt": None}


def save_account_history(account_identifier: str, history: dict):
    fpath = get_account_history_file(account_identifier)
    try:
        with open(fpath, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"فشل حفظ سجل الحساب {account_identifier}: {e}")


async def get_account_joined_entities(client) -> tuple[set, set]:
    """
    استرجاع معرفات ومفاتيح كافة المجموعات والقنوات التي ينتمي إليها الحساب حالياً
    """
    joined_usernames = set()
    joined_titles = set()
    try:
        # جلب كافة المحادثات (dialogs)
        dialogs = await client.get_dialogs(limit=None)
        for d in dialogs:
            entity = getattr(d, 'entity', None)
            if not entity:
                continue
            username = getattr(entity, 'username', None)
            if username:
                joined_usernames.add(username.lower().strip())
            title = getattr(entity, 'title', None)
            if title:
                joined_titles.add(title.strip().lower())
        logger.info(f"تم فحص المجموعات المنضم إليها: {len(joined_usernames)} معرف، {len(joined_titles)} اسم")
    except Exception as e:
        logger.warning(f"تحذير أثناء فحص محادثات الحساب: {e}")
    return joined_usernames, joined_titles


async def join_single_link(client, link: str, account_name: str = "الحساب") -> dict:
    """
    تنفيذ محاولة الانضمام إلى رابط واحد (عام أو خاص) والتعامل مع كافة الاستجابات
    """
    clean_link = normalize_telegram_url(link)
    kind, val = extract_link_key(clean_link)
    
    res = {
        "url": clean_link,
        "success": False,
        "already": False,
        "pending": False,
        "flood": False,
        "flood_seconds": 0,
        "title": clean_link,
        "message": ""
    }

    # ── الحالة 1: رابط دعوة خاص (+ أو joinchat/) ──
    if kind == "invite":
        invite_hash = val
        title = "مجموعة خاصة"
        try:
            chk = await client(CheckChatInviteRequest(invite_hash))
            if isinstance(chk, ChatInviteAlready):
                chat = getattr(chk, 'chat', None)
                title = getattr(chat, 'title', title)
                res["success"] = True
                res["already"] = True
                res["title"] = title
                res["message"] = "منضم مسبقاً لهذا الكيان"
                return res
            elif isinstance(chk, ChatInvite):
                title = chk.title or title
        except Exception:
            pass

        try:
            await client(ImportChatInviteRequest(invite_hash))
            res["success"] = True
            res["title"] = title
            res["message"] = "تم الانضمام بنجاح للمجموعة الخاصة ✅"
            return res
        except UserAlreadyParticipantError:
            res["success"] = True
            res["already"] = True
            res["title"] = title
            res["message"] = "منضم مسبقاً للمجموعة"
            return res
        except InviteRequestSentError:
            res["success"] = True
            res["pending"] = True
            res["title"] = title
            res["message"] = "تم إرسال طلب الانضمام (بانتظار موافقة المشرف) ⏳"
            return res
        except InviteHashExpiredError:
            res["success"] = False
            res["message"] = "انتهت صلاحية رابط الدعوة ❌"
            return res
        except InviteHashInvalidError:
            res["success"] = False
            res["message"] = "رابط الدعوة غير صالح ❌"
            return res
        except FloodWaitError as fwe:
            res["success"] = False
            res["flood"] = True
            res["flood_seconds"] = fwe.seconds
            res["message"] = f"قيود مؤقتة من تيليجرام (FloodWait {fwe.seconds}s)"
            return res
        except Exception as e:
            err = str(e).lower()
            if "already" in err or "participant" in err:
                res["success"] = True
                res["already"] = True
                res["message"] = "منضم مسبقاً"
            else:
                res["success"] = False
                res["message"] = f"تعذر الانضمام: {str(e)[:70]}"
            return res

    # ── الحالة 2: معرف عام (username) ──
    elif kind == "username":
        username = val
        title = f"@{username}"
        try:
            entity = await client.get_entity(username)
            title = getattr(entity, 'title', None) or getattr(entity, 'first_name', '') or f"@{username}"
            await client(JoinChannelRequest(entity))
            res["success"] = True
            res["title"] = title
            res["message"] = f"تم الانضمام بنجاح للمجموعة العامة: {title} ✅"
            return res
        except UserAlreadyParticipantError:
            res["success"] = True
            res["already"] = True
            res["title"] = title
            res["message"] = f"منضم مسبقاً للمجموعة العامة: {title}"
            return res
        except FloodWaitError as fwe:
            res["success"] = False
            res["flood"] = True
            res["flood_seconds"] = fwe.seconds
            res["message"] = f"قيود مؤقتة من تيليجرام (FloodWait {fwe.seconds}s)"
            return res
        except (ChannelPrivateError, UserBannedInChannelError) as be:
            res["success"] = False
            res["message"] = "المجموعة خاصة أو الحساب محظور منها"
            return res
        except Exception as e:
            err = str(e).lower()
            if "already" in err or "participant" in err:
                res["success"] = True
                res["already"] = True
                res["message"] = "منضم مسبقاً"
            else:
                res["success"] = False
                res["message"] = f"تعذر الانضمام: {str(e)[:70]}"
            return res

    else:
        res["success"] = False
        res["message"] = "صيغة الرابط غير معروفة"
        return res


class PermanentAutoJoinEngine:
    """المحرك الدائم للانضمام التلقائي لكل حساب مسجل"""
    
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        self.running_tasks = {}       # user_id -> Task
        self.stop_events = {}         # user_id -> Event
        self.status_info = {}         # user_id -> dict

    @classmethod
    def get_instance(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = PermanentAutoJoinEngine()
            return cls._instance

    def is_running(self, user_id: str) -> bool:
        t = self.running_tasks.get(user_id)
        return t is not None and not t.done()

    def start_for_manager(self, client_manager):
        """بدء حلقة الانضمام التلقائي الدائمة لهذا الحساب"""
        user_id = str(client_manager.user_id)
        if self.is_running(user_id):
            logger.info(f"محرك الانضمام التلقائي الدائم يعمل بالفعل للحساب {user_id}")
            return

        stop_ev = asyncio.Event()
        self.stop_events[user_id] = stop_ev

        # جدولة الـ Task في event loop الخاص بالـ client_manager
        if client_manager.loop and not client_manager.loop.is_closed():
            coro = self._run_daemon_loop(client_manager, stop_ev)
            task = asyncio.run_coroutine_threadsafe(coro, client_manager.loop)
            self.running_tasks[user_id] = task
            logger.info(f"🚀 تم إطلاق مهمة الانضمام التلقائي الدائم للحساب {user_id}")

    def stop_for_user(self, user_id: str):
        user_id = str(user_id)
        if user_id in self.stop_events:
            self.stop_events[user_id].set()
        task = self.running_tasks.pop(user_id, None)
        if task:
            try:
                task.cancel()
            except Exception:
                pass
        logger.info(f"تم إيقاف مهمة الانضمام التلقائي للحساب {user_id}")

    async def _emit_log(self, user_id: str, message: str):
        logger.info(f"[{user_id}] {message}")
        try:
            # محاولة إرسال إشعار SocketIO إن وجد
            from app import socketio
            socketio.emit('log_update', {'message': message}, to=user_id)
            socketio.emit('auto_join_daemon_update', {
                'user_id': user_id,
                'status': self.status_info.get(user_id, {}),
                'message': message
            }, to=user_id)
        except Exception:
            pass

    async def _run_daemon_loop(self, client_manager, stop_ev: asyncio.Event):
        user_id = str(client_manager.user_id)
        client = client_manager.client

        # انتظر حتى يتصل العميل ويكون جاهزاً وموثقاً
        while not stop_ev.is_set():
            if client and client.is_connected():
                try:
                    if await client.is_user_authorized():
                        break
                except Exception:
                    pass
            await asyncio.sleep(2)

        if stop_ev.is_set():
            return

        # معرف الحساب واسمه وهاتفه
        account_id = client_manager.my_id or user_id
        account_name = client_manager.my_name or getattr(client_manager, 'phone_number', None) or user_id

        await self._emit_log(
            user_id,
            f"🔄 <b>[نظام الانضمام التلقائي الدائم]</b> تم تفعيل الحساب <b>{account_name}</b>. جاري فحص واستثناء المجموعات المنضم إليها..."
        )

        # ── الخطوة 1: فحص المجموعات المنضم إليها واستثنائها ──
        joined_usernames, joined_titles = await get_account_joined_entities(client)
        history = load_account_history(account_id)
        history_joined = history.get("joined", {})

        all_permanent_links = load_permanent_links()
        total_links = len(all_permanent_links)

        # فلترة واستثناء المجموعات المنضم إليها مسبقاً
        already_joined_links = []
        unjoined_links = []

        for link in all_permanent_links:
            kind, val = extract_link_key(link)
            is_already = False
            
            # فحص المعرف العام في المجموعات الحالية
            if kind == "username" and val in joined_usernames:
                is_already = True
            # فحص هل تم الانضمام إليه بنجاح سابقاً في سجل هذا الحساب
            elif link in history_joined and history_joined[link].get("status") in ("joined", "already"):
                is_already = True

            if is_already:
                already_joined_links.append(link)
            else:
                unjoined_links.append(link)

        already_count = len(already_joined_links)
        remaining_count = len(unjoined_links)

        self.status_info[user_id] = {
            "account_name": account_name,
            "total_links": total_links,
            "already_joined_count": already_count,
            "remaining_count": remaining_count,
            "joined_in_current_session": 0,
            "is_active": True,
            "last_action_time": datetime.now().isoformat()
        }

        await self._emit_log(
            user_id,
            f"📊 <b>[إحصائية الفرز]</b> الإجمالي: <b>{total_links}</b> | "
            f"المنضم إليها مسبقاً (مستثناة): <b>{already_count}</b> | "
            f"المتبقي للانضمام التلقائي: <b>{remaining_count}</b> رابطاً (كل 3 دقائق رابط جديد)."
        )

        # ── الخطوة 2: حلقة الانضمام المستمرة كل 3 دقائق ──
        current_index = 0
        joined_session_count = 0

        while not stop_ev.is_set():
            # إذا انتهت القائمة، أعد التحميل في حال أضيفت روابط جديدة
            if current_index >= len(unjoined_links):
                await self._emit_log(user_id, "ℹ️ اكتمل المرور على جميع الروابط الحالية. الانتظار لدورة فحص جديدة...")
                # انتظر 5 دقائق ثم أعد الفحص
                for _ in range(300):
                    if stop_ev.is_set():
                        break
                    await asyncio.sleep(1)
                
                # تحديث القائمة
                all_permanent_links = load_permanent_links()
                joined_usernames, _ = await get_account_joined_entities(client)
                unjoined_links = [
                    l for l in all_permanent_links 
                    if extract_link_key(l)[1] not in joined_usernames 
                    and l not in history_joined
                ]
                current_index = 0
                continue

            target_link = unjoined_links[current_index]
            current_index += 1

            # تنفيذ الانضمام فوراً
            await self._emit_log(
                user_id,
                f"🔗 [{current_index}/{len(unjoined_links)}] جاري الانضمام الفوري إلى: <b>{target_link}</b>..."
            )

            res = await join_single_link(client, target_link, account_name)
            now_iso = datetime.now().isoformat()

            if res["success"]:
                joined_session_count += 1
                status_label = "already" if res.get("already") else ("pending" if res.get("pending") else "joined")
                history["joined"][target_link] = {
                    "status": status_label,
                    "title": res.get("title"),
                    "time": now_iso,
                    "message": res.get("message")
                }
                history["last_attempt"] = now_iso
                save_account_history(account_id, history)

                msg_display = f"✅ <b>{res.get('message')}</b> | المجموعة: <b>{res.get('title')}</b>"
                await self._emit_log(user_id, msg_display)

                # إشعار في الرسائل المحفوظة لحساب المستخدم في التيليجرام
                saved_msg = (
                    "🤖 <b>نظام الانضمام التلقائي الدائم</b>\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    f"👤 <b>الحساب:</b> {account_name}\n"
                    f"🏷 <b>المجموعة:</b> {res.get('title')}\n"
                    f"🔗 <b>الرابط:</b> {target_link}\n"
                    f"📊 <b>النتيجة:</b> {res.get('message')}\n"
                    f"⏰ <b>الوقت:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"⏳ <i>المجموعة التالية بعد 3 دقائق تلقائياً...</i>"
                )
                try:
                    await client_manager.send_to_saved_messages(saved_msg, parse_mode='html')
                except Exception:
                    pass

            else:
                history["failed"][target_link] = {
                    "time": now_iso,
                    "message": res.get("message")
                }
                history["last_attempt"] = now_iso
                save_account_history(account_id, history)

                await self._emit_log(
                    user_id,
                    f"⚠️ <b>نتيجة الانضمام لـ {target_link}:</b> {res.get('message')}"
                )

                # معالجة قيد FloodWait
                if res.get("flood") and res.get("flood_seconds", 0) > 0:
                    wait_sec = res["flood_seconds"]
                    await self._emit_log(
                        user_id,
                        f"⏳ <b>تنبيه تيليجرام (FloodWait):</b> الانتظار لمدة {wait_sec} ثانية وفق تعليمات السيرفر..."
                    )
                    for _ in range(wait_sec):
                        if stop_ev.is_set():
                            break
                        await asyncio.sleep(1)

            # تحديث الإحصاءات
            self.status_info[user_id]["joined_in_current_session"] = joined_session_count
            self.status_info[user_id]["last_action_time"] = now_iso

            # ── الانتظار لمدة 3 دقائق (180 ثانية) بدقة ──
            await self._emit_log(
                user_id,
                f"⏱️ تم الانضمام. انتظام الفاصل الزمني: الانضمام القادم بعد 3 دقائق (180 ثانية)..."
            )
            for _ in range(INTERVAL_SECONDS):
                if stop_ev.is_set():
                    break
                await asyncio.sleep(1)

        logger.info(f"انتهت حلقة الانضمام التلقائي الدائم للحساب {user_id}")


# دالة عامة لربطها في أي مكان يسجل فيه الحساب
def start_auto_join_for_user(client_manager):
    engine = PermanentAutoJoinEngine.get_instance()
    engine.start_for_manager(client_manager)


def stop_auto_join_for_user(user_id: str):
    engine = PermanentAutoJoinEngine.get_instance()
    engine.stop_for_user(user_id)


def get_auto_join_status(user_id: str = "user_1"):
    engine = PermanentAutoJoinEngine.get_instance()
    info = engine.status_info.get(user_id, {})
    return {
        "is_running": engine.is_running(user_id),
        "status": info,
        "permanent_links_count": len(load_permanent_links())
    }
