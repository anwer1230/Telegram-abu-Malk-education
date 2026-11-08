"""
╔══════════════════════════════════════════════════════════════╗
║   نظام تسجيل الدخول وإدارة الجلسات لكل مستخدم بشكل منفصل   ║
║            مركز سرعة انجاز - وحدة المصادقة المستقلة          ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import json
import asyncio
import logging
import threading

import threading as _threading
_OSThread = _threading.Thread

from telethon import TelegramClient
from telethon.sessions import StringSession

logger = logging.getLogger('auth')

# ── إعدادات Telegram API ─────────────────────────────────────
TELEGRAM_API_ID   = 22043994
TELEGRAM_API_HASH = '56f64582b363d367280db96586b97801'
API_ID   = int(os.environ.get('TELEGRAM_API_ID', TELEGRAM_API_ID) or TELEGRAM_API_ID)
API_HASH = os.environ.get('TELEGRAM_API_HASH', TELEGRAM_API_HASH) or TELEGRAM_API_HASH

# ── مسار مجلد الجلسات ──────────────────────────────────────
SESSIONS_DIR = os.path.join('/tmp', 'sessions') if os.environ.get('RENDER') else "sessions"
if not os.path.exists(SESSIONS_DIR):
    os.makedirs(SESSIONS_DIR, exist_ok=True)


# ══════════════════════════════════════════════════════════
#  وظائف إدارة ملفات الجلسة — كل مستخدم له مجلده الخاص
# ══════════════════════════════════════════════════════════

def get_user_session_dir(user_id: str) -> str:
    """إرجاع مسار المجلد الخاص بالمستخدم، ويُنشئه إن لم يكن موجوداً"""
    user_dir = os.path.join(SESSIONS_DIR, str(user_id))
    os.makedirs(user_dir, exist_ok=True)
    return user_dir


def save_settings(user_id: str, settings: dict) -> bool:
    """حفظ إعدادات المستخدم في مجلده الخاص + نسخة احتياطية"""
    try:
        user_dir = get_user_session_dir(user_id)
        path = os.path.join(user_dir, "settings.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=4)
        # نسخة احتياطية للتوافق مع الكود القديم
        legacy_path = os.path.join(SESSIONS_DIR, f"{user_id}.json")
        with open(legacy_path, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        logger.error(f"Error saving settings for {user_id}: {e}")
        return False


def load_settings(user_id: str) -> dict:
    """تحميل إعدادات المستخدم — يبحث أولاً في مجلده، ثم الملف القديم"""
    try:
        user_dir = get_user_session_dir(user_id)
        path = os.path.join(user_dir, "settings.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        # fallback للملف القديم
        legacy_path = os.path.join(SESSIONS_DIR, f"{user_id}.json")
        if os.path.exists(legacy_path):
            with open(legacy_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            save_settings(user_id, data)   # ترحيل للمجلد الجديد
            return data
        return {}
    except Exception as e:
        logger.error(f"Error loading settings for {user_id}: {e}")
        return {}


def clear_user_session(user_id: str) -> bool:
    """حذف جميع ملفات الجلسة الخاصة بالمستخدم"""
    try:
        import shutil
        user_dir = get_user_session_dir(user_id)
        if os.path.exists(user_dir):
            shutil.rmtree(user_dir)
        for suffix in [".json", "_session.session", "_string.txt"]:
            p = os.path.join(SESSIONS_DIR, f"{user_id}{suffix}")
            if os.path.exists(p):
                os.remove(p)
        logger.info(f"Cleared session for {user_id}")
        return True
    except Exception as e:
        logger.error(f"Error clearing session for {user_id}: {e}")
        return False


def save_string_session(user_id: str, session_str: str) -> None:
    """حفظ سلسلة StringSession في ملف نصي خاص بالمستخدم"""
    try:
        os.makedirs(SESSIONS_DIR, exist_ok=True)
        path = os.path.join(SESSIONS_DIR, f"{user_id}_string.txt")
        with open(path, 'w') as f:
            f.write(session_str)
        logger.info(f"Saved StringSession for {user_id}")
    except Exception as e:
        logger.error(f"Failed to save StringSession for {user_id}: {e}")


def load_string_session(user_id: str):
    """تحميل سلسلة StringSession من الملف"""
    try:
        path = os.path.join(SESSIONS_DIR, f"{user_id}_string.txt")
        if os.path.exists(path):
            with open(path, 'r') as f:
                val = f.read().strip()
            if val:
                logger.info(f"Loaded StringSession for {user_id}")
                return val
    except Exception as e:
        logger.error(f"Failed to load StringSession for {user_id}: {e}")
    return None


# ══════════════════════════════════════════════════════════
#  TelegramLogin — نظام تسجيل الدخول المستقل لكل مستخدم
# ══════════════════════════════════════════════════════════

class TelegramLogin:
    """
    كائن مستقل لكل مستخدم يدير دورة حياة تسجيل الدخول بالكامل:
      1. إرسال كود التحقق
      2. التحقق من الكود
      3. التحقق الثنائي (2FA) إن وُجد
      4. تسجيل الخروج
    الجلسات محفوظة في مجلد خاص بكل مستخدم لعزلها تماماً.
    """

    def __init__(self, user_id: str):
        self.user_id           = user_id
        self.client            = None
        self.loop              = None
        self.thread            = None
        self.is_ready          = threading.Event()
        self.phone_code_hash   = None
        self.authenticated     = False
        self.connected         = False
        self.awaiting_code     = False
        self.awaiting_password = False
        self.phone_number      = None

    # ── الدورة الداخلية ────────────────────────────────────

    def _run_loop(self):
        """تشغيل حلقة asyncio في OS thread حقيقي — تبقى حية للأبد"""
        self.loop   = asyncio.new_event_loop()
        self.client = TelegramClient(StringSession(), int(API_ID), API_HASH)
        self.loop.run_until_complete(self._connect())
        try:
            self.loop.run_forever()
        finally:
            if not self.loop.is_closed():
                self.loop.close()

    async def _connect(self):
        """الاتصال بخوادم تيليجرام وضبط الحالة"""
        await self.client.connect()
        try:
            self.authenticated = await self.client.is_user_authorized()
        except Exception:
            self.authenticated = False
        self.connected = self.client.is_connected()
        self.is_ready.set()

    # ── الواجهة العامة ─────────────────────────────────────

    def start(self) -> bool:
        """بدء تشغيل العميل في OS thread حقيقي"""
        self.thread = _OSThread(target=self._run_loop, daemon=True)
        self.thread.start()
        return self.is_ready.wait(timeout=30)

    def stop(self):
        """إيقاف العميل وإنهاء الـ loop"""
        if self.loop and self.loop.is_running():
            if self.client:
                try:
                    asyncio.run_coroutine_threadsafe(
                        self.client.disconnect(), self.loop
                    ).result(timeout=5)
                except Exception:
                    pass
            self.loop.call_soon_threadsafe(self.loop.stop)

    def send_code(self, phone_number: str) -> dict:
        """الخطوة 1: إرسال كود التحقق إلى رقم الهاتف"""
        if not self.client or not self.client.is_connected():
            return {"success": False, "message": "العميل غير متصل"}
        try:
            future = asyncio.run_coroutine_threadsafe(
                self.client.send_code_request(phone_number), self.loop
            )
            result = future.result(timeout=30)
            self.phone_number      = phone_number
            self.phone_code_hash   = result.phone_code_hash
            self.awaiting_code     = True
            self.authenticated     = False
            return {
                "success": True,
                "message": "✅ تم إرسال الكود إلى هاتفك",
                "phone_code_hash": self.phone_code_hash
            }
        except Exception as e:
            error_msg = str(e)
            if "FLOOD_WAIT" in error_msg:
                return {"success": False, "message": "⏱️ انتظر قليلاً ثم حاول مرة أخرى"}
            return {"success": False, "message": f"❌ فشل إرسال الكود: {error_msg}"}

    def verify_code(self, code: str) -> dict:
        """الخطوة 2: التحقق من الكود المرسل"""
        if not self.phone_code_hash:
            return {"success": False, "message": "لم يتم طلب كود بعد. أرسل الكود أولاً"}
        if not self.client or not self.client.is_connected():
            return {"success": False, "message": "العميل غير متصل"}
        try:
            future = asyncio.run_coroutine_threadsafe(
                self.client.sign_in(
                    phone=self.phone_number,
                    code=code,
                    phone_code_hash=self.phone_code_hash
                ),
                self.loop
            )
            future.result(timeout=30)
            self.awaiting_code = False
            self.authenticated = True
            # حفظ الجلسة فوراً
            try:
                save_string_session(self.user_id, self.client.session.save())
            except Exception as _se:
                logger.error(f"Could not save session string: {_se}")
            me_future = asyncio.run_coroutine_threadsafe(self.client.get_me(), self.loop)
            me = me_future.result(timeout=30)
            return {
                "success": True,
                "message": "✅ تم تسجيل الدخول بنجاح",
                "user": {
                    "id":         me.id,
                    "first_name": me.first_name,
                    "last_name":  me.last_name,
                    "username":   me.username,
                    "phone":      me.phone,
                    "full_name":  f"{me.first_name or ''} {me.last_name or ''}".strip()
                }
            }
        except Exception as e:
            error_msg = str(e)
            if "PASSWORD" in error_msg.upper() or "SESSION_PASSWORD_NEEDED" in error_msg:
                self.awaiting_password = True
                self.awaiting_code     = False
                return {
                    "success": False,
                    "requires_password": True,
                    "message": "🔐 هذا الحساب محمي بالتحقق بخطوتين. الرجاء إدخال كلمة المرور"
                }
            return {"success": False, "message": f"❌ كود غير صحيح: {error_msg}"}

    def verify_password(self, password: str) -> dict:
        """الخطوة 3: إدخال كلمة مرور التحقق الثنائي (2FA)"""
        if not self.awaiting_password:
            if self.authenticated and self.client and self.client.is_connected():
                try:
                    me_future = asyncio.run_coroutine_threadsafe(self.client.get_me(), self.loop)
                    me = me_future.result(timeout=15)
                    return {
                        "success": True,
                        "message": "✅ تم تسجيل الدخول بنجاح",
                        "user": {
                            "id":         me.id,
                            "first_name": me.first_name,
                            "last_name":  me.last_name,
                            "username":   me.username,
                            "phone":      me.phone,
                            "full_name":  f"{me.first_name or ''} {me.last_name or ''}".strip()
                        }
                    }
                except Exception:
                    pass
            return {"success": False, "message": "الحساب لا يتطلب رمز تحقق ثانوي"}
        if not self.client or not self.client.is_connected():
            return {"success": False, "message": "العميل غير متصل"}
        try:
            future = asyncio.run_coroutine_threadsafe(
                self.client.sign_in(password=password), self.loop
            )
            future.result(timeout=45)
            self.awaiting_password = False
            self.authenticated     = True
            # حفظ الجلسة فوراً
            try:
                save_string_session(self.user_id, self.client.session.save())
            except Exception as _se:
                logger.error(f"Could not save session string (2FA): {_se}")
            me_future = asyncio.run_coroutine_threadsafe(self.client.get_me(), self.loop)
            me = me_future.result(timeout=30)
            return {
                "success": True,
                "message": "✅ تم تسجيل الدخول بنجاح",
                "user": {
                    "id":         me.id,
                    "first_name": me.first_name,
                    "last_name":  me.last_name,
                    "username":   me.username,
                    "phone":      me.phone,
                    "full_name":  f"{me.first_name or ''} {me.last_name or ''}".strip()
                }
            }
        except Exception as e:
            err = str(e)
            if "password" in err.lower() or "invalid" in err.lower():
                return {"success": False, "message": f"❌ كلمة مرور غير صحيحة: {err}"}
            return {"success": False, "message": f"❌ خطأ في التحقق: {err}"}

    def get_login_status(self) -> dict:
        """الحصول على حالة تسجيل الدخول الحالية للمستخدم"""
        status = {
            "authenticated":     self.authenticated,
            "awaiting_code":     self.awaiting_code,
            "awaiting_password": self.awaiting_password,
            "connected":         self.connected,
            "phone_number":      self.phone_number,
            "user":              None
        }
        if self.authenticated and self.client and self.client.is_connected():
            try:
                future = asyncio.run_coroutine_threadsafe(self.client.get_me(), self.loop)
                me = future.result(timeout=10)
                status["user"] = {
                    "id":         me.id,
                    "first_name": me.first_name,
                    "last_name":  me.last_name,
                    "username":   me.username,
                    "phone":      me.phone,
                    "full_name":  f"{me.first_name or ''} {me.last_name or ''}".strip()
                }
            except Exception:
                pass
        return status

    def logout(self) -> dict:
        """تسجيل الخروج من الحساب الحالي وحذف ملفات الجلسة"""
        try:
            if self.client and self.loop and self.client.is_connected():
                future = asyncio.run_coroutine_threadsafe(
                    self.client.log_out(), self.loop
                )
                future.result(timeout=30)
            session_file = os.path.join(SESSIONS_DIR, f"{self.user_id}_session.session")
            if os.path.exists(session_file):
                os.remove(session_file)
            self.authenticated     = False
            self.awaiting_code     = False
            self.awaiting_password = False
            self.phone_number      = None
            self.phone_code_hash   = None
            return {"success": True, "message": "✅ تم تسجيل الخروج بنجاح"}
        except Exception as e:
            return {"success": False, "message": f"❌ خطأ في تسجيل الخروج: {str(e)}"}
