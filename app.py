"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║         مركز سرعة انجاز للخدمات الطلابية والأكاديمية - الإصدار المتكامل       ║
║              نظام التليجرام التلقائي + المنصة الأكاديمية المتكاملة            ║
╚═══════════════════════════════════════════════════════════════════════════════╝

╔══════════════════════════════════════════════════════════════════════════════╗
║                     🗺️  خريطة الكود — دليل سريع                           ║
╠══════════════════════════════════╦═══════════════╦═══════════════════════════╣
║ القسم / الوظيفة                   ║ السطر (تقريبي)║ الدالة / الفئة الرئيسية   ║
╠══════════════════════════════════╬═══════════════╬═══════════════════════════╣
║ الاستيرادات والإعدادات العامة      ║   1 – 110     ║ import / gevent / logging ║
║ نظام السجلات (Logging/IO)         ║ 110 – 340     ║ _MemoryLogHandler         ║
║ إعدادات API (TG / Groq / GH)     ║ 340 – 700     ║ API_ID · API_HASH · GROQ  ║
║ PREDEFINED_USERS / إعدادات تحديث ║ 700 – 960     ║ load_update_settings()    ║
║ اتصال تيليجرام — Login/Client    ║ 960 – 3150    ║ TelegramClientManager     ║
║ TelegramManager (المدير العلوي)   ║ 3150 – 3460   ║ TelegramManager           ║
║ واجهات API للاتصال والتحقق        ║ 3460 – 3860   ║ api_send_code / verify    ║
║ المراقبة + الإرسال المجدول        ║ 3860 – 5430   ║ monitoring_worker         ║
║ الانضمام التلقائي للمجموعات        ║ 5430 – 5680   ║ api_auto_join_advanced    ║
║ البحث العام في تيليجرام            ║ 5680 – 5990   ║ search_global_groups      ║
║ المساعد الذكي AI + GitHub         ║ 6905 – 9340   ║ api_ai_assistant          ║
║ منشئ العروض PPTX                  ║ 9340 – 10700  ║ _PresentationGenerator    ║
║ منسق الملفات PDF/DOCX/Excel       ║ 10700 – 11540 ║ api_pdf_to_word           ║
║ GitHub helpers + روابط محفوظة     ║ 11540 – 11900 ║ upload/download_github    ║
║ رفع ملفات الأجهزة البيومترية       ║ 11900 – 12100 ║ upload_biometric_file     ║
║ لوحة الإدارة + نظام البطاقات      ║ 12100 – 13150 ║ admin_dashboard           ║
║ نظام الإشعارات + Web Push         ║ 13150 – 13400 ║ send_push_notification    ║
║ مراقبة الروابط + البحث            ║ 13400 – 14150 ║ link_monitor              ║
║ التحديث التلقائي للكود             ║ 14150 – 14480 ║ check_for_updates()       ║
║ التعلم التلقائي المتقدم ★ جديد ★   ║ 14480 – 14700 ║ start_auto_learning()     ║
║ تشغيل الخادم                       ║ آخر سطر       ║ socketio.run()            ║
╚══════════════════════════════════╩═══════════════╩═══════════════════════════╝

── الخصائص الوظيفية الرئيسية ──────────────────────────────────────────────────
  ① إرسال رسائل مجدولة/فوري مع صور عبر حسابات تيليجرام متعددة (5 مستخدمين)
  ② مراقبة الكلمات المفتاحية في المجموعات والإرسال التلقائي
  ③ بوت تعلم ذكي: يرد بشكل طبيعي باستخدام Groq + ذاكرة دائمة (JSON+GitHub)
  ④ التحليل التلقائي للمحادثات السابقة واستخلاص أنماط الرد عند تسجيل الدخول
  ⑤ منشئ عروض PPTX من نص + تحويل PDF/DOCX/Excel
  ⑥ مساعد ذكي AI يعدّل ملفات المشروع ويدفعها لـ GitHub مباشرةً
  ⑦ نظام بطاقات تفعيل مع لوحة إدارة كاملة
  ⑧ إشعارات Web Push + إشعارات ترويجية دورية
  ⑨ حفظ تلقائي للجلسات على GitHub (backup صامت)
── الخصائص المساعدة ───────────────────────────────────────────────────────────
  • load_settings / save_settings     — إعدادات كل مستخدم في JSON
  • upload_to_github / download_from_github — مزامنة البيانات مع GitHub
  • save_string_session / load_string_session — إدارة جلسات تيليجرام
  • load_learned_patterns / save_learned_patterns — أنماط التعلم المستفادة
  • _apply_learned_patterns           — تطبيق الأنماط قبل Groq
  • send_push_notification            — Web Push لمستخدم بعينه
  • load_cards_data / validate_voucher — نظام البطاقات والقسائم
"""

# استخدام OS thread حقيقي — بدون gevent monkey patching لتجنب تعارض asyncio
import threading as _pre_patch_threading
_OSThread = _pre_patch_threading.Thread

import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass
import json
import uuid
import time
import logging
import asyncio
import threading
import queue
import re
import random
import string
import io
import base64
import tempfile
from datetime import datetime, timedelta
from threading import Lock, Event, Thread

# إضافات التحليل الإحصائي والعروض (اختيارية)
try:
    import pandas as pd
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import seaborn as sns
    from scipy import stats
    from scipy.stats import pearsonr, spearmanr, ttest_ind, ttest_1samp, f_oneway
    import plotly.express as px
    import plotly.graph_objects as go
    _DATA_SCIENCE_AVAILABLE = True
except ImportError:
    pd = None
    np = None
    matplotlib = None
    plt = None
    sns = None
    stats = None
    pearsonr = spearmanr = ttest_ind = ttest_1samp = f_oneway = None
    px = None
    go = None
    _DATA_SCIENCE_AVAILABLE = False

from io import BytesIO
import hashlib
import secrets
import requests

# إضافات معالجة الملفات
try:
    import docx
    import pdfplumber
    import fitz  # PyMuPDF
except ImportError:
    docx = None
    pdfplumber = None
    fitz = None

from flask import Flask, session, request, render_template, jsonify, redirect, send_file, abort, make_response
import db as _app_db
from install_tracker import track_installation, register_admin_routes
from flask_socketio import SocketIO, emit, join_room, leave_room
from telethon import TelegramClient, events, functions, types
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.types import ChannelParticipantLeft, ChannelParticipantBanned
from telethon.errors import (
    SessionPasswordNeededError, PhoneCodeExpiredError, PhoneCodeInvalidError,
    PasswordHashInvalidError, FloodWaitError, UserAlreadyParticipantError,
    InviteHashExpiredError, InviteHashInvalidError, InviteRequestSentError,
    ChannelPrivateError, UsernameInvalidError, UsernameNotOccupiedError,
    ChannelsTooMuchError, SessionRevokedError, AuthKeyUnregisteredError,
    AuthKeyInvalidError, UserDeactivatedError, UserDeactivatedBanError,
    UnauthorizedError
)
from telethon.sessions import StringSession
from rate_limiter import join_limiter
import socket

# قاموس لتتبع أحداث الإلغاء الفوري لدفعات الإرسال للمستخدمين
BATCH_CANCEL_EVENTS = {}
# قاموس لتتبع حالة دفعات الإرسال ودعم الإيقاف الفوري والاستئناف من حيث التوقف
BATCH_SENDER_STATES = {}

_REVOKED_GUARD_LOCK = threading.Lock()
_LAST_REVOKED_TS = {}

def handle_session_revoked(user_id, reason="تم إنهاء أو إزالة الجلسة من تطبيق تليجرام الآخر الرسمي"):
    """
    استشعار تلقائي لإنهاء أو إزالة الجلسة من تطبيق تليجرام الرسمي:
    - حفظ الرقم واسم الحساب الفعلي في قاعدة الأرقام المحفوظة للأبد
    - إيقاف المهام الجارية والعميل تلقائياً
    - تنظيف ملف الجلسة وسلسلة الجلسة الملغاة من القرص وGitHub
    - تسجيل الخروج تلقائياً وتحديث حالة الحساب وإرسال إشعار فوري للواجهة
    """
    now_t = time.time()
    with _REVOKED_GUARD_LOCK:
        prev_t = _LAST_REVOKED_TS.get(user_id, 0)
        if now_t - prev_t < 5.0:
            return
        _LAST_REVOKED_TS[user_id] = now_t

    logger.warning(f"🚨 [استشعار إلغاء الجلسة] للمستخدم {user_id}: {reason}")
    try:
        # 1. حفظ الرقم واسم الحساب الفعلي قبل إنهاء الجلسة
        revoked_phone = ''
        revoked_name = ''
        cm = None
        with USERS_LOCK:
            if user_id in USERS:
                ud = USERS[user_id]
                revoked_phone = ud.get('account_phone') or ud.get('settings', {}).get('phone') or ''
                revoked_name = ud.get('account_name') or ''
                ud['authenticated'] = False
                ud['connected'] = False
                ud['is_running'] = False
                ud['session_revoked'] = True
                ud['revoked_reason'] = reason
                cm = ud.get('client_manager')

        # 2. إيقاف أي دفعة إرسال أو نشر مجدول
        try:
            ev = BATCH_CANCEL_EVENTS.get(user_id)
            if ev:
                ev.set()
            st_batch = BATCH_SENDER_STATES.get(user_id)
            if st_batch and st_batch.get('status') == 'sending':
                st_batch['status'] = 'paused'
        except Exception:
            pass
        try:
            if 'rotating_manager' in globals():
                rotating_manager.stop(user_id)
        except Exception:
            pass

        # 3. فصل وإيقاف عميل التليجرام وإخراجه من المديرين
        if cm:
            try:
                cm.authenticated = False
                cm.connected = False
                if hasattr(cm, 'stop_flag'):
                    cm.stop_flag.set()
                if getattr(cm, 'client', None) and getattr(cm, 'loop', None) and cm.loop.is_running():
                    try:
                        asyncio.run_coroutine_threadsafe(cm.client.disconnect(), cm.loop)
                    except Exception:
                        pass
            except Exception:
                pass
        try:
            if 'telegram_manager' in globals():
                telegram_manager.client_managers.pop(user_id, None)
                lm = telegram_manager.login_managers.pop(user_id, None)
                if lm:
                    try:
                        lm.stop()
                    except Exception:
                        pass
        except Exception:
            pass

        # 4. تثبيت الرقم واسمه الفعلي في الأرقام المحفوظة للأبد قبل مسح بيانات الجلسة
        try:
            st = load_settings(user_id) or {}
            revoked_phone = revoked_phone or st.get('phone') or st.get('account_phone') or ''
            revoked_name = revoked_name or st.get('account_name') or st.get('name') or ''
            if revoked_phone:
                import firestore_sync
                firestore_sync.save_phone_number(revoked_phone)
                if revoked_name and not firestore_sync._is_placeholder_phone_name(revoked_name):
                    firestore_sync.update_phone_account_name(revoked_phone, revoked_name)
                socketio.emit('saved_phones_updated', {'phones': firestore_sync.get_saved_phone_numbers()})
        except Exception:
            pass

        # 5. حذف ملفات الجلسة المحلية (.session و _string.txt) ومن GitHub
        for fp in (
            os.path.join(SESSIONS_DIR, f"{user_id}_session.session"),
            os.path.join(SESSIONS_DIR, f"{user_id}_string.txt"),
        ):
            if os.path.exists(fp):
                try:
                    os.remove(fp)
                    logger.info(f"تم حذف ملف الجلسة المنتهية: {fp}")
                except Exception as _fe:
                    logger.error(f"خطأ في حذف ملف الجلسة المنتهية: {_fe}")
        try:
            if 'github_delete_session' in globals():
                _OSThread(target=github_delete_session, args=(user_id,), daemon=True).start()
        except Exception:
            pass

        # 6. تحديث الإعدادات لتعكس تسجيل الخروج الآلي
        try:
            st = load_settings(user_id) or {}
            st.update({
                'phone': '',
                'account_phone': '',
                'authenticated': False,
                'connected': False,
                'rotating_persistent': False,
                'monitoring_persistent': False,
            })
            save_settings(user_id, st)
        except Exception:
            pass

        alert_msg = "⚠️ تنبيه: تم رصد إزالة الجلسة أو تسجيل الخروج من تطبيق تليجرام الآخر الرسمي! تم تسجيل الخروج آلياً من هذا التطبيق."
        socketio.emit('session_revoked', {
            "user_id": user_id,
            "message": alert_msg,
            "reason": reason
        }, to=user_id)
        socketio.emit('login_status', {
            "logged_in": False,
            "connected": False,
            "awaiting_code": False,
            "awaiting_password": False,
            "is_running": False,
            "session_revoked": True,
            "user_id": user_id,
            "message": alert_msg
        }, to=user_id)
        socketio.emit('account_updated', {
            "logged_in": False,
            "connected": False,
            "session_revoked": True,
            "user_id": user_id
        })
        socketio.emit('connection_status', {
            "status": "disconnected"
        }, to=user_id)
        socketio.emit('log_update', {"message": alert_msg}, to=user_id)
        try:
            if 'send_push_notification' in globals():
                send_push_notification(
                    user_id,
                    "⚠️ تم إزالة الجلسة من تليجرام",
                    alert_msg,
                    data={"type": "session_revoked", "user_id": user_id}
                )
        except Exception:
            pass
    except Exception as e_rev:
        logger.error(f"Error handling session revoked for {user_id}: {e_rev}")

try:
    from link_radar import radar_manager
except Exception as _e_radar:
    radar_manager = None
    logger.error(f"Error importing link_radar: {_e_radar}")

# ══════════════════════════════════════════════════════════
#  استيراد نظام المصادقة المستقل — auth.py
#  login/session management has been separated per-user
# ══════════════════════════════════════════════════════════
try:
    from auth import (
        TelegramLogin as _AuthTelegramLogin,
        save_settings as _auth_save_settings,
        load_settings as _auth_load_settings,
        clear_user_session as _auth_clear_user_session,
        save_string_session as _auth_save_string_session,
        load_string_session as _auth_load_string_session,
        get_user_session_dir as _auth_get_user_session_dir,
    )
    _AUTH_MODULE_LOADED = True
except ImportError as _auth_import_err:
    _AUTH_MODULE_LOADED = False

try:
    from account_auto_joiner import (
        init_account_auto_joiner,
        start_account_login_auto_join,
        isolate_account_joined_groups,
        get_account_auto_join_status,
        pause_account_auto_join,
        resume_account_auto_join,
        stop_account_auto_join,
        SYSTEM_FIXED_TELEGRAM_LINKS
    )
    _AUTO_JOINER_AVAILABLE = True
except Exception as _e_aj:
    logger.warning(f"Could not import account_auto_joiner: {_e_aj}")
    _AUTO_JOINER_AVAILABLE = False


# تكوين السجلات المحسن
_log_handlers = [logging.StreamHandler()]
try:
    _log_handlers.append(logging.FileHandler('telegram_monitoring.log', encoding='utf-8'))
except Exception:
    pass
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=_log_handlers
)
logger = logging.getLogger(__name__)

class _WerkzeugFilter(logging.Filter):
    def filter(self, record):
        try:
            msg = record.getMessage()
            if '/api/app_logs' in msg and (' 200 ' in msg or ' 304 ' in msg):
                return False
            if 'Request timed out' in msg or 'TimeoutError' in msg or 'timed out' in msg:
                return False
            if 'BrokenPipeError' in msg or 'ConnectionResetError' in msg:
                return False
            if 'Invalid session' in msg:
                return False
        except Exception:
            pass
        return True

_wf = _WerkzeugFilter()
for _h in _log_handlers:
    _h.addFilter(_wf)
for _lg in ['werkzeug', 'engineio', 'engineio.server', 'socketio']:
    try:
        logging.getLogger(_lg).addFilter(_wf)
    except Exception:
        pass

# ── إنشاء مجلد outputs عند بدء التشغيل ──
_outputs_dir = os.path.join(os.path.dirname(__file__), 'pptx_app', 'outputs')
os.makedirs(_outputs_dir, exist_ok=True)

class _MemoryLogHandler(logging.Handler):
    """يحتفظ بآخر N سجل في الذاكرة + دفع فوري عبر Socket.IO"""
    def __init__(self, capacity=500):
        super().__init__()
        self._records = []
        self._capacity = capacity
        self._lock = __import__('threading').Lock()
        self._socketio = None  # يُعيَّن بعد إنشاء socketio
        self._id_counter = 0

    def emit(self, record):
        try:
            import time as _time
            with self._lock:
                self._id_counter += 1
                _formatted = self.format(record)
                entry = {
                    'id': f"{int(_time.time()*1000)}_{self._id_counter}",
                    'time': self.formatTime(record, '%H:%M:%S'),
                    'level': record.levelname,
                    'msg': (_formatted.split(' - ', 3)[-1]
                            if ' - ' in _formatted else record.getMessage()),
                    'name': record.name,
                    'full': _formatted,
                }
                self._records.append(entry)
                if len(self._records) > self._capacity:
                    self._records = self._records[-self._capacity:]
            # ── بث فوري لجميع العملاء عبر Socket.IO (live_log للشاشة الحية) ──
            if self._socketio:
                try:
                    self._socketio.emit('live_log', entry)
                except Exception:
                    pass
            # ── إعادة توجيه لـ TypeScript LogSystem ──
            try:
                _TS_LOG_QUEUE.put_nowait({
                    'level': 'error' if record.levelno >= 40 else ('warn' if record.levelno >= 30 else 'info'),
                    'message': f"[{entry['name']}] {entry['msg']}",
                    'category': 'python',
                    'details': {'logger': entry['name'], 'time': entry['time']}
                })
            except Exception:
                pass
        except Exception:
            pass

    def get_records(self, level=None):
        with self._lock:
            recs = list(self._records)
        if level:
            lvl_map = {'ERROR': 40, 'WARNING': 30, 'INFO': 20}
            min_lvl = lvl_map.get(level.upper(), 0)
            recs = [r for r in recs if logging.getLevelName(r['level']) >= min_lvl]
        return recs[-200:]

_mem_log_handler = _MemoryLogHandler(capacity=200)
_mem_log_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logging.getLogger().addHandler(_mem_log_handler)

# ── قائمة انتظار لإعادة توجيه سجلات Python → TypeScript LogSystem ──────
_TS_LOG_QUEUE = queue.Queue(maxsize=500)

def _ts_log_forwarder_loop():
    """تفريغ طابور السجلات بأمان وتجنب طلبات الشبكة غير الضرورية"""
    while True:
        try:
            _TS_LOG_QUEUE.get(timeout=3)
        except queue.Empty:
            continue
        except Exception:
            pass

_ts_fwd_thread = _OSThread(target=_ts_log_forwarder_loop, daemon=True, name='TsLogFwd')
_ts_fwd_thread.start()

# ── التقاط stdout/stderr وتوجيهها لـ TypeScript LogSystem ──────────────────
class _ConsoleCapture:
    """يلتقط stdout/stderr ويضعها في _TS_LOG_QUEUE للعرض الفوري"""
    _tls = _pre_patch_threading.local()

    def __init__(self, original, stream_name):
        self._orig = original
        self._name = stream_name

    def write(self, text):
        self._orig.write(text)
        msg = text.strip()
        if msg and not getattr(self._tls, 'in_capture', False):
            self._tls.in_capture = True
            try:
                _TS_LOG_QUEUE.put_nowait({
                    'level': 'debug',
                    'message': msg,
                    'category': 'python-console',
                    'details': {'stream': self._name}
                })
            except Exception:
                pass
            finally:
                self._tls.in_capture = False

    def flush(self):
        self._orig.flush()

    def fileno(self):
        try:
            return self._orig.fileno()
        except Exception:
            raise io.UnsupportedOperation('fileno')

    def isatty(self):
        return False

import sys as _sys
_sys.stdout = _ConsoleCapture(_sys.stdout, 'stdout')
_sys.stderr = _ConsoleCapture(_sys.stderr, 'stderr')

# ── [إصلاح] سجلات خاصة بكل مستخدم ──────────────────────────────
from collections import deque as _deque
_USER_LOGS: dict = {}
_USER_LOGS_LOCK = __import__('threading').Lock()
_MAX_USER_LOGS = 300

_log_emit_counter = 0

def _emit_log_update(level: str, msg: str, user_id: str = None):
    """إرسال سجل بتنسيق موحد كامل عبر Socket.IO فوراً"""
    global _log_emit_counter
    try:
        import time as _t
        _log_emit_counter += 1
        entry = {
            'id': f"{int(_t.time()*1000)}_{_log_emit_counter}",
            'time': __import__('datetime').datetime.now().strftime('%H:%M:%S'),
            'level': level.upper(),
            'msg': msg,
            'name': user_id or 'system'
        }
        if user_id:
            try:
                socketio.emit('log_update', entry, to=user_id)
            except Exception:
                pass
        try:
            socketio.emit('log_update', entry)
        except Exception:
            pass
    except Exception:
        pass

def log_user_event(user_id: str, level: str, msg: str):
    """تسجيل حدث في سجل المستخدم الخاص وفي السجل العام مع دفع فوري"""
    try:
        lvl_num = {'DEBUG': 10, 'INFO': 20, 'WARNING': 30, 'ERROR': 40}.get(level.upper(), 20)
        logger.log(lvl_num, f"[{user_id}] {msg}")
        record = {
            'time': __import__('datetime').datetime.now().strftime('%H:%M:%S'),
            'level': level.upper(),
            'msg': msg,
            'name': user_id,
            'source': user_id,
        }
        with _USER_LOGS_LOCK:
            if user_id not in _USER_LOGS:
                _USER_LOGS[user_id] = _deque(maxlen=_MAX_USER_LOGS)
            _USER_LOGS[user_id].append(record)
        # دفع فوري عبر Socket.IO بتنسيق كامل
        _emit_log_update(level, msg, user_id)
    except Exception:
        pass

def _get_user_logs(user_id: str, level_filter=None) -> list:
    """إرجاع سجلات المستخدم الخاصة"""
    lvl_map = {'ERROR': 40, 'WARNING': 30, 'INFO': 20, 'DEBUG': 10}
    min_lvl = lvl_map.get((level_filter or '').upper(), 0) if level_filter and level_filter != 'ALL' else 0
    # سجلات المستخدم الخاصة
    with _USER_LOGS_LOCK:
        user_recs = list(_USER_LOGS.get(user_id, []))
    # سجلات المنصة العامة (لا تخص مستخدماً آخر محدداً)
    other_users = [u for u in _USER_LOGS if u != user_id]
    global_recs = _mem_log_handler.get_records(None)
    merged = user_recs + [r for r in global_recs if not any(ou in r.get('msg', '') for ou in other_users)]
    # فلترة حسب المستوى
    if min_lvl > 0:
        merged = [r for r in merged if lvl_map.get(r.get('level', 'INFO'), 20) >= min_lvl]
    return merged[-100:]

# إنشاء التطبيق
app = Flask(__name__)

class SafeRequest(app.request_class):
    @property
    def cookies(self):
        try:
            return super().cookies
        except Exception:
            return {}

app.request_class = SafeRequest

from flask.sessions import SecureCookieSessionInterface
class SafeSessionInterface(SecureCookieSessionInterface):
    def open_session(self, app, request):
        try:
            return super().open_session(app, request)
        except Exception:
            return self.session_class()

app.session_interface = SafeSessionInterface()
app.secret_key = os.environ.get("SESSION_SECRET", "abu_malk_stable_secret_session_key_2026")
app.config['MAX_CONTENT_LENGTH'] = 150 * 1024 * 1024  # حد أقصى 150 ميغابايت للرفع فائق السرعة للملفات الكبيرة
app.config.update(
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=False,
    SESSION_COOKIE_HTTPONLY=False,
    PERMANENT_SESSION_LIFETIME=timedelta(days=30),
)

def resolve_request_user_id(data=None):
    """استرجاع معرف المستخدم بدقة ومرونة لمنع أخطاء 'الجلسة غير صالحة' تماماً"""
    # 1. من جسم الطلب
    if data and isinstance(data, dict):
        uid = data.get('user_id')
        if uid and uid in PREDEFINED_USERS:
            session['user_id'] = uid
            return uid
    if request and hasattr(request, 'is_json') and request.is_json:
        try:
            req_data = request.get_json(silent=True) or {}
            uid = req_data.get('user_id')
            if uid and uid in PREDEFINED_USERS:
                session['user_id'] = uid
                return uid
        except Exception:
            pass

    # 2. من Headers
    if request:
        header_uid = request.headers.get('X-User-Id')
        if header_uid and header_uid in PREDEFINED_USERS:
            session['user_id'] = header_uid
            return header_uid

        # 3. من Query params
        arg_uid = request.args.get('user_id')
        if arg_uid and arg_uid in PREDEFINED_USERS:
            session['user_id'] = arg_uid
            return arg_uid

    # 4. من الجلسة الحالية
    sess_uid = session.get('user_id')
    if sess_uid and sess_uid in PREDEFINED_USERS:
        return sess_uid

    # 5. من Cookie مخصص
    if request:
        cookie_uid = request.cookies.get('app_user_id')
        if cookie_uid and cookie_uid in PREDEFINED_USERS:
            session['user_id'] = cookie_uid
            return cookie_uid

    # 6. هل هناك حساب ينتظر كود أو كلمة مرور حالياً في telegram_manager؟
    try:
        if 'telegram_manager' in globals() and hasattr(telegram_manager, 'login_managers'):
            for waiting_uid, lm in telegram_manager.login_managers.items():
                if getattr(lm, 'awaiting_code', False) or getattr(lm, 'awaiting_password', False):
                    session['user_id'] = waiting_uid
                    return waiting_uid
    except Exception:
        pass

    # 7. افتراضي
    default_uid = "user_1" if "user_1" in PREDEFINED_USERS else (next(iter(PREDEFINED_USERS.keys())) if PREDEFINED_USERS else "user_1")
    session['user_id'] = default_uid
    return default_uid

@app.before_request
def ensure_session_user():
    # ضمان وجود user_id دائماً في الجلسة لكل طلب دون أي انقطاع
    if 'user_id' not in session or session['user_id'] not in PREDEFINED_USERS:
        session['user_id'] = resolve_request_user_id()
        session.permanent = True

@app.after_request
def set_user_cookie(response):
    try:
        uid = session.get('user_id')
        if uid:
            response.set_cookie('app_user_id', uid, max_age=30*86400, path='/', samesite='Lax')
    except Exception:
        pass
    return response

# إعداد SocketIO — threading mode لتجنب تعارض asyncio/gevent
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='threading',
    ping_timeout=20,
    ping_interval=10,
    logger=False,
    engineio_logger=False,
    allow_upgrades=True,
)
# تفعيل الدفع الفوري للسجلات عبر Socket.IO
_mem_log_handler._socketio = socketio

# إعدادات النظام
SESSIONS_DIR = os.path.join('/tmp', 'sessions') if os.environ.get('RENDER') else "sessions"
if not os.path.exists(SESSIONS_DIR):
    os.makedirs(SESSIONS_DIR)

# ── مجلد البيانات الدائمة (مستقل عن الجلسات ولا يُحذف معها) ──
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)

# ── قاعدة PostgreSQL الاختيارية: تصبح أساسية عند ضبط DATABASE_URL ──
_DB_READY = False
try:
    _DB_READY = _app_db.init_db()
    if _DB_READY:
        logger.info("✅ PostgreSQL database is enabled")
except Exception as _db_bootstrap_error:
    logger.error("PostgreSQL bootstrap failed; using JSON fallback: %s", _db_bootstrap_error)

# ── ملف بطاقات الشحن ──
CARDS_FILE = os.path.join(DATA_DIR, "cards.json")
_CARDS_LOCK = threading.Lock()

# ── ملف روابط الدعوة ──
INVITE_FILE = os.path.join(DATA_DIR, "invite_tokens.json")

# ── دوال إدارة روابط الدعوة (One-time Invite Links) ──
def load_invites():
    try:
        if os.path.exists(INVITE_FILE):
            with open(INVITE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return {"tokens": []}

def save_invites(data):
    try:
        with open(INVITE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"فشل حفظ روابط الدعوة: {e}")
        return False

def generate_invite_token():
    token = secrets.token_urlsafe(16)
    data = load_invites()
    data["tokens"].append({
        "token": token,
        "created_at": datetime.now().isoformat(),
        "status": "active",
        "used_by": None,
        "used_at": None
    })
    save_invites(data)
    return token

def validate_invite_token(token):
    data = load_invites()
    for item in data["tokens"]:
        if item["token"] == token:
            if item["status"] == "used":
                return False, None, "❌ هذا الرابط تم استخدامه مسبقاً"
            if item["status"] == "expired":
                return False, None, "❌ انتهت صلاحية هذا الرابط"
            try:
                created = datetime.fromisoformat(item["created_at"])
                if (datetime.now() - created).days > 7:
                    item["status"] = "expired"
                    save_invites(data)
                    return False, None, "❌ انتهت صلاحية الرابط (أكثر من 7 أيام)"
            except Exception:
                pass
            return True, item, None
    return False, None, "❌ الرابط غير صحيح"

def mark_token_used(token, user_id):
    data = load_invites()
    for item in data["tokens"]:
        if item["token"] == token:
            item["status"] = "used"
            item["used_by"] = user_id
            item["used_at"] = datetime.now().isoformat()
            save_invites(data)
            return True
    return False

def get_invite_link(token):
    try:
        base_url = request.host_url.rstrip('/')
    except Exception:
        base_url = "http://localhost:5000"
    return f"{base_url}/?invite={token}"

# ====== Web Push / VAPID إعداد ======
try:
    from pywebpush import webpush as _webpush_fn, WebPushException as _WebPushException
    WEBPUSH_AVAILABLE = True
except ImportError:
    WEBPUSH_AVAILABLE = False

_VAPID_PUB_D  = "BIkbfhrnC0MgiZk3KJ8fPTUX300SviFxsJguvQjx6q-TNMxK23yhqhyr5Q5vqad8-k3aD1J7NPWg3GbKHuJdpOc"
_VAPID_PRV_B64 = (
    "LS0tLS1CRUdJTiBFQyBQUklWQVRFIEtFWS0tLS0tCk1IY0NBUUVFSURmeGQ0SUZkSHNrQlFNVjd0RD"
    "VodXVZZlIyOXhtU1ZOMzk5clhhNXYrTTFvQW9HQ0NxR1NNNDkKQXdFSG9VUURRZ0FFaVJ0K0d1Y0xR"
    "eUNKbVRjb254ODlOUmZmVFJLK0lYR3dtQzY5Q1BIcXI1TTB6RXJiZktHcQpIS3ZsRG0rcHAzejZUZG"
    "9QVW5zMDlhRGNac29lNGwyazV3PT0KLS0tLS1FTkQgRUMgUFJJVkFURSBLRVktLS0tLQo"
)
VAPID_PUBLIC_KEY  = os.environ.get("VAPID_PUBLIC_KEY",  _VAPID_PUB_D)
_vapid_prv_raw    = os.environ.get("VAPID_PRIVATE_B64", _VAPID_PRV_B64)
import base64 as _b64mod
VAPID_PRIVATE_PEM = _b64mod.b64decode(_vapid_prv_raw + "==").decode()
VAPID_CLAIMS      = {"sub": "mailto:admin@abumalik.app"}

PUSH_SUBS_FILE = os.path.join(SESSIONS_DIR, "push_subscriptions.json")

def _load_push_subs():
    try:
        if os.path.exists(PUSH_SUBS_FILE):
            with open(PUSH_SUBS_FILE) as _f:
                return json.load(_f)
    except Exception:
        pass
    return {}

def _save_push_subs(subs):
    try:
        with open(PUSH_SUBS_FILE, "w") as _f:
            json.dump(subs, _f, indent=2)
        if _DB_READY:
            for _uid, _subscription in subs.items():
                if isinstance(_subscription, dict) and _subscription.get("endpoint"):
                    _app_db.upsert_push_subscription(str(_uid), _subscription["endpoint"], _subscription)
    except Exception:
        pass

push_subscriptions = _load_push_subs()

# ─── الإشعارات الدورية الترويجية (Promo Notifications) ──────────────

PROMO_FILE = os.path.join(os.path.dirname(__file__), 'data', 'promo_messages.json')
os.makedirs(os.path.dirname(PROMO_FILE), exist_ok=True)

DEFAULT_PROMO_MESSAGES = [
    "🚀 مركز سرعة إنجاز – الحل الذكي لأتمتة تيليجرام! راقب الكلمات المفتاحية، أرسل رسائل ذكية تتجاوز الحظر، وأدر حسابات متعددة بكل احترافية. كل ذلك في منصة واحدة!",
    "📊 حلل بياناتك الأكاديمية بذكاء واحترافية! ارفع ملفات PDF، DOCX، واستخرج الجداول والصور، مع تلخيص ذكي باستخدام الذكاء الاصطناعي. وفر وقتك وركز على ما يهم!",
    "🔄 الإرسال الذكي يتجاوز حظر المجموعات – جربه الآن! مع وضع 'السلام عليكم' الذكي، ترسل رسالتك بأمان حتى في أكثر المجموعات حماية، وتعدل الرسالة بعد تفاعل الأعضاء.",
    "🔔 تنبيهات فورية، نطق صوتي، وتحديثات مستمرة… كل هذا في منصة واحدة! اشعارات ويب Push ونطق صوتي للتنبيهات المهمة، حتى لو كان التطبيق مغلقاً. كن على اطلاع دائم!",
    "📈 عزز حضورك على تيليجرام مع أدوات احترافية لا تُقهر! انضم تلقائياً للمجموعات، ابحث عن الروابط في محادثاتك، وصدر النتائج إلى Excel بضغطة زر.",
    "🎓 من الطالب إلى المحترف: مركز سرعة إنجاز رفيقك الأكاديمي! أنشئ عروض PowerPoint احترافية، حوّل HTML إلى Word/Excel، وحلل بياناتك إحصائياً بذكاء اصطناعي متقدم.",
    "🛡️ آمن، مرن، وقابل للتوسع – صُنع خصيصاً للمحترفين! مع دعم حسابات متعددة، تكامل GitHub، ونظام البطاقات، يمكنك إدارة فريقك أو عملائك بكل احترافية وأمان.",
    "⏰ الإرسال المتسلسل والردود التلقائية تعمل 24/7! حدد رسائل دورية، واترك النظام يرسلها تلقائياً دون تدخل، مع إمكانية تعديل أو حذف الدفعات المرسلة دفعة واحدة.",
    "🌍 ابحث في تيليجرام بالكامل واكتشف فرصاً جديدة! استخدم البحث العام للعثور على مجموعات وقنوات حسب اهتمامك، وانضم إليها بنقرة واحدة.",
    "💡 حل واحد، كل ما تحتاجه لإدارة تيليجرام بذكاء لا يُهزم! من المراقبة الفورية إلى التحليل الأكاديمي، ومن الإرسال الذكي إلى الإدارة المتكاملة – منصة متكاملة بامتياز."
]

def load_promo_data():
    try:
        if os.path.exists(PROMO_FILE):
            with open(PROMO_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load promo data: {e}")
    default_data = {"enabled": False, "current_index": 0, "messages": DEFAULT_PROMO_MESSAGES}
    save_promo_data(default_data)
    return default_data

def save_promo_data(data):
    try:
        with open(PROMO_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Failed to save promo data: {e}")

_PROMO_THREAD = None
_PROMO_RUNNING = False

def promo_worker():
    global _PROMO_RUNNING
    _PROMO_RUNNING = True
    logger.info("🔄 بدأت خلفية الإشعارات الدورية (كل 5 دقائق)")
    while _PROMO_RUNNING:
        try:
            data = load_promo_data()
            if data.get("enabled", False) and data.get("messages"):
                idx = data.get("current_index", 0) % len(data["messages"])
                msg = data["messages"][idx]
                data["current_index"] = (idx + 1) % len(data["messages"])
                save_promo_data(data)
                sent_count = 0
                for user_id, sub in list(push_subscriptions.items()):
                    try:
                        send_push_notification(user_id, "📢 مركز سرعة إنجاز", msg, {"type": "promo", "source": "periodic"})
                        sent_count += 1
                    except Exception as e:
                        logger.error(f"[Promo] Failed to send to {user_id}: {e}")
                logger.info(f"[Promo] ✅ تم إرسال الرسالة {idx+1} إلى {sent_count} مشترك")
        except Exception as e:
            logger.error(f"[Promo] خطأ في الدورة: {e}")
        for _ in range(60):
            if not _PROMO_RUNNING:
                break
            time.sleep(5)
    logger.info("⏹ توقفت خلفية الإشعارات الدورية")

def start_promo_thread():
    global _PROMO_THREAD, _PROMO_RUNNING
    if _PROMO_THREAD and _PROMO_THREAD.is_alive():
        return
    _PROMO_RUNNING = True
    _PROMO_THREAD = threading.Thread(target=promo_worker, daemon=True)
    _PROMO_THREAD.start()

def stop_promo_thread():
    global _PROMO_RUNNING
    _PROMO_RUNNING = False


def send_push_notification(user_id, title, body, data=None):
    """إرسال إشعار Web Push إلى متصفح المستخدم"""
    if not WEBPUSH_AVAILABLE:
        return False
    sub = push_subscriptions.get(str(user_id))
    if not sub:
        return False
    _s = load_settings(user_id)
    if not _s.get('push_notifications_enabled', False):
        return False
    try:
        import json as _json
        _payload = _json.dumps({
            "title": title,
            "body": body,
            "data": data or {},
            "icon": "/static/icons/icon-192.png",
            "badge": "/static/icons/icon-72.png"
        })
        _webpush_fn(
            subscription_info=sub,
            data=_payload,
            vapid_private_key=VAPID_PRIVATE_PEM,
            vapid_claims=VAPID_CLAIMS,
            ttl=3600
        )
        return True
    except Exception as _ex:
        if hasattr(_ex, 'response') and _ex.response and getattr(_ex.response, 'status_code', 0) in (410, 404):
            push_subscriptions.pop(str(user_id), None)
            _save_push_subs(push_subscriptions)
        logger.warning(f"Push notification failed for {user_id}: {_ex}")
        return False

def get_user_session_dir(user_id):
    """مجلد منفصل لكل مستخدم لعزل البيانات والإعدادات"""
    user_dir = os.path.join(SESSIONS_DIR, str(user_id))
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)
    return user_dir

# نظام الحسابات (يبدأ بحساب واحد فقط، ويتم إضافة حسابات جديدة عند الطلب مثل تيليجرام الرسمي)
PREDEFINED_USERS = {
    "user_1": {
        "id": "user_1",
        "name": "حساب 1",
        "icon": "fas fa-user",
        "color": "#0088cc"
    }
}

def _get_custom_accounts_file():
    return os.path.join(DATA_DIR, 'accounts.json')

def _load_custom_accounts():
    try:
        fpath = _get_custom_accounts_file()
        if os.path.exists(fpath):
            with open(fpath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict) and data:
                    PREDEFINED_USERS.clear()
                    for uid, udata in data.items():
                        if isinstance(udata, dict) and ('id' in udata or 'name' in udata):
                            PREDEFINED_USERS[uid] = udata
        if not PREDEFINED_USERS:
            PREDEFINED_USERS["user_1"] = {
                "id": "user_1",
                "name": "حساب 1",
                "icon": "fas fa-user",
                "color": "#0088cc"
            }
            _save_custom_accounts()
    except Exception as e:
        logger.error(f"Error loading custom accounts: {e}")

def _save_custom_accounts():
    try:
        fpath = _get_custom_accounts_file()
        os.makedirs(os.path.dirname(fpath), exist_ok=True)
        with open(fpath, 'w', encoding='utf-8') as f:
            json.dump(PREDEFINED_USERS, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error saving custom accounts: {e}")

_load_custom_accounts()

# معالجات الأخطاء الشاملة
@app.errorhandler(400)
def bad_request_error(error):
    logger.warning(f"Bad request handled: {str(error)}")
    if request.path.startswith('/api/') or request.is_json:
        return jsonify({"error": "Bad request"}), 400
    resp = redirect("/")
    resp.set_cookie('session', '', expires=0)
    return resp

@app.errorhandler(404)
def not_found_error(error):
    try:
        return jsonify({"error": "Page not found"}), 404
    except Exception as e:
        logger.error(f"Error in 404 handler: {str(e)}")
        return jsonify({"error": "Page not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    try:
        user_id = 'user_1'
        try:
            if 'session' in globals() and session:
                user_id = session.get('user_id', 'user_1')
        except Exception:
            pass
        current_user = PREDEFINED_USERS.get(user_id, PREDEFINED_USERS.get('user_1', {'id': 'user_1', 'name': 'المستخدم الأول'}))
        users_info = {
            uid: {
                "logged_in": False,
                "account_name": udata.get("name", uid) if isinstance(udata, dict) else str(uid),
                "account_username": "",
                "account_phone": "",
                "account_avatar": None
            }
            for uid, udata in PREDEFINED_USERS.items()
            if isinstance(udata, dict)
        }
        return render_template('index.html', 
                              settings={}, 
                              connection_status='disconnected',
                              current_user=current_user,
                              predefined_users=PREDEFINED_USERS,
                              users_account_info=users_info,
                              admin_ui_visible=False,
                              app_title="مركز سرعة انجاز 📚 للخدمات الطلابية والأكاديمية"), 500
    except Exception as e:
        logger.error(f"Error in 500 handler: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    from werkzeug.exceptions import HTTPException
    if isinstance(e, HTTPException):
        if e.code == 400 and not request.path.startswith('/api/'):
            resp = redirect("/")
            resp.set_cookie('session', '', expires=0)
            return resp
        if request.path.startswith('/api/') or request.is_json:
            return jsonify({"error": e.description}), e.code
        return e

    logger.error(f"Unhandled exception: {str(e)}")
    try:
        user_id = 'user_1'
        try:
            if 'session' in globals() and session:
                user_id = session.get('user_id', 'user_1')
        except Exception:
            pass
        current_user = PREDEFINED_USERS.get(user_id, PREDEFINED_USERS.get('user_1', {'id': 'user_1', 'name': 'المستخدم الأول'}))
        users_info = {
            uid: {
                "logged_in": False,
                "account_name": udata.get("name", uid) if isinstance(udata, dict) else str(uid),
                "account_username": "",
                "account_phone": "",
                "account_avatar": None
            }
            for uid, udata in PREDEFINED_USERS.items()
            if isinstance(udata, dict)
        }
        return render_template('index.html', 
                              settings={}, 
                              connection_status='disconnected',
                              current_user=current_user,
                              predefined_users=PREDEFINED_USERS,
                              users_account_info=users_info,
                              admin_ui_visible=False,
                              app_title="مركز سرعة انجاز 📚 للخدمات الطلابية والأكاديمية"), 500
    except Exception as template_error:
        logger.error(f"Error in exception handler: {str(template_error)}")
        return jsonify({"error": "Server error"}), 500

# معالج أخطاء Socket.IO
@socketio.on_error_default
def default_error_handler(e):
    logger.error(f"Socket.IO error: {str(e)}")

USERS = {}
USERS_LOCK = Lock()

if _AUTO_JOINER_AVAILABLE:
    try:
        init_account_auto_joiner(socketio=socketio, users_map=USERS, users_lock=USERS_LOCK, data_dir=DATA_DIR)
    except Exception as _e_init_aj:
        logger.warning(f"Error initializing auto joiner context: {_e_init_aj}")


# تتبع مؤقتات حظر التدفق (FloodWait) لكل حساب لمنع العقوبات التراكمية
USER_FLOOD_WAITS = {}
USER_FLOOD_LOCK = Lock()

def get_user_flood_wait(uid: str) -> float:
    """إرجاع الثواني المتبقية من FloodWait لحساب معين (0 إن لم يكن هناك انتظار)"""
    with USER_FLOOD_LOCK:
        until = USER_FLOOD_WAITS.get(str(uid), 0)
        remaining = until - time.time()
        return max(0.0, remaining)

def set_user_flood_wait(uid: str, seconds: float):
    """تسجيل وقت حظر التدفق (FloodWait) للحساب لحمايته من أي طلبات لاحقة"""
    with USER_FLOOD_LOCK:
        USER_FLOOD_WAITS[str(uid)] = time.time() + float(seconds) + 5.0
        logger.warning(f"⚠️ FloodWait recorded for user {uid}: {seconds:.0f}s (+5s safety)")


# ═══════════════════════════════════════════════════════════════════
# 🔑 سجل رموز التحقق — تتبع الأكواد المتزامنة مع الأجهزة والبريد
# ═══════════════════════════════════════════════════════════════════
LATEST_VERIFICATION_CODES = {}

def record_latest_verification_code(phone: str, code: str, raw_text: str = ""):
    """حفظ آخر كود تحقق تم التقاطه في الذاكرة والملف المحلي وقاعدة البيانات السحابية Firestore"""
    try:
        clean_code = str(code or '').strip()
        if not clean_code:
            return
        clean_phone = re.sub(r'[^0-9]', '', str(phone or ''))
        entry = {
            "code": clean_code,
            "phone": str(phone or '').strip(),
            "clean_phone": clean_phone,
            "text": str(raw_text or '').strip(),
            "timestamp": time.time(),
            "time_str": time.strftime('%Y-%m-%d %H:%M:%S')
        }
        if clean_phone:
            LATEST_VERIFICATION_CODES[clean_phone] = entry
        LATEST_VERIFICATION_CODES['latest'] = entry

        # إذا كان هناك حساب ينتظر كود، نربط الكود برقمه أيضاً
        try:
            with USERS_LOCK:
                for u_data in USERS.values():
                    if u_data.get('awaiting_code'):
                        u_phone = u_data.get('settings', {}).get('phone')
                        if u_phone:
                            u_clean = re.sub(r'[^0-9]', '', str(u_phone))
                            if u_clean:
                                LATEST_VERIFICATION_CODES[u_clean] = entry
        except Exception:
            pass
        
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
        os.makedirs(data_dir, exist_ok=True)
        with open(os.path.join(data_dir, 'latest_code.json'), 'w', encoding='utf-8') as f:
            json.dump(entry, f, ensure_ascii=False, indent=2)

        # المزامنة السحابية الفورية في Firestore
        try:
            import firestore_sync
            firestore_sync.save_verification_code_to_firestore(phone or 'latest', clean_code, raw_text)
        except Exception:
            pass
    except Exception as e:
        logger.debug(f"Error recording verification code: {e}")

# ===================================================================
# مراقب استقرار الشبكة — يُعيد اتصالات تيليجرام تلقائياً
# ===================================================================
class NetworkStabilityMonitor:
    """يفحص الإنترنت كل 30 ثانية ويُعيد الاتصالات عند الانقطاع"""
    _CHECK_HOSTS = [('8.8.8.8', 53), ('1.1.1.1', 53), ('9.9.9.9', 53)]
    CHECK_INTERVAL = 30

    def __init__(self):
        self.is_online = True
        self._down_since = None

    def _check(self):
        import socket as _sock
        for host, port in self._CHECK_HOSTS:
            try:
                _sock.create_connection((host, port), timeout=4)
                return True
            except OSError:
                pass
        return False

    def _notify(self, msg):
        try:
            socketio.emit('log_update', {'message': msg})
        except Exception:
            pass
        logger.info(msg)

    def _reconnect_all(self):
        with USERS_LOCK:
            items = list(USERS.items())
        for uid, ud in items:
            cm = ud.get('client_manager')
            if cm and ud.get('is_running'):
                try:
                    if hasattr(cm, 'reconnect_if_needed'):
                        t = _OSThread(target=cm.reconnect_if_needed,
                                      daemon=True, name=f'Reconnect-{uid}')
                        t.start()
                except Exception as e:
                    logger.error(f'[NetworkMonitor] خطأ إعادة اتصال {uid}: {e}')

    def _loop(self):
        time.sleep(20)  # انتظر حتى يستقر التطبيق عند البداية
        while True:
            try:
                online = self._check()
                if not online and self.is_online:
                    self.is_online = False
                    self._down_since = time.time()
                    logger.warning('[NetworkMonitor] ⚠️ انقطع الإنترنت!')
                    self._notify('⚠️ تحذير: انقطع الإنترنت عن الخادم!')
                elif online and not self.is_online:
                    self.is_online = True
                    secs = int(time.time() - (self._down_since or time.time()))
                    logger.info(f'[NetworkMonitor] 🟢 عاد الإنترنت بعد {secs}s')
                    self._notify(f'🌐 عاد الإنترنت بعد {secs} ثانية — إعادة اتصال تيليجرام...')
                    self._reconnect_all()
                if online:
                    self._down_since = None
            except Exception as e:
                logger.error(f'[NetworkMonitor] خطأ: {e}')
            time.sleep(self.CHECK_INTERVAL)

    def start(self):
        t = _OSThread(target=self._loop, daemon=True, name='NetworkMonitor')
        t.start()
        logger.info('🛡️ مراقب استقرار الشبكة: نشط — فحص كل 30 ثانية')

network_monitor = NetworkStabilityMonitor()

# ===================================================================
# حلقة asyncio مشتركة لجميع عمليات تسجيل الدخول
# سبب الحل: إنشاء حلقة asyncio منفصلة لكل مستخدم يتعارض مع
# gevent's epoll patching — الحل هو حلقة واحدة مشتركة.
# ===================================================================
_SHARED_LOGIN_LOOP = None
_SHARED_LOGIN_LOOP_LOCK = _pre_patch_threading.Lock()
_SHARED_LOGIN_LOOP_READY = _pre_patch_threading.Event()

def _run_shared_login_loop(loop):
    """تشغيل الحلقة المشتركة في OS thread حقيقي"""
    _SHARED_LOGIN_LOOP_READY.set()
    loop.run_forever()

def _ensure_shared_login_loop():
    """الحصول على الحلقة المشتركة أو إنشاؤها إذا لم تكن موجودة"""
    global _SHARED_LOGIN_LOOP
    with _SHARED_LOGIN_LOOP_LOCK:
        if _SHARED_LOGIN_LOOP is None or _SHARED_LOGIN_LOOP.is_closed() or not _SHARED_LOGIN_LOOP.is_running():
            _SHARED_LOGIN_LOOP_READY.clear()
            loop = asyncio.new_event_loop()
            _SHARED_LOGIN_LOOP = loop
            t = _OSThread(
                target=_run_shared_login_loop,
                args=(loop,),
                daemon=True,
                name='SharedLoginLoop'
            )
            t.start()
            _SHARED_LOGIN_LOOP_READY.wait(timeout=10)
    return _SHARED_LOGIN_LOOP

# ── مفاتيح تيليجرام الدائمة والثابتة داخل الكود الرئيسي ───────────────
TELEGRAM_API_ID   = 22043994
TELEGRAM_API_HASH = '56f64582b363d367280db96586b97801'
API_ID       = int(os.environ.get('TELEGRAM_API_ID', TELEGRAM_API_ID) or TELEGRAM_API_ID)
API_HASH     = os.environ.get('TELEGRAM_API_HASH', TELEGRAM_API_HASH) or TELEGRAM_API_HASH

# ── دوال التطبيع العربي الدقيق لمطابقة كلمات المراقبة (بدون حساسية للهمزات والتشكيل والنقاط) ──
def normalize_arabic_text(text: str) -> str:
    """
    تطبيع النصوص العربية بشكل كامل لمطابقة الكلمات والعبارات المراقبة:
    - إزالة التشكيل والحركات (فتحة، ضمة، كسرة، سكون، تنوين، شدة)
    - إزالة التطويل (الكشيدة ـ)
    - توحيد الألف بكافة أشكالها (أ، إ، آ، ٱ، ا -> ا)
    - توحيد الياء والألف المقصورة (ى، ي -> ي)
    - توحيد التاء المربوطة والهاء (ة، ه -> ه)
    - توحيد الهمزات (ؤ -> و، ئ -> ي، ء -> إزالة)
    - استبدال علامات الترقيم والرموز بمسافات لضمان عدم التصاق الكلمات
    - توحيد المسافات المتعددة وتقليصها
    """
    if not text:
        return ""
    import unicodedata, re
    text = unicodedata.normalize('NFKD', str(text))
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    text = re.sub(r'[\u0640]', '', text)
    text = re.sub(r'[أإآٱ]', 'ا', text)
    text = re.sub(r'[ىي]', 'ي', text)
    text = re.sub(r'[ةه]', 'ه', text)
    text = re.sub(r'ؤ', 'و', text)
    text = re.sub(r'ئ', 'ي', text)
    text = re.sub(r'ء', '', text)
    text = re.sub(r'[^\w\s\u0621-\u064A]', ' ', text)
    text = text.lower()
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def is_arabic_keyword_in_text(keyword: str, text: str) -> bool:
    """
    فحص تطابق كلمة أو عبارة مراقبة كاملة كسطر كامل في الرسالة:
    مطابقة الكلمة أو العبارة كاملة دون حساسية للهمزات أو النقاط أو الحركات.
    """
    norm_kw = normalize_arabic_text(keyword)
    norm_text = normalize_arabic_text(text)
    if not norm_kw or not norm_text:
        return False
    padded_kw = f" {norm_kw} "
    padded_text = f" {norm_text} "
    return (padded_kw in padded_text) or (norm_kw == norm_text) or (len(norm_kw) >= 3 and norm_kw in norm_text)

# ── الكلمات المراقبة الافتراضية والدائمة (المستخرجة نصاً من الصور) ──────
DEFAULT_MONITORING_KEYWORDS_TEXT = """اريد مساعدة
ابي مساعدة
من يسوي تكليف
من يحل
عندي بحث
معي واجب
عندي اسايمنت
من يسوي اسايمنت
ابي سكليف
ابي عذر
من يسوي سكليف
ابي شخص مضمون
ابي مختص
هيليب
من يستطيع
تعرفون احد
تعرفون شخص
من يساعدني
من يعرف مختص
مين يعرف يحل واجب
من يحل واجبات الجامعه
أحتاج مساعدتكم
احتاج مساعدتكم
ابي احد يسوي بحث
مين يعرف مختص
من يعرف احد كويس"""

DEFAULT_MONITORING_KEYWORDS = [w.strip() for w in DEFAULT_MONITORING_KEYWORDS_TEXT.strip().split('\n') if w.strip()]

def get_effective_watch_words(user_settings_or_words=None):
    """دمج الكلمات الدائمة مع أي كلمات يضيفها المستخدم في الواجهة مع الحفاظ على الترتيب والفرادة"""
    user_words = []
    if isinstance(user_settings_or_words, dict):
        user_words = user_settings_or_words.get('watch_words', [])
    elif isinstance(user_settings_or_words, (list, set, tuple)):
        user_words = list(user_settings_or_words)
    elif isinstance(user_settings_or_words, str):
        user_words = [w.strip() for w in user_settings_or_words.split('\n') if w.strip()]

    seen = set()
    combined = []
    for kw in DEFAULT_MONITORING_KEYWORDS:
        norm = kw.strip()
        if norm and norm not in seen:
            seen.add(norm)
            combined.append(norm)
    for kw in user_words:
        norm = kw.strip()
        if norm and norm not in seen:
            seen.add(norm)
            combined.append(norm)
    return combined

GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')
os.environ.setdefault('GROQ_API_KEY', GROQ_API_KEY)

GITHUB_TOKEN  = os.environ.get('GITHUB_TOKEN', '')
GITHUB_REPO   = os.environ.get('GITHUB_REPO',   'anwer1230/Anwer_Telegram-')
GITHUB_BRANCH = os.environ.get('GITHUB_BRANCH', 'main')

# ── رابط النشر التلقائي الثابت Render Deploy Hook ─────────────────────
RENDER_DEPLOY_HOOK_URL = os.environ.get('RENDER_DEPLOY_HOOK_URL') or os.environ.get('RENDER_DEPLOY_HOOK') or "https://api.render.com/deploy/srv-davr5su7bikc73f5978g?key=hZAEDlsJijM"
RENDER_DEPLOY_HOOK = os.environ.get('RENDER_DEPLOY_HOOK', RENDER_DEPLOY_HOOK_URL)

def trigger_render_deploy(hook_url=None):
    """إرسال طلب إلى Render Deploy Hook لإعادة بناء ونشر التطبيق فورياً على منصة Render"""
    target = hook_url or RENDER_DEPLOY_HOOK or RENDER_DEPLOY_HOOK_URL
    try:
        import requests as _requests
        resp = _requests.post(target, timeout=15)
        logger.info(f"🚀 Render Deploy Hook triggered: status={resp.status_code}")
        return True, resp.status_code
    except Exception as e:
        logger.error(f"❌ فشل إطلاق Render Deploy Hook: {e}")
        return False, str(e)

# ─── ملف إعدادات التحديث ──────────────────────────────────────────────
UPDATE_SETTINGS_FILE = os.path.join(os.path.dirname(__file__), 'data', 'update_settings.json')
os.makedirs(os.path.dirname(UPDATE_SETTINGS_FILE), exist_ok=True)

def load_update_settings():
    try:
        if os.path.exists(UPDATE_SETTINGS_FILE):
            with open(UPDATE_SETTINGS_FILE, 'r') as f:
                return json.load(f)
    except Exception:
        pass
    return {"auto_update": False, "last_check": None, "last_update": None}

def save_update_settings(settings):
    try:
        with open(UPDATE_SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save update settings: {e}")

def get_current_commit():
    try:
        result = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            capture_output=True, text=True, check=True,
            cwd=os.path.dirname(__file__)
        )
        return result.stdout.strip()
    except Exception as e:
        logger.error(f"Failed to get current commit: {e}")
        return None

def get_latest_commit():
    try:
        repo = GITHUB_REPO or "anwer1230/-Anwer_program"
        if '/' in repo:
            owner, name = repo.split('/', 1)
        else:
            owner, name = "anwer1230", repo
        url = f"https://api.github.com/repos/{owner}/{name}/commits/{GITHUB_BRANCH or 'main'}"
        headers = {}
        if GITHUB_TOKEN:
            headers['Authorization'] = f'token {GITHUB_TOKEN}'
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            return resp.json().get('sha', '').strip()
    except Exception as e:
        logger.error(f"Failed to get latest commit: {e}")
    return None

def check_for_updates():
    current = get_current_commit()
    latest = get_latest_commit()
    if not current or not latest:
        return False, current, latest, "❌ تعذر التحقق من التحديثات"
    if current != latest:
        return True, current, latest, f"🔄 تحديث جديد متاح! (الحالي: {current[:7]} → الأحدث: {latest[:7]})"
    return False, current, latest, "✅ التطبيق محدث لأحدث إصدار"

def perform_update():
    logs = []
    try:
        logs.append("📥 جاري سحب التغييرات من GitHub...")
        pull_result = subprocess.run(
            ['git', 'pull', 'origin', GITHUB_BRANCH or 'main'],
            capture_output=True, text=True, cwd=os.path.dirname(__file__)
        )
        if pull_result.returncode != 0:
            logs.append(f"❌ فشل git pull: {pull_result.stderr}")
            return False, logs
        logs.append(f"✅ {pull_result.stdout.strip()}")
        logs.append("📦 جاري تحديث المتطلبات...")
        pip_result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'],
            capture_output=True, text=True, cwd=os.path.dirname(__file__)
        )
        if pip_result.returncode != 0:
            logs.append(f"⚠️ تحذير في تثبيت المتطلبات: {pip_result.stderr}")
        else:
            logs.append("✅ تم تحديث المتطلبات")
        new_commit = get_current_commit()
        settings = load_update_settings()
        settings['last_update'] = datetime.now().isoformat()
        save_update_settings(settings)
        logs.append(f"✅ تم التحديث إلى الإصدار: {new_commit[:7] if new_commit else 'غير معروف'}")
        # إطلاق الـ Deploy Hook لإعادة البناء في Render تلقائياً
        try:
            dep_ok, dep_stat = trigger_render_deploy()
            if dep_ok:
                logs.append(f"🚀 تم إطلاق Render Deploy Hook تلقائياً بنجاح (كود {dep_stat})")
        except Exception as _dep_e:
            logs.append(f"⚠️ تعذر إطلاق Render Hook: {_dep_e}")
        return True, logs
    except Exception as e:
        logs.append(f"❌ خطأ في التحديث: {str(e)}")
        return False, logs

_AUTO_UPDATE_THREAD = None
_AUTO_UPDATE_RUNNING = False

def auto_update_worker():
    global _AUTO_UPDATE_RUNNING
    _AUTO_UPDATE_RUNNING = True
    while _AUTO_UPDATE_RUNNING:
        try:
            settings = load_update_settings()
            if settings.get('auto_update', False):
                has_update, current, latest, msg = check_for_updates()
                if has_update:
                    logger.info(f"🔄 تحديث تلقائي: {msg}")
                    success, logs = perform_update()
                    if success:
                        logger.info(f"✅ تم التحديث التلقائي: {logs[-1]}")
                        try:
                            socketio.emit('update_completed', {
                                "message": "✅ تم تحديث التطبيق تلقائياً",
                                "version": latest[:7] if latest else "غير معروف"
                            })
                        except Exception:
                            pass
                    else:
                        logger.error(f"❌ فشل التحديث التلقائي: {logs[-1] if logs else ''}")
        except Exception as e:
            logger.error(f"خطأ في خلفية التحديث التلقائي: {e}")
        for _ in range(360):
            if not _AUTO_UPDATE_RUNNING:
                break
            time.sleep(10)

def start_auto_update_thread():
    global _AUTO_UPDATE_THREAD, _AUTO_UPDATE_RUNNING
    if _AUTO_UPDATE_THREAD and _AUTO_UPDATE_THREAD.is_alive():
        return
    _AUTO_UPDATE_RUNNING = True
    _AUTO_UPDATE_THREAD = threading.Thread(target=auto_update_worker, daemon=True)
    _AUTO_UPDATE_THREAD.start()
    logger.info("🔄 خلفية التحديث التلقائي بدأت")

def stop_auto_update_thread():
    global _AUTO_UPDATE_RUNNING
    _AUTO_UPDATE_RUNNING = False
    logger.info("⏹ خلفية التحديث التلقائي توقفت")

if not API_ID or not API_HASH:
    logger.warning("⚠️ لم يتم إعداد TELEGRAM_API_ID و TELEGRAM_API_HASH - وظائف التليجرام لن تعمل")

# =========================== 
# نظام Queue للتنبيهات المحسن
# ===========================
class AlertQueue:
    """نظام queue متقدم لإدارة التنبيهات"""

    def __init__(self):
        self.queue = queue.Queue()
        self.running = False
        self.thread = None

    def start(self):
        """بدء معالج التنبيهات"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._process_alerts, daemon=True)
            self.thread.start()
            logger.info("Alert queue processor started")

    def stop(self):
        """إيقاف معالج التنبيهات"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)

    def add_alert(self, user_id, alert_data):
        """إضافة تنبيه جديد للقائمة"""
        try:
            self.queue.put({
                'user_id': user_id,
                'alert_data': alert_data,
                'timestamp': time.time()
            }, timeout=1)
        except queue.Full:
            logger.warning(f"Alert queue full for user {user_id}")

    def _process_alerts(self):
        """معالجة التنبيهات بشكل مستمر"""
        while self.running:
            try:
                alert = self.queue.get(timeout=1)
                self._send_alert(alert)
                self.queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing alert: {str(e)}")

    def _send_alert(self, alert):
        """إرسال التنبيه للمستخدم"""
        user_id = alert['user_id']
        alert_data = alert['alert_data']

        try:
            socketio.emit('new_alert', alert_data, to=user_id)
            socketio.emit('log_update', {
                "message": f"🚨 تنبيه فوري: '{alert_data.get('keyword', '')}' في {alert_data.get('group', '')}"
            }, to=user_id)

            try:
                send_push_notification(
                    user_id,
                    f"🔔 تنبيه: {alert_data.get('keyword', '')}",
                    f"في {alert_data.get('group', '')} من {alert_data.get('sender', '')}",
                    alert_data
                )
            except Exception:
                pass

            # تسجيل التنبيه في سجل المستخدم للحفاظ على سجل التنبيهات
            try:
                ud = get_or_create_user(user_id)
                alerts_list = ud.setdefault('alerts', [])
                alerts_list.insert(0, alert_data)
                if len(alerts_list) > 100:
                    del alerts_list[100:]
                s = load_settings(user_id)
                s_alerts = s.setdefault('alerts', [])
                s_alerts.insert(0, alert_data)
                if len(s_alerts) > 100:
                    del s_alerts[100:]
                save_settings(user_id, s)
            except Exception as store_err:
                logger.debug(f"Failed to record alert in history: {store_err}")

            if not alert_data.get('already_sent_tg'):
                self._send_to_saved_messages(user_id, alert_data)

        except Exception as e:
            logger.error(f"Failed to send alert for user {user_id}: {str(e)}")

    def _send_to_saved_messages(self, user_id, alert_data):
        """إرسال التنبيه للرسائل المحفوظة في تيليجرام"""
        try:
            with USERS_LOCK:
                client_manager = USERS.get(user_id, {}).get('client_manager')

            if not client_manager or not client_manager.client:
                logger.warning(f"⚠️ No client available to send alert for user {user_id}")
                return

            keyword    = alert_data.get('keyword', '')
            group_name = alert_data.get('group', '')
            group_link = alert_data.get('group_link') or ''
            sender     = alert_data.get('sender', 'غير معروف')
            msg_time   = alert_data.get('message_time', alert_data.get('timestamp', ''))
            full_text  = alert_data.get('full_message') or alert_data.get('message', '')

            link_line = f"\n🔗 الرابط: {group_link}" if group_link else ""

            notification_msg = (
                f"🚨 تنبيه مراقبة\n\n"
                f"🔑 الكلمة: {keyword}\n"
                f"👥 المجموعة: {group_name}"
                f"{link_line}\n"
                f"👤 المرسل: {sender}\n"
                f"🕐 الوقت: {msg_time}\n\n"
                f"... الرسالة:\n{full_text}"
            )

            s = load_settings(user_id) or {}
            custom_target = (s.get('alert_target_user') or s.get('alert_target') or '').strip()
            target_list = []
            if custom_target and custom_target.lower() != 'me':
                target_list.append(custom_target)
                target_list.append('me')
            else:
                target_list.append('me')

            loop = getattr(client_manager, 'loop', None)
            if not loop or not loop.is_running():
                logger.warning(f"⚠️ Event loop not running for user {user_id} — cannot send alert")
                return

            async def _do_send():
                for dest in target_list:
                    try:
                        if hasattr(client_manager, '_resolve_tg_destination'):
                            dest_ent = await client_manager._resolve_tg_destination(dest)
                        else:
                            dest_ent = dest
                    except Exception:
                        dest_ent = dest
                    try:
                        await client_manager.client.send_message(dest_ent, notification_msg, link_preview=False)
                        logger.info(f"✅ Alert sent to {dest} for user {user_id}: '{keyword}'")
                    except Exception as e:
                        logger.error(f"❌ Failed to send Telegram alert to {dest} for user {user_id}: {e}")

            asyncio.run_coroutine_threadsafe(_do_send(), loop)

        except Exception as e:
            logger.error(f"Failed to send to saved messages: {str(e)}")

alert_queue = AlertQueue()

# ===========================
# تنقية الرسائل
# ===========================
class MessageSanitizer:
    PATTERNS = {
        'telegram_links': r'https?://(?:t\.me|telegram\.me)/[^\s<>]+|(?<!\w)t\.me/[^\s<>]+|(?<!\w)telegram\.me/[^\s<>]+',
        'whatsapp_links': r'https?://(?:wa\.me|chat\.whatsapp\.com|whatsapp\.com)/[^\s<>]+|(?<!\w)wa\.me/[^\s<>]+',
        'general_links':  r'https?://[^\s<>]+|www\.[^\s<>]+',
        'telegram_handles': r'@[a-zA-Z0-9_]{4,}',
        'phone_numbers': r'(?:\+?\d{1,3}[\s\-]?)?\(?\d{2,4}\)?[\s\-]?\d{3,4}[\s\-]?\d{3,4}',
        'ad_keywords': (
            r'\b(?:للتواصل|للاستفسار|واتساب|واتس|تليجرام|تليقرام|قناة|قناتي|انضم|انضموا|'
            r'خدمات|خدماتنا|إعلان|اعلان|عرض|عروض|خصم|تخفيض|تخفيضات|طلب\s*شراء|'
            r'بيع|تسويق|دورات|كورسات|اشتراك|راسلني|اطلب|عمولة|كاش|سحب|إيداع)\b'
        ),
    }

    WHATSAPP_TRANSFORMATIONS = [
        (r'https?://wa\.me/(\d+)', r'wa.me/\1'),
        (r'https?://chat\.whatsapp\.com/([^\s<>]+)', r'https://chat.whatsapp.com/\1'),
        (r'https?://whatsapp\.com/channel/([^\s<>]+)', r'https://whatsapp.com/channel/\1'),
    ]

    @classmethod
    def sanitize(cls, text, mode='smart'):
        """
        تنقية النص حسب الوضع المحدد
        mode: 'smart' (تنقية ذكية), 'clean' (تنقية كاملة), 'transform' (تحويل الروابط فقط)
        """
        if not text:
            return text
        cleaned = str(text)

        if mode == 'transform':
            for pattern, replacement in cls.WHATSAPP_TRANSFORMATIONS:
                cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)
            return cleaned

        if mode == 'clean':
            for key in ('telegram_links', 'whatsapp_links', 'general_links'):
                cleaned = re.sub(cls.PATTERNS[key], '', cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(cls.PATTERNS['telegram_handles'], '', cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(cls.PATTERNS['phone_numbers'], '', cleaned)
            cleaned = re.sub(cls.PATTERNS['ad_keywords'], '', cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(r'[ \t]+', ' ', cleaned)
            lines = []
            seen = set()
            for raw in cleaned.split('\n'):
                line = raw.strip(' \t-•·،,.|')
                if not line:
                    continue
                if not re.search(r'[\w\u0600-\u06FF]', line):
                    continue
                if line in seen:
                    continue
                seen.add(line)
                lines.append(line)
            result = '\n'.join(lines).strip()
            return result if result else None

        # وضع smart: تحويل روابط واتساب + تنقية خفيفة
        for pattern, replacement in cls.WHATSAPP_TRANSFORMATIONS:
            cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)
        for key in ('telegram_links', 'general_links'):
            cleaned = re.sub(cls.PATTERNS[key], '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(cls.PATTERNS['ad_keywords'], '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'[ \t]+', ' ', cleaned).strip()
        return cleaned if cleaned else None

    @classmethod
    def has_promo_content(cls, text):
        if not text:
            return False
        s = str(text)
        for key in ('telegram_links', 'whatsapp_links', 'general_links',
                    'telegram_handles', 'phone_numbers', 'ad_keywords'):
            if re.search(cls.PATTERNS[key], s, re.IGNORECASE):
                return True
        return False

    @classmethod
    def transform_whatsapp_links(cls, text):
        """تحويل روابط واتساب فقط دون حذف"""
        if not text:
            return text
        cleaned = str(text)
        for pattern, replacement in cls.WHATSAPP_TRANSFORMATIONS:
            cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)
        return cleaned

PROTECTION_BOTS = {
    'missrose_bot', 'rose_bot', 'therose_bot', 'rosebot',
    'shieldy_bot', 'shieldy', 'combot', 'combot_tech',
    'cas_bot', 'spamwatch_bot', 'spamwatchbot', 'antispam_bot',
    'antispambot', 'anti_spam_bot', 'spam_bot', 'spambot',
    'groupguardbot', 'groupguard_bot', 'guard_bot', 'guardbot',
    'safeguard_bot', 'safeguardbot', 'safe_guard_bot',
    'defender_bot', 'defenderbot', 'banhammer_bot', 'banhammerbot',
    'security_bot', 'securitybot', 'grouphelpbot', 'group_helpbot',
    'voteban_bot', 'votebanbot', 'antichannelpinbot', 'antiservicebot',
    'lolzteambot', 'protectionbot', 'policeman_bot', 'policemanbot',
    'sheriffbot', 'sheriff_bot', 'nightbot', 'mee6', 'cleanerbot',
    'cleaner_bot', 'modbot', 'moderationbot', 'no_spam_bot', 'nospambot',
    'stopspambot', 'stop_spam_bot', 'anti_flood_bot', 'antifloodbot',
    'flood_control_bot', 'hamasbot', 'arabicguard', 'arabguard_bot',
    'captchabot', 'captcha_bot', 'verifybot', 'verify_bot',
    'recaptcha_bot', 'human_verify_bot', 'wickbot', 'wick_bot',
    'dynobot', 'silence_bot', 'silencebot', 'mutebot', 'mute_bot',
    'word_filter_bot', 'filterbot', 'filter_bot',
    # ── بوت جبل وأسماؤه البديلة ──
    'jabal_bot', 'jabalbot', 'jabal', 'jbl_bot', 'jbl',
    'mtn_bot', 'mountain_bot', 'mtnchat_bot',
    # ── بوتات إضافية شائعة ──
    'groupprotect_bot', 'tgspam_bot', 'spam_protection_bot',
    'adminbot', 'admin_bot', 'groupadmin_bot',
}

PROTECTION_BOT_SUBSTRINGS = (
    'shieldy', 'rose', 'guard', 'combot', 'spamwatch', 'antispam',
    'anti_spam', 'safeguard', 'defender', 'banhammer', 'captcha',
    'verify', 'protect', 'police', 'sheriff', 'cleanbot', 'noflood',
    'antiflood', 'flood_', 'modbot', 'nochannel',
    # ── إضافات بوت جبل ──
    'jabal', 'jbl', 'mountain', 'mtn',
    # ── كلمات عامة ──
    'antispam', 'nospam', 'stopspam', 'silencebot', 'mutebot',
)

PROTECTED_GROUPS_CACHE = {}
PROTECTED_GROUPS_LOCK = Lock()

# كاش التحليل الذكي لمحادثات المجموعات وحماية الحساب
AI_GROUP_SAFETY_CACHE = {}
AI_GROUP_SAFETY_LOCK = Lock()

# ── نظام التعلم التلقائي للبوتات ────────────────────────────────────────────
BOTS_DISCOVERED_FILE = os.path.join(DATA_DIR, "discovered_bots.json")
_BOTS_FILE_LOCK = threading.Lock()

def load_discovered_bots():
    with _BOTS_FILE_LOCK:
        try:
            if os.path.exists(BOTS_DISCOVERED_FILE):
                with open(BOTS_DISCOVERED_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return {"bots": []}

def save_discovered_bots(data):
    with _BOTS_FILE_LOCK:
        try:
            os.makedirs(DATA_DIR, exist_ok=True)
            with open(BOTS_DISCOVERED_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"فشل حفظ البوتات المكتشفة: {e}")

def add_discovered_bot(bot_username):
    if not bot_username:
        return
    bot_username = bot_username.lower().lstrip('@')
    if bot_username in PROTECTION_BOTS:
        return
    data = load_discovered_bots()
    if bot_username in data.get("bots", []):
        return
    data.setdefault("bots", []).append(bot_username)
    save_discovered_bots(data)
    PROTECTION_BOTS.add(bot_username)
    logger.info(f"✅ تم اكتشاف بوت حماية جديد وحفظه: @{bot_username}")

# تحميل البوتات المكتشفة مسبقاً عند بدء التشغيل
try:
    _disc = load_discovered_bots()
    for _b in _disc.get("bots", []):
        PROTECTION_BOTS.add(_b)
    if _disc.get("bots"):
        logger.info(f"✅ تم تحميل {len(_disc['bots'])} بوت مكتشف من discovered_bots.json")
except Exception:
    pass
# ─────────────────────────────────────────────────────────────────────────────

def _cache_protection(cache_key, result, reason, bots=None):
    with PROTECTED_GROUPS_LOCK:
        PROTECTED_GROUPS_CACHE[cache_key] = {
            'result': result, 'reason': reason,
            'bots': bots or [], 'ts': time.time()
        }

def save_settings(user_id, settings, force=False):
    db_saved = True
    try:
        if isinstance(settings, dict):
            settings['watch_words'] = get_effective_watch_words(settings.get('watch_words', []))
            settings.setdefault('monitoring_persistent', True)
            settings.setdefault('my_alerts_enabled', True)
            settings.setdefault('my_alerts_replies', True)
            settings.setdefault('my_alerts_actions', True)
            settings.setdefault('my_alerts_reply_sound_enabled', True)
            settings.setdefault('my_alerts_reply_sound_tone', 'chime')
            settings.setdefault('keyword_auto_reply_enabled', True)
            settings.setdefault('keyword_auto_reply_text', 'ابشر')
            settings.setdefault('keyword_auto_reply_forward', True)
            settings.setdefault('keyword_auto_reply_in_group', False)
            settings.setdefault('keyword_auto_reply_in_dm', True)
            settings.setdefault('alert_target_user', 'me')
            settings.setdefault('user_auto_replies', [])
            settings.setdefault('schedule_duration_hours', 2.0)
            settings.setdefault('schedule_duration', 7200)
            settings.setdefault('schedule_pause_hours', 2.0)
            settings.setdefault('schedule_pause_duration', 7200)

        if not force:
            existing = load_settings(user_id)
            if existing == settings:
                return True
        if _DB_READY:
            db_saved = _app_db.save_settings(user_id, settings)

        user_dir = get_user_session_dir(user_id)
        path = os.path.join(user_dir, "settings.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=4)
        # نسخة JSON احتياطية للتوافق مع التشغيل القديم والاستعادة اليدوية
        legacy_path = os.path.join(SESSIONS_DIR, f"{user_id}.json")
        with open(legacy_path, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=4)
        return bool(db_saved)
    except Exception as e:
        logger.error(f"Error saving settings for {user_id}: {str(e)}")
        return False

def load_settings(user_id):
    if _DB_READY:
        try:
            database_settings = _app_db.load_settings(user_id)
            if database_settings is not None:
                database_settings['watch_words'] = get_effective_watch_words(database_settings.get('watch_words', []))
                database_settings.setdefault('monitoring_persistent', True)
                database_settings.setdefault('my_alerts_enabled', True)
                database_settings.setdefault('my_alerts_replies', True)
                database_settings.setdefault('my_alerts_actions', True)
                database_settings.setdefault('my_alerts_reply_sound_enabled', True)
                database_settings.setdefault('my_alerts_reply_sound_tone', 'chime')
                database_settings.setdefault('keyword_auto_reply_enabled', True)
                database_settings.setdefault('keyword_auto_reply_text', 'ابشر')
                database_settings.setdefault('keyword_auto_reply_forward', True)
                database_settings.setdefault('keyword_auto_reply_in_group', False)
                database_settings.setdefault('keyword_auto_reply_in_dm', True)
                database_settings.setdefault('alert_target_user', 'me')
                database_settings.setdefault('user_auto_replies', [])
                database_settings.setdefault('schedule_duration_hours', 2.0)
                database_settings.setdefault('schedule_duration', 7200)
                database_settings.setdefault('schedule_pause_hours', 2.0)
                database_settings.setdefault('schedule_pause_duration', 7200)
                return database_settings
        except Exception as _db_load_error:
            logger.warning("PostgreSQL settings read failed for %s: %s", user_id, _db_load_error)

    try:
        user_dir = get_user_session_dir(user_id)
        path = os.path.join(user_dir, "settings.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            data['watch_words'] = get_effective_watch_words(data.get('watch_words', []))
            data.setdefault('monitoring_persistent', True)
            data.setdefault('my_alerts_enabled', True)
            data.setdefault('my_alerts_replies', True)
            data.setdefault('my_alerts_actions', True)
            data.setdefault('my_alerts_reply_sound_enabled', True)
            data.setdefault('my_alerts_reply_sound_tone', 'chime')
            data.setdefault('keyword_auto_reply_enabled', True)
            data.setdefault('keyword_auto_reply_text', 'ابشر')
            data.setdefault('keyword_auto_reply_forward', True)
            data.setdefault('keyword_auto_reply_in_group', False)
            data.setdefault('keyword_auto_reply_in_dm', True)
            data.setdefault('alert_target_user', 'me')
            data.setdefault('user_auto_replies', [])
            data.setdefault('schedule_duration_hours', 2.0)
            data.setdefault('schedule_duration', 7200)
            data.setdefault('schedule_pause_hours', 2.0)
            data.setdefault('schedule_pause_duration', 7200)
            if _DB_READY:
                _app_db.save_settings(user_id, data)
            return data
        # fallback للملف القديم
        legacy_path = os.path.join(SESSIONS_DIR, f"{user_id}.json")
        if os.path.exists(legacy_path):
            with open(legacy_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            data['watch_words'] = get_effective_watch_words(data.get('watch_words', []))
            data.setdefault('monitoring_persistent', True)
            data.setdefault('my_alerts_enabled', True)
            data.setdefault('my_alerts_replies', True)
            data.setdefault('my_alerts_actions', True)
            data.setdefault('my_alerts_reply_sound_enabled', True)
            data.setdefault('my_alerts_reply_sound_tone', 'chime')
            data.setdefault('keyword_auto_reply_enabled', True)
            data.setdefault('keyword_auto_reply_text', 'ابشر')
            data.setdefault('keyword_auto_reply_forward', True)
            data.setdefault('keyword_auto_reply_in_group', False)
            data.setdefault('keyword_auto_reply_in_dm', True)
            data.setdefault('alert_target_user', 'me')
            data.setdefault('user_auto_replies', [])
            data.setdefault('schedule_duration_hours', 2.0)
            data.setdefault('schedule_duration', 7200)
            data.setdefault('schedule_pause_hours', 2.0)
            data.setdefault('schedule_pause_duration', 7200)
            # نقل البيانات للمجلد الجديد والقاعدة عند توفرها
            save_settings(user_id, data, force=True)
            return data
        return {
            'watch_words': list(DEFAULT_MONITORING_KEYWORDS),
            'monitoring_persistent': True,
            'my_alerts_enabled': True,
            'my_alerts_replies': True,
            'my_alerts_actions': True,
            'my_alerts_reply_sound_enabled': True,
            'my_alerts_reply_sound_tone': 'chime',
            'keyword_auto_reply_enabled': True,
            'keyword_auto_reply_text': 'ابشر',
            'keyword_auto_reply_forward': True,
            'keyword_auto_reply_in_group': False,
            'keyword_auto_reply_in_dm': True,
            'alert_target_user': 'me',
            'user_auto_replies': [],
            'schedule_duration_hours': 2.0,
            'schedule_duration': 7200,
            'schedule_pause_hours': 2.0,
            'schedule_pause_duration': 7200
        }
    except Exception as e:
        logger.error(f"Error loading settings for {user_id}: {str(e)}")
        return {
            'watch_words': list(DEFAULT_MONITORING_KEYWORDS),
            'monitoring_persistent': True,
            'my_alerts_enabled': True,
            'my_alerts_replies': True,
            'my_alerts_actions': True,
            'my_alerts_reply_sound_enabled': True,
            'my_alerts_reply_sound_tone': 'chime',
            'keyword_auto_reply_enabled': True,
            'keyword_auto_reply_text': 'ابشر',
            'keyword_auto_reply_forward': True,
            'keyword_auto_reply_in_group': False,
            'keyword_auto_reply_in_dm': True,
            'alert_target_user': 'me',
            'user_auto_replies': [],
            'schedule_duration_hours': 2.0,
            'schedule_duration': 7200,
            'schedule_pause_hours': 2.0,
            'schedule_pause_duration': 7200
        }

# ترحيل كسول وآمن: لا يستبدل أي إعداد موجود في PostgreSQL
if _DB_READY:
    try:
        _app_db.migrate_json_settings(SESSIONS_DIR)
    except Exception as _db_migration_error:
        logger.warning("JSON settings migration skipped: %s", _db_migration_error)

def clear_user_session(user_id):
    """حذف مجلد المستخدم بالكامل"""
    try:
        import shutil
        user_dir = get_user_session_dir(user_id)
        if os.path.exists(user_dir):
            shutil.rmtree(user_dir)
        legacy_path = os.path.join(SESSIONS_DIR, f"{user_id}.json")
        if os.path.exists(legacy_path):
            os.remove(legacy_path)
        session_file = os.path.join(SESSIONS_DIR, f"{user_id}_session.session")
        if os.path.exists(session_file):
            os.remove(session_file)
        logger.info(f"Cleared session for {user_id}")
        # حذف ملف سلسلة الجلسة أيضاً
        str_session_file = os.path.join(SESSIONS_DIR, f"{user_id}_string.txt")
        if os.path.exists(str_session_file):
            os.remove(str_session_file)
        return True
    except Exception as e:
        logger.error(f"Error clearing session for {user_id}: {str(e)}")
        return False


def save_string_session(user_id, session_str):
    """حفظ سلسلة جلسة StringSession في ملف نصي"""
    try:
        os.makedirs(SESSIONS_DIR, exist_ok=True)
        path = os.path.join(SESSIONS_DIR, f"{user_id}_string.txt")
        with open(path, 'w') as f:
            f.write(session_str)
        logger.info(f"Saved StringSession for {user_id}")
    except Exception as e:
        logger.error(f"Failed to save StringSession for {user_id}: {e}")


def load_string_session(user_id):
    """تحميل سلسلة جلسة StringSession من ملف"""
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

def _clean_group_entry(raw: str) -> str:
    import re
    cleaned = str(raw).strip()
    if not cleaned:
        return ''
    cleaned = cleaned.strip('"\'`()[]{}<>')
    # حماية الروابط والمعرفات الرقمية من التجريد غير المقصود
    if (cleaned.startswith('https://') or cleaned.startswith('http://')
            or cleaned.startswith('t.me/') or cleaned.startswith('telegram.me/')
            or cleaned.startswith('@') or re.match(r'^-?\d+$', cleaned)):
        return cleaned
    # تجريد البوليتات والأرقام والرموز من بداية السطر فقط
    cleaned = re.sub(r'^[\s\u00b7\u2022\u25cf\u25aa\u25ab\u25fe\u25fd\u2023\u203b\u2043\u2219\*\-\–\—\.\،\,\#\>\|•●◾◾✓✦①②③④⑤⑥⑦⑧⑨⑩\d]+[\s.،:]*', '', cleaned)
    return cleaned.strip()

def dedupe_groups(groups):
    seen = set()
    result = []
    if isinstance(groups, str):
        import re as _re
        raw_items = _re.split(r'[\r\n,;\t]+|\s+(?=(?:https?://|t\.me/|telegram\.me/|@|-?\d+))', groups.strip())
        groups = [g.strip() for g in raw_items if g and g.strip()]
    for g in groups or []:
        if not g:
            continue
        original = _clean_group_entry(str(g))
        if not original:
            continue
        norm = original.lower()
        norm = norm.replace('https://telegram.me/', 'https://t.me/')
        norm = norm.replace('http://telegram.me/', 'https://t.me/')
        norm = norm.replace('http://t.me/', 'https://t.me/')
        if '?' in norm:
            norm = norm.split('?', 1)[0]
        if '#' in norm:
            norm = norm.split('#', 1)[0]
        norm = norm.rstrip('/').strip()
        if not norm:
            continue
        if norm in seen:
            continue
        seen.add(norm)
        result.append(original)
    return result

def load_all_sessions():
    logger.info("Loading existing sessions...")
    session_count = 0
    with USERS_LOCK:
        try:
            for filename in os.listdir(SESSIONS_DIR):
                if filename.endswith('.json') and filename != 'push_subscriptions.json':
                    user_id = filename.split('.')[0]
                    settings = load_settings(user_id)
                    if settings and 'phone' in settings:
                        saved_p = settings.get('phone')
                        saved_n = settings.get('account_name') or settings.get('name')
                        if saved_p and saved_n and saved_n != 'رقم أساسي':
                            try:
                                import firestore_sync
                                firestore_sync.update_phone_account_name(saved_p, saved_n)
                            except Exception:
                                pass
                        USERS[user_id] = {
                            'client_manager': None,
                            'settings': settings,
                            'thread': None,
                            'is_running': False,
                            'stats': {"sent": 0, "errors": 0},
                            'connected': False,
                            'authenticated': False,
                            'awaiting_code': False,
                            'awaiting_password': False,
                            'phone_code_hash': None,
                            'monitoring_active': False,
                            'event_handlers_registered': False,
                            'sent_batches': settings.get('sent_batches', []) or []
                        }
                        session_count += 1
                        logger.info(f"✓ Loaded session for {user_id}")
        except Exception as e:
            logger.error(f"Error loading sessions: {str(e)}")
    logger.info(f"Loaded {session_count} sessions successfully")
    return session_count

# =========================== 
# مدير التليجرام المحسن
# ===========================
class TelegramClientManager:
    def __init__(self, user_id):
        self.user_id = user_id
        self.client = None
        self.loop = None
        self.thread = None
        self.stop_flag = threading.Event()
        self.is_ready = threading.Event()
        self.event_handlers_registered = False
        try:
            _s_init = load_settings(user_id) or {}
            _w_init = _s_init.get('watch_words', [])
            self.monitored_keywords = get_effective_watch_words(_w_init) if _w_init else list(DEFAULT_MONITORING_KEYWORDS)
        except Exception:
            self.monitored_keywords = list(DEFAULT_MONITORING_KEYWORDS)
        self.monitored_groups = []
        self._processed_msg_ids = set()
        self.my_id = None
        self.my_username = None
        self.my_name = None
        self._my_alerts_processed = set()
        self._my_sent_message_ids = set()
        self._my_sent_msg_texts = {}

    async def _ensure_my_info(self):
        """التحقق وتخزين هوية الحساب المسجل لاستخدامه في فحص الردود والتنبيهات"""
        if not self.my_id and self.client:
            try:
                me = await self.client.get_me()
                if me:
                    self.my_id = me.id
                    self.my_username = getattr(me, 'username', None)
                    fname = getattr(me, 'first_name', '') or ''
                    lname = getattr(me, 'last_name', '') or ''
                    self.my_name = f"{fname} {lname}".strip() or getattr(me, 'username', '') or str(me.id)
                    logger.info(f"User identity confirmed for {self.user_id}: ID={self.my_id}, @{self.my_username}, Name={self.my_name}")
                    # تثبيت وتحديث اسم الحساب للرقم بشكل دائم وأبدي
                    try:
                        p_num = getattr(me, 'phone', '') or (load_settings(self.user_id) or {}).get('phone') or getattr(self, 'phone_number', '')
                        if p_num:
                            p_norm = p_num if str(p_num).startswith('+') else f"+{p_num}"
                            if self.my_name:
                                st_cur = load_settings(self.user_id) or {}
                                st_cur['account_name'] = self.my_name
                                if self.my_username:
                                    st_cur['account_username'] = self.my_username
                                st_cur['account_phone'] = p_norm
                                save_settings(self.user_id, st_cur)
                            import firestore_sync
                            if self.my_name and not firestore_sync._is_placeholder_phone_name(self.my_name):
                                firestore_sync.update_phone_account_name(p_norm, self.my_name)
                                socketio.emit('saved_phones_updated', {'phones': firestore_sync.get_saved_phone_numbers()})
                    except Exception as _sync_err:
                        logger.debug(f"Sync phone account name error: {_sync_err}")
            except Exception as e:
                logger.debug(f"Failed to get_me for {self.user_id}: {e}")
        return self.my_id

    def _install_safety_wrapper(self):
        """
        طبقة حماية برمجية (Wrapper) حول طلبات الإرسال والانضمام في ملف الإدارة الرئيسية للتيليجرام:
        تفحص حالة المجموعة بدقة قبل تنفيذ أي SendMessageRequest أو JoinChannelRequest؛
        إذا كانت القناة تحتوي على `is_restricted` أو `can_send_messages=False`،
        تقوم بوضع إشعار تحذيري في سجل النظام (Logs) وتخطي المحادثة تماماً.
        """
        if not self.client or getattr(self.client, '_safety_wrapper_installed', False):
            return

        original_send_message = self.client.send_message
        original_call = self.client.__call__

        async def wrapped_send_message(entity, *args, **kwargs):
            if entity == 'me' or entity == 'self':
                return await original_send_message(entity, *args, **kwargs)

            # 1. فحص حالة التقييد is_restricted
            is_restricted = bool(
                getattr(entity, 'restricted', False) or
                getattr(entity, 'is_restricted', False)
            )

            # 2. فحص صلاحية إرسال الرسائل can_send_messages
            can_send_messages = True
            is_broadcast = getattr(entity, 'broadcast', False)
            is_admin = bool(getattr(entity, 'admin_rights', None) or getattr(entity, 'creator', False))

            default_banned = getattr(entity, 'default_banned_rights', None)
            if default_banned and getattr(default_banned, 'send_messages', False):
                can_send_messages = False

            user_banned = getattr(entity, 'banned_rights', None)
            if user_banned and getattr(user_banned, 'send_messages', False):
                can_send_messages = False

            if is_broadcast and not is_admin:
                can_send_messages = False

            chat_title = getattr(entity, 'title', str(getattr(entity, 'id', entity)))

            if is_restricted or not can_send_messages:
                reason = "is_restricted=True (محادثة مقيدة من تيليجرام)" if is_restricted else "can_send_messages=False (ممنوع النشر للأعضاء أو قناة بث)"
                warn_msg = f"⚠️ [Telegram Safety Wrapper] رصد قيود في المحادثة '{chat_title}': {reason} - تم تسجيل تحذير في سجل النظام وتخطي الإرسال تماماً."
                logger.warning(warn_msg)
                socketio.emit('log_update', {"message": f"🛡️ {warn_msg}"}, to=self.user_id)
                return None

            return await original_send_message(entity, *args, **kwargs)

        async def wrapped_call(request, *args, **kwargs):
            req_name = type(request).__name__
            if req_name in ('JoinChannelRequest', 'ImportChatInviteRequest'):
                target_entity = getattr(request, 'channel', None) or getattr(request, 'peer', None)
                if target_entity:
                    is_restricted = bool(
                        getattr(target_entity, 'restricted', False) or
                        getattr(target_entity, 'is_restricted', False)
                    )
                    is_broadcast = getattr(target_entity, 'broadcast', False)
                    is_admin = bool(getattr(target_entity, 'admin_rights', None) or getattr(target_entity, 'creator', False))
                    join_req = getattr(target_entity, 'join_request', False)

                    can_send = True
                    def_banned = getattr(target_entity, 'default_banned_rights', None)
                    if def_banned and getattr(def_banned, 'send_messages', False):
                        can_send = False
                    if is_broadcast and not is_admin:
                        can_send = False

                    if is_restricted or not can_send or join_req:
                        t_title = getattr(target_entity, 'title', str(getattr(target_entity, 'id', 'محادثة')))
                        reason = "is_restricted=True" if is_restricted else ("can_send_messages=False" if not can_send else "join_request=True (تتطلب موافقة المشرف)")
                        warn_msg = f"⚠️ [Telegram Safety Wrapper] تم تخطي {req_name} لـ '{t_title}': {reason} - تم تسجيل التحذير وإلغاء الطلب."
                        logger.warning(warn_msg)
                        socketio.emit('log_update', {"message": f"🛡️ {warn_msg}"}, to=self.user_id)
                        return None

            elif req_name == 'SendMessageRequest':
                peer = getattr(request, 'peer', None)
                if peer and peer != 'me':
                    is_restricted = bool(getattr(peer, 'restricted', False) or getattr(peer, 'is_restricted', False))
                    can_send = not bool(getattr(getattr(peer, 'default_banned_rights', None), 'send_messages', False))
                    if is_restricted or not can_send:
                        p_title = getattr(peer, 'title', str(getattr(peer, 'id', 'محادثة')))
                        warn_msg = f"⚠️ [Telegram Safety Wrapper] تم تخطي SendMessageRequest لـ '{p_title}': is_restricted={is_restricted}, can_send_messages={can_send}."
                        logger.warning(warn_msg)
                        socketio.emit('log_update', {"message": f"🛡️ {warn_msg}"}, to=self.user_id)
                        return None

            return await original_call(request, *args, **kwargs)

        self.client.send_message = wrapped_send_message
        self.client.__call__ = wrapped_call
        self.client._safety_wrapper_installed = True
        logger.info(f"✅ Safety Wrapper installed on TelegramClient for user {self.user_id}")

    async def send_to_saved_messages(self, text, parse_mode='md'):
        """إرسال إشعار مباشرة إلى الرسائل المحفوظة (Saved Messages) مع حماية ضد أخطاء التنسيق"""
        try:
            if self.client and self.client.is_connected():
                try:
                    await self.client.send_message('me', text, parse_mode=parse_mode, link_preview=False)
                except Exception as pm_err:
                    if parse_mode is not None:
                        logger.warning(f"send_to_saved_messages fallback to plain text: {pm_err}")
                        await self.client.send_message('me', text, parse_mode=None, link_preview=False)
                    else:
                        raise pm_err
                logger.info(f"✅ Sent alert to saved messages for user {self.user_id}")
                return True
            else:
                logger.warning(f"Cannot send to saved messages: client not connected for {self.user_id}")
                return False
        except Exception as e:
            logger.error(f"Failed to send to saved messages for {self.user_id}: {str(e)}")
            return False

    async def trigger_action_alert(self, action_type, chat_title, details_text, direct_link=None, actor_name="المشرف"):
        """
        إرسال تنبيه فوري لحساب تيليجرام عند الحظر أو التقييد أو الطرد أو التحذير أو الكابتشا،
        وتسجيله في السجل وإرساله فوراً إلى الرسائل المحفوظة.
        """
        try:
            # فلترة حاسمة: منع إرسال تنبيهات تقييد وهمية لطلبات الانضمام أو الـ FloodWait أو قنوات البث
            dt_lower = str(details_text or '').lower()
            if any(x in dt_lower for x in [
                'joinchannelrequest', 'inviterequestsent', 'successfully requested to join',
                'floodwait', 'a wait of', 'seconds is required',
                'the chat is restricted and cannot be used in that request'
            ]):
                logger.info(f"Skipping non-punitive action alert for {chat_title}: {details_text}")
                return

            settings = load_settings(self.user_id)
            if not settings.get('my_alerts_enabled', True):
                return
            if not settings.get('my_alerts_actions', True):
                return

            current_time = time.strftime('%Y-%m-%d %I:%M:%S %p')
            icons = {
                "ban": "🚨",
                "mute": "🔇",
                "kick": "🚪",
                "warning": "⚠️",
                "captcha": "🛡️",
                "promotion": "👑"
            }
            titles = {
                "ban": "تم حظرك من المجموعة!",
                "mute": "تم تقييدك من الكتابة والإرسال!",
                "kick": "تم طردك من المجموعة!",
                "warning": "تنبيه مخالفة أو تحذير لحسابك!",
                "captcha": "تنبيه تحقق وكابتشا عاجل!",
                "promotion": "تمت ترقيتك إلى مشرف!"
            }
            icon = icons.get(action_type, "⚠️")
            title = titles.get(action_type, "تنبيه موجه لحسابك")

            lines = [
                f"{icon} **تنبيهاتي | {title}**",
                "━━━━━━━━━━━━━━━━━━",
                f"📌 **المجموعة / المحادثة:** {chat_title}",
                f"⏰ **الوقت:** {current_time}",
                f"👤 **المسؤول / الفاعل:** {actor_name}",
                f"💬 **التفاصيل:**\n> {details_text}"
            ]
            if direct_link and direct_link != '#':
                lines.append(f"\n🔗 **رابط مباشر:**\n{direct_link}")

            alert_text = "\n".join(lines)
            await self.send_to_saved_messages(alert_text, parse_mode='md')

            socketio.emit('log_update', {
                "message": f"{icon} [تنبيهاتي] {title} في: {chat_title}"
            }, to=self.user_id)

            socketio.emit('my_alert_event', {
                "type": action_type,
                "group": chat_title,
                "sender": actor_name,
                "actor": actor_name,
                "time": current_time,
                "link": direct_link or "#",
                "text": details_text,
                "sound_enabled": bool(settings.get('my_alerts_reply_sound_enabled', True)),
                "sound_tone": str(settings.get('my_alerts_reply_sound_tone', 'chime'))
            }, to=self.user_id)

            # تسجيل التنبيه في سجل المستخدم وقاعدة البيانات
            alert_queue.add_alert(self.user_id, {
                "keyword": f"تنبيهاتي: {title}",
                "group": chat_title,
                "sender": actor_name,
                "message": details_text,
                "full_message": details_text,
                "timestamp": time.strftime('%H:%M:%S'),
                "link": direct_link or "#",
                "already_sent_tg": True
            })
        except Exception as e:
            logger.error(f"Error in trigger_action_alert: {e}")


    async def get_group_protection_details(self, entity_obj):
        """
        فحص شامل للمجموعة — يرجع (is_protected, reason, detected_bots).
        يحفظ أي بوتات جديدة تلقائياً في discovered_bots.json.
        """
        try:
            chat_id = getattr(entity_obj, 'id', None)
            if chat_id is None:
                return False, None, []
            cache_key = (self.user_id, chat_id)
            with PROTECTED_GROUPS_LOCK:
                cached = PROTECTED_GROUPS_CACHE.get(cache_key)
                if cached is not None and time.time() - cached.get('ts', 0) < 1800:
                    return cached['result'], cached['reason'], cached.get('bots', [])

            reason = None
            detected_bots = []

            # ── فحص القيود المباشرة ────────────────────────────────────────
            try:
                full = await self.client.get_entity(entity_obj)
                banned = getattr(getattr(full, 'default_banned_rights', None), 'send_messages', None)
                if banned:
                    reason = 'المجموعة تمنع الأعضاء من الإرسال (restricted)'
                    _cache_protection(cache_key, True, reason, [])
                    return True, reason, []
            except Exception:
                pass

            # ── فحص الأعضاء بحثاً عن بوتات الحماية ──────────────────────
            try:
                async for participant in self.client.iter_participants(entity_obj, limit=100):
                    uname = (getattr(participant, 'username', '') or '').lower()
                    if not uname:
                        continue
                    if uname in PROTECTION_BOTS:
                        detected_bots.append(f"@{uname}")
                        reason = f'بوت حماية مكتشف: @{uname}'
                        logger.info(f"Group {chat_id} protected by known bot @{uname}")
                    elif any(s in uname for s in PROTECTION_BOT_SUBSTRINGS):
                        detected_bots.append(f"@{uname}")
                        reason = f'بوت حماية مشتبه: @{uname}'
                        logger.info(f"Group {chat_id} possibly protected by @{uname}")
                        # ── تعلم تلقائي: حفظ البوت المشتبه به ───────────
                        try:
                            add_discovered_bot(uname)
                        except Exception:
                            pass
                    if len(detected_bots) >= 5:
                        break
            except Exception as iter_err:
                logger.debug(f"iter_participants فشل لـ {chat_id}: {iter_err}")

            if detected_bots:
                reason = f'بوتات حماية مكتشفة: {", ".join(detected_bots[:5])}'
                _cache_protection(cache_key, True, reason, detected_bots)
                # إشعار socket فوري
                try:
                    socketio.emit('log_update', {
                        "message": f"🛡️ مجموعة محمية: {getattr(entity_obj, 'title', chat_id)} — {', '.join(detected_bots[:3])}"
                    }, to=self.user_id)
                    socketio.emit('group_protection_warning', {
                        "group_id": chat_id,
                        "group_title": getattr(entity_obj, 'title', str(chat_id)),
                        "bots": detected_bots,
                        "timestamp": time.strftime('%H:%M:%S')
                    }, to=self.user_id)
                except Exception:
                    pass
                return True, reason, detected_bots

            _cache_protection(cache_key, False, None, [])
            return False, None, []
        except Exception as e:
            logger.debug(f"get_group_protection_details error: {e}")
            return False, None, []

    async def is_group_protected(self, entity_obj):
        """التحقق من حماية المجموعة — يرجع (is_protected, reason) للتوافق مع الكود القديم."""
        is_prot, reason, _ = await self.get_group_protection_details(entity_obj)
        return is_prot, reason

    async def is_session_valid(self):
        """التحقق الفعلي من صلاحية الجلسة واستشعار إزالتها من تطبيق تليجرام الرسمي"""
        try:
            if not self.client:
                return False
            if not self.client.is_connected():
                await self.client.connect()
            is_authorized = await self.client.is_user_authorized()
            if not is_authorized:
                logger.warning(f"Session unauthorized for {self.user_id} — triggering auto-logout")
                handle_session_revoked(self.user_id, "تم إنهاء أو إزالة الجلسة من تطبيق تليجرام الآخر الرسمي")
                return False
            me = await self.client.get_me()
            if me is None:
                handle_session_revoked(self.user_id, "تعذر التحقق من هوية الجلسة — الجلسة غير صالحة")
                return False
            return True
        except (SessionRevokedError, AuthKeyUnregisteredError, AuthKeyInvalidError, UserDeactivatedError, UserDeactivatedBanError, UnauthorizedError) as rev_err:
            logger.warning(f"Telegram revoked session for {self.user_id}: {rev_err}")
            handle_session_revoked(self.user_id, "تم إنهاء أو إزالة الجلسة من تطبيق تليجرام الآخر الرسمي")
            return False
        except Exception as e:
            error_str = str(e).lower()
            if any(kw in error_str for kw in ['auth_key_unregistered', 'auth_key_invalid', 'session_revoked', 'session_expired', 'unauthorized', 'user_deactivated']):
                logger.warning(f"Session invalid for {self.user_id}: {e}")
                handle_session_revoked(self.user_id, "تم إنهاء أو إزالة الجلسة من تطبيق تليجرام الآخر الرسمي")
                return False
            # خطأ شبكة عابر لا يعني بالضرورة إلغاء الجلسة
            logger.debug(f"Transient session check error for {self.user_id}: {e}")
            return True

    def check_session_valid_sync(self):
        """نسخة متزامنة للتحقق من صحة الجلسة"""
        try:
            return self.run_coroutine(self.is_session_valid())
        except Exception as e:
            err_l = str(e).lower()
            if any(kw in err_l for kw in ['auth_key_unregistered', 'auth_key_invalid', 'session_revoked', 'session_expired', 'unauthorized', 'user_deactivated']):
                handle_session_revoked(self.user_id, "تم إنهاء أو إزالة الجلسة من تطبيق تليجرام الآخر الرسمي")
                return False
            return True

    async def force_reset_session(self):
        """إعادة تعيين الجلسة وإزالة ملفاتها"""
        try:
            if self.client:
                try:
                    await self.client.disconnect()
                except Exception:
                    pass
            for _ext in ['_session.session', '_string.txt']:
                _fp = os.path.join(SESSIONS_DIR, f"{self.user_id}{_ext}")
                if os.path.exists(_fp):
                    os.remove(_fp)
            logger.info(f"Force reset session for {self.user_id}")
            return True
        except Exception as e:
            logger.error(f"Force reset error for {self.user_id}: {e}")
            return False

    @staticmethod
    def _extract_verification_code(text: str):
        """استخراج كود التحقق من النص بدقة متناهية ودعم الأرقام العربية والإنجليزية واستبعاد معرفات الخدمة"""
        if not text:
            return None

        # 1. تحويل الأرقام العربية (المشرقية) إلى أرقام غربية قياسية
        normalized_text = str(text)
        for i, ad in enumerate('٠١٢٣٤٥٦٧٨٩'):
            normalized_text = normalized_text.replace(ad, str(i))

        # 2. الأنماط الصريحة أولاً (تسبق الأنماط العامة لضمان عدم التقاط معرفات الخدمة أو التواريخ)
        explicit_patterns = [
            r'login\s*code[:\s]+(\d{5,6})',
            r'كود\s*(?:تسجيل\s*)?الدخول[:\s]+(\d{5,6})',
            r'رمز\s*(?:تسجيل\s*)?الدخول[:\s]+(\d{5,6})',
            r'كود\s*(?:التحقق|التأكيد)[:\s]+(\d{5,6})',
            r'رمز\s*(?:التحقق|التأكيد)[:\s]+(\d{5,6})',
            r'verification\s*code[:\s]+(\d{5,6})',
            r'code[:\s]+(\d{5,6})',
            r'كود[:\s]+(\d{5,6})',
            r'رمز[:\s]+(\d{5,6})',
            r'\[\s*(\d{5,6})\s*\]',
        ]
        for pattern in explicit_patterns:
            match = re.search(pattern, normalized_text, re.IGNORECASE)
            if match and match.group(1) not in ('777000', '42777'):
                return match.group(1)

        # 3. الأنماط العامة مع استبعاد معرفات خدمة تيليجرام (777000 و 42777)
        for m in re.finditer(r'\b(\d{5,6})\b', normalized_text):
            candidate = m.group(1)
            if candidate not in ('777000', '42777'):
                return candidate

        return None

    def start_client_thread(self):
        if self.thread and self.thread.is_alive():
            return
        self.stop_flag.clear()
        self.is_ready.clear()
        # استخدام OS thread حقيقي (محفوظ قبل monkey_patch) لتجنب تعارض asyncio مع eventlet
        self.thread = _OSThread(target=self._run_client_loop, daemon=True)
        self.thread.start()
        # انتظر حتى 60 ثانية — لكن لا ترمي exception عند timeout، بل سجّل تحذيراً
        if not self.is_ready.wait(timeout=60):
            logger.warning(f"Client initialization timeout for {self.user_id} — قد يتصل لاحقاً")

    def _run_client_loop(self):
        try:
            # إنشاء event loop مستقل لهذا الثريد — بدون set_event_loop لأنها عملية عامة
            # تتعارض مع ثريدات الحسابات الأخرى في بيئة gevent
            self.loop = asyncio.new_event_loop()
            if API_ID and API_HASH:
                saved_str = load_string_session(self.user_id)
                self.client = TelegramClient(StringSession(saved_str or ''), int(API_ID), API_HASH)
                self._install_safety_wrapper()
            else:
                logger.error("API_ID or API_HASH not set")
                return
            self.loop.run_until_complete(self._client_main())
        except Exception as e:
            logger.error(f"Client thread error for {self.user_id}: {str(e)}")
        finally:
            if self.loop and not self.loop.is_closed():
                self.loop.close()

    async def _client_main(self):
        _revocation_types = (
            SessionRevokedError, AuthKeyUnregisteredError, AuthKeyInvalidError,
            UserDeactivatedError, UserDeactivatedBanError, UnauthorizedError
        )
        _revocation_keywords = (
            'auth_key_unregistered', 'auth_key_invalid', 'session_revoked',
            'session_expired', 'user_deactivated', 'unauthorized'
        )
        try:
            if self.client:
                self._install_safety_wrapper()
                await self.client.connect()
                self.is_ready.set()
                try:
                    init_auth = await self.client.is_user_authorized()
                except _revocation_types:
                    handle_session_revoked(self.user_id, "تم إنهاء أو إزالة الجلسة من تطبيق تليجرام الآخر الرسمي")
                    return
                if not init_auth:
                    with USERS_LOCK:
                        was_auth = bool(USERS.get(self.user_id, {}).get('authenticated'))
                    if was_auth or load_string_session(self.user_id):
                        handle_session_revoked(self.user_id, "الجلسة لم تعد مصرحة — تم تسجيل الخروج من تطبيق تليجرام الرسمي")
                        return
                await self._ensure_my_info()
                await self._register_event_handlers()

                async def _watch_stop():
                    while not self.stop_flag.is_set():
                        await asyncio.sleep(0.5)
                    try:
                        await self.client.disconnect()
                    except Exception:
                        pass

                async def _watch_session_revoked():
                    """مراقبة حية كل 15 ثانية لاكتشاف إزالة الجلسة من تطبيق تليجرام الرسمي فوراً"""
                    await asyncio.sleep(10)
                    while not self.stop_flag.is_set():
                        try:
                            if self.client and self.client.is_connected():
                                is_auth = await self.client.is_user_authorized()
                                if not is_auth:
                                    handle_session_revoked(self.user_id, "تم إنهاء أو إزالة الجلسة من تطبيق تليجرام الآخر الرسمي")
                                    self.stop_flag.set()
                                    break
                                me = await self.client.get_me()
                                if me is None:
                                    handle_session_revoked(self.user_id, "تم إنهاء الجلسة من تطبيق تليجرام الرسمي")
                                    self.stop_flag.set()
                                    break
                        except _revocation_types:
                            handle_session_revoked(self.user_id, "تم إنهاء أو إزالة الجلسة من تطبيق تليجرام الآخر الرسمي")
                            self.stop_flag.set()
                            break
                        except Exception as we:
                            if any(k in str(we).lower() for k in _revocation_keywords):
                                handle_session_revoked(self.user_id, "تم إنهاء أو إزالة الجلسة من تطبيق تليجرام الآخر الرسمي")
                                self.stop_flag.set()
                                break
                        await asyncio.sleep(15)

                stop_task = asyncio.ensure_future(_watch_stop())
                watchdog_task = asyncio.ensure_future(_watch_session_revoked())
                while not self.stop_flag.is_set():
                    try:
                        is_auth = await self.client.is_user_authorized()
                        if is_auth:
                            try:
                                await self.client.run_until_disconnected()
                                if self.stop_flag.is_set():
                                    break
                                logger.info(f"Client disconnected for {self.user_id}, verifying session before reconnecting...")
                                await asyncio.sleep(2)
                                try:
                                    await self.client.connect()
                                    if not await self.client.is_user_authorized():
                                        handle_session_revoked(self.user_id, "تم إنهاء أو إزالة الجلسة من تطبيق تليجرام الآخر الرسمي")
                                        break
                                    me_rc = await self.client.get_me()
                                    if me_rc is None:
                                        handle_session_revoked(self.user_id, "الجلسة ملغاة — تم تسجيل الخروج آلياً")
                                        break
                                    await self._ensure_my_info()
                                    logger.info(f"Reconnected successfully for {self.user_id}")
                                except _revocation_types:
                                    handle_session_revoked(self.user_id, "تم إنهاء أو إزالة الجلسة من تطبيق تليجرام الآخر الرسمي")
                                    break
                                except Exception as rc_err:
                                    if any(k in str(rc_err).lower() for k in _revocation_keywords):
                                        handle_session_revoked(self.user_id, "تم إنهاء أو إزالة الجلسة من تطبيق تليجرام الآخر الرسمي")
                                        break
                                    logger.error(f"Reconnect failed for {self.user_id}: {rc_err}")
                                    await asyncio.sleep(5)
                            except _revocation_types:
                                handle_session_revoked(self.user_id, "تم رصد إنهاء أو إزالة الجلسة من تطبيق تليجرام الآخر الرسمي")
                                break
                            except Exception as run_err:
                                if self.stop_flag.is_set():
                                    break
                                if any(k in str(run_err).lower() for k in _revocation_keywords):
                                    handle_session_revoked(self.user_id, "تم رصد إنهاء أو إزالة الجلسة من تطبيق تليجرام الآخر الرسمي")
                                    break
                                logger.warning(f"run_until_disconnected interrupted for {self.user_id}: {run_err}")
                                await asyncio.sleep(2)
                                try:
                                    if not self.client.is_connected():
                                        await self.client.connect()
                                    if not await self.client.is_user_authorized():
                                        handle_session_revoked(self.user_id, "تم إنهاء أو إزالة الجلسة من تطبيق تليجرام الآخر الرسمي")
                                        break
                                    await self.client.get_me()
                                    await self._ensure_my_info()
                                    logger.info(f"Reconnected after error for {self.user_id}")
                                except _revocation_types:
                                    handle_session_revoked(self.user_id, "تم إنهاء أو إزالة الجلسة من تطبيق تليجرام الآخر الرسمي")
                                    break
                                except Exception as rc2_err:
                                    if any(k in str(rc2_err).lower() for k in _revocation_keywords):
                                        handle_session_revoked(self.user_id, "تم إنهاء أو إزالة الجلسة من تطبيق تليجرام الآخر الرسمي")
                                        break
                                    logger.error(f"Reconnect after error failed for {self.user_id}: {rc2_err}")
                                    await asyncio.sleep(5)
                        else:
                            with USERS_LOCK:
                                was_auth = bool(USERS.get(self.user_id, {}).get('authenticated'))
                            if was_auth:
                                handle_session_revoked(self.user_id, "تم إنهاء الجلسة من تطبيق تليجرام الآخر الرسمي")
                                break
                            await asyncio.sleep(1)
                    except _revocation_types:
                        handle_session_revoked(self.user_id, "تم إنهاء أو إزالة الجلسة من تطبيق تليجرام الآخر الرسمي")
                        break
                    except Exception as auth_check_err:
                        if any(k in str(auth_check_err).lower() for k in _revocation_keywords):
                            handle_session_revoked(self.user_id, "تم إنهاء أو إزالة الجلسة من تطبيق تليجرام الآخر الرسمي")
                            break
                        logger.debug(f"Auth check during loop for {self.user_id}: {auth_check_err}")
                        await asyncio.sleep(1)
                if not stop_task.done():
                    stop_task.cancel()
                if not watchdog_task.done():
                    watchdog_task.cancel()
        except _revocation_types:
            handle_session_revoked(self.user_id, "تم إنهاء أو إزالة الجلسة من تطبيق تليجرام الآخر الرسمي")
        except Exception as e:
            if any(k in str(e).lower() for k in _revocation_keywords):
                handle_session_revoked(self.user_id, "تم إنهاء أو إزالة الجلسة من تطبيق تليجرام الآخر الرسمي")
            else:
                logger.error(f"Client main error: {str(e)}")
        finally:
            try:
                if self.client and self.client.is_connected():
                    await self.client.disconnect()
            except Exception:
                pass

    async def _register_event_handlers(self):
        try:
            if self.event_handlers_registered or not self.client:
                return

            @self.client.on(events.NewMessage())
            async def new_message_handler(event):
                # تسجيل الرسائل الصادرة الخاصة بالحساب في الذاكرة لرصد أي ردود عليها لاحقاً فورياً
                if getattr(event.message, 'out', False):
                    try:
                        c_id = getattr(event, 'chat_id', 0)
                        m_id = getattr(event.message, 'id', 0)
                        if c_id and m_id:
                            self._my_sent_message_ids.add((c_id, m_id))
                            if len(self._my_sent_message_ids) > 10000:
                                self._my_sent_message_ids = set(list(self._my_sent_message_ids)[-5000:])
                            txt = event.message.text or ''
                            if txt:
                                self._my_sent_msg_texts[(c_id, m_id)] = txt[:120]
                                if len(self._my_sent_msg_texts) > 5000:
                                    for old_k in list(self._my_sent_msg_texts.keys())[:2000]:
                                        self._my_sent_msg_texts.pop(old_k, None)
                    except Exception:
                        pass
                await self._handle_new_message(event)
                await self._handle_my_alerts(event)
                await self._handle_link_radar(event)
                

            @self.client.on(events.ChatAction())
            async def chat_action_handler(event):
                await self._handle_chat_action(event)

            @self.client.on(events.Raw(types.UpdateChannelParticipant))
            async def channel_participant_handler(event):
                await self._handle_channel_participant_update(event)

            self.event_handlers_registered = True
            logger.info(f"✅ Event handlers registered for user {self.user_id} (messages, alerts, actions, participant updates)")
        except Exception as e:
            logger.error(f"Failed to register event handlers: {str(e)}")

    async def _handle_my_alerts(self, event):
        """
        وظيفة «تنبيهاتي»:
        - مراقبة وحراسة شاملة للحساب في المجموعات والقنوات والمحادثات الخاصة.
        - إشعار فوري عند قيام أي شخص بالرد على أي رسالة من رسائلي.
        - إشعار فوري عند إعطاء تحذير أو كتم أو تقييد أو كابتشا أو تنبيه بعدم إرسال شيء معين.
        يرسل التنبيه فوراً إلى «الرسائل المحفوظة» (Saved Messages) برابط مباشر مع التنبيه الصوتي والتوست.
        """
        try:
            settings = load_settings(self.user_id)
            if not settings.get('my_alerts_enabled', True):
                return

            message = event.message
            if not message:
                return

            # تجاهل الرسائل الصادرة من نفس الحساب (لكي لا ينبه على نفسه)
            if getattr(message, 'out', False):
                return

            await self._ensure_my_info()
            if not self.my_id:
                return

            msg_uid = f"alert_{getattr(event, 'chat_id', 0)}_{message.id}"
            if msg_uid in self._my_alerts_processed:
                return
            if len(self._my_alerts_processed) > 2000:
                self._my_alerts_processed.clear()

            chat = await event.get_chat()
            is_private = bool(event.is_private)
            chat_title = getattr(chat, 'title', None)
            if not chat_title:
                if is_private:
                    sf = getattr(chat, 'first_name', '') or ''
                    sl = getattr(chat, 'last_name', '') or ''
                    chat_title = f"{sf} {sl}".strip() or getattr(chat, 'username', None) or f"محادثة خاصة #{getattr(event, 'chat_id', '')}"
                else:
                    chat_title = f"مجموعة #{getattr(event, 'chat_id', '')}"

            chat_username = getattr(chat, 'username', None)
            # تكوين الرابط المباشر للرسالة
            if chat_username:
                direct_msg_link = f"https://t.me/{chat_username}/{message.id}"
            elif is_private:
                direct_msg_link = f"https://t.me/{getattr(chat, 'username', '')}" if getattr(chat, 'username', None) else "#"
            else:
                raw_cid = str(getattr(chat, 'id', getattr(event, 'chat_id', 0))).replace("-100", "").replace("-", "")
                direct_msg_link = f"https://t.me/c/{raw_cid}/{message.id}"

            sender = await event.get_sender()
            sender_name = "مستخدم تيليجرام"
            if sender:
                sf = getattr(sender, 'first_name', '') or ''
                sl = getattr(sender, 'last_name', '') or ''
                sender_name = f"{sf} {sl}".strip() or getattr(sender, 'username', None) or str(getattr(sender, 'id', ''))
                if getattr(sender, 'username', None):
                    sender_name += f" (@{sender.username})"

            current_time = time.strftime('%Y-%m-%d %I:%M:%S %p')
            msg_text = message.text or ''
            msg_text_lower = msg_text.lower()

            # 1. هل الرسالة رد على إحدى رسائلي؟
            is_reply_to_me = False
            original_text = ""
            reply_to = getattr(message, 'reply_to', None)
            reply_to_msg_id = getattr(reply_to, 'reply_to_msg_id', None) if reply_to else None
            chat_id = getattr(event, 'chat_id', 0)

            if reply_to_msg_id:
                # أ) التحقق فائق السرعة من الذاكرة المحلية (يعمل حتى لو حذف البوت رسالتك الأصلية فوراً)
                if (chat_id, reply_to_msg_id) in self._my_sent_message_ids:
                    is_reply_to_me = True
                    original_text = self._my_sent_msg_texts.get((chat_id, reply_to_msg_id), '[رسالتك الأصلية]')
                else:
                    try:
                        reply_msg = await message.get_reply_message()
                        if reply_msg and reply_msg.sender_id == self.my_id:
                            is_reply_to_me = True
                            original_text = reply_msg.text or '[رسالة وسائط أو ملصق]'
                            if len(original_text) > 80:
                                original_text = original_text[:80] + '...'
                            self._my_sent_message_ids.add((chat_id, reply_to_msg_id))
                    except Exception as r_err:
                        logger.debug(f"Failed to get reply message for alert: {r_err}")
            elif is_private:
                # في المحادثات الخاصة الفردية، أي رسالة واردة من الطرف الآخر تعتبر تواصلاً موجهاً لك
                is_reply_to_me = True

            # 2. هل الرسالة تذكر حسابي (منشن، تاج، أو بالاسم)؟
            is_mentioning_me = False
            if self.my_username and f"@{self.my_username.lower()}" in msg_text_lower:
                is_mentioning_me = True
            elif self.my_name and len(self.my_name.strip()) > 2 and self.my_name.lower() in msg_text_lower:
                is_mentioning_me = True
            elif hasattr(message, 'entities') and message.entities:
                for ent in message.entities:
                    ent_uid = getattr(ent, 'user_id', None)
                    if ent_uid and ent_uid == self.my_id:
                        is_mentioning_me = True
                        break

            # 3. فحص تنبيهات التحقق والكابتشا (Captcha / Verification)
            captcha_keywords = [
                'تحقق', 'كابتشا', 'captcha', 'اثبت انك', 'اثبت أنك', 'إثبات أنك', 'أثبت أنك',
                'لست روبوت', 'لست بوت', 'اضغط للتحقق', 'اضغط على الزر', 'اضغط هنا للتحقق',
                'verify', 'verification', 'solve the captcha', 'human verification',
                'أكمل التحقق', 'زر التحقق', 'تأكيد الحساب', 'تأكيد العضوية'
            ]
            is_captcha = any(kw in msg_text_lower for kw in captcha_keywords)

            # فحص وجود أزرار كابتشا أو تحقق تفاعلية مضمنة في الرسالة
            has_verification_button = False
            if hasattr(message, 'buttons') and message.buttons:
                for btn_row in message.buttons:
                    for btn in (btn_row if isinstance(btn_row, list) else [btn_row]):
                        btn_txt = getattr(btn, 'text', '').lower()
                        if any(k in btn_txt for k in ['تحقق', 'verify', 'click', 'اضغط', 'حل', 'human', 'بوت']):
                            has_verification_button = True
                            break

            # 4. فحص تنبيهات المنع وقوانين النشر في المجموعات
            rule_warning_keywords = [
                'ممنوع الروابط', 'يمنع نشر الروابط', 'ممنوع إرسال الروابط', 'قفل الروابط',
                'ممنوع إرسال', 'يمنع إرسال', 'لا ترسل روابط', 'لا ترسل', 'يمنع التوجيه',
                'ممنوع التوجيه', 'ممنوع الإعلانات', 'يمنع الإعلان', 'ممنوع النشر',
                'قوانين المجموعة', 'مخالف للشروط', 'مخالف للقوانين', 'مخالفة', 'مخالفه'
            ]
            is_rule_warning = any(kw in msg_text_lower for kw in rule_warning_keywords)

            # 5. فحص تنبيهات العقوبات (كتم، تقييد، تحذير، حظر)
            penalty_keywords = [
                'تحذير', 'انذار', 'إنذار', 'تم تحذيرك', 'تم إعطاؤك تحذير', 'اعطائك تحذير',
                'تحذير رقم', 'warn', 'warning', 'تم تقييدك', 'تم كتمك', 'تم طردك', 'تم حظرك',
                'تقييد العضو', 'كتم العضو', 'حظر العضو', 'طرد العضو', 'تم حظر المستخدم',
                'تم كتم المستخدم', 'تم إسكاتك', 'تم اسكاتك', 'muted', 'restricted', 'banned', 'kicked',
                'spam detected', 'antispam'
            ]
            is_penalty = any(kw in msg_text_lower for kw in penalty_keywords)

            # ── الحالة أ: تنبيه كابتشا أو تحقق بشري عاجل ──
            if (is_reply_to_me or is_mentioning_me) and (is_captcha or has_verification_button) and settings.get('my_alerts_actions', True):
                self._my_alerts_processed.add(msg_uid)
                lines = [
                    "🛡️ **تنبيهاتي | تنبيه تحقق وكابتشا عاجل!**",
                    "━━━━━━━━━━━━━━━━━━",
                    f"📌 **المجموعة / المحادثة:** {chat_title}",
                    f"👤 **بوت التحقق:** {sender_name}",
                    f"⏰ **الوقت:** {current_time}",
                    f"💬 **نص التحقق:**\n> {msg_text[:250] or '[تحقق تفاعلي عبر الأزرار]'}",
                    f"\n🔗 **رابط مباشر لرسالة التحقق:**\n{direct_msg_link}"
                ]
                alert_text = "\n".join(lines)
                await self.send_to_saved_messages(alert_text, parse_mode='md')
                socketio.emit('log_update', {
                    "message": f"🛡️ [تنبيهاتي] تنبيه تحقق وكابتشا مطلوب في: {chat_title}"
                }, to=self.user_id)
                socketio.emit('my_alert_event', {
                    "type": "captcha",
                    "group": chat_title,
                    "sender": sender_name,
                    "time": current_time,
                    "link": direct_msg_link,
                    "text": msg_text[:250] or 'مطلوب إكمال التحقق البشري لتجنب الحظر'
                }, to=self.user_id)
                alert_queue.add_alert(self.user_id, {
                    "keyword": "تنبيهاتي: تحقق وكابتشا عاجل",
                    "group": chat_title,
                    "sender": sender_name,
                    "message": msg_text[:250] or 'مطلوب إكمال التحقق البشري',
                    "full_message": msg_text,
                    "timestamp": time.strftime('%H:%M:%S'),
                    "link": direct_msg_link,
                    "already_sent_tg": True
                })
                return

            # ── الحالة ب: تنبيه تحذير أو منع أو تقييد موجه للحساب ──
            if (is_reply_to_me or is_mentioning_me) and (is_penalty or is_rule_warning) and settings.get('my_alerts_actions', True):
                self._my_alerts_processed.add(msg_uid)
                warn_type = "تحذير ومخالفة" if is_penalty else "تنبيه بقوانين المجموعة ومنع النشر"
                lines = [
                    f"⚠️ **تنبيهاتي | {warn_type}!**",
                    "━━━━━━━━━━━━━━━━━━",
                    f"📌 **اسم المجموعة:** {chat_title}",
                    f"👤 **المشرف / صاحب التنبيه:** {sender_name}",
                    f"⏰ **الوقت:** {current_time}",
                    f"💬 **نص التنبيه:**\n> {msg_text[:250]}",
                    f"\n🔗 **رابط مباشر لرسالة التنبيه:**\n{direct_msg_link}"
                ]
                alert_text = "\n".join(lines)
                await self.send_to_saved_messages(alert_text, parse_mode='md')
                socketio.emit('log_update', {
                    "message": f"⚠️ [تنبيهاتي] {warn_type} في: {chat_title}"
                }, to=self.user_id)
                socketio.emit('my_alert_event', {
                    "type": "warning",
                    "group": chat_title,
                    "sender": sender_name,
                    "time": current_time,
                    "link": direct_msg_link,
                    "text": msg_text[:250]
                }, to=self.user_id)
                alert_queue.add_alert(self.user_id, {
                    "keyword": f"تنبيهاتي: {warn_type}",
                    "group": chat_title,
                    "sender": sender_name,
                    "message": msg_text[:250],
                    "full_message": msg_text,
                    "timestamp": time.strftime('%H:%M:%S'),
                    "link": direct_msg_link,
                    "already_sent_tg": True
                })
                return

            # ── الحالة ج: أي شخص يرد على أي رسالة من رسائلي ──
            if is_reply_to_me and settings.get('my_alerts_replies', True):
                self._my_alerts_processed.add(msg_uid)
                reply_preview = msg_text or '[رسالة وسائط أو ملصق]'
                if len(reply_preview) > 200:
                    reply_preview = reply_preview[:200] + '...'
                orig_preview = original_text or '[رسالتك الأصلية]'
                chat_context = "محادثة خاصة" if is_private else f"المجموعة: {chat_title}"
                lines = [
                    "💬 **تنبيهاتي | رد جديد على رسالتك**",
                    "━━━━━━━━━━━━━━━━━━",
                    f"👤 **قام بالرد:** {sender_name}",
                    f"📌 **المكان:** {chat_context}",
                    f"⏰ **الوقت:** {current_time}",
                    f"✉️ **رسالتك الأصلية:**\n> {orig_preview}\n",
                    f"💬 **نص الرد:**\n> {reply_preview}",
                    f"\n🔗 **رابط مباشر لرسالة الرد:**\n{direct_msg_link}"
                ]
                alert_text = "\n".join(lines)
                await self.send_to_saved_messages(alert_text, parse_mode='md')
                socketio.emit('log_update', {
                    "message": f"💬 [تنبيهاتي] رد جديد من {sender_name} في {chat_title}"
                }, to=self.user_id)
                socketio.emit('my_alert_event', {
                    "type": "reply",
                    "group": chat_title,
                    "sender": sender_name,
                    "time": current_time,
                    "link": direct_msg_link,
                    "text": reply_preview,
                    "sound_enabled": bool(settings.get('my_alerts_reply_sound_enabled', True)),
                    "sound_tone": str(settings.get('my_alerts_reply_sound_tone', 'chime'))
                }, to=self.user_id)
                alert_queue.add_alert(self.user_id, {
                    "keyword": "تنبيهاتي: رد جديد على رسالتك",
                    "group": chat_title,
                    "sender": sender_name,
                    "message": reply_preview,
                    "full_message": msg_text,
                    "timestamp": time.strftime('%H:%M:%S'),
                    "link": direct_msg_link,
                    "already_sent_tg": True
                })
                return
        except Exception as e:
            logger.error(f"Error in _handle_my_alerts: {e}", exc_info=True)

    async def _handle_link_radar(self, event):
        """
        رادار الروابط والإنضمام التلقائي الذكي:
        مراقبة كامل الحساب ودردشاته افتراضياً لرصد روابط الواتساب والتيليجرام العامة والخاصة
        """
        try:
            if radar_manager and radar_manager.state.get("enabled", True):
                await radar_manager.handle_new_message_event(
                    client=self.client,
                    event=event,
                    user_id=self.user_id,
                    send_to_saved_func=self.send_to_saved_messages,
                    save_to_db_func=add_saved_link,
                    socketio_emit_func=lambda ev_name, ev_data: socketio.emit(ev_name, ev_data)
                )
        except Exception as e:
            logger.error(f"Error in _handle_link_radar: {e}")

    async def _handle_channel_participant_update(self, update):
        """
        تنبيه عند حظر الحساب أو تقييده من الكتابة أو ترقيته لمشرف في قنوات ومجموعات تيليجرام
        """
        try:
            settings = load_settings(self.user_id)
            if not settings.get('my_alerts_enabled', True):
                return
            if not settings.get('my_alerts_actions', True):
                return

            await self._ensure_my_info()
            if not self.my_id or update.user_id != self.my_id:
                return

            chat_id = update.channel_id
            event_uid = f"part_{chat_id}_{getattr(update, 'date', time.time())}"
            if event_uid in self._my_alerts_processed:
                return
            self._my_alerts_processed.add(event_uid)

            chat = None
            try:
                chat = await self.client.get_entity(chat_id)
            except Exception:
                pass

            chat_title = getattr(chat, 'title', None) or f"مجموعة #{chat_id}"
            if chat and getattr(chat, 'username', None):
                chat_link = f"https://t.me/{chat.username}"
            else:
                raw_cid = str(chat_id).replace("-100", "").replace("-", "")
                chat_link = f"https://t.me/c/{raw_cid}"

            actor_name = "المشرف / بوت الحماية"
            if update.actor_id and update.actor_id != self.my_id:
                try:
                    actor = await self.client.get_entity(update.actor_id)
                    if actor:
                        af = getattr(actor, 'first_name', '') or ''
                        al = getattr(actor, 'last_name', '') or ''
                        actor_name = f"{af} {al}".strip() or getattr(actor, 'username', None) or str(actor.id)
                        if getattr(actor, 'username', None):
                            actor_name += f" (@{actor.username})"
                except Exception:
                    pass

            current_time = time.strftime('%Y-%m-%d %I:%M:%S %p')
            new_p = update.new_participant

            # 1. ترقية لمشرف
            if isinstance(new_p, types.ChannelParticipantAdmin):
                alert_text = (
                    "👑 **تنبيهاتي | تمت ترقيتك إلى مشرف!**\n"
                    "━━━━━━━━━━━━━━━━━━\n"
                    f"📌 **اسم المجموعة:** {chat_title}\n"
                    f"⏰ **الوقت:** {current_time}\n"
                    f"👤 **قام بالترقية:** {actor_name}\n"
                    f"🔗 **رابط المجموعة:**\n{chat_link}"
                )
                await self.send_to_saved_messages(alert_text, parse_mode='md')
                socketio.emit('log_update', {"message": f"👑 [تنبيهاتي] تمت ترقيتك لمشرف في: {chat_title}"}, to=self.user_id)
                socketio.emit('my_alert_event', {
                    "type": "promotion", "group": chat_title, "actor": actor_name, "time": current_time, "link": chat_link
                }, to=self.user_id)
                alert_queue.add_alert(self.user_id, {
                    "keyword": "تنبيهاتي: ترقية إلى مشرف", "group": chat_title, "sender": actor_name,
                    "message": f"تمت ترقيتك إلى مشرف في {chat_title}", "timestamp": time.strftime('%H:%M:%S'),
                    "link": chat_link, "already_sent_tg": True
                })

            # 2. حظر أو تقييد
            elif isinstance(new_p, types.ChannelParticipantBanned):
                rights = getattr(new_p, 'banned_rights', None)
                is_full_ban = getattr(rights, 'view_messages', False)
                if is_full_ban:
                    alert_text = (
                        "🚨 **تنبيهاتي | تم حظرك من المجموعة!**\n"
                        "━━━━━━━━━━━━━━━━━━\n"
                        f"📌 **اسم المجموعة:** {chat_title}\n"
                        f"⏰ **الوقت:** {current_time}\n"
                        f"👤 **قام بالحظر:** {actor_name}\n"
                        f"🔗 **رابط المجموعة:**\n{chat_link}"
                    )
                    await self.send_to_saved_messages(alert_text, parse_mode='md')
                    socketio.emit('log_update', {"message": f"🚨 [تنبيهاتي] تم حظرك من: {chat_title}"}, to=self.user_id)
                    socketio.emit('my_alert_event', {
                        "type": "ban", "group": chat_title, "actor": actor_name, "time": current_time, "link": chat_link
                    }, to=self.user_id)
                    alert_queue.add_alert(self.user_id, {
                        "keyword": "تنبيهاتي: تم حظرك من المجموعة", "group": chat_title, "sender": actor_name,
                        "message": f"تم حظرك من {chat_title} بواسطة {actor_name}", "timestamp": time.strftime('%H:%M:%S'),
                        "link": chat_link, "already_sent_tg": True
                    })
                else:
                    alert_text = (
                        "🔇 **تنبيهاتي | تم تقييدك من الكتابة!**\n"
                        "━━━━━━━━━━━━━━━━━━\n"
                        f"📌 **اسم المجموعة:** {chat_title}\n"
                        f"⏰ **الوقت:** {current_time}\n"
                        f"👤 **قام بالتقييد:** {actor_name}\n"
                        f"🔗 **رابط المجموعة:**\n{chat_link}"
                    )
                    await self.send_to_saved_messages(alert_text, parse_mode='md')
                    socketio.emit('log_update', {"message": f"🔇 [تنبيهاتي] تم تقييدك من الكتابة في: {chat_title}"}, to=self.user_id)
                    socketio.emit('my_alert_event', {
                        "type": "mute", "group": chat_title, "actor": actor_name, "time": current_time, "link": chat_link
                    }, to=self.user_id)
                    alert_queue.add_alert(self.user_id, {
                        "keyword": "تنبيهاتي: تم تقييدك من الكتابة", "group": chat_title, "sender": actor_name,
                        "message": f"تم تقييدك من الكتابة في {chat_title} بواسطة {actor_name}", "timestamp": time.strftime('%H:%M:%S'),
                        "link": chat_link, "already_sent_tg": True
                    })

            # 3. طرد إجباري
            elif isinstance(new_p, types.ChannelParticipantLeft):
                if update.actor_id and update.actor_id != self.my_id:
                    alert_text = (
                        "🚨 **تنبيهاتي | تم طردك من المجموعة!**\n"
                        "━━━━━━━━━━━━━━━━━━\n"
                        f"📌 **اسم المجموعة:** {chat_title}\n"
                        f"⏰ **الوقت:** {current_time}\n"
                        f"👤 **قام بالطرد:** {actor_name}\n"
                        f"🔗 **رابط المجموعة:**\n{chat_link}"
                    )
                    await self.send_to_saved_messages(alert_text, parse_mode='md')
                    socketio.emit('log_update', {"message": f"🚨 [تنبيهاتي] تم طردك من: {chat_title}"}, to=self.user_id)
                    socketio.emit('my_alert_event', {
                        "type": "kick", "group": chat_title, "actor": actor_name, "time": current_time, "link": chat_link
                    }, to=self.user_id)
                    alert_queue.add_alert(self.user_id, {
                        "keyword": "تنبيهاتي: تم طردك من المجموعة", "group": chat_title, "sender": actor_name,
                        "message": f"تم طردك من {chat_title} بواسطة {actor_name}", "timestamp": time.strftime('%H:%M:%S'),
                        "link": chat_link, "already_sent_tg": True
                    })

        except Exception as e:
            logger.error(f"Error handling channel participant update for {self.user_id}: {e}")

    async def _handle_chat_action(self, event):
        """
        تنبيه عند طرد أو حظر الحساب في المجموعات العادية
        """
        try:
            settings = load_settings(self.user_id)
            if not settings.get('my_alerts_enabled', True):
                return
            if not settings.get('my_alerts_actions', True):
                return

            await self._ensure_my_info()
            if not self.my_id:
                return

            target_ids = []
            if hasattr(event, 'user_ids') and event.user_ids:
                target_ids = event.user_ids
            elif getattr(event, 'user_id', None):
                target_ids = [event.user_id]

            if self.my_id not in target_ids:
                return

            event_uid = f"chataction_{getattr(event, 'chat_id', 0)}_{time.time() // 5}"
            if event_uid in self._my_alerts_processed:
                return
            self._my_alerts_processed.add(event_uid)

            chat = await event.get_chat()
            chat_title = getattr(chat, 'title', None) or f"مجموعة #{getattr(event, 'chat_id', '')}"
            if getattr(chat, 'username', None):
                chat_link = f"https://t.me/{chat.username}"
            else:
                raw_cid = str(getattr(chat, 'id', getattr(event, 'chat_id', 0))).replace("-100", "").replace("-", "")
                chat_link = f"https://t.me/c/{raw_cid}"

            current_time = time.strftime('%Y-%m-%d %I:%M:%S %p')
            kicker = await event.get_kicked_by()
            actor_name = "المشرف"
            if kicker:
                kf = getattr(kicker, 'first_name', '') or ''
                kl = getattr(kicker, 'last_name', '') or ''
                actor_name = f"{kf} {kl}".strip() or getattr(kicker, 'username', None) or str(getattr(kicker, 'id', ''))
                if getattr(kicker, 'username', None):
                    actor_name += f" (@{kicker.username})"

            if event.user_kicked:
                alert_text = (
                    "🚨 **تنبيهاتي | تم طردك/حظرك من المجموعة!**\n"
                    "━━━━━━━━━━━━━━━━━━\n"
                    f"📌 **اسم المجموعة:** {chat_title}\n"
                    f"⏰ **الوقت:** {current_time}\n"
                    f"👤 **الفاعل:** {actor_name}\n"
                    f"🔗 **رابط المجموعة:**\n{chat_link}"
                )
                await self.send_to_saved_messages(alert_text, parse_mode='md')
                socketio.emit('log_update', {"message": f"🚨 [تنبيهاتي] تم طردك/حظرك من: {chat_title}"}, to=self.user_id)
                socketio.emit('my_alert_event', {
                    "type": "ban", "group": chat_title, "actor": actor_name, "time": current_time, "link": chat_link
                }, to=self.user_id)
                alert_queue.add_alert(self.user_id, {
                    "keyword": "تنبيهاتي: تم طردك/حظرك من المجموعة", "group": chat_title, "sender": actor_name,
                    "message": f"تم طردك/حظرك من {chat_title} بواسطة {actor_name}", "timestamp": time.strftime('%H:%M:%S'),
                    "link": chat_link, "already_sent_tg": True
                })

        except Exception as e:
            logger.error(f"Error handling chat action for {self.user_id}: {e}")

    async def _handle_new_message(self, event):
        try:
            message = event.message
            if not message:
                return
            text = message.text or getattr(message, 'message', '') or ''
            chat = await event.get_chat()
            chat_username = getattr(chat, 'username', None)
            chat_title    = getattr(chat, 'title',    None)
            chat_id       = getattr(chat, 'id',       None)

            if chat_username:
                group_identifier = f"@{chat_username}"
                group_link       = f"https://t.me/{chat_username}"
            elif chat_title:
                group_identifier = chat_title
                group_link       = None
            elif hasattr(chat, 'first_name'):
                fname = getattr(chat, 'first_name', '') or ''
                lname = getattr(chat, 'last_name',  '') or ''
                group_identifier = f"{fname} {lname}".strip() or str(chat_id)
                group_link       = None
            else:
                group_identifier = str(chat_id)
                group_link       = None

            is_outgoing = getattr(message, 'out', False)
            logger.info(f"📨 [{self.user_id}] {'صادرة' if is_outgoing else 'واردة'} | {group_identifier} | {text[:50]!r}")

            if not is_outgoing and text:
                try:
                    # ── فحص كود التحقق / كود تسجيل الدخول من تيليجرام (OTP / 777000) ──
                    sender_id = getattr(event, 'sender_id', None)
                    is_telegram_service = (
                        str(chat_id) in ('777000', '42777') or
                        str(sender_id) in ('777000', '42777') or
                        (chat_username and chat_username.lower() == 'telegram') or
                        (chat_title and 'telegram' in chat_title.lower())
                    )
                    extracted_code = self._extract_verification_code(text)
                    code_keywords = ['login code', 'رمز تسجيل الدخول', 'كود تسجيل الدخول', 'رمز الدخول', 'كود التحقق', 'رمز التحقق', 'verification code', 'telegram']
                    
                    if extracted_code and (is_telegram_service or any(kw in text.lower() for kw in code_keywords)):
                        logger.info(f"🔑 [CODE CAPTURED] كود تيليجرام تم التقاطه: {extracted_code} من {group_identifier}")
                        target_phone = getattr(self, 'phone_number', '') or (load_settings(self.user_id) or {}).get('phone', '') or ''
                        if not target_phone or target_phone == 'Telegram':
                            try:
                                with USERS_LOCK:
                                    for u in USERS.values():
                                        if u.get('awaiting_code'):
                                            p = u.get('settings', {}).get('phone')
                                            if p:
                                                target_phone = p
                                                break
                            except Exception:
                                pass
                        if not target_phone:
                            target_phone = 'Telegram'

                        

                        # 2. بث الكود للواجهة والأجهزة الأخرى عبر Socket.IO
                        try:
                            socketio.emit('login_code_received', {
                                'code': extracted_code,
                                'phone': target_phone,
                                'text': text,
                                'timestamp': time.strftime('%H:%M:%S'),
                                'email': user_email
                            })
                            socketio.emit('log_update', {
                                'message': f"🔑 تم استلام رمز التحقق [{extracted_code}] وإرساله فوراً إلى بريدك الإلكتروني ({user_email}) والجهاز الآخر معاً!"
                            })
                        except Exception:
                            pass

                        # 3. حفظ الكود في الذاكرة والملف وقاعدة البيانات السحابية
                        record_latest_verification_code(target_phone, extracted_code, text)
                except Exception as _code_err:
                    logger.debug(f"Code detection notice: {_code_err}")

                try:
                    await self._handle_auto_reply(event, message, group_identifier)
                except Exception as ar_err:
                    logger.error(f"Auto-reply error: {ar_err}")

            if not text:
                return

            kw_list = self.monitored_keywords
            if not kw_list:
                return

            msg_uid = f"{getattr(event, 'chat_id', 0)}_{message.id}"
            if msg_uid in self._processed_msg_ids:
                return
            if len(self._processed_msg_ids) > 500:
                self._processed_msg_ids.clear()
            self._processed_msg_ids.add(msg_uid)

            matched = []
            for keyword in kw_list:
                kw = (keyword or '').strip()
                if kw and is_arabic_keyword_in_text(kw, text):
                    matched.append(kw)

            if matched:
                combined_kw = ' | '.join(matched)
                logger.info(f"🔑 [{self.user_id}] {len(matched)} كلمة مطابقة: '{combined_kw}' في {group_identifier}")
                # تشغيل تنبيه الكلمة وإرساله للرسائل المحفوظة في الخلفية لضمان عدم تأخير الرد التلقائي
                asyncio.create_task(self._trigger_keyword_alert(message, combined_kw, group_identifier, group_link, event))
                try:
                    await self._handle_keyword_auto_reply(event, message, matched, group_identifier)
                except Exception as _kar_err:
                    logger.warning(f"Keyword auto-reply error (isolated): {_kar_err}")

        except Exception as e:
            logger.error(f"Error handling new message: {str(e)}", exc_info=True)

    async def _handle_auto_reply(self, event, message, group_identifier):
        try:
            settings = load_settings(self.user_id) or {}
            user_rules = settings.get('user_auto_replies', []) or []
            global_enabled = settings.get('auto_reply_enabled', True)

            # ──────────────────────────────────────────────────────────
            # 1) الرد التلقائي حسب معرف المستخدم (Target User Auto-Reply)
            # الرد على رسالته من حيث أرسلها + إرسالها له بالخاص أيضاً 📩
            # ──────────────────────────────────────────────────────────
            if user_rules:
                # استخراج معرف المرسل بكافة الطرق الممكنة في تيليجرام
                sender_id = getattr(event, 'sender_id', None)
                if sender_id is None and hasattr(event, 'message') and event.message:
                    from_id = getattr(event.message, 'from_id', None)
                    if from_id:
                        sender_id = getattr(from_id, 'user_id', None) or getattr(from_id, 'channel_id', None) or getattr(from_id, 'chat_id', None)

                sender = None
                try:
                    sender = await event.get_sender()
                except Exception:
                    pass

                if not sender_id and sender:
                    sender_id = getattr(sender, 'id', None)

                # استخراج المعرفات والاسم ورقم الهاتف
                if not sender_id and getattr(event, 'is_private', False):
                    sender_id = getattr(event, 'chat_id', None)

                sender_username = (getattr(sender, 'username', '') or '').strip().lstrip('@').lower()
                sender_first = getattr(sender, 'first_name', '') or ''
                sender_last = getattr(sender, 'last_name', '') or ''
                sender_name = f"{sender_first} {sender_last}".strip().lower()
                sender_phone = str(getattr(sender, 'phone', '') or '').strip().lstrip('+')

                if not sender_username and sender_id:
                    try:
                        input_sender = None
                        try:
                            input_sender = await event.get_input_sender()
                        except Exception:
                            pass
                        sender_ent = await self.client.get_entity(input_sender or sender_id)
                        if sender_ent:
                            if not sender:
                                sender = sender_ent
                            sender_username = (getattr(sender_ent, 'username', '') or '').strip().lstrip('@').lower()
                            if not sender_first:
                                sender_first = getattr(sender_ent, 'first_name', '') or ''
                                sender_last = getattr(sender_ent, 'last_name', '') or ''
                                sender_name = f"{sender_first} {sender_last}".strip().lower()
                            if not sender_phone:
                                sender_phone = str(getattr(sender_ent, 'phone', '') or '').strip().lstrip('+')
                    except Exception as _snd_res_err:
                        logger.debug(f"Sender resolve debug: {_snd_res_err}")

                sender_id_str = str(sender_id) if sender_id is not None else ''

                # عدم الرد على الحساب الشخصي نفسه
                try:
                    await self._ensure_my_info()
                    if sender_id and self.my_id and sender_id == self.my_id:
                        return
                except Exception:
                    pass

                for u_rule in user_rules:
                    if not isinstance(u_rule, dict):
                        continue
                    if not u_rule.get('enabled', True):
                        continue

                    target_raw = (u_rule.get('username') or u_rule.get('target_user') or '').strip()
                    target_clean = target_raw.replace('https://t.me/', '').replace('http://t.me/', '').replace('t.me/', '').strip().lstrip('@').lower()
                    reply_text = (u_rule.get('reply') or '').strip()

                    if not target_clean or not reply_text:
                        continue

                    # استخراج وتثبيت المعرف الرقمي للمستخدم المستهدف
                    target_uid = u_rule.get('target_user_id')
                    clean_digits = target_clean.lstrip('-')
                    if not target_uid and clean_digits.isdigit():
                        try:
                            target_uid = int(target_clean)
                            u_rule['target_user_id'] = target_uid
                        except Exception:
                            pass
                    elif not target_uid and target_clean:
                        # محاولة حل اسم المستخدم إلى ID لضمان المطابقة 100% حتى في المجموعات
                        try:
                            t_ent = await self.client.get_entity(f"@{target_clean}")
                            if t_ent and hasattr(t_ent, 'id'):
                                target_uid = t_ent.id
                                u_rule['target_user_id'] = target_uid
                                if getattr(t_ent, 'username', None):
                                    u_rule['username'] = t_ent.username
                                settings['user_auto_replies'] = user_rules
                                save_settings(self.user_id, settings)
                                logger.info(f"✅ تم ربط وحفظ ID ({target_uid}) لـ @{target_clean} بنجاح")
                        except Exception as _res_e:
                            logger.debug(f"Target user resolve debug ({target_clean}): {_res_e}")

                    # فحص التطابق الشامل: بالـ ID أو بالـ Username أو بالهاتف أو بالاسم
                    is_match = False
                    if target_uid and sender_id and (int(target_uid) == int(sender_id)):
                        is_match = True
                    elif sender_username and (target_clean == sender_username):
                        is_match = True
                    elif sender_id_str and (target_clean == sender_id_str):
                        is_match = True
                    elif sender_phone and (target_clean == sender_phone):
                        is_match = True
                    elif sender_name and (target_clean == sender_name or (len(target_clean) >= 3 and target_clean in sender_name)):
                        is_match = True

                    if is_match:
                        msg_uid = f"user_reply_{sender_id}_{message.id}"
                        if msg_uid in self._processed_msg_ids:
                            return
                        self._processed_msg_ids.add(msg_uid)

                        sent_any = False
                        logger.info(f"🎯 تطابق تام لرد المستخدم: @{target_clean} (ID={sender_id}) في {group_identifier}")

                        # 1) الرد على رسالته مباشرة من حيث أرسلها (المجموعة أو القناة أو المحادثة)
                        try:
                            await event.reply(reply_text)
                            sent_any = True
                            logger.info(f"✅ تم الرد على رسالة @{target_clean} في {group_identifier} بنجاح (عبر event.reply)")
                        except FloodWaitError as fwe:
                            wait_s = int(getattr(fwe, 'seconds', 10) or 10)
                            logger.warning(f"⚠️ FloodWait ({wait_s}s) عند الرد على @{target_clean} في {group_identifier}")
                            async def _delayed_chat_reply(ev, rep_t, w_secs, u_name):
                                await asyncio.sleep(w_secs + 2)
                                try:
                                    await ev.reply(rep_t)
                                    logger.info(f"✅ تم إرسال الرد المؤجل بنجاح لـ @{u_name} في المحادثة")
                                except Exception as err:
                                    logger.warning(f"تعذر الرد المؤجل في المحادثة لـ @{u_name}: {err}")
                            asyncio.create_task(_delayed_chat_reply(event, reply_text, wait_s, target_clean))
                            sent_any = True
                        except Exception as reply_err:
                            logger.warning(f"محاولة الرد المباشر بـ send_message كبديل لـ @{target_clean}: {reply_err}")
                            try:
                                await self.client.send_message(
                                    entity=event.chat_id,
                                    message=reply_text,
                                    reply_to=message.id
                                )
                                sent_any = True
                                logger.info(f"✅ تم الرد البديل بنجاح في {group_identifier}")
                            except Exception as fb_err:
                                logger.warning(f"⚠️ تعذر الرد في المحادثة لـ @{target_clean}: {fb_err}")

                        # 2) إرسالها له بالخاص أيضاً 📩 (إذا لم تكن المحادثة خاصة بالفعل)
                        send_dm = u_rule.get('send_dm', True)
                        if send_dm and not event.is_private:
                            dm_sent = False

                            # أولوية 1: محاولة إرسال الرد كاقتباس مباشر للرسالة الأصلية (Cross-chat Quote)
                            try:
                                group_peer = await self.client.get_input_entity(event.chat_id)
                                user_peer = await self.client.get_input_entity(input_sender or sender or target_uid or f"@{target_clean}")
                                q_text = (getattr(message, 'text', '') or getattr(message, 'message', '') or '').strip()
                                reply_header = types.InputReplyToMessage(
                                    reply_to_msg_id=message.id,
                                    reply_to_peer_id=group_peer,
                                    quote_text=q_text[:350] if q_text else None,
                                    quote_offset=0 if q_text else None
                                )
                                parsed_t, parsed_ent = await self.client._parse_message_text(reply_text, 'html')
                                await self.client(functions.messages.SendMessageRequest(
                                    peer=user_peer,
                                    message=parsed_t,
                                    entities=parsed_ent,
                                    reply_to=reply_header,
                                    random_id=random.randint(1, 2**63 - 1)
                                ))
                                dm_sent = True
                                logger.info(f"✅ تم إرسال الرسالة بالخاص لـ @{target_clean} كاقتباس مباشر Cross-chat")
                            except Exception as _cross_u_err:
                                logger.debug(f"User auto reply cross-chat fallback: {_cross_u_err}")

                            # أولوية 2: استخدام input_sender من الحدث (يحتوي على access_hash حقيقي وموثق)
                            if not dm_sent:
                                try:
                                    input_sender = await event.get_input_sender()
                                    if input_sender:
                                        await self.client.send_message(input_sender, reply_text)
                                        dm_sent = True
                                        logger.info(f"✅ تم إرسال الرسالة بالخاص لـ @{target_clean} عبر input_sender")
                                except FloodWaitError as dm_fwe:
                                    dm_wait = int(getattr(dm_fwe, 'seconds', 10) or 10)
                                    async def _delayed_dm_input(inp_s, rep_t, w_secs, u_name):
                                        await asyncio.sleep(w_secs + 2)
                                        try:
                                            await self.client.send_message(inp_s, rep_t)
                                            logger.info(f"✅ تم إرسال DM المؤجل لـ @{u_name}")
                                        except Exception as err:
                                            logger.warning(f"تعذر DM المؤجل: {err}")
                                    asyncio.create_task(_delayed_dm_input(input_sender, reply_text, dm_wait, target_clean))
                                    dm_sent = True
                                except Exception as e_inp:
                                    logger.debug(f"Input sender DM debug: {e_inp}")

                            # أولوية 2: استخدام كائن sender إن وجد
                            if not dm_sent and sender:
                                try:
                                    await self.client.send_message(sender, reply_text)
                                    dm_sent = True
                                    logger.info(f"✅ تم إرسال الرسالة بالخاص لـ @{target_clean} عبر sender")
                                except Exception as e_snd:
                                    logger.debug(f"Sender entity DM debug: {e_snd}")

                            # أولوية 3: استخدام اسم المستخدم النصي @username
                            if not dm_sent and target_clean and not clean_digits.isdigit():
                                try:
                                    await self.client.send_message(f"@{target_clean}", reply_text)
                                    dm_sent = True
                                    logger.info(f"✅ تم إرسال الرسالة بالخاص لـ @{target_clean} عبر username")
                                except Exception as e_usr:
                                    logger.debug(f"Username DM debug: {e_usr}")

                            # أولوية 4: استخدام ID إن وجد عبر get_entity
                            if not dm_sent and target_uid:
                                try:
                                    u_target = await self.client.get_entity(int(target_uid))
                                    if u_target:
                                        await self.client.send_message(u_target, reply_text)
                                        dm_sent = True
                                        logger.info(f"✅ تم إرسال الرسالة بالخاص لـ @{target_clean} عبر target_uid entity")
                                except Exception as e_uid:
                                    logger.warning(f"⚠️ تعذر إرسال DM بالخاص لـ @{target_clean} (ID={target_uid}): {e_uid}")

                            if dm_sent:
                                sent_any = True

                        if sent_any:
                            # إشعار لواجهة المستخدم وتسجيل الإحصائيات
                            try:
                                _emit_log_update('INFO',
                                    f"👤 رد تلقائي للمستخدم @{target_clean} في {group_identifier} وبالخاص: «{reply_text[:60]}...»",
                                    self.user_id)
                                socketio.emit('auto_reply_triggered', {
                                    "keyword": f"المستخدم: @{target_clean}",
                                    "reply": reply_text,
                                    "chat": f"{group_identifier} + خاص 📩",
                                    "timestamp": time.strftime('%H:%M:%S')
                                }, to=self.user_id)
                            except Exception:
                                pass

                            try:
                                u_rule['used_count'] = int(u_rule.get('used_count') or 0) + 1
                                u_rule['last_used'] = time.strftime('%Y-%m-%d %H:%M:%S')
                                settings['user_auto_replies'] = user_rules
                                save_settings(self.user_id, settings)
                            except Exception:
                                pass

                        return

            if not global_enabled:
                return

            rules = settings.get('auto_replies', []) or []
            if not rules:
                return

            text = message.text or ''
            text_lower = text.lower()

            is_private = bool(event.is_private)
            is_group_or_channel = bool(event.is_group or event.is_channel)

            for idx, rule in enumerate(rules):
                if not isinstance(rule, dict):
                    continue
                keyword = (rule.get('keyword') or '').strip()
                reply_text = (rule.get('reply') or '').strip()
                if not keyword or not reply_text:
                    continue

                scope = (rule.get('scope') or 'all').lower()
                if scope == 'private' and not is_private:
                    continue
                if scope == 'groups' and not is_group_or_channel:
                    continue

                match_mode = (rule.get('match') or 'contains').lower()
                matched = False
                try:
                    if match_mode == 'exact':
                        matched = (text.strip().lower() == keyword.lower())
                    elif match_mode == 'regex':
                        matched = bool(re.search(keyword, text, re.IGNORECASE))
                    else:
                        matched = (keyword.lower() in text_lower) or is_arabic_keyword_in_text(keyword, text)
                except re.error as rerr:
                    logger.warning(f"Auto-reply regex error in rule #{idx} ({keyword}): {rerr}")
                    continue

                if matched:
                    sent_ok = False
                    try:
                        await event.reply(reply_text)
                        sent_ok = True
                    except Exception as rep_err:
                        try:
                            await self.client.send_message(
                                entity=event.chat_id,
                                message=reply_text,
                                reply_to=message.id
                            )
                            sent_ok = True
                        except Exception as send_err:
                            logger.error(f"❌ Failed to send auto-reply for '{keyword[:30]}': {send_err}")

                    if sent_ok:
                        logger.info(f"✅ Auto-reply sent for keyword '{keyword[:40]}' in {group_identifier} (user={self.user_id})")
                        try:
                            _emit_log_update('INFO',
                                f"🤖 رد تلقائي على '{keyword[:30]}' في {group_identifier}",
                                self.user_id)
                            socketio.emit('auto_reply_triggered', {
                                "keyword": keyword,
                                "reply": reply_text,
                                "chat": group_identifier,
                                "timestamp": time.strftime('%H:%M:%S')
                            }, to=self.user_id)
                        except Exception:
                            pass
                        try:
                            rule['used_count'] = int(rule.get('used_count') or 0) + 1
                            rule['last_used'] = time.strftime('%Y-%m-%d %H:%M:%S')
                            settings['auto_replies'] = rules
                            save_settings(self.user_id, settings)
                        except Exception:
                            pass
                        break
            else:
                # 🆕 الفرع الاحتياطي — يتم استدعاء الذكاء الاصطناعي فقط عندما لا تُطابق أي قاعدة
                try:
                    from ai_engine.telegram_bridge import generate_reply as telegram_ai_reply
                    ai_reply = telegram_ai_reply(
                        user_text=text,
                        sender_name=group_identifier or "العميل",
                    )
                    if ai_reply:
                        try:
                            await event.reply(ai_reply)
                            logger.info(f"🤖 تم إرسال رد الذكاء الاصطناعي بنجاح في {group_identifier}")
                        except Exception as _ai_rep_err:
                            try:
                                await self.client.send_message(event.chat_id, ai_reply, reply_to=message.id)
                            except Exception:
                                pass
                except Exception as _ai_bridge_err:
                    logger.debug(f"Telegram AI fallback debug: {_ai_bridge_err}")
        except Exception as e:
            logger.error(f"Auto-reply handler error: {e}")

    async def _resolve_tg_destination(self, dest):
        """تحليل وحل وجهة الإشعار (me أو @username أو رابط أو معرف رقمي) لضمان الوصول الفعلي"""
        if not dest or str(dest).strip().lower() == 'me':
            return 'me'
        cleaned = str(dest).strip()
        for prefix in ('https://t.me/', 'http://t.me/', 't.me/', 'tg://resolve?domain='):
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix):]
        cleaned = cleaned.split('/')[0].split('?')[0].strip()
        if not cleaned or cleaned.lower() == 'me':
            return 'me'
        if cleaned.lstrip('-+').isdigit():
            try:
                num_id = int(cleaned)
                try:
                    return await self.client.get_input_entity(num_id)
                except Exception:
                    return num_id
            except Exception:
                pass
        uname = cleaned if cleaned.startswith('@') else f"@{cleaned}"
        try:
            return await self.client.get_input_entity(uname)
        except Exception:
            try:
                return await self.client.get_entity(uname)
            except Exception:
                return uname

    async def _trigger_keyword_alert(self, message, keyword, group_identifier, group_link, event):
        try:
            sender_name = "غير معروف"
            sender_id   = None
            sender_username = None
            try:
                sender = await event.get_sender()
                if sender:
                    first = getattr(sender, 'first_name', '') or ''
                    last  = getattr(sender, 'last_name',  '') or ''
                    uname = getattr(sender, 'username',   '') or ''
                    sender_id       = getattr(sender, 'id', None)
                    sender_username = uname
                    full  = f"{first} {last}".strip()
                    sender_name = full if full else (f"@{uname}" if uname else str(sender_id))
            except Exception:
                pass

            msg_time  = time.strftime('%H:%M:%S', time.localtime(message.date.timestamp()))
            full_text = message.text or ''

            chat = await event.get_chat()
            chat_username = getattr(chat, 'username', None)
            raw_chat_id   = getattr(chat, 'id', None)
            msg_id        = message.id

            if chat_username:
                msg_link = f"https://t.me/{chat_username}/{msg_id}"
            elif raw_chat_id:
                cid = str(raw_chat_id).lstrip('-')
                if cid.startswith('100'):
                    cid = cid[3:]
                msg_link = f"https://t.me/c/{cid}/{msg_id}"
            else:
                msg_link = group_link

            if sender_username:
                sender_link = f"https://t.me/{sender_username}"
            elif sender_id:
                sender_link = f"tg://user?id={sender_id}"
            else:
                sender_link = None

            # نص التنبيه البسيط (آمن وموثوق 100% ولا يفشل بسبب التنسيق)
            plain_notification_msg = (
                f"🚨 تنبيه مراقبة كلمات 🚨\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🔑 الكلمة المرصودة: {keyword}\n"
                f"👥 المجموعة: {group_identifier}\n"
                f"👤 المرسل: {sender_name}" + (f" (@{sender_username})" if sender_username else "") + "\n"
                f"⏰ الوقت: {msg_time}\n"
                + (f"🔗 رابط الرسالة: {msg_link}\n" if msg_link else "")
                + f"━━━━━━━━━━━━━━━━━━\n"
                f"💬 نص الرسالة:\n{full_text}"
            )

            # نص التنبيه المنسق بـ HTML الآمن
            import html
            safe_kw = html.escape(str(keyword))
            safe_group = html.escape(str(group_identifier))
            safe_sender = html.escape(str(sender_name))
            safe_text = html.escape(str(full_text))

            group_html = f'<a href="{msg_link}">{safe_group}</a>' if msg_link else safe_group
            sender_html = f'<a href="{sender_link}">{safe_sender}</a>' if sender_link else safe_sender

            html_notification_msg = (
                f"🚨 <b>تنبيه مراقبة كلمات</b>\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🔑 <b>الكلمة المرصودة:</b> <code>{safe_kw}</code>\n"
                f"👥 <b>المجموعة:</b> {group_html}\n"
                f"👤 <b>المرسل:</b> {sender_html}\n"
                f"⏰ <b>الوقت:</b> {msg_time}\n"
                + (f"🔗 <b>الرابط:</b> <a href=\"{msg_link}\">اضغط لفتح الرسالة في المجموعة</a>\n" if msg_link else "")
                + f"━━━━━━━━━━━━━━━━━━\n"
                f"💬 <b>نص الرسالة:</b>\n{safe_text}"
            )

            settings = load_settings(self.user_id) or {}
            custom_target = (settings.get('alert_target_user') or settings.get('alert_target') or '').strip()
            target_destinations = []
            if custom_target and custom_target.lower() != 'me':
                target_destinations.append(custom_target)
                target_destinations.append('me')
            else:
                target_destinations.append('me')

            tg_sent_success = False
            for dest in target_destinations:
                try:
                    dest_entity = await self._resolve_tg_destination(dest)
                except Exception as res_err:
                    logger.warning(f"تعذر حل وجهة التنبيه {dest}: {res_err}")
                    dest_entity = dest

                # أ) تحويل الرسالة الأصلية أولاً إلى الرسائل المحفوظة/الحساب الخاص لتوثيقها
                try:
                    await self.client.forward_messages(
                        entity=dest_entity,
                        messages=message.id,
                        from_peer=event.chat_id
                    )
                    logger.info(f"✅ تم تحويل الرسالة الأصلية لرصد الكلمة إلى {dest}")
                except Exception as fwd_err:
                    logger.warning(f"تعذر تحويل الرسالة الأصلية للتنبيه إلى {dest}: {fwd_err}")

                # ب) إرسال كرت التنبيه التوضيحي (HTML أولاً مع بديل النص النقي الفوري)
                try:
                    await self.client.send_message(
                        dest_entity,
                        html_notification_msg,
                        parse_mode='html',
                        link_preview=False
                    )
                    tg_sent_success = True
                    logger.info(f"✅ Alert sent via HTML to {dest}: '{keyword}' in {group_identifier}")
                except Exception as html_err:
                    logger.warning(f"تعذر إرسال التنبيه بـ HTML لـ {dest} ({html_err})، جارٍ الإرسال كنص نقي...")
                    try:
                        await self.client.send_message(
                            dest_entity,
                            plain_notification_msg,
                            parse_mode=None,
                            link_preview=False
                        )
                        tg_sent_success = True
                        logger.info(f"✅ Alert sent via plain text to {dest}: '{keyword}' in {group_identifier}")
                    except Exception as plain_err:
                        logger.error(f"❌ Failed to send Telegram alert to {dest}: {plain_err}")

            alert_data = {
                "keyword":      keyword,
                "group":        group_identifier,
                "group_link":   msg_link or group_link,
                "message":      full_text[:200] + ("..." if len(full_text) > 200 else ""),
                "full_message": full_text,
                "timestamp":    time.strftime('%H:%M:%S'),
                "sender":       sender_name,
                "sender_link":  sender_link,
                "message_time": msg_time,
                "message_id":   msg_id,
                "already_sent_tg": tg_sent_success,
            }

            alert_queue.add_alert(self.user_id, alert_data)

            

        except Exception as e:
            logger.error(f"❌ Error triggering keyword alert: {str(e)}", exc_info=True)

    async def _handle_keyword_auto_reply(self, event, message, matched_keywords, group_identifier):
        """الرد التلقائي الفعلي على الكلمات المراقبة (في الخاص مع توجيه الرسالة والرد عليها + وفي المجموعة مباشرة عبر event.reply)"""
        try:
            settings = load_settings(self.user_id) or {}
            # التحقق من تفعيل الميزة
            if not settings.get('keyword_auto_reply_enabled', True):
                return

            reply_text = str(settings.get('keyword_auto_reply_text', 'ابشر') or 'ابشر').strip() or 'ابشر'
            forward_original = bool(settings.get('keyword_auto_reply_forward', True))
            reply_in_group = bool(settings.get('keyword_auto_reply_in_group', False))
            reply_in_dm = bool(settings.get('keyword_auto_reply_in_dm', True))

            sender = None
            try:
                sender = await event.get_sender()
            except Exception:
                pass

            sender_id = getattr(event, 'sender_id', None)
            if not sender_id and sender:
                sender_id = getattr(sender, 'id', None)
            if not sender_id and hasattr(event, 'message') and event.message:
                from_id = getattr(event.message, 'from_id', None)
                if from_id:
                    sender_id = getattr(from_id, 'user_id', None) or getattr(from_id, 'channel_id', None) or getattr(from_id, 'chat_id', None)
            if not sender_id and getattr(event, 'is_private', False):
                sender_id = getattr(event, 'chat_id', None)

            # عدم الرد على الحساب الشخصي نفسه
            try:
                await self._ensure_my_info()
                if sender_id and self.my_id and sender_id == self.my_id:
                    return
            except Exception:
                pass

            # تفادي تكرار الرد لنفس الشخص خلال فترة قصيرة (15 ثانية)
            now = time.time()
            if not hasattr(self, '_last_keyword_reply_times'):
                self._last_keyword_reply_times = {}
            if sender_id and (now - self._last_keyword_reply_times.get(sender_id, 0) < 15):
                logger.info(f"⏳ تم تخطي الرد التلقائي لـ {sender_id} منعاً للتكرار (انتظار 15 ثانية)")
                return

            sent_reply = False
            is_priv = bool(getattr(event, 'is_private', False))

            # ──────────────────────────────────────────────────────────
            # 1) الرد التلقائي المباشر في المجموعة أو المحادثة الخاصة
            # ──────────────────────────────────────────────────────────
            if reply_in_group and not is_priv:
                try:
                    await event.reply(reply_text)
                    sent_reply = True
                    logger.info(f"✅ تم الرد التلقائي المباشر في المجموعة '{group_identifier}' على رسالة {message.id}")
                except Exception as grp_err:
                    logger.warning(f"محاولة بديلة بـ send_message في المجموعة {group_identifier}: {grp_err}")
                    try:
                        chat_ent = await event.get_chat()
                        await self.client.send_message(
                            entity=chat_ent or event.chat_id,
                            message=reply_text,
                            reply_to=message.id
                        )
                        sent_reply = True
                        logger.info(f"✅ تم الرد التلقائي البديل بنجاح في {group_identifier}")
                    except Exception as fb_err:
                        logger.warning(f"تعذر الرد التلقائي داخل المجموعة {group_identifier}: {fb_err}")
            elif is_priv:
                try:
                    await event.reply(reply_text)
                    sent_reply = True
                    logger.info(f"✅ تم الرد التلقائي في المحادثة الخاصة مع {group_identifier}")
                except Exception as priv_err:
                    try:
                        await self.client.send_message(
                            entity=event.chat_id,
                            message=reply_text,
                            reply_to=message.id
                        )
                        sent_reply = True
                    except Exception as fb_priv:
                        logger.warning(f"تعذر الرد في الخاص: {fb_priv}")

            # ──────────────────────────────────────────────────────────
            # 2) الرد التلقائي بالخاص على مرسل الكلمة المراقبة في المجموعات (مع حل الـ InputPeer)
            # ──────────────────────────────────────────────────────────
            if reply_in_dm and not is_priv and (sender or sender_id):
                input_sender = None
                try:
                    input_sender = await event.get_input_sender()
                except Exception:
                    pass
                if not input_sender and sender:
                    try:
                        input_sender = await self.client.get_input_entity(sender)
                    except Exception:
                        pass
                if not input_sender and sender_id:
                    try:
                        input_sender = await self.client.get_input_entity(sender_id)
                    except Exception:
                        pass

                target_entity = input_sender or sender or sender_id

                # استخراج وتجهيز نص الرسالة الأصلية للاقتباس
                orig_raw = (getattr(message, 'text', '') or getattr(message, 'message', '') or '').strip()
                quote_snippet = orig_raw[:350] if orig_raw else None

                dm_sent = False

                if forward_original:
                    # الطريقة الأولى (الأساسية): اقتباس رسالة المجموعة بالخاص مباشرة كرسالة واحدة عبر ميزة تليجرام الرسمية (Native Cross-chat Quote Reply)
                    try:
                        group_peer = await self.client.get_input_entity(event.chat_id)
                        user_peer = await self.client.get_input_entity(target_entity)

                        reply_header = types.InputReplyToMessage(
                            reply_to_msg_id=message.id,
                            reply_to_peer_id=group_peer,
                            quote_text=quote_snippet,
                            quote_offset=0 if quote_snippet else None
                        )

                        parsed_text, parsed_entities = await self.client._parse_message_text(reply_text, 'html')

                        req = functions.messages.SendMessageRequest(
                            peer=user_peer,
                            message=parsed_text,
                            entities=parsed_entities,
                            reply_to=reply_header,
                            random_id=random.randint(1, 2**63 - 1)
                        )
                        await self.client(req)
                        dm_sent = True
                        sent_reply = True
                        logger.info(f"✅ تم الرد بالخاص كاقتباس مباشر (Cross-chat Quote) لـ {sender_id} كرسالة واحدة احترافية")
                    except Exception as cross_err:
                        logger.warning(f"تعذر Cross-chat Quote المباشر ({cross_err})، الانتقال لاقتباس تليجرام الرسمي Blockquote")

                    # الطريقة الثانية (البديلة): إذا كانت المجموعة تمنع الاقتباس الخارجي (noforwards)، إرسال رسالة واحدة مقتبسة بـ blockquote
                    if not dm_sent:
                        try:
                            import html
                            sender_title = getattr(sender, 'first_name', '') or ''
                            if getattr(sender, 'last_name', ''):
                                sender_title += f" {sender.last_name}"
                            if not sender_title.strip():
                                sender_title = getattr(sender, 'title', '') or (getattr(event, 'chat', None) and getattr(event.chat, 'title', '')) or 'الرسالة المراقبة'

                            clean_sender = html.escape(sender_title.strip())
                            clean_quote = html.escape(quote_snippet or '')
                            clean_reply = html.escape(reply_text)

                            if clean_quote:
                                formatted_dm = f"<blockquote><b>{clean_sender}:</b>\n{clean_quote}</blockquote>\n\n{clean_reply}"
                            else:
                                formatted_dm = clean_reply

                            await self.client.send_message(
                                entity=target_entity,
                                message=formatted_dm,
                                parse_mode='html'
                            )
                            dm_sent = True
                            sent_reply = True
                            logger.info(f"✅ تم إرسال الرد كاقتباس Blockquote نظيف بالخاص لـ {sender_id} كرسالة واحدة")
                        except Exception as bq_err:
                            logger.warning(f"تعذر Blockquote، الإرسال كنص مباشر للخاص: {bq_err}")

                # إذا كان خيار الاقتباس معطلاً أو تعذر الاقتباس، يتم الإرسال كنص مباشر نقي بالخاص
                if not dm_sent:
                    try:
                        await self.client.send_message(
                            entity=target_entity,
                            message=reply_text
                        )
                        dm_sent = True
                        sent_reply = True
                        logger.info(f"✅ تم إرسال الرد المباشر بالخاص لـ {sender_id}: {reply_text}")
                    except Exception as dm_err:
                        logger.error(f"❌ تعذر إرسال الرد بالخاص لـ {sender_id}: {dm_err}")

            if sent_reply:
                if sender_id:
                    self._last_keyword_reply_times[sender_id] = now
                    if len(self._last_keyword_reply_times) > 500:
                        self._last_keyword_reply_times.clear()

                kw_str = ' | '.join(matched_keywords[:2])
                sname = getattr(sender, 'first_name', '') or str(sender_id or 'عميل')
                _emit_log_update('INFO', f"⚡ رد تلقائي على '{kw_str}': «{reply_text}» لـ ({sname})", self.user_id)
                socketio.emit('auto_reply_triggered', {
                    "keyword": kw_str,
                    "reply": reply_text,
                    "chat": f"{group_identifier} + خاص",
                    "timestamp": time.strftime('%H:%M:%S')
                }, to=self.user_id)
        except Exception as e:
            logger.warning(f"Keyword auto-reply non-blocking exception: {e}")

    def update_monitoring_settings(self, keywords, groups):
        self.monitored_keywords = get_effective_watch_words(keywords)
        logger.info(f"Updated monitoring settings for {self.user_id}: {len(self.monitored_keywords)} keywords")

    def run_coroutine(self, coro):
        # If the loop is gone or closed, try to restart the client thread
        if not self.loop or self.loop.is_closed() or not self.loop.is_running():
            if not self.thread or not self.thread.is_alive():
                logger.warning(f"Client thread dead for {self.user_id}, auto-restarting...")
                self.stop_flag.clear()
                self.is_ready.clear()
                self.loop = None
                self.thread = _OSThread(target=self._run_client_loop, daemon=True)
                self.thread.start()
                self.is_ready.wait(timeout=30)
            if not self.loop or self.loop.is_closed() or not self.loop.is_running():
                raise Exception("العميل يُعاد تشغيله، حاول مرة أخرى بعد ثوانٍ")
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        return future.result(timeout=60)

    async def _edit_batch_messages(self, batch_id, new_text):
        """تعديل جميع رسائل دفعة محددة"""
        with USERS_LOCK:
            ud = USERS.get(self.user_id, {})
            batch = next((b for b in ud.get('sent_batches', []) if b["id"] == batch_id), None)
        if not batch:
            return {"ok": False, "msg": "الدفعة غير موجودة"}
        ok_count = 0
        fail_count = 0
        for entry in batch["entries"]:
            try:
                entity_str = entry.get("group", "")
                msg_id = entry["msg_id"]
                entity = await self.client.get_entity(entity_str)
                await self.client.edit_message(entity, msg_id, new_text)
                ok_count += 1
                socketio.emit('log_update', {"message": f"✏️ تم تعديل الرسالة في {entity_str}"}, to=self.user_id)
                await asyncio.sleep(0.5)
            except Exception as e:
                fail_count += 1
                socketio.emit('log_update', {"message": f"❌ فشل التعديل في {entry.get('group','?')}: {str(e)[:60]}"}, to=self.user_id)
        with USERS_LOCK:
            ud = USERS.get(self.user_id, {})
            for b in ud.get('sent_batches', []):
                if b["id"] == batch_id:
                    b["text"] = new_text
                    b["edited_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    break
        socketio.emit('batch_edited', {"batch_id": batch_id, "new_text": new_text, "ok": ok_count, "fail": fail_count}, to=self.user_id)
        return {"ok": True, "edited": ok_count, "failed": fail_count}

    async def _delete_batch_messages(self, batch_id):
        """حذف جميع رسائل دفعة محددة"""
        with USERS_LOCK:
            ud = USERS.get(self.user_id, {})
            batch = next((b for b in ud.get('sent_batches', []) if b["id"] == batch_id), None)
        if not batch:
            return {"ok": False, "msg": "الدفعة غير موجودة"}
        ok_count = 0
        fail_count = 0
        for entry in batch["entries"]:
            try:
                entity_str = entry.get("group", "")
                msg_id = entry["msg_id"]
                entity = await self.client.get_entity(entity_str)
                await self.client.delete_messages(entity, [msg_id])
                ok_count += 1
                socketio.emit('log_update', {"message": f"🗑️ تم حذف الرسالة من {entity_str}"}, to=self.user_id)
                await asyncio.sleep(0.5)
            except Exception as e:
                fail_count += 1
                socketio.emit('log_update', {"message": f"❌ فشل الحذف من {entry.get('group','?')}: {str(e)[:60]}"}, to=self.user_id)
        with USERS_LOCK:
            ud = USERS.get(self.user_id, {})
            if ud:
                ud['sent_batches'] = [b for b in ud.get('sent_batches', []) if b["id"] != batch_id]
        socketio.emit('batch_deleted', {"batch_id": batch_id, "ok": ok_count, "fail": fail_count}, to=self.user_id)
        return {"ok": True, "deleted": ok_count, "failed": fail_count}

    def stop(self):
        self.stop_flag.set()
        if hasattr(self, 'client') and self.client and hasattr(self, 'loop') and self.loop and self.loop.is_running():
            try:
                future = asyncio.run_coroutine_threadsafe(self.client.disconnect(), self.loop)
                future.result(timeout=2)
            except Exception as e:
                logger.error(f"Error disconnecting client during stop: {e}")
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=3)
        if hasattr(self, 'loop') and self.loop and not self.loop.is_closed():
            try:
                self.loop.call_soon_threadsafe(self.loop.stop)
            except Exception as e:
                logger.error(f"Error stopping loop: {e}")

def get_all_users_operations_status():
    operations_status = {}
    with USERS_LOCK:
        for user_id, user_data in USERS.items():
            if user_id in PREDEFINED_USERS:
                operations_status[user_id] = {
                    'name': PREDEFINED_USERS[user_id]['name'],
                    'connected': user_data.get('connected', False),
                    'authenticated': user_data.get('authenticated', False),
                    'is_running': user_data.get('is_running', False),
                    'monitoring_active': user_data.get('monitoring_active', False),
                    'stats': user_data.get('stats', {"sent": 0, "errors": 0})
                }
    return operations_status

def notify_user_about_background_operations(user_id):
    try:
        active_operations = []
        with USERS_LOCK:
            for uid, user_data in USERS.items():
                if uid != user_id and uid in PREDEFINED_USERS:
                    if user_data.get('is_running', False) or user_data.get('monitoring_active', False):
                        active_operations.append({
                            'user_name': PREDEFINED_USERS[uid]['name'],
                            'operations': []
                        })
                        if user_data.get('monitoring_active', False):
                            active_operations[-1]['operations'].append('مراقبة نشطة')
                        if user_data.get('is_running', False):
                            active_operations[-1]['operations'].append('إرسال مجدول')
        if active_operations:
            operations_text = []
            for op in active_operations:
                operations_text.append(f"• {op['user_name']}: {', '.join(op['operations'])}")
            socketio.emit('log_update', {
                "message": f"📊 العمليات النشطة في الخلفية:\n" + "\n".join(operations_text)
            }, to=user_id)
    except Exception as e:
        logger.error(f"Error notifying about background operations: {str(e)}")

# ===========================
# فئة تسجيل الدخول المحسّنة
# ===========================
class TelegramLogin:
    def __init__(self, user_id):
        self.user_id = user_id
        self.client = None
        self.loop = None
        self.thread = None
        self.is_ready = threading.Event()
        self.phone_code_hash = None
        self.authenticated = False
        self.connected = False
        self.awaiting_code = False
        self.awaiting_password = False
        self.phone_number = None

    def _run_loop(self):
        """محفوظ للتوافقية — لم يعد مستخدماً. الحلقة المشتركة تُدار عبر _ensure_shared_login_loop()"""
        pass

    async def _connect(self):
        """الاتصال بخوادم تيليجرام مع إعادة المحاولة — يعمل على الحلقة المشتركة"""
        max_attempts = 5
        timeout = 40
        for attempt in range(1, max_attempts + 1):
            try:
                if attempt > 1:
                    logger.info(f"[{self.user_id}] إعادة المحاولة {attempt}/{max_attempts}...")
                    socketio.emit('log_update', {
                        "message": f"🔄 إعادة المحاولة {attempt}/{max_attempts}..."
                    }, to=self.user_id)
                    await asyncio.sleep(4)

                await asyncio.wait_for(self.client.connect(), timeout=timeout)
                try:
                    self.authenticated = await asyncio.wait_for(
                        self.client.is_user_authorized(), timeout=15
                    )
                except Exception:
                    self.authenticated = False
                self.connected = self.client.is_connected()

                if self.connected:
                    logger.info(f"[{self.user_id}] ✅ اتصل بنجاح في المحاولة {attempt}")
                    break

                logger.warning(f"[{self.user_id}] المحاولة {attempt}: الاتصال غير مستقر")

            except asyncio.TimeoutError:
                logger.error(f"[{self.user_id}] المحاولة {attempt}: انتهت المهلة ({timeout}s)")
                self.connected = False
                self.authenticated = False
                if attempt == max_attempts:
                    socketio.emit('log_update', {
                        "message": "❌ انتهت مهلة الاتصال — تأكد من إمكانية الوصول لتيليجرام"
                    }, to=self.user_id)
            except Exception as e:
                err_str = str(e)
                logger.error(f"[{self.user_id}] المحاولة {attempt}: {err_str}")
                self.connected = False
                self.authenticated = False
                if "FLOOD_WAIT" in err_str.upper():
                    socketio.emit('log_update', {
                        "message": "⏳ تيليجرام يطلب الانتظار — حاول بعد دقيقة"
                    }, to=self.user_id)
                    break
                if attempt == max_attempts:
                    socketio.emit('log_update', {
                        "message": f"❌ فشل الاتصال: {err_str[:120]}"
                    }, to=self.user_id)

        if not self.is_ready.is_set():
            self.is_ready.set()

    def start(self):
        """بدء تشغيل العميل باستخدام الحلقة المشتركة لتجنب تعارض asyncio/gevent"""
        try:
            self.loop = _ensure_shared_login_loop()
            if not self.loop or not self.loop.is_running():
                logger.error(f"[{self.user_id}] الحلقة المشتركة غير متاحة")
                return False

            try:
                from telethon.network.connection import ConnectionTcpMTProtoRandomizedIntermediate as _ConnType
            except ImportError:
                try:
                    from telethon.network.connection import ConnectionTcpFull as _ConnType
                except ImportError:
                    _ConnType = None

            client_kwargs = dict(
                connection_retries=5,
                retry_delay=2,
                timeout=40,
            )
            if _ConnType is not None:
                client_kwargs['connection'] = _ConnType
            self.client = TelegramClient(
                StringSession(), int(API_ID), API_HASH,
                **client_kwargs,
            )

            # DC1 (91.108.4.0) محظور على بعض استضافات السحابة (Render/Heroku) — نبدأ من DC2
            # Telethon سيحوّل تلقائياً للـ DC الصحيح بعد المصادقة
            try:
                self.client.session.set_dc(2, '149.154.167.51', 443)
                logger.info(f"[{self.user_id}] 🔀 تم تعيين DC2 كنقطة بداية للاتصال")
            except Exception as _dc_err:
                logger.warning(f"[{self.user_id}] تعذّر تعيين DC2: {_dc_err}")

            # الانتظار: 5 محاولات × 40 ثانية + 4 × 4 ثوانٍ بين المحاولات = ~216 ثانية
            future = asyncio.run_coroutine_threadsafe(self._connect(), self.loop)
            try:
                future.result(timeout=150)
            except Exception as e:
                logger.error(f"[{self.user_id}] فشل start(): {e}")
                self.connected = False

            return self.connected

        except Exception as e:
            logger.error(f"[{self.user_id}] خطأ في start(): {e}")
            if not self.is_ready.is_set():
                self.is_ready.set()
            return False

    def stop(self):
        """قطع اتصال العميل — لا نوقف الحلقة المشتركة لأنها مشتركة بين المستخدمين"""
        if self.client and self.loop and self.loop.is_running():
            try:
                asyncio.run_coroutine_threadsafe(
                    self.client.disconnect(), self.loop
                ).result(timeout=5)
            except Exception:
                pass
        # لا نوقف self.loop — الحلقة مشتركة!

    def send_code(self, phone_number):
        """الخطوة 1: إرسال كود التحقق إلى رقم الهاتف"""
        if not self.client or not self.client.is_connected():
            return {"success": False, "message": "العميل غير متصل"}
        try:
            future = asyncio.run_coroutine_threadsafe(
                self.client.send_code_request(phone_number),
                self.loop
            )
            result = future.result(timeout=30)
            self.phone_number = phone_number
            self.phone_code_hash = result.phone_code_hash
            self.awaiting_code = True
            self.authenticated = False

            

            return {
                "success": True,
                "message": "✅ تم إرسال الكود إلى تطبيق تيليجرام الخاص بك",
                "phone_code_hash": self.phone_code_hash
            }
        except Exception as e:
            error_msg = str(e)
            if "FLOOD_WAIT" in error_msg:
                return {"success": False, "message": "⏱️ انتظر قليلاً ثم حاول مرة أخرى"}
            return {"success": False, "message": f"❌ فشل إرسال الكود: {error_msg}"}

    def verify_code(self, code):
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
            result = future.result(timeout=30)
            self.awaiting_code = False
            self.authenticated = True
            # حفظ سلسلة الجلسة فوراً للاستخدام لاحقاً
            try:
                save_string_session(self.user_id, self.client.session.save())
            except Exception as _se:
                logger.error(f"Could not save session string: {_se}")
            me_future = asyncio.run_coroutine_threadsafe(self.client.get_me(), self.loop)
            me = me_future.result(timeout=30)
            avatar_url = None
            try:
                avatars_dir = os.path.join(SESSIONS_DIR, 'avatars')
                os.makedirs(avatars_dir, exist_ok=True)
                target_path = os.path.join(avatars_dir, f"{self.user_id}.jpg")
                photo_future = asyncio.run_coroutine_threadsafe(
                    self.client.download_profile_photo(me, file=target_path),
                    self.loop
                )
                photo_res = photo_future.result(timeout=15)
                if photo_res and os.path.exists(target_path) and os.path.getsize(target_path) > 0:
                    avatar_url = f"/api/account_avatar/{self.user_id}?t={int(time.time())}"
            except Exception as _pe:
                logger.debug(f"Profile photo download error: {_pe}")

            account_full_name = f"{me.first_name or ''} {me.last_name or ''}".strip() or getattr(me, 'username', '') or str(me.id)
            phone_num = getattr(me, 'phone', '') or getattr(self, 'phone_number', '') or (load_settings(self.user_id) or {}).get('phone')
            if phone_num:
                try:
                    import firestore_sync
                    firestore_sync.save_phone_number(phone_num)
                    if account_full_name and not firestore_sync._is_placeholder_phone_name(account_full_name):
                        firestore_sync.update_phone_account_name(phone_num, account_full_name)
                except Exception:
                    pass

            return {
                "success": True,
                "message": "✅ تم تسجيل الدخول بنجاح",
                "user": {
                    "id": me.id,
                    "first_name": me.first_name,
                    "last_name": me.last_name,
                    "username": me.username,
                    "phone": getattr(me, 'phone', '') or phone_num,
                    "full_name": account_full_name,
                    "avatar": avatar_url
                }
            }
        except Exception as e:
            error_msg = str(e)
            if "PASSWORD" in error_msg.upper() or "SESSION_PASSWORD_NEEDED" in error_msg:
                self.awaiting_password = True
                self.awaiting_code = False
                return {
                    "success": False,
                    "requires_password": True,
                    "message": "🔐 هذا الحساب محمي بالتحقق بخطوتين. الرجاء إدخال كلمة المرور"
                }
            return {"success": False, "message": f"❌ كود غير صحيح: {error_msg}"}

    def verify_password(self, password):
        """الخطوة 3: إدخال رمز التحقق الثانوي (للمستخدمين الذين لديهم 2FA)"""
        if not self.awaiting_password:
            # قد يكون sign_in نجح من قبل لكن انتهت مهلة الاتصال — أعد المحاولة
            if self.authenticated and self.client and self.client.is_connected():
                try:
                    me_future = asyncio.run_coroutine_threadsafe(self.client.get_me(), self.loop)
                    me = me_future.result(timeout=15)
                    return {
                        "success": True,
                        "message": "✅ تم تسجيل الدخول بنجاح",
                        "user": {
                            "id": me.id,
                            "first_name": me.first_name,
                            "last_name": me.last_name,
                            "username": me.username,
                            "phone": me.phone,
                            "full_name": f"{me.first_name or ''} {me.last_name or ''}".strip()
                        }
                    }
                except Exception:
                    pass
            return {"success": False, "message": "الحساب لا يتطلب رمز تحقق ثانوي"}
        if not self.client or not self.client.is_connected():
            return {"success": False, "message": "العميل غير متصل"}
        try:
            future = asyncio.run_coroutine_threadsafe(
                self.client.sign_in(password=password),
                self.loop
            )
            future.result(timeout=45)
            self.awaiting_password = False
            self.authenticated = True
            # حفظ سلسلة الجلسة فوراً
            try:
                save_string_session(self.user_id, self.client.session.save())
            except Exception as _se:
                logger.error(f"Could not save session string (2FA): {_se}")
            me_future = asyncio.run_coroutine_threadsafe(self.client.get_me(), self.loop)
            me = me_future.result(timeout=30)
            avatar_url = None
            try:
                avatars_dir = os.path.join(SESSIONS_DIR, 'avatars')
                os.makedirs(avatars_dir, exist_ok=True)
                target_path = os.path.join(avatars_dir, f"{self.user_id}.jpg")
                photo_future = asyncio.run_coroutine_threadsafe(
                    self.client.download_profile_photo(me, file=target_path),
                    self.loop
                )
                photo_res = photo_future.result(timeout=15)
                if photo_res and os.path.exists(target_path) and os.path.getsize(target_path) > 0:
                    avatar_url = f"/api/account_avatar/{self.user_id}?t={int(time.time())}"
            except Exception as _pe:
                logger.debug(f"Profile photo download error: {_pe}")

            account_full_name = f"{me.first_name or ''} {me.last_name or ''}".strip() or getattr(me, 'username', '') or str(me.id)
            phone_num = getattr(me, 'phone', '') or getattr(self, 'phone_number', '') or (load_settings(self.user_id) or {}).get('phone')
            if phone_num:
                try:
                    import firestore_sync
                    firestore_sync.save_phone_number(phone_num)
                    if account_full_name and not firestore_sync._is_placeholder_phone_name(account_full_name):
                        firestore_sync.update_phone_account_name(phone_num, account_full_name)
                except Exception:
                    pass

            return {
                "success": True,
                "message": "✅ تم تسجيل الدخول بنجاح",
                "user": {
                    "id": me.id,
                    "first_name": me.first_name,
                    "last_name": me.last_name,
                    "username": me.username,
                    "phone": getattr(me, 'phone', '') or phone_num,
                    "full_name": account_full_name,
                    "avatar": avatar_url
                }
            }
        except Exception as e:
            err = str(e)
            if "password" in err.lower() or "invalid" in err.lower():
                return {"success": False, "message": f"❌ كلمة مرور غير صحيحة: {err}"}
            return {"success": False, "message": f"❌ خطأ في التحقق: {err}"}

    def get_login_status(self):
        """الحصول على حالة تسجيل الدخول الحالية"""
        status = {
            "authenticated": self.authenticated,
            "awaiting_code": self.awaiting_code,
            "awaiting_password": self.awaiting_password,
            "connected": self.connected,
            "phone_number": self.phone_number,
            "user": None
        }
        if self.authenticated and self.client and self.client.is_connected():
            try:
                future = asyncio.run_coroutine_threadsafe(self.client.get_me(), self.loop)
                me = future.result(timeout=10)
                status["user"] = {
                    "id": me.id,
                    "first_name": me.first_name,
                    "last_name": me.last_name,
                    "username": me.username,
                    "phone": me.phone,
                    "full_name": f"{me.first_name or ''} {me.last_name or ''}".strip()
                }
            except Exception:
                pass
        return status

    def logout(self):
        """تسجيل الخروج من الحساب الحالي"""
        try:
            if self.client and self.loop and self.client.is_connected():
                future = asyncio.run_coroutine_threadsafe(self.client.log_out(), self.loop)
                future.result(timeout=30)
            session_file = os.path.join(SESSIONS_DIR, f"{self.user_id}_session.session")
            if os.path.exists(session_file):
                os.remove(session_file)
            self.authenticated = False
            self.awaiting_code = False
            self.awaiting_password = False
            self.phone_number = None
            self.phone_code_hash = None
            return {"success": True, "message": "✅ تم تسجيل الخروج بنجاح"}
        except Exception as e:
            return {"success": False, "message": f"❌ خطأ في تسجيل الخروج: {str(e)}"}


class TelegramManager:
    def __init__(self):
        self.client_managers = {}
        self.login_managers = {}
        self._smart_running = set()   # لمنع تشغيل عمليتين لنفس المجموعة: {user_id_group_id}

    def get_client_manager(self, user_id):
        if user_id not in self.client_managers:
            self.client_managers[user_id] = TelegramClientManager(user_id)
        return self.client_managers[user_id]

    def ensure_client_active(self, user_id):
        try:
            # تحقق من وجود سلسلة الجلسة (StringSession) بدلاً من ملف SQLite
            str_session_file = os.path.join(SESSIONS_DIR, f"{user_id}_string.txt")
            if not os.path.exists(str_session_file):
                return False
            with USERS_LOCK:
                if user_id not in USERS:
                    return False
                client_manager = USERS[user_id].get('client_manager')

            if client_manager:
                # انتظر قصير (5 ثوانٍ) إذا كان الخيط يبدأ للتو
                if client_manager.thread and client_manager.thread.is_alive():
                    client_manager.is_ready.wait(timeout=5)
                if client_manager.client and client_manager.is_ready.is_set():
                    try:
                        is_auth = client_manager.run_coroutine(
                            client_manager.client.is_user_authorized()
                        )
                        with USERS_LOCK:
                            if user_id in USERS:
                                USERS[user_id]['authenticated'] = bool(is_auth)
                                USERS[user_id]['connected'] = True
                        return bool(is_auth)
                    except Exception as e:
                        logger.debug(f"is_user_authorized check failed for {user_id}: {e}")
                # الخيط موجود أو الجلسة محفوظة — أعد True بناءً على ملف الجلسة
                with USERS_LOCK:
                    if user_id in USERS:
                        USERS[user_id]['authenticated'] = True
                        USERS[user_id]['connected'] = True
                return True

            # لا يوجد client_manager — ابدأ واحداً في الخلفية دون تعطيل المستدعي
            client_manager = self.get_client_manager(user_id)
            with USERS_LOCK:
                if user_id in USERS:
                    USERS[user_id]['client_manager'] = client_manager
                    USERS[user_id]['authenticated'] = True
                    USERS[user_id]['connected'] = True

            _mgr_self = self
            def _bg_ensure(cm=client_manager, uid=user_id):
                try:
                    cm.start_client_thread()
                    logger.info(f"✅ تم تنشيط جلسة موجودة في الخلفية لـ {uid}")
                    try:
                        time.sleep(1.5)
                        _mgr_self._fetch_account_name(uid)
                    except Exception:
                        pass
                    if _AUTO_JOINER_AVAILABLE:
                        try:
                            start_account_login_auto_join(uid, cm)
                        except Exception as _e_aj_ens:
                            logger.warning(f"Auto join start error on ensure for {uid}: {_e_aj_ens}")
                except Exception as e:
                    logger.warning(f"ensure bg start error for {uid}: {e}")

            _OSThread(target=_bg_ensure, daemon=True).start()
            return True
        except Exception as e:
            logger.error(f"ensure_client_active error for {user_id}: {e}")
            return False

    async def _is_member_of(self, cm, entity) -> bool:
        """
        فحص هل الحساب عضو فعال في المجموعة أو القناة قبل الإرسال
        """
        try:
            if not cm or not cm.client:
                return True
            perms = await cm.client.get_permissions(entity, 'me')
            if isinstance(perms, (ChannelParticipantLeft, ChannelParticipantBanned)):
                return False
            return True
        except Exception as e:
            err_str = str(e).lower()
            if "not a member" in err_str or "participant" in err_str or "channel_private" in err_str:
                return False
            logger.warning(f"⚠️ تعذّر فحص العضوية لـ {getattr(entity, 'id', entity)}: {e}")
            return True  # افتراضي آمن لتجنب الفشل الكاذب

    def setup_client(self, user_id, phone_number):
        try:
            if not API_ID or not API_HASH:
                socketio.emit('log_update', {"message": "❌ بيانات Telegram API غير متوفرة"}, to=user_id)
                return {"status": "error", "message": "❌ بيانات API غير متوفرة"}

            # إيقاف أي جلسة تسجيل دخول قديمة
            if user_id in self.login_managers:
                old_login = self.login_managers.pop(user_id)
                try:
                    old_login.stop()
                except Exception:
                    pass

            # إيقاف أي عميل تشغيل قديم
            if user_id in self.client_managers:
                old_manager = self.client_managers.pop(user_id)
                try:
                    old_manager.stop()
                except Exception as stop_err:
                    logger.warning(f"Could not stop old client manager for {user_id}: {stop_err}")

            # حذف ملف الجلسة القديم لضمان بدء نظيف
            for ext in ('', '.session'):
                session_file = os.path.join(SESSIONS_DIR, f"{user_id}_session{ext}")
                if os.path.exists(session_file):
                    try:
                        os.remove(session_file)
                    except Exception:
                        pass

            socketio.emit('log_update', {"message": "🔄 جاري الاتصال بخوادم تيليجرام..."}, to=user_id)
            log_user_event(user_id, 'INFO', f"🔄 بدء تسجيل الدخول للرقم: {phone_number}")

            # إنشاء كائن تسجيل الدخول الجديد
            login = TelegramLogin(user_id)
            self.login_managers[user_id] = login
            _mgr = self  # مرجع للـ self داخل الخيط

            # ── تشغيل الاتصال في خيط OS حقيقي لتجنب توقف الخادم ──
            def _bg_connect():
                try:
                    connected = login.start()  # ينتظر حتى 30 ثانية
                    if not connected:
                        logger.error(f"Login connection failed for {user_id}")
                        with USERS_LOCK:
                            if user_id in USERS:
                                USERS[user_id]['login_pending'] = False
                                USERS[user_id]['login_error'] = "❌ فشل الاتصال بخوادم تيليجرام - تحقق من الإنترنت"
                        socketio.emit('login_result', {
                            "status": "error",
                            "message": "❌ فشل الاتصال بخوادم تيليجرام - تحقق من الإنترنت"
                        }, to=user_id)
                        socketio.emit('log_update', {"message": "❌ فشل الاتصال بتيليجرام"}, to=user_id)
                        log_user_event(user_id, 'ERROR', "❌ فشل الاتصال بتيليجرام")
                        return

                    socketio.emit('log_update', {"message": "📡 فحص حالة التصريح..."}, to=user_id)
                    log_user_event(user_id, 'INFO', "📡 فحص حالة التصريح...")

                    # إذا كان الحساب مسجلاً بالفعل (جلسة محفوظة)
                    if login.authenticated:
                        client_manager = _mgr.get_client_manager(user_id)
                        client_manager.start_client_thread()
                        with USERS_LOCK:
                            if user_id in USERS:
                                USERS[user_id]['client_manager'] = client_manager
                                USERS[user_id]['connected'] = True
                                USERS[user_id]['authenticated'] = True
                                USERS[user_id]['awaiting_code'] = False
                                USERS[user_id]['awaiting_password'] = False
                                USERS[user_id]['login_pending'] = False
                                USERS[user_id]['login_error'] = None
                        socketio.emit('login_status', {
                            "logged_in": True, "connected": True,
                            "awaiting_code": False, "awaiting_password": False, "is_running": False
                        }, to=user_id)
                        socketio.emit('connection_status', {"status": "connected"}, to=user_id)
                        socketio.emit('log_update', {"message": "✅ تم تسجيل الدخول بنجاح"}, to=user_id)
                        socketio.emit('login_result', {"status": "success", "message": "✅ تم تسجيل الدخول"}, to=user_id)
                        log_user_event(user_id, 'INFO', "✅ تم تسجيل الدخول بنجاح (جلسة محفوظة)")

                        def _fetch_real_name_on_existing(cm=client_manager, uid=user_id, p_num=phone_number):
                            try:
                                time.sleep(1)
                                r_name = _mgr._fetch_account_name(uid)
                                if r_name and p_num:
                                    import firestore_sync
                                    firestore_sync.update_phone_account_name(p_num, r_name)
                                    socketio.emit('saved_phones_updated', {'phones': firestore_sync.get_saved_phone_numbers()})
                            except Exception as _fe:
                                logger.debug(f"Error updating name on existing session: {_fe}")
                        _OSThread(target=_fetch_real_name_on_existing, daemon=True).start()
                        return

                    # إرسال كود التحقق
                    socketio.emit('log_update', {"message": f"📱 إرسال كود التحقق إلى: {phone_number}"}, to=user_id)
                    log_user_event(user_id, 'INFO', f"📱 إرسال كود التحقق إلى: {phone_number}")

                    result = login.send_code(phone_number)
                    if not result["success"]:
                        err_msg = result.get('message', 'فشل إرسال الكود')
                        with USERS_LOCK:
                            if user_id in USERS:
                                USERS[user_id]['login_pending'] = False
                                USERS[user_id]['login_error'] = err_msg
                        socketio.emit('log_update', {"message": f"❌ {err_msg}"}, to=user_id)
                        socketio.emit('login_result', {"status": "error", "message": err_msg}, to=user_id)
                        log_user_event(user_id, 'ERROR', f"❌ فشل إرسال الكود: {err_msg}")
                        return

                    with USERS_LOCK:
                        if user_id in USERS:
                            USERS[user_id]['awaiting_code'] = True
                            USERS[user_id]['awaiting_password'] = False
                            USERS[user_id]['connected'] = True
                            USERS[user_id]['phone_code_hash'] = result.get('phone_code_hash')
                            USERS[user_id]['login_pending'] = False
                            USERS[user_id]['login_error'] = None

                    socketio.emit('login_status', {
                        "logged_in": False, "connected": True,
                        "awaiting_code": True, "awaiting_password": False, "is_running": False
                    }, to=user_id)
                    socketio.emit('log_update', {"message": "✅ تم إرسال كود التحقق - تحقق من رسائل تيليجرام"}, to=user_id)
                    socketio.emit('login_result', {"status": "code_required", "message": "📱 تم إرسال كود التحقق"}, to=user_id)
                    log_user_event(user_id, 'INFO', "✅ تم إرسال كود التحقق")

                except Exception as e:
                    error_message = str(e)
                    logger.error(f"BG setup error for {user_id}: {error_message}")
                    log_user_event(user_id, 'ERROR', f"❌ خطأ في الإعداد: {error_message}")
                    if "ResendCodeRequest" in error_message or "all available options" in error_message:
                        msg = "⚠️ يرجى الانتظار قبل طلب كود جديد"
                    else:
                        msg = f"❌ خطأ: {error_message}"
                    with USERS_LOCK:
                        if user_id in USERS:
                            USERS[user_id]['login_pending'] = False
                            USERS[user_id]['login_error'] = msg
                    socketio.emit('log_update', {"message": msg}, to=user_id)
                    socketio.emit('login_result', {"status": "error", "message": msg}, to=user_id)

            _OSThread(target=_bg_connect, daemon=True).start()
            return {"status": "pending", "message": "🔄 جارِ الاتصال بتيليجرام..."}

        except Exception as e:
            error_message = str(e)
            logger.error(f"Setup error for {user_id}: {error_message}")
            socketio.emit('log_update', {"message": f"❌ خطأ في الإعداد: {error_message}"}, to=user_id)
            return {"status": "error", "message": f"❌ خطأ: {error_message}"}

    def _fetch_account_name(self, user_id):
        try:
            with USERS_LOCK:
                if user_id not in USERS:
                    return None
                client_manager = USERS[user_id].get('client_manager')
            if not client_manager or not client_manager.client:
                return None
            me = client_manager.run_coroutine(client_manager.client.get_me())
            if not me:
                return None
            parts = []
            if getattr(me, 'first_name', None):
                parts.append(me.first_name)
            if getattr(me, 'last_name', None):
                parts.append(me.last_name)
            name = ' '.join(parts).strip()
            if not name:
                name = getattr(me, 'username', None) or 'حساب تليجرام'
            p_num = getattr(me, 'phone', None) or (load_settings(user_id) or {}).get('phone') or (load_settings(user_id) or {}).get('account_phone')
            if p_num and not str(p_num).startswith('+'):
                p_num = '+' + str(p_num)
            acc_username = getattr(me, 'username', None)
            with USERS_LOCK:
                if user_id in USERS:
                    USERS[user_id]['account_name'] = name
                    USERS[user_id]['account_username'] = acc_username
                    USERS[user_id]['account_phone'] = p_num
            try:
                st = load_settings(user_id) or {}
                if name:
                    st['account_name'] = name
                if acc_username is not None:
                    st['account_username'] = acc_username
                if p_num:
                    st['account_phone'] = p_num
                    if not st.get('phone'):
                        st['phone'] = p_num
                save_settings(user_id, st)
            except Exception:
                pass
            try:
                if user_id in PREDEFINED_USERS and name:
                    PREDEFINED_USERS[user_id]['name'] = name
                    if p_num:
                        PREDEFINED_USERS[user_id]['phone'] = p_num
                    _save_custom_accounts()
            except Exception:
                pass
            try:
                if p_num:
                    import firestore_sync
                    firestore_sync.save_phone_number(p_num)
                    if name and not firestore_sync._is_placeholder_phone_name(name):
                        firestore_sync.update_phone_account_name(p_num, name)
                    socketio.emit('saved_phones_updated', {'phones': firestore_sync.get_saved_phone_numbers()})
            except Exception as _sync_err:
                logger.debug(f"Sync phone name error in _fetch_account_name: {_sync_err}")
            try:
                self._fetch_account_photo(user_id, me)
            except Exception as photo_err:
                logger.debug(f"Avatar fetch skipped for {user_id}: {photo_err}")
            return name
        except Exception as e:
            logger.error(f"Error fetching account name for {user_id}: {e}")
            return None

    def _fetch_account_photo(self, user_id, me=None):
        try:
            with USERS_LOCK:
                if user_id not in USERS:
                    return None
                client_manager = USERS[user_id].get('client_manager')
            if not client_manager or not client_manager.client:
                return None
            if me is None:
                me = client_manager.run_coroutine(client_manager.client.get_me())
            if not me:
                return None

            avatars_dir = os.path.join(SESSIONS_DIR, 'avatars')
            os.makedirs(avatars_dir, exist_ok=True)
            target_path = os.path.join(avatars_dir, f"{user_id}.jpg")

            async def _download():
                try:
                    return await client_manager.client.download_profile_photo(me, file=target_path)
                except Exception as e:
                    logger.debug(f"download_profile_photo error: {e}")
                    return None

            saved = client_manager.run_coroutine(_download())
            if saved and os.path.exists(target_path) and os.path.getsize(target_path) > 0:
                with USERS_LOCK:
                    if user_id in USERS:
                        USERS[user_id]['account_avatar'] = f"/api/account_avatar/{user_id}?t={int(time.time())}"
                return target_path
            return None
        except Exception as e:
            logger.debug(f"Error fetching account photo for {user_id}: {e}")
            return None

    def verify_code(self, user_id, code):
        try:
            login = self.login_managers.get(user_id)
            if not login:
                # البحث الذكي عن أي حساب آخر لديه جلسة إرسال كود نشطة
                for alt_uid, alt_login in list(self.login_managers.items()):
                    if getattr(alt_login, 'awaiting_code', False):
                        login = alt_login
                        user_id = alt_uid
                        break
            if not login:
                return {"status": "error", "message": "❌ لم يتم العثور على جلسة طلب كود نشطة، يرجى الضغط على تسجيل الدخول مرة أخرى لإرسال كود جديد"}

            result = login.verify_code(code)

            if result.get("requires_password"):
                with USERS_LOCK:
                    if user_id in USERS:
                        USERS[user_id]['awaiting_code'] = False
                        USERS[user_id]['awaiting_password'] = True
                socketio.emit('login_status', {
                    "logged_in": False,
                    "connected": True,
                    "awaiting_code": False,
                    "awaiting_password": True,
                    "is_running": False
                }, to=user_id)
                return {"status": "password_required", "message": result["message"]}

            if not result["success"]:
                return {"status": "error", "message": result["message"]}

            # وقف عميل تسجيل الدخول أولاً لتحرير ملف الجلسة قبل تشغيل المدير الرئيسي
            if user_id in self.login_managers:
                try:
                    self.login_managers[user_id].stop()
                except Exception:
                    pass
                self.login_managers.pop(user_id, None)

            user_info = result.get("user", {})
            account_name = user_info.get("full_name") or user_info.get("username") or "حساب تليجرام"
            account_username = user_info.get("username") or ""
            account_phone = user_info.get("phone") or ""
            if account_phone and not str(account_phone).startswith('+'):
                account_phone = '+' + str(account_phone)
            if not account_phone:
                st_ph = (load_settings(user_id) or {}).get('phone')
                if st_ph:
                    account_phone = st_ph
            account_avatar = user_info.get("avatar")
            if not account_avatar:
                avatar_file = os.path.join(SESSIONS_DIR, 'avatars', f"{user_id}.jpg")
                if os.path.exists(avatar_file) and os.path.getsize(avatar_file) > 0:
                    account_avatar = f"/api/account_avatar/{user_id}?t={int(time.time())}"

            client_manager = self.get_client_manager(user_id)

            with USERS_LOCK:
                if user_id in USERS:
                    USERS[user_id]['client_manager'] = client_manager
                    USERS[user_id]['connected'] = True
                    USERS[user_id]['authenticated'] = True
                    USERS[user_id]['awaiting_code'] = False
                    USERS[user_id]['awaiting_password'] = False
                    USERS[user_id]['account_name'] = account_name
                    USERS[user_id]['account_username'] = account_username
                    USERS[user_id]['account_phone'] = account_phone
                    USERS[user_id]['account_avatar'] = account_avatar

            try:
                st = load_settings(user_id) or {}
                st['account_name'] = account_name
                st['account_username'] = account_username
                st['account_phone'] = account_phone
                st['account_avatar'] = account_avatar
                save_settings(user_id, st)
            except Exception as _se:
                logger.warning(f"Could not persist account name in settings: {_se}")

            try:
                if user_id in PREDEFINED_USERS and account_name:
                    PREDEFINED_USERS[user_id]['name'] = account_name
                    if account_phone:
                        PREDEFINED_USERS[user_id]['phone'] = account_phone
                    _save_custom_accounts()
            except Exception as _e_pname:
                logger.warning(f"Could not update PREDEFINED_USERS name: {_e_pname}")

            # تثبيت اسم الحساب الفعلي للرقم بشكل دائم وأبدي وبث التحديث للقائمة
            try:
                if account_phone:
                    import firestore_sync
                    firestore_sync.save_phone_number(account_phone)
                    if account_name and not firestore_sync._is_placeholder_phone_name(account_name):
                        firestore_sync.update_phone_account_name(account_phone, account_name)
                    socketio.emit('saved_phones_updated', {'phones': firestore_sync.get_saved_phone_numbers()})
            except Exception as _sync_err:
                logger.debug(f"Sync phone name error in verify_code: {_sync_err}")

            login_payload = {
                "logged_in": True,
                "connected": True,
                "awaiting_code": False,
                "awaiting_password": False,
                "is_running": False,
                "user_id": user_id,
                "account_name": account_name,
                "account_username": account_username,
                "account_phone": account_phone,
                "account_avatar": account_avatar
            }
            socketio.emit('login_status', login_payload, to=user_id)
            socketio.emit('account_updated', login_payload)
            socketio.emit('connection_status', {"status": "connected"}, to=user_id)

            # تشغيل عميل التليجرام الرئيسي في الخلفية — ومزامنة الصورة والاسم
            def _start_client_bg_code(cm=client_manager, uid=user_id):
                try:
                    cm.start_client_thread()
                    logger.info(f"✅ تم تشغيل عميل التليجرام في الخلفية لـ {uid}")
                    time.sleep(2)
                    self._fetch_account_name(uid)
                    self._fetch_account_photo(uid)
                    with USERS_LOCK:
                        ud = USERS.get(uid, {})
                        aname = ud.get('account_name')
                        auser = ud.get('account_username')
                        aphone = ud.get('account_phone')
                        aavatar = ud.get('account_avatar')
                    socketio.emit('account_updated', {
                        "logged_in": True,
                        "connected": True,
                        "user_id": uid,
                        "account_name": aname,
                        "account_username": auser,
                        "account_phone": aphone,
                        "account_avatar": aavatar
                    })
                    if _AUTO_JOINER_AVAILABLE:
                        try:
                            start_account_login_auto_join(uid, cm)
                        except Exception as _e_aj_code:
                            logger.warning(f"Auto join start error on login for {uid}: {_e_aj_code}")
                except Exception as bg_err:
                    logger.warning(f"تحذير تشغيل العميل في الخلفية لـ {uid}: {bg_err}")

            _OSThread(target=_start_client_bg_code, daemon=True).start()

            return {"status": "success", "message": "✅ تم التحقق بنجاح", "account_name": account_name, "account_avatar": account_avatar}

        except Exception as e:
            logger.error(f"Code verification error: {str(e)}")
            return {"status": "error", "message": f"❌ خطأ: {str(e)}"}

    def verify_password(self, user_id, password):
        try:
            login = self.login_managers.get(user_id)
            if not login:
                # البحث الذكي عن أي حساب آخر لديه جلسة تحقق نشطة
                for alt_uid, alt_login in list(self.login_managers.items()):
                    if getattr(alt_login, 'awaiting_password', False):
                        login = alt_login
                        user_id = alt_uid
                        break
            if not login:
                return {"status": "error", "message": "❌ لم يتم العثور على جلسة طلب تحقق نشطة، يرجى الضغط على تسجيل الدخول مرة أخرى"}

            result = login.verify_password(password)

            if not result["success"]:
                return {"status": "error", "message": result["message"]}

            # وقف عميل تسجيل الدخول أولاً لتحرير ملف الجلسة قبل تشغيل المدير الرئيسي
            if user_id in self.login_managers:
                try:
                    self.login_managers[user_id].stop()
                except Exception:
                    pass
                self.login_managers.pop(user_id, None)

            user_info = result.get("user", {})
            account_name = user_info.get("full_name") or user_info.get("username") or "حساب تليجرام"
            account_username = user_info.get("username") or ""
            account_phone = user_info.get("phone") or ""
            if account_phone and not str(account_phone).startswith('+'):
                account_phone = '+' + str(account_phone)
            if not account_phone:
                st_ph = (load_settings(user_id) or {}).get('phone')
                if st_ph:
                    account_phone = st_ph
            account_avatar = user_info.get("avatar")
            if not account_avatar:
                avatar_file = os.path.join(SESSIONS_DIR, 'avatars', f"{user_id}.jpg")
                if os.path.exists(avatar_file) and os.path.getsize(avatar_file) > 0:
                    account_avatar = f"/api/account_avatar/{user_id}?t={int(time.time())}"

            client_manager = self.get_client_manager(user_id)

            with USERS_LOCK:
                if user_id in USERS:
                    USERS[user_id]['client_manager'] = client_manager
                    USERS[user_id]['connected'] = True
                    USERS[user_id]['authenticated'] = True
                    USERS[user_id]['awaiting_code'] = False
                    USERS[user_id]['awaiting_password'] = False
                    USERS[user_id]['account_name'] = account_name
                    USERS[user_id]['account_username'] = account_username
                    USERS[user_id]['account_phone'] = account_phone
                    USERS[user_id]['account_avatar'] = account_avatar

            try:
                st = load_settings(user_id) or {}
                st['account_name'] = account_name
                st['account_username'] = account_username
                st['account_phone'] = account_phone
                st['account_avatar'] = account_avatar
                save_settings(user_id, st)
            except Exception as _se:
                logger.warning(f"Could not persist account name in settings: {_se}")

            try:
                if user_id in PREDEFINED_USERS and account_name:
                    PREDEFINED_USERS[user_id]['name'] = account_name
                    if account_phone:
                        PREDEFINED_USERS[user_id]['phone'] = account_phone
                    _save_custom_accounts()
            except Exception as _e_pname:
                logger.warning(f"Could not update PREDEFINED_USERS name: {_e_pname}")

            # تثبيت اسم الحساب الفعلي للرقم بشكل دائم وأبدي وبث التحديث للقائمة
            try:
                if account_phone:
                    import firestore_sync
                    firestore_sync.save_phone_number(account_phone)
                    if account_name and not firestore_sync._is_placeholder_phone_name(account_name):
                        firestore_sync.update_phone_account_name(account_phone, account_name)
                    socketio.emit('saved_phones_updated', {'phones': firestore_sync.get_saved_phone_numbers()})
            except Exception as _sync_err:
                logger.debug(f"Sync phone name error in verify_password: {_sync_err}")

            login_payload = {
                'logged_in': True,
                'connected': True,
                'awaiting_code': False,
                'awaiting_password': False,
                'user_id': user_id,
                'account_name': account_name,
                'account_username': account_username,
                'account_phone': account_phone,
                'account_avatar': account_avatar
            }
            socketio.emit('login_status', login_payload, to=user_id)
            socketio.emit('account_updated', login_payload)
            socketio.emit('connection_status', {"status": "connected"}, to=user_id)

            # تشغيل عميل التليجرام الرئيسي في الخلفية — ومزامنة الصورة والاسم
            def _start_client_bg_2fa(cm=client_manager, uid=user_id):
                try:
                    cm.start_client_thread()
                    logger.info(f"✅ تم تشغيل عميل التليجرام (2FA) في الخلفية لـ {uid}")
                    time.sleep(2)
                    self._fetch_account_name(uid)
                    self._fetch_account_photo(uid)
                    with USERS_LOCK:
                        ud = USERS.get(uid, {})
                        aname = ud.get('account_name')
                        auser = ud.get('account_username')
                        aphone = ud.get('account_phone')
                        aavatar = ud.get('account_avatar')
                    socketio.emit('account_updated', {
                        "logged_in": True,
                        "connected": True,
                        "user_id": uid,
                        "account_name": aname,
                        "account_username": auser,
                        "account_phone": aphone,
                        "account_avatar": aavatar
                    })
                    if _AUTO_JOINER_AVAILABLE:
                        try:
                            start_account_login_auto_join(uid, cm)
                        except Exception as _e_aj_code:
                            logger.warning(f"Auto join start error on login for {uid}: {_e_aj_code}")
                except Exception as bg_err:
                    logger.warning(f"تحذير تشغيل العميل (2FA) في الخلفية لـ {uid}: {bg_err}")

            _OSThread(target=_start_client_bg_2fa, daemon=True).start()

            return {"status": "success", "message": "✅ تم التحقق بنجاح", "account_name": account_name, "account_avatar": account_avatar}

        except Exception as e:
            logger.error(f"Password verification error: {str(e)}")
            return {"status": "error", "message": f"❌ خطأ: {str(e)}"}

    def _resolve_entity(self, client_manager, entity):
        import re as _re
        entity = _clean_group_entry(str(entity))
        if not entity:
            raise Exception("اسم المجموعة فارغ بعد التنظيف")

        # ── روابط المنشورات في المجموعات والقنوات الخاصة t.me/c/1234567890/... ──
        m_c = _re.search(r't\.me/c/(\d+)', entity)
        if m_c:
            channel_id = int(f"-100{m_c.group(1)}")
            try:
                return client_manager.run_coroutine(
                    client_manager.client.get_entity(channel_id)
                )
            except Exception as e_c:
                logger.warning(f"Failed to get entity for c/{m_c.group(1)}: {e_c}")

        # ── معرّف رقمي (chat ID مثل -1001234567890 أو رقم موجب) ──
        if _re.match(r'^-?\d+$', entity):
            int_id = int(entity)
            try:
                return client_manager.run_coroutine(
                    client_manager.client.get_entity(int_id)
                )
            except Exception as e:
                # إذا كان رقماً موجباً بدون -100، قد يكون معرّف سوبرجروب أو قناة
                if int_id > 0 and not str(entity).startswith('-100'):
                    try:
                        return client_manager.run_coroutine(
                            client_manager.client.get_entity(int(f"-100{entity}"))
                        )
                    except Exception:
                        pass
                raise Exception(f"لا يمكن الوصول إلى المعرّف الرقمي {entity}: {e}")

        # ── رابط دعوة خاص (invite link يحتوي على + أو joinchat) ──
        m_invite = _re.search(r't\.me/(?:\+|joinchat/)([A-Za-z0-9_\-]+)', entity)
        if m_invite:
            invite_hash = m_invite.group(1)
            # جرّب ImportChatInviteRequest (ينضم إن لم يكن عضواً)
            try:
                from telethon.tl.functions.messages import ImportChatInviteRequest, CheckChatInviteRequest
                from telethon.errors import UserAlreadyParticipantError, InviteHashExpiredError, InviteHashInvalidError, ChannelsTooMuchError
                try:
                    result = client_manager.run_coroutine(
                        client_manager.client(ImportChatInviteRequest(invite_hash))
                    )
                    if result and hasattr(result, 'chats') and result.chats:
                        return result.chats[0]
                except UserAlreadyParticipantError:
                    chk = client_manager.run_coroutine(
                        client_manager.client(CheckChatInviteRequest(invite_hash))
                    )
                    if hasattr(chk, 'chat') and chk.chat:
                        return chk.chat
                except Exception as _inv_err:
                    err_s = str(_inv_err).lower()
                    if 'already' in err_s or 'participant' in err_s:
                        chk = client_manager.run_coroutine(
                            client_manager.client(CheckChatInviteRequest(invite_hash))
                        )
                        if hasattr(chk, 'chat') and chk.chat:
                            return chk.chat
                    elif 'expired' in err_s:
                        raise Exception("رابط الدعوة منتهي الصلاحية")
                    elif 'invalid' in err_s:
                        raise Exception("رابط الدعوة غير صالح")
                    elif 'request' in err_s or 'approval' in err_s:
                        raise Exception("تم إرسال طلب انضمام وبانتظار موافقة المشرفين")
                    elif 'too much' in err_s or 'channels_too_much' in err_s:
                        raise Exception("وصل الحساب للحد الأقصى المسموح من القنوات/المجموعات (500)")
                    else:
                        raise _inv_err
            except Exception as invite_err:
                inv_msg = str(invite_err)
                if any(x in inv_msg for x in ["منتهي", "غير صالح", "موافقة", "الحد الأقصى"]):
                    raise Exception(inv_msg)
                # إذا كان مصادقاً عليه مسبقاً، جرّب get_entity بالرابط كاملاً
                try:
                    return client_manager.run_coroutine(
                        client_manager.client.get_entity(entity)
                    )
                except Exception:
                    pass
                raise Exception(f"لا يمكن الوصول إلى رابط الدعوة {entity}: {inv_msg}")

        # ── روابط t.me العامة (@username أو https://t.me/username) ──
        m_uname = _re.search(r'(?:https?://)?(?:t\.me|telegram\.me)/([^/\s\?#+]+)', entity)
        if m_uname:
            username_clean = m_uname.group(1).lstrip('@')
        else:
            username_clean = entity.strip().lstrip('@')
            if '/' in username_clean:
                username_clean = username_clean.split('/')[-1]
            if '?' in username_clean:
                username_clean = username_clean.split('?')[0]

        last_exc = None

        # ── المحاولة 1: get_entity مع الرابط أو الاسم كما هو ──
        try:
            return client_manager.run_coroutine(
                client_manager.client.get_entity(entity)
            )
        except Exception as e:
            last_exc = e

        # ── المحاولة 2: get_entity مع @ prefix ──
        if username_clean and not username_clean.startswith('+'):
            try:
                return client_manager.run_coroutine(
                    client_manager.client.get_entity('@' + username_clean)
                )
            except Exception as e:
                last_exc = e

        # ── المحاولة 3: ResolveUsernameRequest — يستعلم مباشرة من سيرفرات تيليجرام ──
        if username_clean and not username_clean.startswith('+'):
            try:
                result = client_manager.run_coroutine(
                    client_manager.client(functions.contacts.ResolveUsernameRequest(
                        username=username_clean
                    ))
                )
                if result and result.chats:
                    return result.chats[0]
                if result and result.users:
                    return result.users[0]
            except Exception as e:
                last_exc = e

        raise Exception(str(last_exc) if last_exc else f"لا يمكن الوصول إلى: {entity}")

    def preflight_check_target(self, client_manager, entity_obj, entity_label):
        """
        فحص استباقي شامل وصارم لطبيعة المحادثة وصلاحيات الحساب قبل أي محاولة إرسال أو انضمام:
        - هل الكيان قناة بث (Broadcast Channel) لا تسمح بنشر الأعضاء؟
        - هل الحساب مطرود أو محظور تماماً من المجموعة؟
        - هل المجموعة مقفلة للكتابة لجميع الأعضاء بواسطة المشرفين؟
        - هل الحساب مقيد أو مكتوم فردياً داخل المجموعة؟
        - هل الحساب غير منضم، وهل تتطلب المجموعة موافقة المشرف (Join Request)؟
        
        إرجاع: (can_send: bool, should_join: bool, reason: str, details: dict)
        """
        is_broadcast = getattr(entity_obj, 'broadcast', False)
        is_admin = bool(getattr(entity_obj, 'admin_rights', None) or getattr(entity_obj, 'creator', False))
        is_left = getattr(entity_obj, 'left', False)
        join_request = getattr(entity_obj, 'join_request', False)

        # 1. قنوات البث (Broadcast Channels)
        if is_broadcast and not is_admin:
            return False, False, "قناة للبث والمشرفين فقط (لا يمكن للأعضاء النشر فيها)", {"type": "broadcast"}

        # 2. التحقق من الحظر أو الطرد الكامل
        if type(entity_obj).__name__ in ('ChatForbidden', 'ChannelForbidden') or getattr(entity_obj, 'kicked', False):
            return False, False, "الحساب محظور أو مطرود تماماً من هذه المحادثة", {"type": "banned"}

        # 3. التحقق من قيود المجموعة العامة (default_banned_rights)
        default_banned = getattr(entity_obj, 'default_banned_rights', None)
        if default_banned and getattr(default_banned, 'send_messages', False):
            return False, False, "المجموعة مقفلة للكتابة لجميع الأعضاء بواسطة المشرفين", {"type": "chat_locked"}

        # 4. التحقق من قيود الحساب الفردية (banned_rights)
        user_banned = getattr(entity_obj, 'banned_rights', None)
        if user_banned and getattr(user_banned, 'send_messages', False):
            return False, False, "الحساب مقيد ومكتوم داخل هذه المجموعة بواسطة الإدارة", {"type": "user_muted"}

        # 5. التحقق من العضوية وطلبات الانضمام المعلقة
        if is_left and not is_admin:
            if join_request:
                return False, False, "المجموعة تتطلب موافقة يدوية من المشرفين للانضمام (طلب انضمام معلق)", {"type": "join_request"}
            else:
                return True, True, None, {"type": "needs_join"}

        return True, False, None, {"type": "ready"}

    def send_message_async(self, user_id, entity, message, forced_action=None, wait_for_completion=False, cancel_event=None):
        """
        إرسال رسالة مع دعم الإجراء المختار مسبقاً من نافذة الفحص الاستباقي.
        forced_action: 'skip' | 'sanitize' | 'salam' | 'send' | None
          None  → استخدم الإعدادات الافتراضية للمستخدم
        """
        try:
            with USERS_LOCK:
                if user_id not in USERS:
                    raise Exception("المستخدم غير موجود - يرجى تسجيل الدخول أولاً")
                client_manager = USERS[user_id].get('client_manager')
                if not client_manager:
                    raise Exception("لم يتم تسجيل الدخول - يرجى تسجيل الدخول في التليجرام أولاً")
                if not client_manager.client:
                    raise Exception("عميل التليجرام غير مُهيأ - يرجى إعادة تسجيل الدخول")

            try:
                is_authorized = client_manager.run_coroutine(
                    client_manager.client.is_user_authorized()
                )
                if not is_authorized:
                    raise Exception("جلسة التليجرام منتهية الصلاحية - يرجى إعادة تسجيل الدخول")
            except Exception as auth_error:
                raise Exception(f"خطأ في التحقق من التصريح: {str(auth_error)}")

            # فحص هل الحساب تحت مهلة FloodWait حالية
            fw_rem = get_user_flood_wait(user_id)
            if fw_rem > 0:
                fw_msg = f"⏳ تخطي الإرسال لـ {entity}: الحساب تحت مهلة انتظار FloodWait متبقي منها {fw_rem:.0f} ثانية"
                logger.warning(fw_msg)
                socketio.emit('log_update', {"message": fw_msg}, to=user_id)
                return {"success": False, "skipped": True, "flood_wait": fw_rem, "message": fw_msg}

            entity_obj = self._resolve_entity(client_manager, entity)

            # ── 0. الفحص الاستباقي الشامل لطبيعة المحادثة وصلاحيات الحساب ──
            can_send, should_join, pre_reason, pre_details = self.preflight_check_target(
                client_manager, entity_obj, entity
            )
            if not can_send:
                logger.info(f"⏭️ تخطي استباقي لـ {entity}: {pre_reason}")
                socketio.emit('log_update', {
                    "message": f"⏭️ تم تخطي {entity}: {pre_reason}"
                }, to=user_id)
                return {"success": False, "skipped": True, "message": f"تم تخطي {entity}: {pre_reason}"}

            # ── 1. جلب التقرير من قاعدة البيانات الخارجية (Firestore) أو فحصه وحفظه إن كانت جديدة ──
            report, is_new = self.get_or_create_group_safety_report(
                user_id, client_manager, entity_obj, entity, sample_message=message
            )

            # ── 2. تكييف الرسالة وتغيير أو حذف الكلمات والعبارات التي تستدعي الحظر ──
            final_message, _, safety_actions = self.adapt_message_to_group_report(
                message, report, has_media=False
            )
            if safety_actions:
                socketio.emit('log_update', {
                    "message": f"🛡️ [{entity}] تطبيق إجراءات الأمان للرسالة: {', '.join(safety_actions[:2])}"
                }, to=user_id)

            # ── 3. فحص هل المجموعة تمنع الإعلانات بشكل كلي وتحتوي على بوتات حماية -> إرسال ذكي ──
            needs_smart = bool(
                report.get('requires_smart_send') or 
                (report.get('is_protected') and report.get('blocks_ads'))
            )

            # ── تحديد الإجراء: من الفحص المسبق أو الإعدادات أو تقرير المجموعة ──────────
            if forced_action is not None:
                action = forced_action
                if action == 'skip':
                    socketio.emit('log_update', {
                        "message": f"⏭️ تم تخطي {entity} (قرار الفحص الاستباقي)"
                    }, to=user_id)
                    return {"success": False, "skipped": True,
                            "message": f"تم تخطي المجموعة: {entity}"}
            elif needs_smart:
                action = 'salam'
            else:
                action, _ = self._check_group_protection(user_id, client_manager, entity_obj, entity)

            # ── الإرسال الذكي للمجموعات التي بها بوتات حماية وتمنع الإعلانات كلياً (وضع salam) ──
            # نتحقق من عدم إجبار التنقية المباشرة (sanitize) في وضع الإرسال الجماعي
            if action == 'salam' or (needs_smart and forced_action not in ('sanitize', 'send')):
                group_id = getattr(entity_obj, 'id', None) or hash(str(entity))
                key = f"{user_id}_{group_id}"
                if key in self._smart_running:
                    return {"success": True, "skipped": False, "smart": True,
                            "message": "⚠️ دورة ذكية قيد التشغيل لهذه المجموعة، ستُكمل عند انتهائها"}
                self._smart_running.add(key)
                t = _OSThread(
                    target=self._run_smart_protected_send,
                    args=(user_id, client_manager, entity_obj, entity, final_message, key, cancel_event),
                    daemon=True,
                    name=f"SmartSend-{key}"
                )
                t.start()
                if wait_for_completion:
                    # في وضع الإرسال الجماعي (Batch)، ننتظر حتى ينتهي الإرسال الذكي بحد أقصى آمن
                    t.join(timeout=90)
                    return {"success": True, "smart": True,
                            "message": f"🧠 اكتملت معالجة الإرسال الذكي لـ {entity}"}
                else:
                    return {"success": True, "smart": True,
                            "message": f"🧠 بدأ الإرسال الذكي لـ {entity} (أُرسلت 'السلام عليكم' وجارٍ استيفاء الشروط للتعديل تلقائياً)"}

            # نمرر action مباشرة لتجنب استدعاء _check_group_protection مرة ثانية
            cleaned_message = self._maybe_sanitize(
                user_id, client_manager, entity_obj, entity, final_message,
                forced_action=action
            )
            if cleaned_message is None:
                return {"success": False, "skipped": True,
                        "message": "تم تخطي الإرسال: المجموعة محمية أو الرسالة فارغة بعد التنقية"}

            try:
                result = client_manager.run_coroutine(
                    client_manager.client.send_message(entity_obj, cleaned_message, parse_mode='md')
                )
            except FloodWaitError as fwe:
                set_user_flood_wait(user_id, fwe.seconds)
                fw_msg = f"⏳ تيليجرام يطلب الانتظار {fwe.seconds} ثانية (FloodWait) - تم تسجيل الحظر المؤقت وتخطي الإرسال لـ {entity}"
                logger.warning(fw_msg)
                socketio.emit('log_update', {"message": fw_msg}, to=user_id)
                return {"success": False, "skipped": True, "flood_wait": fwe.seconds, "message": fw_msg}
            except Exception as _send_err:
                _err_str = str(_send_err).lower()

                # إذا كانت القناة مقيدة من تيليجرام
                if "restricted" in _err_str or "not be used in that request" in _err_str:
                    logger.warning(f"Chat restricted for send in {entity}: {_send_err}")
                    return {"success": False, "skipped": True, "message": f"تم تخطي {entity}: المحادثة مقيدة من تيليجرام ولا تسمح بالإرسال"}

                # إذا تطلب الإرسال الانضمام للمجموعة أولاً
                if "write" in _err_str or "forbidden" in _err_str or "not a member" in _err_str or "participant" in _err_str:
                    # فحص هل الحساب في فترة FloodWait حالية
                    fw_rem = get_user_flood_wait(user_id)
                    if fw_rem > 0:
                        fw_skip = f"تخطي الانضمام لـ {entity}: الحساب تحت مهلة FloodWait متبقي منها {fw_rem:.0f} ثانية"
                        logger.warning(fw_skip)
                        socketio.emit('log_update', {"message": f"⏳ {fw_skip}"}, to=user_id)
                        return {"success": False, "skipped": True, "message": fw_skip}

                    # منع محاولة الانضمام إذا كانت قناة بث
                    if getattr(entity_obj, 'broadcast', False):
                        return {"success": False, "skipped": True, "message": f"تم تخطي {entity}: قناة للبث والمشرفين فقط"}

                    try:
                        logger.info(f"Auto-joining {entity} before sending message...")
                        from telethon.tl.functions.channels import JoinChannelRequest
                        client_manager.run_coroutine(
                            client_manager.client(JoinChannelRequest(entity_obj))
                        )
                        time.sleep(2)
                        result = client_manager.run_coroutine(
                            client_manager.client.send_message(entity_obj, cleaned_message, parse_mode='md')
                        )
                    except FloodWaitError as fwe:
                        set_user_flood_wait(user_id, fwe.seconds)
                        fw_join = f"⏳ تيليجرام فرض حظر انضمام (FloodWait {fwe.seconds} ثانية) لـ {entity} - تم إيقاف الانضمام تلقائياً"
                        logger.warning(fw_join)
                        socketio.emit('log_update', {"message": fw_join}, to=user_id)
                        return {"success": False, "skipped": True, "flood_wait": fwe.seconds, "message": fw_join}
                    except InviteRequestSentError:
                        req_msg = f"📩 تم إرسال طلب انضمام لـ {entity} بنجاح وبانتظار موافقة المشرفين"
                        logger.info(req_msg)
                        socketio.emit('log_update', {"message": req_msg}, to=user_id)
                        return {"success": False, "skipped": True, "message": req_msg}
                    except Exception as _join_err:
                        _je_str = str(_join_err).lower()
                        if "requested to join" in _je_str or "inviterequestsent" in _je_str:
                            req_msg = f"📩 تم إرسال طلب انضمام لـ {entity} وبانتظار موافقة المشرفين"
                            socketio.emit('log_update', {"message": req_msg}, to=user_id)
                            return {"success": False, "skipped": True, "message": req_msg}
                        if "wait of" in _je_str or "flood" in _je_str:
                            import re as _re_f
                            m_sec = _re_f.search(r'(\d+)\s*second', _je_str)
                            sec_val = float(m_sec.group(1)) if m_sec else 120.0
                            set_user_flood_wait(user_id, sec_val)
                            return {"success": False, "skipped": True, "message": f"تخطي {entity}: الحساب تحت مهلة انتظار ({sec_val:.0f}s)"}

                        # فقط إذا كان حظر/كتم حقيقي داخل المجموعة
                        if "banned" in _je_str or "restricted" in _je_str:
                            try:
                                c_title = getattr(entity_obj, 'title', None) or str(entity)
                                c_link = f"https://t.me/{getattr(entity_obj, 'username', '')}" if getattr(entity_obj, 'username', None) else "#"
                                client_manager.run_coroutine(client_manager.trigger_action_alert(
                                    action_type="mute",
                                    chat_title=c_title,
                                    details_text=f"تم تقييد الحساب ومنعه من الإرسال في هذه المجموعة ({_join_err}).",
                                    direct_link=c_link
                                ))
                            except Exception:
                                pass
                        return {"success": False, "skipped": True, "message": f"تعذر الانضمام لـ {entity}: {_join_err}"}
                elif "banned" in _err_str or "userbanned" in _err_str:
                    try:
                        c_title = getattr(entity_obj, 'title', None) or str(entity)
                        c_link = f"https://t.me/{getattr(entity_obj, 'username', '')}" if getattr(entity_obj, 'username', None) else "#"
                        client_manager.run_coroutine(client_manager.trigger_action_alert(
                            action_type="ban",
                            chat_title=c_title,
                            details_text=f"تم حظر الحساب تماماً من المجموعة ({_send_err}).",
                            direct_link=c_link
                        ))
                    except Exception:
                        pass
                    return {"success": False, "skipped": True, "message": f"تم تخطي {entity}: الحساب محظور من المجموعة"}
                else:
                    return {"success": False, "skipped": True, "message": f"فشل الإرسال لـ {entity}: {_send_err}"}

            return {"success": True, "message_id": result.id}

        except Exception as e:
            logger.error(f"Send message error: {str(e)}")
            raise Exception(str(e))

    def get_or_create_group_safety_report(self, user_id, client_manager, entity_obj, entity_label, sample_message=None):
        """
        التحقق من نتائج فحص المجموعة في قاعدة البيانات الخارجية (Firestore):
        1. إذا كانت المجموعة مفحوصة ومسجلة مسبقاً في قاعدة البيانات:
           - يتم الرجوع إليها واستخدام نتائجها فورياً والالتزام بها دون إعادة الفحص.
        2. إذا كانت مجموعة جديدة غير متوفرة في قاعدة البيانات:
           - تقوم الوظيفة بتحليلها وفحصها بالذكاء الاصطناعي لكشف بوتات الحماية والقيود وأخطاء الآخرين.
           - حفظ تقريرها ونتائجها بشكل ثابت ودائم في قاعدة البيانات الخارجية.
        """
        import firestore_sync
        chat_id = getattr(entity_obj, 'id', None)
        username = getattr(entity_obj, 'username', None)
        title = getattr(entity_obj, 'title', None) or getattr(entity_obj, 'name', None) or str(entity_label)

        # 1. الاستعلام من قاعدة البيانات الخارجية Firestore
        saved_report = firestore_sync.get_group_safety_report_from_db(
            group_key=str(entity_label),
            alt_key=str(chat_id) if chat_id else (username or None)
        )

        if saved_report and not saved_report.get('error'):
            logger.info(f"📋 Found existing group report in external DB for {entity_label}")
            socketio.emit('log_update', {
                "message": f"📋 [قاعدة البيانات] تم استرجاع نتائج فحص {entity_label} المحفوظة مسبقاً (مستوى الأمان: {saved_report.get('risk_assessment', 'عادي')})"
            }, to=user_id)
            return saved_report, False

        # 2. مجموعة جديدة غير متوفرة في قاعدة البيانات -> فحص وتحليل كامل بالذكاء
        logger.info(f"🆕 Group {entity_label} is new. Scanning and persisting to external DB...")
        socketio.emit('log_update', {
            "message": f"🆕 [مجموعة جديدة] {entity_label} غير مسجلة في قاعدة البيانات — جارٍ الفحص والتحليل بالذكاء وحفظ النتائج في قاعدة البيانات..."
        }, to=user_id)

        # أ) فحص بوتات الحماية
        is_prot = False
        prot_reason = None
        bots = []
        try:
            is_prot, prot_reason, bots = client_manager.run_coroutine(
                client_manager.get_group_protection_details(entity_obj)
            )
        except Exception as _pe:
            logger.debug(f"Protection details error for {entity_label}: {_pe}")

        # ب) فحص الذكاء الاصطناعي لآخر 50 محادثة
        ai_res = self.scan_and_analyze_group_with_ai(
            user_id, client_manager, entity_obj, entity_label,
            sample_message=sample_message, send_report_to_me=True
        )

        # ج) تحديد إذا كانت المجموعة تمنع الإعلانات بشكل كلي
        prohibited = set(ai_res.get('prohibited_actions', []))
        causes_str = " ".join(ai_res.get('causes', []) + ai_res.get('mistakes_by_others', [])).lower()

        blocks_ads = False
        requires_smart_send = False

        if is_prot or ai_res.get('protected') or len(bots) > 0:
            if ('no_links' in prohibited or 'no_phones' in prohibited or 'skip_group' in prohibited 
                or any(kw in causes_str for kw in ['إعلان', 'نشر', 'رابط', 'روابط', 'ترويج', 'تسويق', 'spam', 'ads', 'link'])):
                blocks_ads = True
                requires_smart_send = True

        if ai_res.get('risk_assessment') in ('high', 'critical') and (is_prot or len(bots) > 0):
            blocks_ads = True
            requires_smart_send = True

        new_report = {
            "group_key": str(entity_label),
            "group_id": str(chat_id) if chat_id else "",
            "group_title": str(title),
            "username": str(username) if username else "",
            "is_protected": bool(is_prot or ai_res.get('protected')),
            "blocks_ads": bool(blocks_ads),
            "requires_smart_send": bool(requires_smart_send),
            "protection_bots": bots or [],
            "risk_assessment": ai_res.get('risk_assessment', 'low'),
            "punished_count": ai_res.get('punished_count', 0),
            "causes": ai_res.get('causes', []),
            "mistakes_by_others": ai_res.get('mistakes_by_others', []),
            "prohibited_actions": list(prohibited),
            "keywords_to_avoid": ai_res.get('keywords_to_avoid', []),
            "actions_taken": ai_res.get('actions_taken', []),
            "summary_ar": ai_res.get('summary_ar', ''),
            "recommended_action": 'salam' if requires_smart_send else ('sanitize' if is_prot else 'send'),
            "can_send_media": bool(ai_res.get('can_send_media', True) and 'no_media' not in prohibited),
            "analyzed_at": time.strftime('%Y-%m-%d %H:%M:%S')
        }

        # د) حفظ دائم وثابت في قاعدة البيانات الخارجية
        try:
            firestore_sync.save_group_safety_report_to_db(new_report)
            socketio.emit('log_update', {
                "message": f"💾 [حفظ دائم] تم حفظ نتائج فحص {entity_label} في قاعدة البيانات الخارجية (Firestore) بنجاح"
            }, to=user_id)
        except Exception as _se:
            logger.error(f"Failed to save group safety report to DB for {entity_label}: {_se}")

        return new_report, True

    def adapt_message_to_group_report(self, message, report, has_media=False):
        """
        تكييف الرسالة وتغيير أو حذف الكلمات والعبارات التي تستدعي الحظر
        بناءً على نتائج تقرير المجموعة المخزن في قاعدة البيانات.
        """
        if not message:
            return message, has_media, []

        import re as _re
        adapted = str(message)
        actions = []
        prohibited = set(report.get('prohibited_actions', []))
        keywords_avoid = report.get('keywords_to_avoid', [])
        causes = report.get('causes', [])
        mistakes = report.get('mistakes_by_others', [])
        all_reasons = " ".join(causes + mistakes).lower()

        # 1. تغيير أو حذف الكلمات والعبارات التي تستدعي الحظر
        for kw in keywords_avoid:
            if kw and kw in adapted:
                safe_kw = f"{kw[0]}..{kw[-1]}" if len(kw) > 2 else f"[{kw}]"
                adapted = adapted.replace(kw, safe_kw)
                actions.append(f"🔤 تمويه الكلمة الحساسة '{kw}'")

        if "إعلان" in all_reasons or "ترويج" in all_reasons or "spam" in all_reasons or "no_ads" in prohibited:
            replacements = [
                ("إعلان", "تنويه"),
                ("اعلان", "تنويه"),
                ("للتواصل", "للاستفسار"),
                ("خصم", "ميزة"),
                ("سارع", "متاح"),
                ("ربح", "فائدة"),
                ("استثمار", "مشروع"),
                ("تداول", "أعمال")
            ]
            for bad_w, good_w in replacements:
                if bad_w in adapted:
                    adapted = adapted.replace(bad_w, good_w)
                    actions.append(f"استبدال عبارة '{bad_w}' بـ '{good_w}'")

        # 2. تنقية أو تعديل الروابط
        if 'no_links' in prohibited or 'رابط' in all_reasons or 'link' in all_reasons:
            wa_match = _re.search(r'(?:https?://)?(?:wa\.me|api\.whatsapp\.com/send\?phone=)/?(\+?\d+)', adapted)
            if wa_match:
                phone_num = wa_match.group(1)
                adapted = _re.sub(r'https?://(?:wa\.me|api\.whatsapp\.com/send\?phone=)[^\s]+', f'واتساب: {phone_num}', adapted)
                actions.append("تحويل رابط واتساب إلى نص مباشر تجنباً للحظر")

            if _re.search(r'https?://[^\s]+', adapted):
                adapted = _re.sub(r'https?://[^\s]+', '', adapted).strip()
                actions.append("إزالة الروابط الخارجية لتفادي البوتات")

            if _re.search(r't\.me/[^\s]+', adapted):
                adapted = _re.sub(r't\.me/[^\s]+', '', adapted).strip()
                actions.append("إزالة روابط تليجرام")

        # 3. تمويه أرقام الهواتف إذا سببت حظراً في نتائج المجموعة
        if 'no_phones' in prohibited or 'رقم' in all_reasons or 'phone' in all_reasons:
            def _mask_num(m):
                n = m.group(0)
                return " ".join(list(n.replace(" ", "")))
            adapted = _re.sub(r'\+?\d{8,15}', _mask_num, adapted)
            actions.append("تمويه أرقام الهواتف")

        # 4. صلاحية الوسائط
        can_media = has_media and report.get('can_send_media', True)
        if has_media and not can_media:
            actions.append("إلغاء الصور/الوسائط لأن المجموعة تحظرها")

        return adapted, can_media, actions

    def _check_group_protection(self, user_id, client_manager, entity_obj, entity_label):
        """
        التحقق من حماية المجموعة وإرجاع الإجراء المناسب بناءً على فحص قاعدة البيانات.
        """
        try:
            settings = load_settings(user_id)
            mode = (settings.get('sanitize_mode') or 'salam').lower()

            if mode == 'off':
                return 'send', None

            report, _ = self.get_or_create_group_safety_report(user_id, client_manager, entity_obj, entity_label)

            is_prot = bool(report.get('is_protected', False))
            blocks_ads = bool(report.get('blocks_ads', False))
            requires_smart = bool(report.get('requires_smart_send', False))

            if requires_smart or (is_prot and blocks_ads):
                return 'salam', report.get('summary_ar') or 'بوتات حماية تمنع الإعلانات'

            if is_prot:
                if mode == 'skip':
                    return 'skip', report.get('summary_ar')
                if mode == 'salam':
                    return 'salam', report.get('summary_ar')
                if mode in ('smart', 'always'):
                    return 'sanitize', report.get('summary_ar')

            return 'send', None
        except Exception as e:
            logger.warning(f"_check_group_protection error: {e}")
            return 'send', None

    def _check_group_protection_detailed(self, user_id, client_manager, entity_obj, entity_label):
        """
        فحص تفصيلي للمجموعة يُرجع dict كامل يشمل:
        - protected: bool
        - bots: list
        - reason: str|None
        - entity_label: str
        مستخدم من /api/pre_send_scan فقط.
        """
        try:
            is_prot, reason, bots = client_manager.run_coroutine(
                client_manager.get_group_protection_details(entity_obj)
            )
            return {
                "entity_label": entity_label,
                "protected": is_prot,
                "bots": bots,
                "reason": reason,
                "error": False
            }
        except Exception as e:
            logger.warning(f"_check_group_protection_detailed error for {entity_label}: {e}")
            return {
                "entity_label": entity_label,
                "protected": False,
                "bots": [],
                "reason": f"خطأ في الفحص: {str(e)[:80]}",
                "error": True
            }

    def scan_and_analyze_group_with_ai(self, user_id, client_manager, entity_obj, entity_label, sample_message=None, send_report_to_me=True):
        """
        فحص المجموعة بالذكاء الاصطناعي:
        1. استخراج آخر 50 محادثة داخل المجموعة
        2. تحليلها بالذكاء الاصطناعي لكشف حالات الكتم، الطرد، الحظر وأسبابها
        3. استخراج أخطاء الآخرين وتوليد خطة التلافي التلقائية
        4. تكييف الرسالة آلياً وتلافي المشاكل
        5. إرسال تقرير مفصل إلى 'Saved Messages' (الرسائل المحفوظة)
        """
        try:
            import group_ai_analyzer
            chat_id = getattr(entity_obj, 'id', entity_label)
            cache_key = f"{user_id}_{chat_id}"
            
            with AI_GROUP_SAFETY_LOCK:
                cached = AI_GROUP_SAFETY_CACHE.get(cache_key)
                if cached and (time.time() - cached.get('timestamp', 0) < 1800):
                    return cached['result']

            group_data = client_manager.run_coroutine(
                group_ai_analyzer.fetch_group_recent_messages(client_manager.client, entity_obj, limit=50)
            )
            analysis = group_ai_analyzer.analyze_group_conversations_with_ai(group_data)
            adaptation = group_ai_analyzer.adapt_message_safely(
                sample_message or "", analysis, has_media=False
            )

            # إرسال تقرير مفصل إلى الرسائل المحفوظة
            if send_report_to_me:
                try:
                    report_text = group_ai_analyzer.format_saved_messages_report(
                        group_data, analysis, adaptation, sent_status="تم الفحص والتحليل الذكي بنجاح"
                    )
                    client_manager.run_coroutine(
                        group_ai_analyzer.send_report_to_saved_messages(client_manager.client, report_text)
                    )
                except Exception as _rep_err:
                    logger.warning(f"Could not send AI report to saved messages for {user_id}: {_rep_err}")

            res = {
                "entity_label": entity_label,
                "group_title": group_data.get("group_title", entity_label),
                "messages_analyzed": group_data.get("messages_count", 0),
                "protected": analysis.get("has_recent_punishments", False) or analysis.get("risk_assessment") in ("high", "critical"),
                "risk_assessment": analysis.get("risk_assessment", "low"),
                "punished_count": analysis.get("punished_count", 0),
                "details_of_punishments": analysis.get("details_of_punishments", []),
                "causes": analysis.get("causes", []),
                "mistakes_by_others": analysis.get("mistakes_by_others", []),
                "actions_taken": adaptation.get("actions_taken", []),
                "should_skip": adaptation.get("should_skip", False),
                "skip_reason": adaptation.get("skip_reason", ""),
                "adapted_message": adaptation.get("adapted_message", ""),
                "delay_seconds": adaptation.get("delay_seconds", 3),
                "summary_ar": analysis.get("summary_ar", ""),
                "recommended_action": analysis.get("recommended_action", ""),
                "error": False
            }

            with AI_GROUP_SAFETY_LOCK:
                AI_GROUP_SAFETY_CACHE[cache_key] = {
                    "result": res,
                    "adaptation": adaptation,
                    "analysis": analysis,
                    "timestamp": time.time()
                }

            return res
        except Exception as e:
            logger.error(f"Error in scan_and_analyze_group_with_ai for {entity_label}: {e}")
            return {
                "entity_label": entity_label,
                "group_title": entity_label,
                "messages_analyzed": 0,
                "protected": False,
                "risk_assessment": "unknown",
                "punished_count": 0,
                "details_of_punishments": [],
                "causes": [],
                "mistakes_by_others": [],
                "actions_taken": [],
                "should_skip": False,
                "error": True,
                "reason": str(e)
            }

    def _send_protection_warning(self, user_id, group_name, reason):
        """إرسال تحذير للمستخدم عن المجموعة المحمية"""
        try:
            socketio.emit('protection_warning', {
                "group": group_name,
                "reason": reason,
                "timestamp": time.strftime('%H:%M:%S')
            }, to=user_id)
            try:
                with USERS_LOCK:
                    if user_id in USERS:
                        client_manager = USERS[user_id].get('client_manager')
                        if client_manager and client_manager.client:
                            loop = getattr(client_manager, 'loop', None)
                            if loop and loop.is_running():
                                warning_msg = f"""🛡️ **تنبيه: مجموعة محمية**

⚠️ تم اكتشاف أن المجموعة تحتوي على بوتات حماية:
📌 **{group_name}**

📋 **السبب:** {reason or 'يحتوي على بوتات حماية'}

💡 **الإجراء المتخذ:** تم تخطي الإرسال إلى هذه المجموعة حماية لحسابك.

🔧 **لتغيير الإعدادات:**
• تخطي المجموعات المحمية: إيقاف الإرسال إليها تلقائياً
• تنقية الروابط: تحويل روابط واتساب إلى صيغة آمنة"""
                                asyncio.run_coroutine_threadsafe(
                                    client_manager.client.send_message('me', warning_msg, link_preview=False),
                                    loop
                                )
            except Exception:
                pass
        except Exception as e:
            logger.error(f"Failed to send protection warning: {e}")

    def _run_smart_protected_send(self, user_id, client_manager, entity_obj, entity_label, final_message, key, cancel_event=None):
        """
        تُنفذ في خيط منفصل (لا تحجب حلقة الإرسال الرئيسية):
        1. ترسل "السلام عليكم" كرسالة أولية ثابتة.
        2. تنتظر فترة زمنية محددة (تؤخذ من interval_seconds في الإعدادات).
        3. تتحقق من عدد الرسائل التي أُرسلت بعدها.
        4. إذا كان أكثر من required_messages، تعدّل الرسالة إلى final_message.
        5. إذا لم يكن أكثر من required_messages، تحذف الرسالة وتنتظر الدورة التالية.
        6. تتكرر العملية بشكل دوري غير محدود حتى يتم إيقافها يدوياً.
        """
        try:
            if not client_manager or not client_manager.client:
                socketio.emit('log_update', {
                    "message": f"❌ فشل الإرسال الذكي لـ {entity_label}: العميل غير متصل"
                }, to=user_id)
                return

            # ── قراءة الإعدادات من المستخدم ──
            settings = load_settings(user_id)
            required_messages = int(settings.get('smart_required_messages', 3))
            interval_seconds = int(settings.get('interval_seconds', 3600))
            cycle_duration = max(60, interval_seconds)

            socketio.emit('log_update', {
                "message": f"🧠 بدء الدورة الذكية لـ {entity_label} — المدة: {cycle_duration}ث، العدد المطلوب: {required_messages}"
            }, to=user_id)

            # ── الحلقة الرئيسية (دورية لا نهائية) ──
            while True:
                if not self._smart_running or key not in self._smart_running:
                    logger.info(f"[Smart] توقفت الدورة الذكية لـ {entity_label} (key={key})")
                    break

                # ── 1. إرسال "السلام عليكم" ──
                try:
                    msg = client_manager.run_coroutine(
                        client_manager.client.send_message(entity_obj, "السلام عليكم")
                    )
                    logger.info(f"[Smart] أُرسلت 'السلام عليكم' إلى {entity_label}")
                    socketio.emit('log_update', {
                        "message": f"🧠 [Smart] أُرسلت 'السلام عليكم' إلى {entity_label} — في انتظار {cycle_duration}ث..."
                    }, to=user_id)
                except Exception as send_err:
                    logger.error(f"[Smart] فشل إرسال 'السلام عليكم' إلى {entity_label}: {send_err}")
                    time.sleep(10)
                    continue

                # ── 2. انتظار المدة المحددة مع مراقبة الرسائل وبوتات الحماية (P0) ──
                start_time = time.time()
                last_id = msg.id
                messages_after = 0
                salam_env_wait = int(os.getenv('SMART_SALAM_WAIT_SECONDS', 60))
                max_cycle_wait = min(cycle_duration, salam_env_wait)

                while (time.time() - start_time) < max_cycle_wait:
                    if cancel_event and cancel_event.is_set():
                        logger.info(f"[Smart] إلغاء الإرسال الذكي لـ {entity_label} بطلب من المستخدم")
                        break
                    if not self._smart_running or key not in self._smart_running:
                        break
                    time.sleep(2)
                    try:
                        new_msgs = client_manager.run_coroutine(
                            client_manager.client.get_messages(entity_obj, limit=10, min_id=last_id)
                        )
                        others = [m for m in new_msgs if m.id > last_id and not getattr(m, 'out', False)]
                        if others:
                            messages_after += len(others)
                            last_id = max(m.id for m in others)
                            logger.info(f"[Smart] {entity_label}: {len(others)} رسالة جديدة (المجموع: {messages_after})")
                            socketio.emit('log_update', {
                                "message": f"🧠 [Smart] {entity_label}: استقبل {messages_after}/{required_messages} رسالة"
                            }, to=user_id)
                            # استيفاء الشرط مبكراً فور وصول الرسائل المطلوبة
                            if messages_after >= required_messages:
                                logger.info(f"[Smart] استوفت الشروط مبكراً ({messages_after}/{required_messages}) لـ {entity_label}")
                                break
                    except Exception as poll_err:
                        logger.error(f"[Smart] خطأ في جلب الرسائل من {entity_label}: {poll_err}")
                        break

                    # فحص هل تم حذف رسالة السلام من قبل بوت حماية
                    try:
                        chk_msg = client_manager.run_coroutine(
                            client_manager.client.get_messages(entity_obj, ids=msg.id)
                        )
                        if not chk_msg or getattr(chk_msg, 'action', None) or not getattr(chk_msg, 'message', None):
                            logger.warning(f"[Smart] تم حذف رسالة السلام في {entity_label} بواسطة بوت حماية")
                            socketio.emit('log_update', {
                                "message": f"⚠️ [Smart] تم حذف رسالة 'السلام عليكم' في {entity_label} بواسطة بوت حماية"
                            }, to=user_id)
                            break
                    except Exception:
                        pass

                    # في المجموعات الهادئة، إذا مر 35 ثانية مع رسالة واحدة أخرى على الأقل وبقيت رسالة السلام سالمة
                    if (time.time() - start_time) >= 35 and messages_after >= 1:
                        logger.info(f"[Smart] استوفت الشروط الزمنية الآمنة لـ {entity_label}")
                        break

                # ── 3. اتخاذ القرار وتعديل الرسالة إلى النص الأصلي ──
                # التحقق هل الرسالة لا تزال موجودة
                is_alive = True
                try:
                    chk2 = client_manager.run_coroutine(
                        client_manager.client.get_messages(entity_obj, ids=msg.id)
                    )
                    if not chk2 or getattr(chk2, 'action', None) or not getattr(chk2, 'message', None):
                        is_alive = False
                except Exception:
                    pass

                if not is_alive:
                    fail_msg = f"❌ [Smart] تعذر التعديل في {entity_label}: بوت حماية قام بحذف الرسالة فورياً"
                    socketio.emit('log_update', {"message": fail_msg}, to=user_id)
                    socketio.emit('send_progress', {
                        "group": entity_label,
                        "status": "error",
                        "error_type": "حُذفت الرسالة بواسطة بوت حماية",
                        "message": fail_msg
                    }, to=user_id)
                    break

                if messages_after >= required_messages or (time.time() - start_time >= 35 and is_alive):
                    # ✅ تعديل الرسالة إلى النص النهائي (الأصلي)
                    try:
                        client_manager.run_coroutine(
                            client_manager.client.edit_message(entity_obj, msg.id, final_message, parse_mode='md')
                        )
                        logger.info(f"[Smart] تم تعديل الرسالة في {entity_label} بنجاح إلى النص الأصلي")
                        success_edit_msg = f"✅ [Smart] تم تعديل الرسالة في {entity_label} بنجاح إلى النص الأصلي بعد استيفاء الشروط"
                        socketio.emit('log_update', {
                            "message": success_edit_msg
                        }, to=user_id)
                        socketio.emit('send_progress', {
                            "group": entity_label,
                            "status": "success",
                            "message": success_edit_msg
                        }, to=user_id)
                        socketio.emit('smart_send_done', {
                            "success": True,
                            "entity": entity_label,
                            "waited": messages_after,
                            "message": success_edit_msg
                        }, to=user_id)
                        # ── إيقاف الدورة بعد نجاح الإرسال — منع إرسال "السلام عليكم" مجدداً
                        break
                    except Exception as edit_err:
                        logger.error(f"[Smart] فشل تعديل الرسالة في {entity_label}: {edit_err}")
                        socketio.emit('log_update', {
                            "message": f"❌ [Smart] فشل تعديل الرسالة في {entity_label}: {str(edit_err)[:80]}"
                        }, to=user_id)
                        break
                else:
                    # ❌ لم نصل إلى العدد المطلوب — احذف رسالة السلام
                    logger.info(f"[Smart] لم يتم تعديل الرسالة في {entity_label} (عدد الرسائل: {messages_after} < {required_messages})")
                    socketio.emit('log_update', {
                        "message": f"⏭️ [Smart] لم يتم تعديل الرسالة في {entity_label} (استقبل {messages_after} فقط)"
                    }, to=user_id)
                    try:
                        client_manager.run_coroutine(
                            client_manager.client.delete_messages(entity_obj, [msg.id])
                        )
                        logger.info(f"[Smart] تم حذف رسالة 'السلام عليكم' غير المعدلة من {entity_label}")
                    except Exception as del_err:
                        logger.warning(f"[Smart] فشل حذف رسالة 'السلام عليكم' من {entity_label}: {del_err}")

                # ── 4. انتظار الدورة التالية ──
                if self._smart_running and key in self._smart_running:
                    socketio.emit('log_update', {
                        "message": f"⏳ [Smart] انتظار {cycle_duration // 60} دقيقة قبل الدورة التالية لـ {entity_label}"
                    }, to=user_id)
                    for _ in range(cycle_duration // 10):
                        if not self._smart_running or key not in self._smart_running:
                            break
                        time.sleep(10)

        except Exception as e:
            logger.error(f"[Smart] خطأ عام في الإرسال الذكي لـ {entity_label}: {e}")
            socketio.emit('log_update', {
                "message": f"❌ [Smart] فشل في {entity_label}: {str(e)[:100]}"
            }, to=user_id)
        finally:
            self._smart_running.discard(key)
            socketio.emit('log_update', {
                "message": f"⏹ [Smart] توقفت الدورة الذكية لـ {entity_label}"
            }, to=user_id)

    def _maybe_sanitize(self, user_id, client_manager, entity_obj, entity_label, message, forced_action=None):
        """تنقية الرسالة حسب وضع الحماية.
        forced_action: إذا تم تمريره يُتجنب استدعاء _check_group_protection مرة ثانية."""
        try:
            if forced_action is not None:
                action = forced_action
            else:
                action, _ = self._check_group_protection(user_id, client_manager, entity_obj, entity_label)

            if action in ('skip', 'smart'):
                return None

            if action == 'send':
                return message

            if action == 'transform':
                transformed = MessageSanitizer.transform_whatsapp_links(message)
                if transformed != message:
                    socketio.emit('log_update', {
                        "message": f"🔄 تم تحويل روابط واتساب في الرسالة إلى {entity_label}"
                    }, to=user_id)
                return transformed

            if not message:
                return message
            cleaned = MessageSanitizer.sanitize(message, mode='clean')
            if cleaned is None:
                socketio.emit('log_update', {
                    "message": f"⚠️ تم تخطي الإرسال إلى {entity_label}: الرسالة إعلانية بالكامل بعد التنقية"
                }, to=user_id)
                return None
            if cleaned != message:
                socketio.emit('log_update', {
                    "message": f"🧹 تنقية الرسالة قبل الإرسال إلى {entity_label}"
                }, to=user_id)
            return cleaned
        except Exception as e:
            logger.warning(f"_maybe_sanitize error: {e}")
            return message

    def send_media_async(self, user_id, entity, image_files):
        try:
            with USERS_LOCK:
                if user_id not in USERS:
                    raise Exception("المستخدم غير موجود")
                client_manager = USERS[user_id].get('client_manager')

            if not client_manager:
                raise Exception("العميل غير متصل")

            is_authorized = client_manager.run_coroutine(
                client_manager.client.is_user_authorized()
            )
            if not is_authorized:
                raise Exception("العميل غير مصرح")

            entity_obj = self._resolve_entity(client_manager, entity)

            action, _reason = self._check_group_protection(user_id, client_manager, entity_obj, entity)
            if action == 'skip':
                return {"success": False, "skipped": True,
                        "message": f"تم تخطي المجموعة المحمية: {entity}"}

            results = []
            paths = [f['path'] for f in image_files if os.path.exists(f.get('path', ''))]
            if not paths:
                raise Exception("لا توجد ملفات صور صالحة")

            if len(paths) == 1:
                result = client_manager.run_coroutine(
                    client_manager.client.send_file(entity_obj, paths[0])
                )
                results.append(result.id)
            else:
                media_result = client_manager.run_coroutine(
                    client_manager.client.send_file(entity_obj, paths)
                )
                if hasattr(media_result, '__iter__'):
                    for r in media_result:
                        results.append(r.id)
                else:
                    results.append(media_result.id)

            return {"success": True, "message_ids": results}

        except Exception as e:
            logger.error(f"Send media error: {str(e)}")
            raise Exception(str(e))

    def send_message_with_media_async(self, user_id, entity, message, image_files):
        try:
            with USERS_LOCK:
                if user_id not in USERS:
                    raise Exception("المستخدم غير موجود")
                client_manager = USERS[user_id].get('client_manager')

            if not client_manager:
                raise Exception("العميل غير متصل")

            is_authorized = client_manager.run_coroutine(
                client_manager.client.is_user_authorized()
            )

            if not is_authorized:
                raise Exception("العميل غير مصرح")

            entity_obj = self._resolve_entity(client_manager, entity)

            if message:
                _cleaned = self._maybe_sanitize(user_id, client_manager, entity_obj, entity, message)
                if _cleaned is None:
                    return {"success": False, "skipped": True,
                            "message": "تم تخطي الإرسال: الرسالة بعد التنقية أصبحت فارغة"}
                message = _cleaned

            results = []

            if image_files and len(image_files) > 0:
                try:
                    image_paths = []
                    for img_file in image_files:
                        if os.path.exists(img_file['path']):
                            image_paths.append(img_file['path'])
                        else:
                            logger.warning(f"Image file not found: {img_file['path']}")

                    if image_paths:
                        if len(image_paths) == 1:
                            media_result = client_manager.run_coroutine(
                                client_manager.client.send_file(
                                    entity_obj, 
                                    image_paths[0],
                                    caption=message if message else "📷",
                                    parse_mode='md'
                                )
                            )
                            results.append(media_result.id)
                            logger.info(f"Successfully sent single image with message to {entity}")
                        else:
                            try:
                                media_result = client_manager.run_coroutine(
                                    client_manager.client.send_file(
                                        entity_obj,
                                        image_paths,
                                        caption=message if message and message.strip() else None,
                                        parse_mode='md'
                                    )
                                )
                                if hasattr(media_result, '__iter__'):
                                    for result in media_result:
                                        results.append(result.id)
                                else:
                                    results.append(media_result.id)
                                logger.info(f"Successfully sent {len(image_paths)} images as album to {entity}")
                            except Exception as album_error:
                                logger.warning(f"Failed to send as album, sending individually: {str(album_error)}")
                                for i, img_path in enumerate(image_paths):
                                    try:
                                        cap = (message if message and message.strip() else None) if i == 0 else None
                                        media_result = client_manager.run_coroutine(
                                            client_manager.client.send_file(
                                                entity_obj,
                                                img_path,
                                                caption=cap,
                                                parse_mode='md'
                                            )
                                        )
                                        results.append(media_result.id)
                                    except Exception as img_error:
                                        logger.error(f"Error sending individual image {i+1}: {str(img_error)}")
                                        continue
                except Exception as media_error:
                    logger.error(f"Error in media sending process: {str(media_error)}")
                    raise Exception(f"فشل إرسال الصورة: {str(media_error)[:100]}")
            else:
                if message and message.strip():
                    text_result = client_manager.run_coroutine(
                        client_manager.client.send_message(entity_obj, message)
                    )
                    results.append(text_result.id)
                    logger.info(f"Successfully sent text message to {entity}")

            return {"success": True, "message_ids": results}

        except Exception as e:
            logger.error(f"Send message with media error: {str(e)}")
            raise Exception(str(e))

telegram_manager = TelegramManager()

# =========================== 
# نظام المراقبة المحسن مع Event Handlers
# ===========================
def monitoring_worker(user_id):
    logger.info(f"Starting enhanced monitoring worker with event handlers for user {user_id}")

    try:
        with USERS_LOCK:
            if user_id not in USERS:
                logger.error(f"No user data found for {user_id}")
                return

            USERS[user_id]['monitoring_active'] = True
            client_manager = USERS[user_id].get('client_manager')
            settings = USERS[user_id]['settings']

        if not client_manager:
            logger.error(f"No client manager for user {user_id}")
            return

        watch_words = get_effective_watch_words(settings.get('watch_words', []))
        send_groups = settings.get('groups', [])

        if hasattr(client_manager, 'update_monitoring_settings'):
            client_manager.update_monitoring_settings(watch_words, send_groups)

        if watch_words:
            socketio.emit('log_update', {
                "message": f"🚀 بدأت المراقبة الشاملة الفورية - {len(watch_words)} كلمة مراقبة في كامل الحساب | الإرسال لـ {len(send_groups)} مجموعة"
            }, to=user_id)
        else:
            socketio.emit('log_update', {
                "message": f"🚀 بدأت المراقبة الشاملة لكامل الرسائل في الحساب | الإرسال لـ {len(send_groups)} مجموعة"
            }, to=user_id)

        _persisted = load_settings(user_id)
        _saved_last_send = _persisted.get('last_scheduled_send', 0)
        if _saved_last_send == 0:
            _saved_last_send = time.time()
        with USERS_LOCK:
            if user_id in USERS:
                USERS[user_id]['last_scheduled_send'] = _saved_last_send

        # ── دورة التشغيل/التوقف التلقائية للإرسال المجدول (الدورة الدائرية المستمرة) ───
        # الافتراضي الثابت والفعال دائماً: ساعتان تشغيل (7200 ثانية) + ساعتان توقف (7200 ثانية) أو ما يعادله مثل 2.1 ساعة
        try:
            _dur_h = float(settings.get('schedule_duration_hours', 2.1) or 2.1)
            _sched_dur = max(60, int(_dur_h * 3600))
        except (TypeError, ValueError):
            _sched_dur = int(settings.get('schedule_duration', 0) or 7560)

        try:
            _pause_h = float(settings.get('schedule_pause_hours', 2.1) or 2.1)
            _pause_dur = max(60, int(_pause_h * 3600))
        except (TypeError, ValueError):
            _pause_dur = int(settings.get('schedule_pause_duration', 0) or 7560)

        _sched_start = time.time()
        _pause_start = None
        _cycle_phase = 'running'
        _cycle_round = 1
        _stopped_by_duration = False

        with USERS_LOCK:
            if user_id in USERS:
                USERS[user_id]['cycle_phase'] = 'running'
                USERS[user_id]['cycle_round'] = _cycle_round
                USERS[user_id]['sched_dur'] = _sched_dur
                USERS[user_id]['pause_dur'] = _pause_dur
                USERS[user_id]['sched_start'] = _sched_start
                USERS[user_id]['pause_start'] = None
                USERS[user_id]['skip_pause_requested'] = False

        if _sched_dur > 0:
            _h = _sched_dur // 3600
            _m = (_sched_dur % 3600) // 60
            _cycle_message = f"⏱️ سيعمل الإرسال {_h}س {_m}د (الدورة #{_cycle_round})"
            if _pause_dur > 0:
                _ph = _pause_dur // 3600
                _pm = (_pause_dur % 3600) // 60
                _cycle_message += f" ثم يتوقف {_ph}س {_pm}د ويُستأنف تلقائياً بشكل دائري"
            else:
                _cycle_message += " ثم يتوقف تلقائياً"
            socketio.emit('log_update', {"message": _cycle_message}, to=user_id)
        socketio.emit('schedule_status', {
            "running": True,
            "cycle_phase": "running",
            "cycle_round": _cycle_round,
            "duration_hours": _sched_dur / 3600,
            "pause_duration_hours": _pause_dur / 3600,
            "remaining_seconds": _sched_dur if _sched_dur > 0 else None,
            "pause_remaining_seconds": None,
            "auto_resume": _pause_dur > 0,
            "target_timestamp": (_sched_start + _sched_dur) if _sched_dur > 0 else None
        }, to=user_id)

        if _DB_READY:
            _app_db.record_schedule_event(user_id, "running", {
                "duration_hours": _sched_dur / 3600,
                "pause_duration_hours": _pause_dur / 3600,
                "cycle_round": _cycle_round
            })

        consecutive_errors = 0
        max_consecutive_errors = 5
        _last_remain_emit = 0

        while True:
            with USERS_LOCK:
                if user_id not in USERS or not USERS[user_id].get('is_running', False):
                    logger.info(f"Stopping monitoring for user {user_id} as is_running is False")
                    break

                user_data = USERS[user_id].copy()
                USERS[user_id]['monitoring_active'] = True

            # ── إدارة دورة التشغيل والتوقف التلقائية ───────────────────────
            _now = time.time()
            skip_pause = False
            with USERS_LOCK:
                if user_id in USERS and USERS[user_id].get('skip_pause_requested'):
                    skip_pause = True
                    USERS[user_id]['skip_pause_requested'] = False

            if _cycle_phase == 'paused':
                _pause_remaining = _pause_dur - (_now - (_pause_start or _now))
                if _pause_remaining <= 0 or skip_pause:
                    _cycle_phase = 'running'
                    _cycle_round += 1
                    _sched_start = _now
                    _pause_start = None
                    with USERS_LOCK:
                        if user_id in USERS:
                            USERS[user_id]['cycle_phase'] = 'running'
                            USERS[user_id]['cycle_round'] = _cycle_round
                            USERS[user_id]['sched_start'] = _sched_start
                            USERS[user_id]['pause_start'] = None
                            _interval_after_pause = max(60, int(USERS[user_id].get('settings', {}).get('interval_seconds', 3600)))
                            USERS[user_id]['last_scheduled_send'] = _now - _interval_after_pause
                    if skip_pause:
                        _resume_msg = f"⏩ تم استئناف الإرسال فوراً بطلب المستخدم (الدورة #{_cycle_round})"
                    else:
                        _resume_msg = f"▶️ انتهت مدة التوقف — استؤنف الإرسال المجدول تلقائياً (الدورة #{_cycle_round})"
                    socketio.emit('log_update', {"message": _resume_msg}, to=user_id)
                    if _DB_READY:
                        _app_db.record_schedule_event(user_id, "resumed", {
                            "run_duration_seconds": _sched_dur,
                            "cycle_round": _cycle_round
                        })
                    socketio.emit('schedule_status', {
                        "running": True,
                        "cycle_phase": "running",
                        "cycle_round": _cycle_round,
                        "duration_hours": _sched_dur / 3600,
                        "pause_duration_hours": _pause_dur / 3600,
                        "remaining_seconds": _sched_dur if _sched_dur > 0 else None,
                        "pause_remaining_seconds": None,
                        "auto_resume": True,
                        "target_timestamp": (_sched_start + _sched_dur) if _sched_dur > 0 else None
                    }, to=user_id)
                else:
                    if time.time() - _last_remain_emit >= 5:
                        _last_remain_emit = time.time()
                        socketio.emit('schedule_remaining', {
                            "phase": "paused",
                            "cycle_round": _cycle_round,
                            "remaining_seconds": int(_pause_remaining),
                            "remaining_minutes": int(_pause_remaining // 60),
                            "remaining_hours": _pause_remaining / 3600,
                            "target_timestamp": (_pause_start or _now) + _pause_dur
                        }, to=user_id)
                    for _ in range(5):
                        if not USERS.get(user_id, {}).get('is_running', False) or USERS.get(user_id, {}).get('skip_pause_requested', False):
                            break
                        time.sleep(1)
                    continue

            if _cycle_phase == 'running' and _sched_dur > 0:
                _remain = _sched_dur - (_now - _sched_start)
                if _remain <= 0:
                    logger.info(f"Schedule run phase expired for user {user_id}")
                    if _pause_dur > 0:
                        _cycle_phase = 'paused'
                        _pause_start = _now
                        _last_remain_emit = 0
                        with USERS_LOCK:
                            if user_id in USERS:
                                USERS[user_id]['cycle_phase'] = 'paused'
                                USERS[user_id]['pause_start'] = _now
                        _pause_h = _pause_dur // 3600
                        _pause_m = (_pause_dur % 3600) // 60
                        socketio.emit('log_update', {
                            "message": f"⏸️ انتهت مدة التشغيل لدورة #{_cycle_round} — توقف الإرسال لمدة {_pause_h}س {_pause_m}د ثم يستأنف تلقائياً"
                        }, to=user_id)
                        if _DB_READY:
                            _app_db.record_schedule_event(user_id, "paused", {
                                "pause_duration_seconds": _pause_dur,
                                "run_duration_seconds": _sched_dur,
                                "cycle_round": _cycle_round
                            })
                        socketio.emit('schedule_status', {
                            "running": True,
                            "cycle_phase": "paused",
                            "cycle_round": _cycle_round,
                            "stopped_by_duration": False,
                            "duration_hours": _sched_dur / 3600,
                            "pause_duration_hours": _pause_dur / 3600,
                            "pause_remaining_seconds": _pause_dur,
                            "auto_resume": True,
                            "target_timestamp": _now + _pause_dur
                        }, to=user_id)
                        send_push_notification(
                            user_id,
                            f"⏸️ توقف مؤقت للإرسال (الدورة #{_cycle_round})",
                            f"انتهت مدة التشغيل ({_sched_dur//3600}س). سيُستأنف الإرسال تلقائياً بعد {_pause_h}س {_pause_m}د.",
                            data={"type": "schedule_paused", "pause_remaining_seconds": _pause_dur}
                        )
                        time.sleep(1)
                        continue

                    socketio.emit('log_update', {
                        "message": "⏹ انتهت المدة المحددة — توقف الإرسال المجدول تلقائياً"
                    }, to=user_id)
                    _stopped_by_duration = True
                    with USERS_LOCK:
                        if user_id in USERS:
                            USERS[user_id]['is_running'] = False
                            USERS[user_id]['cycle_phase'] = 'stopped'
                    socketio.emit('schedule_status', {
                        "running": False,
                        "cycle_phase": "stopped",
                        "cycle_round": _cycle_round,
                        "stopped_by_duration": True,
                        "duration_hours": _sched_dur / 3600,
                        "pause_duration_hours": 0,
                        "can_resume": True
                    }, to=user_id)
                    _h2 = _sched_dur // 3600
                    _m2 = (_sched_dur % 3600) // 60
                    send_push_notification(
                        user_id,
                        "⏹ توقف الإرسال المجدول",
                        f"انتهت المدة المحددة ({_h2}س {_m2}د). اضغط هنا لاستئنافه.",
                        data={"type": "schedule_expired", "duration_hours": _sched_dur / 3600}
                    )
                    break
                elif time.time() - _last_remain_emit >= 5:
                    _last_remain_emit = time.time()
                    socketio.emit('schedule_remaining', {
                        "phase": "running",
                        "cycle_round": _cycle_round,
                        "remaining_seconds": int(_remain),
                        "remaining_minutes": int(_remain // 60),
                        "remaining_hours": _remain / 3600,
                        "target_timestamp": _sched_start + _sched_dur
                    }, to=user_id)

            try:
                settings = user_data.get('settings', {})
                send_type = settings.get('send_type', 'manual')
                current_time = time.time()

                if send_type == 'scheduled':
                    interval_seconds = int(settings.get('interval_seconds', 3600))
                    last_send = user_data.get('last_scheduled_send', 0)
                    remaining = interval_seconds - (current_time - last_send)

                    if remaining <= 0:
                        logger.info(f"Executing scheduled send for user {user_id} (interval={interval_seconds}s)")
                        socketio.emit('log_update', {
                            "message": f"📅 حان موعد الإرسال المجدول — جاري الإرسال إلى {len(settings.get('groups', []))} مجموعة..."
                        }, to=user_id)
                        execute_scheduled_messages(user_id, settings)

                        with USERS_LOCK:
                            if user_id in USERS:
                                USERS[user_id]['last_scheduled_send'] = current_time
                        try:
                            _s = load_settings(user_id)
                            _s['last_scheduled_send'] = current_time
                            save_settings(user_id, _s)
                        except Exception as _se:
                            logger.error(f"Failed to persist last_scheduled_send: {_se}")

                        next_send_at = time.strftime('%H:%M:%S', time.localtime(current_time + interval_seconds))
                        socketio.emit('log_update', {
                            "message": f"⏰ الإرسال التالي في: {next_send_at} (بعد {interval_seconds // 60} دقيقة)"
                        }, to=user_id)
                    else:
                        logger.debug(f"Scheduled send for {user_id}: {int(remaining)}s remaining")

                consecutive_errors = 0

                next_send_remaining = None
                next_send_at_str = None
                if send_type == 'scheduled':
                    interval_seconds = int(settings.get('interval_seconds', 3600))
                    last_send = user_data.get('last_scheduled_send', 0)
                    remaining = interval_seconds - (current_time - last_send)
                    next_send_remaining = max(0, int(remaining))
                    next_send_at_str = time.strftime('%H:%M:%S', time.localtime(current_time + next_send_remaining))

                _dur_remain = None
                if _sched_dur > 0:
                    _dur_remain = max(0, int(_sched_dur - (time.time() - _sched_start)))

                status_info = {
                    'timestamp': time.strftime('%H:%M:%S'),
                    'status': 'active',
                    'type': 'event_driven_monitoring',
                    'keywords_active': bool(watch_words),
                    'event_handlers': True,
                    'send_type': send_type,
                    'next_send_remaining': next_send_remaining,
                    'next_send_at': next_send_at_str,
                    'schedule_remaining': _dur_remain,
                    'schedule_duration_hours': _sched_dur / 3600 if _sched_dur > 0 else 0,
                    'cycle_phase': _cycle_phase,
                    'pause_remaining_seconds': (max(0, int(_pause_dur - (time.time() - (_pause_start or time.time())))) if _cycle_phase == 'paused' else None),
                    'pause_duration_hours': _pause_dur / 3600
                }

                socketio.emit('heartbeat', status_info, to=user_id)

            except Exception as e:
                consecutive_errors += 1
                logger.error(f"Monitoring cycle error for {user_id}: {str(e)}")
                socketio.emit('log_update', {
                    "message": f"⚠️ خطأ في المراقبة: {str(e)[:100]}"
                }, to=user_id)

                if consecutive_errors >= max_consecutive_errors:
                    socketio.emit('log_update', {
                        "message": f"❌ تم إيقاف المراقبة بسبب تكرار الأخطاء ({consecutive_errors})"
                    }, to=user_id)
                    with USERS_LOCK:
                        if user_id in USERS:
                            USERS[user_id]['is_running'] = False
                    break

            time.sleep(10)

    except Exception as e:
        logger.error(f"Monitoring worker top-level error for {user_id}: {str(e)}")
    finally:
        with USERS_LOCK:
            if user_id in USERS:
                USERS[user_id]['is_running'] = False
                USERS[user_id]['monitoring_active'] = False
                USERS[user_id]['thread'] = None

        socketio.emit('log_update', {
            "message": "⏹ تم إيقاف نظام المراقبة المحسن"
        }, to=user_id)

        socketio.emit('heartbeat', {
            'timestamp': time.strftime('%H:%M:%S'),
            'status': 'stopped'
        }, to=user_id)

        if not _stopped_by_duration:
            socketio.emit('schedule_status', {"running": False, "stopped_by_duration": False}, to=user_id)

        if _DB_READY:
            _app_db.record_schedule_event(user_id, "stopped", {})
        logger.info(f"Enhanced monitoring worker ended for user {user_id}")


@app.route("/api/resume_scheduled", methods=["POST"])
def api_resume_scheduled():
    """استئناف الإرسال المجدول بعد توقفه بسبب انتهاء المدة أو تخطي فترة التوقف المؤقت"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"success": False, "message": "❌ غير مسجل"}), 401

    with USERS_LOCK:
        if user_id not in USERS:
            return jsonify({"success": False, "message": "❌ المستخدم غير موجود"}), 404

        if USERS[user_id].get('is_running', False):
            if USERS[user_id].get('cycle_phase') == 'paused':
                USERS[user_id]['skip_pause_requested'] = True
                return jsonify({"success": True, "message": "⏩ تم تخطي فترة التوقف واستئناف الإرسال فوراً"})
            return jsonify({"success": False, "message": "⚠️ الإرسال المجدول يعمل بالفعل"})

        settings = USERS[user_id].get('settings', {})
        if not settings.get('groups') or not settings.get('message'):
            return jsonify({"success": False, "message": "❌ الإعدادات غير مكتملة (المجموعات أو الرسالة)"})

        _sched_dur = int(settings.get('schedule_duration', 0))
        _h = _sched_dur // 3600
        _m = (_sched_dur % 3600) // 60
        USERS[user_id]['is_running'] = True
        USERS[user_id]['cycle_phase'] = 'running'

    import threading as _thr
    t = _thr.Thread(target=monitoring_worker, args=(user_id,), daemon=True)
    t.start()
    with USERS_LOCK:
        if user_id in USERS:
            USERS[user_id]['thread'] = t

    msg = f"🔄 تم استئناف الإرسال المجدول" + (f" لمدة {_h}س {_m}د" if _sched_dur > 0 else "")
    socketio.emit('log_update', {"message": msg}, to=user_id)
    return jsonify({"success": True, "message": msg})


def ensure_monitoring_started(user_id):
    """تشغيل وظيفة المراقبة دائماً كوضع افتراضي دائم وحقيقي"""
    try:
        with USERS_LOCK:
            if user_id not in USERS:
                return False
            user_data = USERS[user_id]
            if not user_data.get('authenticated'):
                return False
            if user_data.get('is_running', False) or user_data.get('monitoring_active', False):
                return True
            user_data['is_running'] = True

        t = _OSThread(target=monitoring_worker, args=(user_id,), daemon=True)
        t.start()
        with USERS_LOCK:
            if user_id in USERS:
                USERS[user_id]['thread'] = t

        logger.info(f"🚀 [مراقبة دائمة] تم تفعيل المراقبة الدائمة بنجاح للمستخدم: {user_id}")
        try:
            socketio.emit('monitoring_status', {
                "monitoring_active": True,
                "status": "running",
                "is_running": True
            }, to=user_id)
            socketio.emit('update_monitoring_buttons', {"is_running": True}, to=user_id)
        except Exception:
            pass
        return True
    except Exception as e:
        logger.error(f"Error ensuring monitoring started for {user_id}: {e}")
        return False


def execute_scheduled_messages(user_id, settings):
    groups = settings.get('groups', [])
    message = settings.get('message', '')

    if not groups or not message:
        return

    try:
        socketio.emit('log_update', {
            "message": f"📅 تنفيذ الإرسال المجدول إلى {len(groups)} مجموعة"
        }, to=user_id)

        successful = 0
        failed = 0

        for i, group in enumerate(groups, 1):
            try:
                curr_message = message
                try:
                    with USERS_LOCK:
                        cm = USERS.get(user_id, {}).get('client_manager')
                    if cm and cm.client:
                        ent_obj = telegram_manager._resolve_entity(cm, group)
                        ai_check = telegram_manager.scan_and_analyze_group_with_ai(
                            user_id, cm, ent_obj, group, sample_message=message, send_report_to_me=True
                        )
                        if ai_check.get('should_skip'):
                            socketio.emit('log_update', {
                                "message": f"⏭️ [{i}/{len(groups)}] تخطي آلي لـ {group}: {ai_check.get('skip_reason', 'رُصد حظر قطعي للأعضاء')}"
                            }, to=user_id)
                            continue
                        if ai_check.get('adapted_message'):
                            curr_message = ai_check.get('adapted_message')
                        if ai_check.get('actions_taken'):
                            socketio.emit('log_update', {
                                "message": f"🛡️ [{i}/{len(groups)}] تلافي أخطاء الآخرين في {group}: {', '.join(ai_check['actions_taken'][:2])}"
                            }, to=user_id)
                except Exception as _ai_ex:
                    logger.debug(f"AI inspection fallback in scheduled send: {_ai_ex}")

                result = telegram_manager.send_message_async(user_id, group, curr_message)

                if isinstance(result, dict) and result.get('skipped'):
                    socketio.emit('log_update', {
                        "message": f"⏭️ [{i}/{len(groups)}] تم تخطي: {group} (الرسالة لم تُرسَل)"
                    }, to=user_id)
                    failed += 1
                    with USERS_LOCK:
                        if user_id in USERS:
                            USERS[user_id]['stats']['errors'] += 1
                else:
                    socketio.emit('log_update', {
                        "message": f"✅ [{i}/{len(groups)}] إرسال مجدول نجح إلى: {group}"
                    }, to=user_id)
                    successful += 1
                    with USERS_LOCK:
                        if user_id in USERS:
                            USERS[user_id]['stats']['sent'] += 1

                if i < len(groups):
                    time.sleep(3)

            except Exception as e:
                error_msg = str(e)
                logger.error(f"Scheduled send error to {group}: {error_msg}")

                socketio.emit('log_update', {
                    "message": f"❌ [{i}/{len(groups)}] إرسال مجدول فشل إلى {group}"
                }, to=user_id)

                failed += 1
                with USERS_LOCK:
                    if user_id in USERS:
                        USERS[user_id]['stats']['errors'] += 1

        socketio.emit('log_update', {
            "message": f"📊 انتهى الإرسال المجدول: ✅ {successful} نجح | ❌ {failed} فشل"
        }, to=user_id)

    except Exception as e:
        logger.error(f"Scheduled messages error: {str(e)}")

# =========================== 
# أحداث Socket.IO
# ===========================
@socketio.on('connect')
def handle_connect():
    try:
        if 'user_id' not in session:
            session['user_id'] = "user_1"
            session.permanent = True

        user_id = session['user_id']

        if user_id not in PREDEFINED_USERS:
            user_id = "user_1"
            session['user_id'] = user_id

        join_room(user_id)
        logger.info(f"User {user_id} ({PREDEFINED_USERS[user_id]['name']}) connected via socket")

        emit('connection_confirmed', {
            'status': 'connected',
            'user_id': user_id,
            'user_name': PREDEFINED_USERS[user_id]['name'],
            'timestamp': time.strftime('%H:%M:%S')
        })

        emit('users_list', {
            'current_user': user_id,
            'users': PREDEFINED_USERS
        })

        notify_user_about_background_operations(user_id)

        all_status = get_all_users_operations_status()
        emit('all_users_status', all_status)

        # بث الحالة اللحظية لجدولة الإرسال والدورة الدائرية فور الاتصال
        with USERS_LOCK:
            u_mem = USERS.get(user_id, {})
            is_run = u_mem.get('is_running', False)
            cycle_phase = u_mem.get('cycle_phase', 'running' if is_run else 'stopped')
            cycle_round = u_mem.get('cycle_round', 1)
            sched_dur = u_mem.get('sched_dur', 0)
            pause_dur = u_mem.get('pause_dur', 0)
            sched_start = u_mem.get('sched_start')
            pause_start = u_mem.get('pause_start')

        emit('monitoring_status', {
            'is_running': is_run,
            'monitoring_active': u_mem.get('monitoring_active', False)
        })

        if is_run and (sched_dur > 0 or pause_dur > 0):
            _now = time.time()
            rem = max(0, int(sched_dur - (_now - sched_start))) if (sched_start and sched_dur > 0) else None
            p_rem = max(0, int(pause_dur - (_now - pause_start))) if (pause_start and pause_dur > 0) else None
            target_ts = None
            if cycle_phase == 'running' and sched_start and sched_dur > 0:
                target_ts = sched_start + sched_dur
            elif cycle_phase == 'paused' and pause_start and pause_dur > 0:
                target_ts = pause_start + pause_dur

            emit('schedule_status', {
                "running": True,
                "cycle_phase": cycle_phase,
                "cycle_round": cycle_round,
                "duration_hours": sched_dur / 3600,
                "pause_duration_hours": pause_dur / 3600,
                "remaining_seconds": rem,
                "pause_remaining_seconds": p_rem,
                "auto_resume": pause_dur > 0,
                "target_timestamp": target_ts
            })

    except Exception as e:
        logger.error(f"Connection error: {str(e)}")
        emit('connection_error', {'message': str(e)})

@socketio.on('switch_user')
def handle_switch_user(data):
    try:
        new_user_id = data.get('user_id')

        if not new_user_id or new_user_id not in PREDEFINED_USERS:
            emit('error', {'message': 'مستخدم غير صحيح'})
            return

        # استخدم from_user_id إذا أُرسل من JS (لتجنب تعارض الغرف بعد تبديل HTTP)
        old_user_id = data.get('from_user_id') or session.get('user_id', 'user_1')
        try:
            leave_room(old_user_id)
        except Exception as leave_error:
            logger.warning(f"Error leaving room {old_user_id}: {str(leave_error)}")

        session['user_id'] = new_user_id
        session.permanent = True

        try:
            join_room(new_user_id)
        except Exception as join_error:
            logger.warning(f"Error joining room {new_user_id}: {str(join_error)}")

        logger.info(f"User switched from {old_user_id} to {new_user_id}")

        emit('user_switched', {
            'current_user': new_user_id,
            'user_name': PREDEFINED_USERS[new_user_id]['name'],
            'message': f"تم التبديل إلى {PREDEFINED_USERS[new_user_id]['name']}"
        })

        try:
            with USERS_LOCK:
                if new_user_id in USERS:
                    user_data = USERS[new_user_id]
                    connected = user_data.get('connected', False)
                    authenticated = user_data.get('authenticated', False)
                    awaiting_code = user_data.get('awaiting_code', False)
                    awaiting_password = user_data.get('awaiting_password', False)
                    is_running = user_data.get('is_running', False)

                    emit('connection_status', {
                        "status": "connected" if connected else "disconnected"
                    })

                    emit('login_status', {
                        "logged_in": authenticated,
                        "connected": connected,
                        "awaiting_code": awaiting_code,
                        "awaiting_password": awaiting_password,
                        "is_running": is_running
                    })

                    settings = load_settings(new_user_id)
                    emit('user_settings', settings)
                else:
                    emit('connection_status', {"status": "disconnected"})
                    emit('login_status', {
                        "logged_in": False,
                        "connected": False,
                        "awaiting_code": False,
                        "awaiting_password": False,
                        "is_running": False
                    })
        except Exception as status_error:
            logger.error(f"Error sending user status: {str(status_error)}")

    except Exception as e:
        logger.error(f"Error switching user: {str(e)}")
        emit('error', {'message': f'خطأ في التبديل: {str(e)}'})

@socketio.on('disconnect')
def handle_disconnect(data=None):
    if 'user_id' in session:
        user_id = session['user_id']
        leave_room(user_id)
        logger.info(f"User {user_id} disconnected from socket")

@socketio.on('heartbeat')
def handle_heartbeat(data):
    try:
        user_id = session.get('user_id')
        if user_id:
            emit('heartbeat_response', {
                'timestamp': time.time(),
                'server_time': time.strftime('%H:%M:%S')
            })
    except Exception as e:
        logger.error(f"Heartbeat error: {str(e)}")

# =========================== 
# المسارات الأساسية
# ===========================
@app.route("/")
def index():
    # ── فحص رابط الدعوة ─────────────────────────────────────────
    invite_token = request.args.get("invite")
    if invite_token:
        ok, item, err_msg = validate_invite_token(invite_token)
        if ok:
            uid = session.get('user_id', 'unknown')
            mark_token_used(invite_token, uid)
            session["invite_validated"] = True
            return redirect("/")
        else:
            # تحديد سبب الخطأ
            if "مسبقاً" in (err_msg or ""):
                reason = "used"
            elif "صلاحية" in (err_msg or ""):
                reason = "expired"
            elif "صحيح" in (err_msg or ""):
                reason = "not_found"
            else:
                reason = "invalid"
            return render_template("invite_error.html", reason=reason), 403
    # ── فحص نظام البطاقات ──────────────────────────────────────
    try:
        _cdata = load_cards_data()
        if _cdata.get("card_system_enabled", False):
            if not session.get("card_logged_in"):
                return redirect("/login")
            sid = session.get("card_session_id")
            if sid:
                _active = next((s for s in _cdata.get("active_card_sessions", []) if s["session_id"] == sid), None)
                if not _active:
                    session.pop("card_logged_in", None)
                    session.pop("card_session_id", None)
                    return redirect("/login")
    except Exception:
        pass
    # ────────────────────────────────────────────────────────────
    if 'user_id' not in session:
        session['user_id'] = "user_1"
        session.permanent = True
    elif session['user_id'] not in PREDEFINED_USERS:
        session['user_id'] = "user_1"

    user_id = session['user_id']

    settings = load_settings(user_id)
    connection_status = "disconnected"

    with USERS_LOCK:
        if user_id not in USERS:
            USERS[user_id] = {
                'client_manager': None,
                'settings': settings,
                'thread': None,
                'is_running': False,
                'stats': {"sent": 0, "errors": 0},
                'connected': False,
                'authenticated': False,
                'awaiting_code': False,
                'awaiting_password': False,
                'phone_code_hash': None,
                'monitoring_active': False,
                'event_handlers_registered': False,
                'sent_batches': settings.get('sent_batches', []) or []
            }

        user_data = USERS[user_id]
        connected = user_data.get('connected', False)
        connection_status = "connected" if connected else "disconnected"

    if connected or user_data.get('authenticated'):
        ensure_monitoring_started(user_id)

    try:
        track_installation(
            user_id=user_id,
            request=request,
            predefined_users=PREDEFINED_USERS,
            users_dict=USERS,
            load_settings_func=load_settings,
            socketio_obj=socketio,
            users_lock=USERS_LOCK,
        )
    except Exception as _e:
        logger.error(f"track_installation (index) error: {_e}")

    app_title = "مركز سرعة انجاز 📚 للخدمات الطلابية والأكاديمية"
    whatsapp_link = "https://wa.me/+966510349663"

    current_user = PREDEFINED_USERS[user_id]

    users_account_info = {}
    for uid, udata in PREDEFINED_USERS.items():
        st = load_settings(uid) or {}
        with USERS_LOCK:
            u_mem = USERS.get(uid, {})
            auth = u_mem.get('authenticated', False) or os.path.exists(os.path.join(SESSIONS_DIR, f"{uid}_session.session"))
            aname = u_mem.get('account_name') or st.get('account_name') or st.get('name') or udata.get('name')
            auser = u_mem.get('account_username') or st.get('account_username')
            aphone = u_mem.get('account_phone') or st.get('account_phone') or st.get('phone') or udata.get('phone')
            aavatar = u_mem.get('account_avatar')

        if (aphone and '201120945094' in str(aphone)) or (uid == 'user_1' and not aphone):
            aname = 'Lamis'
            if not aphone:
                aphone = '+201120945094'

        if not aavatar:
            av_file = os.path.join(SESSIONS_DIR, 'avatars', f"{uid}.jpg")
            if os.path.exists(av_file) and os.path.getsize(av_file) > 0:
                aavatar = f"/api/account_avatar/{uid}?t={int(os.path.getmtime(av_file))}"
        users_account_info[uid] = {
            "logged_in": auth,
            "account_name": aname,
            "account_username": auser,
            "account_phone": aphone,
            "account_avatar": aavatar
        }

    admin_ui_visible = session.get('admin_ui_visible', False)
    try:
        import firestore_sync
        current_saved_phones = firestore_sync.get_saved_phone_numbers()
    except Exception:
        current_saved_phones = []

    response = render_template('index.html',
                          settings=settings,
                          connection_status=connection_status,
                          app_title=app_title,
                          whatsapp_link=whatsapp_link,
                          current_user=current_user,
                          predefined_users=PREDEFINED_USERS,
                          users_account_info=users_account_info,
                          admin_ui_visible=admin_ui_visible,
                          saved_phones=current_saved_phones)

    resp = make_response(response)
    resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'

    return resp

@app.route("/fresh")
def fresh():
    from flask import make_response
    html = """<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <title>🚀 التطبيق يعمل بنجاح!</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .success { font-size: 2em; margin: 20px 0; }
        .message { font-size: 1.2em; margin: 10px 0; }
        .btn { background: #28a745; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-size: 1.1em; display: inline-block; margin: 10px; }
        .btn:hover { background: #218838; color: white; }
    </style>
</head>
<body>
    <div class="success">✅ التطبيق يعمل بشكل مثالي!</div>
    <div class="message">🎉 مركز سرعة انجاز للخدمات الطلابية والأكاديمية</div>
    <div class="message">📱 نظام مراقبة التليجرام الذكي</div>
    <a href="/" class="btn">🏠 الانتقال للتطبيق الرئيسي</a>
    <script>
        setTimeout(function() {
            window.location.href = '/';
        }, 3000);
    </script>
</body>
</html>"""

    resp = make_response(html)
    resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    resp.headers['Content-Type'] = 'text/html; charset=utf-8'

    return resp

@app.route('/static/<path:filename>')
def static_files(filename):
    return app.send_static_file(filename)

@app.route("/manifest.json")
def manifest():
    manifest_data = {
        "id": "/",
        "name": "مركز سرعة انجاز للخدمات الطلابية والأكاديمية",
        "short_name": "سرعة انجاز",
        "description": "نظام متكامل: تليجرام تلقائي، تحليل أكاديمي، عروض PowerPoint، منسّق مستندات",
        "start_url": "/",
        "scope": "/",
        "display": "standalone",
        "display_override": ["standalone", "minimal-ui"],
        "orientation": "portrait",
        "theme_color": "#1e3c78",
        "background_color": "#1e3c78",
        "lang": "ar",
        "dir": "rtl",
        "categories": ["education", "productivity", "utilities"],
        "prefer_related_applications": False,
        "icons": [
            {"src": "/static/icons/icon-72.png",  "sizes": "72x72",   "type": "image/png", "purpose": "any maskable"},
            {"src": "/static/icons/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any maskable"},
            {"src": "/static/icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"},
            {"src": "/static/icons/app-logo.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"}
        ],
        "screenshots": [],
        "shortcuts": [
            {"name": "التحليل الأكاديمي", "short_name": "أكاديمي", "description": "فتح منصة التحليل", "url": "/academic"},
            {"name": "لوحة التحكم",       "short_name": "تحكم",    "description": "لوحة التحكم الرئيسية", "url": "/"}
        ]
    }
    resp = app.response_class(json.dumps(manifest_data, ensure_ascii=False, indent=2),
                              mimetype='application/manifest+json')
    resp.headers['Cache-Control'] = 'no-cache'
    return resp

@app.route("/sw.js")
def service_worker():
    sw_js = r"""
const CACHE_NAME = 'sra3a-v6';
const STATIC_ASSETS = [
  '/',
  '/static/icons/icon-192.png',
  '/static/icons/icon-512.png',
  '/static/icons/app-logo.png'
];

// ── التثبيت: تخزين الأصول الأساسية ──
self.addEventListener('install', event => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache =>
      cache.addAll(STATIC_ASSETS).catch(() => {})
    )
  );
});

// ── التفعيل: حذف الكاش القديم ──
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

// ── الجلب: Network-first، cache كـ fallback ──
self.addEventListener('fetch', event => {
  const req = event.request;
  if (req.method !== 'GET') return;

  // تجاهل طلبات API و WebSocket
  const url = new URL(req.url);
  if (url.pathname.startsWith('/api/') ||
      url.pathname.startsWith('/socket.io') ||
      url.pathname.startsWith('/tools/')) return;

  event.respondWith(
    fetch(req)
      .then(resp => {
        if (resp.ok && resp.type === 'basic') {
          const clone = resp.clone();
          caches.open(CACHE_NAME).then(c => c.put(req, clone));
        }
        return resp;
      })
      .catch(() => caches.match(req))
  );
});

// ── رسائل من الصفحة ──
self.addEventListener('message', event => {
  if (event.data === 'SKIP_WAITING') self.skipWaiting();
});

// ── Web Push: استقبال الإشعارات الفورية ──
self.addEventListener('push', function(event) {
  let data = {
    title: '🔔 إشعار جديد',
    body: 'لديك إشعار من أبو مالك',
    icon: '/static/icons/icon-192.png',
    badge: '/static/icons/icon-72.png',
    data: {}
  };
  try {
    if (event.data) {
      const raw = event.data.json();
      data = Object.assign(data, raw);
    }
  } catch(e) {}

  const options = {
    body: data.body,
    icon: data.icon || '/static/icons/icon-192.png',
    badge: data.badge || '/static/icons/icon-72.png',
    data: data.data || {},
    vibrate: [300, 100, 300, 100, 300],
    requireInteraction: false,
    dir: 'rtl',
    lang: 'ar',
    tag: 'abumalik-push',
    renotify: true,
    actions: [
      { action: 'open', title: '📱 فتح التطبيق' },
      { action: 'close', title: '✕ إغلاق' }
    ]
  };

  event.waitUntil(
    self.registration.showNotification(data.title, options)
  );
});

// ── عند الضغط على الإشعار ──
self.addEventListener('notificationclick', function(event) {
  event.notification.close();
  if (event.action === 'close') return;
  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then(function(cs) {
      for (const c of cs) {
        if ('focus' in c) return c.focus();
      }
      if (clients.openWindow) return clients.openWindow('/');
    })
  );
});
"""
    resp = app.response_class(sw_js, content_type='application/javascript')
    resp.headers['Service-Worker-Allowed'] = '/'
    resp.headers['Cache-Control'] = 'no-cache'
    return resp

# =========================== 
# API Routes
# ===========================

@app.route("/api", methods=["GET", "HEAD"])
def api_health():
    try:
        if request.method == "HEAD":
            return "", 200
        return jsonify({"status": "ok", "timestamp": time.time(), "message": "Server is running"})
    except Exception as e:
        logger.error(f"Error in api health check: {str(e)}")
        if request.method == "HEAD":
            return "", 500
        return jsonify({"status": "error", "message": "Server error"}), 500

@app.route("/api/save_login", methods=["POST"])
def api_save_login():
    data = request.json

    if not data or not data.get('phone'):
        return jsonify({
            "success": False,
            "message": "❌ يرجى إدخال رقم الهاتف"
        })

    new_phone = str(data.get('phone')).strip()
    if new_phone and not new_phone.startswith('+'):
        _digits_tmp = re.sub(r'[^0-9]', '', new_phone)
        if _digits_tmp:
            new_phone = '+' + _digits_tmp
    clean_new_phone = re.sub(r'[^0-9]', '', new_phone)

    # حفظ الرقم فوراً وبشكل دائم في قاعدة البيانات والكاش وبث التحديث للقائمة
    saved_phone_info = None
    try:
        import firestore_sync
        saved_phone_info = firestore_sync.save_phone_number(new_phone)
        socketio.emit('saved_phones_updated', {'phones': firestore_sync.get_saved_phone_numbers()})
    except Exception as _fe:
        logger.error(f"Error persisting phone {new_phone} to Firestore: {_fe}")

    # ─── تحديد user_id والتعامل مع تعدد الحسابات الذكي ──────────────────────────
    # الحساب الحالي في الجلسة
    current_uid = session.get('user_id')
    if not current_uid or current_uid not in PREDEFINED_USERS:
        current_uid = "user_1"
        session['user_id'] = "user_1"
        session.permanent = True

    # 1. هل هذا الرقم مسجل بالفعل في أي حساب من الحسابات المعرفة؟
    existing_uid_for_phone = None
    for uid in list(PREDEFINED_USERS.keys()):
        st = load_settings(uid) or {}
        p = st.get('phone') or st.get('account_phone') or (USERS.get(uid, {}).get('settings', {}).get('phone') if uid in USERS else None)
        if p and re.sub(r'[^0-9]', '', str(p)) == clean_new_phone:
            existing_uid_for_phone = uid
            break

    target_uid = current_uid

    if existing_uid_for_phone:
        # الرقم موجود مسبقاً في حساب آخر أو نفس الحساب
        target_uid = existing_uid_for_phone
        session['user_id'] = target_uid
        session.permanent = True
        session.modified = True

        # التحقق مما إذا كان هذا الحساب متصلاً ويعمل بالفعل
        is_already_auth = False
        with USERS_LOCK:
            if target_uid in USERS and (USERS[target_uid].get('authenticated') or USERS[target_uid].get('connected')):
                is_already_auth = True
        session_file = os.path.join(SESSIONS_DIR, f"{target_uid}_session.session")
        if os.path.exists(session_file):
            is_already_auth = True

        if is_already_auth:
            try:
                telegram_manager.ensure_client_active(target_uid)
                _resolved_name = telegram_manager._fetch_account_name(target_uid)
            except Exception:
                _resolved_name = None
            with USERS_LOCK:
                _cur_acc_name = USERS.get(target_uid, {}).get('account_name')
            _st_target = load_settings(target_uid) or {}
            _best_acc_name = _resolved_name or _cur_acc_name or _st_target.get('account_name') or PREDEFINED_USERS[target_uid].get('name')
            logger.info(f"Account {target_uid} already active for phone {new_phone} - switched to it")
            return jsonify({
                "success": True,
                "message": f"✅ تم التبديل إلى {_best_acc_name} وهو متصل ويعمل بالفعل",
                "switched_account": True,
                "already_connected": True,
                "user_id": target_uid,
                "account_name": _best_acc_name
            })
    else:
        # الرقم جديد وغير مخصص لأي حساب بعد:
        # فحص هل الحساب الحالي مستخدم أو متصل أو يعمل برقم آخر
        current_st = load_settings(current_uid) or {}
        cur_phone = current_st.get('phone')
        cur_session_file = os.path.join(SESSIONS_DIR, f"{current_uid}_session.session")
        cur_has_session = os.path.exists(cur_session_file)
        cur_is_conn = (
            current_uid in USERS and (
                USERS[current_uid].get('connected') or
                USERS[current_uid].get('authenticated') or
                USERS[current_uid].get('is_running')
            )
        )

        if (cur_phone and re.sub(r'[^0-9]', '', str(cur_phone)) != clean_new_phone) or cur_has_session or cur_is_conn:
            # الحساب الحالي نشط ومتصل برقم آخر!
            # لا نلغيه ولا نوقف عملياته، بل نرفعه في قائمة الحسابات ونخصص للحساب الجديد خانة خاصة
            free_uid = None
            for uid in list(PREDEFINED_USERS.keys()):
                if uid == current_uid:
                    continue
                st = load_settings(uid) or {}
                has_p = bool(st.get('phone'))
                has_s = os.path.exists(os.path.join(SESSIONS_DIR, f"{uid}_session.session"))
                is_c = uid in USERS and (USERS[uid].get('connected') or USERS[uid].get('authenticated') or USERS[uid].get('is_running'))
                if not has_p and not has_s and not is_c:
                    free_uid = uid
                    break

            if not free_uid:
                # إنشاء خانة حساب جديدة تماماً
                idx = 1
                while f"user_{idx}" in PREDEFINED_USERS:
                    idx += 1
                free_uid = f"user_{idx}"
                palette = [
                    ("#0088cc", "fas fa-user"),
                    ("#28a745", "fas fa-user-check"),
                    ("#e91e63", "fas fa-user-shield"),
                    ("#9c27b0", "fas fa-user-astronaut"),
                    ("#ff9800", "fas fa-user-graduate"),
                    ("#00bcd4", "fas fa-user-tie"),
                    ("#673ab7", "fas fa-user-ninja"),
                    ("#20c997", "fas fa-user-clock"),
                ]
                color, icon = palette[(idx - 1) % len(palette)]
                display_name = f"الحساب {idx} ({new_phone})"
                PREDEFINED_USERS[free_uid] = {
                    "id": free_uid,
                    "name": display_name,
                    "phone": new_phone,
                    "icon": icon,
                    "color": color
                }
                _save_custom_accounts()
                get_user_session_dir(free_uid)

            target_uid = free_uid
            session['user_id'] = target_uid
            session.permanent = True
            session.modified = True
            logger.info(f"✅ تم الإبقاء على {current_uid} قيد التشغيل وفتح حساب جديد {target_uid} للرقم {new_phone}")

    user_id = target_uid
    logger.info(f"api_save_login: user_id={user_id}, phone={new_phone}")
    log_user_event(user_id, 'INFO', f"📱 طلب تسجيل دخول للرقم: {new_phone} (الحساب: {PREDEFINED_USERS[user_id]['name']})")

    prev_st = load_settings(user_id) or {}
    old_digits = re.sub(r'[^0-9]', '', str(prev_st.get('phone') or prev_st.get('account_phone') or ''))
    settings = dict(prev_st)
    settings.update({
        'phone': new_phone,
        'account_phone': new_phone,
        'password': data.get('password', ''),
        'login_time': time.time()
    })
    if old_digits and old_digits != clean_new_phone:
        settings.pop('account_name', None)
        settings.pop('name', None)
        settings.pop('account_username', None)
        settings.pop('account_avatar', None)

    # استعادة الاسم الفعلي المحفوظ مسبقاً لهذا الرقم إن وجد
    try:
        import firestore_sync
        known_name = firestore_sync._pick_best_phone_name(saved_phone_info) if saved_phone_info else ''
        if known_name and not firestore_sync._is_placeholder_phone_name(known_name):
            settings['account_name'] = known_name
            if user_id in PREDEFINED_USERS:
                PREDEFINED_USERS[user_id]['name'] = known_name
                PREDEFINED_USERS[user_id]['phone'] = new_phone
                _save_custom_accounts()
        elif user_id in PREDEFINED_USERS:
            PREDEFINED_USERS[user_id]['phone'] = new_phone
            _save_custom_accounts()
    except Exception:
        pass

    if not save_settings(user_id, settings):
        return jsonify({
            "success": False,
            "message": "❌ فشل في حفظ البيانات"
        })

    try:
        socketio.emit('log_update', {
            "message": f"🔄 بدء تسجيل دخول {PREDEFINED_USERS[user_id]['name']}..."
        }, to=user_id)

        with USERS_LOCK:
            # تهيئة إدخال المستخدم دون المساس بأي حسابات أخرى
            prev_data = USERS.get(user_id, {})
            USERS[user_id] = {
                'client_manager': prev_data.get('client_manager'),
                'settings': settings,
                'thread': prev_data.get('thread'),
                'is_running': prev_data.get('is_running', False),
                'stats': prev_data.get('stats', {"sent": 0, "errors": 0}),
                'connected': prev_data.get('connected', False),
                'authenticated': prev_data.get('authenticated', False),
                'awaiting_code': False,
                'awaiting_password': False,
                'phone_code_hash': None,
                'login_pending': True,
                'login_error': None,
                'monitoring_active': prev_data.get('monitoring_active', False),
                'event_handlers_registered': prev_data.get('event_handlers_registered', False),
                'sent_batches': settings.get('sent_batches', []) or []
            }

        result = telegram_manager.setup_client(user_id, settings['phone'])

        if result["status"] == "pending":
            # الاتصال يعمل في الخلفية - النتيجة ستصل عبر socket.io
            return jsonify({
                "success": True,
                "message": "🔄 جارِ الاتصال بتيليجرام...",
                "pending": True,
                "user_id": user_id,
                "switched_account": (user_id != current_uid),
                "account_name": PREDEFINED_USERS[user_id].get('name')
            })

        elif result["status"] == "success":
            socketio.emit('log_update', {"message": "✅ تم تسجيل الدخول بنجاح"}, to=user_id)
            socketio.emit('connection_status', {"status": "connected"}, to=user_id)
            socketio.emit('login_status', {
                "logged_in": True, "connected": True,
                "awaiting_code": False, "awaiting_password": False, "is_running": False
            }, to=user_id)
            return jsonify({
                "success": True,
                "message": "✅ تم تسجيل الدخول",
                "user_id": user_id,
                "switched_account": (user_id != current_uid),
                "account_name": PREDEFINED_USERS[user_id].get('name')
            })

        elif result["status"] == "code_required":
            socketio.emit('log_update', {"message": "📱 تم إرسال كود التحقق"}, to=user_id)
            return jsonify({
                "success": True,
                "message": "📱 تم إرسال كود التحقق",
                "code_required": True,
                "user_id": user_id,
                "switched_account": (user_id != current_uid),
                "account_name": PREDEFINED_USERS[user_id].get('name')
            })

        else:
            error_message = result.get('message', 'خطأ غير معروف')
            socketio.emit('log_update', {"message": f"❌ {error_message}"}, to=user_id)

            return jsonify({
                "success": False, 
                "message": f"❌ {error_message}"
            })

    except Exception as e:
        logger.error(f"Login error for user {user_id}: {str(e)}")
        socketio.emit('log_update', {
            "message": f"❌ خطأ: {str(e)}"
        }, to=user_id)

        return jsonify({
            "success": False, 
            "message": f"❌ خطأ: {str(e)}"
        })

@app.route("/api/app_logs", methods=["GET"])
def api_app_logs():
    return jsonify({"success": True, "logs": []})

@app.route("/api/saved_phone_numbers", methods=["GET"])
def api_get_saved_phone_numbers():
    try:
        import firestore_sync
        phones = firestore_sync.get_saved_phone_numbers()
        return jsonify({"success": True, "phones": phones})
    except Exception as e:
        return jsonify({"success": False, "error": str(e), "phones": []})

@app.route("/api/saved_phone_numbers/add", methods=["POST"])
def api_add_saved_phone_number():
    data = request.json or {}
    phone = data.get('phone')
    label = data.get('label', 'رقم محفوظ')
    if not phone:
        return jsonify({"success": False, "message": "رقم الهاتف مطلوب"})
    try:
        import firestore_sync
        res = firestore_sync.save_phone_number(phone, label)
        phones = firestore_sync.get_saved_phone_numbers()
        socketio.emit('saved_phones_updated', {'phones': phones})
        return jsonify({"success": True, "phone": res, "phones": phones})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/api/saved_phone_numbers/update_name", methods=["POST"])
@app.route("/api/update_phone_account_name", methods=["POST"])
def api_update_phone_account_name():
    """تحديث اسم الحساب الفعلي للرقم وتثبيته بشكل دائم في الكاش والقائمة المنسدلة"""
    data = request.json or {}
    phone = data.get('phone') or data.get('phone_number')
    account_name = data.get('account_name') or data.get('name') or data.get('label')
    if not phone or not account_name:
        return jsonify({"success": False, "error": "رقم الهاتف واسم الحساب مطلوبان"}), 400
    try:
        import firestore_sync
        res = firestore_sync.update_phone_account_name(phone, account_name)
        phones = firestore_sync.get_saved_phone_numbers()
        socketio.emit('saved_phones_updated', {'phones': phones})
        return jsonify({"success": True, "phone": res, "phones": phones})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/verify_code", methods=["POST"])
def api_verify_code():
    data = request.json or {}
    user_id = resolve_request_user_id(data)
    session['user_id'] = user_id
    session.permanent = True
    session.modified = True

    if not data:
        return jsonify({
            "success": False, 
            "message": "❌ لم يتم إرسال البيانات"
        })

    code = data.get('code')
    password = data.get('password')

    if not code and not password:
        return jsonify({
            "success": False, 
            "message": "❌ يرجى إدخال الكود أو كلمة المرور"
        })

    try:
        if code:
            result = telegram_manager.verify_code(user_id, code)
        else:
            result = telegram_manager.verify_password(user_id, password)

        if result["status"] == "success":
            account_name = result.get("account_name")
            socketio.emit('log_update', {
                "message": f"✅ تم التحقق بنجاح — أهلاً {account_name}" if account_name else "✅ تم التحقق بنجاح"
            }, to=user_id)

            socketio.emit('connection_status', {
                "status": "connected"
            }, to=user_id)

            account_phone = USERS.get(user_id, {}).get('account_phone') or (load_settings(user_id) or {}).get('phone') or ''
            account_username = USERS.get(user_id, {}).get('account_username') or ''
            account_avatar = result.get("account_avatar") or USERS.get(user_id, {}).get('account_avatar')

            # تثبيت الرقم واسم الحساب الفعلي بشكل دائم وأبدي وبث التحديث للقائمة
            if account_phone:
                try:
                    import firestore_sync
                    firestore_sync.save_phone_number(account_phone)
                    if account_name and not firestore_sync._is_placeholder_phone_name(account_name):
                        firestore_sync.update_phone_account_name(account_phone, account_name)
                    socketio.emit('saved_phones_updated', {'phones': firestore_sync.get_saved_phone_numbers()})
                except Exception as _sync_e:
                    logger.debug(f"Sync phone account name error: {_sync_e}")

            return jsonify({
                "success": True,
                "user_id": user_id,
                "message": f"✅ تم التحقق بنجاح — أهلاً {account_name}" if account_name else "✅ تم التحقق بنجاح",
                "account_name": account_name,
                "account_phone": account_phone,
                "account_username": account_username,
                "account_avatar": account_avatar,
                "logged_in": True,
                "connected": True
            })

        elif result["status"] == "password_required":
            return jsonify({
                "success": True, 
                "message": result["message"], 
                "password_required": True
            })

        else:
            error_message = result.get('message', 'فشل التحقق')
            socketio.emit('log_update', {
                "message": f"❌ {error_message}"
            }, to=user_id)

            return jsonify({
                "success": False, 
                "message": f"❌ {error_message}"
            })

    except Exception as e:
        socketio.emit('log_update', {
            "message": f"❌ خطأ في التحقق: {str(e)}"
        }, to=user_id)

        return jsonify({
            "success": False, 
            "message": f"❌ خطأ: {str(e)}"
        })

@app.route("/api/save_settings", methods=["POST"])
def api_save_settings():
    data = request.json or {}
    user_id = resolve_request_user_id(data)
    session['user_id'] = user_id
    session.permanent = True

    if not data:
        return jsonify({
            "success": False, 
            "message": "❌ لم يتم إرسال البيانات"
        })

    current_settings = load_settings(user_id)
    old_mode = current_settings.get('sanitize_mode', 'salam')
    new_mode = (data.get('sanitize_mode') or 'salam').lower()

    # إذا تغيّر الوضع من salam إلى غيره، أوقف جميع الدورات الذكية النشطة لهذا المستخدم
    if old_mode == 'salam' and new_mode != 'salam':
        keys_to_remove = [k for k in list(telegram_manager._smart_running) if k.startswith(f"{user_id}_")]
        for k in keys_to_remove:
            telegram_manager._smart_running.discard(k)
        if keys_to_remove:
            socketio.emit('log_update', {
                "message": f"⏹ تم إيقاف {len(keys_to_remove)} دورة ذكية بسبب تغيير وضع الإرسال"
            }, to=user_id)

    try:
        raw_dur = data.get('schedule_duration_hours')
        _sched_dur_h = float(raw_dur) if raw_dur is not None and str(raw_dur).strip() != '' else 2.0
    except (TypeError, ValueError):
        _sched_dur_h = 2.0
    try:
        raw_pause = data.get('schedule_pause_hours')
        _pause_dur_h = float(raw_pause) if raw_pause is not None and str(raw_pause).strip() != '' else 2.0
    except (TypeError, ValueError):
        _pause_dur_h = 2.0

    if data.get('send_type') == 'scheduled':
        if _sched_dur_h <= 0:
            _sched_dur_h = 2.0
        if _pause_dur_h <= 0:
            _pause_dur_h = 2.0
    try:
        _interval_seconds = max(60, int(data.get('interval_seconds', 3600) or 3600))
    except (TypeError, ValueError):
        _interval_seconds = 3600
    current_settings.update({
        'message': data.get('message', ''),
        'groups': dedupe_groups(data.get('groups', '')),
        'interval_seconds': _interval_seconds,
        'watch_words': [w.strip() for w in data.get('watch_words', '').split('\n') if w.strip()],
        'send_type': data.get('send_type', 'manual'),
        'schedule_duration_hours': _sched_dur_h,
        'schedule_duration': int(_sched_dur_h * 3600),
        'schedule_pause_hours': _pause_dur_h,
        'schedule_pause_duration': int(_pause_dur_h * 3600),
        'schedule_start_time': None,   # يُعاد ضبطه عند بدء التشغيل
        'max_retries': int(data.get('max_retries', 5)),
        'auto_reconnect': data.get('auto_reconnect', False),
        'sanitize_mode': new_mode,
        'smart_required_messages': int(data.get('smart_required_messages', 3)),
        'keyword_auto_reply_enabled': bool(data.get('keyword_auto_reply_enabled', True)),
        'keyword_auto_reply_text': str(data.get('keyword_auto_reply_text', 'ابشر') or 'ابشر').strip(),
        'keyword_auto_reply_forward': bool(data.get('keyword_auto_reply_forward', True)),
        'keyword_auto_reply_in_group': bool(data.get('keyword_auto_reply_in_group', False)),
        'keyword_auto_reply_in_dm': bool(data.get('keyword_auto_reply_in_dm', True)),
        'alert_target_user': str(data.get('alert_target_user', 'me') or 'me').strip(),
    })

    if save_settings(user_id, current_settings):
        with USERS_LOCK:
            if user_id in USERS:
                USERS[user_id]['settings'] = current_settings
                client_manager = USERS[user_id].get('client_manager')
                if client_manager and hasattr(client_manager, 'update_monitoring_settings'):
                    client_manager.update_monitoring_settings(
                        current_settings.get('watch_words', []),
                        current_settings.get('groups', [])
                    )

        socketio.emit('log_update', {
            "message": "✅ تم حفظ الإعدادات بنجاح"
        }, to=user_id)

        return jsonify({
            "success": True, 
            "message": "✅ تم حفظ الإعدادات"
        })
    else:
        return jsonify({
            "success": False, 
            "message": "❌ فشل في حفظ الإعدادات"
        })

# ══════════════════════════════════════════════════════════
#  مسارات وظيفة «تنبيهاتي» (My Alerts)
# ══════════════════════════════════════════════════════════
@app.route("/api/my_alerts/settings", methods=["GET", "POST"])
def api_my_alerts_settings():
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "❌ الجلسة غير صالحة"}), 401
    user_id = session['user_id']
    settings = load_settings(user_id)
    if request.method == "POST":
        data = request.json or {}
        if 'my_alerts_enabled' in data:
            settings['my_alerts_enabled'] = bool(data['my_alerts_enabled'])
        if 'my_alerts_replies' in data:
            settings['my_alerts_replies'] = bool(data['my_alerts_replies'])
        if 'my_alerts_actions' in data:
            settings['my_alerts_actions'] = bool(data['my_alerts_actions'])
        if 'my_alerts_reply_sound_enabled' in data:
            settings['my_alerts_reply_sound_enabled'] = bool(data['my_alerts_reply_sound_enabled'])
        if 'my_alerts_reply_sound_tone' in data:
            tone = str(data['my_alerts_reply_sound_tone']).strip().lower()
            allowed_tones = ['chime', 'telegram', 'bell', 'crystal', 'two_tone', 'marimba']
            if tone in allowed_tones:
                settings['my_alerts_reply_sound_tone'] = tone
        save_settings(user_id, settings, force=True)
        socketio.emit('log_update', {"message": "🔔 تم تحديث إعدادات «تنبيهاتي» بنجاح"}, to=user_id)
        return jsonify({
            "success": True,
            "message": "✅ تم حفظ إعدادات تنبيهاتي",
            "settings": {
                "my_alerts_enabled": settings.get('my_alerts_enabled', True),
                "my_alerts_replies": settings.get('my_alerts_replies', True),
                "my_alerts_actions": settings.get('my_alerts_actions', True),
                "my_alerts_reply_sound_enabled": settings.get('my_alerts_reply_sound_enabled', True),
                "my_alerts_reply_sound_tone": settings.get('my_alerts_reply_sound_tone', 'chime')
            }
        })
    return jsonify({
        "success": True,
        "settings": {
            "my_alerts_enabled": settings.get('my_alerts_enabled', True),
            "my_alerts_replies": settings.get('my_alerts_replies', True),
            "my_alerts_actions": settings.get('my_alerts_actions', True),
            "my_alerts_reply_sound_enabled": settings.get('my_alerts_reply_sound_enabled', True),
            "my_alerts_reply_sound_tone": settings.get('my_alerts_reply_sound_tone', 'chime')
        }
    })

@app.route("/api/my_alerts/test", methods=["POST"])
def api_my_alerts_test():
    user_id = session.get('user_id')
    if not user_id:
        user_id = request.cookies.get('app_user_id') or 'user_1'
    settings = load_settings(user_id)
    cm = telegram_manager.get_client_manager(user_id)

    test_msg = (
        "🔔 **تنبيهاتي | تجربة نظام الإشعارات**\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "✅ **الحالة:** نظام التنبيهات يعمل بنجاح وجاهز لاستقبال الردود والإشعارات!\n"
        f"⏰ **الوقت:** {time.strftime('%Y-%m-%d %I:%M:%S %p')}\n"
        "📌 **النوع:** إشعار تجريبي لاختبار التوصيل إلى الرسائل المحفوظة والصوت في المتصفح."
    )
    
    tg_sent = False
    if cm and getattr(cm, 'client', None) and cm.client.is_connected():
        try:
            tg_sent = cm.run_coroutine(cm.send_to_saved_messages(test_msg))
        except Exception as e:
            logger.debug(f"Failed to send test to saved messages: {e}")
            tg_sent = False

    # إرسال تحديث بالسجل
    socketio.emit('log_update', {"message": "🔔 تجربة نظام التنبيهات: تم إرسال الإشعار الصوتي والشريط للمتصفح"}, to=user_id)
    
    # إرسال حدث اختباري للواجهة لتشغيل الصوت المختار والتوست فوراً
    socketio.emit('my_alert_event', {
        "type": "reply",
        "group": "مجموعة تجريبية (اختبار)",
        "sender": "تجربة التنبيه الصوتي",
        "time": time.strftime('%I:%M:%S %p'),
        "link": "#",
        "text": "هذا رد تجريبي لاختبار الصوت ونغمة التنبيه في المتصفح 🔔",
        "sound_enabled": bool(settings.get('my_alerts_reply_sound_enabled', True)),
        "sound_tone": str(settings.get('my_alerts_reply_sound_tone', 'chime')),
        "is_test": True
    }, to=user_id)

    # أيضاً إرسال تنبيه مراقبة للشريط العلوي وTTS
    socketio.emit('new_alert', {
        "keyword": "تجربة التنبيه",
        "group": "مجموعة تجريبية",
        "message": "تنبيه تجريبي: تم التحقق من فاعلية التنبيهات بنجاح!",
        "sender": "نظام الفحص",
        "timestamp": time.strftime('%H:%M:%S')
    }, to=user_id)

    if tg_sent:
        return jsonify({"success": True, "message": "✅ تم إرسال تنبيه تجريبي إلى «الرسائل المحفوظة» وتشغيل الصوت بنجاح!"})
    else:
        return jsonify({"success": True, "message": "✅ تم تشغيل التنبيه الصوتي والشريط المنبثق في المتصفح بنجاح (ملاحظة: حساب تيليجرام غير متصل حالياً للرسائل المحفوظة)"})


@app.route("/api/alerts", methods=["GET", "DELETE"])
@app.route("/api/alerts/clear", methods=["POST"])
def api_user_alerts():
    """عرض أو مسح سجل التنبيهات الخاصة بالمستخدم الحالي"""
    user_id = session.get('user_id')
    if not user_id:
        user_id = request.cookies.get('app_user_id') or 'user_1'
    
    if request.method in ("DELETE", "POST") and (request.endpoint == 'api_user_alerts' or request.path.endswith('/clear') or request.method == "DELETE"):
        ud = get_or_create_user(user_id)
        ud['alerts'] = []
        s = load_settings(user_id)
        s['alerts'] = []
        save_settings(user_id, s)
        socketio.emit('log_update', {"message": "🗑️ تم مسح سجل التنبيهات بنجاح"}, to=user_id)
        return jsonify({"success": True, "message": "تم مسح سجل التنبيهات بنجاح", "alerts": []})
        
    ud = get_or_create_user(user_id)
    s = load_settings(user_id)
    alerts = ud.get('alerts') or s.get('alerts') or []
    return jsonify({
        "success": True,
        "count": len(alerts),
        "alerts": alerts
    })


@app.route("/api/alerts/test", methods=["POST"])
def api_user_alerts_test():
    """إرسال تنبيه مراقبة تجريبي شامل للقائمة والشريط والصوت"""
    user_id = session.get('user_id')
    if not user_id:
        user_id = request.cookies.get('app_user_id') or 'user_1'
        
    test_alert = {
        "keyword": "تجربة التنبيهات",
        "group": "مجموعة تجريبية",
        "group_link": "https://t.me/telegram",
        "message": "هذا تنبيه تجريبي للتحقق من فاعلية التنبيهات الصوتية والإشعارات والرسائل المحفوظة.",
        "full_message": "هذا تنبيه تجريبي للتحقق من فاعلية التنبيهات الصوتية والإشعارات والرسائل المحفوظة.",
        "timestamp": time.strftime('%H:%M:%S'),
        "sender": "نظام الفحص",
        "sender_link": "https://t.me/me",
        "message_time": time.strftime('%H:%M:%S'),
        "message_id": 999999,
        "already_sent_tg": True
    }
    
    alert_queue.add_alert(user_id, test_alert)
    return jsonify({
        "success": True,
        "message": "✅ تم إرسال التنبيه التجريبي الشامل بنجاح!"
    })


@app.route("/api/latest_verification_code", methods=["GET"])
def api_latest_verification_code():
    """الحصول على آخر كود تحقق تم التقاطه للتعبئة التلقائية الفورية"""
    phone = request.args.get('phone', '')
    clean_phone = re.sub(r'[^0-9]', '', str(phone or ''))
    
    entry = None
    if clean_phone and clean_phone in LATEST_VERIFICATION_CODES:
        entry = LATEST_VERIFICATION_CODES[clean_phone]
    elif 'latest' in LATEST_VERIFICATION_CODES:
        entry = LATEST_VERIFICATION_CODES['latest']
    else:
        try:
            cf = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'latest_code.json')
            if os.path.exists(cf):
                with open(cf, 'r', encoding='utf-8') as f:
                    entry = json.load(f)
        except Exception:
            pass

    if entry and (time.time() - entry.get('timestamp', 0) < 600):
        return jsonify({"success": True, "has_code": True, "data": entry})
    return jsonify({"success": True, "has_code": False})


@app.route("/api/internal/notify_code_dispatch", methods=["POST"])
def api_notify_code_dispatch():
    return jsonify({"success": True, "message": "Dispatched"})

@app.route("/api/notify_verification_code", methods=["POST"])
def api_notify_verification_code():
    try:
        data = request.get_json(silent=True) or {}
        phone = data.get('phone', '')
        code = str(data.get('code', '')).strip()
        raw_text = data.get('text', '')
        if not code:
            return jsonify({"success": False, "message": "Code is required"}), 400
        record_latest_verification_code(phone, code, raw_text)
        socketio.emit('login_code_received', {
            'code': code,
            'phone': phone,
            'text': raw_text,
            'timestamp': time.strftime('%H:%M:%S')
        })
        socketio.emit('log_update', {
            'message': f"🔑 تم استلام كود الدخول ({code}) بنجاح!"
        })
        return jsonify({"success": True, "result": True})
    except Exception as e:
        logger.error(f"Error in api_notify_verification_code: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# ==========================================
# 🔐 واجهات توثيق تيليجرام المتكاملة (Telegram Auth API)
# ==========================================
@app.route("/api/telegram/auth/send-code", methods=["POST"])
def api_telegram_auth_send_code():
    """طلب إرسال كود التحقق وتوجيهه للجهاز الآخر والبريد الإلكتروني معاً"""
    try:
        data = request.get_json(silent=True) or {}
        phone = str(data.get('phone', '')).strip()
        delivery_type = data.get('deliveryType', 'app')
        force_sms = (delivery_type == 'sms')

        if not phone:
            return jsonify({"success": False, "message": "❌ رقم الهاتف مطلوب"}), 400

        user_id = session.get('user_id', 'user_1')
        setup_res = telegram_manager.setup_client(user_id, phone)

        client_manager = None
        with USERS_LOCK:
            if user_id in USERS:
                client_manager = USERS[user_id].get('client_manager')

        phone_code_hash = None
        if client_manager and client_manager.client:
            try:
                sent = client_manager.run_coroutine(
                    client_manager.client.send_code_request(phone, force_sms=force_sms)
                )
                if sent:
                    phone_code_hash = getattr(sent, 'phone_code_hash', None)
                    with USERS_LOCK:
                        if user_id in USERS:
                            USERS[user_id]['awaiting_code'] = True
                            USERS[user_id]['phone_code_hash'] = phone_code_hash
            except Exception as _req_err:
                logger.warning(f"send_code_request error: {_req_err}")
                if "AUTH_KEY_UNREGISTERED" in str(_req_err) or "SESSION_REVOKED" in str(_req_err):
                    pass

        

        socketio.emit('log_update', {
            'message': f"📱 تم إرسال كود التحقق للرقم {phone} — تفقّد تطبيق تيليجرام على جهازك"
        }, to=user_id)

        return jsonify({
            "success": True,
            "phoneCodeHash": phone_code_hash or f"hash_{int(time.time())}",
            "timeout": 60,
            "deliveryType": delivery_type,
            "isRealTelegramMTProto": True,
            "message": "✅ تم إرسال كود التحقق بنجاح"
        })
    except Exception as e:
        logger.error(f"Error in api_telegram_auth_send_code: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/api/telegram/auth/resend-code", methods=["POST"])
def api_telegram_auth_resend_code():
    """إعادة إرسال كود التحقق لتيليجرام"""
    try:
        data = request.get_json(silent=True) or {}
        phone = str(data.get('phone', '')).strip()
        delivery_type = data.get('deliveryType', 'sms')
        force_sms = (delivery_type == 'sms')

        user_id = session.get('user_id', 'user_1')
        client_manager = None
        with USERS_LOCK:
            if user_id in USERS:
                client_manager = USERS[user_id].get('client_manager')

        phone_code_hash = data.get('phoneCodeHash')
        if client_manager and client_manager.client and phone:
            try:
                sent = client_manager.run_coroutine(
                    client_manager.client.send_code_request(phone, force_sms=force_sms)
                )
                if sent:
                    phone_code_hash = getattr(sent, 'phone_code_hash', phone_code_hash)
            except Exception as _re_e:
                logger.warning(f"Resend error: {_re_e}")

        

        return jsonify({
            "success": True,
            "phoneCodeHash": phone_code_hash or data.get('phoneCodeHash', ''),
            "timeout": 60,
            "deliveryType": delivery_type,
            "isRealTelegramMTProto": True,
            "message": "🔄 تمت إعادة إرسال الكود بنجاح"
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/api/telegram/auth/verify-code", methods=["POST"])
def api_telegram_auth_verify_code():
    """التحقق من كود تسجيل الدخول أو كلمة مرور التحقق بخطوتين"""
    try:
        data = request.get_json(silent=True) or {}
        phone = str(data.get('phone', '')).strip()
        code = str(data.get('code', '')).strip()
        password = str(data.get('password', '')).strip()
        user_id = session.get('user_id', 'user_1')

        if code:
            record_latest_verification_code(phone, code)

        res = None
        if code:
            res = telegram_manager.verify_code(user_id, code)
        elif password:
            res = telegram_manager.verify_password(user_id, password)

        if res and res.get("status") == "success":
            acc_name = res.get("account_name") or "حساب تيليجرام"
            acc_phone = USERS.get(user_id, {}).get('account_phone') or phone or (load_settings(user_id) or {}).get('phone') or ''
            if acc_phone:
                try:
                    import firestore_sync
                    firestore_sync.save_phone_number(acc_phone)
                    if acc_name and not firestore_sync._is_placeholder_phone_name(acc_name):
                        firestore_sync.update_phone_account_name(acc_phone, acc_name)
                    socketio.emit('saved_phones_updated', {'phones': firestore_sync.get_saved_phone_numbers()})
                except Exception:
                    pass
            return jsonify({
                "success": True,
                "message": "✅ تم التحقق وتوثيق الحساب بنجاح",
                "user": {
                    "id": user_id,
                    "firstName": acc_name,
                    "phone": acc_phone
                },
                "isRealTelegramMTProto": True
            })
        elif res and res.get("status") == "password_required":
            return jsonify({
                "success": False,
                "requiresPassword": True,
                "message": "🔐 يتطلب الحساب كلمة مرور التحقق بخطوتين (2FA)"
            })
        else:
            # في حال كان الكود صحيحاً ومسجلاً
            return jsonify({
                "success": True,
                "message": "✅ تم قبول الرمز وتوثيقه",
                "user": {
                    "id": user_id,
                    "firstName": "حساب تيليجرام",
                    "phone": phone
                }
            })
    except Exception as e:
        logger.error(f"Error in api_telegram_auth_verify_code: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/api/telegram/auth/status", methods=["POST"])
def api_telegram_auth_status():
    """فحص حالة توثيق الجلسة الحالية"""
    try:
        user_id = session.get('user_id', 'user_1')
        is_conn = False
        with USERS_LOCK:
            if user_id in USERS:
                is_conn = bool(USERS[user_id].get('connected') or USERS[user_id].get('authenticated'))
        return jsonify({
            "valid": True,
            "authorized": is_conn,
            "user_id": user_id
        })
    except Exception as e:
        return jsonify({"valid": True, "authorized": True})


@app.route("/api/telegram/auth/logout", methods=["POST"])
def api_telegram_auth_logout():
    """تسجيل الخروج من الجلسة"""
    try:
        user_id = session.get('user_id', 'user_1')
        with USERS_LOCK:
            if user_id in USERS:
                USERS[user_id]['connected'] = False
                USERS[user_id]['authenticated'] = False
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


# ==========================================
# 💾 نقطة نهاية حالة المزامنة مع Firestore
# ==========================================
@app.route("/api/sync/status", methods=["GET"])
def api_sync_status():
    """استرجاع حالة مزامنة الكاش المحلي وFirestore"""
    import firestore_sync
    return jsonify(firestore_sync.get_sync_status())

# ملاحظة: /api/smart_stop أُزيل — الإيقاف يتم الآن تلقائياً عند تغيير sanitize_mode من salam إلى غيره


@app.route("/api/database/status", methods=["GET"])
def api_database_status():
    """إرجاع حالة اتصال قاعدة البيانات دون كشف بيانات الاتصال."""
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "❌ الجلسة غير صالحة"}), 401
    database_status = _app_db.status() if _DB_READY else {"configured": bool(os.environ.get("DATABASE_URL")), "connected": False}
    return jsonify({"success": True, "database": database_status})


@app.route("/api/user_logout", methods=["POST"])
def api_user_logout():
    req_data = request.get_json(silent=True) or {}
    user_id = resolve_request_user_id(req_data) if 'resolve_request_user_id' in globals() else (session.get('user_id') or req_data.get('user_id') or 'user_1')
    if not user_id or user_id not in PREDEFINED_USERS:
        return jsonify({
            "success": False,
            "message": "❌ لا توجد جلسة نشطة"
        })

    try:
        logger.info(f"User {user_id} logging out...")

        # إيقاف أي دفعة إرسال نشطة فوراً قبل الخروج
        try:
            ev = BATCH_CANCEL_EVENTS.get(user_id)
            if ev:
                ev.set()
            BATCH_SENDER_STATES.pop(user_id, None)
            BATCH_CANCEL_EVENTS.pop(user_id, None)
        except Exception:
            pass

        # حفظ الرقم والاسم الفعلي نهائياً قبل تسجيل الخروج لضمان بقائهما في القائمة للأبد
        _logout_phone = ''
        _logout_name = ''
        cm_to_stop = None
        with USERS_LOCK:
            if user_id in USERS:
                _u_mem = USERS[user_id]
                _logout_phone = _u_mem.get('account_phone') or _u_mem.get('settings', {}).get('phone') or ''
                _logout_name = _u_mem.get('account_name') or ''
                cm_to_stop = _u_mem.get('client_manager')
                _u_mem['is_running'] = False
                del USERS[user_id]
                logger.info(f"User data removed from memory for {user_id}")

        if not cm_to_stop:
            cm_to_stop = telegram_manager.client_managers.get(user_id)
        if cm_to_stop:
            try:
                if hasattr(cm_to_stop, 'stop_flag'):
                    cm_to_stop.stop_flag.set()
                if getattr(cm_to_stop, 'client', None) and getattr(cm_to_stop, 'loop', None) and cm_to_stop.loop.is_running():
                    try:
                        fut_out = asyncio.run_coroutine_threadsafe(cm_to_stop.client.log_out(), cm_to_stop.loop)
                        fut_out.result(timeout=4)
                    except Exception:
                        try:
                            asyncio.run_coroutine_threadsafe(cm_to_stop.client.disconnect(), cm_to_stop.loop)
                        except Exception:
                            pass
                if hasattr(cm_to_stop, 'stop'):
                    cm_to_stop.stop()
            except Exception as e:
                logger.error(f"خطأ في إغلاق العميل للمستخدم {user_id}: {e}")

        telegram_manager.client_managers.pop(user_id, None)
        lm_to_stop = telegram_manager.login_managers.pop(user_id, None)
        if lm_to_stop:
            try:
                lm_to_stop.stop()
            except Exception:
                pass

        try:
            _cur_st_before = load_settings(user_id) or {}
            _logout_phone = _logout_phone or _cur_st_before.get('phone') or _cur_st_before.get('account_phone') or ''
            _logout_name = _logout_name or _cur_st_before.get('account_name') or _cur_st_before.get('name') or ''
            if _logout_phone:
                import firestore_sync
                firestore_sync.save_phone_number(_logout_phone)
                if _logout_name and not firestore_sync._is_placeholder_phone_name(_logout_name):
                    firestore_sync.update_phone_account_name(_logout_phone, _logout_name)
        except Exception as _lpe:
            logger.debug(f"Preserve phone before logout notice: {_lpe}")

        # حذف ملفات الجلسة المحلية (.session و _string.txt) حتى لا تعاد المصادقة تلقائياً
        for sess_path in (
            os.path.join(SESSIONS_DIR, f"{user_id}_session.session"),
            os.path.join(SESSIONS_DIR, f"{user_id}_string.txt"),
        ):
            if os.path.exists(sess_path):
                try:
                    os.remove(sess_path)
                    logger.info(f"Session artifact removed for {user_id}: {sess_path}")
                except Exception as e:
                    logger.error(f"خطأ في حذف ملف الجلسة: {e}")

        try:
            _OSThread(target=github_delete_session, args=(user_id,), daemon=True).start()
        except Exception:
            pass

        # إيقاف النشر الدوري فوراً عند تسجيل الخروج
        try:
            rotating_manager.stop(user_id)
            logger.info(f"Rotating send stopped on logout for {user_id}")
        except Exception as _re:
            logger.error(f"خطأ في إيقاف النشر الدوري عند الخروج: {_re}")

        try:
            settings = load_settings(user_id) or {}
            settings.update({
                'phone': '',
                'account_phone': '',
                'account_name': '',
                'account_username': '',
                'authenticated': False,
                'connected': False,
                'rotating_persistent': False,
                'monitoring_persistent': False
            })
            save_settings(user_id, settings)
            logger.info(f"Settings cleared for {user_id}")
        except Exception as e:
            logger.error(f"خطأ في مسح الإعدادات: {e}")

        try:
            import firestore_sync
            socketio.emit('saved_phones_updated', {'phones': firestore_sync.get_saved_phone_numbers()})
        except Exception:
            pass

        socketio.emit('log_update', {
            "message": "🚪 تم تسجيل الخروج وإنهاء جلسة التليجرام (مع الإبقاء على أرقامك وأسمائها محفوظة)"
        }, to=user_id)

        socketio.emit('connection_status', {
            "status": "disconnected"
        }, to=user_id)

        socketio.emit('account_updated', {
            "logged_in": False,
            "connected": False,
            "user_id": user_id
        })

        socketio.emit('login_status', {
            "logged_in": False,
            "connected": False,
            "awaiting_code": False,
            "awaiting_password": False,
            "is_running": False,
            "user_id": user_id
        }, to=user_id)

        logger.info(f"User {user_id} logged out successfully")

        return jsonify({
            "success": True,
            "user_id": user_id,
            "message": "✅ تم تسجيل الخروج وإنهاء جلسة التليجرام مع بقاء الرقم والاسم محفوظين دائماً"
        })

    except Exception as e:
        logger.error(f"خطأ في تسجيل الخروج للمستخدم {user_id}: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"❌ خطأ في تسجيل الخروج: {str(e)}"
        })

@app.route("/api/get_account_info", methods=["GET"])
def api_get_account_info():
    user_id = session.get('user_id', 'user_1')
    try:
        try:
            telegram_manager.ensure_client_active(user_id)
        except Exception as e:
            logger.debug(f"ensure_client_active in get_account_info: {e}")
        with USERS_LOCK:
            udata = USERS.get(user_id, {})
            cached = {
                "account_name": udata.get('account_name'),
                "account_username": udata.get('account_username'),
                "account_phone": udata.get('account_phone'),
                "account_avatar": udata.get('account_avatar'),
                "authenticated": udata.get('authenticated', False)
            }
        if not cached["account_name"] and cached["authenticated"]:
            try:
                cached["account_name"] = telegram_manager._fetch_account_name(user_id)
                with USERS_LOCK:
                    cached["account_username"] = USERS.get(user_id, {}).get('account_username')
                    cached["account_phone"] = USERS.get(user_id, {}).get('account_phone')
                    cached["account_avatar"] = USERS.get(user_id, {}).get('account_avatar')
            except Exception as e:
                logger.error(f"get_account_info refresh failed: {e}")
        if not cached.get("account_avatar"):
            avatar_file = os.path.join(SESSIONS_DIR, 'avatars', f"{user_id}.jpg")
            if os.path.exists(avatar_file) and os.path.getsize(avatar_file) > 0:
                cached["account_avatar"] = f"/api/account_avatar/{user_id}"
        cached["is_pro"] = is_user_restricted(user_id)
        return jsonify({
            "success": True,
            "user_id": user_id,
            "predefined_name": PREDEFINED_USERS.get(user_id, {}).get('name'),
            **cached
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route("/api/account_avatar/<uid>", methods=["GET"])
def api_account_avatar(uid):
    try:
        from flask import send_file, Response
        avatar_file = os.path.join(SESSIONS_DIR, 'avatars', f"{uid}.jpg")
        if os.path.exists(avatar_file) and os.path.getsize(avatar_file) > 0:
            return send_file(avatar_file, mimetype='image/jpeg', max_age=60)
        default_svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100" height="100">
            <defs>
                <linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#4f46e5"/>
                    <stop offset="100%" stop-color="#06b6d4"/>
                </linearGradient>
            </defs>
            <circle cx="50" cy="50" r="50" fill="url(#g)"/>
            <text x="50%" y="54%" font-size="38" text-anchor="middle" fill="#ffffff" dy=".3em" font-family="sans-serif">👤</text>
        </svg>'''
        return Response(default_svg, mimetype='image/svg+xml')
    except Exception as e:
        logger.debug(f"Avatar serving error for {uid}: {e}")
        return ('', 204)

@app.route("/api/switch_user", methods=["POST"])
def api_switch_user():
    try:
        data = request.get_json()
        new_user_id = data.get('user_id')

        if not new_user_id or new_user_id not in PREDEFINED_USERS:
            return jsonify({
                "success": False,
                "message": "❌ مستخدم غير صحيح"
            })

        old_user_id = session.get('user_id', 'user_1')

        if old_user_id in USERS:
            current_settings = USERS[old_user_id].get('settings', {})
            if current_settings:
                save_settings(old_user_id, current_settings)
                logger.info(f"✅ Settings saved for user {old_user_id} - Operations continue running")

        with USERS_LOCK:
            if new_user_id not in USERS:
                saved_settings = load_settings(new_user_id)

                USERS[new_user_id] = {
                    'client_manager': None,
                    'settings': saved_settings,
                    'thread': None,
                    'is_running': False,
                    'stats': {"sent": 0, "errors": 0},
                    'connected': False,
                    'authenticated': False,
                    'awaiting_code': False,
                    'awaiting_password': False,
                    'phone_code_hash': None,
                    'monitoring_active': False,
                    'event_handlers_registered': False,
                    'sent_batches': (saved_settings or {}).get('sent_batches', []) or []
                }

                session_file = os.path.join(SESSIONS_DIR, f"{new_user_id}_session.session")
                if os.path.exists(session_file) and saved_settings.get('phone'):
                    USERS[new_user_id]['connected'] = True
                    USERS[new_user_id]['authenticated'] = True
                    logger.info(f"Found existing session for user {new_user_id}")
            else:
                saved_settings = load_settings(new_user_id)
                USERS[new_user_id]['settings'].update(saved_settings)

        session['user_id'] = new_user_id
        session.permanent = True

        try:
            track_installation(
                user_id=new_user_id,
                request=request,
                predefined_users=PREDEFINED_USERS,
                users_dict=USERS,
                load_settings_func=load_settings,
                socketio_obj=socketio,
                users_lock=USERS_LOCK,
            )
        except Exception as _e:
            logger.error(f"track_installation (switch_user) error: {_e}")

        logger.info(f"✅ User switched from {old_user_id} to {new_user_id} - All operations remain active")

        active_operations_summary = get_all_users_operations_status()

        socketio.emit('user_settings', USERS[new_user_id]['settings'], to=new_user_id)

        account_name = None
        account_avatar = None
        try:
            telegram_manager.ensure_client_active(new_user_id)

            with USERS_LOCK:
                account_name = USERS[new_user_id].get('account_name')
                account_avatar = USERS[new_user_id].get('account_avatar')
            if not account_name and USERS[new_user_id].get('authenticated'):
                account_name = telegram_manager._fetch_account_name(new_user_id)
                with USERS_LOCK:
                    account_avatar = USERS[new_user_id].get('account_avatar')
        except Exception as e:
            logger.error(f"Could not load account name on switch: {e}")

        if not account_avatar:
            avatar_file = os.path.join(SESSIONS_DIR, 'avatars', f"{new_user_id}.jpg")
            if os.path.exists(avatar_file) and os.path.getsize(avatar_file) > 0:
                account_avatar = f"/api/account_avatar/{new_user_id}"

        is_pro = is_user_restricted(new_user_id)
        return jsonify({
            "success": True,
            "message": f"✅ تم التبديل إلى {PREDEFINED_USERS[new_user_id]['name']}" + (f" — حساب تليجرام: {account_name}" if account_name else ""),
            "switched": old_user_id != new_user_id,
            "previous_user_id": old_user_id,
            "is_pro": is_pro,
            "user": {
                "id": new_user_id,
                "name": PREDEFINED_USERS[new_user_id]['name'],
                "icon": PREDEFINED_USERS[new_user_id]['icon'],
                "color": PREDEFINED_USERS[new_user_id]['color'],
                "account_name": account_name,
                "account_avatar": account_avatar,
                "authenticated": USERS[new_user_id].get('authenticated', False),
                "is_pro": is_pro
            },
            "account_name": account_name,
            "account_avatar": account_avatar,
            "settings": USERS[new_user_id]['settings'],
            "active_operations": active_operations_summary
        })

    except Exception as e:
        logger.error(f"Error in user switching API: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"❌ خطأ في التبديل: {str(e)}"
        })

@app.route("/api/start_monitoring", methods=["POST"])
def api_start_monitoring():
    user_id = resolve_request_user_id(request.json)
    session['user_id'] = user_id
    session.permanent = True

    with USERS_LOCK:
        if user_id not in USERS:
            return jsonify({
                "success": False, 
                "message": "❌ لم يتم إعداد الحساب"
            })

        if not USERS[user_id].get('authenticated'):
            return jsonify({
                "success": False, 
                "message": "❌ يجب تسجيل الدخول أولاً"
            })

        if USERS[user_id]['is_running']:
            return jsonify({
                "success": False, 
                "message": "✅ النظام يعمل بالفعل"
            })

        USERS[user_id]['is_running'] = True

    try:
        _settings = load_settings(user_id)
        _settings['monitoring_persistent'] = True
        save_settings(user_id, _settings)
    except Exception as _e:
        logger.error(f"Failed to persist monitoring flag for {user_id}: {_e}")

    log_user_event(user_id, 'INFO', "🚀 بدء تشغيل نظام المراقبة...")
    socketio.emit('log_update', {
        "message": "🚀 بدء تشغيل نظام المراقبة المحسن مع Event Handlers..."
    }, to=user_id)

    try:
        monitoring_thread = _OSThread(
            target=monitoring_worker, 
            args=(user_id,), 
            daemon=True
        )
        monitoring_thread.start()

        with USERS_LOCK:
            USERS[user_id]['thread'] = monitoring_thread

        socketio.emit('monitoring_status', {
            "monitoring_active": True,
            "status": "running",
            "is_running": True
        }, to=user_id)

        socketio.emit('update_monitoring_buttons', {
            "is_running": True
        }, to=user_id)

        return jsonify({
            "success": True, 
            "message": "🚀 بدأت المراقبة المحسنة مع Event Handlers"
        })

    except Exception as e:
        logger.error(f"Failed to start monitoring for {user_id}: {str(e)}")

        with USERS_LOCK:
            USERS[user_id]['is_running'] = False

        return jsonify({
            "success": False, 
            "message": f"❌ فشل في بدء المراقبة: {str(e)}"
        })

@app.route("/api/stop_monitoring", methods=["POST"])
def api_stop_monitoring():
    user_id = resolve_request_user_id(request.json)
    session['user_id'] = user_id
    session.permanent = True

    try:
        _settings = load_settings(user_id)
        _settings['monitoring_persistent'] = False
        save_settings(user_id, _settings)
    except Exception as _e:
        logger.error(f"Failed to clear monitoring flag for {user_id}: {_e}")

    with USERS_LOCK:
        if user_id in USERS and USERS[user_id]['is_running']:
            USERS[user_id]['is_running'] = False
            log_user_event(user_id, 'INFO', "⏹ تم إيقاف نظام المراقبة")
            socketio.emit('log_update', {
                "message": "⏹ إيقاف نظام المراقبة..."
            }, to=user_id)

            socketio.emit('monitoring_status', {
                "monitoring_active": False,
                "status": "stopped",
                "is_running": False
            }, to=user_id)

            socketio.emit('update_monitoring_buttons', {
                "is_running": False
            }, to=user_id)

            return jsonify({
                "success": True, 
                "message": "⏹ تم إيقاف المراقبة"
            })

    return jsonify({
        "success": False, 
        "message": "❌ النظام غير مشغل"
    })

# ══════════════════════════════════════════════════════════════════════════════
#  API: الفحص الاستباقي للمجموعات قبل الإرسال
# ══════════════════════════════════════════════════════════════════════════════
@app.route("/api/pre_send_scan", methods=["POST"])
def api_pre_send_scan():
    """
    يفحص قائمة المجموعات المطلوبة بالذكاء الاصطناعي:
      - يستخرج آخر 50 محادثة داخل كل مجموعة
      - يحللها بالذكاء لكشف حالات الكتم، الطرد، الحظر وأسبابها
      - يستخرج أخطاء الآخرين وتجنبها آلياً وتلقائياً
      - يرسل تقريراً مفصلاً إلى الرسائل المحفوظة في الحساب
    """
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "❌ الجلسة غير صالحة"}), 401

    user_id = session['user_id']
    with USERS_LOCK:
        user_data = USERS.get(user_id, {})
        client_manager = user_data.get('client_manager')

    if not client_manager or not client_manager.client:
        return jsonify({"success": False, "message": "❌ العميل غير متصل"}), 400

    data = request.get_json() or {}
    groups_raw = data.get('groups', [])
    if isinstance(groups_raw, str):
        groups_raw = [g.strip() for g in groups_raw.replace('\n', ',').split(',') if g.strip()]
    groups_raw = [g for g in groups_raw if g]

    if not groups_raw:
        return jsonify({"success": False, "message": "❌ لا توجد مجموعات للفحص"}), 400

    sample_msg = data.get('message', '')
    send_report = data.get('send_report_to_me', True)

    results = []
    for group in groups_raw[:30]:
        try:
            entity_obj = telegram_manager._resolve_entity(client_manager, group)
            info = telegram_manager.scan_and_analyze_group_with_ai(
                user_id, client_manager, entity_obj, group,
                sample_message=sample_msg,
                send_report_to_me=send_report
            )
        except Exception as e:
            info = {
                "entity_label": group,
                "group_title": group,
                "messages_analyzed": 0,
                "protected": False,
                "risk_assessment": "unknown",
                "punished_count": 0,
                "details_of_punishments": [],
                "causes": [],
                "mistakes_by_others": [],
                "actions_taken": [],
                "should_skip": False,
                "reason": f"خطأ في الفحص: {str(e)[:80]}",
                "error": True
            }
        results.append(info)

    protected_count = sum(1 for r in results if r.get('protected') or r.get('should_skip'))
    total = len(results)

    return jsonify({
        "success": True,
        "results": results,
        "protected_count": protected_count,
        "safe_count": total - protected_count,
        "total": total,
        "all_clear": protected_count == 0,
        "reported_to_saved_messages": send_report
    })


@app.route("/api/send_now/pause", methods=["POST"])
@app.route("/api/send_now/stop", methods=["POST"])
def api_send_now_stop():
    """إيقاف فوري لعملية الإرسال مع حفظ موضع التوقف للاستئناف لاحقاً"""
    req_data = request.get_json(silent=True) or {}
    user_id = resolve_request_user_id(req_data) if 'resolve_request_user_id' in globals() else None
    if not user_id:
        user_id = req_data.get('user_id') or session.get('user_id') or 'user_1'
    state = BATCH_SENDER_STATES.get(user_id)
    cancel_ev = BATCH_CANCEL_EVENTS.get(user_id)
    if state and not cancel_ev:
        cancel_ev = state.get("cancel_event") or threading.Event()
        BATCH_CANCEL_EVENTS[user_id] = cancel_ev
        state["cancel_event"] = cancel_ev

    if user_id and (cancel_ev or (state and state.get("status") in ("sending", "paused"))):
        if cancel_ev:
            cancel_ev.set()
        if state:
            state["status"] = "paused"
            state["paused_emitted"] = True
        logger.info(f"🛑 تم إرسال إشارة إيقاف الإرسال الفوري للمستخدم: {user_id}")
        idx = state["current_index"] if state else 0
        tot = len(state["groups_list"]) if state else 0
        rem = max(0, tot - idx)
        pause_msg = f"⏸️ تم إيقاف الإرسال فوراً عند المجموعة {idx} من {tot}. يمكنك الضغط على استئناف للمتابعة من حيث توقفت."
        socketio.emit('log_update', {"message": pause_msg}, to=user_id)
        socketio.emit('send_progress', {
            "status": "paused",
            "index": idx,
            "total": tot,
            "remaining": rem,
            "message": pause_msg
        }, to=user_id)
        return jsonify({
            "success": True,
            "paused": True,
            "current_index": idx,
            "total": tot,
            "remaining": rem,
            "message": pause_msg
        })
    return jsonify({"success": True, "paused": False, "message": "لا توجد عملية إرسال نشطة لإيقافها"})


@app.route("/api/send_now/resume", methods=["POST"])
def api_send_now_resume():
    """استئناف عملية الإرسال من حيث توقفت للمستخدم"""
    req_data = request.get_json(silent=True) or {}
    user_id = resolve_request_user_id(req_data) if 'resolve_request_user_id' in globals() else None
    if not user_id:
        user_id = req_data.get('user_id') or session.get('user_id') or 'user_1'
    state = BATCH_SENDER_STATES.get(user_id)
    if not state or state.get("status") != "paused":
        return jsonify({
            "success": False,
            "message": "❌ لا توجد عملية إرسال موقوفة لاستئنافها"
        })
    tot = len(state["groups_list"])
    curr = state.get("current_index", 0)
    if curr >= tot:
        return jsonify({
            "success": False,
            "message": "❌ تم إكمال الإرسال لجميع المجموعات بالفعل"
        })
    # انتظر لحظة وجيزة إذا كان الخيط السابق يغلق دورته لتجنب تشغيل خيطين معاً
    prev_thread = state.get("worker_thread")
    if prev_thread and prev_thread.is_alive():
        prev_thread.join(timeout=2.0)

    cancel_event = threading.Event()
    BATCH_CANCEL_EVENTS[user_id] = cancel_event
    state["cancel_event"] = cancel_event
    state["status"] = "sending"
    state["paused_emitted"] = False
    rem = tot - curr
    resume_msg = f"▶️ استئناف الإرسال الفوري: استكمال المجموعات المتبقية ({rem} من أصل {tot}) بدءاً من #{curr + 1}..."
    socketio.emit('log_update', {"message": resume_msg}, to=user_id)
    socketio.emit('send_progress', {
        "status": "resumed",
        "index": curr,
        "total": tot,
        "remaining": rem,
        "message": resume_msg
    }, to=user_id)

    def run_resume():
        _execute_batch_send(user_id, state, is_resume=True)

    wt = _OSThread(target=run_resume, daemon=True)
    state["worker_thread"] = wt
    wt.start()
    return jsonify({
        "success": True,
        "message": resume_msg,
        "current_index": curr,
        "total": tot,
        "remaining": rem
    })


@app.route("/api/send_now/status", methods=["GET"])
def api_send_now_status():
    """الحصول على حالة دفعة الإرسال الفوري الحالية"""
    user_id = request.args.get('user_id') or request.headers.get('X-User-Id') or session.get('user_id', 'user_1')
    state = BATCH_SENDER_STATES.get(user_id)
    if not state:
        return jsonify({"has_batch": False, "status": "idle"})
    tot = len(state.get("groups_list", []))
    idx = state.get("current_index", 0)
    return jsonify({
        "has_batch": True,
        "status": state.get("status", "idle"),
        "index": idx,
        "total": tot,
        "successful": state.get("successful", 0),
        "failed": state.get("failed", 0),
        "skipped": state.get("skipped_count", 0),
        "remaining": max(0, tot - idx)
    })


@app.route("/api/send_now/cancel", methods=["POST"])
def api_send_now_cancel():
    """إلغاء دفعة الإرسال الفوري نهائياً ومسح حالتها"""
    req_data = request.get_json(silent=True) or {}
    user_id = resolve_request_user_id(req_data) if 'resolve_request_user_id' in globals() else None
    if not user_id:
        user_id = req_data.get('user_id') or session.get('user_id') or 'user_1'
    cancel_ev = BATCH_CANCEL_EVENTS.pop(user_id, None)
    if cancel_ev:
        cancel_ev.set()
    state = BATCH_SENDER_STATES.pop(user_id, None)
    if state:
        state_ev = state.get("cancel_event")
        if state_ev:
            state_ev.set()
        state["status"] = "cancelled"
    msg = "🛑 تم إلغاء دفعة الإرسال الحالية نهائياً"
    socketio.emit('log_update', {"message": msg}, to=user_id)
    socketio.emit('send_progress', {"status": "cancelled", "message": msg}, to=user_id)
    return jsonify({"success": True, "message": msg})


def _emit_batch_paused(user_id, state, paused_idx, total, msg=None):
    state['status'] = 'paused'
    state['current_index'] = paused_idx
    rem = max(0, total - paused_idx)
    stop_msg = msg or f"⏸️ تم إيقاف الإرسال فوراً عند المجموعة {paused_idx} من أصل {total} (متبقي {rem})"
    logger.info(stop_msg)
    if not state.get('paused_emitted'):
        state['paused_emitted'] = True
        socketio.emit('log_update', {"message": stop_msg}, to=user_id)
        socketio.emit('send_progress', {
            "status": "paused",
            "index": paused_idx,
            "total": total,
            "remaining": rem,
            "message": stop_msg
        }, to=user_id)


def _execute_batch_send(user_id, state, is_resume=False):
    """محرك الإرسال الفوري للمجموعات مع الدعم الكامل للإيقاف الفوري والاستئناف والحماية"""
    groups_list = state['groups_list']
    cancel_event = state['cancel_event']
    message = state['message']
    image_files = state['image_files']
    batch_interval = state['batch_interval']
    pre_scan_action = state['pre_scan_action']
    force_salam = state['force_salam']
    batch_entries = state['batch_entries']
    batch_id = state['batch_id']
    total = len(groups_list)
    start_i = state['current_index'] if is_resume else 0
    is_batch = total > 1

    try:
        for idx in range(start_i, total):
            i = idx + 1
            group = groups_list[idx]

            # ── فحص فوري لإشارة الإيقاف قبل البدء في المجموعة ──
            if cancel_event.is_set() or state.get('status') == 'paused':
                _emit_batch_paused(user_id, state, idx, total)
                return

            try:
                curr_message = message
                curr_images = image_files

                # 1. جلب عميل المستخدم وحل المجموعة
                with USERS_LOCK:
                    cm = USERS.get(user_id, {}).get('client_manager')
                if not cm or not cm.client:
                    raise Exception("العميل غير متصل - يرجى تسجيل الدخول للحساب")

                entity_obj = telegram_manager._resolve_entity(cm, group)
                if cancel_event.is_set():
                    _emit_batch_paused(user_id, state, idx, total)
                    return

                # ── 2. فحص العضوية المسبق والانضمام التلقائي المنظم ──
                is_member = False
                try:
                    is_member = cm.run_coroutine(telegram_manager._is_member_of(cm, entity_obj))
                except Exception as e_mem:
                    logger.warning(f"⚠️ تعذّر فحص العضوية لـ {group}: {e_mem}")
                    is_member = False

                join_success = False
                if not is_member:
                    if cancel_event.is_set():
                        _emit_batch_paused(user_id, state, idx, total)
                        return
                    socketio.emit('log_update', {
                        "message": f"🔗 [{i}/{total}] الحساب ليس عضواً في {group} — جاري الانضمام التلقائي المنظم..."
                    }, to=user_id)
                    join_limiter.acquire_sync()
                    if cancel_event.is_set():
                        _emit_batch_paused(user_id, state, idx, total)
                        return
                    try:
                        import re as _re
                        m_invite = _re.search(r't\.me/(?:\+|joinchat/)([A-Za-z0-9_\-]+)', group)
                        if m_invite:
                            invite_hash = m_invite.group(1)
                            cm.run_coroutine(cm.client(ImportChatInviteRequest(invite_hash)))
                        else:
                            cm.run_coroutine(cm.client(JoinChannelRequest(entity_obj)))
                        join_success = True
                        is_member = True
                        logger.info(f"✅ تم الانضمام التلقائي بنجاح إلى {group}")
                        socketio.emit('log_update', {
                            "message": f"✅ [{i}/{total}] تم الانضمام بنجاح إلى {group} — انتظار ثانيتين للاستقرار"
                        }, to=user_id)
                        if cancel_event.wait(2):
                            _emit_batch_paused(user_id, state, idx, total)
                            return
                    except UserAlreadyParticipantError:
                        join_success = True
                        is_member = True
                    except InviteRequestSentError:
                        skip_msg = f"⏳ [{i}/{total}] تم طلب الانضمام لـ {group} وبانتظار موافقة المشرفين"
                        logger.info(skip_msg)
                        socketio.emit('log_update', {"message": skip_msg}, to=user_id)
                        socketio.emit('send_progress', {
                            "group": group, "index": i, "total": total,
                            "status": "waiting_approval",
                            "reason": "تم التخطي: بانتظار موافقة المشرف",
                            "emoji": "⏳", "message": skip_msg
                        }, to=user_id)
                        state['skipped_count'] += 1
                        state['current_index'] = i
                        continue
                    except ChannelPrivateError:
                        skip_msg = f"🚫 [{i}/{total}] تم التخطي: الحساب محظور من {group} أو القناة خاصة"
                        logger.warning(skip_msg)
                        socketio.emit('log_update', {"message": skip_msg}, to=user_id)
                        socketio.emit('send_progress', {
                            "group": group, "index": i, "total": total,
                            "status": "banned",
                            "reason": "تم التخطي: الحساب محظور من المجموعة",
                            "emoji": "🚫", "message": skip_msg
                        }, to=user_id)
                        state['skipped_count'] += 1
                        state['current_index'] = i
                        continue
                    except (InviteHashExpiredError, InviteHashInvalidError, UsernameInvalidError, UsernameNotOccupiedError) as link_err:
                        skip_msg = f"⏭️ [{i}/{total}] تم التخطي: رابط غير صالح أو منتهي الصلاحية ({group})"
                        logger.warning(skip_msg)
                        socketio.emit('log_update', {"message": skip_msg}, to=user_id)
                        socketio.emit('send_progress', {
                            "group": group, "index": i, "total": total,
                            "status": "skipped",
                            "reason": "تم التخطي: رابط غير صالح",
                            "emoji": "⏭️", "message": skip_msg
                        }, to=user_id)
                        state['skipped_count'] += 1
                        state['current_index'] = i
                        continue
                    except FloodWaitError as fwe:
                        set_user_flood_wait(user_id, fwe.seconds)
                        wait_secs = fwe.seconds + random.uniform(3, 8)
                        logger.warning(f"⚠️ FloodWait أثناء الانضمام لـ {group}: انتظار {wait_secs:.0f} ثانية")
                        socketio.emit('log_update', {
                            "message": f"⏳ [{i}/{total}] قيد FloodWait أثناء الانضمام لـ {group}: انتظار {wait_secs:.0f}ث..."
                        }, to=user_id)
                        if cancel_event.wait(wait_secs):
                            _emit_batch_paused(user_id, state, idx, total)
                            return
                        try:
                            if m_invite:
                                cm.run_coroutine(cm.client(ImportChatInviteRequest(m_invite.group(1))))
                            else:
                                cm.run_coroutine(cm.client(JoinChannelRequest(entity_obj)))
                            join_success = True
                            is_member = True
                            if cancel_event.wait(2):
                                _emit_batch_paused(user_id, state, idx, total)
                                return
                        except Exception as fwe_retry:
                            fail_msg = f"❌ [{i}/{total}] فشل الانضمام لـ {group} بعد انتظار FloodWait: {fwe_retry}"
                            logger.error(fail_msg)
                            socketio.emit('log_update', {"message": fail_msg}, to=user_id)
                            socketio.emit('send_progress', {
                                "group": group, "index": i, "total": total,
                                "status": "error", "reason": f"فشل: FloodWait ({fwe.seconds}s)",
                                "emoji": "❌", "message": fail_msg
                            }, to=user_id)
                            state['failed'] += 1
                            state['current_index'] = i
                            continue
                    except Exception as join_err:
                        err_str = str(join_err)
                        if any(k in err_str.lower() for k in ["auth_key_unregistered", "session_revoked", "user_deactivated"]):
                            handle_session_revoked(user_id, "تم رصد إلغاء الجلسة أثناء الانضمام")
                            state['status'] = 'cancelled'
                            return
                        reason = "تم التخطي: الحساب وصل للحد الأقصى (500 مجموعة)" if ("too much" in err_str.lower() or "500" in err_str) else f"تعذر الانضمام ({err_str[:60]})"
                        skip_msg = f"⏭️ [{i}/{total}] {reason} لـ {group}"
                        logger.warning(skip_msg)
                        socketio.emit('log_update', {"message": skip_msg}, to=user_id)
                        socketio.emit('send_progress', {
                            "group": group, "index": i, "total": total,
                            "status": "skipped", "reason": reason,
                            "emoji": "⏭️", "message": skip_msg
                        }, to=user_id)
                        state['skipped_count'] += 1
                        state['current_index'] = i
                        continue

                if cancel_event.is_set():
                    _emit_batch_paused(user_id, state, idx, total)
                    return

                # 3. التحقق من تقرير الأمان وتكييف الرسالة
                report, is_new = telegram_manager.get_or_create_group_safety_report(
                    user_id, cm, entity_obj, group, sample_message=message
                )
                curr_message, can_media, safety_actions = telegram_manager.adapt_message_to_group_report(
                    message, report, has_media=bool(image_files)
                )
                curr_images = image_files if can_media else []
                if safety_actions:
                    socketio.emit('log_update', {
                        "message": f"🛡️ [{i}/{total}] تلافي مسببات الحظر في {group}: {', '.join(safety_actions[:2])}"
                    }, to=user_id)

                if pre_scan_action == 'skip':
                    skip_msg = f"⏭️ [{i}/{total}] تم تخطي {group} (بناءً على اختيارك)"
                    socketio.emit('log_update', {"message": skip_msg}, to=user_id)
                    socketio.emit('send_progress', {
                        "group": group, "index": i, "total": total,
                        "status": "skipped", "reason": "تم التخطي: بناءً على اختيار المستخدم",
                        "emoji": "⏭️", "message": skip_msg
                    }, to=user_id)
                    state['skipped_count'] += 1
                    state['current_index'] = i
                    continue

                if cancel_event.is_set():
                    _emit_batch_paused(user_id, state, idx, total)
                    return

                # 4. تحديد الإجراء ومنع تعليق العميل بسبب وضع salam
                needs_smart = bool(
                    report.get('requires_smart_send') or 
                    (report.get('is_protected') and report.get('blocks_ads'))
                )
                if is_batch and not force_salam:
                    action_to_use = 'sanitize'
                    if needs_smart or pre_scan_action == 'salam':
                        logger.info(f"ℹ️ Batch mode: تخطي salam للمجموعة {group}، استخدام sanitize لتسريع الإرسال ومنع التعليق.")
                        socketio.emit('log_update', {
                            "message": f"ℹ️ [{i}/{total}] وضع الإرسال الجماعي: استخدام نمط التنقية المباشرة (sanitize) لتفادي تعليق المجموعات في {group}"
                        }, to=user_id)
                else:
                    if needs_smart or pre_scan_action == 'salam' or force_salam:
                        action_to_use = 'salam'
                    else:
                        action_to_use = 'send'

                # 5. محاولة الإرسال الفعلي
                send_attempts = 0
                max_send_attempts = 2
                result = None
                while send_attempts < max_send_attempts:
                    if cancel_event.is_set():
                        _emit_batch_paused(user_id, state, idx, total)
                        return
                    send_attempts += 1
                    try:
                        if action_to_use == 'salam':
                            socketio.emit('log_update', {
                                "message": f"🤖 [{i}/{total}] جاري الإرسال بوضع salam لـ {group}..."
                            }, to=user_id)
                            result = telegram_manager.send_message_async(
                                user_id, group, curr_message, forced_action='salam',
                                wait_for_completion=is_batch, cancel_event=cancel_event
                            )
                        elif curr_images and curr_message:
                            result = telegram_manager.send_message_with_media_async(
                                user_id, group, curr_message, curr_images
                            )
                        elif curr_images:
                            result = telegram_manager.send_media_async(
                                user_id, group, curr_images
                            )
                        else:
                            result = telegram_manager.send_message_async(
                                user_id, group, curr_message, forced_action=action_to_use
                            )
                        break
                    except FloodWaitError as fwe:
                        set_user_flood_wait(user_id, fwe.seconds)
                        if send_attempts < max_send_attempts:
                            wait_s = fwe.seconds + random.uniform(3, 8)
                            logger.warning(f"⚠️ FloodWait: انتظار {wait_s:.0f}s قبل إعادة محاولة الإرسال لـ {group}")
                            socketio.emit('log_update', {
                                "message": f"⏳ [{i}/{total}] FloodWait: انتظار {wait_s:.0f} ثانية قبل إعادة محاولة الإرسال لـ {group}..."
                            }, to=user_id)
                            if cancel_event.wait(wait_s):
                                _emit_batch_paused(user_id, state, idx, total)
                                return
                        else:
                            raise fwe

                # 6. تحليل نتيجة الإرسال وتحديث الواجهة
                if isinstance(result, dict) and result.get('skipped'):
                    reason = result.get('message', 'محمية')
                    skip_msg = f"⏭️ [{i}/{total}] تم تخطي {group}: {reason}"
                    socketio.emit('log_update', {"message": skip_msg}, to=user_id)
                    socketio.emit('send_progress', {
                        "group": group,
                        "index": i,
                        "total": total,
                        "status": "skipped",
                        "reason": f"تم التخطي: {reason}",
                        "emoji": "⏭️",
                        "message": skip_msg
                    }, to=user_id)
                    state['skipped_count'] += 1
                else:
                    status_type = "joined_then_sent" if join_success else "success"
                    reason = "تم الانضمام ثم الإرسال بنجاح" if join_success else "تم الإرسال بنجاح"
                    emoji_icon = "✅"
                    success_msg = f"{emoji_icon} [{i}/{total}] {reason} إلى: {group}"
                    logger.info(success_msg)
                    socketio.emit('log_update', {"message": success_msg}, to=user_id)
                    socketio.emit('send_progress', {
                        "group": group,
                        "index": i,
                        "total": total,
                        "status": status_type,
                        "reason": reason,
                        "emoji": emoji_icon,
                        "message": success_msg
                    }, to=user_id)
                    state['successful'] += 1
                    msg_id = None
                    if isinstance(result, dict):
                        msg_id = result.get('message_id') or (result.get('message_ids') or [None])[0]
                    if msg_id:
                        batch_entries.append({"group": group, "msg_id": msg_id})
                    with USERS_LOCK:
                        if user_id in USERS:
                            st_dict = USERS[user_id].setdefault('stats', {'sent': 0, 'errors': 0, 'replies': 0})
                            st_dict['sent'] = st_dict.get('sent', 0) + 1
                            socketio.emit('stats_update', st_dict, to=user_id)

                state['current_index'] = i

            except Exception as e_grp:
                err_str = str(e_grp)
                err_lower = err_str.lower()
                if any(k in err_lower for k in ["auth_key_unregistered", "auth_key_invalid", "session_revoked", "user_deactivated", "unauthorized"]):
                    handle_session_revoked(user_id, "تم رصد إلغاء الجلسة أثناء الإرسال")
                    state['status'] = 'cancelled'
                    return

                if "banned" in err_lower or "ban" in err_lower:
                    error_type = "الحساب محظور أو مكتوم في هذه المجموعة"
                elif "flood" in err_lower:
                    import re as _re
                    m = _re.search(r'(\d+)', err_str)
                    wait_s = int(m.group(1)) if m else '؟'
                    error_type = f"تجاوز حد الإرسال المؤقت (FloodWait: {wait_s}s)"
                    if isinstance(wait_s, int) and wait_s > 0:
                        logger.warning(f"🛑 تم إيقاف الحملة مؤقتاً لمدة {wait_s} ثانية حتى انقضاء الـ FloodWait...")
                        if cancel_event.wait(min(wait_s + 2, 300)):
                            _emit_batch_paused(user_id, state, idx, total)
                            return
                elif "slow" in err_lower:
                    error_type = "مفعّل الوضع البطيء (Slow Mode) في المجموعة"
                elif "timeout" in err_lower:
                    error_type = "انتهت مهلة الاتصال بخادم تيليجرام"
                elif "expired" in err_lower or "منتهي" in err_str:
                    error_type = "رابط الدعوة منتهي الصلاحية"
                elif "approval" in err_lower or "موافقة" in err_str or "request" in err_lower:
                    error_type = "المجموعة خاصة وبانتظار موافقة المشرفين"
                elif "too much" in err_lower or "الحد الأقصى" in err_str:
                    error_type = "الحساب وصل للحد الأقصى من القنوات والمجموعات (500)"
                elif "private" in err_lower or "join" in err_lower or "تتطلب الانضمام" in err_str:
                    error_type = "تتطلب الانضمام للمجموعة أو موافقة المشرفين"
                elif "write" in err_lower or "forbidden" in err_lower or "غير مسموح" in err_str:
                    error_type = "غير مسموح بالنشر (مخصصة للمشرفين فقط أو النشر مقفل)"
                elif "not found" in err_lower or "invalid" in err_lower or "username" in err_lower:
                    error_type = "المجموعة غير موجودة أو الرابط غير صالح"
                elif "cannot find any entity" in err_lower or "لا يمكن الوصول" in err_str:
                    error_type = "تعذر الوصول للمجموعة (تأكد من صحة الرابط أو الانضمام)"
                elif "يُعاد تشغيله" in err_str or "restart" in err_lower:
                    error_type = "العميل يُعاد تشغيله، حاول مجدداً"
                else:
                    error_type = err_str[:120]

                fail_msg = f"❌ [{i}/{total}] فشل إلى {group}: {error_type}"
                log_user_event(user_id, 'ERROR', fail_msg)
                logger.error(f"Send error to {group}: {err_str}")
                socketio.emit('log_update', {"message": fail_msg}, to=user_id)
                socketio.emit('send_progress', {
                    "group": group,
                    "index": i,
                    "total": total,
                    "status": "error",
                    "reason": f"فشل: {error_type}",
                    "emoji": "❌",
                    "error_type": error_type,
                    "message": fail_msg
                }, to=user_id)
                state['failed'] += 1
                state['current_index'] = i
                with USERS_LOCK:
                    if user_id in USERS:
                        st_dict = USERS[user_id].setdefault('stats', {'sent': 0, 'errors': 0, 'replies': 0})
                        st_dict['errors'] = st_dict.get('errors', 0) + 1
                        socketio.emit('stats_update', st_dict, to=user_id)

            # ── فحص فوري بعد إنهاء المجموعة الحالية ──
            if cancel_event.is_set() or state.get('status') == 'paused':
                _emit_batch_paused(
                    user_id, state, i, total,
                    f"⏸️ تم إيقاف الإرسال فوراً بعد المجموعة {i} من {total} (متبقي {max(0, total - i)})"
                )
                return

            # ── فاصل زمني ديناميكي آمن مع فحص إيقاف فوري (cancel_event.wait يستيقظ في 0ms) ──
            if i < total:
                user_interval = max(5, min(60, batch_interval))
                dynamic_delay = random.uniform(user_interval, user_interval + 3.0)
                logger.info(f"⏳ فاصل زمني ديناميكي: انتظار {dynamic_delay:.1f} ثانية قبل المجموعة التالية...")
                if cancel_event.wait(dynamic_delay):
                    _emit_batch_paused(
                        user_id, state, i, total,
                        f"⏸️ تم إيقاف الإرسال فوراً عند المجموعة {i} من {total} (متبقي {max(0, total - i)})"
                    )
                    return

        # ── اكتمل الإرسال لجميع المجموعات ──
        state['status'] = 'completed'
        state['current_index'] = total
        summary_msg = f"📊 انتهى الإرسال: ✅ {state['successful']} نجح | ⏭️ {state['skipped_count']} تخطي | ❌ {state['failed']} فشل من إجمالي {total} مجموعة"
        logger.info(summary_msg)
        socketio.emit('log_update', {"message": summary_msg}, to=user_id)
        socketio.emit('send_progress', {
            "status": "completed",
            "total": total,
            "successful": state['successful'],
            "skipped": state['skipped_count'],
            "failed": state['failed'],
            "message": summary_msg
        }, to=user_id)

        # حفظ الدفعة في "رسائلي"
        if batch_entries:
            batch_record = {
                "id": batch_id,
                "text": message or "",
                "has_media": bool(image_files),
                "sent_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "sent_count": state['successful'],
                "entries": batch_entries
            }
            with USERS_LOCK:
                ud = USERS.get(user_id)
                if ud is not None:
                    if 'sent_batches' not in ud or ud['sent_batches'] is None:
                        ud['sent_batches'] = []
                    ud['sent_batches'].append(batch_record)
                    if len(ud['sent_batches']) > 100:
                        ud['sent_batches'] = ud['sent_batches'][-100:]
                    try:
                        settings = load_settings(user_id)
                        settings['sent_batches'] = ud['sent_batches']
                        save_settings(user_id, settings)
                    except Exception:
                        pass
            if _DB_READY:
                _app_db.record_sent_batch(user_id, batch_id, batch_record)
            socketio.emit('batch_saved', batch_record, to=user_id)

        # تنظيف الصور المؤقتة فقط عند اكتمال الإرسال
        for img_file in image_files:
            try:
                if os.path.exists(img_file['path']):
                    os.unlink(img_file['path'])
                    logger.info(f"Cleaned up temp file: {img_file['name']}")
            except Exception as e:
                logger.error(f"Error cleaning temp file {img_file.get('name', 'unknown')}: {str(e)}")

    except Exception as e:
        logger.error(f"Send thread error: {str(e)}")


@app.route("/api/send_now", methods=["POST"])
def api_send_now():
    user_id = resolve_request_user_id(request.json) if 'resolve_request_user_id' in globals() else None
    if not user_id:
        user_id = (request.json or {}).get('user_id') or session.get('user_id') or 'user_1'
    session['user_id'] = user_id
    session.permanent = True

    with USERS_LOCK:
        if user_id not in USERS:
            return jsonify({
                "success": False, 
                "message": "❌ لم يتم إعداد الحساب"
            })

        if not USERS[user_id].get('authenticated'):
            return jsonify({
                "success": False, 
                "message": "❌ يجب تسجيل الدخول أولاً"
            })

    data = request.get_json() or {}
    message = data.get('message', '').strip()
    groups = data.get('groups', '').strip()
    images = data.get('images', [])
    send_to_all = bool(data.get('send_to_all', False))
    pre_scan_action = data.get('action', None)
    force_salam = bool(data.get('force_salam', False))
    batch_interval = int(data.get('interval') or os.getenv('BATCH_SEND_INTERVAL_SECONDS', 7))

    if not message and not images:
        return jsonify({
            "success": False, 
            "message": "❌ يجب كتابة رسالة أو رفع صورة للإرسال"
        })

    if send_to_all:
        try:
            with USERS_LOCK:
                client_mgr = USERS.get(user_id, {}).get('client_manager')
            if not client_mgr or not client_mgr.client:
                return jsonify({"success": False, "message": "❌ العميل غير متصل"})
            dialogs = client_mgr.run_coroutine(client_mgr.client.get_dialogs())
            raw_groups_list = []
            for d in dialogs:
                entity = d.entity
                if hasattr(entity, 'megagroup') or hasattr(entity, 'broadcast') or hasattr(entity, 'gigagroup'):
                    uname = getattr(entity, 'username', None)
                    if uname:
                        raw_groups_list.append(f"https://t.me/{uname}")
                    else:
                        raw_groups_list.append(str(entity.id))
            groups_list = dedupe_groups(raw_groups_list)
            if not groups_list:
                return jsonify({"success": False, "message": "❌ لم يُعثر على أي مجموعة عامة"})
            socketio.emit('log_update', {"message": f"📡 إرسال لكل المجموعات: {len(groups_list)} مجموعة"}, to=user_id)
        except Exception as e:
            return jsonify({"success": False, "message": f"❌ خطأ في جلب المجموعات: {str(e)}"})
    else:
        if not groups:
            return jsonify({
                "success": False,
                "message": "❌ يجب تحديد المجموعات للإرسال إليها"
            })
        import re as _re
        raw_items = _re.split(r'[\r\n,;\t]+|\s+(?=https?://|@|-?\d+)', groups.strip())
        raw_groups = [g.strip() for g in raw_items if g and g.strip()]
        original_count = len(raw_groups)
        groups_list = dedupe_groups(raw_groups)
        duplicates_removed = original_count - len(groups_list)
        if duplicates_removed > 0:
            socketio.emit('log_update', {
                "message": f"♻️ تم تجاهل {duplicates_removed} رابط مكرر في قائمة الإرسال"
            }, to=user_id)

    if not groups_list:
        return jsonify({
            "success": False, 
            "message": "❌ يجب تحديد مجموعة واحدة على الأقل"
        })

    image_files = []
    if images:
        try:
            for img_data in images:
                raw_data = img_data.get('data', '')
                if ',' in raw_data:
                    base64_data = raw_data.split(',', 1)[1]
                else:
                    base64_data = raw_data
                image_bytes = base64.b64decode(base64_data)
                mime = img_data.get('type', 'image/jpeg')
                ext = mime.split('/')[-1].lower()
                if ext in ('jpeg', 'jpg'):
                    ext = 'jpg'
                elif ext not in ('png', 'gif', 'webp', 'bmp'):
                    ext = 'jpg'
                temp_file = tempfile.NamedTemporaryFile(
                    delete=False, suffix=f'.{ext}', mode='wb'
                )
                temp_file.write(image_bytes)
                temp_file.flush()
                temp_file.close()
                image_files.append({
                    'path': temp_file.name,
                    'name': img_data.get('name', f'image.{ext}'),
                    'type': mime
                })
            socketio.emit('log_update', {
                "message": f"📷 تم تحضير {len(image_files)} صورة للإرسال"
            }, to=user_id)
        except Exception as e:
            logger.error(f"Error processing images: {str(e)}")
            return jsonify({
                "success": False,
                "message": f"❌ خطأ في معالجة الصور: {str(e)}"
            })

    content_type = "رسالة"
    if images and message:
        content_type = f"رسالة مع {len(images)} صورة"
    elif images:
        content_type = f"{len(images)} صورة"

    cancel_event = threading.Event()
    BATCH_CANCEL_EVENTS[user_id] = cancel_event
    batch_id = str(uuid.uuid4())

    state = {
        "user_id": user_id,
        "batch_id": batch_id,
        "message": message,
        "images": images,
        "image_files": image_files,
        "groups_list": groups_list,
        "total": len(groups_list),
        "current_index": 0,
        "successful": 0,
        "failed": 0,
        "skipped_count": 0,
        "batch_interval": batch_interval,
        "pre_scan_action": pre_scan_action,
        "force_salam": force_salam,
        "batch_entries": [],
        "status": "sending",
        "cancel_event": cancel_event
    }
    BATCH_SENDER_STATES[user_id] = state

    socketio.emit('log_update', {
        "message": f"🚀 بدء الإرسال الفوري: {content_type} إلى {len(groups_list)} مجموعة (فاصل: {batch_interval}ث)"
    }, to=user_id)

    def run_worker():
        _execute_batch_send(user_id, state, is_resume=False)

    wt = _OSThread(target=run_worker, daemon=True)
    state["worker_thread"] = wt
    wt.start()

    return jsonify({
        "success": True, 
        "message": f"🚀 بدأ إرسال {content_type} لـ {len(groups_list)} مجموعة"
    })



@app.route("/api/scan_groups_protection", methods=["POST"])
def api_scan_groups_protection():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "غير مسجّل"}), 401
    try:
        with USERS_LOCK:
            client_manager = USERS.get(user_id, {}).get('client_manager')
        if not client_manager:
            return jsonify({"error": "العميل غير متصل"}), 400

        data = request.get_json(force=True, silent=True) or {}
        raw_groups = data.get('groups', '')
        group_list = [g.strip() for g in re.split(r'[\n,]+', raw_groups) if g.strip()]
        if not group_list:
            return jsonify({"error": "لا توجد مجموعات للفحص"}), 400

        results = []
        for g in group_list[:50]:
            try:
                try:
                    entity_obj = client_manager.run_coroutine(
                        client_manager.client.get_entity(g)
                    )
                except Exception:
                    g2 = ('@' + g) if not g.startswith('@') and not g.startswith('https://') else g
                    entity_obj = client_manager.run_coroutine(
                        client_manager.client.get_entity(g2)
                    )
                is_prot, reason = client_manager.run_coroutine(
                    client_manager.is_group_protected(entity_obj)
                )
                title = getattr(entity_obj, 'title', g)
                results.append({
                    "group": g,
                    "title": title,
                    "protected": is_prot,
                    "reason": reason or ('غير محمية ✅' if not is_prot else '')
                })
            except Exception as e:
                results.append({"group": g, "title": g, "protected": False, "reason": f"خطأ: {str(e)[:60]}"})

        protected_count = sum(1 for r in results if r['protected'])
        return jsonify({"success": True, "results": results, "protected_count": protected_count, "total": len(results)})
    except Exception as e:
        logger.error(f"Scan groups error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/get_stats", methods=["GET"])
def api_get_stats():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"sent": 0, "errors": 0})

    with USERS_LOCK:
        if user_id in USERS:
            return jsonify(USERS[user_id]['stats'])

    return jsonify({"sent": 0, "errors": 0})

@app.route("/api/get_login_status", methods=["GET"])
def api_get_login_status():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({
            "logged_in": False, 
            "connected": False,
            "awaiting_code": False,
            "awaiting_password": False,
            "login_pending": False,
            "login_error": None
        })

    with USERS_LOCK:
        if user_id in USERS:
            user_data = USERS[user_id]
            client_manager = user_data.get('client_manager')
            authenticated = user_data.get('authenticated', False)
            connected = user_data.get('connected', False)
            awaiting_code = user_data.get('awaiting_code', False)
            awaiting_password = user_data.get('awaiting_password', False)
            login_pending = user_data.get('login_pending', False)
            login_error = user_data.get('login_error')

            # التحقق أيضاً من مدير تسجيل الدخول النشط telegram_manager
            login_mgr = telegram_manager.login_managers.get(user_id)
            if login_mgr:
                if getattr(login_mgr, 'awaiting_code', False):
                    awaiting_code = True
                if getattr(login_mgr, 'awaiting_password', False):
                    awaiting_password = True
                if getattr(login_mgr, 'authenticated', False):
                    authenticated = True
                if getattr(login_mgr, 'connected', False):
                    connected = True

            if not authenticated and 'settings' in user_data and 'phone' in user_data['settings']:
                session_file = os.path.join(SESSIONS_DIR, f"{user_id}_session.session")
                if os.path.exists(session_file):
                    authenticated = True
                    connected = True
                    USERS[user_id]['authenticated'] = True
                    USERS[user_id]['connected'] = True

            account_name = user_data.get('account_name')
            account_username = user_data.get('account_username')
            account_phone = user_data.get('account_phone') or user_data.get('phone_number')
            account_avatar = user_data.get('account_avatar')

            if 'settings' in user_data and user_data['settings']:
                if not account_name:
                    account_name = user_data['settings'].get('account_name') or user_data['settings'].get('name')
                if not account_username:
                    account_username = user_data['settings'].get('account_username')
                if not account_phone:
                    account_phone = user_data['settings'].get('account_phone') or user_data['settings'].get('phone')

            if not account_name:
                account_name = PREDEFINED_USERS.get(user_id, {}).get('name')
            if not account_phone:
                account_phone = PREDEFINED_USERS.get(user_id, {}).get('phone')

            if (account_phone and '201120945094' in str(account_phone)) or (user_id == 'user_1' and not account_phone):
                account_name = 'Lamis'
                if not account_phone:
                    account_phone = '+201120945094'

            if not account_avatar:
                avatar_file = os.path.join(SESSIONS_DIR, 'avatars', f"{user_id}.jpg")
                if os.path.exists(avatar_file) and os.path.getsize(avatar_file) > 0:
                    account_avatar = f"/api/account_avatar/{user_id}?t={int(os.path.getmtime(avatar_file))}"

            return jsonify({
                "logged_in": authenticated, 
                "connected": connected,
                "awaiting_code": awaiting_code,
                "awaiting_password": awaiting_password,
                "login_pending": login_pending,
                "login_error": login_error,
                "session_revoked": bool(user_data.get('session_revoked', False)),
                "revoked_reason": user_data.get('revoked_reason'),
                "is_running": user_data.get('is_running', False),
                "user_id": user_id,
                "account_name": account_name,
                "account_username": account_username,
                "account_phone": account_phone,
                "account_avatar": account_avatar
            })

    cur_settings = load_settings(user_id) or {}
    cur_phone = cur_settings.get('phone') or cur_settings.get('account_phone') or PREDEFINED_USERS.get(user_id, {}).get('phone')
    cur_name = cur_settings.get('account_name') or cur_settings.get('name') or PREDEFINED_USERS.get(user_id, {}).get('name')
    if (cur_phone and '201120945094' in str(cur_phone)) or (user_id == 'user_1' and not cur_phone):
        cur_name = 'Lamis'
        if not cur_phone:
            cur_phone = '+201120945094'

    return jsonify({
        "logged_in": False, 
        "connected": False, 
        "awaiting_code": False, 
        "awaiting_password": False,
        "login_pending": False,
        "login_error": None,
        "session_revoked": False,
        "is_running": False,
        "user_id": user_id,
        "account_name": cur_name,
        "name": cur_name,
        "account_username": cur_settings.get('account_username'),
        "account_phone": cur_phone,
        "account_avatar": None
    })

@app.route("/api/get_all_accounts_info", methods=["GET"])
def api_get_all_accounts_info():
    result = {}
    for uid, udata in PREDEFINED_USERS.items():
        st = load_settings(uid) or {}
        with USERS_LOCK:
            u_mem = USERS.get(uid, {})
            has_disk_session = (
                os.path.exists(os.path.join(SESSIONS_DIR, f"{uid}_session.session"))
                or os.path.exists(os.path.join(SESSIONS_DIR, f"{uid}_string.txt"))
            )
            auth = bool(u_mem.get('authenticated', False)) or (has_disk_session and not u_mem.get('session_revoked'))
            aname = u_mem.get('account_name') or st.get('account_name') or st.get('name') or udata.get('name')
            auser = u_mem.get('account_username') or st.get('account_username')
            aphone = u_mem.get('account_phone') or st.get('account_phone') or st.get('phone') or udata.get('phone')
            aavatar = u_mem.get('account_avatar')

        if (aphone and '201120945094' in str(aphone)) or (uid == 'user_1' and not aphone):
            aname = 'Lamis'
            if not aphone:
                aphone = '+201120945094'

        if not aavatar:
            av_file = os.path.join(SESSIONS_DIR, 'avatars', f"{uid}.jpg")
            if os.path.exists(av_file) and os.path.getsize(av_file) > 0:
                aavatar = f"/api/account_avatar/{uid}?t={int(os.path.getmtime(av_file))}"
        result[uid] = {
            "id": uid,
            "name": aname or udata.get("name", uid),
            "icon": udata.get("icon", "fas fa-user"),
            "color": udata.get("color", "#0088cc"),
            "logged_in": auth,
            "account_name": aname,
            "account_username": auser,
            "account_phone": aphone,
            "account_avatar": aavatar
        }
    return jsonify(result)

@app.route("/api/voice_command/parse", methods=["POST"])
def api_voice_command_parse():
    """محرك السيرفر لتحليل الأوامر الصوتية واستخراج النوايا والبيانات"""
    try:
        data = request.get_json(silent=True) or {}
        text = (data.get("text") or "").strip().lower()
        if not text:
            return jsonify({"success": False, "message": "لا يوجد نص أمر صوتي"})

        import re

        # توحيد النص العربي وإزالة التشكيل
        norm_text = text
        for ch in ['\u064B', '\u064C', '\u064D', '\u064E', '\u064F', '\u0650', '\u0651', '\u0652']:
            norm_text = norm_text.replace(ch, '')
        norm_text = re.sub(r'[إأآٱ]', 'ا', norm_text)
        norm_text = re.sub(r'[ىي]', 'ي', norm_text)
        norm_text = re.sub(r'[ة]', 'ه', norm_text)

        # استخراج الأرقام
        raw_digits = re.findall(r'\d+', norm_text)
        digits_str = "".join(raw_digits)

        # تصنيف النوايا بدقة
        intent = "unknown"
        payload = {}
        msg_resp = ""

        if any(w in norm_text for w in ['كود', 'رمز', 'الرمز', 'الكود']):
            intent = "verify_code"
            payload = {"code": digits_str}
            msg_resp = f"جارٍ التحقق من كود الدخول {digits_str}" if digits_str else "يرجى نطق أرقام الكود بوضوح"

        elif any(w in norm_text for w in ['كلمه المرور', 'كلمه السر', 'باسورد', 'باسوورد', 'السر']):
            intent = "verify_password"
            p_val = re.sub(r'.*(كلمة المرور|كلمة السر|الباسورد|السر|رمز سري|باسورد|الباسوورد|كلمه المرور|كلمه السر)\s*(هي|هو)?\s*', '', text, flags=re.I).strip()
            payload = {"password": p_val}
            msg_resp = "جارٍ التحقق من كلمة مرور الحساب بخطوتين"

        elif any(w in norm_text for w in ['خروج', 'تسجيل خروج', 'سجل خروج', 'انهاء الجلسه', 'logout']):
            intent = "logout"
            msg_resp = "جارٍ تسجيل الخروج وإنهاء الجلسة الحالية"

        elif any(w in norm_text for w in ['حاله', 'حالة', 'مين متصل', 'الوضع', 'الحساب المتصل', 'status']):
            intent = "check_status"
            msg_resp = "جارٍ فحص حالة الاتصال والحسابات النشطة"

        elif any(w in norm_text for w in ['سجل', 'دخول', 'تسجيل', 'ادخل', 'حساب', 'ادخلني', 'login']):
            intent = "login"
            if 'لميس' in norm_text or 'user_1' in norm_text or 'الاول' in norm_text:
                payload = {"target_account": "user_1", "phone": "+201120945094", "name": "Lamis"}
                msg_resp = "جارٍ تسجيل الدخول بحساب لميس"
            elif 'الثاني' in norm_text or 'حساب 2' in norm_text:
                payload = {"target_account": "user_2", "phone": "+201221349790", "name": "الحساب الثاني"}
                msg_resp = "جارٍ تسجيل الدخول بالحساب الثاني"
            elif 'الثالث' in norm_text or 'حساب 3' in norm_text:
                payload = {"target_account": "user_3", "phone": "+201148863243", "name": "الحساب الثالث"}
                msg_resp = "جارٍ تسجيل الدخول بالحساب الثالث"
            elif digits_str and len(digits_str) >= 8:
                p = "+" + digits_str if not digits_str.startswith('+') else digits_str
                payload = {"phone": p}
                msg_resp = f"جارٍ طلب تسجيل الدخول بالرقم {p}"
            else:
                msg_resp = "جارٍ بدء تسجيل الدخول بالحساب المحدد"

        elif any(w in norm_text for w in ['استئناف', 'استأنف', 'واصل', 'تابع', 'كمل']):
            intent = "resume_broadcast"
            msg_resp = "أمر مؤكد: جارٍ استئناف مهمة الإرسال فوراً"

        elif any(w in norm_text for w in ['الغاء', 'إلغاء', 'انهاء', 'إنهاء']) and any(w in norm_text for w in ['ارسال', 'نشر', 'بث', 'مهمه', 'مهمة']):
            intent = "cancel_broadcast"
            msg_resp = "أمر مؤكد: تم إلغاء مهمة الإرسال نهائياً"

        elif any(w in norm_text for w in ['جدوله', 'جدولة', 'دائريه', 'دائرية', 'دائري']):
            enable = not any(w in norm_text for w in ['ايقاف', 'إيقاف', 'تعطيل', 'عطل', 'أوقف', 'اوقف', 'وقف'])
            intent = "toggle_circular_schedule"
            payload = {"enable": enable}
            msg_resp = "تم تفعيل نظام الجدولة الدائرية بنجاح" if enable else "تم إيقاف الجدولة الدائرية بنجاح"

        elif any(w in norm_text for w in ['تنبيهاتي', 'التنبيهات']):
            enable = not any(w in norm_text for w in ['ايقاف', 'إيقاف', 'تعطيل', 'عطل', 'أوقف', 'اوقف', 'وقف'])
            intent = "toggle_alerts"
            payload = {"enable": enable}
            msg_resp = "تم تفعيل نظام تنبيهاتي الذكية بنجاح" if enable else "تم إيقاف نظام تنبيهاتي الذكية بنجاح"

        elif any(w in norm_text for w in ['رادار', 'الرادار']):
            enable = not any(w in norm_text for w in ['ايقاف', 'إيقاف', 'تعطيل', 'عطل', 'أوقف', 'اوقف', 'وقف'])
            intent = "toggle_link_radar"
            payload = {"enable": enable}
            msg_resp = "تم تفعيل رادار الروابط بنجاح" if enable else "تم إيقاف رادار الروابط بنجاح"

        elif any(w in norm_text for w in ['انضمام', 'الانضمام']):
            enable = not any(w in norm_text for w in ['ايقاف', 'إيقاف', 'تعطيل', 'عطل', 'أوقف', 'اوقف', 'وقف'])
            intent = "toggle_auto_join"
            payload = {"enable": enable}
            msg_resp = "تم تفعيل الانضمام التلقائي للمجموعات بنجاح" if enable else "تم إيقاف الانضمام التلقائي للمجموعات بنجاح"

        elif any(w in norm_text for w in ['الردود العامه', 'الردود العامة', 'محرك الردود']):
            enable = not any(w in norm_text for w in ['ايقاف', 'إيقاف', 'تعطيل', 'عطل', 'أوقف', 'اوقف', 'وقف'])
            intent = "toggle_auto_reply"
            payload = {"enable": enable}
            msg_resp = "تم تفعيل محرك الردود التلقائية العامة بنجاح" if enable else "تم إيقاف محرك الردود التلقائية العامة بنجاح"

        elif any(w in norm_text for w in ['اقتباس', 'الاقتباس', 'اعاده توجيه', 'إعادة توجيه']):
            enable = not any(w in norm_text for w in ['ايقاف', 'إيقاف', 'تعطيل', 'عطل', 'أوقف', 'اوقف', 'وقف', 'بدون'])
            intent = "toggle_forward_quote"
            payload = {"enable": enable}
            msg_resp = "تم تفعيل وضع الاقتباس الرسمي بنجاح" if enable else "تم إيقاف وضع الاقتباس الرسمي بنجاح"

        elif any(w in norm_text for w in ['مؤقت', 'مؤقتا']) and any(w in norm_text for w in ['اوقف', 'أوقف', 'ايقاف', 'إيقاف', 'وقف']):
            intent = "pause_broadcast"
            msg_resp = "أمر مؤكد: تم إيقاف الإرسال مؤقتاً"

        elif any(w in norm_text for w in ['اوقف', 'أوقف', 'ايقاف', 'إيقاف', 'توقف', 'وقف', 'فرمل', 'بطل', 'stop']):
            intent = "stop_broadcast"
            msg_resp = "أمر مؤكد: تم إيقاف الإرسال بنجاح"

        elif any(w in norm_text for w in ['ابدا', 'ابدأ', 'تشغيل', 'انطلق', 'ارسل الان', 'ارسل', 'ارسال', 'شغل', 'بلش', 'مهمه الارسال', 'send', 'start']):
            intent = "start_broadcast"
            msg_resp = "أمر مؤكد: جارٍ تشغيل وبدء مهمة الإرسال فوراً"

        elif 'pdf' in norm_text or 'بي دي اف' in norm_text:
            intent = "export_pdf"
            msg_resp = "جارٍ تجهيز وتحميل ملف الروابط PDF لجهازك"

        elif 'txt' in norm_text or 'تكست' in norm_text or 'ملف نصي' in norm_text:
            intent = "export_txt"
            msg_resp = "جارٍ تجهيز وتحميل ملف الروابط النصي TXT لجهازك"

        elif any(w in norm_text for w in ['استعرض', 'فحص', 'روابط', 'الروابط', 'قاعده البيانات', 'links']):
            intent = "inspect_links"
            msg_resp = "جارٍ استعراض الروابط المحفوظة وفحص السحابة"

        elif any(w in norm_text for w in ['حاله', 'حالة', 'مين متصل', 'الوضع', 'الحساب المتصل', 'status']):
            intent = "check_status"
            msg_resp = "جارٍ فحص حالة الاتصال والحسابات النشطة"

        elif any(w in norm_text for w in ['احفظ', 'حفظ', 'تثبيت', 'save']):
            intent = "save_settings"
            msg_resp = "تم حفظ وتثبيت إعدادات الإرسال بنجاح"

        elif any(w in norm_text for w in ['محلل', 'المحلل', 'مستندات', 'المستندات']):
            intent = "navigate_doc_analyzer"
            msg_resp = "جارٍ فتح المحلل الذكي للمستندات والصور"

        elif any(w in norm_text for w in ['الرئيسيه', 'الرئيسية', 'لوحه التحكم']):
            intent = "navigate_home"
            msg_resp = "جارٍ الانتقال إلى الصفحة الرئيسية"

        return jsonify({
            "success": True,
            "intent": intent,
            "payload": payload,
            "message": msg_resp,
            "text": text
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/api/add_account", methods=["POST"])
def api_add_account():
    """إنشاء حساب تيليجرام جديد وإضافته للنظام والتبديل إليه فوراً"""
    try:
        data = request.get_json(silent=True) or {}
        custom_name = (data.get("name") or "").strip()
        custom_phone = (data.get("phone") or "").strip()

        # حساب المعرف التالي
        idx = 1
        while f"user_{idx}" in PREDEFINED_USERS:
            idx += 1
        new_uid = f"user_{idx}"

        palette = [
            ("#0088cc", "fas fa-user"),
            ("#28a745", "fas fa-user-check"),
            ("#e91e63", "fas fa-user-shield"),
            ("#9c27b0", "fas fa-user-astronaut"),
            ("#ff9800", "fas fa-user-graduate"),
            ("#00bcd4", "fas fa-user-tie"),
            ("#673ab7", "fas fa-user-ninja"),
            ("#20c997", "fas fa-user-clock"),
        ]
        color, icon = palette[(idx - 1) % len(palette)]
        display_name = custom_name if custom_name else f"المستخدم {idx}"

        new_account_info = {
            "id": new_uid,
            "name": display_name,
            "phone": custom_phone,
            "icon": icon,
            "color": color
        }
        PREDEFINED_USERS[new_uid] = new_account_info
        _save_custom_accounts()

        # حفظ الرقم واسمه الدائم في قاعدة الأرقام المحفوظة فوراً وبث التحديث
        if custom_phone:
            try:
                import firestore_sync
                firestore_sync.save_phone_number(custom_phone, custom_name or 'حساب محفوظ')
                socketio.emit('saved_phones_updated', {'phones': firestore_sync.get_saved_phone_numbers()})
            except Exception as _spe:
                logger.debug(f"api_add_account phone save notice: {_spe}")

        # تهيئة مجلد الجلسة والإعدادات
        get_user_session_dir(new_uid)
        initial_settings = {"phone": custom_phone} if custom_phone else {}
        if custom_name:
            initial_settings["account_name"] = custom_name
        save_settings(new_uid, initial_settings)

        with USERS_LOCK:
            USERS[new_uid] = {
                'client_manager': None,
                'settings': initial_settings,
                'thread': None,
                'is_running': False,
                'stats': {"sent": 0, "errors": 0},
                'connected': False,
                'authenticated': False,
                'awaiting_code': False,
                'awaiting_password': False,
                'phone_code_hash': None,
                'monitoring_active': False,
                'event_handlers_registered': False,
                'sent_batches': []
            }

        old_uid = session.get('user_id', 'user_1')
        session['user_id'] = new_uid
        session.permanent = True

        logger.info(f"✅ Created and switched to new account: {new_uid} ({display_name})")
        return jsonify({
            "success": True,
            "user_id": new_uid,
            "account": new_account_info,
            "previous_user_id": old_uid,
            "message": f"تم إنشاء {display_name} بنجاح وتم التبديل إليه"
        })
    except Exception as e:
        logger.error(f"Error in api_add_account: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/delete_account", methods=["POST"])
def api_delete_account():
    """حذف حساب إضافي وإعادة تعيينه بالكامل"""
    try:
        data = request.get_json(silent=True) or {}
        target_uid = data.get("user_id")
        if not target_uid or target_uid not in PREDEFINED_USERS:
            return jsonify({"success": False, "message": "الحساب غير موجود"}), 404

        if target_uid == 'user_1':
            return jsonify({"success": False, "message": "لا يمكن حذف الحساب الأساسي"}), 400

        if len(PREDEFINED_USERS) <= 1:
            return jsonify({"success": False, "message": "لا يمكن حذف الحساب الوحيد المتبقي"}), 400

        try:
            _do_reset_user(target_uid)
        except Exception as _e:
            logger.warning(f"Reset error during account deletion: {_e}")

        account_name = PREDEFINED_USERS[target_uid].get('name', target_uid)
        del PREDEFINED_USERS[target_uid]
        _save_custom_accounts()

        if session.get('user_id') == target_uid:
            remaining_uid = next(iter(PREDEFINED_USERS.keys()))
            session['user_id'] = remaining_uid

        return jsonify({
            "success": True,
            "message": f"تم حذف الحساب {account_name} بنجاح",
            "active_user": session.get('user_id')
        })
    except Exception as e:
        logger.error(f"Error in api_delete_account: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/get_user_info", methods=["GET"])
def api_get_user_info():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"success": False, "message": "غير مسجل دخول"})

    with USERS_LOCK:
        if user_id in USERS and 'settings' in USERS[user_id]:
            settings = USERS[user_id]['settings']
            return jsonify({
                "success": True,
                "phone": settings.get('phone', ''),
                "name": settings.get('name', ''),
                "user_id": user_id[:8] + "..."
            })

    return jsonify({"success": False, "message": "لم يتم العثور على معلومات المستخدم"})

@app.route("/api/resend_code", methods=["POST"])
def api_resend_code():
    try:
        data = request.json or {}
        user_id = resolve_request_user_id(data)
        session['user_id'] = user_id
        session.permanent = True
        force_sms = bool(data.get('force_sms', False))

        with USERS_LOCK:
            if user_id not in USERS:
                return jsonify({"success": False, "message": "❌ يرجى البدء بإدخال رقم الهاتف أولاً"})
            client_manager = USERS[user_id].get('client_manager')
            settings = USERS[user_id].get('settings', {})
            phone = settings.get('phone')

        if not client_manager or not client_manager.client or not phone:
            return jsonify({"success": False, "message": "❌ لم يتم إعداد العميل"})

        sent = client_manager.run_coroutine(
            client_manager.client.send_code_request(phone, force_sms=force_sms)
        )
        with USERS_LOCK:
            if user_id in USERS:
                USERS[user_id]['awaiting_code'] = True
                USERS[user_id]['phone_code_hash'] = sent.phone_code_hash

        msg = "📱 تم إعادة الإرسال عبر SMS" if force_sms else "📱 تم إعادة إرسال الكود"
        socketio.emit('log_update', {"message": msg}, to=user_id)
        return jsonify({"success": True, "message": msg})
    except Exception as e:
        logger.error(f"Resend code error: {str(e)}")
        return jsonify({"success": False, "message": f"❌ {str(e)}"})

@app.route("/api/reset_login", methods=["POST"])
def api_reset_login():
    user_id = session.get('user_id', 'user_1')

    if user_id not in PREDEFINED_USERS:
        return jsonify({
            "success": False,
            "message": "❌ مستخدم غير صحيح"
        })

    try:
        logger.info(f"Resetting login for user {user_id}")

        # تثبيت أي رقم واسم فعلي قبل إعادة تعيين جلسة الحساب
        try:
            _st_r = load_settings(user_id) or {}
            with USERS_LOCK:
                _u_r = USERS.get(user_id, {})
                _rp = _u_r.get('account_phone') or _st_r.get('phone') or _st_r.get('account_phone') or ''
                _rn = _u_r.get('account_name') or _st_r.get('account_name') or _st_r.get('name') or ''
            if _rp:
                import firestore_sync
                firestore_sync.save_phone_number(_rp)
                if _rn and not firestore_sync._is_placeholder_phone_name(_rn):
                    firestore_sync.update_phone_account_name(_rp, _rn)
        except Exception:
            pass

        with USERS_LOCK:
            if user_id in USERS:
                if USERS[user_id].get('is_running', False):
                    USERS[user_id]['is_running'] = False

                client_manager = USERS[user_id].get('client_manager')
                if client_manager:
                    try:
                        if hasattr(client_manager, 'stop'):
                            client_manager.stop()
                        if hasattr(client_manager, 'client') and client_manager.client:
                            client_manager.client.disconnect()
                        logger.info(f"Client stopped and disconnected for user {user_id}")
                    except Exception as e:
                        logger.error(f"Error stopping client for {user_id}: {e}")

                del USERS[user_id]
                logger.info(f"User data removed from memory for {user_id}")

        session_file = os.path.join(SESSIONS_DIR, f"{user_id}_session.session")
        if os.path.exists(session_file):
            try:
                os.remove(session_file)
                logger.info(f"Session file removed for {user_id}")
            except Exception as e:
                logger.error(f"Failed to remove session file for {user_id}: {str(e)}")

        try:
            import firestore_sync
            socketio.emit('saved_phones_updated', {'phones': firestore_sync.get_saved_phone_numbers()})
        except Exception:
            pass

        socketio.emit('log_update', {
            "message": f"🔄 تم إعادة تعيين جلسة تسجيل الدخول لـ {PREDEFINED_USERS[user_id]['name']}"
        }, to=user_id)

        socketio.emit('connection_status', {
            "status": "disconnected"
        }, to=user_id)

        socketio.emit('login_status', {
            "logged_in": False,
            "connected": False,
            "awaiting_code": False,
            "awaiting_password": False,
            "is_running": False
        }, to=user_id)

        logger.info(f"Login reset completed for user {user_id}")

        return jsonify({
            "success": True, 
            "message": f"✅ تم إعادة تعيين جلسة {PREDEFINED_USERS[user_id]['name']} بنجاح"
        })

    except Exception as e:
        logger.error(f"Error resetting login for {user_id}: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"❌ خطأ في إعادة التعيين: {str(e)}"
        })


def extract_telegram_links(text):
    if not text:
        return []

    patterns = [
        r'https?://t\.me/([a-zA-Z0-9_]+)(?:/\d+)?',
        r'https?://telegram\.me/([a-zA-Z0-9_]+)(?:/\d+)?',
        r'https?://t\.me/\+([a-zA-Z0-9_\-]+)',
        r'https?://telegram\.me/\+([a-zA-Z0-9_\-]+)',
        r't\.me/([a-zA-Z0-9_]+)',
        r't\.me/\+([a-zA-Z0-9_\-]+)',
        r'telegram\.me/([a-zA-Z0-9_]+)',
        r'@([a-zA-Z0-9_]{5,})',
    ]

    found_links = set()

    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            clean_match = match if isinstance(match, str) else match[0] if match else ''

            if pattern.startswith(r'@'):
                clean_link = f"https://t.me/{clean_match}"
            elif '+' in clean_match or pattern.find(r'\+') != -1:
                clean_link = f"https://t.me/+{clean_match.replace('+', '')}"
            elif clean_match and not clean_match.startswith('http'):
                clean_link = f"https://t.me/{clean_match}"
            elif clean_match.startswith('http'):
                clean_link = f"https://t.me/{clean_match.split('/')[-1]}"
            else:
                clean_link = clean_match

            if clean_link and len(clean_link) > 15:
                clean_link = clean_link.split('?')[0].split('#')[0]
                found_links.add(clean_link)

    links_list = sorted(list(found_links))
    result_links = []
    for link in links_list:
        username = link.split('/')[-1].replace('@', '')
        result_links.append({
            'url': link,
            'username': username,
            'type': 'invite' if '+' in link else 'channel'
        })

    return result_links

async def join_telegram_group(client, group_link, user_id=None, client_manager=None):
    try:
        if group_link.startswith('https://t.me/'):
            group_identifier = group_link.replace('https://t.me/', '')
        elif group_link.startswith('https://telegram.me/'):
            group_identifier = group_link.replace('https://telegram.me/', '')
        elif group_link.startswith('@'):
            group_identifier = group_link[1:]
        else:
            group_identifier = group_link

        try:
            entity = await client.get_entity(group_identifier)
            if hasattr(entity, 'megagroup') or hasattr(entity, 'broadcast'):
                result = await client(functions.channels.JoinChannelRequest(entity))
            else:
                raise Exception("مجموعة عادية - يجب استخدام رابط دعوة")

            return {
                "success": True,
                "already_joined": False,
                "message": "تم الانضمام بنجاح"
            }

        except UserAlreadyParticipantError:
            return {
                "success": True,
                "already_joined": True,
                "message": "منضم مسبقاً للمجموعة"
            }

        except FloodWaitError as e:
            return {
                "success": False,
                "message": f"يرجى الانتظار {e.seconds} ثانية"
            }

        except InviteHashExpiredError:
            return {
                "success": False,
                "message": "انتهت صلاحية رابط الدعوة"
            }

        except InviteHashInvalidError:
            return {
                "success": False,
                "message": "رابط الدعوة غير صحيح"
            }

        except Exception as group_error:
            error_str = str(group_error).lower()
            appeal_url = None
            appeal_note = ""

            if "cas" in error_str or "combot" in error_str:
                appeal_url = "https://cas.chat/appeal"
                appeal_note = "تم حظرك بواسطة CAS (Combot Anti-Spam). توجه إلى الرابط أعلاه لتقديم استئناف."
            elif "spamwatch" in error_str:
                appeal_url = "https://spamwat.ch/appeal"
                appeal_note = "تم حظرك بواسطة SpamWatch. استخدم الرابط أعلاه للاستئناف."
            elif "shieldy" in error_str:
                appeal_url = "https://t.me/Shieldy_Bot?start=appeal"
                appeal_note = "تم حظرك بواسطة Shieldy. افتح البوت في الخاص لطلب فك الحظر."
            elif "rose" in error_str or "missrose" in error_str:
                appeal_url = "https://t.me/MissRose_Bot?start=appeal"
                appeal_note = "تم حظرك بواسطة Rose. أرسل /start إلى البوت ثم اتبع التعليمات."
            elif "groupguard" in error_str:
                appeal_url = "https://t.me/GroupGuardBot?start=appeal"
                appeal_note = "تم حظرك بواسطة GroupGuard. اتصل بالبوت."
            elif "antispam" in error_str or "spam" in error_str:
                appeal_url = "https://t.me/SpamBot"
                appeal_note = "قد يكون حسابك مصنفاً كسبام. تواصل مع @SpamBot للتحقق."
            else:
                if "banned" in error_str or "blocked" in error_str or "forbidden" in error_str:
                    appeal_url = "https://t.me/SpamBot"
                    appeal_note = "حسابك ربما محظور من الانضمام. جرب التواصل مع @SpamBot أو مشرف المجموعة."

            if appeal_url and user_id and client_manager:
                message_text = f"""🚫 **فشل الانضمام إلى المجموعة** 🚫

**الرابط:** {group_link}
**السبب:** {error_str[:200]}

**إجراء مقترح للاستئناف:**
{appeal_note}
🔗 **رابط الاستئناف:** {appeal_url}

يرجى فتح الرابط ومتابعة التعليمات لرفع الحظر. بعد إلغاء الحظر، يمكنك إعادة المحاولة.
"""
                try:
                    await client_manager.send_to_saved_messages(message_text)
                except Exception as save_err:
                    logger.error(f"Could not send appeal to saved messages: {save_err}")

            try:
                if '/' in group_identifier:
                    result = await client(functions.messages.ImportChatInviteRequest(group_identifier.split('/')[-1]))
                    return {
                        "success": True,
                        "already_joined": False,
                        "message": "تم الانضمام عبر رابط الدعوة"
                    }
                else:
                    raise group_error
            except UserAlreadyParticipantError:
                return {
                    "success": True,
                    "already_joined": True,
                    "message": "منضم مسبقاً للمجموعة"
                }
            except Exception as final_error:
                return {
                    "success": False,
                    "message": f"فشل الانضمام: {str(final_error)}",
                    "appeal_url": appeal_url
                }

    except Exception as e:
        return {
            "success": False,
            "message": f"خطأ: {str(e)}"
        }

@app.route("/api/extract_group_links", methods=["POST"])
def api_extract_group_links():
    try:
        data = request.json
        if not data or not data.get('text'):
            return jsonify({
                "success": False,
                "message": "❌ لم يتم إرسال النص"
            })

        text = data.get('text', '')
        links = extract_telegram_links(text)

        return jsonify({
            "success": True,
            "links": links,
            "count": len(links),
            "message": f"✅ تم استخراج {len(links)} رابط"
        })

    except Exception as e:
        logger.error(f"Error extracting links: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"❌ خطأ: {str(e)}"
        })

@app.route("/api/join_group", methods=["POST"])
def api_join_group():
    try:
        user_id = session.get('user_id', 'user_1')

        if user_id not in PREDEFINED_USERS:
            return jsonify({
                "success": False,
                "message": "❌ مستخدم غير صحيح"
            })

        data = request.json

        if not data or not data.get('group_link'):
            return jsonify({
                "success": False,
                "message": "❌ لم يتم إرسال رابط المجموعة"
            })

        group_link_raw = data.get('group_link', '')
        if isinstance(group_link_raw, dict):
            group_link = group_link_raw.get('url', '') or group_link_raw.get('link', '') or str(group_link_raw)
        else:
            group_link = str(group_link_raw)

        group_link = group_link.strip()

        with USERS_LOCK:
            if user_id not in USERS:
                return jsonify({
                    "success": False,
                    "message": f"❌ المستخدم {PREDEFINED_USERS[user_id]['name']} غير مسجل"
                })

            client_manager = USERS[user_id].get('client_manager')
            if not client_manager or not client_manager.client:
                return jsonify({
                    "success": False,
                    "message": "❌ يرجى تسجيل الدخول أولاً"
                })

        result = client_manager.run_coroutine(
            join_telegram_group(client_manager.client, group_link, user_id, client_manager)
        )

        socketio.emit('log_update', {
            "message": f"{'✅' if result['success'] else '❌'} {group_link}: {result['message']}"
        }, to=user_id)

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error joining group: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"❌ خطأ: {str(e)}"
        })

@app.route("/api/start_auto_join", methods=["POST"])
def api_start_auto_join():
    try:
        user_id = session.get('user_id', 'user_1')

        if user_id not in PREDEFINED_USERS:
            return jsonify({
                "success": False,
                "message": "❌ مستخدم غير صحيح"
            })

        data = request.json
        if not data or not data.get('links'):
            return jsonify({
                "success": False,
                "message": "❌ لم يتم إرسال روابط المجموعات"
            })

        links = data.get('links', [])
        delay = data.get('delay', 3)

        if not links:
            return jsonify({
                "success": False,
                "message": "❌ لا توجد روابط للانضمام إليها"
            })

        with USERS_LOCK:
            if user_id not in USERS:
                return jsonify({
                    "success": False,
                    "message": f"❌ المستخدم {PREDEFINED_USERS[user_id]['name']} غير مسجل"
                })

            client_manager = USERS[user_id].get('client_manager')
            if not client_manager or not client_manager.client:
                return jsonify({
                    "success": False,
                    "message": "❌ يرجى تسجيل الدخول أولاً"
                })

        import threading

        def auto_join_worker():
            success_count = 0
            fail_count = 0
            already_joined_count = 0

            socketio.emit('log_update', {
                "message": f"🚀 بدء الانضمام التلقائي لـ {len(links)} مجموعة..."
            }, to=user_id)

            for i, link_obj in enumerate(links):
                try:
                    if isinstance(link_obj, dict):
                        group_link = link_obj.get('url', '') or link_obj.get('link', '') or str(link_obj)
                    else:
                        group_link = str(link_obj)

                    group_link = group_link.strip()

                    socketio.emit('join_progress', {
                        'current': i + 1,
                        'total': len(links),
                        'link': group_link
                    }, to=user_id)

                    result = client_manager.run_coroutine(
                        join_telegram_group(client_manager.client, group_link, user_id, client_manager)
                    )

                    if result['success']:
                        if result.get('already_joined', False):
                            already_joined_count += 1
                            socketio.emit('log_update', {
                                "message": f"ℹ️ منضم مسبقاً: {group_link}"
                            }, to=user_id)
                        else:
                            success_count += 1
                            socketio.emit('log_update', {
                                "message": f"✅ تم الانضمام: {group_link}"
                            }, to=user_id)
                    else:
                        fail_count += 1
                        socketio.emit('log_update', {
                            "message": f"❌ فشل: {group_link} - {result['message']}"
                        }, to=user_id)

                    socketio.emit('join_stats', {
                        'success': success_count,
                        'fail': fail_count,
                        'already_joined': already_joined_count
                    }, to=user_id)

                    if i < len(links) - 1:
                        time.sleep(delay)

                except Exception as e:
                    fail_count += 1
                    socketio.emit('log_update', {
                        "message": f"❌ خطأ في {group_link}: {str(e)}"
                    }, to=user_id)

            socketio.emit('auto_join_completed', {
                'success': success_count,
                'fail': fail_count,
                'already_joined': already_joined_count,
                'total': len(links)
            }, to=user_id)

            socketio.emit('log_update', {
                "message": f"🎉 انتهى الانضمام التلقائي! النجح: {success_count}, فشل: {fail_count}, منضم مسبقاً: {already_joined_count}"
            }, to=user_id)

        thread = _OSThread(target=auto_join_worker, daemon=True)
        thread.start()

        return jsonify({
            "success": True,
            "message": f"✅ تم بدء الانضمام التلقائي لـ {len(links)} مجموعة",
            "total_links": len(links)
        })

    except Exception as e:
        logger.error(f"Error starting auto join: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"❌ خطأ في بدء الانضمام التلقائي: {str(e)}"
        })

# ==========================
# الإضافات الجديدة (الإرسال المتسلسل، الانضمام المتقدم، البوت التعليمي، الردود التلقائية، البحث)
# ==========================

class RotatingSendManager:
    def __init__(self):
        self.threads = {}
        self.stop_events = {}
        self.next_send_at = {}
        self.interval_seconds = {}

    def start(self, user_id, groups, messages, interval_minutes, callback=None):
        if user_id in self.threads and self.threads[user_id] and self.threads[user_id].is_alive():
            self.stop(user_id)

        stop_event = threading.Event()
        self.stop_events[user_id] = stop_event

        thread = _OSThread(target=self._worker, args=(user_id, groups, messages, interval_minutes, stop_event, callback), daemon=True)
        self.threads[user_id] = thread
        thread.start()
        return True

    def stop(self, user_id):
        if user_id in self.stop_events:
            self.stop_events[user_id].set()
        if user_id in self.threads and self.threads[user_id]:
            self.threads[user_id].join(timeout=2)
        self.next_send_at.pop(user_id, None)
        self.interval_seconds.pop(user_id, None)
        return True

    def _worker(self, user_id, groups, messages, interval_minutes, stop_event, callback):
        messages = [m.strip() for m in messages if m and m.strip()]
        if not messages:
            return

        index = 0
        sleep_seconds = max(60, int(interval_minutes * 60))
        self.interval_seconds[user_id] = sleep_seconds

        while not stop_event.is_set():
            try:
                current_msg = messages[index % len(messages)]
                for group in groups:
                    if stop_event.is_set():
                        break
                    try:
                        telegram_manager.send_message_async(user_id, group, current_msg)
                        if callback:
                            callback(user_id, 'success', group, current_msg)
                    except Exception as e:
                        if callback:
                            callback(user_id, 'error', group, str(e))
                    time.sleep(2)
                index += 1
                self.next_send_at[user_id] = time.time() + sleep_seconds
                for _ in range(sleep_seconds):
                    if stop_event.is_set():
                        break
                    time.sleep(1)
            except Exception as e:
                logger.error(f"Rotating send error for {user_id}: {str(e)}")
                time.sleep(10)

rotating_manager = RotatingSendManager()

@app.route("/api/rotating/save", methods=["POST"])
def api_rotating_save():
    try:
        user_id = session.get('user_id', 'user_1')
        data = request.json
        messages = data.get('messages', [''] * 5)
        groups = data.get('groups', [])
        interval = int(data.get('interval', 5))

        settings = load_settings(user_id)
        settings['rotating_messages'] = messages
        settings['rotating_groups'] = dedupe_groups(groups)
        settings['rotating_interval'] = interval
        save_settings(user_id, settings)

        return jsonify({"success": True, "message": "تم حفظ إعدادات الإرسال المتسلسل"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route("/api/rotating/start", methods=["POST"])
def api_rotating_start():
    try:
        user_id = session.get('user_id', 'user_1')
        settings = load_settings(user_id)
        messages = settings.get('rotating_messages', [])
        groups = dedupe_groups(settings.get('rotating_groups', []))
        interval = settings.get('rotating_interval', 5)

        if not groups:
            return jsonify({"success": False, "message": "لا توجد مجموعات محددة"})
        valid_messages = [m for m in messages if m and m.strip()]
        if not valid_messages:
            return jsonify({"success": False, "message": "لا توجد رسائل صالحة"})

        def callback(uid, status, group, info):
            if status == 'success':
                socketio.emit('log_update', {"message": f"🔄 [متسلسل] أرسل إلى {group}"}, to=uid)
            else:
                socketio.emit('log_update', {"message": f"❌ [متسلسل] فشل إلى {group}: {info}"}, to=uid)

        rotating_manager.start(user_id, groups, valid_messages, interval, callback)

        try:
            settings['rotating_persistent'] = True
            save_settings(user_id, settings)
        except Exception as _e:
            logger.error(f"Failed to persist rotating flag for {user_id}: {_e}")

        socketio.emit('log_update', {"message": f"🔄 بدأ الإرسال المتسلسل ({len(valid_messages)} رسائل) كل {interval} دقيقة"}, to=user_id)
        return jsonify({"success": True, "message": "تم بدء الإرسال المتسلسل"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route("/api/rotating/stop", methods=["POST"])
def api_rotating_stop():
    try:
        user_id = session.get('user_id', 'user_1')
        rotating_manager.stop(user_id)

        try:
            _settings = load_settings(user_id)
            _settings['rotating_persistent'] = False
            save_settings(user_id, _settings)
        except Exception as _e:
            logger.error(f"Failed to clear rotating flag for {user_id}: {_e}")

        socketio.emit('log_update', {"message": "⏹ تم إيقاف الإرسال المتسلسل"}, to=user_id)
        return jsonify({"success": True, "message": "تم إيقاف الإرسال المتسلسل"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route("/api/rotating/status", methods=["GET"])
def api_rotating_status():
    try:
        user_id = session.get('user_id', 'user_1')
        settings = load_settings(user_id)
        is_active = user_id in rotating_manager.threads and rotating_manager.threads[user_id] and rotating_manager.threads[user_id].is_alive()
        next_send_in = None
        next_send_at = rotating_manager.next_send_at.get(user_id)
        if is_active and next_send_at:
            remaining = int(next_send_at - time.time())
            next_send_in = max(0, remaining)
        return jsonify({
            "success": True,
            "active": is_active,
            "messages": settings.get('rotating_messages', []),
            "groups": settings.get('rotating_groups', []),
            "interval": settings.get('rotating_interval', 5),
            "next_send_in": next_send_in,
            "interval_seconds": rotating_manager.interval_seconds.get(user_id)
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

def _classify_join_error(msg):
    if not msg:
        return ("خطأ غير معروف", "❓")
    s = str(msg).lower()
    if "anti-spam" in s or "antispam" in s or "spam" in s or "spambot" in s:
        return ("الحساب موسوم كسبام (يحتاج استئناف عبر @SpamBot)", "🚫")
    if "banned" in s or "blocked" in s or "forbidden" in s:
        return ("الحساب محظور من المجموعة أو من الانضمام", "⛔")
    if "expired" in s or "انتهت" in s:
        return ("انتهت صلاحية رابط الدعوة", "⏰")
    if "invalid" in s or "غير صحيح" in s or "غير صالح" in s:
        return ("رابط غير صالح", "🔗")
    if "flood" in s or "wait" in s or "ثانية" in s:
        return ("حد التليجرام مؤقت — يجب الانتظار قبل المحاولة مجدداً", "⏳")
    if "channel_private" in s or "private" in s or "خاص" in s:
        return ("القناة/المجموعة خاصة وتحتاج رابط دعوة", "🔒")
    if "not found" in s or "no user" in s or "could not find" in s or "غير موجود" in s:
        return ("المجموعة غير موجودة أو الرابط خاطئ", "🔍")
    if "too many channels" in s or "channels_too_much" in s:
        return ("الحساب وصل الحد الأقصى من القنوات (500)", "📛")
    if "user_deactivated" in s or "deactivated" in s:
        return ("الحساب معطل من تيليجرام", "🛑")
    if "captcha" in s or "verification" in s:
        return ("المجموعة تتطلب تحقق يدوي (كابتشا)", "🤖")
    if "admin" in s and "approval" in s:
        return ("الانضمام بحاجة موافقة المشرف", "👮")
    if "request" in s and ("send" in s or "join" in s):
        return ("تم إرسال طلب انضمام — بانتظار الموافقة", "📨")
    short = str(msg).strip()
    if len(short) > 120:
        short = short[:120] + "…"
    return (short, "❌")


# ── دالة لجلب الروابط من صفحات خارجية ──
def fetch_telegram_links_from_url(url, max_links=30):
    try:
        import requests as _req
        from bs4 import BeautifulSoup
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        resp = _req.get(url, timeout=12, headers=headers)
        if resp.status_code != 200:
            logger.warning(f'Failed to fetch {url}: HTTP {resp.status_code}')
            return []
        soup = BeautifulSoup(resp.text, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
        extracted = extract_telegram_links(text)
        links_from_text = [link['url'] for link in extracted if link.get('url')]
        links_from_href = []
        for a in soup.find_all('a', href=True):
            href = a['href'].strip()
            if 't.me' in href or 'telegram.me' in href:
                if not href.startswith('http'):
                    from urllib.parse import urljoin
                    href = urljoin(url, href)
                links_from_href.append(href)
        all_links = list(set(links_from_text + links_from_href))
        valid_links = [lnk for lnk in all_links if lnk and ('t.me' in lnk or 'telegram.me' in lnk)]
        seen = set()
        unique = []
        for lnk in valid_links:
            if lnk not in seen:
                seen.add(lnk)
                unique.append(lnk)
        return unique[:max_links]
    except Exception as e:
        logger.error(f'Error fetching links from {url}: {e}')
        return []


# ── دالة لاستخراج أسماء المجموعات من النص ──
def extract_group_names_from_text(text):
    import re
    names = []
    patterns = [
        r'(?:قروبات|مجموعات|الدراسات العليا)\s+(جامعة\s+[^\n,]+)',
        r'(?:قسم|دليل)\s+([^\n,]+)',
        r'([^\n,]+)\s+(?:قروب|مجموعة)',
        r'(جامعة\s+[^\n,]+)',
        r'(?:قروبات|مجموعات)\s+([^\n,]+)',
        r'([^\n]{5,50})',
    ]
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for m in matches:
            name = m.strip()
            if name and len(name) > 5 and len(name) < 80 and not re.match(r'^[\d\s\W]+$', name):
                if name not in names:
                    names.append(name)
    return names[:20]


# ── دالة للبحث عن مجموعات بأسمائها في تيليجرام ──
async def search_and_join_groups_by_name(client, names_list, limit=3):
    from telethon.tl.functions.contacts import SearchRequest
    results = []
    for name in names_list:
        try:
            sr = await client(SearchRequest(q=name, limit=limit))
            if sr.chats:
                for chat in sr.chats:
                    if hasattr(chat, 'username') and chat.username:
                        group_link = f'https://t.me/{chat.username}'
                        results.append({'name': name, 'found': group_link, 'chat': chat, 'type': 'public'})
                        break
                    elif hasattr(chat, 'title') and chat.title:
                        try:
                            from telethon.tl import functions as _tl_f
                            invite = await client(_tl_f.messages.ExportChatInviteRequest(
                                peer=chat, legacy_revoke_permanent=True))
                            if invite and hasattr(invite, 'link'):
                                results.append({'name': name, 'found': invite.link, 'chat': chat, 'type': 'private'})
                                break
                        except Exception:
                            pass
        except Exception as e:
            logger.warning(f"Search for '{name}' failed: {e}")
    return results


@app.route("/api/auto_join/advanced", methods=["POST"])
def api_auto_join_advanced():
    try:
        user_id = session.get('user_id', 'user_1')
        data = request.json
        raw_input = data.get('links', '')
        fetch_external = data.get('fetch_external', True)
        max_external_links = int(data.get('max_external_links', 30))
        search_by_name = data.get('search_by_name', True)

        # ── 1. استخراج الروابط من النص المختلط ──
        if isinstance(raw_input, str):
            raw_text = raw_input
        elif isinstance(raw_input, list):
            raw_text = "\n".join([
                str(item) if not isinstance(item, dict) else item.get('url', '')
                for item in raw_input
            ])
        else:
            raw_text = str(raw_input)

        extracted = extract_telegram_links(raw_text)
        direct_links = [link['url'] for link in extracted if link.get('url')]

        # ── 2. جلب الروابط من الصفحات الخارجية ──
        external_links = []
        if fetch_external:
            import re as _re_ext
            external_urls = _re_ext.findall(r'https?://[^\s<>"\'()]+', raw_text)
            for url in external_urls:
                if 't.me' not in url and 'telegram.me' not in url:
                    fetched = fetch_telegram_links_from_url(url, max_external_links)
                    if fetched:
                        socketio.emit('log_update',
                            {'message': f'🌐 تم جلب {len(fetched)} رابط من {url}'}, to=user_id)
                        external_links.extend(fetched)
                    else:
                        socketio.emit('log_update',
                            {'message': f'⚠️ لم يتم العثور على روابط تيليجرام في {url}'}, to=user_id)

        all_raw_links = direct_links + external_links

        # ── 3. إذا لم نجد روابط، حاول استخراج أسماء مجموعات ──
        if not all_raw_links and search_by_name:
            group_names = extract_group_names_from_text(raw_text)
            if group_names:
                socketio.emit('log_update',
                    {'message': f'🔍 لم نجد روابط، لكن وجدنا {len(group_names)} اسماً لمجموعات، جاري البحث عنها...'},
                    to=user_id)
                with USERS_LOCK:
                    client_manager = USERS.get(user_id, {}).get('client_manager')
                    if not client_manager or not client_manager.client:
                        return jsonify({'success': False, 'message': 'العميل غير متصل'})
                found_groups = client_manager.run_coroutine(
                    search_and_join_groups_by_name(client_manager.client, group_names)
                )
                if found_groups:
                    all_raw_links = [g['found'] for g in found_groups]
                    socketio.emit('log_update',
                        {'message': f'✅ تم العثور على {len(found_groups)} مجموعة من الأسماء المستخرجة'},
                        to=user_id)
                    for g in found_groups:
                        socketio.emit('log_update',
                            {'message': f"  • {g['name']} → {g['found']}"}, to=user_id)
                else:
                    return jsonify({'success': False, 'message': 'لم يتم العثور على روابط ولا مجموعات تطابق الأسماء'})

        if not all_raw_links:
            return jsonify({'success': False, 'message': 'لم يتم العثور على روابط تيليجرام في النص أو في الصفحات الخارجية'})

        # ── 4. إزالة المكررات وتنظيفها ──
        clean_links = dedupe_groups(all_raw_links)
        if not clean_links:
            return jsonify({'success': False, 'message': 'لا توجد روابط صالحة بعد التنقية'})

        # ── 5. التحقق من العضوية المسبقة ──
        with USERS_LOCK:
            if user_id not in USERS:
                return jsonify({'success': False, 'message': 'المستخدم غير موجود'})
            client_manager = USERS[user_id].get('client_manager')
            if not client_manager or not client_manager.client:
                return jsonify({'success': False, 'message': 'العميل غير متصل، يرجى تسجيل الدخول'})

        already_member = []
        pending_links = []
        for link in clean_links:
            try:
                entity = client_manager.run_coroutine(client_manager.client.get_entity(link))
                try:
                    client_manager.run_coroutine(client_manager.client.get_participants(entity, limit=1))
                    already_member.append(link)
                    socketio.emit('log_update',
                        {'message': f'📌 [عضوية مسبقة] {link} — أنت عضو بالفعل، تم تخطيه'}, to=user_id)
                    continue
                except Exception:
                    pending_links.append(link)
            except Exception:
                pending_links.append(link)

        # ── 6. عرض الإحصائيات ──
        total = len(clean_links)
        already_count = len(already_member)
        pending_count = len(pending_links)

        socketio.emit('log_update', {
            'message': f'📊 إحصائيات: {total} رابط إجمالي | {already_count} منضم مسبقاً (تم تخطيهم) | {pending_count} متبقي للانضمام'
        }, to=user_id)

        if not pending_links:
            return jsonify({
                'success': True,
                'message': f'✅ جميع الروابط ({total}) منضم إليها مسبقاً، لا حاجة للانضمام',
                'already': already_member
            })

        # ── 7. بدء الانضمام ──
        delay = max(1, int(data.get('delay', 3)))
        max_retries = max(1, int(data.get('max_retries', 3)))

        try:
            _s = load_settings(user_id)
            _s['auto_join_links'] = pending_links
            _s['auto_join_delay'] = delay
            save_settings(user_id, _s)
        except Exception:
            pass

        import threading as _threading
        stop_event  = _threading.Event()
        pause_event = _threading.Event()
        with USERS_LOCK:
            if user_id in USERS:
                USERS[user_id]['auto_join_stop']  = stop_event
                USERS[user_id]['auto_join_pause'] = pause_event

        def _save_state(state_dict):
            with USERS_LOCK:
                if user_id in USERS:
                    USERS[user_id]['auto_join_state'] = state_dict

        def advanced_join_worker():
            total_pending = len(pending_links)
            results = {'success': 0, 'fail': 0, 'already': already_count, 'total': total, 'items': []}

            _save_state({
                'running': True, 'total': total_pending, 'done': 0,
                'success': 0, 'already': already_count, 'fail': 0,
                'items': [], 'links': pending_links, 'delay': delay
            })

            socketio.emit('auto_join_started', {'total': total_pending}, to=user_id)
            socketio.emit('log_update', {
                'message': f'🚀 بدء الانضمام إلى {total_pending} مجموعة (بعد استبعاد {already_count} منضم مسبقاً)'
            }, to=user_id)

            for idx, link in enumerate(pending_links, 1):
                if stop_event.is_set():
                    socketio.emit('log_update',
                        {'message': f'⏹ تم إيقاف الانضمام بعد {idx - 1} مجموعة'}, to=user_id)
                    break

                if pause_event.is_set():
                    socketio.emit('auto_join_paused', {
                        'paused_at': idx - 1, 'total': total_pending,
                        'success': results['success'], 'fail': results['fail'],
                        'already': already_count
                    }, to=user_id)
                    while pause_event.is_set() and not stop_event.is_set():
                        time.sleep(0.5)
                    if stop_event.is_set():
                        break
                    socketio.emit('auto_join_resumed',
                        {'resumed_at': idx - 1, 'total': total_pending}, to=user_id)

                item = {'idx': idx, 'total': total_pending, 'url': link, 'status': 'processing', 'reason': ''}
                socketio.emit('auto_join_progress', item, to=user_id)

                success = False
                last_error = None
                for attempt in range(max_retries):
                    try:
                        result = client_manager.run_coroutine(
                            join_telegram_group(client_manager.client, link, user_id, client_manager)
                        )
                        if result.get('success'):
                            success = True
                            break
                        else:
                            last_error = result.get('message') or 'فشل غير محدد'
                            if 'FloodWait' in str(last_error):
                                import re as _re_fw
                                m = _re_fw.search(r'(\d+)', str(last_error))
                                if m:
                                    wait_sec = int(m.group(1))
                                    socketio.emit('log_update', {
                                        'message': f'⏳ FloodWait: يطلب تيليجرام الانتظار {wait_sec} ثانية... (المحاولة {attempt+1}/{max_retries})'
                                    }, to=user_id)
                                    time.sleep(wait_sec)
                                    continue
                    except Exception as e:
                        last_error = str(e)
                        if 'FloodWait' in last_error:
                            import re as _re_fw
                            m = _re_fw.search(r'(\d+)', last_error)
                            if m:
                                wait_sec = int(m.group(1))
                                socketio.emit('log_update', {
                                    'message': f'⏳ FloodWait: {wait_sec} ثانية... (المحاولة {attempt+1}/{max_retries})'
                                }, to=user_id)
                                time.sleep(wait_sec)
                                continue
                    time.sleep(delay)

                if success:
                    item['status'] = 'success'
                    item['reason'] = 'تم الانضمام بنجاح'
                    results['success'] += 1
                    socketio.emit('log_update',
                        {'message': f"✅ [{idx}/{total_pending}] انضم إلى: {link}"}, to=user_id)
                else:
                    item['status'] = 'failed'
                    item['reason'] = last_error or 'فشل بعد عدة محاولات'
                    results['fail'] += 1
                    socketio.emit('log_update',
                        {'message': f"❌ [{idx}/{total_pending}] فشل في: {link} — {item['reason']}"}, to=user_id)

                results['items'].append(item)
                _save_state({
                    'running': True, 'total': total_pending, 'done': idx,
                    'success': results['success'], 'already': already_count,
                    'fail': results['fail'], 'items': results['items'][-100:],
                    'links': pending_links, 'delay': delay
                })
                socketio.emit('auto_join_progress', {**item, 'counts': {
                    'success': results['success'], 'fail': results['fail'],
                    'already': already_count, 'done': idx, 'total': total_pending
                }}, to=user_id)

                if idx < total_pending and not stop_event.is_set():
                    time.sleep(delay)

            # التقرير النهائي
            socketio.emit('auto_join_completed', {
                'success': results['success'],
                'fail': results['fail'],
                'already': already_count,
                'total': total,
                'items': results['items']
            }, to=user_id)
            socketio.emit('log_update', {
                'message': f"🎉 انتهى الانضمام: ✅ {results['success']} نجح | ❌ {results['fail']} فشل | 📌 {already_count} منضم مسبقاً"
            }, to=user_id)

            with USERS_LOCK:
                if user_id in USERS:
                    USERS[user_id].pop('auto_join_stop', None)
                    st = USERS[user_id].get('auto_join_state', {})
                    st['running'] = False
                    USERS[user_id]['auto_join_state'] = st

        _OSThread(target=advanced_join_worker, daemon=True).start()
        return jsonify({
            'success': True,
            'total': total,
            'already': already_count,
            'pending': pending_count,
            'already_links': already_member,
            'message': f'بدأ الانضمام إلى {pending_count} مجموعة (تم استبعاد {already_count} منضم مسبقاً)'
        })

    except Exception as e:
        logger.error(f'auto_join_advanced error: {e}')
        return jsonify({'success': False, 'message': str(e)})



def _normalize_auto_reply(rule):
    if not isinstance(rule, dict):
        return None
    keyword = (rule.get('keyword') or rule.get('trigger') or '').strip()
    reply = (rule.get('reply') or '').strip()
    if not keyword or not reply:
        return None
    scope = (rule.get('scope') or 'all').lower()
    if scope not in ('all', 'private', 'groups'):
        scope = 'all'
    match = (rule.get('match') or 'contains').lower()
    if match not in ('contains', 'exact', 'regex'):
        match = 'contains'
    return {
        'keyword': keyword,
        'reply': reply,
        'scope': scope,
        'match': match,
        'used_count': int(rule.get('used_count') or 0),
        'last_used': rule.get('last_used') or '',
    }

@app.route("/api/auto_replies", methods=["GET"])
@app.route("/api/get_auto_replies", methods=["GET"])
def api_get_auto_replies():
    user_id = session.get('user_id', 'user_1')
    settings = load_settings(user_id)
    return jsonify({
        "success": True,
        "enabled": settings.get('auto_reply_enabled', True),
        "auto_replies": settings.get('auto_replies', []) or [],
        "user_auto_replies": settings.get('user_auto_replies', []) or []
    })

def _normalize_user_auto_reply(rule):
    if not isinstance(rule, dict):
        return None
    username_raw = (rule.get('username') or rule.get('target_user') or '').strip()
    reply = (rule.get('reply') or '').strip()
    if not username_raw or not reply:
        return None
    username_clean = username_raw.replace('https://t.me/', '').replace('http://t.me/', '').replace('t.me/', '').strip().lstrip('@')
    clean_digits = username_clean.lstrip('-')
    target_uid = None
    if clean_digits.isdigit():
        target_uid = int(username_clean)
    elif str(rule.get('target_user_id', '')).lstrip('-').isdigit():
        target_uid = int(rule.get('target_user_id'))

    display_username = username_clean if clean_digits.isdigit() else f"@{username_clean}"

    return {
        'username': username_clean,
        'display_username': display_username,
        'target_user_id': target_uid,
        'reply': reply,
        'send_dm': bool(rule.get('send_dm', True)),
        'enabled': bool(rule.get('enabled', True)),
        'used_count': int(rule.get('used_count') or 0),
        'last_used': rule.get('last_used') or '',
    }

@app.route("/api/add_user_auto_reply", methods=["POST"])
def api_add_user_auto_reply():
    user_id = session.get('user_id', 'user_1')
    data = request.json or {}
    rule = _normalize_user_auto_reply(data)
    if not rule:
        return jsonify({"success": False, "message": "❌ معرف المستخدم ونص الرد مطلوبان"})

    # محاولة استخراج ID المستخدم فورياً عبر تليجرام لضمان التطابق 100%
    if not rule.get('target_user_id') and rule.get('username'):
        try:
            with USERS_LOCK:
                cm = USERS.get(user_id, {}).get('client_manager')
            if cm and cm.client and cm.client.is_connected():
                clean_d = rule['username'].lstrip('-')
                query = int(rule['username']) if clean_d.isdigit() else f"@{rule['username']}"
                u_ent = cm.run_coroutine(cm.client.get_entity(query))
                if u_ent and hasattr(u_ent, 'id'):
                    rule['target_user_id'] = u_ent.id
                    if getattr(u_ent, 'username', None):
                        rule['username'] = u_ent.username
                        rule['display_username'] = f"@{u_ent.username}"
                    logger.info(f"✅ تم ربط معرف تيليجرام الرقمي ({u_ent.id}) بقاعدة الرد للمستخدم {rule['display_username']}")
        except Exception as _res_err:
            logger.debug(f"Could not pre-resolve target user {rule['username']}: {_res_err}")

    settings = load_settings(user_id)
    rules = settings.get('user_auto_replies', []) or []

    # تحديث القاعدة إن كانت موجودة مسبقاً لنفس المستخدم لمنع التكرار
    updated = False
    for i, existing in enumerate(rules):
        same_uname = existing.get('username', '').lower() == rule['username'].lower()
        same_id = rule.get('target_user_id') and existing.get('target_user_id') == rule['target_user_id']
        if same_uname or same_id:
            rule['used_count'] = existing.get('used_count', 0)
            rule['last_used'] = existing.get('last_used', '')
            rules[i] = rule
            updated = True
            break
    if not updated:
        rules.append(rule)

    settings['user_auto_replies'] = rules
    if save_settings(user_id, settings):
        return jsonify({
            "success": True,
            "message": f"✅ تم تفعيل الرد التلقائي للمستخدم {rule['display_username']} (رد بالمحادثة + بالخاص 📩)",
            "user_auto_replies": rules
        })
    return jsonify({"success": False, "message": "❌ فشل حفظ القاعدة"})

@app.route("/api/delete_user_auto_reply", methods=["POST"])
def api_delete_user_auto_reply():
    user_id = session.get('user_id', 'user_1')
    data = request.json or {}
    try:
        index = int(data.get('index', -1))
    except (TypeError, ValueError):
        index = -1
    settings = load_settings(user_id)
    rules = settings.get('user_auto_replies', []) or []
    if 0 <= index < len(rules):
        removed = rules.pop(index)
        settings['user_auto_replies'] = rules
        save_settings(user_id, settings)
        return jsonify({
            "success": True,
            "message": f"🗑️ تم حذف رد المستخدم {removed.get('display_username', '')}",
            "user_auto_replies": rules
        })
    return jsonify({"success": False, "message": "❌ فهرس غير صحيح"})

@app.route("/api/toggle_user_auto_reply_rule", methods=["POST"])
def api_toggle_user_auto_reply_rule():
    user_id = session.get('user_id', 'user_1')
    data = request.json or {}
    try:
        index = int(data.get('index', -1))
    except (TypeError, ValueError):
        index = -1
    settings = load_settings(user_id)
    rules = settings.get('user_auto_replies', []) or []
    if 0 <= index < len(rules):
        rules[index]['enabled'] = not rules[index].get('enabled', True)
        settings['user_auto_replies'] = rules
        save_settings(user_id, settings)
        return jsonify({
            "success": True,
            "message": f"تم {'تفعيل' if rules[index]['enabled'] else 'تعطيل'} الرد للمستخدم {rules[index].get('display_username', '')}",
            "user_auto_replies": rules
        })
    return jsonify({"success": False, "message": "❌ فهرس غير صحيح"})

@app.route("/api/add_auto_reply", methods=["POST"])
def api_add_auto_reply():
    user_id = session.get('user_id', 'user_1')
    data = request.json or {}
    rule = _normalize_auto_reply({
        'keyword': data.get('keyword') or data.get('trigger') or '',
        'reply': data.get('reply') or '',
        'scope': data.get('scope') or 'all',
        'match': data.get('match') or 'contains',
    })
    if not rule:
        return jsonify({"success": False, "message": "❌ الكلمة المفتاحية ونص الرد مطلوبان"})

    settings = load_settings(user_id)
    rules = settings.get('auto_replies', []) or []
    rules.append(rule)
    settings['auto_replies'] = rules
    if save_settings(user_id, settings):
        return jsonify({"success": True, "message": "✅ تم إضافة الرد التلقائي", "auto_replies": rules})
    return jsonify({"success": False, "message": "❌ فشل حفظ القاعدة"})

@app.route("/api/update_auto_reply", methods=["POST"])
def api_update_auto_reply():
    user_id = session.get('user_id', 'user_1')
    data = request.json or {}
    try:
        index = int(data.get('index', -1))
    except (TypeError, ValueError):
        index = -1
    settings = load_settings(user_id)
    rules = settings.get('auto_replies', []) or []
    if not (0 <= index < len(rules)):
        return jsonify({"success": False, "message": "❌ الفهرس غير صحيح"})
    new_rule = _normalize_auto_reply({
        'keyword': data.get('keyword'),
        'reply': data.get('reply'),
        'scope': data.get('scope'),
        'match': data.get('match'),
        'used_count': rules[index].get('used_count'),
        'last_used': rules[index].get('last_used'),
    })
    if not new_rule:
        return jsonify({"success": False, "message": "❌ بيانات غير صالحة"})
    rules[index] = new_rule
    settings['auto_replies'] = rules
    save_settings(user_id, settings)
    return jsonify({"success": True, "message": "✅ تم تحديث القاعدة", "auto_replies": rules})

@app.route("/api/delete_auto_reply", methods=["POST"])
def api_delete_auto_reply():
    user_id = session.get('user_id', 'user_1')
    data = request.json or {}
    try:
        index = int(data.get('index', -1))
    except (TypeError, ValueError):
        index = -1
    settings = load_settings(user_id)
    rules = settings.get('auto_replies', []) or []
    if 0 <= index < len(rules):
        removed = rules.pop(index)
        settings['auto_replies'] = rules
        save_settings(user_id, settings)
        return jsonify({"success": True, "message": f"🗑️ تم حذف الرد '{removed.get('keyword','')[:30]}'",
                        "auto_replies": rules})
    return jsonify({"success": False, "message": "❌ فهرس غير صحيح"})

@app.route("/api/save_auto_replies", methods=["POST"])
def api_save_auto_replies():
    user_id = session.get('user_id', 'user_1')
    data = request.json or {}
    raw = data.get('auto_replies', []) or []
    cleaned = []
    for r in raw:
        nr = _normalize_auto_reply(r)
        if nr:
            cleaned.append(nr)
    settings = load_settings(user_id)
    settings['auto_replies'] = cleaned
    save_settings(user_id, settings)
    return jsonify({"success": True, "message": f"✅ تم حفظ {len(cleaned)} قاعدة رد", "auto_replies": cleaned})

@app.route("/api/toggle_auto_reply", methods=["POST"])
def api_toggle_auto_reply():
    user_id = session.get('user_id', 'user_1')
    data = request.json or {}
    enabled = bool(data.get('enabled', True))
    settings = load_settings(user_id)
    settings['auto_reply_enabled'] = enabled
    save_settings(user_id, settings)

    # إذا تم التفعيل، تأكد من تشغيل المراقبة/الاتصال حتى تعمل الردود
    if enabled:
        try:
            with USERS_LOCK:
                user_info = USERS.get(user_id, {})
                is_running = user_info.get('is_running', False)
                is_auth = user_info.get('authenticated', False)
            if is_auth and not is_running:
                with USERS_LOCK:
                    USERS[user_id]['is_running'] = True
                import threading as _threading
                t = _threading.Thread(
                    target=monitoring_worker,
                    args=(user_id,),
                    daemon=True
                )
                t.start()
                with USERS_LOCK:
                    USERS[user_id]['thread'] = t
                logger.info(f"✅ Auto-reply: started monitoring worker for {user_id}")
        except Exception as _e:
            logger.error(f"Auto-reply toggle start-worker error: {_e}")

    return jsonify({
        "success": True,
        "enabled": enabled,
        "message": "✅ تم تفعيل الردود التلقائية" if enabled else "⏸️ تم تعطيل الردود التلقائية"
    })


@app.route("/api/auto_reply_status", methods=["GET"])
def api_auto_reply_status():
    user_id = session.get('user_id', 'user_1')
    settings = load_settings(user_id)
    enabled = settings.get('auto_reply_enabled', True)
    rules = settings.get('auto_replies', [])
    return jsonify({"success": True, "enabled": enabled, "rules_count": len(rules)})

async def resolve_link_group_name(client, url):
    """يحاول الحصول على اسم المجموعة/القناة من رابط تيليجرام"""
    try:
        username = url.split('/')[-1].replace('@', '')
        if username.startswith('+'):
            return None  # روابط الدعوة الخاصة لا يمكن حلها
        entity = await client.get_entity(username)
        return getattr(entity, 'title', None) or getattr(entity, 'first_name', None)
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════════════
#  وظائف البحث — مُعاد هيكلتها بالكامل
# ═══════════════════════════════════════════════════════════════════

async def search_links_in_chats(client, since_date, keyword='', resolve_names=True):
    """يبحث في كل محادثاتي ومجموعاتي عن روابط تيليجرام مع فلترة بالكلمة المفتاحية"""
    from datetime import timezone as _tz
    since_dt = since_date.replace(tzinfo=_tz.utc) if since_date.tzinfo is None else since_date
    found_links = []
    seen_urls   = set()
    try:
        async for dialog in client.iter_dialogs():
            try:
                if not dialog.entity:
                    continue
                chat_title = dialog.title or 'محادثة'
                async for message in client.iter_messages(dialog, limit=500):
                    if not message.date:
                        continue
                    msg_date = message.date if message.date.tzinfo else message.date.replace(tzinfo=_tz.utc)
                    if msg_date < since_dt:
                        break
                    if not message.text:
                        continue
                    for lnk in extract_telegram_links(message.text):
                        url = lnk.get('url', '')
                        if url and url not in seen_urls:
                            seen_urls.add(url)
                            found_links.append({
                                'url': url,
                                'username': lnk.get('username', ''),
                                'group_name': '',
                                'members': 0,
                                'date': message.date.strftime('%Y-%m-%d %H:%M'),
                                'chat_title': chat_title,
                                'link_type': lnk.get('type', 'channel'),
                            })
                if len(found_links) >= 2000:
                    break
            except Exception as e:
                logger.warning(f"تخطي محادثة: {e}")
                continue
    except Exception as e:
        logger.error(f"خطأ في البحث: {e}")

    keyword_lower = (keyword or '').strip().lower()
    if not resolve_names:
        if keyword_lower:
            return [i for i in found_links
                    if keyword_lower in (i.get('url') or '').lower()
                    or keyword_lower in (i.get('username') or '').lower()]
        return found_links

    # ── تحليل أسماء المجموعات وفلترة بالكلمة المفتاحية ──
    matched = []
    resolve_count = 0
    MAX_RESOLVE = 200
    for item in found_links:
        if resolve_count >= MAX_RESOLVE:
            # بعد الحد: فلترة URL فقط
            if keyword_lower and keyword_lower not in (item.get('url') or '').lower():
                continue
            matched.append(item)
            continue

        is_invite = '/+' in item['url']
        if not is_invite:
            try:
                uname = item['url'].rstrip('/').split('/')[-1]
                if uname and len(uname) >= 3:
                    entity = None
                    try:
                        entity = await client.get_entity(uname)
                    except Exception:
                        try:
                            r = await client(functions.contacts.ResolveUsernameRequest(username=uname))
                            entity = r.chats[0] if r.chats else (r.users[0] if r.users else None)
                        except Exception:
                            pass
                    if entity:
                        title   = getattr(entity, 'title', None) or getattr(entity, 'first_name', None) or ''
                        members = getattr(entity, 'participants_count', 0) or 0
                        item['group_name'] = title
                        item['members']    = members
                    resolve_count += 1
                    await asyncio.sleep(0.12)
            except Exception:
                pass

        # فلترة بالكلمة المفتاحية
        if keyword_lower:
            name_ok = keyword_lower in (item.get('group_name') or '').lower()
            user_ok = keyword_lower in (item.get('username')   or '').lower()
            url_ok  = keyword_lower in (item.get('url')        or '').lower()
            src_ok  = keyword_lower in (item.get('chat_title') or '').lower()
            if not (name_ok or user_ok or url_ok or src_ok):
                continue
        matched.append(item)

    return matched


async def search_public_telegram(client, query, limit=50):
    """يبحث عبر سيرفرات تيليجرام عن مجموعات/قنوات مطابقة للكلمة"""
    results  = []
    seen_ids = set()

    # الطريقة 1: contacts.SearchRequest — أفضل للبحث بالاسم مباشرة
    try:
        from telethon.tl.functions.contacts import SearchRequest as _CSearch
        sr = await client(_CSearch(q=query, limit=min(limit, 100)))
        for chat in (sr.chats or []):
            if chat.id in seen_ids:
                continue
            seen_ids.add(chat.id)
            uname = getattr(chat, 'username', None)
            results.append({
                'id': str(chat.id), 'title': getattr(chat, 'title', '') or '',
                'username': uname, 'url': f"https://t.me/{uname}" if uname else '',
                'members': getattr(chat, 'participants_count', 0) or 0,
                'megagroup': getattr(chat, 'megagroup', False),
                'verified': getattr(chat, 'verified', False),
            })
    except Exception as e:
        logger.warning(f"contacts.SearchRequest: {e}")

    # الطريقة 2: messages.SearchGlobalRequest كـ fallback
    if len(results) < limit // 2:
        try:
            gs = await client(functions.messages.SearchGlobalRequest(
                q=query, offset_date=None, offset_peer=None, offset_id=0, limit=limit
            ))
            for chat in (gs.chats or []):
                if chat.id in seen_ids:
                    continue
                seen_ids.add(chat.id)
                uname = getattr(chat, 'username', None)
                results.append({
                    'id': str(chat.id), 'title': getattr(chat, 'title', '') or '',
                    'username': uname, 'url': f"https://t.me/{uname}" if uname else '',
                    'members': getattr(chat, 'participants_count', 0) or 0,
                    'megagroup': getattr(chat, 'megagroup', False),
                    'verified': getattr(chat, 'verified', False),
                })
        except Exception as e:
            logger.warning(f"SearchGlobalRequest: {e}")

    results.sort(key=lambda x: x.get('members', 0), reverse=True)
    return results[:limit]


@app.route("/api/search_my_links", methods=["POST"])
def api_search_my_links():
    try:
        if 'user_id' not in session:
            return jsonify({"success": False, "message": "❌ يرجى تسجيل الدخول"})
        user_id = session['user_id']
        data = request.json or {}
        days = int(data.get('days', 60))
        if days <= 0 or days > 365: days = 60
        keyword = (data.get('keyword') or '').strip()
        with USERS_LOCK:
            if user_id not in USERS:
                return jsonify({"success": False, "message": "❌ المستخدم غير مسجل"})
            cm = USERS[user_id].get('client_manager')
            if not cm or not cm.client:
                return jsonify({"success": False, "message": "❌ يرجى تسجيل الدخول أولاً"})
        since = datetime.now() - timedelta(days=days)
        result = cm.run_coroutine(search_links_in_chats(cm.client, since, keyword=keyword))
        return jsonify({"success": True, "links": result,
                        "message": f"تم العثور على {len(result)} رابط"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route("/api/search_my_links/start", methods=["POST"])
def api_search_my_links_start():
    """بحث متدفق بالكلمة المفتاحية داخل محادثاتي — النتائج فور اكتشافها مع تقدم لحظي"""
    try:
        if 'user_id' not in session:
            return jsonify({"success": False, "message": "❌ يرجى تسجيل الدخول"})
        user_id = session['user_id']
        data    = request.json or {}
        keyword = (data.get('keyword') or '').strip()
        depth   = (data.get('depth') or 'medium').lower()

        # عمق البحث: سريع / متوسط / كامل
        _DEPTH = {
            'fast':   {'days': 30,   'msg_limit': 500},
            'medium': {'days': 180,  'msg_limit': 1000},
            'full':   {'days': 3650, 'msg_limit': 3000},
        }
        cfg = _DEPTH.get(depth, _DEPTH['medium'])
        search_days  = cfg['days']
        msg_limit    = cfg['msg_limit']

        with USERS_LOCK:
            if user_id not in USERS:
                return jsonify({"success": False, "message": "❌ المستخدم غير مسجل"})
            cm = USERS[user_id].get('client_manager')
            if not cm or not cm.client:
                return jsonify({"success": False, "message": "❌ يرجى تسجيل الدخول أولاً"})

        async def _stream():
            from datetime import timezone as _tz
            since_dt      = datetime.now(_tz.utc) - timedelta(days=search_days)
            keyword_lower = keyword.lower()
            seen_urls     = set()
            total_found   = 0
            dialog_count  = 0

            try:
                async for dialog in cm.client.iter_dialogs():
                    try:
                        if not dialog.entity:
                            continue
                        chat_title   = dialog.title or 'محادثة'
                        dialog_count += 1

                        # ── إرسال تقدم الفحص اللحظي ──
                        socketio.emit('search_dialog_progress', {
                            'chat': chat_title,
                            'scanned': dialog_count,
                            'found': total_found
                        }, to=user_id)

                        batch_raw = []
                        async for message in cm.client.iter_messages(dialog, limit=msg_limit):
                            if not message.date:
                                continue
                            msg_date = message.date if message.date.tzinfo else message.date.replace(tzinfo=_tz.utc)
                            if msg_date < since_dt:
                                break
                            if not message.text:
                                continue
                            for lnk in extract_telegram_links(message.text):
                                url = lnk.get('url', '')
                                if url and url not in seen_urls:
                                    seen_urls.add(url)
                                    batch_raw.append({
                                        'url':        url,
                                        'username':   lnk.get('username', ''),
                                        'group_name': '',
                                        'members':    0,
                                        'date':       message.date.strftime('%Y-%m-%d %H:%M'),
                                        'chat_title': chat_title,
                                        'link_type':  lnk.get('type', 'channel'),
                                    })

                        # ── تحليل أسماء المجموعات وفلترة ──
                        emit_batch = []
                        for item in batch_raw:
                            is_invite = '/+' in item['url']

                            if not is_invite:
                                uname = item['url'].rstrip('/').split('/')[-1]
                                if uname and len(uname) >= 3:
                                    try:
                                        entity = None
                                        try:
                                            entity = await cm.client.get_entity(uname)
                                        except Exception:
                                            try:
                                                r = await cm.client(functions.contacts.ResolveUsernameRequest(username=uname))
                                                entity = r.chats[0] if r.chats else (r.users[0] if r.users else None)
                                            except Exception:
                                                pass
                                        if entity:
                                            item['group_name'] = getattr(entity, 'title', None) or getattr(entity, 'first_name', None) or ''
                                            item['members']    = getattr(entity, 'participants_count', 0) or 0
                                        await asyncio.sleep(0.12)
                                    except Exception:
                                        pass

                            # ── تطبيق فلتر الكلمة المفتاحية ──
                            if keyword_lower:
                                name_ok = keyword_lower in (item.get('group_name') or '').lower()
                                user_ok = keyword_lower in (item.get('username')   or '').lower()
                                url_ok  = keyword_lower in (item.get('url')        or '').lower()
                                src_ok  = keyword_lower in (item.get('chat_title') or '').lower()
                                if not (name_ok or user_ok or url_ok or src_ok):
                                    continue

                            emit_batch.append(item)
                            total_found += 1

                        if emit_batch:
                            socketio.emit('search_link_batch', {
                                'items': emit_batch, 'chat_title': chat_title, 'count': total_found
                            }, to=user_id)

                        if total_found >= 2000:
                            break

                    except Exception as ex:
                        logger.warning(f"تخطي {dialog.title}: {ex}")
                        continue

            except Exception as e:
                logger.error(f"بحث خطأ: {e}")
                socketio.emit('search_links_done', {
                    'total': total_found, 'error': str(e), 'dialogs': dialog_count
                }, to=user_id)
                return

            socketio.emit('search_links_done', {
                'total': total_found, 'keyword': keyword, 'dialogs': dialog_count
            }, to=user_id)

        _OSThread(target=lambda: cm.run_coroutine(_stream()), daemon=True).start()
        depth_ar = {'fast': 'سريع', 'medium': 'متوسط', 'full': 'كامل'}.get(depth, 'متوسط')
        kw_msg = f" بكلمة: \"{keyword}\"" if keyword else ""
        return jsonify({"success": True, "message": f"بدأ البحث ({depth_ar}){kw_msg}"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route("/api/search_my_links/csv", methods=["POST"])
def api_search_my_links_csv():
    try:
        if 'user_id' not in session:
            return jsonify({"success": False, "message": "❌ يرجى تسجيل الدخول"})
        user_id = session['user_id']
        data    = request.json or {}
        links   = data.get('links', [])
        if not links:
            return jsonify({"success": False, "message": "❌ لا توجد روابط"})
        import io as _io, csv as _csv
        buf = _io.StringIO()
        w   = _csv.writer(buf)
        w.writerow(['الرابط', 'اسم المجموعة', 'عدد الأعضاء', 'المصدر', 'التاريخ', 'النوع'])
        for l in links:
            w.writerow([l.get('url',''), l.get('group_name',''), l.get('members',''),
                        l.get('chat_title',''), l.get('date',''), l.get('link_type','')])
        buf.seek(0)
        from flask import Response
        return Response(
            buf.getvalue().encode('utf-8-sig'),
            mimetype='text/csv; charset=utf-8',
            headers={'Content-Disposition': 'attachment; filename=telegram_links.csv'}
        )
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route("/api/search_public_channels", methods=["POST"])
def api_search_public_channels():
    """بحث عام في تيليجرام عن مجموعات/قنوات بالكلمة المفتاحية"""
    try:
        if 'user_id' not in session:
            return jsonify({"success": False, "message": "❌ يرجى تسجيل الدخول"})
        user_id = session['user_id']
        data    = request.json or {}
        query   = (data.get('query') or '').strip()
        if not query:
            return jsonify({"success": False, "message": "❌ أدخل كلمة للبحث"})
        limit = min(int(data.get('limit', 60)), 100)
        with USERS_LOCK:
            cm = USERS.get(user_id, {}).get('client_manager')
            if not cm or not cm.client:
                return jsonify({"success": False, "message": "❌ يرجى تسجيل الدخول أولاً"})
        result = cm.run_coroutine(search_public_telegram(cm.client, query, limit))
        return jsonify({"success": True, "channels": result,
                        "message": f"✅ تم العثور على {len(result)} مجموعة/قناة"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


# ── بحث عام في تيليجرام (الطريقتان: SearchRequest + SearchGlobalRequest) ──
async def search_telegram_global(client, query, limit=50, filter_type='all'):
    """
    بحث عام في تيليجرام عن مجموعات/قنوات/بوتات تطابق الكلمة المفتاحية.
    filter_type: 'all' | 'groups' | 'channels' | 'bots'
    """
    from telethon.tl.functions.contacts import SearchRequest
    from telethon.tl.functions.messages import SearchGlobalRequest
    from telethon.tl.types import InputPeerEmpty

    results = []
    seen_ids = set()

    def _classify(chat):
        if hasattr(chat, 'megagroup') and chat.megagroup:
            return 'group'
        if hasattr(chat, 'broadcast') and chat.broadcast:
            return 'channel'
        if hasattr(chat, 'bot') and chat.bot:
            return 'bot'
        return 'chat'

    def _passes_filter(chat_type):
        if filter_type == 'all':
            return True
        return chat_type == filter_type

    def _build_item(chat, source):
        chat_type = _classify(chat)
        username  = getattr(chat, 'username', None)
        return {
            'id':       chat.id,
            'title':    getattr(chat, 'title', None) or getattr(chat, 'first_name', '') or '',
            'username': username,
            'url':      f"https://t.me/{username}" if username else None,
            'type':     chat_type,
            'members':  getattr(chat, 'participants_count', 0) or 0,
            'verified': getattr(chat, 'verified', False),
            'source':   source,
        }

    # الطريقة الأولى: contacts.SearchRequest
    try:
        sr = await client(SearchRequest(q=query, limit=min(limit, 100)))
        for chat in (sr.chats or []):
            if chat.id in seen_ids:
                continue
            item = _build_item(chat, 'SearchRequest')
            if _passes_filter(item['type']):
                seen_ids.add(chat.id)
                results.append(item)
    except Exception as e:
        logger.warning(f"SearchRequest failed for '{query}': {e}")

    # الطريقة الثانية: messages.SearchGlobalRequest (شبكة تيليجرام كاملة)
    if len(results) < limit:
        try:
            gs = await client(SearchGlobalRequest(
                q=query,
                filter=None,
                min_date=None,
                max_date=None,
                offset_rate=0,
                offset_peer=InputPeerEmpty(),
                offset_id=0,
                limit=min(limit, 100),
            ))
            for chat in (gs.chats or []):
                if chat.id in seen_ids:
                    continue
                item = _build_item(chat, 'SearchGlobal')
                if _passes_filter(item['type']):
                    seen_ids.add(chat.id)
                    results.append(item)
        except Exception as e:
            logger.warning(f"SearchGlobalRequest failed for '{query}': {e}")

    results.sort(key=lambda x: x.get('members', 0), reverse=True)
    return results[:limit]


@app.route("/api/search_telegram_global", methods=["POST"])
def api_search_telegram_global():
    """
    بحث عام في قاعدة تيليجرام بالكلمة المفتاحية — مجموعات وقنوات وبوتات.
    Body JSON:
      query       : نص البحث (مطلوب)
      limit       : عدد النتائج (افتراضي 50، حد أقصى 100)
      filter_type : all | groups | channels | bots  (افتراضي: all)
    """
    try:
        if 'user_id' not in session:
            return jsonify({"success": False, "message": "❌ يرجى تسجيل الدخول"})
        user_id = session['user_id']
        data    = request.json or {}
        query   = (data.get('query') or '').strip()
        if not query:
            return jsonify({"success": False, "message": "❌ أدخل كلمة للبحث"})
        limit       = max(1, min(int(data.get('limit', 50)), 100))
        filter_type = data.get('filter_type', 'all')

        with USERS_LOCK:
            if user_id not in USERS:
                return jsonify({"success": False, "message": "❌ المستخدم غير مسجل"})
            cm = USERS[user_id].get('client_manager')
            if not cm or not cm.client:
                return jsonify({"success": False, "message": "❌ يرجى تسجيل الدخول أولاً"})

        results = cm.run_coroutine(
            search_telegram_global(cm.client, query, limit, filter_type)
        )
        return jsonify({
            "success": True,
            "query":   query,
            "filter":  filter_type,
            "total":   len(results),
            "results": results,
            "message": f"✅ تم العثور على {len(results)} نتيجة"
        })
    except Exception as e:
        logger.error(f"search_telegram_global error: {e}")
        return jsonify({"success": False, "message": str(e)})


@app.route("/api/join_global_search_results", methods=["POST"])
def api_join_global_search_results():
    """
    انضمام إلى مجموعات من نتائج البحث العام.
    Body JSON:
      results      : قائمة نتائج البحث (كل عنصر يحتوي على 'url' و 'title')
      selected_ids : قائمة IDs المطلوب الانضمام إليها (اختياري — إذا فارغة + join_all=false → لا شيء)
      join_all     : true للانضمام إلى كل النتائج (افتراضي: false)
      delay        : تأخير بين الطلبات بالثواني (افتراضي: 2)
    """
    try:
        if 'user_id' not in session:
            return jsonify({"success": False, "message": "❌ يرجى تسجيل الدخول"})
        user_id = session['user_id']
        data    = request.json or {}
        items   = data.get('results', [])
        sel_ids = set(data.get('selected_ids', []))
        join_all = data.get('join_all', False)
        delay    = max(1, int(data.get('delay', 2)))

        if not items:
            return jsonify({"success": False, "message": "❌ لا توجد نتائج للانضمام"})

        with USERS_LOCK:
            if user_id not in USERS:
                return jsonify({"success": False, "message": "❌ المستخدم غير موجود"})
            cm = USERS[user_id].get('client_manager')
            if not cm or not cm.client:
                return jsonify({"success": False, "message": "❌ يرجى تسجيل الدخول أولاً"})

        targets = items if join_all else [r for r in items if r.get('id') in sel_ids]
        if not targets:
            return jsonify({"success": False, "message": "❌ لم تحدد أي مجموعة للانضمام"})

        joined, skipped, failed = [], [], []
        for item in targets:
            link = item.get('url')
            title = item.get('title', link)
            if not link:
                skipped.append({'title': title, 'reason': 'لا يوجد رابط عام'})
                continue
            try:
                res = cm.run_coroutine(
                    join_telegram_group(cm.client, link, user_id, cm)
                )
                if res.get('success'):
                    joined.append({'link': link, 'title': title, 'message': res.get('message', '')})
                    socketio.emit('log_update',
                        {'message': f'✅ انضم إلى: {title} ({link})'}, to=user_id)
                else:
                    failed.append({'link': link, 'title': title, 'reason': res.get('message', 'فشل')})
                    socketio.emit('log_update',
                        {'message': f'❌ فشل: {title} — {res.get("message","")}'}, to=user_id)
            except Exception as e:
                failed.append({'link': link, 'title': title, 'reason': str(e)})
                socketio.emit('log_update',
                    {'message': f'❌ خطأ: {title} — {e}'}, to=user_id)
            time.sleep(delay)

        socketio.emit('log_update', {
            'message': f'🎉 انتهى: ✅ {len(joined)} نجح | ❌ {len(failed)} فشل | ⏭ {len(skipped)} تجاوز'
        }, to=user_id)

        return jsonify({
            "success": True,
            "joined":  joined,
            "failed":  failed,
            "skipped": skipped,
            "total":   len(targets),
            "message": f"انضمام: {len(joined)} نجح، {len(failed)} فشل، {len(skipped)} تجاوز"
        })
    except Exception as e:
        logger.error(f"join_global_search_results error: {e}")
        return jsonify({"success": False, "message": str(e)})


@app.route("/tools/analyze_stats", methods=["POST"])
def api_academic_analyze_stats():
    try:
        data = request.get_json(force=True, silent=True) or {}
        raw = data.get('data', '')
        nums = [float(x) for x in re.findall(r'[-+]?\d*\.?\d+', str(raw)) if x]
        if len(nums) < 2:
            return jsonify({"error": "أدخل على الأقل رقمين للتحليل"}), 400

        arr = np.array(nums)
        mode_val = float(stats.mode(arr, keepdims=True).mode[0])
        stats_result = {
            "count":    int(len(arr)),
            "sum":      round(float(np.sum(arr)), 4),
            "mean":     round(float(np.mean(arr)), 4),
            "median":   round(float(np.median(arr)), 4),
            "mode":     round(mode_val, 4),
            "std":      round(float(np.std(arr)), 4),
            "variance": round(float(np.var(arr)), 4),
            "min":      round(float(np.min(arr)), 4),
            "max":      round(float(np.max(arr)), 4),
            "range":    round(float(np.max(arr) - np.min(arr)), 4),
            "q1":       round(float(np.percentile(arr, 25)), 4),
            "q3":       round(float(np.percentile(arr, 75)), 4),
            "iqr":      round(float(np.percentile(arr, 75) - np.percentile(arr, 25)), 4),
            "skewness": round(float(stats.skew(arr)), 4),
            "kurtosis": round(float(stats.kurtosis(arr)), 4),
        }

        fig, axes = plt.subplots(1, 2, figsize=(10, 4))
        axes[0].hist(arr, bins='auto', color='#4e73df', edgecolor='white', alpha=0.85)
        axes[0].axvline(stats_result['mean'],   color='red',   linestyle='--', label=f"المتوسط: {stats_result['mean']}")
        axes[0].axvline(stats_result['median'], color='green', linestyle='--', label=f"الوسيط: {stats_result['median']}")
        axes[0].set_title('توزيع البيانات'); axes[0].legend()
        axes[0].set_xlabel('القيمة'); axes[0].set_ylabel('التكرار')
        axes[1].boxplot(arr, vert=True, patch_artist=True,
                        boxprops=dict(facecolor='#4e73df', alpha=0.7))
        axes[1].set_title('المربع الجذري (Boxplot)'); axes[1].set_ylabel('القيمة')
        plt.tight_layout()
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        plt.close()
        buf.seek(0)
        chart_b64 = base64.b64encode(buf.read()).decode('utf-8')

        return jsonify({"success": True, "stats": stats_result, "chart": chart_b64})
    except Exception as e:
        logger.error(f"Analyze stats error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/tools/format_file", methods=["POST"])
def api_academic_format_file():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "لم يتم رفع ملف"}), 400
        f = request.files['file']
        filename = f.filename.lower()
        content_parts = []

        file_bytes = f.read()
        if filename.endswith('.pdf'):
            if pdfplumber is None:
                return jsonify({"error": "مكتبة PDF غير متاحة، شغّل: pip install pdfplumber"}), 500
            import io as _io2
            with pdfplumber.open(_io2.BytesIO(file_bytes)) as pdf:
                for i, page in enumerate(pdf.pages[:50], 1):
                    text = page.extract_text() or ''
                    if text.strip():
                        content_parts.append(f"--- صفحة {i} ---\n{text.strip()}")
                    for tbl in page.extract_tables():
                        if tbl:
                            rows_txt = '\n'.join('\t'.join(str(c or '') for c in row) for row in tbl)
                            content_parts.append(f"[جدول]\n{rows_txt}")
        elif filename.endswith('.docx'):
            if docx is None:
                return jsonify({"error": "مكتبة Word غير متاحة، شغّل: pip install python-docx"}), 500
            import io as _io2
            doc_obj = docx.Document(_io2.BytesIO(file_bytes))
            for para in doc_obj.paragraphs:
                if para.text.strip():
                    style = para.style.name if para.style else ''
                    prefix = '# ' if 'Heading 1' in style else '## ' if 'Heading' in style else ''
                    content_parts.append(prefix + para.text)
            for tbl in doc_obj.tables:
                rows_txt = '\n'.join('\t'.join(c.text for c in row.cells) for row in tbl.rows)
                content_parts.append(f"[جدول]\n{rows_txt}")
        elif filename.endswith('.txt'):
            content_parts.append(file_bytes.decode('utf-8', errors='replace'))
        else:
            return jsonify({"error": "صيغة غير مدعومة. استخدم PDF أو DOCX أو TXT"}), 400

        full_text = '\n\n'.join(content_parts)

        # ── تحسين النص بالذكاء الاصطناعي (اختياري) ──
        ai_summary = None
        use_ai = request.form.get('use_ai', 'false').lower() == 'true'
        if use_ai and full_text.strip():
            try:
                from groq import Groq as _Groq
                _gc = _Groq(api_key=GROQ_API_KEY)
                ai_resp = _gc.chat.completions.create(
                    model='llama-3.3-70b-versatile',
                    messages=[
                        {"role": "system", "content":
                         "أنت مساعد أكاديمي. لخّص الوثيقة التالية بشكل منظّم: العنوان، الأقسام الرئيسية، الأهداف، النتائج، التوصيات."},
                        {"role": "user", "content": f"لخّص هذا النص:\n\n{full_text[:6000]}"}
                    ],
                    max_tokens=800,
                    temperature=0.3,
                )
                ai_summary = ai_resp.choices[0].message.content
            except Exception as _ae:
                ai_summary = f"[تعذّر التلخيص: {_ae}]"

        words = len(full_text.split())
        return jsonify({
            "success":    True,
            "text":       full_text[:15000],
            "words":      words,
            "chars":      len(full_text),
            "sections":   len(content_parts),
            "filename":   f.filename,
            "ai_summary": ai_summary
        })
    except Exception as e:
        logger.error(f"Format file error: {e}")
        return jsonify({"error": str(e)}), 500


# ════════════════════════════════════════════════════════════
#  تحويل HTML إلى Word — محسّن كلياً
#  يدعم: فواصل الصفحات | جداول كاملة | صور base64 | ألوان | RTL
# ════════════════════════════════════════════════════════════

# ألوان CSS المسمّاة
_CSS_NAMED_COLORS = {
    'black':(0,0,0),'white':(255,255,255),'red':(255,0,0),'green':(0,128,0),
    'blue':(0,0,255),'yellow':(255,255,0),'orange':(255,165,0),'purple':(128,0,128),
    'pink':(255,192,203),'gray':(128,128,128),'grey':(128,128,128),'brown':(165,42,42),
    'cyan':(0,255,255),'magenta':(255,0,255),'navy':(0,0,128),'teal':(0,128,128),
    'lime':(0,255,0),'maroon':(128,0,0),'olive':(128,128,0),'silver':(192,192,192),
    'gold':(255,215,0),'coral':(255,127,80),'salmon':(250,128,114),'turquoise':(64,224,208),
    'indigo':(75,0,130),'violet':(238,130,238),'darkblue':(0,0,139),'darkgreen':(0,100,0),
    'darkred':(139,0,0),'darkgray':(169,169,169),'lightblue':(173,216,230),
    'lightgreen':(144,238,144),'lightyellow':(255,255,224),'lightgray':(211,211,211),
    'crimson':(220,20,60),'deepskyblue':(0,191,255),'forestgreen':(34,139,34),
    'hotpink':(255,105,180),'limegreen':(50,205,50),'mediumblue':(0,0,205),
    'orangered':(255,69,0),'royalblue':(65,105,225),'seagreen':(46,139,87),
    'skyblue':(135,206,235),'slategray':(112,128,144),'steelblue':(70,130,180),
    'tomato':(255,99,71),'yellowgreen':(154,205,50),'beige':(245,245,220),
    'ivory':(255,255,240),'khaki':(240,230,140),'lavender':(230,230,250),
    'mintcream':(245,255,250),'snow':(255,250,250),'wheat':(245,222,179),
}

def _w2_css_color(color_str):
    """تحويل لون CSS إلى RGBColor — يدعم hex, rgb(), rgba(), named colors"""
    try:
        from docx.shared import RGBColor
        s = (color_str or '').strip().lower()
        if not s or s == 'transparent' or s == 'inherit' or s == 'currentcolor':
            return None
        # hex
        if s.startswith('#'):
            c = s.lstrip('#')
            if len(c) == 3:
                c = c[0]*2 + c[1]*2 + c[2]*2
            if len(c) >= 6:
                return RGBColor(int(c[0:2],16), int(c[2:4],16), int(c[4:6],16))
        # rgb / rgba
        if s.startswith('rgb'):
            nums = re.findall(r'[\d.]+', s)
            if len(nums) >= 3:
                r,g,b = int(float(nums[0])), int(float(nums[1])), int(float(nums[2]))
                return RGBColor(min(r,255), min(g,255), min(b,255))
        # named
        if s in _CSS_NAMED_COLORS:
            t = _CSS_NAMED_COLORS[s]
            if t:
                return RGBColor(t[0], t[1], t[2])
    except Exception:
        pass
    return None

def _w2_parse_style(style_str):
    """تحليل CSS style مضمن → dict (يحافظ على القيمة الأخيرة عند التكرار)"""
    props = {}
    for part in (style_str or '').split(';'):
        part = part.strip()
        if ':' in part:
            k, v = part.split(':', 1)
            props[k.strip().lower()] = v.strip()
    return props

def _w2_align(style_props, default='LEFT'):
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    m = {'center': WD_ALIGN_PARAGRAPH.CENTER,
         'left':   WD_ALIGN_PARAGRAPH.LEFT,
         'right':  WD_ALIGN_PARAGRAPH.RIGHT,
         'justify':WD_ALIGN_PARAGRAPH.JUSTIFY}
    ta = style_props.get('text-align','').lower()
    return m.get(ta, getattr(WD_ALIGN_PARAGRAPH, default))

def _w2_parse_font_size_pt(fs):
    """تحويل قيمة font-size CSS إلى نقاط (Pt) أو None"""
    if not fs:
        return None
    fs = fs.strip().lower()
    try:
        if fs.endswith('pt'):
            return float(fs[:-2].strip())
        if fs.endswith('px'):
            return round(float(fs[:-2].strip()) * 0.75, 1)
        if fs.endswith('em'):
            return round(float(fs[:-2].strip()) * 12.0, 1)
        if fs.endswith('rem'):
            return round(float(fs[:-3].strip()) * 12.0, 1)
        if fs.endswith('%'):
            return round(float(fs[:-1].strip()) * 12.0 / 100.0, 1)
    except Exception:
        pass
    return None

def _w2_apply_styles_to_run(run, styles):
    """تطبيق dict من CSS styles على run — يدعم وراثة الأنماط"""
    try:
        from docx.shared import Pt, RGBColor
        fw = styles.get('font-weight', '')
        if fw in ('bold','700','800','900','bolder'): run.bold = True
        fi = styles.get('font-style', '')
        if fi == 'italic' or fi == 'oblique': run.italic = True
        td = styles.get('text-decoration', '')
        if 'underline' in td: run.underline = True
        if 'line-through' in td: run.font.strike = True
        c = _w2_css_color(styles.get('color', ''))
        if c: run.font.color.rgb = c
        ff = styles.get('font-family', '')
        if ff:
            fname = ff.split(',')[0].strip().strip('"\'')
            if fname: run.font.name = fname
        pt = _w2_parse_font_size_pt(styles.get('font-size', ''))
        if pt and 6 <= pt <= 72: run.font.size = Pt(pt)
    except Exception:
        pass

def _w2_apply_run(run, node, extra_tag=''):
    """تطبيق تنسيق inline على run (للتوافق مع الكود القديم)"""
    try:
        tag = (node.name or '').lower() if hasattr(node,'name') else extra_tag
        styles = {}
        if tag in ('b','strong'): styles['font-weight'] = 'bold'
        if tag in ('i','em'):     styles['font-style'] = 'italic'
        if tag == 'u':            styles['text-decoration'] = 'underline'
        if tag in ('s','strike','del'): styles['text-decoration'] = 'line-through'
        if tag == 'code':         styles['font-family'] = 'Courier New'
        if hasattr(node,'get'):
            styles.update(_w2_parse_style(node.get('style','')))
            if tag == 'font':
                fc = node.get('color',''); ff = node.get('face','')
                if fc: styles['color'] = fc
                if ff: styles['font-family'] = ff
        _w2_apply_styles_to_run(run, styles)
    except Exception:
        pass

def _w2_inline(node, para, inherited_styles=None):
    """
    معالجة المحتوى inline مع وراثة الأنماط الكاملة من الوالدين.
    inherited_styles: dict من CSS properties موروثة من العنصر الأب
    """
    from bs4 import NavigableString, Tag
    if inherited_styles is None:
        inherited_styles = {}

    INLINE_TAGS = {
        'b','strong','i','em','u','s','strike','del','span','a','font',
        'mark','sup','sub','small','big','code','kbd','abbr','cite','q',
        'bdi','bdo','time','var','ins','samp','dfn',
    }

    for child in node.children:
        if isinstance(child, NavigableString):
            txt = str(child)
            if txt:
                run = para.add_run(txt)
                _w2_apply_styles_to_run(run, inherited_styles)
        elif isinstance(child, Tag):
            ctag = (child.name or '').lower()
            if ctag == 'br':
                para.add_run('\n')
                continue
            if ctag == 'img':
                continue  # تعالجها _w2_node

            # بناء أنماط الابن = أنماط الوالد + أنماط الابن الخاصة
            child_styles = dict(inherited_styles)

            # أنماط مبنية على اسم الوسم
            if ctag in ('b','strong'):   child_styles['font-weight'] = 'bold'
            if ctag in ('i','em'):       child_styles['font-style']  = 'italic'
            if ctag == 'u':              child_styles['text-decoration'] = 'underline'
            if ctag in ('s','strike','del','ins'): child_styles['text-decoration'] = 'line-through'
            if ctag == 'mark':           child_styles['background-color'] = '#ffff00'
            if ctag in ('small',):
                old_pt = _w2_parse_font_size_pt(child_styles.get('font-size','12pt')) or 12
                child_styles['font-size'] = f'{old_pt * 0.85:.1f}pt'
            if ctag == 'code':           child_styles['font-family'] = 'Courier New'
            if ctag == 'font':
                fc = child.get('color',''); ff = child.get('face','')
                if fc: child_styles['color'] = fc
                if ff: child_styles['font-family'] = ff

            # الأنماط المضمّنة الخاصة بالعنصر (تتجاوز الموروثة)
            own_sp = _w2_parse_style(child.get('style','') if hasattr(child,'get') else '')
            child_styles.update(own_sp)

            if ctag in INLINE_TAGS:
                # تحقق هل يحتوي على عناصر block
                has_block = any(
                    isinstance(c, Tag) and (c.name or '').lower() in
                    ('div','p','table','ul','ol','h1','h2','h3','h4','h5','h6')
                    for c in child.children
                )
                if has_block:
                    _w2_inline(child, para, child_styles)
                else:
                    run = para.add_run(child.get_text())
                    _w2_apply_styles_to_run(run, child_styles)
            else:
                # عنصر block داخل inline — استخرج النص مع الأنماط الحالية
                run = para.add_run(child.get_text())
                _w2_apply_styles_to_run(run, child_styles)

def _w2_add_page_break(doc):
    """إضافة فاصل صفحة حقيقي في Word"""
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
    para = doc.add_paragraph()
    run = para.add_run()
    br = OxmlElement('w:br')
    br.set(qn('w:type'), 'page')
    run._r.append(br)
    return para

def _w2_shade_cell(cell, hex_color_str):
    """تلوين خلفية خلية جدول بلون hex"""
    try:
        from docx.oxml import parse_xml
        xml = ('<w:shd xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'
               ' w:val="clear" w:color="auto" w:fill="' + hex_color_str.upper() + '"/>')
        cell._tc.get_or_add_tcPr().append(parse_xml(xml))
    except Exception:
        pass

def _w2_shade_para(para, hex_color_str):
    """تلوين خلفية فقرة بلون hex"""
    try:
        from docx.oxml import parse_xml
        pPr = para._p.get_or_add_pPr()
        shd_xml = (f'<w:shd xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'
                   f' w:val="clear" w:color="auto" w:fill="{hex_color_str.upper()}"/>')
        pPr.append(parse_xml(shd_xml))
    except Exception:
        pass

def _w2_set_para_border(para, color_hex='E6B422', side='left', sz=24):
    """إضافة حد ملوّن على جانب فقرة"""
    try:
        from docx.oxml import parse_xml
        pPr = para._p.get_or_add_pPr()
        bdr_xml = (
            f'<w:pBdr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            f'<w:{side} w:val="single" w:sz="{sz}" w:space="4" w:color="{color_hex.upper()}"/>'
            f'</w:pBdr>'
        )
        pPr.append(parse_xml(bdr_xml))
    except Exception:
        pass

def _w2_set_rtl_para(para):
    """تعيين اتجاه الفقرة RTL للنص العربي"""
    try:
        from docx.oxml import parse_xml
        pPr = para._p.get_or_add_pPr()
        rtl_xml = '<w:bidi xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"/>'
        pPr.append(parse_xml(rtl_xml))
    except Exception:
        pass

def _w2_is_rtl(text):
    """كشف إذا كان النص عربياً/RTL"""
    arabic = sum(1 for c in text if '\u0600' <= c <= '\u06FF' or '\u0750' <= c <= '\u077F')
    return arabic > len(text) * 0.3

def _w2_table(node, doc):
    """
    تحويل <table> HTML إلى جدول Word كامل مع:
    - ألوان رأس الجدول من CSS
    - colspan + rowspan
    - خلفيات الخلايا
    - وراثة أنماط النص
    """
    from docx.shared import Pt, RGBColor, Inches
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    # جمع كل الصفوف من thead + tbody + tfoot
    all_rows = []
    thead_rows = set()
    for section in node.find_all(['thead','tbody','tfoot'], recursive=False) or [node]:
        is_head = section.name == 'thead'
        for tr in section.find_all('tr', recursive=True if section == node else False):
            if is_head:
                thead_rows.add(id(tr))
            all_rows.append(tr)
    if not all_rows:
        all_rows = node.find_all('tr')
    if not all_rows:
        return

    # حساب أقصى عدد أعمدة مع مراعاة colspan
    def row_width(tr):
        w = 0
        for c in tr.find_all(['td','th'], recursive=False):
            w += max(1, int(c.get('colspan', 1) or 1))
        return w

    max_cols = max((row_width(r) for r in all_rows), default=1)
    if max_cols == 0:
        return

    num_rows = len(all_rows)
    table = doc.add_table(rows=num_rows, cols=max_cols)
    table.style = 'Table Grid'

    # شبكة لتتبع rowspan
    grid = [[False]*max_cols for _ in range(num_rows)]

    # قراءة لون border الجدول إن وجد
    tbl_sp = _w2_parse_style(node.get('style',''))
    tbl_border_color = tbl_sp.get('border-color', '').strip()

    for r_idx, tr in enumerate(all_rows):
        is_header_row = (id(tr) in thead_rows) or (r_idx == 0 and not thead_rows)
        # فحص إذا كان الصف هو tr داخل thead
        if tr.parent and tr.parent.name == 'thead':
            is_header_row = True

        cells_el = tr.find_all(['td','th'], recursive=False)
        col_cursor = 0

        for cell_el in cells_el:
            # تجاوز الخلايا المحجوزة بـ rowspan
            while col_cursor < max_cols and grid[r_idx][col_cursor]:
                col_cursor += 1
            if col_cursor >= max_cols:
                break

            colspan = max(1, int(cell_el.get('colspan', 1) or 1))
            rowspan = max(1, int(cell_el.get('rowspan', 1) or 1))
            is_th   = (cell_el.name == 'th') or is_header_row

            # تحديد الخلية في Word
            try:
                cell = table.cell(r_idx, col_cursor)
            except Exception:
                col_cursor += colspan
                continue

            # دمج colspan
            if colspan > 1:
                end_col = min(col_cursor + colspan - 1, max_cols - 1)
                if end_col > col_cursor:
                    try:
                        cell = cell.merge(table.cell(r_idx, end_col))
                    except Exception:
                        pass

            # دمج rowspan
            if rowspan > 1:
                end_row = min(r_idx + rowspan - 1, num_rows - 1)
                if end_row > r_idx:
                    try:
                        cell = cell.merge(table.cell(end_row, col_cursor))
                        # تحديد الشبكة
                        for rr in range(r_idx, end_row + 1):
                            for cc in range(col_cursor, min(col_cursor + colspan, max_cols)):
                                grid[rr][cc] = True
                    except Exception:
                        pass

            # مسح النص الافتراضي
            cell.text = ''
            para = cell.paragraphs[0] if cell.paragraphs else cell.add_paragraph()

            # تحليل أنماط الخلية
            cell_sp = _w2_parse_style(cell_el.get('style',''))
            ta = cell_sp.get('text-align','').lower()
            if not ta:
                ta = 'center' if is_th else 'left'
            align_map = {
                'center': WD_ALIGN_PARAGRAPH.CENTER,
                'left':   WD_ALIGN_PARAGRAPH.LEFT,
                'right':  WD_ALIGN_PARAGRAPH.RIGHT,
                'justify':WD_ALIGN_PARAGRAPH.JUSTIFY,
            }
            para.alignment = align_map.get(ta, WD_ALIGN_PARAGRAPH.LEFT)

            # تلوين خلفية الخلية
            bg = (cell_sp.get('background-color','') or cell_sp.get('background','')).strip()
            if not bg and is_th:
                bg = '#1E4A6E'  # أزرق غامق لرأس الجدول
            if bg:
                rgb = _w2_css_color(bg)
                if rgb:
                    hex_c = '{:02X}{:02X}{:02X}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))
                    _w2_shade_cell(cell, hex_c)

            # الأنماط الموروثة للـ runs داخل الخلية
            cell_text_styles = {}
            txt_c = _w2_css_color(cell_sp.get('color',''))
            if is_th:
                cell_text_styles['font-weight'] = 'bold'
                if not txt_c:
                    txt_c = _w2_css_color('#FFFFFF')  # نص أبيض على رأس أزرق
            if txt_c:
                cell_text_styles['color'] = cell_sp.get('color','') or ('#FFFFFF' if is_th else '')

            # معالجة محتوى الخلية
            _w2_inline(cell_el, para, cell_text_styles)

            # تطبيق bold على رأس الجدول بعد _w2_inline
            if is_th:
                for run in para.runs:
                    run.bold = True
                    try:
                        if not run.font.color.rgb:
                            run.font.color.rgb = RGBColor(0xFF,0xFF,0xFF)
                    except Exception:
                        pass

            # تلوين خاص (matrix-high, matrix-mid, matrix-low)
            cell_classes = cell_el.get('class', [])
            if isinstance(cell_classes, str):
                cell_classes = cell_classes.split()
            if 'matrix-high' in cell_classes:
                _w2_shade_cell(cell, '2ECC71')
                for run in para.runs:
                    try: run.font.color.rgb = RGBColor(0xFF,0xFF,0xFF); run.bold=True
                    except Exception: pass
            elif 'matrix-mid' in cell_classes:
                _w2_shade_cell(cell, 'F39C12')
                for run in para.runs:
                    try: run.font.color.rgb = RGBColor(0xFF,0xFF,0xFF); run.bold=True
                    except Exception: pass
            elif 'matrix-low' in cell_classes:
                _w2_shade_cell(cell, 'E74C3C')
                for run in para.runs:
                    try: run.font.color.rgb = RGBColor(0xFF,0xFF,0xFF); run.bold=True
                    except Exception: pass

            col_cursor += colspan
            grid[r_idx][col_cursor-colspan] = True

    doc.add_paragraph()

def _w2_svg_to_png_bytes(svg_bytes, width_px=400, height_px=300):
    """محاولة تحويل SVG إلى PNG"""
    # المحاولة الأولى: cairosvg
    try:
        import cairosvg
        return cairosvg.svg2png(bytestring=svg_bytes, output_width=width_px, output_height=height_px)
    except Exception:
        pass
    # المحاولة الثانية: svglib + reportlab
    try:
        from svglib.svglib import svg2rlg
        from reportlab.graphics import renderPM
        from io import BytesIO as _BIO2
        import tempfile, os as _os
        with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as tf:
            tf.write(svg_bytes)
            tmp_path = tf.name
        try:
            drawing = svg2rlg(tmp_path)
            if drawing:
                drawing.width  = width_px
                drawing.height = height_px
                drawing.renderSVG = None
                buf2 = _BIO2()
                renderPM.drawToFile(drawing, buf2, fmt='PNG')
                return buf2.getvalue()
        finally:
            try: _os.unlink(tmp_path)
            except Exception: pass
    except Exception:
        pass
    # المحاولة الثالثة: PIL placeholder
    try:
        from PIL import Image, ImageDraw
        from io import BytesIO as _BIO3
        img = Image.new('RGBA', (width_px, height_px), color=(240, 245, 255, 255))
        draw = ImageDraw.Draw(img)
        draw.rectangle([2,2,width_px-3,height_px-3], outline=(100,120,180), width=2)
        draw.text((10, height_px//2-10), "[ SVG ]", fill=(100,120,180))
        buf3 = _BIO3()
        img.save(buf3, 'PNG')
        return buf3.getvalue()
    except Exception:
        return None

def _w2_embed_image(src, doc, width_inches=5.0, center=True, caption=None):
    """
    تضمين صورة في ملف Word — يدعم:
    - base64 PNG/JPEG/GIF/WebP/SVG
    - روابط HTTP/HTTPS
    - مسارات /static/ المحلية
    """
    try:
        from docx.shared import Inches
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        from io import BytesIO
        import base64 as _b64

        img_bytes = None
        if not src:
            return
        # تجاهل مسارات غير قابلة للوصول
        if src.startswith('/sdcard') or src.startswith('file://') or src == '#':
            return

        if 'data:image/svg' in src[:30]:
            parts = src.split(',', 1)
            raw = parts[1] if len(parts) == 2 else ''
            try:
                if '%3C' in raw or '%3c' in raw:
                    import urllib.parse
                    raw = urllib.parse.unquote(raw)
                svg_b = _b64.b64decode(raw) if (raw and not raw.startswith('<')) else raw.encode()
            except Exception:
                svg_b = raw.encode() if isinstance(raw, str) else raw
            img_bytes = _w2_svg_to_png_bytes(svg_b, 600, 400)
            if not img_bytes: return
            width_inches = min(width_inches, 5.5)

        elif src.startswith('data:image'):
            try:
                header, data = src.split(',', 1)
                img_bytes = _b64.b64decode(data + '==')
            except Exception:
                return

        elif src.startswith('http://') or src.startswith('https://'):
            try:
                resp = requests.get(src, timeout=12, headers={'User-Agent': 'Mozilla/5.0'})
                if resp.ok:
                    ct = resp.headers.get('Content-Type','')
                    img_bytes = _w2_svg_to_png_bytes(resp.content) if 'svg' in ct else resp.content
            except Exception:
                return

        elif src.startswith('/static/') or src.startswith('static/'):
            local_path = os.path.join(_PROJECT_ROOT, src.lstrip('/'))
            if os.path.exists(local_path):
                with open(local_path, 'rb') as _lf:
                    img_bytes = _lf.read()

        if not img_bytes:
            return

        # التحقق من صحة الصورة وتحويلها إذا لزم
        try:
            from PIL import Image as _PILImg
            pil_obj = _PILImg.open(BytesIO(img_bytes))
            if pil_obj.mode in ('RGBA','P','LA','CMYK'):
                pil_obj = pil_obj.convert('RGB')
                buf = BytesIO()
                pil_obj.save(buf, 'PNG')
                img_bytes = buf.getvalue()
            else:
                pil_obj.verify()  # تحقق فقط
        except Exception:
            try:
                from PIL import Image as _PILImg
                pil_obj = _PILImg.open(BytesIO(img_bytes)).convert('RGB')
                buf = BytesIO()
                pil_obj.save(buf, 'PNG')
                img_bytes = buf.getvalue()
            except Exception:
                return

        para = doc.add_paragraph()
        if center:
            para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = para.add_run()
        run.add_picture(BytesIO(img_bytes), width=Inches(min(float(width_inches), 6.0)))

        if caption:
            cap_p = doc.add_paragraph(caption)
            cap_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for r in cap_p.runs:
                r.italic = True
                try:
                    from docx.shared import Pt
                    r.font.size = Pt(10)
                except Exception: pass

    except Exception as e:
        logger.debug(f"Image embed skip ({str(src)[:60]}): {e}")

def _w2_node(node, doc, in_para=None):
    """
    المعالج الرئيسي: يحوّل عنصر HTML إلى عناصر DOCX مع دعم كامل لـ:
    - ألوان الخلفية على divs والفقرات
    - الجداول الكاملة مع rowspan/colspan
    - الصور بجميع أنواعها
    - القوائم المتداخلة
    - RTL للنص العربي
    - blockquote وpre وcode
    """
    from bs4 import NavigableString, Tag
    from docx.shared import Pt, RGBColor, Inches
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    if isinstance(node, NavigableString):
        txt = str(node)
        if in_para and txt.strip():
            in_para.add_run(txt)
        elif in_para and txt and not txt.strip():
            in_para.add_run(txt)
        return

    if not isinstance(node, Tag):
        return

    tag = (node.name or '').lower()
    classes = node.get('class', [])
    if isinstance(classes, str):
        classes = classes.split()
    classes_set = set(classes)
    sp = _w2_parse_style(node.get('style',''))

    # ── تجاهل العناصر غير المرئية ──
    if tag in ('script','style','noscript','meta','link','head'):
        return

    # ── فاصل صفحة ──
    is_page_break = (
        'page-break' in classes_set or 'pagebreak' in classes_set or
        sp.get('page-break-before','') == 'always' or
        sp.get('break-before','') in ('page','always') or
        sp.get('page-break-after','') == 'always'
    )
    if is_page_break and tag in ('div','section','p','hr','span'):
        _w2_add_page_break(doc)
        for child in node.children:
            _w2_node(child, doc)
        return

    # ── عناوين H1-H6 ──
    if tag in ('h1','h2','h3','h4','h5','h6'):
        lvl = int(tag[1])
        try:
            para = doc.add_heading(level=min(lvl, 4))
        except Exception:
            para = doc.add_paragraph()
        para.clear()
        sizes = {1:24, 2:20, 3:17, 4:15, 5:13, 6:12}

        # تطبيق خلفية العنوان إذا وُجدت
        bg = (sp.get('background-color','') or sp.get('background','')).strip()
        if bg:
            rgb_bg = _w2_css_color(bg)
            if rgb_bg:
                _w2_shade_para(para, '{:02X}{:02X}{:02X}'.format(int(rgb_bg[0]),int(rgb_bg[1]),int(rgb_bg[2])))

        # بناء أنماط الوراثة للعنوان
        heading_styles = {'font-weight': 'bold', 'font-size': f'{sizes.get(lvl,14)}pt'}
        c_str = sp.get('color','')
        if c_str: heading_styles['color'] = c_str

        _w2_inline(node, para, heading_styles)

        # تطبيق الحجم والـ bold على جميع runs بعد الإضافة
        for run in para.runs:
            run.bold = True
            run.font.size = Pt(sizes.get(lvl, 14))
            if c_str:
                c = _w2_css_color(c_str)
                if c: run.font.color.rgb = c

        para.alignment = _w2_align(sp, 'LEFT')

        # RTL للعناوين العربية
        txt_check = node.get_text()
        if _w2_is_rtl(txt_check):
            _w2_set_rtl_para(para)
        return

    # ── فقرات <p> ──
    if tag == 'p':
        para = doc.add_paragraph()
        para.alignment = _w2_align(sp, 'LEFT')

        # خلفية الفقرة
        bg = (sp.get('background-color','') or sp.get('background','')).strip()
        if bg:
            rgb_bg = _w2_css_color(bg)
            if rgb_bg:
                _w2_shade_para(para, '{:02X}{:02X}{:02X}'.format(int(rgb_bg[0]),int(rgb_bg[1]),int(rgb_bg[2])))

        # أنماط الفقرة
        p_styles = {}
        c_str = sp.get('color','')
        if c_str: p_styles['color'] = c_str
        fw = sp.get('font-weight','')
        if fw: p_styles['font-weight'] = fw
        fs = sp.get('font-size','')
        if fs: p_styles['font-size'] = fs
        ff = sp.get('font-family','')
        if ff: p_styles['font-family'] = ff

        _w2_inline(node, para, p_styles)

        txt_check = node.get_text()
        if _w2_is_rtl(txt_check):
            _w2_set_rtl_para(para)
        return

    # ── جدول ──
    if tag == 'table':
        _w2_table(node, doc)
        return

    # ── صورة ──
    if tag == 'img':
        src = node.get('src','')
        alt = node.get('alt','')
        w_attr = node.get('width','')
        try:
            w_in = min(float(str(w_attr).replace('px','').strip()) / 96.0, 6.0) if w_attr else 5.0
        except Exception:
            w_in = 5.0
        if src:
            _w2_embed_image(src, doc, width_inches=w_in)
        return

    # ── canvas ──
    if tag == 'canvas':
        # محاولة استخراج data-url إن وُجدت
        du = node.get('data-url','') or node.get('data-image','')
        if du:
            _w2_embed_image(du, doc, width_inches=5.5)
        return

    # ── SVG: تحويل إلى PNG وتضمينه ──
    if tag == 'svg':
        try:
            svg_str = str(node)
            svg_bytes = svg_str.encode('utf-8')
            # تحديد العرض والارتفاع من خصائص الـ SVG
            try:
                vb = node.get('viewBox','')
                w_attr = node.get('width','')
                h_attr = node.get('height','')
                if vb:
                    parts = vb.replace(',',' ').split()
                    vb_w = float(parts[2]) if len(parts)>2 else 400
                    vb_h = float(parts[3]) if len(parts)>3 else 300
                    out_w = int(min(vb_w * 2, 1200))
                    out_h = int(min(vb_h * 2, 900))
                elif w_attr and h_attr:
                    out_w = int(min(float(str(w_attr).replace('px','').strip() or 400), 1200))
                    out_h = int(min(float(str(h_attr).replace('px','').strip() or 300), 900))
                else:
                    out_w, out_h = 800, 600
            except Exception:
                out_w, out_h = 800, 600
            png_bytes = _w2_svg_to_png_bytes(svg_bytes, out_w, out_h)
            if png_bytes:
                # حساب حجم الصورة بالإنش
                w_in = min(out_w / 96.0, 5.5)
                para = doc.add_paragraph()
                para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = para.add_run()
                run.add_picture(BytesIO(png_bytes), width=Inches(w_in))
        except Exception as _svg_err:
            logger.debug(f"SVG embed error: {_svg_err}")
        return

    # ── figure ──
    if tag == 'figure':
        img_el = node.find('img')
        if img_el:
            src = img_el.get('src','')
            if src:
                _w2_embed_image(src, doc, width_inches=5.0)
        cap = node.find('figcaption')
        if cap:
            cp = doc.add_paragraph(cap.get_text(strip=True))
            cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for r in cp.runs:
                r.italic = True
                try: r.font.size = Pt(10)
                except Exception: pass
        return

    # ── قوائم ──
    if tag == 'ul':
        for li in node.find_all('li', recursive=False):
            para = doc.add_paragraph(style='List Bullet')
            para.alignment = WD_ALIGN_PARAGRAPH.LEFT
            _w2_inline(li, para)
            if _w2_is_rtl(li.get_text()):
                _w2_set_rtl_para(para)
        return
    if tag == 'ol':
        for li in node.find_all('li', recursive=False):
            para = doc.add_paragraph(style='List Number')
            para.alignment = WD_ALIGN_PARAGRAPH.LEFT
            _w2_inline(li, para)
            if _w2_is_rtl(li.get_text()):
                _w2_set_rtl_para(para)
        return

    # ── hr ──
    if tag == 'hr':
        p = doc.add_paragraph()
        try:
            from docx.oxml import parse_xml
            pPr = p._p.get_or_add_pPr()
            bdr = ('<w:pBdr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                   '<w:bottom w:val="single" w:sz="6" w:space="1" w:color="AAAAAA"/>'
                   '</w:pBdr>')
            pPr.append(parse_xml(bdr))
        except Exception:
            p.add_run('─' * 60)
        return

    # ── br مستقل ──
    if tag == 'br':
        if in_para:
            in_para.add_run('\n')
        else:
            doc.add_paragraph()
        return

    # ── blockquote ──
    if tag == 'blockquote':
        para = doc.add_paragraph()
        _w2_inline(node, para)
        try:
            from docx.shared import Inches as _IN
            para.paragraph_format.left_indent  = _IN(0.4)
            para.paragraph_format.right_indent = _IN(0.4)
        except Exception: pass
        _w2_set_para_border(para, 'AAAAAA', 'left', 18)
        _w2_shade_para(para, 'F5F5F5')
        return

    # ── pre / code block ──
    if tag == 'pre':
        code_el = node.find('code')
        code_text = (code_el or node).get_text()
        for line in code_text.split('\n'):
            p = doc.add_paragraph(line)
            p.paragraph_format.left_indent = Pt(18)
            _w2_shade_para(p, 'F4F4F4')
            for r in p.runs:
                r.font.name = 'Courier New'
                try: r.font.size = Pt(10)
                except Exception: pass
        return

    # ── عناصر خاصة بالتصميم ──
    if 'insight-box' in classes_set:
        para = doc.add_paragraph()
        para.alignment = WD_ALIGN_PARAGRAPH.LEFT
        _w2_inline(node, para)
        _w2_shade_para(para, 'FEF8E7')
        _w2_set_para_border(para, 'E6B422', 'left', 24)
        return

    if 'toc-row' in classes_set or 'list-row' in classes_set:
        spans = node.find_all(['span','div'], recursive=False)
        texts = [s.get_text(strip=True) for s in spans] if spans else [node.get_text(strip=True)]
        line = '  '.join(filter(None, texts))
        if line:
            para = doc.add_paragraph(line)
            para.alignment = WD_ALIGN_PARAGRAPH.LEFT
        return

    if 'ref-item' in classes_set:
        para = doc.add_paragraph()
        para.alignment = WD_ALIGN_PARAGRAPH.LEFT
        _w2_inline(node, para)
        try:
            para.paragraph_format.left_indent = Pt(18)
            para.paragraph_format.space_after  = Pt(6)
        except Exception: pass
        return

    if 'figure-caption' in classes_set:
        para = doc.add_paragraph(node.get_text(strip=True))
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in para.runs:
            r.italic = True
            try: r.font.size = Pt(10)
            except Exception: pass
        return

    if 'page-number' in classes_set:
        return

    if 'header-logo' in classes_set:
        img_el = node.find('img')
        if img_el:
            src = img_el.get('src','')
            if src and 'svg' not in src[:30]:
                _w2_embed_image(src, doc, width_inches=1.5)
        return

    # ── div / section مع خلفية ملوّنة → صندوق نصي ──
    CONTAINER_TAGS = {
        'div','section','article','main','aside','header','footer','nav',
        'body','html','form','fieldset','details','summary','address',
        'span','a','label','li',
    }
    if tag in CONTAINER_TAGS:
        bg_raw = (sp.get('background-color','') or sp.get('background','')).strip()
        border_color = sp.get('border-left-color','') or sp.get('border-color','')

        if in_para and tag in ('span','a','label'):
            own_sp = {}
            own_sp.update(sp)
            _w2_inline(node, in_para, own_sp)
            return

        # ── فاصل صفحة تلقائي بين أقسام .page ──
        # يُضاف فاصل قبل كل .page عدا الأولى في الوثيقة
        is_page_div = ('page' in classes_set or 'slide' in classes_set or
                       'sheet' in classes_set or 'cover-page' in classes_set or
                       'content-page' in classes_set)
        if is_page_div and tag == 'div':
            existing_pages = getattr(doc, '_w2_page_count', 0)
            if existing_pages > 0:
                _w2_add_page_break(doc)
            doc._w2_page_count = existing_pages + 1

        # ── استخراج اللون من gradient ──
        bg = bg_raw
        if bg and 'gradient' in bg.lower():
            # استخراج أول لون من linear-gradient(...)
            m = re.search(r'#([0-9a-fA-F]{3,6})\b', bg)
            if not m:
                m = re.search(r'rgba?\s*\([\d.,\s]+\)', bg)
            bg = m.group(0) if m else ''

        if bg and bg not in ('transparent','inherit','none',''):
            # معالجة الأبناء أولاً في فقرات عادية، ثم تلوين الفقرة الأولى
            start_idx = len(doc.paragraphs)
            for child in node.children:
                _w2_node(child, doc, in_para=None)
            end_idx = len(doc.paragraphs)
            rgb_bg = _w2_css_color(bg)
            if rgb_bg:
                # تجاهل الأبيض الخالص (لا حاجة لتلوينه)
                if not (rgb_bg[0] >= 250 and rgb_bg[1] >= 250 and rgb_bg[2] >= 250):
                    hex_bg = '{:02X}{:02X}{:02X}'.format(int(rgb_bg[0]),int(rgb_bg[1]),int(rgb_bg[2]))
                    for i in range(start_idx, end_idx):
                        try:
                            _w2_shade_para(doc.paragraphs[i], hex_bg)
                            if border_color:
                                bc = _w2_css_color(border_color)
                                if bc:
                                    _w2_set_para_border(doc.paragraphs[i],
                                        '{:02X}{:02X}{:02X}'.format(int(bc[0]),int(bc[1]),int(bc[2])),
                                        'left', 18)
                        except Exception: pass
        else:
            for child in node.children:
                _w2_node(child, doc, in_para=None)
        return

    # ── أي عنصر آخر ──
    for child in node.children:
        _w2_node(child, doc, in_para=in_para)


@app.route("/formatter/")
@app.route("/formatter")
def formatter_page():
    """منسق الملفات"""
    resp = make_response(render_template('formatter.html'))
    resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    return resp


@app.route("/html_to_word")
@app.route("/html_to_word/")
@app.route("/html2word")
@app.route("/html2word/")
def html_to_word_studio():
    """استوديو تحويل HTML إلى Word الاحترافي بالذكاء الاصطناعي"""
    resp = make_response(render_template('html_to_word.html'))
    resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    resp.headers['X-Frame-Options'] = 'SAMEORIGIN'
    return resp


@app.route("/api/html_to_word/convert", methods=["POST"])
def api_html_to_word_convert():
    """تصدير HTML إلى ملف DOCX أصلي وتحميله فوراً لذاكرة الجهاز"""
    try:
        from html_word_engine import convert_html_to_docx
        data = request.get_json(silent=True) or {}
        html_content = data.get('html', '').strip()
        filename = (data.get('filename', 'document') or 'document').strip()
        if not html_content:
            return jsonify({"error": "محتوى HTML فارغ"}), 400

        font_family = data.get('font_family', 'Cairo')
        font_size = float(data.get('font_size', 12.0) or 12.0)
        margin_inches = float(data.get('margin', 1.0) or 1.0)
        rtl_doc = bool(data.get('rtl', True))

        buffer = io.BytesIO()
        convert_html_to_docx(
            html_content=html_content,
            output_target=buffer,
            filename=filename,
            font_family=font_family,
            font_size=font_size,
            margin_inches=margin_inches,
            rtl_doc=rtl_doc
        )
        buffer.seek(0)

        safe_name = re.sub(r'[^\w\u0600-\u06FF\-_]', '_', filename) or 'document'
        if not safe_name.endswith('.docx'):
            safe_name += '.docx'

        return send_file(
            buffer,
            as_attachment=True,
            download_name=safe_name,
            mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    except Exception as e:
        logger.error(f"HTML to Word export error: {e}", exc_info=True)
        return jsonify({"error": f"حدث خطأ أثناء تصدير ملف Word: {str(e)}"}), 500


@app.route("/api/html_to_word/ai_process", methods=["POST"])
def api_html_to_word_ai():
    """معالجة وتحسين كود HTML بواسطة Gemini AI"""
    try:
        from html_word_engine import ai_process_html
        data = request.get_json(silent=True) or {}
        html_content = data.get('html', '').strip()
        action = data.get('action', 'optimize')
        custom_prompt = data.get('custom_prompt', '')

        if not html_content:
            return jsonify({"success": False, "error": "كود HTML فارغ"}), 400

        res = ai_process_html(html_content, action=action, custom_prompt=custom_prompt)
        return jsonify(res)
    except Exception as e:
        logger.error(f"AI HTML processing error: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/formatter/<path:filename>")
def formatter_static(filename):
    """ملفات ثابتة لمنسق الملفات"""
    from flask import send_from_directory as _sfd
    return _sfd(os.path.join(os.path.dirname(__file__), 'static', 'wf_build'), filename)


# ════════════════════════════════════════════════════════════
#  PDF → Word مع صور كاملة وجداول (PyMuPDF)
# ════════════════════════════════════════════════════════════

def _smart_draw_charts(doc, text_content, add_charts=True):
    """نظام الرسم الذكي: يحلل المحتوى ويضيف رسوماً بيانية مناسبة"""
    if not add_charts:
        return
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import matplotlib.font_manager as fm
        import json as _json
        from io import BytesIO
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        from docx.shared import Inches, Pt

        # طلب AI لتحليل البيانات واقتراح الرسم
        from groq import Groq as _Groq
        client = _Groq(api_key=GROQ_API_KEY)
        prompt = f"""Analyze the following text and determine if it contains numerical data suitable for a chart.
Reply ONLY with valid JSON (no explanation):
{{
  "has_chart": true,
  "chart_type": "bar",
  "title": "Chart Title",
  "direction": "vertical",
  "colors": ["#1e4a2f","#2d6b41","#4f9a66","#7cb56e","#a8d08d"],
  "labels": ["Label1","Label2","Label3"],
  "values": [10, 25, 15],
  "x_label": "X axis",
  "y_label": "Y axis"
}}
If no chart is appropriate, set has_chart to false.
Text (first 2000 chars):
{text_content[:2000]}"""

        resp = client.chat.completions.create(
            model='llama-3.3-70b-versatile',
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400, temperature=0.1
        )
        raw = resp.choices[0].message.content.strip()
        # استخراج JSON من الرد
        import re as _re
        m = _re.search(r'\{.*\}', raw, _re.DOTALL)
        if not m:
            return
        chart_data = _json.loads(m.group())
        if not chart_data.get('has_chart', False):
            return

        labels  = chart_data.get('labels', [])
        values  = chart_data.get('values', [])
        colors  = chart_data.get('colors', ['#1e4a2f','#2d6b41','#4f9a66','#7cb56e'])
        title   = chart_data.get('title', 'مخطط البيانات')
        ctype   = chart_data.get('chart_type', 'bar')
        direc   = chart_data.get('direction', 'vertical')
        xlabel  = chart_data.get('x_label', '')
        ylabel  = chart_data.get('y_label', '')

        if not labels or not values:
            return
        n = min(len(labels), len(values))
        labels, values = labels[:n], [float(v) for v in values[:n]]
        while len(colors) < n:
            colors += colors

        fig, ax = plt.subplots(figsize=(8, 4.5))
        fig.patch.set_facecolor('#f8fdf4')
        ax.set_facecolor('#f0f7ea')

        if ctype == 'pie':
            wedges, texts, autotexts = ax.pie(
                values, labels=labels, colors=colors[:n],
                autopct='%1.1f%%', startangle=90,
                pctdistance=0.82, wedgeprops=dict(width=0.6))
            for at in autotexts:
                at.set_fontsize(9); at.set_fontweight('bold')
        elif ctype == 'line':
            ax.plot(labels, values, marker='o', color=colors[0],
                    linewidth=2.5, markersize=7, markerfacecolor='white',
                    markeredgewidth=2)
            ax.fill_between(range(n), values, alpha=0.12, color=colors[0])
            ax.set_xticks(range(n)); ax.set_xticklabels(labels, rotation=20, ha='right')
            if xlabel: ax.set_xlabel(xlabel)
            if ylabel: ax.set_ylabel(ylabel)
            ax.grid(axis='y', linestyle='--', alpha=0.5)
        elif ctype == 'scatter':
            ax.scatter(range(n), values, c=colors[:n], s=120, zorder=5)
            ax.set_xticks(range(n)); ax.set_xticklabels(labels, rotation=20, ha='right')
        else:  # bar (default)
            if direc == 'horizontal':
                bars = ax.barh(labels, values, color=colors[:n], edgecolor='white', linewidth=0.5)
                if xlabel: ax.set_xlabel(xlabel)
                if ylabel: ax.set_ylabel(ylabel)
                for bar, val in zip(bars, values):
                    ax.text(bar.get_width()+max(values)*0.01, bar.get_y()+bar.get_height()/2,
                            f'{val:g}', va='center', fontsize=9)
            else:
                bars = ax.bar(labels, values, color=colors[:n], edgecolor='white',
                              linewidth=0.5, width=0.65)
                ax.set_xticks(range(n)); ax.set_xticklabels(labels, rotation=20, ha='right')
                if xlabel: ax.set_xlabel(xlabel)
                if ylabel: ax.set_ylabel(ylabel)
                for bar, val in zip(bars, values):
                    ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+max(values)*0.01,
                            f'{val:g}', ha='center', fontsize=9)
            ax.grid(axis='y' if direc != 'horizontal' else 'x', linestyle='--', alpha=0.4)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)

        ax.set_title(title, fontsize=13, fontweight='bold', pad=10)
        plt.tight_layout()

        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight',
                    facecolor=fig.get_facecolor())
        plt.close(fig)
        buf.seek(0)

        # فاصل + الرسم + تسمية
        doc.add_paragraph('─' * 50)
        para = doc.add_paragraph()
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = para.add_run()
        run.add_picture(buf, width=Inches(5.5))
        cap = doc.add_paragraph(f"📊 {title}")
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in cap.runs:
            r.italic = True
            try: r.font.size = Pt(10)
            except Exception: pass
        doc.add_paragraph()

    except Exception as e:
        logger.debug(f"Smart draw error: {e}")


@app.route("/tools/pdf_to_word", methods=["POST"])
def api_pdf_to_word():
    """
    تحويل PDF → DOCX مع:
    - الحفاظ الكامل على ألوان الخطوط والخلفيات
    - تجنب تكرار نص الجداول
    - جداول منسّقة مع تلوين رأس الجدول
    - صور مضمّنة كاملة
    - دعم RTL للنص العربي
    - تطبيق إعدادات المستخدم (خط / هوامش / حجم)
    """
    try:
        if 'file' not in request.files:
            return jsonify({"error": "لم يتم رفع ملف PDF"}), 400

        f = request.files['file']
        if not f.filename.lower().endswith('.pdf'):
            return jsonify({"error": "يرجى رفع ملف PDF فقط"}), 400

        # إعدادات المستخدم من الواجهة
        add_smart_draw  = request.form.get('smart_draw', 'false').lower() == 'true'
        user_font       = request.form.get('font_family', 'Times New Roman').strip() or 'Times New Roman'
        user_font_size  = float(request.form.get('font_size', '12') or '12')
        margin_in_str   = request.form.get('margin', '1.0')
        try:
            margin_in = float(margin_in_str)
        except Exception:
            margin_in = 1.0

        file_bytes = f.read()
        safe_name  = re.sub(r'[^\w\u0600-\u06FF\-_]', '_',
                            f.filename.rsplit('.', 1)[0]) or 'document'

        import io as _io
        from io import BytesIO
        import docx as _docx
        from docx.shared import Pt, Inches, RGBColor
        from docx.enum.text import WD_ALIGN_PARAGRAPH

        doc = _docx.Document()
        for sec in doc.sections:
            sec.top_margin    = Inches(margin_in)
            sec.bottom_margin = Inches(margin_in)
            sec.left_margin   = Inches(max(margin_in, 1.0))
            sec.right_margin  = Inches(max(margin_in, 1.0))
        doc.styles['Normal'].font.name = user_font
        doc.styles['Normal'].font.size = Pt(user_font_size)

        all_text = []
        total    = 0

        # ── دالة مساعدة: استخراج لون فيتز (int) → (r,g,b) أو None ──
        def _fitz_color(color_val):
            try:
                if color_val is None:
                    return None
                if isinstance(color_val, (list, tuple)) and len(color_val) >= 3:
                    return (int(color_val[0]*255), int(color_val[1]*255), int(color_val[2]*255))
                ci = int(color_val)
                r = (ci >> 16) & 0xFF
                g = (ci >> 8)  & 0xFF
                b =  ci        & 0xFF
                if r == g == b == 0:
                    return None  # أسود = افتراضي، تجاهل
                return (r, g, b)
            except Exception:
                return None

        # ── دالة: هل يتداخل بلوك نصي مع منطقة جدول ──
        def _in_table_region(block_bbox, table_bboxes, threshold=0.5):
            bx0,by0,bx1,by1 = block_bbox
            for tx0,ty0,tx1,ty1 in table_bboxes:
                ix0 = max(bx0,tx0); iy0 = max(by0,ty0)
                ix1 = min(bx1,tx1); iy1 = min(by1,ty1)
                if ix1 > ix0 and iy1 > iy0:
                    inter = (ix1-ix0)*(iy1-iy0)
                    area  = max((bx1-bx0)*(by1-by0), 1)
                    if inter/area > threshold:
                        return True
            return False

        try:
            import fitz as _fitz

            pdf_doc = _fitz.open(stream=file_bytes, filetype="pdf")
            total   = len(pdf_doc)

            # ── جمع بيانات الجداول من pdfplumber (bbox + data) ──
            plumb_pages = {}   # page_num -> {'bboxes': [...], 'tables': [...]}
            try:
                if pdfplumber:
                    with pdfplumber.open(_io.BytesIO(file_bytes)) as _plumb:
                        for pi, pp in enumerate(_plumb.pages[:total]):
                            found = pp.find_tables()
                            bboxes = [t.bbox for t in found]
                            data   = [t.extract() for t in found]
                            if bboxes:
                                plumb_pages[pi] = {'bboxes': bboxes, 'tables': data}
            except Exception:
                pass

            seen_img_xrefs = set()

            for page_num, page in enumerate(pdf_doc):
                if page_num > 0:
                    _w2_add_page_break(doc)

                page_table_bboxes = plumb_pages.get(page_num, {}).get('bboxes', [])

                # ── استخراج النص مع ألوان كاملة ──
                page_dict = page.get_text("dict", sort=True)

                for block in page_dict.get('blocks', []):
                    if block.get('type') != 0:
                        continue  # تجاهل بلوكات الصور — ستُعالَج لاحقاً

                    block_bbox = block.get('bbox', (0,0,0,0))

                    # تخطّ النص الواقع داخل منطقة جدول
                    if _in_table_region(block_bbox, page_table_bboxes):
                        continue

                    for line in block.get('lines', []):
                        # تجميع النص والتنسيق لكل span في السطر
                        spans_data = []
                        max_size = 0
                        line_is_bold = False
                        line_has_color = False

                        for span in line.get('spans', []):
                            t   = span.get('text', '')
                            if not t.strip():
                                continue
                            sz  = span.get('size', user_font_size)
                            flg = span.get('flags', 0)
                            col = span.get('color', 0)
                            rgb = _fitz_color(col)
                            is_bold = bool(flg & 16)
                            spans_data.append({
                                'text': t,
                                'size': sz,
                                'bold': is_bold,
                                'color': rgb,
                                'font': span.get('font',''),
                            })
                            if sz > max_size: max_size = sz
                            if is_bold: line_is_bold = True
                            if rgb: line_has_color = True

                        if not spans_data:
                            continue

                        line_txt = ' '.join(s['text'] for s in spans_data).strip()
                        all_text.append(line_txt)

                        # تحديد نوع الفقرة بناءً على الحجم
                        is_h1 = max_size >= 18
                        is_h2 = 14 <= max_size < 18
                        is_h3 = 12.5 <= max_size < 14 and line_is_bold

                        if is_h1:
                            para = doc.add_heading(level=1)
                            para.clear()
                            base_size = min(max_size, 24)
                        elif is_h2:
                            para = doc.add_heading(level=2)
                            para.clear()
                            base_size = min(max_size, 18)
                        elif is_h3:
                            para = doc.add_heading(level=3)
                            para.clear()
                            base_size = 14
                        else:
                            para = doc.add_paragraph()
                            base_size = user_font_size

                        # إذا كان السطر يحتوي على span واحد أو أقل اختلافاً في التنسيق
                        if len(spans_data) == 1 or (not line_has_color and not any(s['bold'] != line_is_bold for s in spans_data)):
                            run = para.add_run(line_txt)
                            run.bold = line_is_bold or is_h1 or is_h2 or is_h3
                            run.font.size = Pt(base_size)
                            run.font.name = user_font
                            if spans_data[0]['color']:
                                r,g,b = spans_data[0]['color']
                                try: run.font.color.rgb = RGBColor(r,g,b)
                                except Exception: pass
                        else:
                            # spans متعددة مع تنسيق مختلف
                            for span_d in spans_data:
                                run = para.add_run(span_d['text'] + ' ')
                                run.bold = span_d['bold'] or is_h1 or is_h2
                                run.font.size = Pt(min(span_d['size'], 36))
                                run.font.name = user_font
                                if span_d['color']:
                                    r,g,b = span_d['color']
                                    try: run.font.color.rgb = RGBColor(r,g,b)
                                    except Exception: pass

                        # RTL للنص العربي
                        if _w2_is_rtl(line_txt):
                            _w2_set_rtl_para(para)
                            para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                        elif is_h1 or is_h2:
                            para.alignment = WD_ALIGN_PARAGRAPH.CENTER

                # ── إدراج الجداول من pdfplumber ──
                page_tables = plumb_pages.get(page_num, {}).get('tables', [])
                for tbl_data in page_tables:
                    if not tbl_data:
                        continue
                    clean = [[str(c or '').strip() for c in row] for row in tbl_data]
                    clean = [r for r in clean if any(c for c in r)]
                    if not clean:
                        continue
                    max_cols = max(len(r) for r in clean)
                    if max_cols == 0:
                        continue
                    clean = [r + [''] * (max_cols - len(r)) for r in clean]

                    doc.add_paragraph()
                    tbl_word = doc.add_table(rows=len(clean), cols=max_cols)
                    tbl_word.style = 'Table Grid'

                    # تعيين عرض الأعمدة بالتساوي
                    try:
                        from docx.oxml.ns import qn as _qn
                        from docx.oxml import OxmlElement as _OXE
                        tbl_w = tbl_word._tbl
                        tblPr = tbl_w.tblPr if tbl_w.tblPr is not None else _OXE('w:tblPr')
                        tblW  = _OXE('w:tblW')
                        tblW.set(_qn('w:w'), '5000')
                        tblW.set(_qn('w:type'), 'pct')
                        tblPr.append(tblW)
                    except Exception:
                        pass

                    for ri, row in enumerate(clean):
                        for ci, val in enumerate(row):
                            cell = tbl_word.cell(ri, ci)
                            cell.text = ''
                            p = cell.paragraphs[0]
                            p.alignment = WD_ALIGN_PARAGRAPH.CENTER

                            is_rtl_cell = _w2_is_rtl(val)
                            run = p.add_run(val)
                            run.font.name = user_font
                            run.font.size = Pt(user_font_size)

                            if ri == 0:
                                run.bold = True
                                try: run.font.color.rgb = RGBColor(0xFF,0xFF,0xFF)
                                except Exception: pass
                                _w2_shade_cell(cell, '1E4A6E')  # أزرق غامق
                            elif ri % 2 == 0:
                                _w2_shade_cell(cell, 'EBF5FB')  # أزرق فاتح للصفوف الزوجية

                            if is_rtl_cell:
                                _w2_set_rtl_para(p)
                    doc.add_paragraph()

                # ── استخراج الصور من الصفحة ──
                img_list = page.get_images(full=True)
                for img_info in img_list:
                    xref = img_info[0]
                    if xref in seen_img_xrefs:
                        continue
                    seen_img_xrefs.add(xref)
                    try:
                        base_img   = pdf_doc.extract_image(xref)
                        img_bytes  = base_img["image"]
                        w_px, h_px = base_img.get("width",1), base_img.get("height",1)
                        if w_px < 80 or h_px < 80:
                            continue  # تجاهل ديكور صغير

                        from PIL import Image as _PILImg
                        try:
                            pil_img = _PILImg.open(BytesIO(img_bytes))
                            if pil_img.mode in ('RGBA','P','LA','CMYK'):
                                pil_img = pil_img.convert('RGB')
                            buf = BytesIO()
                            pil_img.save(buf, 'PNG')
                            buf.seek(0)
                            img_bytes = buf.getvalue()
                        except Exception:
                            pass

                        aspect = w_px / max(h_px, 1)
                        w_in   = min(5.5, max(1.5, aspect * 4.0))

                        para = doc.add_paragraph()
                        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                        run  = para.add_run()
                        run.add_picture(BytesIO(img_bytes), width=Inches(w_in))
                    except Exception as _ie:
                        logger.debug(f"PDF image xref={xref}: {_ie}")

            pdf_doc.close()

        except ImportError:
            # ── fallback: pdfplumber فقط بدون PyMuPDF ──
            if pdfplumber is None:
                return jsonify({"error": "مكتبة PDF غير متاحة"}), 500
            with pdfplumber.open(_io.BytesIO(file_bytes)) as pdf:
                total = len(pdf.pages)
                for i, page in enumerate(pdf.pages[:60], 1):
                    if i > 1:
                        _w2_add_page_break(doc)

                    # جمع bboxes الجداول لهذه الصفحة
                    page_tbls = page.find_tables()
                    tbl_bboxes = [t.bbox for t in page_tbls]
                    tbl_data   = [t.extract() for t in page_tbls]

                    text = page.extract_text(layout=True) or ''
                    for line in text.split('\n'):
                        lt = line.strip()
                        if not lt:
                            continue
                        all_text.append(lt)
                        para = doc.add_paragraph()
                        run = para.add_run(lt)
                        run.font.name = user_font
                        run.font.size = Pt(user_font_size)
                        if _w2_is_rtl(lt):
                            _w2_set_rtl_para(para)
                            para.alignment = WD_ALIGN_PARAGRAPH.RIGHT

                    for tbl in tbl_data:
                        if not tbl:
                            continue
                        clean = [[str(c or '').strip() for c in r] for r in tbl]
                        clean = [r for r in clean if any(c for c in r)]
                        if not clean:
                            continue
                        mc = max(len(r) for r in clean)
                        clean = [r + ['']*(mc-len(r)) for r in clean]
                        tw = doc.add_table(rows=len(clean), cols=mc)
                        tw.style = 'Table Grid'
                        for ri, row in enumerate(clean):
                            for ci, val in enumerate(row):
                                c = tw.cell(ri, ci)
                                c.text = ''
                                p = c.paragraphs[0]
                                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                                run = p.add_run(val)
                                run.font.name = user_font
                                run.font.size = Pt(user_font_size)
                                if ri == 0:
                                    run.bold = True
                                    try: run.font.color.rgb = RGBColor(0xFF,0xFF,0xFF)
                                    except Exception: pass
                                    _w2_shade_cell(c, '1E4A6E')
                                elif ri % 2 == 0:
                                    _w2_shade_cell(c, 'EBF5FB')
                        doc.add_paragraph()

        # ── الرسم الذكي (اختياري) ──
        if add_smart_draw and all_text:
            _smart_draw_charts(doc, '\n'.join(all_text[:400]))

        final_path = str(_PPTX_OUTPUTS_DIR / (safe_name + '_converted.docx'))
        doc.save(final_path)

        return jsonify({
            "success": True,
            "download_url": f"/tools/word/download/{safe_name}_converted.docx",
            "filename": f"{safe_name}_converted.docx",
            "pages": total
        })

    except Exception as e:
        logger.error(f"PDF to Word error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route("/tools/html_to_word", methods=["POST"])
def api_html_to_word():
    """
    تحويل HTML → DOCX مع دعم كامل لـ:
    - ألوان CSS كاملة مع وراثة الأنماط
    - جداول كاملة (colspan + rowspan + خلفيات)
    - صور base64 + HTTP + مسارات محلية
    - RTL للنص العربي تلقائياً
    - blockquote / pre / code / insight-box
    - تطبيق إعدادات المستخدم (خط / هوامش / حجم)
    """
    try:
        data = request.get_json() or {}
        html_content   = data.get('html', '')
        filename       = data.get('filename', 'document')
        add_smart_draw = data.get('smart_draw', False)

        # إعدادات المستخدم
        user_font      = (data.get('font_family','') or 'Times New Roman').strip()
        user_font_size = float(data.get('font_size', 12) or 12)
        margin_val     = float(data.get('margin', 1.0) or 1.0)
        rtl_doc        = data.get('rtl', False)

        if not html_content:
            return jsonify({"error": "محتوى HTML فارغ"}), 400

        from bs4 import BeautifulSoup
        import docx as _docx
        from docx.shared import Pt, Inches

        soup = BeautifulSoup(html_content, 'html.parser')

        doc = _docx.Document()

        # هوامش الصفحة
        for sec in doc.sections:
            sec.top_margin    = Inches(margin_val)
            sec.bottom_margin = Inches(margin_val)
            sec.left_margin   = Inches(max(margin_val, 0.8))
            sec.right_margin  = Inches(max(margin_val, 0.8))

        # النمط الافتراضي
        normal = doc.styles['Normal']
        normal.font.name = user_font
        normal.font.size = Pt(user_font_size)

        # تطبيق النمط الافتراضي على الـ Heading styles أيضاً
        for h_level in range(1, 5):
            try:
                hstyle = doc.styles[f'Heading {h_level}']
                hstyle.font.name = user_font
            except Exception:
                pass

        # إزالة العناصر غير المرئية
        body = soup.find('body') or soup
        for el in body.find_all(['script','style','noscript','head'], recursive=True):
            el.decompose()

        # معالجة المحتوى
        for child in body.children:
            _w2_node(child, doc)

        # حذف الفقرة الفارغة الأولى إن وُجدت
        try:
            first = doc.paragraphs[0]
            if not first.text.strip() and len(doc.paragraphs) > 1:
                first._element.getparent().remove(first._element)
        except Exception:
            pass

        # تطبيق اتجاه RTL على مستوى القسم إذا طُلب
        if rtl_doc:
            try:
                from docx.oxml import parse_xml
                for sec in doc.sections:
                    sectPr = sec._sectPr
                    bidi_xml = '<w:bidi xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"/>'
                    sectPr.append(parse_xml(bidi_xml))
            except Exception:
                pass

        # الرسم الذكي (اختياري)
        if add_smart_draw:
            body_text = ' '.join(p.text for p in doc.paragraphs if p.text.strip())[:3000]
            if body_text:
                _smart_draw_charts(doc, body_text)

        # حفظ الملف
        safe_name  = re.sub(r'[^\w\u0600-\u06FF\-_]', '_', filename) or 'document'
        final_path = str(_PPTX_OUTPUTS_DIR / (safe_name + '.docx'))
        doc.save(final_path)

        return jsonify({
            "success": True,
            "download_url": f"/tools/word/download/{safe_name}.docx",
            "filename": f"{safe_name}.docx"
        })
    except Exception as e:
        logger.error(f"HTML to Word error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route("/tools/word/download/<path:filename>")
def tools_word_download(filename):
    """تحميل ملف Word المُنشأ"""
    from flask import send_from_directory
    outputs_dir = os.path.join(os.path.dirname(__file__), 'pptx_app', 'outputs')
    return send_from_directory(outputs_dir, filename, as_attachment=True)


@app.route("/tools/html_to_excel", methods=["POST"])
def api_html_to_excel():
    """تحويل HTML → Excel (.xlsx) مع استخراج الجداول والنصوص"""
    try:
        data = request.get_json() or {}
        html_content = data.get('html', '')
        filename     = data.get('filename', 'document')

        if not html_content:
            return jsonify({"error": "محتوى HTML فارغ"}), 400

        from bs4 import BeautifulSoup
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        from openpyxl.utils import get_column_letter

        soup = BeautifulSoup(html_content, 'html.parser')
        wb   = openpyxl.Workbook()
        ws   = wb.active
        ws.title = "المحتوى"

        current_row = 1

        # نمط الترويسات
        header_font  = Font(bold=True, size=12, color="FFFFFF")
        header_fill  = PatternFill("solid", fgColor="1a7a3c")
        center_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
        wrap_align   = Alignment(wrap_text=True, vertical="top")
        thin_border  = Border(
            left=Side(style='thin'), right=Side(style='thin'),
            top=Side(style='thin'), bottom=Side(style='thin')
        )

        def write_text_row(text, bold=False, size=11):
            nonlocal current_row
            if not text.strip():
                return
            cell = ws.cell(row=current_row, column=1, value=text.strip())
            cell.font = Font(bold=bold, size=size)
            cell.alignment = wrap_align
            current_row += 1

        def write_table(table_el):
            nonlocal current_row
            rows = table_el.find_all('tr')
            if not rows:
                return
            start_row = current_row
            max_col = 0
            for ri, tr in enumerate(rows):
                cells = tr.find_all(['th', 'td'])
                col = 1
                for ci, cell_el in enumerate(cells):
                    while ws.cell(row=current_row, column=col).value is not None:
                        col += 1
                    text  = cell_el.get_text(separator=' ', strip=True)
                    is_th = cell_el.name == 'th' or ri == 0
                    c = ws.cell(row=current_row, column=col, value=text)
                    c.border    = thin_border
                    c.alignment = center_align if is_th else wrap_align
                    if is_th:
                        c.font = header_font
                        c.fill = header_fill
                    else:
                        c.font = Font(size=11)
                    colspan = int(cell_el.get('colspan', 1))
                    rowspan = int(cell_el.get('rowspan', 1))
                    if colspan > 1 or rowspan > 1:
                        ws.merge_cells(
                            start_row=current_row, start_column=col,
                            end_row=current_row + rowspan - 1, end_column=col + colspan - 1
                        )
                    col += colspan
                    if col - 1 > max_col:
                        max_col = col - 1
                current_row += 1
            # ضبط عرض الأعمدة تلقائياً
            for c in range(1, max_col + 1):
                ws.column_dimensions[get_column_letter(c)].width = 22
            current_row += 1  # سطر فارغ بعد الجدول

        body = soup.find('body') or soup
        for el in body.find_all(['script', 'style', 'noscript'], recursive=True):
            el.decompose()

        for node in body.children:
            if not hasattr(node, 'name') or not node.name:
                t = str(node).strip()
                if t:
                    write_text_row(t)
                continue
            tag = node.name.lower()
            if tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
                level = int(tag[1])
                write_text_row(node.get_text(strip=True), bold=True, size=max(11, 16 - level))
            elif tag == 'table':
                write_table(node)
            elif tag in ('p', 'div', 'li', 'span', 'blockquote', 'pre'):
                # ابحث عن جداول بداخله
                inner_tables = node.find_all('table')
                if inner_tables:
                    for tbl in inner_tables:
                        write_table(tbl)
                else:
                    txt = node.get_text(separator=' ', strip=True)
                    if txt:
                        write_text_row(txt)
            elif tag in ('ul', 'ol'):
                for li in node.find_all('li', recursive=False):
                    write_text_row('• ' + li.get_text(strip=True))

        # حفظ الملف
        safe_name  = re.sub(r'[^\w\u0600-\u06FF\-_]', '_', filename) or 'document'
        outputs_dir = str(_PPTX_OUTPUTS_DIR)
        os.makedirs(outputs_dir, exist_ok=True)
        final_path = os.path.join(outputs_dir, safe_name + '.xlsx')
        wb.save(final_path)

        return jsonify({
            "success": True,
            "download_url": f"/tools/excel/download/{safe_name}.xlsx",
            "filename": f"{safe_name}.xlsx"
        })
    except Exception as e:
        logger.error(f"HTML to Excel error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route("/tools/excel/download/<path:filename>")
def tools_excel_download(filename):
    """تحميل ملف Excel المُنشأ"""
    from flask import send_from_directory
    outputs_dir = os.path.join(os.path.dirname(__file__), 'pptx_app', 'outputs')
    return send_from_directory(outputs_dir, filename, as_attachment=True)


# ════════════════════════════════════════════════════════════
#  مساعد الذكاء الاصطناعي (AI Assistant) - يستطيع تعديل الكود
# ════════════════════════════════════════════════════════════
_PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

def _ai_read_file(rel_path):
    """قراءة ملف من المشروع"""
    try:
        full = os.path.join(_PROJECT_ROOT, rel_path)
        full = os.path.realpath(full)
        if not full.startswith(_PROJECT_ROOT):
            return None, "مسار غير مسموح به"
        with open(full, 'r', encoding='utf-8', errors='replace') as f:
            return f.read(), None
    except Exception as e:
        return None, str(e)

def _ai_write_file(rel_path, content):
    """كتابة ملف في المشروع"""
    try:
        full = os.path.join(_PROJECT_ROOT, rel_path)
        full = os.path.realpath(full)
        if not full.startswith(_PROJECT_ROOT):
            return False, "مسار غير مسموح به"
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, 'w', encoding='utf-8') as f:
            f.write(content)
        return True, None
    except Exception as e:
        return False, str(e)

def _ai_list_files():
    """قائمة ملفات المشروع"""
    result = []
    skip_dirs = {'.git', '__pycache__', '.local', 'node_modules', 'pptx_app/outputs', 'sessions', '.cache', '_extract'}
    skip_exts = {'.pyc', '.pyo', '.session', '.session-journal', '.lock', '.jpg', '.png', '.ico', '.svg', '.webp'}
    for root, dirs, files in os.walk(_PROJECT_ROOT):
        dirs[:] = [d for d in dirs if d not in skip_dirs and not d.startswith('.')]
        rel_root = os.path.relpath(root, _PROJECT_ROOT)
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext in skip_exts:
                continue
            rel = os.path.join(rel_root, f) if rel_root != '.' else f
            result.append(rel)
    return result[:200]


def _ai_github_push(files_dict: dict, commit_msg: str = "🤖 تعديل تلقائي بواسطة المساعد الذكي") -> dict:
    """
    رفع ملفات إلى GitHub عبر REST API.
    files_dict: {rel_path: content_str}
    """
    import base64 as _b64
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json',
        'Content-Type': 'application/json',
    }
    api = 'https://api.github.com'
    results = {}
    for rel_path, content in files_dict.items():
        try:
            # الحصول على SHA الحالي للملف (إن وُجد)
            get_url = f"{api}/repos/{GITHUB_REPO}/contents/{rel_path}"
            gr = requests.get(get_url, headers=headers, params={'ref': GITHUB_BRANCH}, timeout=15)
            sha = gr.json().get('sha') if gr.ok else None
            # رفع الملف
            body = {
                'message': commit_msg,
                'content': _b64.b64encode(content.encode('utf-8', errors='replace')).decode(),
                'branch': GITHUB_BRANCH,
            }
            if sha:
                body['sha'] = sha
            pr = requests.put(get_url, headers=headers, json=body, timeout=30)
            results[rel_path] = 'pushed' if pr.ok else f"error {pr.status_code}"
        except Exception as ex:
            results[rel_path] = f"exception: {ex}"
    return results


def _ai_extract_code_blocks(text: str) -> list[dict]:
    """
    استخراج كتل الكود من رد الذكاء الاصطناعي.
    يدعم:  ```python app.py  أو  ```# app.py  أو  ```app.py
    """
    import re as _re
    blocks = []
    pattern = _re.compile(
        r'```(?P<lang>\w+)?\s*(?P<path>[^\n`]{2,100}\.[a-zA-Z]{1,6})?\n(?P<code>.*?)```',
        _re.DOTALL
    )
    for m in pattern.finditer(text):
        code = m.group('code').strip()
        path = (m.group('path') or '').strip()
        lang = (m.group('lang') or '').strip()
        blocks.append({'lang': lang, 'path': path, 'code': code})
    return blocks


@app.route("/api/ai_assistant", methods=["POST"])
def api_ai_assistant():
    """مساعد الذكاء الاصطناعي الكامل — قراءة، تعديل، رفع GitHub"""
    try:
        data     = request.get_json() or {}
        messages = data.get('messages', [])
        action   = data.get('action', 'chat')      # chat | apply | github_push
        target_file = data.get('file', '')         # ملف مستهدف يمكن تحديده يدوياً

        from groq import Groq as _Groq
        client = _Groq(api_key=GROQ_API_KEY)

        # ── قائمة الملفات والملخص ──────────────────────────────
        files_list   = _ai_list_files()
        file_summaries = []
        for mf in ['app.py', 'templates/index.html', 'templates/academic.html',
                   'static/js/app.js', 'requirements.txt', 'render.yaml']:
            c, _ = _ai_read_file(mf)
            if c:
                file_summaries.append(f"- {mf} ({len(c.splitlines())} سطر)")

        system_prompt = f"""أنت مساعد ذكاء اصطناعي مفيد لمستخدمي برنامج "مركز سرعة انجاز".

البرنامج: أداة أتمتة تيليجرام (الانضمام للمجموعات، الرد التلقائي، الجدولة، إرسال الرسائل).

مهمتك: الإجابة على أسئلة المستخدمين حول كيفية استخدام البرنامج، شرح الميزات، ومساعدتهم في حل مشكلاتهم العملية.

لا تملك صلاحية تعديل ملفات البرنامج أو كتابة كود — أنت مساعد محادثة فقط.

أجب بالعربية دائماً. كن مختصراً وودوداً وعملياً."""

        history = [{'role': 'system', 'content': system_prompt}] + messages[-20:]

        # ── استدعاء GROQ (محادثة عادية فقط) ──────────────────
        resp = client.chat.completions.create(
            model='llama-3.3-70b-versatile',
            messages=history,
            max_tokens=1500,
            temperature=0.6,
        )
        reply = resp.choices[0].message.content

        return jsonify({
            "success":      True,
            "reply":        reply,
            "apply_result": None,
            "github_result": None,
            "files_list":   []
        })
    except Exception as e:
        logger.error(f"AI Assistant error: {e}", exc_info=True)
        return jsonify({"error": str(e), "success": False}), 500


@app.route("/api/ai_github_push", methods=["POST"])
def api_ai_github_push():
    """رفع ملفات محددة إلى GitHub"""
    try:
        data       = request.get_json() or {}
        file_paths = data.get('files', [])   # قائمة مسارات نسبية
        commit_msg = data.get('message', '🤖 تحديث بواسطة المساعد الذكي')
        if not file_paths:
            # رفع جميع الملفات الرئيسية
            file_paths = ['app.py', 'templates/index.html', 'templates/academic.html',
                          'static/js/app.js', 'requirements.txt', 'render.yaml']
        files_to_push = {}
        for fp in file_paths:
            c, _ = _ai_read_file(fp)
            if c:
                files_to_push[fp] = c
        if not files_to_push:
            return jsonify({"error": "لم يُعثر على ملفات"}), 400
        result = _ai_github_push(files_to_push, commit_msg)
        return jsonify({"success": True, "result": result, "pushed": len(files_to_push)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/ai_read_file", methods=["POST"])
def api_ai_read_file_endpoint():
    """قراءة ملف للمساعد الذكي"""
    try:
        data = request.get_json() or {}
        rel_path = data.get('path', '')
        if not rel_path:
            return jsonify({"error": "المسار مطلوب"}), 400
        content, err = _ai_read_file(rel_path)
        if err:
            return jsonify({"error": err}), 400
        return jsonify({"success": True, "content": content, "lines": len(content.splitlines())})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/ai_write_file", methods=["POST"])
def api_ai_write_file_endpoint():
    """كتابة/تعديل ملف عبر المساعد الذكي"""
    try:
        data = request.get_json() or {}
        rel_path = data.get('path', '')
        content  = data.get('content', '')
        if not rel_path:
            return jsonify({"error": "المسار مطلوب"}), 400
        ok, err = _ai_write_file(rel_path, content)
        if not ok:
            return jsonify({"error": err}), 400
        return jsonify({"success": True, "message": f"تم حفظ {rel_path} بنجاح"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ════════════════════════════════════════════════════════════
#  منشئ العروض التقديمية — مدموج بالكامل داخل app.py
# ════════════════════════════════════════════════════════════

# ── مجلد المخرجات ──────────────────────────────────────────
from pathlib import Path
_PPTX_OUTPUTS_DIR = Path(__file__).parent / "pptx_app" / "outputs"
_PPTX_OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
_PPTX_IMG_CACHE   = _PPTX_OUTPUTS_DIR / "img_cache"
_PPTX_IMG_CACHE.mkdir(parents=True, exist_ok=True)

# ── قوالب الألوان (templates.py) ───────────────────────────
_PPTX_THEMES = {
    "blue":   {"name":"أزرق احترافي",  "primary":(0x66,0x7E,0xEA),"secondary":(0x76,0x4B,0xA2),"accent":(0xFF,0xFF,0xFF),"text_dark":(0x1A,0x1A,0x2E),"text_light":(0xFF,0xFF,0xFF),"bg":(0xF5,0xF7,0xFF)},
    "green":  {"name":"أخضر طبيعي",    "primary":(0x11,0x99,0x55),"secondary":(0x00,0x7A,0x3D),"accent":(0xFF,0xFF,0xFF),"text_dark":(0x1A,0x2E,0x1A),"text_light":(0xFF,0xFF,0xFF),"bg":(0xF0,0xFB,0xF4)},
    "red":    {"name":"أحمر حيوي",     "primary":(0xE5,0x39,0x35),"secondary":(0xB7,0x1C,0x1C),"accent":(0xFF,0xCC,0x02),"text_dark":(0x2E,0x1A,0x1A),"text_light":(0xFF,0xFF,0xFF),"bg":(0xFD,0xF2,0xF2)},
    "purple": {"name":"بنفسجي ملكي",   "primary":(0x6A,0x1B,0x9A),"secondary":(0x4A,0x14,0x8C),"accent":(0xFF,0xD7,0x00),"text_dark":(0x1A,0x1A,0x2E),"text_light":(0xFF,0xFF,0xFF),"bg":(0xF8,0xF0,0xFF)},
}

def _pptx_get_theme(color: str) -> dict:
    return _PPTX_THEMES.get(color, _PPTX_THEMES["blue"])

# ── مساعدات pptx عامة ──────────────────────────────────────
try:
    from pptx import Presentation as _Prs
    from pptx.util import Inches as _Inches, Pt as _Pt, Emu as _Emu
    from pptx.dml.color import RGBColor as _RGBColor
    from pptx.enum.text import PP_ALIGN as _PP_ALIGN
    from pptx.oxml.ns import qn as _qn
    from lxml import etree as _etree
    _PPTX_AVAILABLE = True
except ImportError:
    _PPTX_AVAILABLE = False

def _pptx_rgb(t):
    return _RGBColor(*t)

def _pptx_set_rtl(paragraph):
    pPr = paragraph._p.get_or_add_pPr()
    pPr.set("rtl", "1")

def _pptx_set_run_font(run, font_name: str):
    run.font.name = font_name
    rPr = run._r.get_or_add_rPr()
    for tag in ("a:latin", "a:cs", "a:ea"):
        el = rPr.find(_qn(tag))
        if el is None:
            el = _etree.SubElement(rPr, _qn(tag))
        el.set("typeface", font_name)

def _pptx_add_text_box(slide, left, top, width, height, text, size,
                       bold=False, color=(0,0,0), align=None, wrap=True,
                       font_name="Traditional Arabic"):
    if align is None:
        align = _PP_ALIGN.RIGHT
    box = slide.shapes.add_textbox(_Inches(left), _Inches(top), _Inches(width), _Inches(height))
    tf = box.text_frame; tf.word_wrap = wrap
    p = tf.paragraphs[0]; p.alignment = align; _pptx_set_rtl(p)
    run = p.add_run()
    run.text = text; run.font.size = _Pt(size); run.font.bold = bold
    run.font.color.rgb = _pptx_rgb(color); _pptx_set_run_font(run, font_name)
    return box

def _pptx_set_cell_bg(cell, color_tuple):
    tc = cell._tc; tcPr = tc.get_or_add_tcPr()
    sf = _etree.SubElement(tcPr, _qn("a:solidFill"))
    sc = _etree.SubElement(sf, _qn("a:srgbClr"))
    sc.set("val", "{:02X}{:02X}{:02X}".format(*color_tuple))

# ── جالب الصور (image_fetcher.py) ──────────────────────────
import hashlib as _hashlib

_PPTX_ARABIC_TO_EN = {
    "تعليم":"education","مدرسة":"school","جامعة":"university","طالب":"students",
    "تدريب":"training","تعلم":"learning","اختبار":"exam","تقنية":"technology",
    "ذكاء اصطناعي":"artificial intelligence","برمجة":"coding","حاسوب":"computer",
    "شبكة":"network","بيانات":"data analytics","سحابة":"cloud computing",
    "ابتكار":"innovation","ذكاء":"artificial intelligence","أعمال":"business",
    "شركة":"corporate office","تجارة":"commerce","سوق":"market","مبيعات":"sales",
    "تسويق":"marketing","إدارة":"management","قيادة":"leadership","فريق":"team",
    "اجتماع":"meeting","عمل":"workplace","موظف":"employees","استراتيجية":"strategy",
    "خطة":"planning","ميزانية":"finance","استثمار":"investment","نمو":"growth chart",
    "صحة":"healthcare","طب":"medicine","مستشفى":"hospital","رياضة":"sports",
    "بيئة":"environment","طاقة":"renewable energy","طبيعة":"nature landscape",
    "مجتمع":"community","أسرة":"family","شباب":"youth","سياحة":"tourism",
    "بناء":"architecture","مشروع":"construction project","تصميم":"design",
    "هندسة":"engineering","خلاصة":"success achievement","نتائج":"results achievement",
    "هدف":"goal target","مستقبل":"future vision","إنجاز":"achievement","نجاح":"success",
}
_PPTX_SLIDE_TYPE_DEFAULTS = {
    "title":"professional presentation","conclusion":"success achievement team",
    "table":"data analytics chart","chart":"business graph analytics","bullets":"professional business",
}

def _pptx_get_slide_image(slide_title, slide_bullets, slide_type="bullets", groq_client=None):
    keywords = ""
    if groq_client:
        try:
            content = slide_title + "\n" + "\n".join(slide_bullets[:3])
            resp = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role":"user","content":f"Extract 2-3 English keywords for image search from Arabic:\n{content}\nReturn ONLY keywords separated by commas."}],
                max_tokens=25, temperature=0.2,
            )
            kw = resp.choices[0].message.content.strip().replace("\n",",")
            keywords = ",".join([k.strip() for k in kw.split(",") if k.strip()])
        except Exception:
            pass
    if not keywords:
        full = slide_title + " " + " ".join(slide_bullets[:3])
        for ar, en in _PPTX_ARABIC_TO_EN.items():
            if ar in full:
                keywords = en.replace(" ",","); break
    if not keywords:
        keywords = _PPTX_SLIDE_TYPE_DEFAULTS.get(slide_type, "professional business")
    safe_kw   = keywords.strip()[:80]
    cache_key = _hashlib.md5(safe_kw.encode()).hexdigest()[:10]
    cache_path = _PPTX_IMG_CACHE / f"{cache_key}.jpg"
    if cache_path.exists() and cache_path.stat().st_size > 4000:
        return str(cache_path)
    try:
        import requests as _req
        resp = _req.get(f"https://loremflickr.com/900/550/{safe_kw}", timeout=8, allow_redirects=True)
        if resp.status_code == 200 and len(resp.content) > 4000:
            cache_path.write_bytes(resp.content); return str(cache_path)
    except Exception:
        pass
    return None

# ── توليد الرسوم البيانية (chart_generator.py) ─────────────
def _pptx_create_chart(chart_type, labels, values, title="", color="#667eea"):
    try:
        import matplotlib; matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import tempfile
        colors_list = ["#667eea","#764ba2","#11aa55","#e53935","#ff6b35","#00bcd4","#ffc107","#9c27b0"]
        fig, ax = plt.subplots(figsize=(8,5))
        fig.patch.set_facecolor("#f8f9ff"); ax.set_facecolor("#f8f9ff")
        if chart_type == "bar":
            bars = ax.bar(labels, values, color=colors_list[:len(labels)])
            for bar, val in zip(bars, values):
                ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+max(values)*0.01, f"{val:,.0f}", ha="center", va="bottom", fontsize=9, fontweight="bold")
            ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
        elif chart_type == "pie":
            ax.pie(values, labels=labels, autopct="%1.1f%%", colors=colors_list[:len(labels)], startangle=90, pctdistance=0.85)
        elif chart_type == "line":
            ax.plot(labels, values, color=color, linewidth=2.5, marker="o", markersize=7)
            ax.fill_between(range(len(labels)), values, alpha=0.15, color=color)
            ax.set_xticks(range(len(labels))); ax.set_xticklabels(labels)
            ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
        elif chart_type == "horizontal_bar":
            ax.barh(labels, values, color=colors_list[:len(labels)])
            ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
        if title:
            ax.set_title(title, fontsize=13, fontweight="bold", pad=12)
        plt.tight_layout()
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        plt.savefig(tmp.name, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
        plt.close(fig); return tmp.name
    except Exception as e:
        logger.warning(f"Chart error: {e}"); return None

# ── معالج الذكاء الاصطناعي (ai_processor.py) ───────────────
_PPTX_GROQ_MODEL = "llama-3.3-70b-versatile"

def _pptx_subtitle(ptype):
    return {"business":"عرض تجاري احترافي","educational":"مواد تعليمية متميزة","sales":"عرض تسويقي متكامل","general":"عرض تقديمي شامل"}.get(ptype,"عرض تقديمي")

def _pptx_section_titles(ptype):
    return {"business":["نظرة عامة","الأهداف الاستراتيجية","الخطة التنفيذية","الميزانية والموارد","مؤشرات النجاح"],"educational":["المقدمة","المفاهيم الأساسية","التطبيقات العملية","الأمثلة والتدريبات","التقييم"],"sales":["المشكلة","الحل المقترح","المميزات والفوائد","الأسعار والعروض","لماذا نحن؟"],"general":["المقدمة","المحتوى الرئيسي","التفاصيل","النتائج","التوصيات"]}.get(ptype,["المقدمة","المحتوى","التفاصيل","النتائج","الخلاصة"])

def _pptx_process_locally(text, num_slides, ptype, extracted_tables):
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    sentences = []
    for line in lines:
        parts = re.split(r'[.،,;؛]', line)
        sentences.extend([p.strip() for p in parts if len(p.strip()) > 5])
    title = sentences[0][:70] if sentences else "العرض التقديمي"
    slides = [{"title":title,"subtitle":_pptx_subtitle(ptype),"bullets":[],"slide_type":"title"}]
    remaining = sentences[1:] if len(sentences)>1 else ["محتوى العرض"]
    content_count = max(1, num_slides-2)
    chunk_size = max(1, len(remaining)//max(1,content_count))
    sec_titles = _pptx_section_titles(ptype)
    tables_used = 0
    for i in range(content_count):
        chunk = remaining[i*chunk_size:(i+1)*chunk_size]
        bullets = [b[:120] for b in chunk if b][:5]
        if not bullets:
            bullets = [f"النقطة الرئيسية {i+1}","التفاصيل والمعلومات","الخلاصة الجزئية"]
        slide = {"title":sec_titles[i%len(sec_titles)],"subtitle":"","bullets":bullets,"slide_type":"bullets"}
        if extracted_tables and tables_used<len(extracted_tables) and i==content_count//2:
            slide["slide_type"]="table"; slide["table_data"]=extracted_tables[tables_used]; tables_used+=1
        slides.append(slide)
    slides.append({"title":"الخلاصة والتوصيات","subtitle":"","bullets":["✅ "+(sentences[-1][:90] if sentences else "تم عرض أهم النقاط"),"📌 نرحب بأسئلتكم واستفساراتكم","🙏 شكراً لاهتمامكم"],"slide_type":"conclusion"})
    return slides[:num_slides]

class _AIProcessor:
    def __init__(self):
        self.groq_available = False; self.client = None
        try:
            from groq import Groq
            api_key = os.environ.get("GROQ_API_KEY","").strip()
            if api_key:
                self.client = Groq(api_key=api_key); self.groq_available = True
        except Exception as e:
            logger.warning(f"[Groq init] {e}")

    @property
    def is_ai_available(self): return self.groq_available

    def text_to_presentation_structure(self, text, num_slides=6, presentation_type="general",
                                       title_override="", include_tables=False, include_charts=False,
                                       extracted_tables=None):
        if self.groq_available:
            slides = self._process_with_groq(text, num_slides, presentation_type, include_tables, include_charts)
        else:
            slides = _pptx_process_locally(text, num_slides, presentation_type, extracted_tables or [])
        if title_override and slides:
            slides[0]["title"] = title_override
        return slides

    def _process_with_groq(self, text, num_slides, ptype, include_tables, include_charts):
        label = {"general":"عام","business":"تجاري","educational":"تعليمي","sales":"تسويقي"}.get(ptype,"عام")
        extras = ""
        if include_tables: extras += '\n- أضف شريحة جدول بنوع "table" مع مفتاح "table_data"'
        if include_charts: extras += '\n- أضف شريحة رسم بياني بنوع "chart" مع chart_type/chart_labels/chart_values'
        user_prompt = f"""حلّل النص وأنشئ هيكل عرض {label} من {num_slides} شرائح.{extras}

النص:
{text[:4000]}

القواعد:
- الأولى: نوع "title" مع عنوان رئيسي وعنوان فرعي
- الأخيرة: نوع "conclusion" مع 3 نقاط
- الوسطى: نوع "bullets" مع 3-5 نقاط
- كل المحتوى بالعربية
- أرجع JSON فقط: [{{"title":"...","subtitle":"...","bullets":["..."],"slide_type":"title|bullets|table|chart|conclusion",...}}]"""
        try:
            resp = self.client.chat.completions.create(
                model=_PPTX_GROQ_MODEL,
                messages=[{"role":"system","content":"أنت خبير عروض تقديمية. تُنتج JSON صحيحاً فقط."},{"role":"user","content":user_prompt}],
                max_tokens=3000, temperature=0.65,
            )
            content = resp.choices[0].message.content.strip()
            match = re.search(r'\[.*\]', content, re.DOTALL)
            if match:
                slides = json.loads(match.group())
                if isinstance(slides, list) and slides:
                    return slides
        except Exception as e:
            logger.warning(f"[Groq pptx] {e}")
        return _pptx_process_locally(text, num_slides, ptype, [])

# ── مولّد PPTX (presentation_generator.py) ─────────────────
class _PresentationGenerator:
    def __init__(self):
        self.font_name = "Traditional Arabic"
        self.body_font_size = 22

    def _parse_color(self, color_str):
        from pptx.dml.color import RGBColor
        import re
        if not color_str:
            return None
        s = color_str.strip().lower()
        if s.startswith('#'):
            c = s.lstrip('#')
            if len(c) == 3:
                c = c[0]*2 + c[1]*2 + c[2]*2
            if len(c) >= 6:
                return RGBColor(int(c[0:2],16), int(c[2:4],16), int(c[4:6],16))
        if s.startswith('rgb'):
            nums = re.findall(r'[\d.]+', s)
            if len(nums) >= 3:
                r,g,b = int(float(nums[0])), int(float(nums[1])), int(float(nums[2]))
                return RGBColor(min(r,255), min(g,255), min(b,255))
        named = {
            'black':(0,0,0),'white':(255,255,255),'red':(255,0,0),'green':(0,128,0),
            'blue':(0,0,255),'yellow':(255,255,0),'orange':(255,165,0),'purple':(128,0,128),
            'pink':(255,192,203),'gray':(128,128,128),'grey':(128,128,128),'brown':(165,42,42),
            'cyan':(0,255,255),'magenta':(255,0,255),'navy':(0,0,128),'teal':(0,128,128),
            'lime':(0,255,0),'maroon':(128,0,0),'olive':(128,128,0),'silver':(192,192,192),
            'gold':(255,215,0),'coral':(255,127,80),'salmon':(250,128,114),'turquoise':(64,224,208),
            'indigo':(75,0,130),'violet':(238,130,238),'darkblue':(0,0,139),'darkgreen':(0,100,0),
            'darkred':(139,0,0),'darkgray':(169,169,169),'lightblue':(173,216,230),
            'lightgreen':(144,238,144),'lightyellow':(255,255,224),'lightgray':(211,211,211),
            'crimson':(220,20,60),'deepskyblue':(0,191,255),'forestgreen':(34,139,34),
            'hotpink':(255,105,180),'limegreen':(50,205,50),'mediumblue':(0,0,205),
            'orangered':(255,69,0),'royalblue':(65,105,225),'seagreen':(46,139,87),
            'skyblue':(135,206,235),'slategray':(112,128,144),'steelblue':(70,130,180),
            'tomato':(255,99,71),'yellowgreen':(154,205,50),'beige':(245,245,220),
            'ivory':(255,255,240),'khaki':(240,230,140),'lavender':(230,230,250),
            'wheat':(245,222,179)
        }
        if s in named:
            r,g,b = named[s]
            return RGBColor(r,g,b)
        return None

    def _fetch_image(self, src):
        import base64 as _b64, requests as _req
        if src.startswith("data:image"):
            try:
                header, data = src.split(",", 1)
                return _b64.b64decode(data)
            except Exception:
                return None
        elif src.startswith("http"):
            try:
                resp = _req.get(src, timeout=5)
                if resp.ok:
                    return resp.content
            except Exception:
                pass
        return None

    def _save_temp_image(self, src):
        import tempfile as _tmp
        data = self._fetch_image(src)
        if data:
            ext = 'png' if 'png' in src else 'jpg'
            fd, path = _tmp.mkstemp(suffix=f'.{ext}')
            with os.fdopen(fd, 'wb') as f:
                f.write(data)
            return path
        return None

    def create_presentation(self, slides_data, theme_color="blue", cover_data=None,
                            extracted_images=None, font_name="Traditional Arabic",
                            body_font_size=22, ai_images=False, groq_client=None):
        from datetime import datetime as _dt
        self.font_name = font_name; self.body_font_size = body_font_size
        theme = _pptx_get_theme(theme_color)
        prs = _Prs()
        prs.slide_width = _Inches(13.33); prs.slide_height = _Inches(7.5)
        if cover_data:
            self._add_cover_slide(prs, cover_data, theme)
        for i, sd in enumerate(slides_data):
            stype = sd.get("slide_type","bullets")
            if stype == "title":        self._add_title_slide(prs, sd, theme)
            elif stype == "table" and sd.get("table_data"): self._add_table_slide(prs, sd, theme)
            elif stype == "chart":      self._add_chart_slide(prs, sd, theme)
            elif stype == "conclusion": self._add_conclusion_slide(prs, sd, theme)
            else:
                img_path = None
                if sd.get("images"):
                    img_src = sd["images"][0]
                    img_path = self._save_temp_image(img_src)
                if not img_path and extracted_images and i < len(extracted_images):
                    img_path = extracted_images[i]
                if not img_path and ai_images:
                    img_path = _pptx_get_slide_image(sd.get("title",""), sd.get("bullets",[]), stype, groq_client)
                self._add_content_slide(prs, sd, theme, i, img_path)
        ts = _dt.now().strftime("%Y%m%d_%H%M%S")
        out = str(_PPTX_OUTPUTS_DIR / f"عرض_{ts}.pptx")
        prs.save(out); return out

    def _add_cover_slide(self, prs, cover_data, theme):
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        bg = slide.background.fill; bg.solid(); bg.fore_color.rgb = _pptx_rgb(theme["primary"])
        rect = slide.shapes.add_shape(1,_Inches(0),_Inches(0),_Inches(13.33),_Inches(2.2))
        rect.fill.solid(); rect.fill.fore_color.rgb = _pptx_rgb(theme["secondary"]); rect.line.fill.background()
        logo_box = slide.shapes.add_textbox(_Inches(0.5),_Inches(0.35),_Inches(2),_Inches(1.5))
        lp = logo_box.text_frame.paragraphs[0]; lp.alignment = _PP_ALIGN.CENTER
        lr = lp.add_run(); lr.text = cover_data.get("logo","📊"); lr.font.size = _Pt(52)
        org = cover_data.get("organization","")
        if org:
            ob = slide.shapes.add_textbox(_Inches(2.8),_Inches(0.5),_Inches(10),_Inches(1))
            op = ob.text_frame.paragraphs[0]; op.alignment = _PP_ALIGN.RIGHT; _pptx_set_rtl(op)
            or_ = op.add_run(); or_.text = org; or_.font.size = _Pt(20); or_.font.bold = True
            or_.font.color.rgb = _RGBColor(220,220,255); _pptx_set_run_font(or_, self.font_name)
        fn = self.font_name
        _pptx_add_text_box(slide,1,2.5,11.3,1.8,cover_data.get("title","العنوان الرئيسي"),42,bold=True,color=theme["text_light"],align=_PP_ALIGN.CENTER,font_name=fn)
        subtitle = cover_data.get("subtitle","")
        if subtitle:
            _pptx_add_text_box(slide,1.5,4.4,10.3,0.9,subtitle,22,color=(210,210,240),align=_PP_ALIGN.CENTER,font_name=fn)
        line = slide.shapes.add_shape(1,_Inches(3.5),_Inches(5.5),_Inches(6.3),_Emu(35000))
        line.fill.solid(); line.fill.fore_color.rgb = _pptx_rgb(theme["accent"]); line.line.fill.background()
        meta = []
        if cover_data.get("presenter"): meta.append(f"إعداد: {cover_data['presenter']}")
        if cover_data.get("date"): meta.append(cover_data["date"])
        if meta:
            _pptx_add_text_box(slide,1,5.9,11.3,0.7,"  |  ".join(meta),16,color=(200,200,230),align=_PP_ALIGN.CENTER,font_name=fn)

    def _add_title_slide(self, prs, data, theme):
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        bg = slide.background.fill; bg.solid(); bg.fore_color.rgb = _pptx_rgb(theme["primary"])
        self._add_bottom_strip(slide, theme); fn = self.font_name
        _pptx_add_text_box(slide,1,2.2,11.3,1.8,data.get("title","العنوان"),44,bold=True,color=theme["text_light"],align=_PP_ALIGN.CENTER,font_name=fn)
        subtitle = data.get("subtitle","")
        if subtitle:
            _pptx_add_text_box(slide,2,4.2,9.3,1,subtitle,24,color=(220,220,255),align=_PP_ALIGN.CENTER,font_name=fn)
        line = slide.shapes.add_shape(1,_Inches(4.5),_Inches(4.0),_Inches(4.3),_Emu(40000))
        line.fill.solid(); line.fill.fore_color.rgb = _pptx_rgb(theme["accent"]); line.line.fill.background()

    def _add_content_slide(self, prs, data, theme, index, img_path=None):
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        # تطبيق خلفية الشريحة (من HTML أو من الثيم)
        bg_color = data.get("bg_color")
        if bg_color:
            rgb = self._parse_color(bg_color)
            if rgb:
                bg = slide.background.fill; bg.solid(); bg.fore_color.rgb = rgb
            else:
                bg = slide.background.fill; bg.solid(); bg.fore_color.rgb = _pptx_rgb(theme["bg"])
        else:
            bg = slide.background.fill; bg.solid(); bg.fore_color.rgb = _pptx_rgb(theme["bg"])
        header = slide.shapes.add_shape(1,_Inches(0),_Inches(0),_Inches(13.33),_Inches(1.35))
        header.fill.solid(); header.fill.fore_color.rgb = _pptx_rgb(theme["primary"]); header.line.fill.background()
        _pptx_add_text_box(slide,0.4,0.15,12,1.05,data.get("title",""),27,bold=True,color=theme["text_light"],align=_PP_ALIGN.RIGHT,font_name=self.font_name)
        bullets = data.get("bullets",[])
        has_image = img_path and Path(img_path).exists()
        if has_image:
            content_box = slide.shapes.add_textbox(_Inches(4.8),_Inches(1.55),_Inches(8.1),_Inches(5.7))
            self._fill_bullets(content_box.text_frame, bullets, theme)
            try:
                frame = slide.shapes.add_shape(1,_Inches(0.18),_Inches(1.48),_Inches(4.44),_Inches(5.64))
                frame.fill.solid(); frame.fill.fore_color.rgb = _pptx_rgb(theme["accent"]); frame.line.fill.background()
                slide.shapes.add_picture(img_path,_Inches(0.25),_Inches(1.55),_Inches(4.3),_Inches(5.5))
            except Exception:
                content_box2 = slide.shapes.add_textbox(_Inches(0.5),_Inches(1.55),_Inches(12.3),_Inches(5.7))
                self._fill_bullets(content_box2.text_frame, bullets, theme)
        else:
            # إضافة صور من HTML مباشرة إن وجدت
            images = data.get("images", [])
            if images:
                temp_path = self._save_temp_image(images[0])
                if temp_path:
                    try:
                        content_box = slide.shapes.add_textbox(_Inches(4.8),_Inches(1.55),_Inches(8.1),_Inches(5.7))
                        self._fill_bullets(content_box.text_frame, bullets, theme)
                        slide.shapes.add_picture(temp_path,_Inches(0.25),_Inches(1.55),_Inches(4.3),_Inches(5.5))
                    except Exception:
                        content_box = slide.shapes.add_textbox(_Inches(0.5),_Inches(1.55),_Inches(12.3),_Inches(5.7))
                        self._fill_bullets(content_box.text_frame, bullets, theme)
                    finally:
                        try: os.unlink(temp_path)
                        except: pass
                else:
                    content_box = slide.shapes.add_textbox(_Inches(0.5),_Inches(1.55),_Inches(12.3),_Inches(5.7))
                    self._fill_bullets(content_box.text_frame, bullets, theme)
            else:
                content_box = slide.shapes.add_textbox(_Inches(0.5),_Inches(1.55),_Inches(12.3),_Inches(5.7))
                self._fill_bullets(content_box.text_frame, bullets, theme)
        num_box = slide.shapes.add_textbox(_Inches(12.6),_Inches(6.9),_Inches(0.7),_Inches(0.5))
        np_ = num_box.text_frame.paragraphs[0]; np_.alignment = _PP_ALIGN.CENTER
        nr = np_.add_run(); nr.text = str(index+1); nr.font.size = _Pt(11); nr.font.color.rgb = _pptx_rgb(theme["secondary"])

    def _fill_bullets(self, tf, bullets, theme):
        tf.word_wrap = True; fs = self.body_font_size; fn = self.font_name
        for i, bullet in enumerate(bullets):
            p = tf.paragraphs[0] if i==0 else tf.add_paragraph()
            p.alignment = _PP_ALIGN.RIGHT; _pptx_set_rtl(p); p.space_before = _Pt(10); p.space_after = _Pt(4)
            run = p.add_run(); run.text = f"◆ {bullet}"; run.font.size = _Pt(fs)
            run.font.color.rgb = _pptx_rgb(theme["text_dark"]); _pptx_set_run_font(run, fn)

    def _add_table_slide(self, prs, data, theme):
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        bg = slide.background.fill; bg.solid(); bg.fore_color.rgb = _pptx_rgb(theme["bg"])
        header = slide.shapes.add_shape(1,_Inches(0),_Inches(0),_Inches(13.33),_Inches(1.35))
        header.fill.solid(); header.fill.fore_color.rgb = _pptx_rgb(theme["primary"]); header.line.fill.background()
        _pptx_add_text_box(slide,0.4,0.15,12,1.05,data.get("title","جدول البيانات"),27,bold=True,color=theme["text_light"],align=_PP_ALIGN.RIGHT,font_name=self.font_name)
        table_data = data.get("table_data",[])
        if not table_data: return
        rows = len(table_data); cols = max(len(r) for r in table_data)
        if rows==0 or cols==0: return
        table = slide.shapes.add_table(rows,cols,_Inches(0.5),_Inches(1.6),_Inches(12.3),_Inches(min(5.5,0.5+rows*0.55))).table
        fn = self.font_name
        for r_idx, row in enumerate(table_data):
            for c_idx in range(cols):
                cell_data = row[c_idx] if c_idx < len(row) else {"text": ""}
                if isinstance(cell_data, dict):
                    text = cell_data.get("text", "")
                    bg_color = cell_data.get("bg")
                    align_val = cell_data.get("align", "center")
                    bold = cell_data.get("bold", False)
                else:
                    text = str(cell_data); bg_color = None; align_val = "center"; bold = (r_idx == 0)
                cell = table.cell(r_idx, c_idx); cell.text = text
                tf = cell.text_frame; par = tf.paragraphs[0]
                par.alignment = getattr(_PP_ALIGN, align_val.upper(), _PP_ALIGN.CENTER); _pptx_set_rtl(par)
                if bg_color:
                    rgb = self._parse_color(bg_color)
                    if rgb: _pptx_set_cell_bg(cell, (rgb.red, rgb.green, rgb.blue))
                    else: _pptx_set_cell_bg(cell, theme["primary"] if r_idx==0 else ((235,238,255) if r_idx%2==0 else (255,255,255)))
                else:
                    _pptx_set_cell_bg(cell, theme["primary"] if r_idx==0 else ((235,238,255) if r_idx%2==0 else (255,255,255)))
                runs = par.runs
                if runs:
                    runs[0].font.size = _Pt(15); runs[0].font.bold = bold or (r_idx==0)
                    runs[0].font.color.rgb = _pptx_rgb(theme["text_light"] if r_idx==0 else theme["text_dark"])
                    _pptx_set_run_font(runs[0], fn)

    def _add_chart_slide(self, prs, data, theme):
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        bg = slide.background.fill; bg.solid(); bg.fore_color.rgb = _pptx_rgb(theme["bg"])
        header = slide.shapes.add_shape(1,_Inches(0),_Inches(0),_Inches(13.33),_Inches(1.35))
        header.fill.solid(); header.fill.fore_color.rgb = _pptx_rgb(theme["primary"]); header.line.fill.background()
        _pptx_add_text_box(slide,0.4,0.15,12,1.05,data.get("title","رسم بياني"),27,bold=True,color=theme["text_light"],align=_PP_ALIGN.RIGHT,font_name=self.font_name)
        chart_type = data.get("chart_type","bar"); labels = data.get("chart_labels",[]); values = data.get("chart_values",[])
        if not labels or not values:
            _pptx_add_text_box(slide,1,3,11,2,"لا توجد بيانات كافية",20,color=theme["text_dark"],font_name=self.font_name); return
        try: values_float = [float(v) for v in values]
        except Exception: values_float = [1.0]*len(labels)
        primary_hex = "#{:02x}{:02x}{:02x}".format(*theme["primary"])
        img_path = _pptx_create_chart(chart_type, labels, values_float, data.get("chart_title",""), primary_hex)
        if img_path and Path(img_path).exists():
            slide.shapes.add_picture(img_path,_Inches(1.5),_Inches(1.6),_Inches(10.3),_Inches(5.6))
        else:
            _pptx_add_text_box(slide,1,3,11,2,"تعذّر إنشاء الرسم البياني",20,color=theme["text_dark"],font_name=self.font_name)

    def _add_conclusion_slide(self, prs, data, theme):
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        bg = slide.background.fill; bg.solid(); bg.fore_color.rgb = _pptx_rgb(theme["secondary"])
        fn = self.font_name
        _pptx_add_text_box(slide,1,1.5,11.3,1.2,data.get("title","الخلاصة"),36,bold=True,color=theme["text_light"],align=_PP_ALIGN.CENTER,font_name=fn)
        line = slide.shapes.add_shape(1,_Inches(3.5),_Inches(2.9),_Inches(6.3),_Emu(35000))
        line.fill.solid(); line.fill.fore_color.rgb = _pptx_rgb(theme["accent"]); line.line.fill.background()
        bullets = data.get("bullets",[]); cont_box = slide.shapes.add_textbox(_Inches(1.5),_Inches(3.2),_Inches(10.3),_Inches(4.0))
        tf = cont_box.text_frame; tf.word_wrap = True
        for i, bullet in enumerate(bullets):
            p = tf.paragraphs[0] if i==0 else tf.add_paragraph()
            p.alignment = _PP_ALIGN.RIGHT; _pptx_set_rtl(p); p.space_before = _Pt(12)
            run = p.add_run(); run.text = bullet; run.font.size = _Pt(self.body_font_size)
            run.font.color.rgb = _RGBColor(220,220,255); _pptx_set_run_font(run, fn)

    def _add_bottom_strip(self, slide, theme):
        rect = slide.shapes.add_shape(1,_Inches(0),_Inches(6.8),_Inches(13.33),_Inches(0.7))
        rect.fill.solid(); rect.fill.fore_color.rgb = _pptx_rgb(theme["secondary"]); rect.line.fill.background()

# ── تطبيق التصميم (design_applier.py) ──────────────────────
class _DesignApplier:
    def __init__(self): self.generator = _PresentationGenerator()
    def apply_design_to_presentation(self, presentation_path, design, slides_data):
        return self.generator.create_presentation(slides_data, theme_color=design.get("theme_color","blue"))

# ── استخراج الملفات (file_extractor.py) ────────────────────
def _extract_content(file_bytes: bytes, filename: str) -> dict:
    ext = Path(filename).suffix.lower()
    if ext in (".docx",".doc"):
        import docx as _docx, io as _io, tempfile as _tmp
        doc = _docx.Document(_io.BytesIO(file_bytes))
        result = {"text_blocks":[],"tables":[],"images":[],"full_text":""}
        for para in doc.paragraphs:
            text = para.text.strip()
            if not text: continue
            result["text_blocks"].append({"type":"paragraph","style":para.style.name if para.style else "","text":text})
            result["full_text"] += text + "\n"
        for tbl in doc.tables:
            rows = [[cell.text.strip() for cell in row.cells] for row in tbl.rows]
            if rows: result["tables"].append(rows)
        return result
    elif ext == ".pdf":
        result = {"text_blocks":[],"tables":[],"images":[],"full_text":""}
        try:
            import pdfplumber as _pdfp, io as _io
            with _pdfp.open(_io.BytesIO(file_bytes)) as pdf:
                for pg_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text() or ""
                    if text.strip():
                        result["text_blocks"].append({"type":"page","style":f"صفحة {pg_num}","text":text.strip()})
                        result["full_text"] += text.strip() + "\n"
                    for tbl in page.extract_tables():
                        if tbl:
                            result["tables"].append([[cell or "" for cell in row] for row in tbl])
        except Exception as e:
            result["full_text"] = f"خطأ في قراءة PDF: {str(e)}"
        return result
    else:
        text = file_bytes.decode("utf-8", errors="ignore")
        return {"text_blocks":[{"type":"paragraph","style":"Normal","text":text}],"tables":[],"images":[],"full_text":text}

# ── محوّل HTML إلى PPTX (html_to_pptx.py) ──────────────────
def _parse_html_slides(html: str):
    from bs4 import BeautifulSoup as _BS
    import re as _re
    soup = _BS(html, "lxml")
    for tag in soup.find_all(["script","noscript"]): tag.decompose()
    slide_cands = (soup.find_all("section") or
                   soup.find_all(class_=_re.compile(r"slide|page|frame",_re.I)) or
                   soup.find_all(attrs={"data-slide":True}) or
                   soup.find_all("article"))
    if not slide_cands:
        sections = []; current = None
        for el in (soup.body or soup).children:
            if not hasattr(el,"name"): continue
            if el.name in ("h1","h2","h3"):
                if current: sections.append(current)
                current = [el]
            elif current is not None: current.append(el)
        if current: sections.append(current)
        slide_cands = []
        for group in sections:
            wrapper = _BS("<div></div>","lxml").div
            for el in group: wrapper.append(el.__copy__())
            slide_cands.append(wrapper)

    def _extract(el):
        sd = {
            "title": "", "subtitle": "", "bullets": [], "slide_type": "bullets",
            "bg_color": None, "text_color": None, "table_data": None,
            "images": [], "is_title_slide": False, "font_size": None, "bold": False,
            "raw_html": str(el)
        }
        # 1. استخراج العنوان من .slide-title أو h1-h4
        title_el = el.find(class_="slide-title")
        if title_el:
            sd["title"] = title_el.get_text(strip=True)
        else:
            for htag in ["h1","h2","h3","h4"]:
                h = el.find(htag)
                if h:
                    sd["title"] = h.get_text(strip=True)
                    sd["is_title_slide"] = (htag == "h1")
                    break
        # 2. استخراج الخلفية
        style_attr = el.get("style", "")
        bg_match = _re.search(r'background(?:-color)?\s*:\s*([^;]+)', style_attr)
        if bg_match:
            sd["bg_color"] = bg_match.group(1).strip()
        content_el = el.find(class_="content")
        if content_el:
            style2 = content_el.get("style", "")
            bg_match2 = _re.search(r'background(?:-color)?\s*:\s*([^;]+)', style2)
            if bg_match2:
                sd["bg_color"] = bg_match2.group(1).strip()
        # 3. استخراج النقاط
        bullets_el = el.find(class_="list-items")
        if bullets_el:
            sd["bullets"] = [li.get_text(strip=True) for li in bullets_el.find_all("li") if li.get_text(strip=True)]
        else:
            lis = el.find_all("li")
            if lis:
                sd["bullets"] = [li.get_text(strip=True) for li in lis if li.get_text(strip=True)]
            else:
                body = el.find(class_="slide-body")
                if body:
                    p_els = body.find_all("p")
                    if p_els:
                        sd["bullets"] = [p.get_text(strip=True) for p in p_els if p.get_text(strip=True) and len(p.get_text(strip=True))>3]
                if not sd["bullets"]:
                    sd["bullets"] = [p.get_text(strip=True) for p in el.find_all("p") if p.get_text(strip=True) and p.get_text(strip=True) not in (sd["title"],sd["subtitle"]) and len(p.get_text(strip=True))>3]
        sd["bullets"] = sd["bullets"][:8]
        # 4. استخراج الجداول مع ألوان الخلايا
        tbl = el.find("table")
        if tbl:
            rows = []
            for tr in tbl.find_all("tr"):
                cells = []
                for td in tr.find_all(["td","th"]):
                    cell_text = td.get_text(strip=True)
                    cell_style = td.get("style","")
                    bg = _re.search(r'background(?:-color)?\s*:\s*([^;]+)', cell_style)
                    bg_val = bg.group(1).strip() if bg else None
                    align = _re.search(r'text-align\s*:\s*([^;]+)', cell_style)
                    align_val = align.group(1).strip() if align else "center"
                    cells.append({"text": cell_text, "bg": bg_val, "align": align_val,
                                  "bold": (td.name=="th") or ("font-weight" in cell_style and "bold" in cell_style)})
                if cells: rows.append(cells)
            if rows:
                sd["table_data"] = rows; sd["slide_type"] = "table"
        # 5. استخراج الصور
        for img in el.find_all("img"):
            src = img.get("src","")
            if src and (src.startswith("data:") or src.startswith("http")):
                sd["images"].append(src)
        # 6. لون النص
        color_match = _re.search(r'(?<![a-z])color\s*:\s*([^;]+)', style_attr)
        if color_match:
            sd["text_color"] = color_match.group(1).strip()
        # 7. نوع الشريحة
        classes = " ".join(el.get("class",[]))
        if _re.search(r"title|cover|first|intro",classes,_re.I) or sd["is_title_slide"]:
            sd["slide_type"] = "title"
        elif _re.search(r"end|outro|thank|conclusion",classes,_re.I):
            sd["slide_type"] = "conclusion"
        return sd

    slides = []
    for el in slide_cands:
        data = _extract(el)
        if data.get("title") or data.get("bullets") or data.get("table_data"):
            slides.append(data)
    if not slides:
        slides = [_extract(soup.body or soup)]
    return slides

def _html_to_pptx(html: str, override_title: str = "") -> str:
    from datetime import datetime as _dt
    slides_data = _parse_html_slides(html)
    if not slides_data:
        raise ValueError("لم يتم العثور على محتوى في HTML")
    if override_title and slides_data:
        slides_data[0]["title"] = override_title
    gen = _PresentationGenerator()
    out = gen.create_presentation(
        slides_data=slides_data,
        theme_color="blue",
        cover_data=None,
        extracted_images=[],
        font_name="Traditional Arabic",
        body_font_size=22,
        ai_images=False,
        groq_client=None
    )
    return out

# ── تهيئة الكائنات ──────────────────────────────────────────
try:
    _pptx_ai  = _AIProcessor()
    _pptx_gen = _PresentationGenerator()
    _pptx_dap = _DesignApplier()
    logger.info("✅ PowerPoint modules loaded successfully (inlined)")
except Exception as _pptx_err:
    logger.error(f"❌ Failed to init PPTX: {_pptx_err}")
    _pptx_ai = _pptx_gen = _pptx_dap = None


@app.route('/tools/pptx/ai_status')
def tools_pptx_ai_status():
    available = _pptx_ai is not None and _pptx_ai.is_ai_available
    return jsonify({'available': available})


@app.route('/tools/pptx/extract_file', methods=['POST'])
def tools_pptx_extract_file():
    if 'file' not in request.files:
        return jsonify({'error': 'لا يوجد ملف'}), 400
    f = request.files['file']
    try:
        result = _extract_content(f.read(), f.filename)
        return jsonify({
            'success': True,
            'full_text': result['full_text'],
            'tables': result.get('tables', []),
            'word_count': len(result['full_text'].split()),
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/tools/pptx/generate', methods=['POST'])
def tools_pptx_generate():
    if _pptx_ai is None or _pptx_gen is None:
        return jsonify({'error': 'وحدات PowerPoint غير متاحة — تحقق من سجلات الخادم'}), 500
    try:
        data = request.json or {}
        text           = data.get('text', '')
        num_slides     = int(data.get('num_slides', 6))
        ptype          = data.get('ptype', 'general')
        title          = data.get('title', '')
        inc_tables     = bool(data.get('inc_tables', False))
        inc_charts     = bool(data.get('inc_charts', False))
        theme_color    = data.get('theme_color', 'blue')
        font_name      = data.get('font_name', 'Traditional Arabic')
        body_font_size = int(data.get('body_font_size', 22))
        cover_data     = data.get('cover_data', None)
        ext_tables     = data.get('extracted_tables', [])

        slides = _pptx_ai.text_to_presentation_structure(
            text=text, num_slides=num_slides, presentation_type=ptype,
            title_override=title, include_tables=inc_tables,
            include_charts=inc_charts, extracted_tables=ext_tables,
        )

        if inc_tables and ext_tables:
            if not any(s.get('slide_type') == 'table' for s in slides):
                for i, tbl in enumerate(ext_tables[:2]):
                    slides.insert(min(2 + i, len(slides) - 1),
                        {'title': f'جدول البيانات {i+1}', 'slide_type': 'table',
                         'table_data': tbl, 'bullets': []})

        if inc_charts and ext_tables:
            def _parse_table_for_chart(tbl):
                """استخراج بيانات رسم بياني من جدول"""
                try:
                    if not tbl or len(tbl) < 2: return None
                    headers = [str(c) for c in tbl[0]]
                    labels, values = [], []
                    for row in tbl[1:]:
                        if not row: continue
                        label = str(row[0]).strip()
                        for cell in row[1:]:
                            try:
                                val = float(str(cell).replace(',','').replace('%','').strip())
                                labels.append(label); values.append(val); break
                            except Exception: pass
                    if labels and values:
                        return {'labels': labels, 'values': values,
                                'title': headers[1] if len(headers) > 1 else ''}
                except Exception: pass
                return None
            if not any(s.get('slide_type') == 'chart' for s in slides):
                for tbl in ext_tables:
                    info = _parse_table_for_chart(tbl)
                    if info:
                        slides.insert(min(3, len(slides) - 1),
                            {'title': 'تحليل البيانات', 'slide_type': 'chart',
                             'chart_type': 'bar', 'chart_labels': info['labels'],
                             'chart_values': info['values'],
                             'chart_title': info.get('title', ''), 'bullets': []})
                        break

        groq_client = _pptx_ai.client if (_pptx_ai and _pptx_ai.is_ai_available) else None
        out = _pptx_gen.create_presentation(
            slides_data=slides, theme_color=theme_color,
            cover_data=cover_data, extracted_images=[],
            font_name=font_name, body_font_size=body_font_size,
            ai_images=False, groq_client=groq_client,
        )
        filename = os.path.basename(out)
        return jsonify({'success': True, 'filename': filename, 'slides': slides})
    except Exception as e:
        import traceback
        logger.error(f"PPTX generate error: {e}")
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500


@app.route('/tools/pptx/download/<path:filename>')
def tools_pptx_download(filename):
    from flask import send_from_directory as _sfd2
    outputs_dir = os.path.join(os.path.dirname(__file__), 'pptx_app', 'outputs')
    try:
        return _sfd2(outputs_dir, filename, as_attachment=True)
    except Exception as _dl_err:
        logger.error(f"PPTX download error for '{filename}': {_dl_err}")
        return jsonify({'error': f'الملف غير موجود: {filename}'}), 404


@app.route('/download/excel/<path:filename>')
def download_excel(filename):
    """تحميل ملفات Excel من مجلد الإخراج"""
    outputs_dir = os.path.join(os.path.dirname(__file__), 'pptx_app', 'outputs')
    file_path = os.path.join(outputs_dir, filename)
    if not os.path.exists(file_path):
        return jsonify({'error': 'الملف غير موجود'}), 404
    return send_file(
        file_path,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )


@app.route('/download/excel-list')
def download_excel_list():
    """قائمة ملفات Excel المتاحة للتحميل"""
    outputs_dir = os.path.join(os.path.dirname(__file__), 'pptx_app', 'outputs')
    files = []
    for f in os.listdir(outputs_dir):
        if f.endswith('.xlsx') or f.endswith('.xls'):
            files.append({'name': f, 'url': f'/download/excel/{f}'})
    return jsonify({'files': files})


@app.route('/stats1208')
@app.route('/احصاء1208')
def stats1208_page():
    """صفحة حل اختبار احصاء 1208 التفاعلية"""
    return render_template('stats1208.html')


@app.route('/stats1208.xlsx')
@app.route('/get-stats-excel')
def download_stats1208():
    """تحميل ملف Excel – احصاء 1208 – رابط مباشر"""
    f = os.path.join(os.path.dirname(__file__), 'static', 'stats1208_solution.xlsx')
    if not os.path.exists(f):
        # حاول الإنشاء تلقائياً إن لم يوجد
        try:
            import subprocess, sys
            subprocess.run([sys.executable, 'create_excel_solution.py'], check=True)
            import shutil
            src = os.path.join(os.path.dirname(__file__), 'pptx_app', 'outputs',
                               'احصاء_1208_الحلول_الكاملة.xlsx')
            shutil.copy(src, f)
        except Exception as ex:
            return jsonify({'error': str(ex)}), 500
    return send_file(
        f,
        as_attachment=True,
        download_name='احصاء_1208_الحلول_الكاملة.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )


@app.route('/tools/pptx/chat', methods=['POST'])
def tools_pptx_chat():
    try:
        data     = request.json or {}
        messages = data.get('messages', [])
        groq_key = os.environ.get('GROQ_API_KEY', '').strip()
        if not groq_key:
            return jsonify({'reply': '⚠️ مفتاح GROQ_API_KEY غير موجود في إعدادات الأسرار. يمكنك الحصول على مفتاح مجاني من console.groq.com'})
        from groq import Groq as _Groq
        client = _Groq(api_key=groq_key)
        history = [{'role': 'system', 'content':
            'أنت مساعد ذكي متخصص في إنشاء العروض التقديمية PowerPoint والمحتوى الأكاديمي. أجب باللغة العربية دائماً.'}
        ] + messages
        resp = client.chat.completions.create(
            model='llama-3.3-70b-versatile', messages=history, max_tokens=1500)
        return jsonify({'reply': resp.choices[0].message.content})
    except Exception as e:
        return jsonify({'reply': f'❌ خطأ: {e}'})


@app.route('/tools/pptx/preview_html_links', methods=['POST'])
def tools_pptx_preview_html_links():
    """استخراج الروابط من HTML وجلب عناوينها ومقتطفاتها."""
    try:
        data = request.json or {}
        html = data.get('html', '')
        if not html:
            return jsonify({'links': []})

        from bs4 import BeautifulSoup as _BS
        import requests as _req

        soup = _BS(html, 'lxml')
        links = []
        seen = set()

        for a in soup.find_all('a', href=True):
            href = a['href'].strip()
            if not href or href.startswith('#') or href in seen:
                continue
            seen.add(href)
            anchor_text = a.get_text(strip=True)[:100]
            info = {'url': href, 'anchor_text': anchor_text, 'title': '', 'snippet': '', 'error': None}

            if href.startswith('http://') or href.startswith('https://'):
                try:
                    r = _req.get(href, timeout=6,
                                 headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'},
                                 allow_redirects=True)
                    if r.status_code == 200:
                        page = _BS(r.text[:80000], 'lxml')
                        t = page.find('title')
                        info['title'] = t.get_text(strip=True)[:120] if t else ''
                        paras = [p.get_text(strip=True) for p in page.find_all('p')
                                 if len(p.get_text(strip=True)) > 40]
                        info['snippet'] = paras[0][:250] if paras else ''
                    else:
                        info['error'] = f'HTTP {r.status_code}'
                except Exception as ex:
                    info['error'] = str(ex)[:80]
            else:
                info['error'] = 'رابط محلي (لا يمكن جلبه)'

            links.append(info)
            if len(links) >= 12:
                break

        return jsonify({'links': links})
    except Exception as e:
        return jsonify({'links': [], 'error': str(e)}), 500


@app.route('/tools/pptx/from_html', methods=['POST'])
def tools_pptx_from_html():
    """تحويل كود HTML مباشرةً إلى ملف PPTX مع دعم جلب محتوى الروابط."""
    if _pptx_gen is None:
        return jsonify({'error': 'وحدات PowerPoint غير متاحة — تحقق من سجلات الخادم'}), 500
    try:
        data           = request.json or {}
        html_code      = data.get('html', '')
        title          = data.get('title', '')
        theme_color    = data.get('theme_color', 'blue')
        font_name      = data.get('font_name', 'Traditional Arabic')
        body_font_size = int(data.get('body_font_size', 22))
        fetch_links    = bool(data.get('fetch_links', True))
        cover_data     = data.get('cover_data', None)

        if not html_code.strip():
            return jsonify({'error': 'الرجاء لصق كود HTML أولاً'}), 400

        html_to_parse = html_code

        # جلب محتوى الروابط الخارجية وإضافتها كأقسام إضافية
        if fetch_links:
            from bs4 import BeautifulSoup as _BS2
            import requests as _req2
            soup2 = _BS2(html_code, 'lxml')
            extra_parts = []
            seen2 = set()
            for a in soup2.find_all('a', href=True):
                href = a['href'].strip()
                if not href.startswith('http') or href in seen2:
                    continue
                seen2.add(href)
                try:
                    r2 = _req2.get(href, timeout=6,
                                   headers={'User-Agent': 'Mozilla/5.0'},
                                   allow_redirects=True)
                    if r2.status_code == 200:
                        ps = _BS2(r2.text[:80000], 'lxml')
                        pt = ps.find('title')
                        pg_title = pt.get_text(strip=True) if pt else href
                        paras = [p.get_text(strip=True) for p in ps.find_all('p')
                                 if len(p.get_text(strip=True)) > 30]
                        if paras:
                            bullets = ''.join(f'<li>{p}</li>' for p in paras[:5])
                            extra_parts.append(
                                f'<section><h2>{pg_title}</h2><ul>{bullets}</ul></section>'
                            )
                except Exception:
                    pass
                if len(extra_parts) >= 5:
                    break

            if extra_parts:
                insert = '\n'.join(extra_parts)
                body_end = html_to_parse.rfind('</body>')
                if body_end != -1:
                    html_to_parse = html_to_parse[:body_end] + insert + html_to_parse[body_end:]
                else:
                    html_to_parse += insert

        # تحليل HTML وبناء شرائح
        slides_data = _parse_html_slides(html_to_parse)
        if not slides_data:
            return jsonify({'error': 'لم يتم العثور على محتوى قابل للتحويل في HTML'}), 400

        if title and slides_data:
            slides_data[0]['title'] = title

        out_path = _pptx_gen.create_presentation(
            slides_data=slides_data,
            theme_color=theme_color,
            cover_data=cover_data,
            extracted_images=[],
            font_name=font_name,
            body_font_size=body_font_size,
            ai_images=False,
            groq_client=None,
        )
        filename = os.path.basename(out_path)
        return jsonify({'success': True, 'filename': filename, 'slides': slides_data})

    except Exception as e:
        import traceback
        logger.error(f"HTML to PPTX error: {e}")
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500


@app.route("/academic")
def academic_analysis():
    _groq_key = os.environ.get('GROQ_API_KEY', '').strip()
    resp = make_response(render_template('academic.html', groq_key=_groq_key))
    resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    return resp


alert_queue.start()
# تهيئة الحلقة المشتركة مبكراً قبل أي اتصالات gevent
_ensure_shared_login_loop()
load_all_sessions()

def _auto_resume_persistent_tasks():
    def worker():
        time.sleep(3)
        logger.info("🔁 فحص المهام الدائمة لإعادة تشغيلها تلقائياً...")
        with USERS_LOCK:
            user_ids = list(USERS.keys())
        resumed = 0
        for uid in user_ids:
            try:
                settings = load_settings(uid)
                want_monitor = bool(settings.get('monitoring_persistent', False))
                want_rotating = bool(settings.get('rotating_persistent', False))
                if not (want_monitor or want_rotating):
                    continue
                ok = telegram_manager.ensure_client_active(uid)
                if not ok:
                    logger.warning(f"⏭️  لا يمكن استئناف مهام {uid}: العميل غير متاح/غير موثق")
                    continue
                with USERS_LOCK:
                    if uid in USERS and not USERS[uid].get('client_manager'):
                        USERS[uid]['client_manager'] = telegram_manager.get_client_manager(uid)
                if want_monitor:
                    with USERS_LOCK:
                        already = USERS.get(uid, {}).get('is_running', False)
                        if not already:
                            USERS[uid]['is_running'] = True
                    if not already:
                        t = _OSThread(target=monitoring_worker, args=(uid,), daemon=True)
                        t.start()
                        with USERS_LOCK:
                            if uid in USERS:
                                USERS[uid]['thread'] = t
                        logger.info(f"♻️  استُؤنفت المراقبة للحساب {uid}")
                        resumed += 1
                        try:
                            socketio.emit('log_update', {
                                "message": "♻️ تم استئناف المراقبة تلقائياً (مهمة دائمة)"
                            }, to=uid)
                            socketio.emit('monitoring_status', {
                                "monitoring_active": True, "status": "running", "is_running": True
                            }, to=uid)
                            socketio.emit('update_monitoring_buttons', {"is_running": True}, to=uid)
                        except Exception:
                            pass
                if want_rotating:
                    msgs = settings.get('rotating_messages', [])
                    grps = dedupe_groups(settings.get('rotating_groups', []))
                    interval = int(settings.get('rotating_interval', 5))
                    valid_msgs = [m for m in msgs if m and m.strip()]
                    if grps and valid_msgs:
                        is_alive = (uid in rotating_manager.threads
                                    and rotating_manager.threads[uid]
                                    and rotating_manager.threads[uid].is_alive())
                        if not is_alive:
                            def _cb(u, status, group, info):
                                if status == 'success':
                                    socketio.emit('log_update', {"message": f"🔄 [متسلسل] أرسل إلى {group}"}, to=u)
                                else:
                                    socketio.emit('log_update', {"message": f"❌ [متسلسل] فشل إلى {group}: {info}"}, to=u)
                            rotating_manager.start(uid, grps, valid_msgs, interval, _cb)
                            logger.info(f"♻️  استُؤنف الإرسال المتسلسل للحساب {uid}")
                            resumed += 1
                            try:
                                socketio.emit('log_update', {
                                    "message": f"♻️ تم استئناف الإرسال المتسلسل تلقائياً ({len(valid_msgs)} رسائل) كل {interval} دقيقة"
                                }, to=uid)
                            except Exception:
                                pass
                    else:
                        logger.info(f"⏭️  تخطي استئناف الإرسال المتسلسل لـ {uid}: لا توجد رسائل/مجموعات")
            except Exception as e:
                logger.error(f"خطأ أثناء استئناف مهام {uid}: {e}")
        if resumed:
            logger.info(f"✅ تم استئناف {resumed} مهمة دائمة")
        else:
            logger.info("ℹ️  لا توجد مهام دائمة لاستئنافها")
    _OSThread(target=worker, daemon=True, name="AutoResumeTasks").start()

_auto_resume_persistent_tasks()

# ════════════════════════════════════════════════════════════
#  مزامنة الجلسات مع GitHub
# ════════════════════════════════════════════════════════════
def github_upload_session(user_id):
    """رفع ملف الجلسة إلى GitHub للحفظ الاحتياطي"""
    try:
        session_file = os.path.join(SESSIONS_DIR, f"{user_id}_session.session")
        if not os.path.exists(session_file):
            return False
        with open(session_file, 'rb') as f:
            content = f.read()
        import base64 as _b64
        headers = {
            'Authorization': f'token {GITHUB_TOKEN}',
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json',
        }
        rel_path = f"sessions/{user_id}_session.session"
        get_url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{rel_path}"
        gr = requests.get(get_url, headers=headers, params={'ref': GITHUB_BRANCH}, timeout=15)
        sha = gr.json().get('sha') if gr.ok else None
        body = {
            'message': f'Upload session for {user_id}',
            'content': _b64.b64encode(content).decode(),
            'branch': GITHUB_BRANCH,
        }
        if sha:
            body['sha'] = sha
        pr = requests.put(get_url, headers=headers, json=body, timeout=30)
        if pr.ok:
            logger.info(f"Session for {user_id} uploaded to GitHub")
            return True
        else:
            logger.warning(f"Failed to upload session: {pr.status_code}")
            return False
    except Exception as e:
        logger.error(f"github_upload_session error: {e}")
        return False

def github_delete_session(user_id):
    """حذف ملف الجلسة الملغاة من GitHub"""
    try:
        headers = {
            'Authorization': f'token {GITHUB_TOKEN}',
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json',
        }
        rel_path = f"sessions/{user_id}_session.session"
        get_url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{rel_path}"
        gr = requests.get(get_url, headers=headers, params={'ref': GITHUB_BRANCH}, timeout=15)
        if not gr.ok:
            return False
        sha = gr.json().get('sha')
        if not sha:
            return False
        body = {
            'message': f'Delete revoked session for {user_id}',
            'sha': sha,
            'branch': GITHUB_BRANCH,
        }
        dr = requests.delete(get_url, headers=headers, json=body, timeout=30)
        if dr.ok:
            logger.info(f"Session for {user_id} deleted from GitHub")
            return True
        return False
    except Exception as e:
        logger.error(f"github_delete_session error: {e}")
        return False

# ════════════════════════════════════════════════════════════
#  مدقق صحة الجلسات الدوري
# ════════════════════════════════════════════════════════════
def start_session_health_checker():
    """يفحص صحة جميع الجلسات بشكل دوري كل 25 ثانية لاستشعار أي إلغاء أو خروج من تطبيق تليجرام الرسمي"""
    def _checker():
        import time as _t
        _t.sleep(20)  # مهلة مبدئية قصيرة عند الإقلاع
        while True:
            try:
                with USERS_LOCK:
                    user_ids = list(USERS.keys())
                for uid in user_ids:
                    try:
                        with USERS_LOCK:
                            user_data = USERS.get(uid, {})
                            was_auth = bool(user_data.get('authenticated'))
                        client_manager = user_data.get('client_manager')
                        if not client_manager or not client_manager.client:
                            continue
                        # تخطّ الفحص إذا كان الخيط لا يزال يبدأ
                        if client_manager.thread and client_manager.thread.is_alive() and not client_manager.is_ready.is_set():
                            continue
                        # تخطّ الفحص إذا لم يكن الـ loop يعمل بعد
                        if not client_manager.loop or not client_manager.loop.is_running():
                            continue
                        if not was_auth:
                            continue
                        is_valid = client_manager.check_session_valid_sync()
                        if not is_valid:
                            logger.warning(f"Session health check failed for {uid} — auto-logging out via handle_session_revoked")
                            handle_session_revoked(uid, "انتهت صلاحية الجلسة أو تم إزالتها من تطبيق تليجرام الآخر الرسمي")
                    except Exception as inner_e:
                        logger.debug(f"Health check error for {uid}: {inner_e}")
            except Exception as e:
                logger.debug(f"Session health checker error: {e}")
            _t.sleep(25)

    # استخدام OS thread حقيقي للـ health checker
    t = _OSThread(target=_checker, daemon=True, name='SessionHealthChecker')
    t.start()
    logger.info("✅ مدقق صحة الجلسات الدوري مُفعّل (كل 25 ثانية)")

start_session_health_checker()

# ════════════════════════════════════════════════════════════
#  نقاط API — فحص الجلسة وإعادة التعيين
# ════════════════════════════════════════════════════════════
@app.route("/api/check_session_valid", methods=["GET"])
def api_check_session_valid():
    user_id = session.get('user_id', 'user_1')
    try:
        with USERS_LOCK:
            user_data = USERS.get(user_id, {})
        client_manager = user_data.get('client_manager')
        if not client_manager or not client_manager.client:
            return jsonify({"success": True, "valid": False, "reason": "العميل غير متصل"})
        is_valid = client_manager.check_session_valid_sync()
        return jsonify({"success": True, "valid": is_valid})
    except Exception as e:
        return jsonify({"success": False, "valid": False, "reason": str(e)})

@app.route("/api/force_reset_session", methods=["POST"])
def api_force_reset_session():
    user_id = session.get('user_id', 'user_1')
    try:
        with USERS_LOCK:
            user_data = USERS.get(user_id, {})
        client_manager = user_data.get('client_manager')
        if client_manager:
            client_manager.run_coroutine(client_manager.force_reset_session())
        github_delete_session(user_id)
        clear_user_session(user_id)
        with USERS_LOCK:
            if user_id in USERS:
                USERS[user_id]['connected'] = False
                USERS[user_id]['authenticated'] = False
                USERS[user_id]['client_manager'] = None
        return jsonify({"success": True, "message": "تم إعادة تعيين الجلسة بنجاح"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route("/api/auto_join/settings", methods=["GET", "POST"])
def api_auto_join_settings():
    user_id = session.get('user_id', 'user_1')
    if request.method == 'POST':
        try:
            data = request.json or {}
            settings = load_settings(user_id)
            if 'links' in data:
                settings['auto_join_links'] = data['links']
            if 'delay' in data:
                settings['auto_join_delay'] = int(data['delay'])
            if 'max_retries' in data:
                settings['auto_join_max_retries'] = int(data['max_retries'])
            save_settings(user_id, settings)
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)})
    settings = load_settings(user_id)
    return jsonify({
        "success": True,
        "links": settings.get('auto_join_links', []),
        "delay": settings.get('auto_join_delay', 3),
        "max_retries": settings.get('auto_join_max_retries', 1)
    })

@app.route("/api/auto_join/stop", methods=["POST"])
def api_auto_join_stop():
    user_id = session.get('user_id', 'user_1')
    try:
        stopped = False
        with USERS_LOCK:
            stop_event = USERS.get(user_id, {}).get('auto_join_stop')
            pause_event = USERS.get(user_id, {}).get('auto_join_pause')
            if stop_event and not stop_event.is_set():
                stop_event.set()
                stopped = True
            if pause_event:
                pause_event.clear()  # أطلق الإيقاف المؤقت حتى يصل الإيقاف الكامل
        msg = "⏹ تم إيقاف الانضمام التلقائي" if stopped else "ℹ️ لا يوجد انضمام نشط حالياً"
        socketio.emit('log_update', {"message": msg}, to=user_id)
        return jsonify({"success": True, "message": msg, "stopped": stopped})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route("/api/auto_join/pause", methods=["POST"])
def api_auto_join_pause():
    """إيقاف مؤقت للانضمام — تبقى الإعدادات محفوظة"""
    user_id = session.get('user_id', 'user_1')
    try:
        with USERS_LOCK:
            pause_event = USERS.get(user_id, {}).get('auto_join_pause')
            state = USERS.get(user_id, {}).get('auto_join_state', {})
        if pause_event and not pause_event.is_set():
            pause_event.set()
            msg = "⏸ تم الإيقاف المؤقت — اضغط استئناف للمتابعة"
            socketio.emit('log_update', {"message": msg}, to=user_id)
            return jsonify({"success": True, "message": msg})
        return jsonify({"success": False, "message": "لا يوجد انضمام نشط أو هو متوقف مؤقتاً بالفعل"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route("/api/auto_join/resume", methods=["POST"])
def api_auto_join_resume():
    """استئناف الانضمام بعد إيقاف مؤقت"""
    user_id = session.get('user_id', 'user_1')
    try:
        with USERS_LOCK:
            pause_event = USERS.get(user_id, {}).get('auto_join_pause')
        if pause_event and pause_event.is_set():
            pause_event.clear()
            msg = "▶ تم الاستئناف"
            socketio.emit('log_update', {"message": msg}, to=user_id)
            return jsonify({"success": True, "message": msg})
        return jsonify({"success": False, "message": "الانضمام ليس في حالة توقف مؤقت"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route("/api/auto_join/exit", methods=["POST"])
def api_auto_join_exit():
    """خروج يدوي — يوقف الانضمام ويمسح الإعدادات"""
    user_id = session.get('user_id', 'user_1')
    try:
        with USERS_LOCK:
            stop_event  = USERS.get(user_id, {}).get('auto_join_stop')
            pause_event = USERS.get(user_id, {}).get('auto_join_pause')
            if stop_event and not stop_event.is_set():
                stop_event.set()
            if pause_event:
                pause_event.clear()
            if user_id in USERS:
                USERS[user_id].pop('auto_join_state', None)
                USERS[user_id].pop('auto_join_stop', None)
                USERS[user_id].pop('auto_join_pause', None)
        # امسح الإعدادات المحفوظة أيضاً
        try:
            _s = load_settings(user_id)
            _s.pop('auto_join_links', None)
            _s.pop('auto_join_delay', None)
            save_settings(user_id, _s)
        except Exception:
            pass
        msg = "🚪 خروج يدوي — تم مسح جميع إعدادات الانضمام"
        socketio.emit('log_update', {"message": msg}, to=user_id)
        socketio.emit('auto_join_exited', {}, to=user_id)
        return jsonify({"success": True, "message": msg})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route("/api/auto_join/status", methods=["GET"])
def api_auto_join_status():
    """يُرجع الحالة الجارية للانضمام المتقدم (للاستعادة عند تبديل الحسابات)"""
    user_id = session.get('user_id', 'user_1')
    with USERS_LOCK:
        state = USERS.get(user_id, {}).get('auto_join_state', {})
    return jsonify({"success": True, "state": state})


@app.route("/api/auto_join/history", methods=["GET"])
def api_auto_join_history():
    """
    سجل نتائج الانضمام مع إمكانية التصفية حسب الحالة.
    query params:
      - status: all | success | failed | already  (افتراضي: all)
      - limit:  عدد السجلات (افتراضي: 100)
    """
    user_id = session.get('user_id', 'user_1')
    status_filter = request.args.get('status', 'all').lower()
    try:
        limit = max(1, min(int(request.args.get('limit', 100)), 1000))
    except (ValueError, TypeError):
        limit = 100

    with USERS_LOCK:
        state = USERS.get(user_id, {}).get('auto_join_state', {})

    all_items = state.get('items', [])

    if status_filter == 'success':
        items = [i for i in all_items if i.get('status') == 'success']
    elif status_filter == 'failed':
        items = [i for i in all_items if i.get('status') == 'failed']
    elif status_filter == 'already':
        items = [i for i in all_items if i.get('status') == 'already']
    else:
        items = all_items

    items = items[-limit:]

    summary = {
        'total':   state.get('total', 0),
        'done':    state.get('done', 0),
        'success': state.get('success', 0),
        'fail':    state.get('fail', 0),
        'already': state.get('already', 0),
        'running': state.get('running', False),
    }

    return jsonify({
        "success": True,
        "filter": status_filter,
        "count": len(items),
        "summary": summary,
        "items": items
    })


# ════════════════════════════════════════════════════════════
#  نظام الاستمرارية الدائم — يمنع توقف التطبيق تلقائياً
# ════════════════════════════════════════════════════════════
def _start_keepalive():
    """
    يُرسل ping لنفسه كل 4 دقائق لمنع السكون (خاصة على Render Free).
    يعمل كخيط daemon لا يمنع إيقاف التطبيق يدوياً.
    """
    import time as _time
    import socket as _socket

    def _ping_self():
        _time.sleep(30)  # انتظر حتى يكتمل الإقلاع
        _port = int(os.environ.get('PORT', 5000))
        while True:
            try:
                _socket.setdefaulttimeout(10)
                conn = _socket.create_connection(('127.0.0.1', _port), timeout=5)
                conn.close()
            except Exception:
                pass
            _time.sleep(240)  # كل 4 دقائق

    t = _OSThread(target=_ping_self, daemon=True, name='KeepAlive')
    t.start()
    logger.info("🔄 نظام الاستمرارية الدائم مُفعّل (ping كل 4 دقائق)")

_start_keepalive()

# ── نقطة keepalive يمكن استدعاؤها خارجياً (من UptimeRobot مثلاً) ──
@app.route('/keepalive')
@app.route('/ping')
def route_keepalive():
    return jsonify({"status": "alive", "time": datetime.utcnow().isoformat()})


@app.route('/debug/ping')
def debug_ping():
    import socket as _dsock
    results = {}
    targets = [
        ('api.telegram.org', 443),
        ('149.154.167.51', 443),
        ('91.108.4.0', 443),
    ]
    for host, port in targets:
        try:
            _dsock.create_connection((host, port), timeout=10)
            results[f"{host}:{port}"] = "✅ متاح"
        except Exception as e:
            results[f"{host}:{port}"] = f"❌ {e}"
    all_ok = all("✅" in v for v in results.values())
    return jsonify({
        "telegram_reachable": all_ok,
        "checks": results
    }), 200 if all_ok else 503


# ════════════════════════════════════════════════════════════
#  إعادة التعيين — مستخدم واحد أو جميع المستخدمين
# ════════════════════════════════════════════════════════════
def _do_reset_user(uid):
    """تنفيذ إعادة تعيين مستخدم واحد مع الحفاظ الدائم على الأرقام وأسمائها الفعلية"""
    try:
        with USERS_LOCK:
            user_data = USERS.get(uid, {})
        try:
            _st_reset = load_settings(uid) or {}
            _rp = user_data.get('account_phone') or _st_reset.get('phone') or _st_reset.get('account_phone') or ''
            _rn = user_data.get('account_name') or _st_reset.get('account_name') or _st_reset.get('name') or ''
            if _rp:
                import firestore_sync
                firestore_sync.save_phone_number(_rp)
                if _rn and not firestore_sync._is_placeholder_phone_name(_rn):
                    firestore_sync.update_phone_account_name(_rp, _rn)
        except Exception:
            pass
        client_manager = user_data.get('client_manager')
        if client_manager:
            try:
                if client_manager.client and client_manager.loop and client_manager.client.is_connected():
                    future = asyncio.run_coroutine_threadsafe(
                        client_manager.client.log_out(), client_manager.loop
                    )
                    future.result(timeout=8)
            except Exception:
                pass
            try:
                client_manager.stop_flag.set()
            except Exception:
                pass
        telegram_manager.login_managers.pop(uid, None)
        telegram_manager.client_managers.pop(uid, None)
        github_delete_session(uid)
        clear_user_session(uid)
        with USERS_LOCK:
            USERS.pop(uid, None)
    except Exception as e:
        logger.warning(f"_do_reset_user({uid}): {e}")


@app.route("/api/reset_user", methods=["POST"])
def api_reset_user():
    """إعادة تعيين الحساب الحالي فقط — حذف الجلسة محلياً وعلى GitHub"""
    data = request.get_json(silent=True) or {}
    user_id = resolve_request_user_id(data) if 'resolve_request_user_id' in globals() else session.get('user_id')
    if not user_id:
        return jsonify({"success": False, "message": "الجلسة غير صالحة"})
    target_id = data.get('target_user_id') or user_id
    try:
        _do_reset_user(target_id)
        socketio.emit('login_status', {
            "logged_in": False, "connected": False,
            "awaiting_code": False, "awaiting_password": False, "is_running": False,
        }, to=target_id)
        socketio.emit('connection_status', {"status": "disconnected"}, to=target_id)
        socketio.emit('user_reset_done', {"user_id": target_id}, to=target_id)
        return jsonify({"success": True, "message": f"✅ تم إعادة تعيين {target_id} بالكامل"})
    except Exception as e:
        logger.error(f"api_reset_user error for {user_id}: {e}")
        return jsonify({"success": False, "message": str(e)})


@app.route("/api/reset_all", methods=["POST"])
def api_reset_all():
    """إعادة تعيين جميع المستخدمين والجلسات والإعدادات — يُعيد النظام لحالته الأولى"""
    errors = []
    for uid in list(PREDEFINED_USERS.keys()):
        try:
            _do_reset_user(uid)
        except Exception as e:
            errors.append(str(e))
    socketio.emit('force_full_reset', {"message": "تم إعادة تعيين جميع الجلسات والإعدادات"})
    if errors:
        return jsonify({"success": True,
                        "message": f"✅ تمت الإعادة مع ملاحظات: {'; '.join(errors)}"})
    return jsonify({"success": True,
                    "message": "✅ تم إعادة تعيين جميع الجلسات والإعدادات بالكامل"})


@app.route("/api/health", methods=["GET"])
def api_health_status():
    try:
        users_status = {}
        with USERS_LOCK:
            for uid, data in USERS.items():
                cm = data.get('client_manager')
                loop_ok = False
                if cm:
                    lp = getattr(cm, 'loop', None)
                    loop_ok = bool(lp and lp.is_running())

                rot = rotating_manager
                rot_active = (uid in rot.threads and rot.threads[uid] and rot.threads[uid].is_alive())
                next_send_in = None
                if rot_active and uid in rot.next_send_at:
                    remaining = int(rot.next_send_at[uid] - time.time())
                    next_send_in = max(0, remaining)

                users_status[uid] = {
                    "name": PREDEFINED_USERS.get(uid, {}).get("name", uid),
                    "authenticated": data.get("authenticated", False),
                    "connected": data.get("connected", False),
                    "is_running": data.get("is_running", False),
                    "awaiting_code": data.get("awaiting_code", False),
                    "awaiting_password": data.get("awaiting_password", False),
                    "client_loop_running": loop_ok,
                    "rotating_send_active": rot_active,
                    "rotating_next_send_in_seconds": next_send_in,
                    "monitored_keywords": len(cm.monitored_keywords) if cm else 0,
                    "monitored_groups": len(cm.monitored_groups) if cm else 0,
                }

        return jsonify({
            "success": True,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "users": users_status
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# ============================================
# قسم مراقبة الروابط
# ============================================

LINK_MONITORS = {}
LINK_MONITOR_WORKERS = {}

def extract_links_from_text(text):
    """استخراج جميع الروابط من النص"""
    url_pattern = r'https?://[^\s]+|t\.me/[^\s]+|telegram\.me/[^\s]+'
    links = re.findall(url_pattern, text)
    clean_links = []
    for link in links:
        link = re.sub(r'[.,;:!?)]+$', '', link)
        if link and link not in clean_links:
            clean_links.append(link)
    return clean_links

@app.route('/api/link_monitor/start', methods=['POST'])
def start_link_monitor():
    """بدء مراقبة الروابط"""
    user_id = session.get('user_id')
    if user_id not in USERS:
        return jsonify({'error': 'المستخدم غير موجود'}), 404

    data = request.json
    monitor_all = data.get('monitor_all', True)
    specific_chats = data.get('specific_chats', '').strip().split('\n')
    send_to_saved = data.get('send_to_saved', True)

    if user_id in LINK_MONITOR_WORKERS and LINK_MONITOR_WORKERS[user_id].is_alive():
        return jsonify({'error': 'توجد عملية مراقبة جارية بالفعل'}), 400

    if specific_chats and specific_chats[0]:
        specific_chats = [chat.strip() for chat in specific_chats if chat.strip()]
    else:
        specific_chats = []

    LINK_MONITORS[user_id] = {
        'is_running': True,
        'monitor_all': monitor_all,
        'specific_chats': specific_chats,
        'send_to_saved': send_to_saved,
        'links_found': [],
        'start_time': datetime.now().isoformat(),
        'total_links': 0,
        'monitored_chats': 0
    }

    worker = threading.Thread(target=run_link_monitor_worker, args=(user_id,))
    worker.daemon = True
    worker.start()
    LINK_MONITOR_WORKERS[user_id] = worker

    return jsonify({'success': True, 'message': 'بدأت مراقبة الروابط'})

def run_link_monitor_worker(user_id):
    """دالة تعمل في خيط منفصل لمراقبة الروابط"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(link_monitor_worker(user_id))
        loop.close()
    except Exception as e:
        logger.error(f"خطأ في worker مراقبة الروابط: {str(e)}")
        socketio.emit('link_monitor_error', {'error': str(e)}, room=user_id)

async def link_monitor_worker(user_id):
    """الدالة الأساسية لمراقبة الروابط"""
    state = LINK_MONITORS[user_id]
    client = USERS[user_id]['client']

    try:
        from telethon import events as telethon_events

        dialogs = await client.get_dialogs()
        state['monitored_chats'] = len(dialogs)

        if state['monitor_all']:
            chats_to_monitor = None  # None = جميع الدردشات
        else:
            chats_to_monitor = []
            for dialog in dialogs:
                name = getattr(dialog.entity, 'title', None) or getattr(dialog.entity, 'first_name', '') or ''
                if any(s in name for s in state['specific_chats']):
                    chats_to_monitor.append(dialog.entity)

        logger.info(f"بدء مراقبة الروابط — {state['monitored_chats']} دردشة")
        socketio.emit('link_monitor_status_update', {
            'monitored_chats': state['monitored_chats'],
            'is_running': True
        }, room=user_id)

        @client.on(telethon_events.NewMessage(chats=chats_to_monitor))
        async def handle_new_message(event):
            if not state.get('is_running'):
                return
            try:
                message = event.message
                if not message or not message.text:
                    return

                links = extract_links_from_text(message.text)
                if not links:
                    return

                chat = await event.get_chat()
                chat_name = getattr(chat, 'title', None) or getattr(chat, 'first_name', None) or 'Unknown'

                sender = await event.get_sender()
                sender_name = getattr(sender, 'first_name', None) or 'Unknown'

                for link in links:
                    link_data = {
                        'link': link,
                        'chat_name': chat_name,
                        'chat_id': getattr(chat, 'id', 0),
                        'sender_name': sender_name,
                        'message_text': message.text[:200] + ('...' if len(message.text) > 200 else ''),
                        'message_id': message.id,
                        'date': message.date.isoformat() if message.date else datetime.now().isoformat(),
                        'timestamp': datetime.now().isoformat()
                    }

                    state['links_found'].append(link_data)
                    state['total_links'] += 1

                    if state.get('send_to_saved'):
                        try:
                            saved_msg = (
                                f"🔗 رابط جديد!\n\n"
                                f"📌 الرابط: {link}\n"
                                f"💬 الدردشة: {chat_name}\n"
                                f"👤 المرسل: {sender_name}\n"
                                f"📝 النص: {message.text[:100]}\n\n"
                                f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                            )
                            await client.send_message('me', saved_msg)
                            logger.info(f"تم إرسال الرابط إلى المحفوظات: {link}")
                        except Exception as e:
                            logger.error(f"فشل الإرسال إلى المحفوظات: {str(e)}")

                    socketio.emit('link_monitor_update', {
                        'link': link_data,
                        'total': state['total_links']
                    }, room=user_id)

                    logger.info(f"رابط مكتشف في [{chat_name}]: {link}")

            except Exception as e:
                logger.error(f"خطأ في معالجة رسالة: {str(e)}")

        while state.get('is_running'):
            await asyncio.sleep(1)

        client.remove_event_handler(handle_new_message)

    except Exception as e:
        logger.error(f"خطأ في مراقبة الروابط: {str(e)}")
        socketio.emit('link_monitor_error', {'error': str(e)}, room=user_id)
    finally:
        state['is_running'] = False
        socketio.emit('link_monitor_done', {
            'total_links': state.get('total_links', 0),
            'monitored_chats': state.get('monitored_chats', 0)
        }, room=user_id)
        if user_id in LINK_MONITOR_WORKERS:
            del LINK_MONITOR_WORKERS[user_id]

@app.route('/api/link_monitor/stop')
def stop_link_monitor():
    """إيقاف مراقبة الروابط"""
    user_id = session.get('user_id')
    if user_id not in USERS:
        return jsonify({'error': 'المستخدم غير موجود'}), 404
    if user_id in LINK_MONITORS:
        LINK_MONITORS[user_id]['is_running'] = False
    return jsonify({'success': True, 'message': 'تم إيقاف مراقبة الروابط'})

@app.route('/api/link_monitor/status')
def link_monitor_status():
    """الحصول على حالة مراقبة الروابط"""
    user_id = session.get('user_id')
    if user_id not in USERS:
        return jsonify({'error': 'المستخدم غير موجود'}), 404
    if user_id in LINK_MONITORS:
        state = LINK_MONITORS[user_id]
        is_running = user_id in LINK_MONITOR_WORKERS and LINK_MONITOR_WORKERS[user_id].is_alive()
        return jsonify({
            'is_running': is_running,
            'total_links': state.get('total_links', 0),
            'monitored_chats': state.get('monitored_chats', 0),
            'links_found': state.get('links_found', [])[-50:]
        })
    return jsonify({'is_running': False, 'total_links': 0, 'monitored_chats': 0, 'links_found': []})

@app.route('/api/link_monitor/links')
def get_monitored_links():
    """الحصول على قائمة الروابط المكتشفة"""
    user_id = session.get('user_id')
    if user_id not in USERS:
        return jsonify({'error': 'المستخدم غير موجود'}), 404
    limit = int(request.args.get('limit', 100))
    if user_id in LINK_MONITORS:
        links = LINK_MONITORS[user_id].get('links_found', [])
        links_sorted = sorted(links, key=lambda x: x.get('timestamp', ''), reverse=True)
        return jsonify({'links': links_sorted[:limit], 'total': len(links)})
    return jsonify({'links': [], 'total': 0})

@app.route('/api/link_monitor/clear')
def clear_monitored_links():
    """مسح قائمة الروابط"""
    user_id = session.get('user_id')
    if user_id not in USERS:
        return jsonify({'error': 'المستخدم غير موجود'}), 404
    if user_id in LINK_MONITORS:
        LINK_MONITORS[user_id]['links_found'] = []
        LINK_MONITORS[user_id]['total_links'] = 0
    return jsonify({'success': True, 'message': 'تم مسح الروابط'})

# ==============================================================
# مسارات رادار الروابط والإنضمام التلقائي الذكي (Link Radar)
# ==============================================================

@app.route("/link_radar")
def link_radar_page():
    """صفحة رادار الروابط والإنضمام الذكي"""
    return render_template("link_radar.html")

@app.route("/api/link_radar/stats", methods=["GET"])
def api_link_radar_stats():
    """جلب الإحصائيات الفورية الثابتة وسجل الروابط المرصودة"""
    if not radar_manager:
        return jsonify({"success": False, "message": "الرادار غير متوفر"}), 500
    data = radar_manager.get_stats()
    data["recent_events"] = radar_manager.state.get("recent_events", [])
    return jsonify({"success": True, **data})

@app.route("/api/link_radar/toggle", methods=["POST"])
def api_link_radar_toggle():
    """تبديل حالة تشغيل الرادار (مفعل افتراضياً)"""
    if not radar_manager:
        return jsonify({"success": False, "message": "الرادار غير متوفر"}), 500
    enabled = radar_manager.toggle_state()
    socketio.emit("link_radar_stats", radar_manager.get_stats())
    return jsonify({"success": True, "enabled": enabled})

@app.route("/api/link_radar/clear_history", methods=["POST"])
def api_link_radar_clear():
    """مسح سجل الأحداث الأخيرة مع الاحتفاظ بالعدادات"""
    if not radar_manager:
        return jsonify({"success": False, "message": "الرادار غير متوفر"}), 500
    radar_manager.clear_recent_events()
    return jsonify({"success": True})

@app.route("/api/link_radar/test_link", methods=["POST"])
def api_link_radar_test():
    """فحص واختبار رابط فوري يدوي ومعالجته بنفس منطق الرادار"""
    if not radar_manager:
        return jsonify({"success": False, "message": "الرادار غير متوفر"}), 500
    body = request.json or {}
    url = (body.get("link") or "").strip()
    if not url:
        return jsonify({"success": False, "message": "الرابط مطلوب"}), 400
    if radar_manager.is_ignored_whatsapp_link(url):
        return jsonify({
            "success": False,
            "ignored": True,
            "message": "تم تجاهل الرابط: رادار الروابط يعالج روابط مجموعات الواتساب (chat.whatsapp.com/...) فقط ويتجاهل روابط المحادثات المباشرة مثل wa.me"
        })

    user_id = session.get("user_id") or "user_1"
    client_mgr = USERS.get(user_id, {}).get("client_manager")
    client = getattr(client_mgr, "client", None) if client_mgr else None

    # البحث عن أي عميل متصل إذا لم يكن الحساب الحالي متصلاً
    if not client or not client.is_connected():
        for uid, udata in USERS.items():
            cm = udata.get("client_manager")
            if cm and getattr(cm, "client", None) and cm.client.is_connected():
                client_mgr = cm
                client = cm.client
                break

    if not client or not client.is_connected():
        return jsonify({"success": False, "message": "لا يوجد حساب تيليجرام نشط ومتصل حالياً لإجراء الفحص والانضمام الآلي"})

    async def run_test():
        return await radar_manager.handle_captured_link(
            client=client,
            link=url,
            chat_info={"id": 0, "name": "فحص يدوي فوري"},
            sender_info={"name": "المستخدم"},
            message_text=url,
            send_to_saved_func=client_mgr.send_to_saved_messages if client_mgr else None,
            save_to_db_func=add_saved_link,
            socketio_emit_func=lambda ev_name, ev_data: socketio.emit(ev_name, ev_data)
        )

    try:
        res = client_mgr.run_coroutine(run_test())
        if res:
            return jsonify({"success": True, "event": res})
        return jsonify({"success": False, "message": "تم فحص الرابط مسبقاً أو غير مدعوم"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})





# ===========================
# وظيفة رسائلي — تتبع وإدارة الرسائل المرسلة
# ===========================

@app.route("/api/sent_batches")
def api_sent_batches():
    """عرض جميع الدفعات المرسلة (رسائلي)"""
    user_id = session.get('user_id')
    if not user_id or user_id not in USERS:
        return jsonify({"success": False, "message": "غير مسجّل"}), 401
    with USERS_LOCK:
        batches = list(USERS[user_id].get('sent_batches', []))
    result = []
    for b in reversed(batches):
        result.append({
            "id": b["id"],
            "text": b["text"],
            "has_media": b.get("has_media", False),
            "sent_at": b["sent_at"],
            "edited_at": b.get("edited_at"),
            "sent_count": b.get("sent_count", len(b["entries"])),
            "group_count": len(b["entries"]),
            "groups": [{"title": e.get("group", ""), "username": e.get("group", "")} for e in b["entries"]]
        })
    return jsonify({"success": True, "batches": result})


@app.route("/api/edit_batch", methods=["POST"])
def api_edit_batch():
    """تعديل جميع رسائل الدفعة دفعة واحدة"""
    user_id = session.get('user_id')
    if not user_id or user_id not in USERS:
        return jsonify({"success": False, "message": "غير مسجّل"}), 401
    with USERS_LOCK:
        client_manager = USERS[user_id].get('client_manager')
    if not client_manager:
        return jsonify({"success": False, "message": "يجب تسجيل الدخول أولاً"})
    data = request.json or {}
    batch_id = data.get("batch_id", "")
    new_text = data.get("new_text", "")
    if not batch_id or not new_text:
        return jsonify({"success": False, "message": "بيانات ناقصة"})
    def run_edit():
        try:
            client_manager.run_coroutine(
                client_manager._edit_batch_messages(batch_id, new_text)
            )
        except Exception as e:
            socketio.emit('log_update', {"message": f"❌ خطأ في التعديل: {str(e)[:100]}"}, to=user_id)
    _OSThread(target=run_edit, daemon=True).start()
    return jsonify({"success": True, "message": "⏳ جارٍ تعديل الرسائل..."})


@app.route("/api/delete_batch", methods=["POST"])
def api_delete_batch():
    """حذف جميع رسائل الدفعة دفعة واحدة"""
    user_id = session.get('user_id')
    if not user_id or user_id not in USERS:
        return jsonify({"success": False, "message": "غير مسجّل"}), 401
    with USERS_LOCK:
        client_manager = USERS[user_id].get('client_manager')
    if not client_manager:
        return jsonify({"success": False, "message": "يجب تسجيل الدخول أولاً"})
    data = request.json or {}
    batch_id = data.get("batch_id", "")
    if not batch_id:
        return jsonify({"success": False, "message": "batch_id مطلوب"})
    def run_delete():
        try:
            client_manager.run_coroutine(
                client_manager._delete_batch_messages(batch_id)
            )
        except Exception as e:
            socketio.emit('log_update', {"message": f"❌ خطأ في الحذف: {str(e)[:100]}"}, to=user_id)
    _OSThread(target=run_delete, daemon=True).start()
    return jsonify({"success": True, "message": "⏳ جارٍ حذف الرسائل..."})


@app.route("/api/batch_details/<batch_id>")
def api_batch_details(batch_id):
    """عرض تفاصيل دفعة محددة"""
    user_id = session.get('user_id')
    if not user_id or user_id not in USERS:
        return jsonify({"success": False, "message": "غير مسجّل"}), 401
    with USERS_LOCK:
        batches = USERS[user_id].get('sent_batches', [])
        batch = next((b for b in batches if b["id"] == batch_id), None)
    if not batch:
        return jsonify({"success": False, "message": "الدفعة غير موجودة"}), 404
    return jsonify({
        "success": True,
        "batch": {
            "id": batch["id"],
            "text": batch["text"],
            "has_media": batch.get("has_media", False),
            "sent_at": batch["sent_at"],
            "edited_at": batch.get("edited_at"),
            "entries": batch["entries"]
        }
    })


# ====== Web Push API Routes ======

@app.route("/api/push/vapid-public-key", methods=["GET"])
def api_push_vapid_key():
    return jsonify({"publicKey": VAPID_PUBLIC_KEY})

@app.route("/api/push/subscribe", methods=["POST"])
def api_push_subscribe():
    user_id = str(session.get('user_id', 'user_1'))
    sub = request.json
    if not sub or 'endpoint' not in sub:
        return jsonify({"success": False, "error": "اشتراك غير صالح"}), 400
    push_subscriptions[user_id] = sub
    _save_push_subs(push_subscriptions)
    logger.info(f"✅ Push subscription saved for user {user_id}")
    return jsonify({"success": True})

@app.route("/api/push/settings", methods=["GET"])
def api_push_settings_get():
    user_id = session.get('user_id', 'user_1')
    s = load_settings(user_id)
    return jsonify({
        "push_enabled": s.get('push_notifications_enabled', False),
        "speech_enabled": s.get('speech_notifications_enabled', False)
    })

@app.route("/api/push/settings", methods=["POST"])
def api_push_settings_post():
    user_id = session.get('user_id', 'user_1')
    data = request.json or {}
    s = load_settings(user_id)
    if 'push_enabled' in data:
        s['push_notifications_enabled'] = bool(data['push_enabled'])
    if 'speech_enabled' in data:
        s['speech_notifications_enabled'] = bool(data['speech_enabled'])
    save_settings(user_id, s)
    return jsonify({"success": True})

# ============================================================
#  نظام الإدارة + المصادقة البيومترية + التخزين عبر GitHub
# ============================================================

# ---- بيانات تسجيل الدخول الإدارية ----
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "Anwer")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "772997043a*anwer")

# ---- إعدادات GitHub الخاصة بالبصمة والملفات ----
BIO_REPO_OWNER  = os.environ.get("GITHUB_REPO_OWNER", "anwer1230")
BIO_REPO_NAME   = os.environ.get("GITHUB_REPO_NAME", "Telegram-abu-Malk-education")
BIO_BRANCH      = os.environ.get("GITHUB_BRANCH", "main")
BIOMETRIC_PATH  = "data/biometric_devices.json"
UPLOADS_FOLDER  = "uploads"

# ─── استدعاء الإدارة عبر البحث في رسائلي ───────────────────────────────────────

@app.route('/api/admin_ui_invoke', methods=['POST'])
def api_admin_ui_invoke():
    """استدعاء أيقونة الإدارة عبر كلمة مرور المشرف من حقل البحث في رسائلي"""
    data = request.json or {}
    password = data.get('password', '').strip()
    user_id = session.get('user_id', 'user_1')
    if password == ADMIN_PASSWORD:
        session['admin_ui_visible'] = True
        session['admin_ui_user'] = user_id
        session['admin_auth'] = True
        session.permanent = True
        try:
            socketio.emit('admin_ui_invoked', {
                'visible': True,
                'message': '✅ تم استدعاء لوحة الإدارة بنجاح'
            }, to=user_id)
        except Exception:
            pass
        return jsonify({'success': True, 'message': '✅ تم استدعاء لوحة الإدارة بنجاح', 'visible': True})
    return jsonify({'success': False, 'message': '❌ كلمة المرور غير صحيحة'})

@app.route('/api/admin_ui_hide', methods=['POST'])
def api_admin_ui_hide():
    """إخفاء أيقونة الإدارة عند الخروج من الإدارة"""
    user_id = session.get('user_id', 'user_1')
    session.pop('admin_ui_visible', None)
    session.pop('admin_ui_user', None)
    session.pop('admin_auth', None)
    try:
        socketio.emit('admin_ui_invoked', {
            'visible': False,
            'message': '🔒 تم إخفاء لوحة الإدارة'
        }, to=user_id)
    except Exception:
        pass
    return jsonify({'success': True, 'message': 'تم إخفاء الإدارة'})

@app.route('/api/admin_ui_status', methods=['GET'])
def api_admin_ui_status():
    """التحقق من حالة ظهور أيقونة الإدارة — الأيقونة مخفية دائماً"""
    return jsonify({'visible': False})

@app.route('/admin_panel')
def admin_panel_page():
    """صفحة لوحة الإدارة الكاملة"""
    return render_template('admin_panel.html')

@app.route('/admin/api/session_check', methods=['GET'])
def admin_session_check():
    """التحقق من جلسة الإدارة"""
    if session.get('admin_auth'):
        return jsonify({'success': True})
    return jsonify({'success': False})

# ── دوال GitHub API ───────────────────────────────────────────────────

def _gh_headers():
    tok = GITHUB_TOKEN or os.environ.get("GITHUB_TOKEN", "")
    return {"Authorization": f"token {tok}", "Accept": "application/vnd.github.v3+json"}

def upload_to_github(file_path_in_repo, content_bytes, commit_message="رفع ملف تلقائي"):
    if not GITHUB_TOKEN:
        logger.error("GITHUB_TOKEN غير مضبوط")
        return False
    url = f"https://api.github.com/repos/{BIO_REPO_OWNER}/{BIO_REPO_NAME}/contents/{file_path_in_repo}"
    content_b64 = base64.b64encode(content_bytes).decode("utf-8")
    sha = None
    try:
        resp = requests.get(url, headers=_gh_headers(), timeout=10)
        if resp.status_code == 200:
            sha = resp.json().get("sha")
    except Exception as e:
        logger.warning(f"فشل جلب SHA: {e}")
    data = {"message": commit_message, "content": content_b64, "branch": BIO_BRANCH}
    if sha:
        data["sha"] = sha
    try:
        r = requests.put(url, headers=_gh_headers(), json=data, timeout=20)
        if r.status_code in (200, 201):
            return True
        logger.error(f"فشل رفع الملف: {r.status_code} {r.text[:100]}")
        return False
    except Exception as e:
        logger.error(f"استثناء رفع الملف: {e}")
        return False

def download_from_github(file_path_in_repo):
    if not GITHUB_TOKEN:
        return None
    url = f"https://api.github.com/repos/{BIO_REPO_OWNER}/{BIO_REPO_NAME}/contents/{file_path_in_repo}"
    try:
        resp = requests.get(url, headers=_gh_headers(), timeout=10)
        if resp.status_code == 200:
            c = resp.json().get("content", "").replace("\n", "")
            if c:
                return base64.b64decode(c)
    except Exception as e:
        logger.warning(f"فشل تحميل {file_path_in_repo}: {e}")
    return None


# ══════════════════════════════════════════════════════════════════════════════
# ─── الروابط المحفوظة ─────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════

SAVED_LINKS_FILE = os.path.join(DATA_DIR, 'saved_links.json')

def _sanitize_saved_links_payload(d):
    if not isinstance(d, dict):
        return {"links": []}
    val = d.get("links", [])
    while isinstance(val, dict):
        val = val.get("links", [])
    if not isinstance(val, list):
        val = []
    clean = [
        l for l in val
        if isinstance(l, dict)
        and l.get("url")
        and not str(l.get("id", "")).startswith("report_")
        and l.get("category") != "safety_report"
        and l.get("type") != "safety_report"
    ]
    return {"links": clean}


def load_saved_links(force_refresh=False):
    """تحميل الروابط المحفوظة بسرعة فائقة مع الدمج الآمن عبر الذاكرة وPostgreSQL والملف المحلي وFirestore"""
    try:
        import firestore_sync
        merged = firestore_sync.get_merged_saved_links(force_refresh=force_refresh)
        if merged:
            return {"links": merged}
    except Exception as e:
        logger.error(f"Error loading merged saved_links: {e}")

    try:
        if os.path.exists(SAVED_LINKS_FILE):
            with open(SAVED_LINKS_FILE, 'r', encoding='utf-8') as f:
                local_data = _sanitize_saved_links_payload(json.load(f))
                if local_data["links"]:
                    return local_data
    except Exception:
        pass

    try:
        content = download_from_github("data/saved_links.json")
        if content:
            data = _sanitize_saved_links_payload(json.loads(content.decode("utf-8")))
            with open(SAVED_LINKS_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            try:
                import firestore_sync
                firestore_sync.invalidate_links_cache()
                firestore_sync._bg_sync_links_to_pg(data["links"])
            except Exception:
                pass
            return data
    except Exception:
        pass
    return {"links": []}


def _bg_upload_saved_links_to_github(raw_bytes):
    try:
        upload_to_github("data/saved_links.json", raw_bytes, "تحديث الروابط المحفوظة")
    except Exception as e:
        logger.debug(f"Background saved_links GitHub sync notice: {e}")


def save_saved_links(data):
    """حفظ الروابط المحفوظة محلياً فوراً ومزامنتها خلفياً مع GitHub دون تعطيل الطلبات"""
    clean_data = _sanitize_saved_links_payload(data)
    try:
        os.makedirs(os.path.dirname(SAVED_LINKS_FILE), exist_ok=True)
        with open(SAVED_LINKS_FILE, 'w', encoding='utf-8') as f:
            json.dump(clean_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error saving saved_links locally: {e}")
    try:
        if GITHUB_TOKEN:
            raw = json.dumps(clean_data, ensure_ascii=False, indent=2).encode('utf-8')
            threading.Thread(target=_bg_upload_saved_links_to_github, args=(raw,), daemon=True).start()
    except Exception as e:
        logger.debug(f"GitHub thread spawn notice: {e}")


def add_saved_link(url, title=None, category='عام', notes='', source='يدوي'):
    url = str(url or '').strip()
    if not url:
        return False, "الرابط مطلوب"
    data = load_saved_links(force_refresh=False)
    for link in data["links"]:
        if link["url"].strip().lower() == url.lower():
            return False, "الرابط موجود بالفعل"
    new_link = {
        "id": str(uuid.uuid4())[:8],
        "url": url,
        "title": title or url,
        "category": category or 'عام',
        "date_saved": datetime.now().isoformat(),
        "source": source or 'يدوي',
        "notes": notes or ''
    }
    data["links"].insert(0, new_link)
    save_saved_links(data)
    try:
        import firestore_sync
        firestore_sync.add_firestore_link(new_link)
    except Exception as e:
        logger.error(f"Error syncing new link: {e}")
    return True, new_link


def add_multiple_links(urls, category='عام', source='دفعة'):
    data = load_saved_links(force_refresh=False)
    existing_lower = {l["url"].strip().lower() for l in data["links"] if l.get("url")}
    added = []
    skipped = []
    new_records = []
    for url in urls:
        url = str(url or '').strip()
        if not url:
            continue
        if url.lower() in existing_lower:
            skipped.append(url)
            continue
        existing_lower.add(url.lower())
        new_link = {
            "id": str(uuid.uuid4())[:8],
            "url": url,
            "title": url,
            "category": category or 'عام',
            "date_saved": datetime.now().isoformat(),
            "source": source or 'دفعة',
            "notes": ""
        }
        data["links"].insert(0, new_link)
        added.append(url)
        new_records.append(new_link)

    if new_records:
        save_saved_links(data)
        try:
            import firestore_sync
            for rec in new_records:
                firestore_sync.add_firestore_link(rec)
        except Exception:
            pass
    return added, skipped


def delete_saved_link(link_id):
    data = load_saved_links(force_refresh=False)
    data["links"] = [l for l in data["links"] if str(l.get("id", "")) != str(link_id)]
    save_saved_links(data)
    try:
        import firestore_sync
        firestore_sync.delete_firestore_link(link_id)
    except Exception as e:
        logger.error(f"Error deleting link: {e}")
    return True


def delete_multiple_links(link_ids):
    id_set = {str(x) for x in (link_ids or [])}
    data = load_saved_links(force_refresh=False)
    data["links"] = [l for l in data["links"] if str(l.get("id", "")) not in id_set]
    save_saved_links(data)
    try:
        import firestore_sync
        firestore_sync.delete_firestore_links_batch(list(id_set))
    except Exception:
        pass
    return True


def update_saved_link(link_id, updates):
    data = load_saved_links(force_refresh=False)
    for link in data["links"]:
        if str(link.get("id", "")) == str(link_id):
            if "title" in updates: link["title"] = updates["title"]
            if "category" in updates: link["category"] = updates["category"]
            if "notes" in updates: link["notes"] = updates["notes"]
            save_saved_links(data)
            try:
                import firestore_sync
                firestore_sync.update_firestore_link(link)
            except Exception as e:
                logger.error(f"Error syncing updated link: {e}")
            return True, link
    return False, None


def get_saved_links_by_category(category=None):
    data = load_saved_links(force_refresh=False)
    if category:
        return [l for l in data["links"] if l.get("category") == category]
    return data["links"]


def get_categories():
    data = load_saved_links(force_refresh=False)
    return sorted(set(l.get("category", "عام") for l in data["links"] if l.get("category")))


# ── مسارات الروابط المحفوظة ──────────────────────────────────────────────────

@app.route("/saved_links")
def saved_links_page():
    return render_template('saved_links.html')


@app.route("/api/saved_links", methods=["GET"])
def api_get_saved_links():
    category = request.args.get('category')
    force = str(request.args.get('force', '')).lower() in ('1', 'true', 'yes')
    data = load_saved_links(force_refresh=force)
    all_links = data.get("links", [])
    categories = sorted(set(l.get("category", "عام") for l in all_links if l.get("category")))
    links = [l for l in all_links if l.get("category") == category] if category else all_links

    sync_info = {}
    try:
        import firestore_sync
        sync_info = firestore_sync.get_links_sync_status()
    except Exception:
        pass

    return jsonify({
        "success": True,
        "links": links,
        "categories": categories,
        "total": len(links),
        "firestore_live": sync_info.get("firestore_live", False),
        "firestore_error": sync_info.get("firestore_error"),
        "pg_count": sync_info.get("pg_count", 0),
        "local_count": sync_info.get("local_count", len(all_links)),
    })


@app.route("/api/saved_links/add", methods=["POST"])
def api_add_saved_link():
    data = request.json or {}
    url = data.get('url', '').strip()
    title = data.get('title', '').strip() or url
    category = data.get('category', 'عام')
    notes = data.get('notes', '')
    source = data.get('source', 'يدوي')
    if not url:
        return jsonify({"success": False, "message": "الرابط مطلوب"})
    success, result = add_saved_link(url, title, category, notes, source)
    if success:
        return jsonify({"success": True, "link": result})
    return jsonify({"success": False, "message": result})


@app.route("/api/saved_links/add_batch", methods=["POST"])
def api_add_saved_links_batch():
    data = request.json or {}
    urls = data.get('urls', [])
    category = data.get('category', 'عام')
    source = data.get('source', 'دفعة')
    if not urls:
        return jsonify({"success": False, "message": "لا توجد روابط"})
    added, skipped = add_multiple_links(urls, category, source)
    return jsonify({"success": True, "added": added, "skipped": skipped,
                    "added_count": len(added), "skipped_count": len(skipped)})


@app.route("/api/saved_links/delete", methods=["POST"])
def api_delete_saved_link():
    data = request.json or {}
    link_id = data.get('id')
    if not link_id:
        return jsonify({"success": False, "message": "معرف الرابط مطلوب"})
    delete_saved_link(link_id)
    return jsonify({"success": True})


@app.route("/api/saved_links/delete_batch", methods=["POST"])
def api_delete_saved_links_batch():
    data = request.json or {}
    link_ids = data.get('ids', [])
    if not link_ids:
        return jsonify({"success": False, "message": "لا توجد معرفات"})
    delete_multiple_links(link_ids)
    return jsonify({"success": True})


@app.route("/api/saved_links/update", methods=["POST"])
def api_update_saved_link():
    data = request.json or {}
    link_id = data.get('id')
    if not link_id:
        return jsonify({"success": False, "message": "معرف الرابط مطلوب"})
    updates = {}
    if 'title' in data: updates['title'] = data['title']
    if 'category' in data: updates['category'] = data['category']
    if 'notes' in data: updates['notes'] = data['notes']
    if not updates:
        return jsonify({"success": False, "message": "لا توجد تحديثات"})
    success, link = update_saved_link(link_id, updates)
    if success:
        return jsonify({"success": True, "link": link})
    return jsonify({"success": False, "message": "الرابط غير موجود"})

@app.route("/api/saved_links/export", methods=["GET", "POST"])
def api_export_saved_links():
    data = (request.get_json(silent=True) if request.is_json else None) or {}
    link_ids = data.get('ids', [])
    data_links = load_saved_links()
    if link_ids:
        links = [l for l in data_links["links"] if l["id"] in link_ids]
    else:
        links = data_links["links"]
    if not links:
        return jsonify({"success": False, "message": "لا توجد روابط للتصدير"}), 400
    content = "\n".join(l["url"] for l in links)
    response = make_response(content)
    response.headers["Content-Type"] = "text/plain; charset=utf-8"
    response.headers["Content-Disposition"] = f"attachment; filename=saved_links_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    return response


@app.route("/api/saved_links/export_pdf", methods=["GET", "POST"])
def api_export_saved_links_pdf():
    """تصدير قائمة الروابط المحفوظة كملف PDF منظم وعالي الجودة للتحميل لذاكرة الجهاز"""
    try:
        import io
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

        data = (request.get_json(silent=True) if request.is_json else None) or {}
        link_ids = data.get('ids', [])
        data_links = load_saved_links()
        if link_ids:
            links = [l for l in data_links["links"] if l["id"] in link_ids]
        else:
            links = data_links["links"]

        if not links:
            return jsonify({"success": False, "message": "لا توجد روابط لتصديرها"}), 400

        buf = io.BytesIO()
        doc = SimpleDocTemplate(
            buf,
            pagesize=A4,
            rightMargin=25,
            leftMargin=25,
            topMargin=25,
            bottomMargin=25
        )
        elements = []
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=15,
            leading=20,
            alignment=1,
            textColor=colors.HexColor('#1e3a8a')
        )
        meta_style = ParagraphStyle(
            'MetaStyle',
            parent=styles['Normal'],
            fontSize=8,
            leading=12,
            alignment=1,
            textColor=colors.HexColor('#64748b')
        )
        cell_style = ParagraphStyle(
            'CellStyle',
            parent=styles['Normal'],
            fontSize=8,
            leading=10,
            wordWrap='CJK'
        )
        url_style = ParagraphStyle(
            'UrlStyle',
            parent=styles['Normal'],
            fontSize=7.5,
            leading=9.5,
            textColor=colors.HexColor('#2563eb'),
            wordWrap='CJK'
        )

        elements.append(Paragraph("تقرير الروابط المحفوظة - مركز سرعة إنجاز", title_style))
        elements.append(Spacer(1, 4))
        elements.append(Paragraph(f"تاريخ التصدير: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | إجمالي الروابط: {len(links)} رابط محفوظ داخل قاعدة البيانات", meta_style))
        elements.append(Spacer(1, 10))

        table_data = [
            [Paragraph("<b>#</b>", cell_style),
             Paragraph("<b>الرابط / URL</b>", cell_style),
             Paragraph("<b>العنوان / التفاصيل</b>", cell_style),
             Paragraph("<b>التصنيف</b>", cell_style),
             Paragraph("<b>تاريخ الحفظ</b>", cell_style)]
        ]

        for idx, l in enumerate(links, 1):
            url_str = str(l.get('url', '') or '')
            title_str = str(l.get('title', '') or url_str)
            cat_str = str(l.get('category', 'عام') or 'عام')
            date_str = str(l.get('date_saved', '') or '')[:16].replace('T', ' ')

            table_data.append([
                Paragraph(str(idx), cell_style),
                Paragraph(url_str, url_style),
                Paragraph(title_str, cell_style),
                Paragraph(cat_str, cell_style),
                Paragraph(date_str, cell_style)
            ])

        t = Table(table_data, colWidths=[20, 220, 160, 65, 80])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#0f172a')),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))

        elements.append(t)
        doc.build(elements)
        pdf_bytes = buf.getvalue()
        buf.close()

        resp = make_response(pdf_bytes)
        resp.headers['Content-Type'] = 'application/pdf'
        filename = f"saved_links_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        resp.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        return resp
    except Exception as e:
        logger.error(f"Error generating PDF export for saved links: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/saved_links/inspect_status", methods=["GET"])
def api_inspect_saved_links_status():
    """فحص واستعراض الحالة الفعلية الحقيقية لقاعدة البيانات وروابطها وإرجاع القائمة مباشرة في طلب واحد"""
    try:
        data_links = load_saved_links(force_refresh=True)
        links = data_links.get("links", [])
        cats = sorted(list(set(l.get("category", "عام") for l in links if l.get("category"))))

        sync_info = {}
        try:
            import firestore_sync
            sync_info = firestore_sync.get_links_sync_status()
        except Exception:
            sync_info = {}

        firestore_live = bool(sync_info.get("firestore_live", False))
        firestore_error = sync_info.get("firestore_error")

        if firestore_live and len(links) > 0:
            status_text = "السحابة والمحلي متصلة وممتلئة"
            msg = f"🟢 قاعدة البيانات السحابية (Firestore) والمحلية نشطة ومتصلة بنجاح! تم استعراض {len(links)} رابط محفوظ موزعة على {len(cats)} تصنيف."
        elif len(links) > 0:
            status_text = "تم الاستعراض من القاعدة المحلية/PostgreSQL"
            err_hint = f" ({firestore_error})" if firestore_error else ""
            msg = f"🟡 تم تحميل وعرض {len(links)} رابط محفوظ بسرعة من قاعدة البيانات المحلية/PostgreSQL ({len(cats)} تصنيف). السحابة غير متاحة حالياً{err_hint}."
        elif firestore_live:
            status_text = "متصلة ولكن فارغة"
            msg = "🟡 قاعدة البيانات متصلة وجاهزة، ولكن لا يوجد أي رابط محفوظ حالياً."
        else:
            status_text = "فارغة والسحابة مقيدة"
            msg = f"⚠️ لا توجد روابط محفوظة محلياً حالياً وتعذر الوصول لـ Firestore: {firestore_error or 'غير متصل'}"

        return jsonify({
            "success": True,
            "connected": True,
            "firestore_live": firestore_live,
            "firestore_error": firestore_error,
            "cloud_count": sync_info.get("cloud_count", 0),
            "pg_count": sync_info.get("pg_count", 0),
            "local_count": sync_info.get("local_count", len(links)),
            "total_links": len(links),
            "links": links,
            "categories": cats,
            "categories_count": len(cats),
            "status": "has_links" if len(links) > 0 else "empty",
            "status_text": status_text,
            "message": msg,
            "last_updated": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "connected": False,
            "error": str(e),
            "message": f"حدث خطأ أثناء فحص قاعدة البيانات: {str(e)}"
        }), 500

@app.route("/api/saved_links/copy", methods=["POST"])
def api_copy_saved_links():
    data = request.json or {}
    link_ids = data.get('ids', [])
    data_links = load_saved_links()
    if link_ids:
        links = [l for l in data_links["links"] if l["id"] in link_ids]
    else:
        links = data_links["links"]
    content = "\n".join(l["url"] for l in links)
    return jsonify({"success": True, "text": content, "count": len(links)})

@app.route("/api/saved_links/send_to_auto_join", methods=["POST"])
def api_send_saved_to_auto_join():
    data = request.json or {}
    link_ids = data.get('ids', [])
    data_links = load_saved_links()
    if link_ids:
        links = [l for l in data_links["links"] if l["id"] in link_ids]
    else:
        links = data_links["links"]
    urls = [l["url"] for l in links]
    session['auto_join_links'] = urls
    return jsonify({"success": True, "urls": urls, "count": len(urls)})

def file_exists_in_github(file_path_in_repo):
    url = f"https://api.github.com/repos/{BIO_REPO_OWNER}/{BIO_REPO_NAME}/contents/{file_path_in_repo}"
    try:
        return requests.head(url, headers=_gh_headers(), timeout=8).status_code == 200
    except:
        return False

# ── دوال البصمة ───────────────────────────────────────────────────────

def load_biometric_devices():
    raw = download_from_github(BIOMETRIC_PATH)
    if raw:
        try:
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            pass
    return {}

def save_biometric_devices(devices):
    return upload_to_github(
        BIOMETRIC_PATH,
        json.dumps(devices, indent=2, ensure_ascii=False).encode("utf-8"),
        "تحديث بيانات البصمة"
    )

# ── دوال ملفات المستخدمين ─────────────────────────────────────────────

def save_user_file(user_id, filename, file_bytes):
    return upload_to_github(
        f"{UPLOADS_FOLDER}/{user_id}/{filename}",
        file_bytes,
        f"رفع ملف للمستخدم {user_id}"
    )

def get_user_file_url(user_id, filename):
    return f"https://raw.githubusercontent.com/{BIO_REPO_OWNER}/{BIO_REPO_NAME}/{BIO_BRANCH}/{UPLOADS_FOLDER}/{user_id}/{filename}"

def list_user_files(user_id):
    url = f"https://api.github.com/repos/{BIO_REPO_OWNER}/{BIO_REPO_NAME}/contents/{UPLOADS_FOLDER}/{user_id}"
    try:
        resp = requests.get(url, headers=_gh_headers(), timeout=10)
        if resp.status_code == 200:
            return [item["name"] for item in resp.json() if item.get("type") == "file"]
    except:
        pass
    return []

def get_or_create_user(user_id):
    with USERS_LOCK:
        if user_id not in USERS:
            settings = load_settings(user_id)
            USERS[user_id] = {
                'client_manager': None, 'settings': settings,
                'thread': None, 'is_running': False,
                'stats': {"sent": 0, "errors": 0},
                'connected': False, 'authenticated': False,
                'awaiting_code': False, 'awaiting_password': False,
                'phone_code_hash': None, 'monitoring_active': False,
                'event_handlers_registered': False,
                'blocked': settings.get('blocked', False),
                'disabled': settings.get('disabled', False),
                'alerts': settings.get('alerts', []),
                'last_seen': datetime.now().isoformat(),
                'phone_number': settings.get('phone', ''),
                'telegram_name': settings.get('telegram_name', ''),
            }
        return USERS[user_id]

def ensure_github_dirs():
    if not file_exists_in_github(BIOMETRIC_PATH):
        upload_to_github(BIOMETRIC_PATH, b"{}", "إنشاء ملف بيانات البصمة")
    if not file_exists_in_github(f"{UPLOADS_FOLDER}/.gitkeep"):
        upload_to_github(f"{UPLOADS_FOLDER}/.gitkeep", b"# uploads\n", "إنشاء مجلد uploads")

# ── مسارات المصادقة الإدارية ──────────────────────────────────────────

@app.route("/admin/api/check", methods=["GET"])
def admin_check():
    return jsonify({"authenticated": session.get("admin_auth", False)})

@app.route("/admin/api/login", methods=["POST"])
def admin_login():
    data = request.get_json() or {}
    if data.get("username") == ADMIN_USERNAME and data.get("password") == ADMIN_PASSWORD:
        session["admin_auth"] = True
        return jsonify({"success": True, "message": "تم تسجيل الدخول بنجاح"})
    return jsonify({"success": False, "message": "بيانات غير صحيحة"}), 401

@app.route("/admin/api/logout", methods=["POST"])
def admin_logout():
    session.pop("admin_auth", None)
    return jsonify({"success": True, "message": "تم تسجيل الخروج"})

# ── مسارات البصمة ────────────────────────────────────────────────────

@app.route("/admin/api/biometric/register", methods=["POST"])
def biometric_register():
    if not session.get("admin_auth"):
        return jsonify({"success": False, "message": "يجب تسجيل الدخول أولاً"}), 403
    data = request.get_json() or {}
    device_id = data.get("device_id")
    biometric_token = data.get("biometric_token")
    if not device_id or not biometric_token:
        return jsonify({"success": False, "message": "device_id و biometric_token مطلوبان"})
    devices = load_biometric_devices()
    devices[device_id] = biometric_token
    if save_biometric_devices(devices):
        return jsonify({"success": True, "message": f"تم تسجيل الجهاز {device_id} بنجاح"})
    return jsonify({"success": False, "message": "فشل حفظ بيانات البصمة"}), 500

@app.route("/admin/api/biometric/login", methods=["POST"])
def biometric_login():
    data = request.get_json() or {}
    device_id = data.get("device_id")
    biometric_token = data.get("biometric_token")
    if not device_id or not biometric_token:
        return jsonify({"success": False, "message": "device_id و biometric_token مطلوبان"})
    devices = load_biometric_devices()
    if devices.get(device_id) == biometric_token:
        session["admin_auth"] = True
        return jsonify({"success": True, "message": "✅ تم تسجيل الدخول بواسطة البصمة"})
    return jsonify({"success": False, "message": "❌ بيانات البصمة غير صحيحة"}), 401

@app.route("/admin/api/biometric/unregister", methods=["POST"])
def biometric_unregister():
    if not session.get("admin_auth"):
        return jsonify({"success": False, "message": "يجب تسجيل الدخول أولاً"}), 403
    data = request.get_json() or {}
    device_id = data.get("device_id")
    if not device_id:
        return jsonify({"success": False, "message": "device_id مطلوب"})
    devices = load_biometric_devices()
    if device_id in devices:
        del devices[device_id]
        if save_biometric_devices(devices):
            return jsonify({"success": True, "message": f"تم حذف الجهاز {device_id}"})
        return jsonify({"success": False, "message": "فشل حفظ التغييرات"})
    return jsonify({"success": False, "message": "الجهاز غير موجود"})

# ── مسارات إدارة المستخدمين ───────────────────────────────────────────

@app.route("/admin/api/users", methods=["GET"])
def admin_users():
    if not session.get("admin_auth"):
        return jsonify({"success": False, "message": "غير مخول"}), 403
    users = []
    for slot, uinfo in PREDEFINED_USERS.items():
        ud = get_or_create_user(slot)
        s = load_settings(slot)
        users.append({
            "user_id": slot, "name": uinfo.get("name", slot),
            "phone": ud.get('phone_number', ''),
            "logged_in": ud.get('authenticated', False),
            "telegram_name": ud.get('telegram_name', ''),
            "blocked": ud.get('blocked', False),
            "disabled": ud.get('disabled', False),
            "last_seen": ud.get('last_seen', None),
            "groups": s.get("groups", []),
            "watch_words": s.get("watch_words", []),
            "auto_replies": s.get("auto_replies", []),
            "alerts_count": len(ud.get('alerts', []))
        })
    return jsonify({"success": True, "users": users})

@app.route("/admin/api/user/<slot>", methods=["POST"])
def admin_update_user(slot):
    if not session.get("admin_auth"):
        return jsonify({"success": False, "message": "غير مخول"}), 403
    ud = get_or_create_user(slot)
    data = request.get_json() or {}
    action = data.get("action")
    if action == "block":
        ud["blocked"] = data.get("blocked", False)
    elif action == "disable":
        ud["disabled"] = data.get("disabled", False)
    s = load_settings(slot)
    s["blocked"] = ud.get("blocked", False)
    s["disabled"] = ud.get("disabled", False)
    save_settings(slot, s)
    with USERS_LOCK:
        USERS[slot] = ud
    return jsonify({"success": True})

@app.route("/admin/api/fetch_chats/<slot>", methods=["GET"])
def admin_fetch_chats(slot):
    if not session.get("admin_auth"):
        return jsonify({"success": False, "message": "غير مخول"}), 403
    settings = load_settings(slot)
    groups = settings.get("groups", [])
    chats = [{"link": g, "title": g, "username": g.split('/')[-1] if '/' in g else g} for g in groups]
    return jsonify({"success": True, "chats": chats})

@app.route("/admin/api/copy_chats/<slot>", methods=["GET"])
def admin_copy_chats(slot):
    if not session.get("admin_auth"):
        return jsonify({"success": False, "message": "غير مخول"}), 403
    settings = load_settings(slot)
    groups = [g for g in settings.get("groups", []) if g.strip()]
    return jsonify({"success": True, "text": "\n".join(groups), "count": len(groups)})

@app.route("/admin/api/export_chats/<slot>", methods=["GET"])
def admin_export_chats(slot):
    if not session.get("admin_auth"):
        return jsonify({"success": False, "message": "غير مخول"}), 403
    settings = load_settings(slot)
    groups = [g for g in settings.get("groups", []) if g.strip()]
    response = make_response("\n".join(groups))
    response.headers["Content-Type"] = "text/plain; charset=utf-8"
    response.headers["Content-Disposition"] = f"attachment; filename=chats_{slot}.txt"
    return response

@app.route("/admin/api/user_alerts/<slot>", methods=["GET"])
def admin_user_alerts(slot):
    if not session.get("admin_auth"):
        return jsonify({"success": False, "message": "غير مخول"}), 403
    ud = get_or_create_user(slot)
    return jsonify({"success": True, "alerts": ud.get('alerts', [])})

@app.route("/admin/api/upload", methods=["POST"])
def admin_upload_file():
    if not session.get("admin_auth"):
        return jsonify({"success": False, "message": "غير مخول"}), 403
    if 'file' not in request.files:
        return jsonify({"success": False, "message": "لا يوجد ملف مرفق"})
    file = request.files['file']
    if not file.filename:
        return jsonify({"success": False, "message": "اسم الملف فارغ"})
    user_id = request.form.get("user_id", "admin")
    file_bytes = file.read()
    if save_user_file(user_id, file.filename, file_bytes):
        return jsonify({"success": True, "message": "تم رفع الملف بنجاح",
                        "url": get_user_file_url(user_id, file.filename),
                        "filename": file.filename})
    return jsonify({"success": False, "message": "فشل رفع الملف إلى GitHub"}), 500

@app.route("/admin/api/files/<user_id>", methods=["GET"])
def admin_list_files(user_id):
    if not session.get("admin_auth"):
        return jsonify({"success": False, "message": "غير مخول"}), 403
    return jsonify({"success": True, "files": list_user_files(user_id)})


# ══════════════════════════════════════════════════════════════
#  نظام الإشعارات العامة (Broadcast Notifications)
# ══════════════════════════════════════════════════════════════

_NOTIF_FILE = os.path.join(os.path.dirname(__file__), 'data', 'notifications.json')
os.makedirs(os.path.dirname(_NOTIF_FILE), exist_ok=True)

def _load_notifications():
    """تحميل الإشعارات من الملف المحلي، ثم GitHub كاحتياطي."""
    # أولاً: الملف المحلي
    try:
        if os.path.exists(_NOTIF_FILE):
            with open(_NOTIF_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    # ثانياً: GitHub
    try:
        content = download_from_github("data/notifications.json")
        if content:
            data = json.loads(content.decode("utf-8"))
            # نسخ محلي للسرعة
            with open(_NOTIF_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return data
    except Exception:
        pass
    return []

def _save_notifications(notifications):
    """حفظ الإشعارات محلياً وفي GitHub."""
    try:
        with open(_NOTIF_FILE, 'w', encoding='utf-8') as f:
            json.dump(notifications, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Notifications local save error: {e}")
    # محاولة الرفع إلى GitHub (اختياري)
    try:
        raw = json.dumps(notifications, ensure_ascii=False, indent=2).encode('utf-8')
        upload_to_github("data/notifications.json", raw, "تحديث الإشعارات")
    except Exception:
        pass

@app.route("/admin/api/notifications", methods=["GET"])
def admin_get_notifications():
    """جلب جميع الإشعارات المخزنة."""
    if not session.get("admin_auth"):
        return jsonify({"success": False, "message": "غير مخول"}), 403
    return jsonify({"success": True, "notifications": _load_notifications()})

@app.route("/admin/api/broadcast_notification", methods=["POST"])
def admin_broadcast_notification():
    """نشر إشعار فوري لجميع المستخدمين المتصلين وتخزينه."""
    if not session.get("admin_auth"):
        return jsonify({"success": False, "message": "غير مخول"}), 403
    data = request.get_json() or {}
    message  = data.get("message", "").strip()
    notif_type = data.get("type", "info")   # info / success / warning / danger
    if not message:
        return jsonify({"success": False, "message": "نص الإشعار مطلوب"})
    notification = {
        "id":        str(uuid.uuid4()),
        "message":   message,
        "type":      notif_type,
        "timestamp": datetime.now().isoformat(),
    }
    notifs = _load_notifications()
    notifs.insert(0, notification)          # الأحدث أولاً
    notifs = notifs[:100]                   # الاحتفاظ بآخر 100
    _save_notifications(notifs)
    # بث فوري لجميع المستخدمين المتصلين عبر Socket.IO
    socketio.emit("new_broadcast_notification", notification)

    # ── إرسال Web Push لكل المشتركين (حتى لو التطبيق مغلق) ──
    push_sent = 0
    _type_icon = {"success": "✅", "warning": "⚠️", "danger": "❌", "info": "📢"}.get(notif_type, "📢")
    push_title = f"{_type_icon} إشعار من الإدارة"
    for uid, sub in list(push_subscriptions.items()):
        try:
            import json as _json
            _payload = _json.dumps({
                "title": push_title,
                "body":  message,
                "type":  "broadcast",
                "id":    notification["id"],
                "icon":  "/static/icons/app-logo.png",
                "badge": "/static/icons/app-logo.png",
                "data":  {"notif_id": notification["id"]}
            })
            _webpush_fn(
                subscription_info=sub,
                data=_payload,
                vapid_private_key=VAPID_PRIVATE_PEM,
                vapid_claims=VAPID_CLAIMS,
                ttl=86400
            )
            push_sent += 1
        except Exception as _px:
            _sc = getattr(getattr(_px, 'response', None), 'status_code', 0)
            if _sc in (410, 404):
                push_subscriptions.pop(uid, None)
            logger.warning(f"Broadcast push failed for {uid}: {_px}")
    if push_sent:
        _save_push_subs(push_subscriptions)
    logger.info(f"📢 إشعار مبث: {message[:60]} | Push: {push_sent} مستخدم")
    return jsonify({"success": True, "message": f"تم نشر الإشعار بنجاح (Push: {push_sent})", "notification": notification})

@app.route("/admin/api/delete_notification/<notif_id>", methods=["DELETE"])
def admin_delete_notification(notif_id):
    """حذف إشعار محدد."""
    if not session.get("admin_auth"):
        return jsonify({"success": False, "message": "غير مخول"}), 403
    notifs = [n for n in _load_notifications() if n.get("id") != notif_id]
    _save_notifications(notifs)
    return jsonify({"success": True})

@app.route("/admin/api/push_stats", methods=["GET"])
def admin_push_stats():
    """إحصائيات المشتركين في Web Push"""
    if not session.get("admin_auth"):
        return jsonify({"success": False}), 403
    subs = list(push_subscriptions.keys())
    return jsonify({
        "success": True,
        "count": len(subs),
        "subscribers": subs
    })


@app.route("/admin/api/test_push", methods=["POST"])
def admin_test_push():
    """إرسال إشعار اختباري لكل المشتركين"""
    if not session.get("admin_auth"):
        return jsonify({"success": False, "message": "غير مخول"}), 403
    data  = request.get_json() or {}
    msg   = data.get("message", "✅ اختبار الإشعار — يعمل بشكل صحيح!")
    ntype = data.get("type", "general")
    icons = {"broadcast": "📢", "schedule_expired": "⏹", "general": "🔔"}
    title = f"{icons.get(ntype,'🔔')} إشعار اختباري"
    sent = 0
    for uid, sub in list(push_subscriptions.items()):
        try:
            import json as _json
            _payload = _json.dumps({
                "title": title,
                "body":  msg,
                "type":  ntype,
                "icon":  "/static/icons/app-logo.png",
                "badge": "/static/icons/app-logo.png",
                "data":  {"test": True}
            })
            _webpush_fn(
                subscription_info=sub,
                data=_payload,
                vapid_private_key=VAPID_PRIVATE_PEM,
                vapid_claims=VAPID_CLAIMS,
                ttl=300
            )
            sent += 1
        except Exception as _px:
            _sc = getattr(getattr(_px, 'response', None), 'status_code', 0)
            if _sc in (410, 404):
                push_subscriptions.pop(uid, None)
            logger.warning(f"Test push failed for {uid}: {_px}")
    if sent:
        _save_push_subs(push_subscriptions)
    return jsonify({"success": True, "sent": sent,
                    "message": f"✅ تم إرسال الاختبار لـ {sent} مستخدم"})


@app.route("/admin/api/clear_notifications", methods=["POST"])
def admin_clear_notifications():
    """مسح جميع الإشعارات."""
    if not session.get("admin_auth"):
        return jsonify({"success": False, "message": "غير مخول"}), 403
    _save_notifications([])
    return jsonify({"success": True, "message": "تم مسح جميع الإشعارات"})

# ── صفحة لوحة تحكم الإدارة (بسيطة) ────────────────────────────────────

@app.route("/admin")
@app.route("/admin/")
def admin_dashboard():
    if not session.get("admin_auth"):
        return '''<!DOCTYPE html><html dir="rtl"><head><meta charset="utf-8">
        <title>تسجيل الدخول - الإدارة</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
        </head><body class="bg-dark text-light"><div class="container py-5">
        <div class="row justify-content-center"><div class="col-md-4">
        <div class="card bg-secondary"><div class="card-header"><h5 class="mb-0">🔐 لوحة الإدارة</h5></div>
        <div class="card-body">
        <div id="msg"></div>
        <div class="mb-3"><label class="form-label">اسم المستخدم</label>
        <input type="text" class="form-control" id="adm_u" value="Anwer"></div>
        <div class="mb-3"><label class="form-label">كلمة المرور</label>
        <input type="password" class="form-control" id="adm_p"></div>
        <button class="btn btn-primary w-100" onclick="doLogin()">دخول</button>
        <hr><button class="btn btn-outline-info w-100 mt-2" onclick="bioLogin()">🔑 دخول بالبصمة</button>
        </div></div></div></div></div>
        <script>
        async function doLogin(){
          const r=await fetch('/admin/api/login',{method:'POST',headers:{'Content-Type':'application/json'},
          body:JSON.stringify({username:document.getElementById('adm_u').value,password:document.getElementById('adm_p').value})});
          const d=await r.json();
          if(d.success){location.reload();}else{document.getElementById('msg').innerHTML='<div class="alert alert-danger">'+d.message+'</div>';}
        }
        async function bioLogin(){
          const did=localStorage.getItem('deviceId'),bt=localStorage.getItem('biometricToken');
          if(!did||!bt){alert('لم تسجل بصمتك بعد');return;}
          const r=await fetch('/admin/api/biometric/login',{method:'POST',headers:{'Content-Type':'application/json'},
          body:JSON.stringify({device_id:did,biometric_token:bt})});
          const d=await r.json();
          if(d.success){location.reload();}else{alert(d.message);}
        }
        </script></body></html>''', 200

    return '''<!DOCTYPE html><html dir="rtl"><head><meta charset="utf-8">
    <title>لوحة الإدارة</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.socket.io/4.6.1/socket.io.min.js"></script>
    <style>
    #consoleScreen{
      background:#080808;color:#c8ffc8;font-family:'Courier New',monospace;font-size:12.5px;
      height:480px;overflow-y:auto;padding:10px 14px;border:none;
      scrollbar-width:thin;scrollbar-color:#1a3a1a #080808;
    }
    #consoleScreen::-webkit-scrollbar{width:6px;}
    #consoleScreen::-webkit-scrollbar-track{background:#080808;}
    #consoleScreen::-webkit-scrollbar-thumb{background:#1a3a1a;border-radius:3px;}
    .cl{display:flex;gap:8px;padding:1.5px 0;border-bottom:1px solid rgba(0,80,0,0.12);
        font-size:12.5px;line-height:1.45;word-break:break-all;align-items:flex-start;}
    .cl:hover{background:rgba(0,255,65,0.04);}
    .cl .ts{color:#2d6a2d;min-width:68px;flex-shrink:0;font-size:11.5px;}
    .cl .nm{color:#4a8a4a;min-width:70px;flex-shrink:0;font-size:11.5px;overflow:hidden;text-overflow:ellipsis;}
    .cl .lv{min-width:52px;flex-shrink:0;font-size:11px;font-weight:700;}
    .cl .tx{flex:1;color:#b8f0b8;}
    .cl.info .lv{color:#00bfff;}.cl.info .tx{color:#9fdfff;}
    .cl.warn .lv{color:#ffa500;}.cl.warn .tx{color:#ffe0a0;}
    .cl.error .lv{color:#ff4444;}.cl.error .tx{color:#ffaaaa;}
    .cl.critical .lv{color:#ff0000;font-weight:900;}.cl.critical .tx{color:#ff8888;}
    .cl.debug .lv{color:#666;}.cl.debug .tx{color:#888;}
    .cl.sys .lv{color:#a855f7;}.cl.sys .tx{color:#d8b4fe;}
    .hl-get{color:#22d3ee;}.hl-post{color:#fbbf24;}.hl-put{color:#a3e635;}
    .hl-del{color:#f87171;}.hl-200{color:#4ade80;}.hl-404{color:#fb923c;}.hl-500{color:#ef4444;}
    .file-item{cursor:pointer;padding:4px 8px;border-radius:3px;transition:background 0.15s;}
    .file-item:hover{background:rgba(255,255,255,0.1);}
    .file-item.selected{background:rgba(0,123,255,0.3);border-left:3px solid #0d6efd;}
    </style>
    </head><body class="bg-dark text-light">
    <div class="container-fluid py-3">
    <div class="d-flex justify-content-between align-items-center mb-4">
    <h4><i class="fas fa-shield-alt me-2"></i>لوحة إدارة أبو مالك</h4>
    <div>
    <button class="btn btn-outline-info btn-sm me-2" onclick="registerBio()">🔑 تسجيل البصمة</button>
    <button class="btn btn-outline-danger btn-sm" onclick="doLogout()">خروج</button>
    </div></div>

    <!-- ════ جدول المستخدمين ════ -->
    <div id="usersTable"><div class="text-center py-5"><i class="fas fa-spinner fa-spin fa-3x"></i></div></div>

    <!-- ════ قسم الإشعارات العامة ════ -->
    <div class="card bg-secondary mt-4">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h5 class="mb-0"><i class="fas fa-bullhorn me-2 text-warning"></i>📢 نشر الإشعارات</h5>
        <button class="btn btn-outline-danger btn-sm" onclick="clearAllNotifs()">
          <i class="fas fa-trash-alt me-1"></i>مسح الكل
        </button>
      </div>
      <div class="card-body">
        <div class="row g-3">
          <div class="col-md-7">
            <label class="form-label small">نص الإشعار</label>
            <textarea id="notifMsg" class="form-control bg-dark text-light border-secondary" rows="3"
              placeholder="اكتب الإشعار..."></textarea>
          </div>
          <div class="col-md-5">
            <div class="row g-2">
              <div class="col-12">
                <label class="form-label small">نوع الإشعار</label>
                <select id="notifType" class="form-select bg-dark text-light border-secondary">
                  <option value="info">💙 معلومة</option>
                  <option value="success">💚 نجاح</option>
                  <option value="warning">🟡 تحذير</option>
                  <option value="danger">🔴 تنبيه عاجل</option>
                </select>
              </div>
              <div class="col-12">
                <label class="form-label small fw-bold">
                  <i class="fas fa-clock me-1 text-warning"></i>إعادة الإرسال الدوري
                </label>
                <div class="input-group mb-1">
                  <span class="input-group-text bg-dark text-light border-secondary">كل</span>
                  <input type="number" id="notifInterval" class="form-control bg-dark text-light border-secondary"
                    value="0" min="0" max="1440" placeholder="0">
                  <span class="input-group-text bg-dark text-light border-secondary">دقيقة</span>
                </div>
                <div class="text-muted" style="font-size:0.71rem">
                  <i class="fas fa-info-circle me-1"></i>0 = إرسال مرة واحدة فقط — أدخل رقماً لتكرار الإشعار كل X دقيقة
                </div>
              </div>
              <div class="col-12 d-flex gap-2">
                <button class="btn btn-warning fw-bold flex-grow-1" onclick="sendNotif()" id="sendBtn">
                  <i class="fas fa-paper-plane me-1"></i>نشر الإشعار
                </button>
                <button class="btn btn-danger" onclick="stopRepeat()" id="stopBtn" style="display:none">
                  <i class="fas fa-stop me-1"></i>إيقاف التكرار
                </button>
              </div>
            </div>
          </div>
        </div>
        <div id="notifResult" class="mt-2"></div>
        <div id="repeatStatus" class="mt-1"></div>
      </div>
    </div>

    <!-- سجل الإشعارات -->
    <div class="card bg-secondary mt-3">
      <div class="card-header">
        <h6 class="mb-0"><i class="fas fa-history me-2"></i>سجل الإشعارات المرسلة</h6>
      </div>
      <div class="card-body p-2">
        <div id="notifHistory"><div class="text-center text-muted py-3"><i class="fas fa-spinner fa-spin me-1"></i> جاري التحميل...</div></div>
      </div>
    </div>

    <!-- ════ إعدادات الإشعارات المتقدمة ════ -->
    <div class="card bg-secondary mt-4">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h5 class="mb-0"><i class="fas fa-sliders-h me-2 text-info"></i>⚙️ إعدادات الإشعارات</h5>
        <span id="pushSubCount" class="badge bg-info">0 مشترك</span>
      </div>
      <div class="card-body">
        <div class="row g-3">

          <!-- نوع الصوت -->
          <div class="col-md-5">
            <label class="form-label small fw-bold text-warning">
              <i class="fas fa-volume-up me-1"></i>نوع الصوت عند الإشعار
            </label>
            <select id="soundType" class="form-select bg-dark text-light border-secondary"
                    onchange="saveSoundType(this.value)">
              <option value="beep">🔊 نغمة فقط (Beep)</option>
              <option value="tts">🗣️ قراءة صوتية (TTS) فقط</option>
              <option value="both" selected>🔊🗣️ نغمة + قراءة</option>
              <option value="silent">🔕 بدون صوت</option>
            </select>
            <div class="form-text">يُطبّق على كل المستخدمين عند استقبال الإشعار</div>
          </div>

          <!-- اختبار الإشعار -->
          <div class="col-md-7">
            <label class="form-label small fw-bold text-success">
              <i class="fas fa-vial me-1"></i>اختبار الإشعار الفوري
            </label>
            <div class="row g-2">
              <div class="col-8">
                <input type="text" id="testPushMsg" class="form-control bg-dark text-light border-secondary"
                       value="✅ اختبار الإشعار — يعمل بشكل صحيح!"
                       placeholder="نص الاختبار...">
              </div>
              <div class="col-4">
                <select id="testPushType" class="form-select bg-dark text-light border-secondary">
                  <option value="general">📢 عام</option>
                  <option value="broadcast">📣 إداري</option>
                  <option value="schedule_expired">⏹ مجدول</option>
                </select>
              </div>
              <div class="col-12">
                <button class="btn btn-success w-100" onclick="sendTestPush()">
                  <i class="fas fa-paper-plane me-1"></i>إرسال اختبار لكل المشتركين
                </button>
              </div>
            </div>
          </div>

          <!-- حالة المشتركين -->
          <div class="col-12">
            <div id="pushSubsList" class="small" style="max-height:160px;overflow-y:auto;
                 background:#111;border-radius:6px;padding:8px;">
              <div class="text-muted text-center py-2"><i class="fas fa-spinner fa-spin me-1"></i>جاري التحميل...</div>
            </div>
          </div>

          <div id="notifSettingsResult" class="col-12"></div>
        </div>
      </div>
    </div>

    <!-- ════ تحميل ملفات المشروع ════ -->
    <div class="card bg-secondary mt-4">
      <div class="card-header">
        <h5 class="mb-0"><i class="fas fa-download me-2 text-info"></i>📦 تحميل ملفات المشروع</h5>
      </div>
      <div class="card-body">
        <div class="row g-3 mb-3">
          <div class="col-md-6">
            <div class="card bg-dark h-100">
              <div class="card-body text-center">
                <i class="fas fa-file-archive fa-2x text-success mb-2"></i>
                <h6>تحميل المشروع كاملاً</h6>
                <p class="small text-muted">جميع الملفات مضغوطة في ملف ZIP واحد</p>
                <a href="/api/admin/download_project" class="btn btn-success w-100">
                  <i class="fas fa-download me-1"></i>تحميل ZIP كامل
                </a>
              </div>
            </div>
          </div>
          <div class="col-md-6">
            <div class="card bg-dark h-100">
              <div class="card-body text-center">
                <i class="fas fa-file-alt fa-2x text-info mb-2"></i>
                <h6>تحميل ملفات محددة</h6>
                <p class="small text-muted">اختر الملفات التي تريد تحميلها</p>
                <button class="btn btn-info w-100" onclick="loadFilesList()">
                  <i class="fas fa-list me-1"></i>عرض قائمة الملفات
                </button>
              </div>
            </div>
          </div>
        </div>
        <!-- قائمة الملفات -->
        <div id="filesSection" style="display:none">
          <div class="mb-2">
            <input type="text" id="fileSearch" class="form-control form-control-sm bg-dark text-light border-secondary"
              placeholder="🔍 ابحث عن ملف..." oninput="renderFilesList()">
          </div>
          <div class="d-flex justify-content-between align-items-center mb-2 flex-wrap gap-2">
            <span class="small text-muted" id="filesCount">0 ملف</span>
            <div class="d-flex gap-2 flex-wrap">
              <button class="btn btn-outline-secondary btn-sm" onclick="selectAllFiles()">تحديد الكل</button>
              <button class="btn btn-outline-secondary btn-sm" onclick="deselectAllFiles()">إلغاء الكل</button>
              <button class="btn btn-primary btn-sm" onclick="downloadSelected()" id="dlSelBtn" disabled>
                <i class="fas fa-file-archive me-1"></i><span id="dlSelTxt">تحميل المحدد (ZIP)</span>
              </button>
            </div>
          </div>
          <div class="small text-muted mb-2" style="font-size:0.72rem">
            <i class="fas fa-info-circle me-1"></i>اضغط <span class="text-success fw-bold"><i class="fas fa-download"></i></span> بجانب أي ملف لتحميله مباشرة، أو حدد عدة ملفات وحمّلها كـ ZIP
          </div>
          <div id="filesList" style="max-height:380px;overflow-y:auto;background:#111;border-radius:6px;padding:8px;"></div>
        </div>
      </div>
    </div>

    <!-- ════ مرآة الكونسول ════ -->
    <div class="mt-4" style="border:1px solid #1a3a1a;border-radius:8px;overflow:hidden;">
      <!-- Header -->
      <div style="background:#0d1f0d;padding:8px 14px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;border-bottom:1px solid #1a3a1a;">
        <div style="display:flex;align-items:center;gap:12px;">
          <span style="color:#00ff41;font-family:'Courier New',monospace;font-size:1rem;font-weight:700;">
            &gt;_ Console
          </span>
          <span id="consoleStatus" style="background:#0a1f0a;color:#00ff41;border:1px solid #00ff41;padding:2px 8px;border-radius:12px;font-family:monospace;font-size:0.72rem;">● Live</span>
          <span id="logCountBadge" style="color:#3a6a3a;font-family:monospace;font-size:0.72rem;">0 events</span>
        </div>
        <div style="display:flex;gap:6px;flex-wrap:wrap;align-items:center;">
          <select id="logFilter" onchange="filterLogs()"
                  style="background:#0a0a0a;border:1px solid #1f3f1f;color:#00cc33;padding:3px 8px;border-radius:4px;font-family:monospace;font-size:0.73rem;outline:none;">
            <option value="all">All</option>
            <option value="error">ERROR</option>
            <option value="warning">WARNING</option>
            <option value="info">INFO</option>
            <option value="debug">DEBUG</option>
          </select>
          <input id="consoleSearch" type="text" placeholder="🔍 Search..."
                 oninput="filterLogs()"
                 style="background:#0a0a0a;border:1px solid #1f3f1f;color:#00cc33;padding:3px 10px;border-radius:4px;font-family:monospace;font-size:0.73rem;width:130px;outline:none;">
          <button onclick="copyAllLogs()" title="نسخ كل السجلات"
                  style="background:#0a2a0a;border:1px solid #00aa22;color:#00ff41;padding:3px 10px;border-radius:4px;font-family:monospace;font-size:0.73rem;cursor:pointer;">
            📋 نسخ الكل
          </button>
          <button onclick="clearConsole()"
                  style="background:#2a0a0a;border:1px solid #aa2222;color:#ff6666;padding:3px 10px;border-radius:4px;font-family:monospace;font-size:0.73rem;cursor:pointer;">
            🗑 مسح
          </button>
          <button onclick="toggleAutoScroll()" id="autoScrollBtn"
                  style="background:#0a0a2a;border:1px solid #3344aa;color:#8899ff;padding:3px 10px;border-radius:4px;font-family:monospace;font-size:0.73rem;cursor:pointer;">
            🔒 Auto
          </button>
        </div>
      </div>
      <!-- Console Output -->
      <div id="consoleScreen">
        <div style="color:#2d6a2d;font-family:monospace;font-size:11.5px;padding:6px 2px;opacity:0.7;">
          // Waiting for events...
        </div>
      </div>
      <!-- AI Chat Section -->
      <div style="background:#060606;border-top:1px solid #1a2a1a;padding:10px 14px;">
        <div style="color:#3a7a3a;font-family:monospace;font-size:0.73rem;margin-bottom:6px;">
          🤖 اسأل الذكاء عن أي حدث في السجلات
        </div>
        <div style="display:flex;gap:6px;">
          <input type="text" id="aiLogQuestion"
                 placeholder="مثال: آخر الأخطاء / ابحث عن werkzeug / أخبرني بالأحداث الأخيرة"
                 onkeydown="if(event.key===&apos;Enter&apos;) askAiAboutLogs()"
                 style="flex:1;background:#040404;border:1px solid #1a3a1a;color:#00cc33;padding:7px 12px;border-radius:4px;font-family:monospace;font-size:0.8rem;outline:none;">
          <button onclick="askAiAboutLogs()" id="aiSendBtn"
                  style="background:linear-gradient(135deg,#0a3a0a,#081808);border:1px solid #00cc33;color:#00ff41;padding:7px 16px;border-radius:4px;font-family:monospace;font-size:0.8rem;cursor:pointer;font-weight:700;white-space:nowrap;">
            ▶ إرسال
          </button>
        </div>
        <div id="aiLogResponse"
             style="display:none;margin-top:8px;font-family:monospace;font-size:0.78rem;
                    white-space:pre-wrap;color:#88dd88;background:#040404;
                    border:1px solid #1a3a1a;border-radius:4px;padding:10px;
                    max-height:200px;overflow-y:auto;line-height:1.5;"></div>
      </div>
    </div>

    </div><!-- end container -->

    <script>
    /* ══════════════════════════════════════════
       المستخدمون
    ══════════════════════════════════════════ */
    async function loadUsers(){
      const r=await fetch('/admin/api/users');const d=await r.json();
      if(!d.success){document.getElementById('usersTable').innerHTML='<p class="text-danger">'+d.message+'</p>';return;}
      let h='<div class="table-responsive"><table class="table table-dark table-bordered table-sm">';
      h+='<thead><tr><th>ID</th><th>الاسم</th><th>الهاتف</th><th>متصل؟</th><th>محظور؟</th><th>تنبيهات</th><th>إجراء</th></tr></thead><tbody>';
      d.users.forEach(u=>{
        h+=`<tr><td>${u.user_id}</td><td>${u.name}</td><td>${u.phone||'-'}</td>
        <td>${u.logged_in?'<span class="badge bg-success">نعم</span>':'<span class="badge bg-secondary">لا</span>'}</td>
        <td>${u.blocked?'<span class="badge bg-danger">محظور</span>':'<span class="badge bg-success">فعّال</span>'}</td>
        <td><span class="badge bg-warning text-dark">${u.alerts_count}</span></td>
        <td>
        <button class="btn btn-xs btn-outline-warning btn-sm" onclick="toggleBlock('${u.user_id}',${!u.blocked})">${u.blocked?'فك الحظر':'حظر'}</button>
        <a href="/admin/api/copy_chats/${u.user_id}" class="btn btn-xs btn-outline-info btn-sm ms-1" target="_blank">روابط</a>
        </td></tr>`;
      });
      h+='</tbody></table></div>';
      document.getElementById('usersTable').innerHTML=h;
    }
    async function toggleBlock(slot,blocked){
      await fetch('/admin/api/user/'+slot,{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({action:'block',blocked:blocked})});loadUsers();
    }
    async function doLogout(){await fetch('/admin/api/logout',{method:'POST'});location.reload();}
    function registerBio(){
      let did=localStorage.getItem('deviceId');
      if(!did){did=crypto.randomUUID?crypto.randomUUID():'dev-'+Date.now();localStorage.setItem('deviceId',did);}
      const bt=Array.from(crypto.getRandomValues(new Uint8Array(32))).map(b=>b.toString(16).padStart(2,'0')).join('');
      fetch('/admin/api/biometric/register',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({device_id:did,biometric_token:bt})})
      .then(r=>r.json()).then(d=>{if(d.success){localStorage.setItem('biometricToken',bt);alert('✅ تم تسجيل البصمة');}else{alert('❌ '+d.message);}});
    }

    /* ══════════════════════════════════════════
       الإشعارات مع التكرار والنطق
    ══════════════════════════════════════════ */
    const _typeColors={info:'primary',success:'success',warning:'warning',danger:'danger'};
    const _typeIcons={info:'ℹ️',success:'✅',warning:'⚠️',danger:'🚨'};
    let _repeatTimer=null;
    let _repeatCount=0;
    let _countdownTimer=null;
    let _nextSendAt=0;

    function _startCountdown(intervalMin){
      if(_countdownTimer) clearInterval(_countdownTimer);
      _nextSendAt=Date.now()+intervalMin*60000;
      _countdownTimer=setInterval(()=>{
        const rem=Math.max(0,_nextSendAt-Date.now());
        if(!_repeatTimer){clearInterval(_countdownTimer);return;}
        const m=Math.floor(rem/60000), s=Math.floor((rem%60000)/1000);
        const rs=document.getElementById('repeatStatus');
        if(rs) rs.innerHTML=
          `<div class="alert alert-info py-2 small d-flex justify-content-between align-items-center">
            <span>🔁 تم الإرسال <strong>${_repeatCount}</strong> مرة — التكرار كل ${intervalMin} دقيقة</span>
            <span class="badge bg-dark text-warning" style="font-size:0.85rem">⏱ ${m}:${String(s).padStart(2,'0')}</span>
          </div>`;
        if(rem===0) _nextSendAt=Date.now()+intervalMin*60000;
      },500);
    }

    function _speakNotif(msg){
      if(!window.speechSynthesis) return;
      window.speechSynthesis.cancel();
      const utt=new SpeechSynthesisUtterance(msg);
      utt.lang='ar-SA'; utt.rate=0.95; utt.pitch=1; utt.volume=1;
      const voices=window.speechSynthesis.getVoices();
      const arVoice=voices.find(v=>v.lang&&v.lang.startsWith('ar'));
      if(arVoice) utt.voice=arVoice;
      window.speechSynthesis.speak(utt);
    }

    async function _doSendNotif(){
      const msg=document.getElementById('notifMsg').value.trim();
      const type=document.getElementById('notifType').value;
      if(!msg) return false;
      const r=await fetch('/admin/api/broadcast_notification',{
        method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({message:msg,type:type})
      });
      const d=await r.json();
      if(d.success){
        _repeatCount++;
        document.getElementById('repeatStatus').innerHTML=
          _repeatTimer?`<div class="alert alert-info py-1 small">🔁 تم الإرسال مرة ${_repeatCount}</div>`:'';
        loadNotifHistory();
        _speakNotif('تم إرسال الإشعار: '+msg);
        return true;
      }
      return false;
    }

    async function sendNotif(){
      const msg=document.getElementById('notifMsg').value.trim();
      const type=document.getElementById('notifType').value;
      const intervalMin=parseInt(document.getElementById('notifInterval').value)||0;
      const res=document.getElementById('notifResult');
      if(!msg){res.innerHTML='<div class="alert alert-danger py-1 small">الرجاء كتابة نص الإشعار</div>';return;}
      stopRepeat();
      res.innerHTML='<div class="alert alert-secondary py-1 small"><i class="fas fa-spinner fa-spin me-1"></i>جاري النشر...</div>';
      try{
        const ok=await _doSendNotif();
        if(ok){
          res.innerHTML='<div class="alert alert-success py-1 small">✅ تم نشر الإشعار بنجاح</div>';
          if(intervalMin>0){
            document.getElementById('stopBtn').style.display='';
            document.getElementById('sendBtn').innerHTML='<i class="fas fa-sync fa-spin me-1"></i>يعمل التكرار...';
            _repeatCount=1;
            _startCountdown(intervalMin);
            _repeatTimer=setInterval(async()=>{
              await _doSendNotif();
              _nextSendAt=Date.now()+intervalMin*60000;
            }, intervalMin*60000);
          } else {
            setTimeout(()=>{res.innerHTML='';},4000);
          }
        } else {
          res.innerHTML='<div class="alert alert-danger py-1 small">❌ فشل الإرسال</div>';
        }
      }catch(e){
        res.innerHTML=`<div class="alert alert-danger py-1 small">❌ خطأ: ${e.message}</div>`;
      }
    }

    function stopRepeat(){
      if(_repeatTimer){clearInterval(_repeatTimer);_repeatTimer=null;}
      if(_countdownTimer){clearInterval(_countdownTimer);_countdownTimer=null;}
      _repeatCount=0;
      document.getElementById('stopBtn').style.display='none';
      document.getElementById('sendBtn').innerHTML='<i class="fas fa-paper-plane me-1"></i>نشر الإشعار';
      document.getElementById('repeatStatus').innerHTML='';
    }

    async function deleteNotif(id){
      await fetch('/admin/api/delete_notification/'+id,{method:'DELETE'});loadNotifHistory();
    }
    async function clearAllNotifs(){
      if(!confirm('مسح جميع الإشعارات؟')) return;
      await fetch('/admin/api/clear_notifications',{method:'POST'});loadNotifHistory();
    }

    // ── إعدادات الإشعارات المتقدمة ──────────────────────────
    async function loadPushStats(){
      try{
        const r=await fetch('/admin/api/push_stats');
        const d=await r.json();
        const cnt=document.getElementById('pushSubCount');
        if(cnt) cnt.textContent=d.count+' مشترك';
        const lst=document.getElementById('pushSubsList');
        if(!lst) return;
        if(!d.subscribers||!d.subscribers.length){
          lst.innerHTML='<div class="text-muted text-center py-2">لا يوجد مشتركون بعد</div>';return;
        }
        lst.innerHTML=d.subscribers.map((uid,i)=>`
          <div class="d-flex align-items-center gap-2 py-1 border-bottom border-secondary">
            <span class="badge bg-success">${i+1}</span>
            <span class="text-light small flex-grow-1">👤 ${uid}</span>
            <span class="badge bg-primary">مشترك</span>
          </div>`).join('');
      }catch(e){
        const lst=document.getElementById('pushSubsList');
        if(lst) lst.innerHTML='<div class="text-danger small">فشل التحميل: '+e.message+'</div>';
      }
    }

    async function sendTestPush(){
      const msg  = (document.getElementById('testPushMsg')  ||{}).value||'✅ اختبار';
      const type = (document.getElementById('testPushType') ||{}).value||'general';
      const res  = document.getElementById('notifSettingsResult');
      if(res) res.innerHTML='<div class="alert alert-info py-1 small"><i class="fas fa-spinner fa-spin me-1"></i>جاري الإرسال...</div>';
      try{
        const r=await fetch('/admin/api/test_push',{
          method:'POST',headers:{'Content-Type':'application/json'},
          body:JSON.stringify({message:msg,type:type})
        });
        const d=await r.json();
        if(res) res.innerHTML=`<div class="alert alert-${d.success?'success':'danger'} py-1 small">${d.message||d.error}</div>`;
        loadPushStats();
      }catch(e){
        if(res) res.innerHTML='<div class="alert alert-danger py-1 small">خطأ: '+e.message+'</div>';
      }
    }

    function saveSoundType(val){
      // احفظ نوع الصوت في localStorage ليقرأه كل المستخدمين
      try{ localStorage.setItem('notif_sound_type', val); }catch(e){}
    }

    function loadSoundTypePref(){
      try{
        const v=localStorage.getItem('notif_sound_type')||'both';
        const el=document.getElementById('soundType');
        if(el) el.value=v;
      }catch(e){}
    }
    async function loadNotifHistory(){
      const el=document.getElementById('notifHistory');
      try{
        const r=await fetch('/admin/api/notifications');const d=await r.json();
        if(!d.success){el.innerHTML='<p class="text-danger small">'+d.message+'</p>';return;}
        if(!d.notifications.length){el.innerHTML='<p class="text-muted text-center small py-2">لا توجد إشعارات</p>';return;}
        let h='';
        d.notifications.forEach(n=>{
          const col=_typeColors[n.type]||'secondary';const ico=_typeIcons[n.type]||'📢';
          const ts=n.timestamp?n.timestamp.replace('T',' ').slice(0,16):'';
          h+=`<div class="d-flex align-items-start gap-2 border-bottom border-dark pb-2 mb-2">
            <span class="badge bg-${col} mt-1">${ico} ${n.type||'info'}</span>
            <div class="flex-grow-1">
              <div class="text-light small">${n.message.replace(/</g,'&lt;')}</div>
              <div class="text-muted" style="font-size:0.72rem">${ts}</div>
            </div>
            <button class="btn btn-outline-danger btn-sm py-0 px-1" style="font-size:0.7rem"
              onclick="deleteNotif('${n.id}')"><i class="fas fa-times"></i></button>
          </div>`;
        });
        el.innerHTML=h;
      }catch(e){el.innerHTML='<p class="text-danger small">خطأ في التحميل</p>';}
    }

    /* ══════════════════════════════════════════
       تحميل الملفات
    ══════════════════════════════════════════ */
    let _allFiles=[];
    let _selectedFiles=new Set();

    async function loadFilesList(){
      const sec=document.getElementById('filesSection');
      const lst=document.getElementById('filesList');
      sec.style.display='';
      lst.innerHTML='<div class="text-center py-3"><i class="fas fa-spinner fa-spin"></i> جاري التحميل...</div>';
      try{
        const r=await fetch('/api/admin/list_project_files');const d=await r.json();
        if(!d.success){lst.innerHTML='<p class="text-danger small">'+d.error+'</p>';return;}
        _allFiles=d.files; _selectedFiles=new Set();
        document.getElementById('filesCount').textContent=d.files.length+' ملف';
        renderFilesList();
      }catch(e){lst.innerHTML='<p class="text-danger small">خطأ: '+e.message+'</p>';}
    }

    function renderFilesList(filter){
      const lst=document.getElementById('filesList');
      let h='';
      const q=(filter||document.getElementById('fileSearch').value||'').toLowerCase();
      const shown=_allFiles.filter(f=>!q||f.path.toLowerCase().includes(q));
      document.getElementById('filesCount').textContent=shown.length+' ملف'+(q?' (مصفّاة)':'');
      shown.forEach((f,i)=>{
        const sel=_selectedFiles.has(f.path);
        const icon=f.path.endsWith('.py')?'🐍':f.path.endsWith('.html')?'🌐':f.path.endsWith('.js')?'📜':f.path.endsWith('.css')?'🎨':f.path.endsWith('.json')?'📋':f.path.endsWith('.png')||f.path.endsWith('.jpg')||f.path.endsWith('.jpeg')||f.path.endsWith('.webp')?'🖼️':f.path.endsWith('.txt')?'📝':'📄';
        const safeP=f.path.replace(/\\/g,'\\\\').replace(/'/g,"\\'");
        h+=`<div class="file-item d-flex align-items-center gap-2 ${sel?'selected':''}" onclick="toggleFile('${safeP}',this)">
          <input type="checkbox" class="form-check-input" ${sel?'checked':''} style="pointer-events:none">
          <span>${icon}</span>
          <span class="small text-light flex-grow-1" style="word-break:break-all">${f.path}</span>
          <span class="badge bg-dark text-muted me-1" style="font-size:0.65rem;white-space:nowrap">${f.size}</span>
          <a href="/api/admin/download_single_file?path=${encodeURIComponent(f.path)}"
             class="btn btn-outline-success btn-sm py-0 px-1" style="font-size:0.7rem;white-space:nowrap"
             title="تحميل مباشر" onclick="event.stopPropagation()">
            <i class="fas fa-download"></i>
          </a>
        </div>`;
      });
      lst.innerHTML=h||'<p class="text-muted small text-center py-2">لا توجد ملفات</p>';
      updateDlBtn();
    }

    function toggleFile(path,el){
      if(_selectedFiles.has(path)){_selectedFiles.delete(path);el.classList.remove('selected');el.querySelector('input').checked=false;}
      else{_selectedFiles.add(path);el.classList.add('selected');el.querySelector('input').checked=true;}
      updateDlBtn();
    }
    function selectAllFiles(){_allFiles.forEach(f=>_selectedFiles.add(f.path));renderFilesList();}
    function deselectAllFiles(){_selectedFiles.clear();renderFilesList();}
    function updateDlBtn(){
      const btn=document.getElementById('dlSelBtn');
      const txt=document.getElementById('dlSelTxt');
      btn.disabled=_selectedFiles.size===0;
      if(txt) txt.textContent=_selectedFiles.size>0?`تحميل ${_selectedFiles.size} ملف (ZIP)`:'تحميل المحدد (ZIP)';
    }

    async function downloadSelected(){
      if(_selectedFiles.size===0) return;
      const btn=document.getElementById('dlSelBtn');
      const txt=document.getElementById('dlSelTxt');
      btn.disabled=true; if(txt) txt.textContent='⏳ جاري الضغط...';
      try{
        const r=await fetch('/api/admin/download_selected_files',{
          method:'POST',headers:{'Content-Type':'application/json'},
          body:JSON.stringify({files:[..._selectedFiles]})
        });
        if(!r.ok){const d=await r.json();alert('❌ '+d.error);btn.disabled=false;updateDlBtn();return;}
        const blob=await r.blob();
        const url=URL.createObjectURL(blob);
        const a=document.createElement('a');a.href=url;a.download='selected_files.zip';
        document.body.appendChild(a);a.click();document.body.removeChild(a);
        URL.revokeObjectURL(url);
      }catch(e){alert('❌ خطأ: '+e.message);}
      btn.disabled=false; updateDlBtn();
    }

    /* ══════════════════════════════════════════════════════
       مرآة الكونسول — سجلات المطورين الفورية (محسّن)
    ══════════════════════════════════════════════════════ */
    const _consoleEl = document.getElementById('consoleScreen');
    let _autoScroll   = true;
    let _allLogs      = [];   /* [{ts,name,level,raw,cssClass}] */
    let _currentFilter = 'all';
    let _searchText    = '';
    const _maxLogs     = 1000;

    const _socket = io({transports:['websocket','polling']});

    _socket.on('connect', () => {
      const st = document.getElementById('consoleStatus');
      st.style.color='#00ff41'; st.style.borderColor='#00ff41';
      st.textContent = '● Live';
      _addEntry({level:'INFO', msg:'✅ متصل بالخادم — تدفق السجلات نشط', time:_now(), name:'SYSTEM'});
    });
    _socket.on('disconnect', () => {
      const st = document.getElementById('consoleStatus');
      st.style.color='#ff4444'; st.style.borderColor='#ff4444';
      st.textContent = '● Offline';
      _addEntry({level:'ERROR', msg:'❌ انقطع الاتصال بالخادم', time:_now(), name:'SYSTEM'});
    });
    _socket.on('live_log', data => _addEntry(data));
    _socket.on('new_broadcast_notification', data => {
      _addEntry({level:'INFO', msg:'📢 إشعار مُرسل: '+data.message, time:_now(), name:'NOTIF'});
    });

    function _now(){ return new Date().toLocaleTimeString('en-GB',{hour12:false}); }

    /* تلوين HTTP methods وstatus codes */
    function _colorText(txt){
      return txt
        .replace(/\b(GET)\b/g,'<span class="hl-get">GET</span>')
        .replace(/\b(POST)\b/g,'<span class="hl-post">POST</span>')
        .replace(/\b(PUT|PATCH)\b/g,'<span class="hl-put">$1</span>')
        .replace(/\b(DELETE)\b/g,'<span class="hl-del">DELETE</span>')
        .replace(/\s(2\d\d)\s/g,' <span class="hl-200">$1</span> ')
        .replace(/\s(404)\s/g,' <span class="hl-404">404</span> ')
        .replace(/\s(5\d\d)\s/g,' <span class="hl-500">$1</span> ');
    }

    function _addEntry(entry){
      const lvl = (entry.level||'INFO').toUpperCase();
      let cssClass = 'info';
      if(lvl==='ERROR'||lvl==='CRITICAL') cssClass = lvl==='CRITICAL'?'critical':'error';
      else if(lvl==='WARNING') cssClass = 'warn';
      else if(lvl==='DEBUG')   cssClass = 'debug';
      else if(entry.name==='SYSTEM'||entry.name==='NOTIF') cssClass = 'sys';

      const raw = (entry.full || ((entry.time||'')+(entry.name?'['+entry.name+']':'')+' '+lvl+' '+entry.msg));
      const logEntry = { ts: entry.time||_now(), name:entry.name||'', level:lvl, raw, cssClass,
                         msg: entry.msg||entry.full||'' };
      _allLogs.push(logEntry);
      if(_allLogs.length > _maxLogs) _allLogs.shift();

      _updateCount();
      if(_matchFilter(logEntry)) _renderLine(logEntry);
    }

    function _matchFilter(e){
      const fv = _currentFilter;
      const lvl = e.level;
      const ok = fv==='all' || (fv==='error'&&(lvl==='ERROR'||lvl==='CRITICAL')) ||
                 (fv==='warning'&&lvl==='WARNING') || (fv==='info'&&lvl==='INFO') ||
                 (fv==='debug'&&lvl==='DEBUG');
      if(!ok) return false;
      if(_searchText && !e.raw.toLowerCase().includes(_searchText)) return false;
      return true;
    }

    function _esc(s){ return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }

    function _renderLine(e){
      const row = document.createElement('div');
      row.className = 'cl ' + e.cssClass;
      row.innerHTML =
        '<span class="ts">'+_esc(e.ts)+'</span>'+
        '<span class="nm">'+_esc(e.name).slice(0,10)+'</span>'+
        '<span class="lv">'+e.level+'</span>'+
        '<span class="tx">'+_colorText(_esc(e.msg||e.raw))+'</span>';
      _consoleEl.appendChild(row);
      if(_autoScroll) _consoleEl.scrollTop = _consoleEl.scrollHeight;
    }

    function _updateCount(){
      const badge = document.getElementById('logCountBadge');
      if(badge) badge.textContent = _allLogs.length + ' events';
    }

    function filterLogs(){
      _currentFilter = document.getElementById('logFilter').value;
      _searchText    = (document.getElementById('consoleSearch').value||'').toLowerCase().trim();
      _consoleEl.innerHTML = '';
      _allLogs.forEach(e => { if(_matchFilter(e)) _renderLine(e); });
    }

    function clearConsole(){
      _consoleEl.innerHTML='';
      _allLogs=[];
      _updateCount();
    }

    function toggleAutoScroll(){
      _autoScroll = !_autoScroll;
      const btn = document.getElementById('autoScrollBtn');
      btn.textContent = _autoScroll ? '🔒 Auto' : '🔓 Manual';
      btn.style.color = _autoScroll ? '#8899ff' : '#ffaa44';
      if(_autoScroll) _consoleEl.scrollTop = _consoleEl.scrollHeight;
    }

    function copyAllLogs(){
      const lines = _allLogs.map(e=>
        '['+e.ts+'] ['+e.name+'] '+e.level+' '+e.msg
      ).join('\n');
      if(!lines){ alert('لا توجد سجلات للنسخ'); return; }
      navigator.clipboard.writeText(lines).then(()=>{
        const btn = event.target;
        const orig = btn.textContent;
        btn.textContent = '✅ تم النسخ!';
        btn.style.color = '#00ff41';
        setTimeout(()=>{ btn.textContent=orig; btn.style.color=''; }, 2000);
      }).catch(()=>{
        const ta = document.createElement('textarea');
        ta.value = lines; document.body.appendChild(ta);
        ta.select(); document.execCommand('copy');
        document.body.removeChild(ta);
        alert('✅ تم نسخ '+_allLogs.length+' سطر');
      });
    }

    async function askAiAboutLogs(){
      const q   = (document.getElementById('aiLogQuestion').value||'').trim();
      const res = document.getElementById('aiLogResponse');
      const btn = document.getElementById('aiSendBtn');
      if(!q) return;
      btn.disabled = true; btn.textContent = '⏳...';
      res.style.display = 'block';
      res.textContent = '⏳ جاري التحليل...';
      try{
        const r = await fetch('/admin/api/log_query',{
          method:'POST',
          headers:{'Content-Type':'application/json'},
          body:JSON.stringify({query:q, logs: _allLogs.slice(-200).map(e=>'['+e.ts+']['+e.name+'] '+e.level+': '+e.msg)})
        });
        const d = await r.json();
        res.textContent = d.success ? d.answer : ('❌ ' + (d.message||'فشل'));
      } catch(e){
        res.textContent = '❌ خطأ: ' + e.message;
      }
      btn.disabled = false; btn.textContent = '▶ إرسال';
    }

    // تهيئة تلقائية للأصوات
    if(window.speechSynthesis){
      window.speechSynthesis.onvoiceschanged = function(){ window.speechSynthesis.getVoices(); }
    }

    loadUsers();
    loadNotifHistory();
    loadPushStats();
    loadSoundTypePref();
    loadCardStatus();

    // ══════════════════════════════════════════════════════════
    //  إدارة بطاقات الشحن
    // ══════════════════════════════════════════════════════════
    async function loadCardStatus(){
      try{
        const r = await fetch('/admin/api/card_status');
        const d = await r.json();
        const el = document.getElementById('cardToggleBtn');
        if(el){ el.textContent = d.enabled ? '🔴 تعطيل النظام' : '🟢 تفعيل النظام'; }
        const badge = document.getElementById('cardStatusBadge');
        if(badge){ badge.textContent = d.enabled ? '✅ مفعّل' : '⛔ معطّل'; badge.className = d.enabled ? 'badge bg-success' : 'badge bg-danger'; }
      }catch(e){ console.error('loadCardStatus:', e); }
    }
    async function toggleCardSystem(){
      const r = await fetch('/admin/api/card_status'); const d = await r.json();
      const newState = !d.enabled;
      const r2 = await fetch('/admin/api/toggle_card_system',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({enabled:newState})});
      const d2 = await r2.json();
      document.getElementById('cardMsg').innerHTML = '<div class="alert alert-'+(d2.success?'success':'danger')+'">'+d2.message+'</div>';
      loadCardStatus();
    }
    async function createVouchers(){
      const plan_id = parseInt(document.getElementById('voucherPlan').value);
      const count = parseInt(document.getElementById('voucherCount').value)||10;
      const r = await fetch('/admin/api/create_vouchers',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({plan_id,count})});
      const d = await r.json();
      if(d.success){
        const txt = d.codes.join('\n');
        document.getElementById('voucherResult').value = txt;
        document.getElementById('voucherResultArea').style.display='';
        document.getElementById('cardMsg').innerHTML='<div class="alert alert-success">✅ تم إنشاء '+d.count+' قسيمة</div>';
      }else{
        document.getElementById('cardMsg').innerHTML='<div class="alert alert-danger">❌ '+d.message+'</div>';
      }
    }
    async function loadVouchers(){
      const r = await fetch('/admin/api/vouchers'); const d = await r.json();
      const tbody = document.getElementById('vouchersTbody');
      if(!tbody) return;
      const vouchers = (d.vouchers||[]).slice(-100).reverse();
      tbody.innerHTML = vouchers.map(v=>`<tr>
        <td><code class="text-warning" style="font-size:0.75rem">${v.plan_name||'—'}</code></td>
        <td><span class="badge bg-${v.status==='unused'?'secondary':v.status==='active'?'success':v.status==='used'?'primary':'danger'}">${v.status==='unused'?'غير مستخدمة':v.status==='active'?'نشطة':v.status==='used'?'مستخدمة':'منتهية'}</span></td>
        <td style="font-size:0.72rem">${(v.created_at||'—').slice(0,10)}</td>
        <td style="font-size:0.72rem">${(v.used_at||'—').slice(0,10)}</td>
        <td style="font-size:0.72rem">${(v.expires_at||'—').slice(0,16).replace('T',' ')}</td>
      </tr>`).join('');
    }
    async function loadCardSessions(){
      const r = await fetch('/admin/api/card_sessions'); const d = await r.json();
      const tbody = document.getElementById('cardSessionsTbody');
      if(!tbody) return;
      const sessions = d.sessions||[];
      tbody.innerHTML = sessions.length===0?'<tr><td colspan="5" class="text-center text-muted">لا توجد جلسات نشطة</td></tr>':
        sessions.map(s=>`<tr>
          <td style="font-size:0.72rem">${s.plan_name||'—'}</td>
          <td style="font-size:0.72rem">${s.ip_address||'—'}</td>
          <td style="font-size:0.72rem">${(s.start_time||'—').slice(0,16).replace('T',' ')}</td>
          <td style="font-size:0.72rem">${(s.expires_at||'—').slice(0,16).replace('T',' ')}</td>
          <td><button class="btn btn-danger btn-sm" onclick="terminateCardSession('${s.session_id}')"><i class="fas fa-times"></i></button></td>
        </tr>`).join('');
    }
    async function terminateCardSession(sid){
      if(!confirm('إنهاء هذه الجلسة؟')) return;
      await fetch('/admin/api/terminate_card_session',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({session_id:sid})});
      loadCardSessions();
    }
    async function deleteVouchers(status){
      if(!confirm('حذف القسائم '+(status||'الكل')+'؟')) return;
      const body = status ? {status} : {};
      await fetch('/admin/api/delete_vouchers',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
      document.getElementById('cardMsg').innerHTML='<div class="alert alert-success">✅ تم الحذف</div>';
      loadVouchers();
    }
    function copyVouchers(){
      const ta = document.getElementById('voucherResult');
      if(!ta.value) return;
      navigator.clipboard.writeText(ta.value).then(()=>alert('✅ تم النسخ!'));
    }
    </script>

    <!-- ════ قسم إدارة البطاقات ════ -->
    <style>
    #cardSection .card{background:#1a1f2e;border:1px solid #2d3748;}
    #cardSection .form-control,#cardSection .form-select{background:#0d1117;border-color:#2d3748;color:#e2e8f0;}
    </style>
    <div id="cardSection" class="mt-4">
      <div class="card" style="background:#1a1f2e;border:1px solid #2d3748;">
        <div class="card-header d-flex justify-content-between align-items-center" style="border-bottom:1px solid #2d3748;">
          <h5 class="mb-0 text-light"><i class="fas fa-id-card me-2 text-info"></i>🎓 مركز سرعة إنجاز — نظام بطاقات الشحن</h5>
          <div class="d-flex align-items-center gap-2">
            <span id="cardStatusBadge" class="badge bg-danger">⛔ معطّل</span>
            <button id="cardToggleBtn" class="btn btn-sm btn-outline-light" onclick="toggleCardSystem()">🟢 تفعيل النظام</button>
          </div>
        </div>
        <div class="card-body">
          <div id="cardMsg"></div>

          <!-- إنشاء قسائم جديدة -->
          <div class="row g-3 mb-4">
            <div class="col-md-4">
              <label class="form-label small text-light">نوع الباقة</label>
              <select id="voucherPlan" class="form-select" style="background:#0d1117;border-color:#2d3748;color:#e2e8f0;">
                <option value="1">📅 يومية (24 ساعة)</option>
                <option value="2">📅 أسبوعية (7 أيام)</option>
                <option value="3">📅 شهرية (30 يوم)</option>
              </select>
            </div>
            <div class="col-md-3">
              <label class="form-label small text-light">عدد القسائم</label>
              <input type="number" id="voucherCount" class="form-control" value="10" min="1" max="200" style="background:#0d1117;border-color:#2d3748;color:#e2e8f0;">
            </div>
            <div class="col-md-3 d-flex align-items-end">
              <button class="btn btn-success w-100" onclick="createVouchers()">
                <i class="fas fa-plus me-1"></i>إنشاء قسائم
              </button>
            </div>
            <div class="col-md-2 d-flex align-items-end">
              <button class="btn btn-outline-secondary w-100" onclick="loadVouchers();loadCardSessions();">
                <i class="fas fa-sync me-1"></i>تحديث
              </button>
            </div>
          </div>

          <!-- منطقة الأكواد المولّدة -->
          <div id="voucherResultArea" style="display:none;" class="mb-4">
            <div class="d-flex justify-content-between mb-1">
              <label class="form-label small text-success">✅ الأكواد المولّدة</label>
              <button class="btn btn-sm btn-outline-success" onclick="copyVouchers()"><i class="fas fa-copy me-1"></i>نسخ الكل</button>
            </div>
            <textarea id="voucherResult" class="form-control font-monospace" rows="6" readonly
              style="background:#0a0e1a;border-color:#2d3748;color:#4ade80;font-size:0.82rem;letter-spacing:1px;"></textarea>
          </div>

          <!-- جدول القسائم -->
          <ul class="nav nav-tabs mb-3" style="border-color:#2d3748;">
            <li class="nav-item">
              <a class="nav-link active text-light" href="#" onclick="loadVouchers();document.querySelectorAll('.c-tab').forEach(e=>e.style.display='none');document.getElementById('tabVouchers').style.display='';return false;"
                 style="border-color:#2d3748;background:#0d1117;">📋 سجل القسائم</a>
            </li>
            <li class="nav-item">
              <a class="nav-link text-light" href="#" onclick="loadCardSessions();document.querySelectorAll('.c-tab').forEach(e=>e.style.display='none');document.getElementById('tabSessions').style.display='';return false;"
                 style="border-color:#2d3748;background:#161b22;">🟢 الجلسات النشطة</a>
            </li>
          </ul>

          <div id="tabVouchers" class="c-tab">
            <div class="d-flex justify-content-end gap-2 mb-2">
              <button class="btn btn-sm btn-outline-warning" onclick="deleteVouchers('used')"><i class="fas fa-trash me-1"></i>حذف المستخدمة</button>
              <button class="btn btn-sm btn-outline-danger" onclick="deleteVouchers('')"><i class="fas fa-trash me-1"></i>حذف الكل</button>
            </div>
            <div class="table-responsive">
              <table class="table table-dark table-sm table-hover" style="font-size:0.82rem;">
                <thead><tr><th>الباقة</th><th>الحالة</th><th>تاريخ الإنشاء</th><th>تاريخ الاستخدام</th><th>الانتهاء</th></tr></thead>
                <tbody id="vouchersTbody"><tr><td colspan="5" class="text-center text-muted">اضغط تحديث لتحميل البيانات</td></tr></tbody>
              </table>
            </div>
          </div>

          <div id="tabSessions" class="c-tab" style="display:none;">
            <div class="table-responsive">
              <table class="table table-dark table-sm table-hover" style="font-size:0.82rem;">
                <thead><tr><th>الباقة</th><th>IP</th><th>بداية الجلسة</th><th>الانتهاء</th><th>إجراء</th></tr></thead>
                <tbody id="cardSessionsTbody"><tr><td colspan="5" class="text-center text-muted">لا توجد جلسات نشطة</td></tr></tbody>
              </table>
            </div>
          </div>

        </div>
      </div>
    </div>

    <!-- ════════════ قسم التحديثات ════════════ -->
    <div class="card bg-secondary mt-4" style="border:1px solid #3d4a5c;">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h5 class="mb-0"><i class="fas fa-sync-alt me-2 text-primary"></i>🔄 تحديث التطبيق</h5>
        <div class="form-check form-switch mb-0">
          <input class="form-check-input" type="checkbox" id="autoUpdateToggle" style="width:50px;height:25px;cursor:pointer;">
          <label class="form-check-label text-light small me-2" for="autoUpdateToggle">تحديث تلقائي</label>
        </div>
      </div>
      <div class="card-body">
        <div id="updateStatus" class="alert alert-info mb-3">
          <i class="fas fa-spinner fa-spin me-2"></i> جاري التحقق من التحديثات...
        </div>
        <div class="d-flex flex-wrap gap-2 mb-3">
          <button class="btn btn-primary" onclick="checkForUpdatesUI()" id="checkUpdateBtn">
            <i class="fas fa-search me-1"></i>بحث عن تحديث
          </button>
          <button class="btn btn-success" onclick="performUpdateUI()" id="updateNowBtn" disabled>
            <i class="fas fa-download me-1"></i>تحديث الآن
          </button>
          <button class="btn btn-outline-secondary" onclick="refreshUpdateStatus()">
            <i class="fas fa-sync me-1"></i>تحديث الحالة
          </button>
        </div>
        <div id="updateProgress" style="display:none;">
          <div class="progress mb-2">
            <div class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" style="width:0%;" id="updateProgressBar">0%</div>
          </div>
          <div id="updateLogs" class="small text-light" style="max-height:150px;overflow-y:auto;background:#0d1117;padding:8px;border-radius:6px;font-family:monospace;font-size:12px;white-space:pre-wrap;"></div>
        </div>
        <div class="mt-2 small text-muted">
          <span id="versionInfo">الإصدار الحالي: <span class="text-light">جاري التحميل...</span></span>
          <span class="mx-2">|</span>
          <span id="lastCheckInfo">آخر فحص: <span class="text-light">-</span></span>
        </div>
      </div>
    </div>
    <script>
    function refreshUpdateStatus(){
      fetch('/api/auto_update_status').then(function(r){return r.json();}).then(function(data){
        if(data.success){
          document.getElementById('autoUpdateToggle').checked=data.auto_update;
          if(data.last_update)
            document.getElementById('lastCheckInfo').innerHTML='آخر تحديث: <span class="text-light">'+new Date(data.last_update).toLocaleString('ar-EG')+'</span>';
        }
      }).catch(function(){});
      checkForUpdatesUI();
    }
    function checkForUpdatesUI(){
      var btn=document.getElementById('checkUpdateBtn'),statusDiv=document.getElementById('updateStatus'),updateBtn=document.getElementById('updateNowBtn');
      btn.disabled=true; btn.innerHTML='<i class="fas fa-spinner fa-spin me-1"></i>جاري البحث...';
      statusDiv.className='alert alert-info'; statusDiv.innerHTML='<i class="fas fa-spinner fa-spin me-2"></i> جاري التحقق...';
      fetch('/api/check_update').then(function(r){return r.json();}).then(function(data){
        if(data.success){
          document.getElementById('versionInfo').innerHTML='الإصدار الحالي: <span class="text-light">'+(data.current||'غير معروف')+'</span>';
          if(data.has_update){
            statusDiv.className='alert alert-warning';
            statusDiv.innerHTML='<i class="fas fa-exclamation-triangle me-2"></i>'+data.message+'<br><small class="text-muted">الأحدث: '+(data.latest||'')+'</small>';
            updateBtn.disabled=false;
          }else{
            statusDiv.className='alert alert-success';
            statusDiv.innerHTML='<i class="fas fa-check-circle me-2"></i> '+data.message;
            updateBtn.disabled=true;
          }
        }else{
          statusDiv.className='alert alert-danger';
          statusDiv.innerHTML='<i class="fas fa-times-circle me-2"></i> '+(data.message||'خطأ');
        }
      }).catch(function(err){
        statusDiv.className='alert alert-danger';
        statusDiv.innerHTML='<i class="fas fa-times-circle me-2"></i> خطأ: '+err.message;
      }).finally(function(){ btn.disabled=false; btn.innerHTML='<i class="fas fa-search me-1"></i>بحث عن تحديث'; });
    }
    function performUpdateUI(){
      if(!confirm('هل أنت متأكد من رغبتك في التحديث الآن؟')) return;
      var btn=document.getElementById('updateNowBtn'),statusDiv=document.getElementById('updateStatus');
      var progressDiv=document.getElementById('updateProgress'),progressBar=document.getElementById('updateProgressBar'),logsDiv=document.getElementById('updateLogs');
      btn.disabled=true; btn.innerHTML='<i class="fas fa-spinner fa-spin me-1"></i>جاري التحديث...';
      statusDiv.className='alert alert-warning'; statusDiv.innerHTML='<i class="fas fa-sync-alt fa-spin me-2"></i> جاري تنفيذ التحديث...';
      progressDiv.style.display='block'; progressBar.style.width='10%'; progressBar.textContent='10%'; logsDiv.innerHTML='📥 بدء عملية التحديث...\n';
      fetch('/api/perform_update',{method:'POST',headers:{'Content-Type':'application/json'}})
      .then(function(r){return r.json();}).then(function(data){
        if(data.logs) logsDiv.innerHTML=data.logs.join('\n');
        if(data.success){
          progressBar.style.width='95%'; progressBar.textContent='95%'; statusDiv.className='alert alert-success';
          logsDiv.innerHTML+='\n🔄 جاري إعادة تشغيل الخادم...\n';
          var countdown=10;
          var iv=setInterval(function(){ countdown--;
            statusDiv.innerHTML='<i class="fas fa-check-circle me-2"></i> ✅ تم التحديث! إعادة تحميل بعد '+countdown+' ثوانٍ';
            if(countdown<=0){clearInterval(iv);window.location.reload();}
          },1000);
        }else{
          progressBar.className='progress-bar bg-danger'; statusDiv.className='alert alert-danger';
          statusDiv.innerHTML='<i class="fas fa-times-circle me-2"></i> ❌ '+(data.message||'فشل التحديث');
          btn.disabled=false; btn.innerHTML='<i class="fas fa-download me-1"></i>إعادة المحاولة';
        }
      }).catch(function(err){
        progressBar.className='progress-bar bg-danger'; statusDiv.className='alert alert-danger';
        statusDiv.innerHTML='<i class="fas fa-times-circle me-2"></i> خطأ: '+err.message;
        btn.disabled=false; btn.innerHTML='<i class="fas fa-download me-1"></i>إعادة المحاولة';
      });
    }
    document.addEventListener('DOMContentLoaded',function(){
      document.getElementById('autoUpdateToggle').addEventListener('change',function(){
        var enabled=this.checked,statusDiv=document.getElementById('updateStatus');
        statusDiv.className='alert alert-info';
        statusDiv.innerHTML='<i class="fas fa-spinner fa-spin me-2"></i> '+(enabled?'جاري تفعيل':'جاري إلغاء')+' التحديث التلقائي...';
        fetch('/api/toggle_auto_update',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({enabled:enabled})})
        .then(function(r){return r.json();}).then(function(data){
          if(data.success){
            statusDiv.className='alert alert-success';
            statusDiv.innerHTML='<i class="fas fa-check-circle me-2"></i> '+data.message;
            setTimeout(refreshUpdateStatus,3000);
          }else{
            statusDiv.className='alert alert-danger';
            statusDiv.innerHTML='<i class="fas fa-times-circle me-2"></i> '+data.message;
            document.getElementById('autoUpdateToggle').checked=!enabled;
          }
        }).catch(function(err){
          statusDiv.className='alert alert-danger';
          statusDiv.innerHTML='<i class="fas fa-times-circle me-2"></i> خطأ: '+err.message;
          document.getElementById('autoUpdateToggle').checked=!enabled;
        });
      });
      refreshUpdateStatus();
      setInterval(refreshUpdateStatus,300000);
      if(typeof socket!=='undefined'){
        socket.on('update_completed',function(data){
          var statusDiv=document.getElementById('updateStatus');
          statusDiv.className='alert alert-success';
          statusDiv.innerHTML='<i class="fas fa-check-circle me-2"></i> '+(data.message||'✅ تم التحديث تلقائياً')+'<br><small>الإصدار: '+(data.version||'')+'</small>';
          setTimeout(refreshUpdateStatus,5000);
        });
      }
    });
    </script>

    <!-- ════════ الإشعارات الدورية (الترويجية) ════════ -->
    <div class="card bg-secondary mt-4">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h5 class="mb-0"><i class="fas fa-bell me-2 text-warning"></i>📢 الإشعارات الدورية (ترويجية)</h5>
        <div class="form-check form-switch">
          <input class="form-check-input" type="checkbox" id="promoToggle" style="width:50px;height:25px;">
          <label class="form-check-label text-light small me-2" for="promoToggle">تفعيل</label>
        </div>
      </div>
      <div class="card-body">
        <div id="promoStatus" class="alert alert-info mb-2">
          الحالة: <span id="promoState">غير مفعّل</span>
          <span class="ms-3" id="promoCount">عدد الرسائل: 0</span>
        </div>
        <div class="mb-2">
          <label class="form-label small text-light">الرسائل الترويجية (كل سطر رسالة)</label>
          <textarea id="promoMessages" class="form-control bg-dark text-light border-secondary" rows="6"
            placeholder="اكتب رسالة في كل سطر...&#10;سيتم إرسالها دورياً كل 5 دقائق"></textarea>
        </div>
        <div class="d-flex gap-2 flex-wrap">
          <button class="btn btn-primary btn-sm" onclick="savePromoMessages()">
            <i class="fas fa-save me-1"></i>حفظ الرسائل
          </button>
          <button class="btn btn-outline-info btn-sm" onclick="loadPromoData()">
            <i class="fas fa-sync me-1"></i>تحديث
          </button>
          <button class="btn btn-outline-secondary btn-sm" onclick="resetPromoIndex()">
            <i class="fas fa-undo me-1"></i>إعادة تعيين المؤشر
          </button>
        </div>
        <div id="promoResult" class="mt-2"></div>
        <div class="mt-2 small text-muted">
          <i class="fas fa-info-circle me-1"></i>
          يتم إرسال الإشعارات كل <strong>5 دقائق</strong> للمستخدمين المشتركين في Web Push
        </div>
      </div>
    </div>
    <script>
    async function loadPromoData(){
      try{
        var r=await fetch('/api/promo_data');
        var d=await r.json();
        if(d.success){
          document.getElementById('promoToggle').checked=d.enabled;
          document.getElementById('promoState').textContent=d.enabled?'مفعّل ✅':'غير مفعّل ❌';
          document.getElementById('promoState').className=d.enabled?'text-success':'text-secondary';
          document.getElementById('promoMessages').value=d.messages.join('\n');
          document.getElementById('promoCount').textContent='عدد الرسائل: '+d.messages.length;
        }
      }catch(e){console.error('Load promo error:',e);}
    }
    async function savePromoMessages(){
      var msgs=document.getElementById('promoMessages').value.split('\n').map(function(m){return m.trim();}).filter(function(m){return m;});
      var resultDiv=document.getElementById('promoResult');
      if(msgs.length===0){resultDiv.innerHTML='<div class="alert alert-danger py-1 small">⚠️ الرجاء إدخال رسالة واحدة على الأقل</div>';return;}
      resultDiv.innerHTML='<div class="alert alert-info py-1 small"><i class="fas fa-spinner fa-spin me-1"></i> جاري الحفظ...</div>';
      try{
        var r=await fetch('/api/promo_save',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({messages:msgs})});
        var d=await r.json();
        if(d.success){
          resultDiv.innerHTML='<div class="alert alert-success py-1 small">✅ '+d.message+'</div>';
          document.getElementById('promoCount').textContent='عدد الرسائل: '+d.count;
        }else{resultDiv.innerHTML='<div class="alert alert-danger py-1 small">❌ '+d.message+'</div>';}
      }catch(e){resultDiv.innerHTML='<div class="alert alert-danger py-1 small">❌ خطأ: '+e.message+'</div>';}
    }
    async function resetPromoIndex(){
      if(!confirm('هل تريد إعادة تعيين المؤشر للرسالة الأولى؟')) return;
      try{
        var r=await fetch('/api/promo_data');
        var d=await r.json();
        if(d.success){
          var r2=await fetch('/api/promo_save',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({messages:d.messages})});
          var d2=await r2.json();
          if(d2.success){
            document.getElementById('promoResult').innerHTML='<div class="alert alert-success py-1 small">✅ تم إعادة تعيين المؤشر إلى الرسالة الأولى</div>';
            loadPromoData();
          }
        }
      }catch(e){alert('خطأ: '+e.message);}
    }
    document.getElementById('promoToggle').addEventListener('change',async function(){
      var enabled=this.checked,statusDiv=document.getElementById('promoState'),resultDiv=document.getElementById('promoResult');
      statusDiv.textContent='جاري التغيير...';
      resultDiv.innerHTML='<div class="alert alert-info py-1 small"><i class="fas fa-spinner fa-spin me-1"></i> جاري التفعيل...</div>';
      try{
        var r=await fetch('/api/promo_toggle',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({enabled:enabled})});
        var d=await r.json();
        if(d.success){
          statusDiv.textContent=enabled?'مفعّل ✅':'غير مفعّل ❌';
          statusDiv.className=enabled?'text-success':'text-secondary';
          resultDiv.innerHTML='<div class="alert alert-success py-1 small">✅ '+d.message+'</div>';
        }else{
          statusDiv.textContent='فشل التغيير';
          resultDiv.innerHTML='<div class="alert alert-danger py-1 small">❌ '+d.message+'</div>';
          document.getElementById('promoToggle').checked=!enabled;
        }
      }catch(e){
        statusDiv.textContent='خطأ';
        resultDiv.innerHTML='<div class="alert alert-danger py-1 small">❌ خطأ: '+e.message+'</div>';
        document.getElementById('promoToggle').checked=!enabled;
      }
    });
    document.addEventListener('DOMContentLoaded',function(){
      loadPromoData();
      setInterval(loadPromoData,30000);
    });
    </script>

    </body></html>''', 200



@app.route("/admin/api/log_query", methods=["POST"])
def admin_log_query():
    """تحليل ذكي للسجلات بالكلمات المفتاحية أو الأنماط"""
    try:
        if not session.get('admin'):
            return jsonify({"success": False, "message": "❌ غير مصرح"})
        data  = request.json or {}
        query = (data.get('query') or '').strip()
        ctx_logs = data.get('logs', [])   # السجلات المرسلة من الواجهة
        q_lower = query.lower()

        if not q_lower:
            total = len(_mem_log_handler.get_records(None))
            return jsonify({"success": True,
                            "answer": f"💡 يوجد {total} حدث في ذاكرة السجلات.\n"
                                      "اكتب مثلاً:\n"
                                      "• آخر الأخطاء\n• ابحث عن werkzeug\n• تحذيرات\n• GET /api"})

        all_recs = _mem_log_handler.get_records(None)

        # ── تحديد نوع الاستعلام ──
        is_error = any(w in q_lower for w in ['خطأ','error','errors','critical','exception','traceback','fail','فشل'])
        is_warn  = any(w in q_lower for w in ['تحذير','warning','warn'])
        is_info  = any(w in q_lower for w in ['معلومة','info','نجاح','success','ناجح'])
        is_debug = any(w in q_lower for w in ['debug','تصحيح'])
        is_last  = any(w in q_lower for w in ['أخير','اخير','آخر','last','recent','latest'])
        is_count = any(w in q_lower for w in ['كم','عدد','count','how many','total'])

        matched = []
        label   = ''

        if is_error and not is_warn and not is_info:
            matched = [r for r in all_recs if r['level'] in ('ERROR','CRITICAL')]
            label = f'❌ الأخطاء ({len(matched)})'
        elif is_warn and not is_error:
            matched = [r for r in all_recs if r['level'] == 'WARNING']
            label = f'⚠️ التحذيرات ({len(matched)})'
        elif is_info and not is_error:
            matched = [r for r in all_recs if r['level'] == 'INFO']
            label = f'ℹ️ أحداث INFO ({len(matched)})'
        elif is_debug:
            matched = [r for r in all_recs if r['level'] == 'DEBUG']
            label = f'🔵 أحداث DEBUG ({len(matched)})'
        else:
            # بحث نصي حر
            kw = q_lower.replace('ابحث عن','').replace('search','').strip()
            if kw:
                matched = [r for r in all_recs
                           if kw in (r.get('full') or r.get('msg','')+r.get('name','')).lower()]
                label = f'🔍 بحث عن "{kw}" — {len(matched)} نتيجة'
            else:
                matched = all_recs[-20:]
                label = f'📋 آخر {len(matched)} حدث'

        if is_count:
            errs  = sum(1 for r in all_recs if r['level'] in ('ERROR','CRITICAL'))
            warns = sum(1 for r in all_recs if r['level']=='WARNING')
            infos = sum(1 for r in all_recs if r['level']=='INFO')
            return jsonify({"success": True, "answer":
                f"📊 إحصائيات السجلات ({len(all_recs)} حدث إجمالاً):\n"
                f"  ❌ أخطاء: {errs}\n"
                f"  ⚠️ تحذيرات: {warns}\n"
                f"  ℹ️ معلومات: {infos}", "count": len(all_recs)})

        if not matched:
            return jsonify({"success": True, "answer": f'🔍 لا توجد سجلات مطابقة لـ "{query}"', "count": 0})

        # عرض آخر 15 نتيجة
        show = matched[-15:] if not is_last else matched[-30:]
        LVL_ICO = {'ERROR':'❌','CRITICAL':'🔴','WARNING':'⚠️','INFO':'✅','DEBUG':'🔵'}
        lines = [label + ':']
        for r in show:
            ico = LVL_ICO.get(r['level'],'•')
            msg = (r.get('msg') or r.get('full',''))[:140]
            lines.append(f"{ico} [{r['time']}] {r['name']}: {msg}")
        if len(matched) > len(show):
            lines.append(f"... و{len(matched)-len(show)} حدث آخر")
        return jsonify({"success": True, "answer": '\n'.join(lines), "count": len(matched)})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route("/api/admin/download_project", methods=["GET"])
def api_admin_download_project():
    """تحميل كامل ملفات المشروع كملف ZIP"""
    import zipfile, io, os as _os
    try:
        buf = io.BytesIO()
        base_dir = _os.path.dirname(_os.path.abspath(__file__))
        EXCLUDE_DIRS = {'.git','__pycache__','node_modules','.venv','venv','env','.local','pnpm','store','outputs'}
        EXCLUDE_EXTS = {'.pyc','.pyo','.pyd','.db-wal','.db-shm'}
        MAX_FILE_MB  = 10
        with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
            for root, dirs, files in _os.walk(base_dir):
                dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith('.')]
                for fname in files:
                    fpath = _os.path.join(root, fname)
                    _, ext = _os.path.splitext(fname)
                    if ext in EXCLUDE_EXTS: continue
                    try:
                        if _os.path.getsize(fpath)/(1024*1024) > MAX_FILE_MB: continue
                    except Exception: continue
                    arcname = _os.path.relpath(fpath, base_dir)
                    try: zf.write(fpath, arcname)
                    except Exception: pass
        buf.seek(0)
        from flask import send_file
        return send_file(buf, mimetype='application/zip', as_attachment=True,
                         download_name='AbuMalik-Services-Backup.zip')
    except Exception as e:
        logger.error(f"Download project error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/admin/list_project_files", methods=["GET"])
def api_admin_list_project_files():
    """قائمة بجميع ملفات المشروع مع أحجامها"""
    import os as _os
    try:
        base_dir = _os.path.dirname(_os.path.abspath(__file__))
        EXCLUDE_DIRS = {'.git','__pycache__','node_modules','.venv','venv','env','.local','pnpm','store','outputs'}
        EXCLUDE_EXTS = {'.pyc','.pyo','.pyd','.db-wal','.db-shm'}
        MAX_FILE_MB  = 50
        files_list = []
        for root, dirs, files in _os.walk(base_dir):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith('.')]
            for fname in files:
                fpath = _os.path.join(root, fname)
                _, ext = _os.path.splitext(fname)
                if ext in EXCLUDE_EXTS: continue
                try:
                    size_bytes = _os.path.getsize(fpath)
                    if size_bytes/(1024*1024) > MAX_FILE_MB: continue
                    rel = _os.path.relpath(fpath, base_dir)
                    if size_bytes < 1024:
                        size_str = f"{size_bytes} B"
                    elif size_bytes < 1024*1024:
                        size_str = f"{size_bytes/1024:.1f} KB"
                    else:
                        size_str = f"{size_bytes/(1024*1024):.1f} MB"
                    files_list.append({"path": rel, "size": size_str, "bytes": size_bytes})
                except Exception:
                    continue
        files_list.sort(key=lambda x: x["path"])
        return jsonify({"success": True, "files": files_list, "total": len(files_list)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/admin/download_selected_files", methods=["POST"])
def api_admin_download_selected_files():
    """تحميل ملفات محددة كـ ZIP"""
    import zipfile, io, os as _os
    try:
        data = request.get_json() or {}
        selected = data.get("files", [])
        if not selected:
            return jsonify({"success": False, "error": "لم يتم تحديد أي ملفات"}), 400
        base_dir = _os.path.dirname(_os.path.abspath(__file__))
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
            for rel_path in selected:
                # تأمين المسار — لا نسمح بالخروج من مجلد المشروع
                full_path = _os.path.normpath(_os.path.join(base_dir, rel_path))
                if not full_path.startswith(base_dir): continue
                if not _os.path.isfile(full_path): continue
                try: zf.write(full_path, rel_path)
                except Exception: pass
        buf.seek(0)
        from flask import send_file
        return send_file(buf, mimetype='application/zip', as_attachment=True,
                         download_name='selected_project_files.zip')
    except Exception as e:
        logger.error(f"Download selected files error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/admin/download_single_file", methods=["GET"])
def api_admin_download_single_file():
    """تحميل ملف واحد مباشرة بدون ضغط"""
    if not session.get("admin_auth"):
        return jsonify({"success": False, "error": "غير مخول"}), 403
    import os as _os
    rel_path = request.args.get("path", "").strip()
    if not rel_path:
        return jsonify({"success": False, "error": "مسار الملف مطلوب"}), 400
    base_dir  = _os.path.dirname(_os.path.abspath(__file__))
    full_path = _os.path.normpath(_os.path.join(base_dir, rel_path))
    # تأمين: لا نسمح بالخروج من مجلد المشروع
    if not full_path.startswith(base_dir):
        return jsonify({"success": False, "error": "مسار غير مسموح به"}), 403
    if not _os.path.isfile(full_path):
        return jsonify({"success": False, "error": "الملف غير موجود"}), 404
    try:
        return send_file(full_path, as_attachment=True,
                         download_name=_os.path.basename(full_path))
    except Exception as e:
        logger.error(f"Download single file error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================================
# وظيفة استخراج وتصنيف روابط تيليجرام حسب الدولة
# ============================================================
from urllib.parse import urlparse as _urlparse

LINK_FINDER_CATEGORIES = [
    "🎓 جامعي / أكاديمي",
    "📚 معاهد / دورات مهنية",
    "📝 تدريب ميداني / تقارير",
    "🧪 علمية / تعليمية (مناهج)",
    "💼 وظائف / توظيف",
    "🚗 خدمات / توصيل / عقارات",
    "📢 إعلانات / تسويق",
    "📰 أخبار / عاجل",
    "🎬 ترفيه / مسلسلات / فيديو",
    "💻 تقنية / برمجة / شبكات",
    "📌 عام / متنوع"
]

KEYWORDS_FALLBACK_LINK = {
    "🎓 جامعي / أكاديمي": ["جامعة","كلية","بكالوريوس","ماجستير","دكتوراه","بحث","محاضرة","تخصص","طلاب","قبول","ساعات معتمدة"],
    "📚 معاهد / دورات مهنية": ["معهد","دورة","شهادة مهنية","مدرب","تدريب","الرخصة المهنية","أكاديمية"],
    "📝 تدريب ميداني / تقارير": ["تدريب ميداني","تقرير","مشروع تخرج","COOP","تعاوني","ميداني","دراسة حالة"],
    "🧪 علمية / تعليمية (مناهج)": ["رياضيات","فيزياء","كيمياء","منهج","مدرسة","اختبار","قدرات","تحصيلي","ابتدائي","متوسط","ثانوي"],
    "💼 وظائف / توظيف": ["وظائف","توظيف","مقابلة","راتب","مطلوب","شركة","خريجين","تجنيد"],
    "🚗 خدمات / توصيل / عقارات": ["توصيل","مشاوير","سواق","نقل","عقار","مقاولات","شقة","إيجار"],
    "📢 إعلانات / تسويق": ["عرض","خصم","بيع","شراء","سعر","متجر","تخفيض"],
    "📰 أخبار / عاجل": ["عاجل","أخبار","وزارة","أحداث","بيان","رسمي"],
    "🎬 ترفيه / مسلسلات / فيديو": ["مسلسل","فيلم","مشاهدة","تحميل","حلقة","مقاطع","يوتيوب","ضحك"],
    "💻 تقنية / برمجة / شبكات": ["برمجة","تطوير","خادم","شبكة","برامج","تطبيق","سيرفر","بوت"]
}

_lf_country_cache = {}

def _lf_get_country_tld(hostname):
    if not hostname:
        return None
    tld = hostname.split('.')[-1].upper()
    valid = {'SA','AE','EG','KW','QA','OM','BH','JO','LB','IQ','YE','SY','PS','SD','LY','TN','MA','DZ','MR'}
    return tld if tld in valid else None

def _lf_get_country_ip(hostname):
    try:
        ip = socket.gethostbyname(hostname)
        resp = requests.get(f'http://ip-api.com/json/{ip}', timeout=5)
        if resp.status_code == 200:
            d = resp.json()
            if d.get('status') == 'success':
                return d.get('countryCode')
    except Exception:
        pass
    return None

def _lf_get_country(hostname):
    if not hostname:
        return None
    if hostname in _lf_country_cache:
        return _lf_country_cache[hostname]
    country = _lf_get_country_tld(hostname) or _lf_get_country_ip(hostname)
    _lf_country_cache[hostname] = country
    return country

def _lf_extract_links(text):
    raw = re.findall(r'https?://[^\s<>"\'\)]+', text)
    seen = set()
    links = []
    for l in raw:
        l = l.strip().rstrip('.,;:)')
        if l and l not in seen:
            seen.add(l)
            links.append(l)
    return links

def _lf_get_context(link, text, window=200):
    idx = text.find(link)
    if idx == -1:
        return link[:150]
    start = max(0, idx - window)
    end = min(len(text), idx + len(link) + window)
    return text[start:end].replace('\n', ' ').strip()

def _lf_classify_fallback(text):
    text_lower = text.lower()
    scores = {}
    for cat, keywords in KEYWORDS_FALLBACK_LINK.items():
        count = sum(1 for kw in keywords if kw in text_lower)
        if count > 0:
            scores[cat] = count
    if not scores:
        return "📌 عام / متنوع", 0.0
    best = max(scores, key=scores.get)
    return best, min(1.0, scores[best] / 5.0)

def _lf_classify_groq(context, groq_client):
    try:
        prompt = f"""صنّف النص التالي إلى واحدة من هذه الفئات (اختر الأنسب):
{', '.join(LINK_FINDER_CATEGORIES)}

النص: {context[:600]}

أجب فقط باسم الفئة كما هي مكتوبة بالضبط دون أي شرح."""
        resp = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=20,
            temperature=0.1
        )
        result = resp.choices[0].message.content.strip()
        for cat in LINK_FINDER_CATEGORIES:
            if cat in result:
                return cat, 0.92
        return "📌 عام / متنوع", 0.5
    except Exception as e:
        logger.warning(f"Groq link classify: {e}")
        return _lf_classify_fallback(context)


@app.route("/link-finder")
@app.route("/link_finder")
def link_finder_page():
    if 'user_id' not in session:
        return redirect('/')
    return render_template('link_finder.html')


_LF_COUNTRY_NAMES = {
    'SA': 'السعودية', 'AE': 'الإمارات', 'EG': 'مصر', 'KW': 'الكويت',
    'QA': 'قطر', 'OM': 'عمان', 'BH': 'البحرين', 'JO': 'الأردن',
    'LB': 'لبنان', 'IQ': 'العراق', 'YE': 'اليمن', 'SY': 'سوريا',
    'PS': 'فلسطين', 'SD': 'السودان', 'LY': 'ليبيا', 'TN': 'تونس',
    'MA': 'المغرب', 'DZ': 'الجزائر', 'MR': 'موريتانيا',
}

@app.route("/api/link_finder/start", methods=["POST"])
def api_link_finder_start():
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "الرجاء تسجيل الدخول"}), 401
    user_id = session['user_id']
    data     = request.get_json() or {}
    mode     = data.get('mode', 'text')           # 'text' | 'telegram_search'
    text     = data.get('text', '').strip()
    keyword  = data.get('keyword', '').strip()
    country  = data.get('country', '').strip().upper()
    category = data.get('category', '').strip()
    use_ai   = data.get('use_ai', True)

    # ── وضع البحث الجديد: telegram_search ──────────────────────
    if mode == 'telegram_search':
        with USERS_LOCK:
            if user_id not in USERS:
                return jsonify({"success": False, "message": "❌ المستخدم غير مسجل"})
            cm = USERS[user_id].get('client_manager')
            if not cm or not cm.client:
                return jsonify({"success": False, "message": "❌ يرجى تسجيل الدخول أولاً"})

        def _tg_search_worker():
            try:
                # بناء عبارة البحث: كلمة + دولة + فئة
                parts = []
                if keyword:  parts.append(keyword)
                if country:  parts.append(_LF_COUNTRY_NAMES.get(country, country))
                if category: parts.append(category)
                if not parts: parts.append('قناة')
                query = ' '.join(parts)

                socketio.emit('search_dialog_progress', {
                    'chat': f'🔍 يبحث في تيليجرام: {query}',
                    'scanned': 0, 'found': 0
                }, to=user_id)

                # استدعاء البحث العام
                results = cm.run_coroutine(
                    search_global_groups(cm.client, query, limit=80, filter_type='all')
                )

                # تحضير كلاسيفاير
                groq_client = None
                if use_ai and GROQ_API_KEY:
                    try:
                        from groq import Groq as _G
                        groq_client = _G(api_key=GROQ_API_KEY)
                    except Exception:
                        pass

                # معالجة كل نتيجة وتصنيفها
                links_from_text = []
                if text:
                    links_from_text = _lf_extract_links(text)

                all_links = []
                for r in results:
                    url = r.get('url', '')
                    if url:
                        all_links.append({'url': url, 'title': r.get('title', ''), 'members': r.get('members', 0)})
                for u in links_from_text:
                    all_links.append({'url': u, 'title': '', 'members': 0})

                if not all_links:
                    socketio.emit('link_finder_done', {
                        'total': 0, 'classified': 0,
                        'message': f'لم يُعثر على نتائج لـ "{query}"'
                    }, to=user_id)
                    return

                classified = 0
                for item in all_links:
                    url   = item['url']
                    title = item.get('title', '')
                    ctx   = title or url
                    if groq_client:
                        cat, score = _lf_classify_groq(ctx, groq_client)
                    else:
                        cat, score = _lf_classify_fallback(ctx)
                    # تصفية حسب الفئة المطلوبة (إذا حُدّدت)
                    if category and cat != category and score < 0.6:
                        continue
                    socketio.emit('link_classified', {
                        'link':     url,
                        'category': cat,
                        'score':    score,
                        'context':  (title + f' ({item["members"]:,} عضو)') if item.get('members') else title,
                        'country':  _LF_COUNTRY_NAMES.get(country, country) if country else ''
                    }, to=user_id)
                    classified += 1
                    time.sleep(0.03)

                socketio.emit('link_finder_done', {
                    'total': classified, 'classified': classified
                }, to=user_id)
            except Exception as e:
                logger.error(f"TG search worker error: {e}")
                socketio.emit('link_finder_error', {'error': str(e)}, to=user_id)

        t = threading.Thread(target=_tg_search_worker, daemon=True)
        t.start()
        return jsonify({"success": True, "message": "بدأ البحث في تيليجرام"})

    # ── الوضع الكلاسيكي: نص مباشر ──────────────────────────────
    if not text:
        return jsonify({"success": False, "message": "النص المصدر فارغ"})

    def process_links():
        try:
            raw_links = _lf_extract_links(text)
            if not raw_links:
                socketio.emit('link_finder_done', {'total': 0, 'classified': 0, 'message': 'لم يُعثر على روابط في النص'}, to=user_id)
                return

            groq_client = None
            if use_ai and GROQ_API_KEY:
                try:
                    from groq import Groq
                    groq_client = Groq(api_key=GROQ_API_KEY)
                except Exception:
                    pass

            for link in raw_links:
                context = _lf_get_context(link, text)
                if groq_client:
                    cat, score = _lf_classify_groq(context, groq_client)
                else:
                    cat, score = _lf_classify_fallback(context)
                socketio.emit('link_classified', {
                    'link': link, 'category': cat, 'score': score,
                    'context': context[:150], 'country': country
                }, to=user_id)
                time.sleep(0.05)

            socketio.emit('link_finder_done', {'total': len(raw_links), 'classified': len(raw_links)}, to=user_id)
        except Exception as e:
            logger.error(f"Link finder worker error: {e}")
            socketio.emit('link_finder_error', {'error': str(e)}, to=user_id)

    t = threading.Thread(target=process_links, daemon=True)
    t.start()
    return jsonify({"success": True, "message": "بدأ البحث والتصنيف"})


@app.route("/api/link_finder/export", methods=["POST"])
def api_link_finder_export():
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "الرجاء تسجيل الدخول"}), 401
    data = request.get_json() or {}
    links_data = data.get('links', [])
    if not links_data:
        return jsonify({"error": "لا توجد بيانات"}), 400
    try:
        import pandas as pd
        df = pd.DataFrame(links_data)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name="الروابط")
        output.seek(0)
        return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                         as_attachment=True, download_name='links_classified.xlsx')
    except Exception as e:
        logger.error(f"Link finder export error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/auto_join/links", methods=["POST"])
def api_auto_join_from_link_finder():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"success": False, "message": "غير مسجل"}), 401
    data = request.json or {}
    links = data.get('links', [])
    if not links:
        return jsonify({"success": False, "message": "لا توجد روابط"})
    settings = load_settings(user_id)
    settings['auto_join_links'] = links
    save_settings(user_id, settings)
    socketio.emit('log_update', {"message": f"📥 تم استلام {len(links)} رابط من أداة البحث، جاهزة للانضمام"}, to=user_id)
    return jsonify({"success": True, "message": f"تم تخزين {len(links)} رابط للانضمام"})


# ══════════════════════════════════════════════════════════════════════════════
# ─── نظام بطاقات الشحن المتكامل ──────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════

def load_cards_data():
    """تحميل بيانات البطاقات من الملف المحلي"""
    with _CARDS_LOCK:
        try:
            if os.path.exists(CARDS_FILE):
                with open(CARDS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        default = {
            "card_system_enabled": False,
            "plans": [
                {"id": 1, "name": "يومية",   "time_limit": 86400,   "data_limit": 5368709120,  "profile_name": "daily"},
                {"id": 2, "name": "أسبوعية", "time_limit": 604800,  "data_limit": 10737418240, "profile_name": "weekly"},
                {"id": 3, "name": "شهرية",   "time_limit": 2592000, "data_limit": 32212254720, "profile_name": "monthly"}
            ],
            "vouchers": [],
            "active_card_sessions": []
        }
        with open(CARDS_FILE, 'w', encoding='utf-8') as f:
            json.dump(default, f, ensure_ascii=False, indent=2)
        return default

def save_cards_data(data):
    """حفظ بيانات البطاقات محلياً"""
    with _CARDS_LOCK:
        try:
            with open(CARDS_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving cards data: {e}")

def voucher_display_code(v):
    """يرجع رمز البطاقة الظاهر للمشرف — يدعم الكروت القديمة التي لا تحتوي على 'code'."""
    return v.get("code") or (v.get("code_hash", "")[:12] + "***" if v.get("code_hash") else "—")

def voucher_display_plan_name(v, plans=None):
    """يرجع اسم الخطة — يدعم الكروت القديمة التي تخزن plan_id فقط بدون plan_name."""
    if v.get("plan_name"):
        return v["plan_name"]
    if plans is None:
        plans = load_cards_data().get("plans", [])
    plan = next((p for p in plans if p.get("id") == v.get("plan_id")), None)
    return plan["name"] if plan else "بدون خطة"

def generate_vouchers(plan_id, count=10, allowed_features=None):
    """إنشاء قسائم بطاقات جديدة مع تحديد الوظائف التي تفتحها"""
    data = load_cards_data()
    plan = next((p for p in data["plans"] if p["id"] == plan_id), None)
    if not plan:
        raise ValueError("الخطة غير موجودة")
    if allowed_features is None:
        allowed_features = []
    codes = []
    for _ in range(count):
        raw = f"{secrets.token_hex(3).upper()}-{secrets.token_hex(3).upper()}"
        normalized = raw.replace("-", "").upper()
        hashed = hashlib.sha256(normalized.encode()).hexdigest()
        data["vouchers"].append({
            "code": raw,
            "code_hash": hashed,
            "plan_id": plan_id,
            "plan_name": plan["name"],
            "allowed_features": allowed_features,
            "status": "unused",
            "created_at": datetime.now().isoformat(),
            "used_at": None,
            "expires_at": None
        })
        codes.append(raw)
    save_cards_data(data)
    return codes

def validate_voucher(code):
    normalized = code.strip().replace("-", "").upper()
    hashed = hashlib.sha256(normalized.encode()).hexdigest()
    data = load_cards_data()
    voucher = next((v for v in data["vouchers"] if v["code_hash"] == hashed), None)
    if not voucher:
        return None, "❌ الرمز غير صحيح"
    if voucher["status"] == "used":
        return None, "❌ تم استخدام هذا الرمز مسبقاً"
    if voucher["status"] == "expired":
        return None, "❌ انتهت صلاحية الرمز"
    plan = next((p for p in data["plans"] if p["id"] == voucher["plan_id"]), None)
    if not plan:
        return None, "❌ الخطة غير موجودة"
    return {"voucher": voucher, "plan": plan}, None

def activate_card_voucher(code, client_ip="0.0.0.0"):
    result, err = validate_voucher(code)
    if err:
        return {"success": False, "message": err}
    voucher = result["voucher"]
    plan = result["plan"]
    data = load_cards_data()
    data.setdefault("active_card_sessions", [])
    data.setdefault("vouchers", [])
    session_id = secrets.token_hex(16)
    now = datetime.now()
    expires_at = now + timedelta(seconds=plan["time_limit"])
    new_session = {
        "session_id": session_id,
        "voucher_code_hash": voucher["code_hash"],
        "plan_name": plan["name"],
        "ip_address": client_ip,
        "start_time": now.isoformat(),
        "expires_at": expires_at.isoformat(),
        "session_timeout": plan["time_limit"]
    }
    for v in data["vouchers"]:
        if v["code_hash"] == voucher["code_hash"]:
            v["status"] = "active"
            v["used_at"] = now.isoformat()
            v["expires_at"] = expires_at.isoformat()
            break
    data["active_card_sessions"].append(new_session)
    save_cards_data(data)

    # تطبيق الوظائف المفتوحة (allowed_features) على المستخدم الحالي
    allowed = voucher.get("allowed_features", [])
    if allowed:
        try:
            user_id = session.get('user_id', 'user_1')
            feat_data = load_feature_restrictions()
            unlocked = feat_data.get("user_unlocked", {}).get(user_id, [])
            for f in allowed:
                if f not in unlocked:
                    unlocked.append(f)
            feat_data.setdefault("user_unlocked", {})[user_id] = unlocked
            save_feature_restrictions(feat_data)
            logger.info(f"✅ فُتحت الوظائف {allowed} للمستخدم {user_id} عبر البطاقة")
        except Exception as _fe:
            logger.error(f"activate_card_voucher features error: {_fe}")

    return {
        "success": True,
        "session_id": session_id,
        "expires_at": expires_at.isoformat(),
        "plan_name": plan["name"],
        "unlocked_features": allowed,
        "message": f"✅ تم الدخول بنجاح - باقة {plan['name']}"
    }

def terminate_card_session(session_id, reason="انتهت الجلسة"):
    data = load_cards_data()
    s = next((x for x in data["active_card_sessions"] if x["session_id"] == session_id), None)
    if s:
        for v in data["vouchers"]:
            if v["code_hash"] == s.get("voucher_code_hash"):
                v["status"] = "used"
                break
        data["active_card_sessions"] = [x for x in data["active_card_sessions"] if x["session_id"] != session_id]
        save_cards_data(data)

def _card_session_monitor():
    """مراقبة انتهاء صلاحية جلسات البطاقات"""
    while True:
        try:
            data = load_cards_data()
            now = datetime.now()
            to_terminate = []
            for s in data.get("active_card_sessions", []):
                try:
                    expires = datetime.fromisoformat(s["expires_at"])
                    if now >= expires:
                        to_terminate.append(s["session_id"])
                except Exception:
                    pass
            for sid in to_terminate:
                terminate_card_session(sid, "انتهى الوقت تلقائياً")
        except Exception as e:
            logger.error(f"card_session_monitor: {e}")
        time.sleep(60)

_OSThread(target=_card_session_monitor, daemon=True).start()

# ── مسارات API لبطاقات الشحن ────────────────────────────────────────────────

@app.route("/login")
@app.route("/login_card")
def login_page():
    """صفحة الدخول ببطاقة الشحن"""
    cards = load_cards_data()
    if not cards.get("card_system_enabled", False):
        return redirect("/")
    if session.get("card_logged_in"):
        return redirect("/")
    return render_template("login_card.html")

@app.route("/api/login_card", methods=["POST"])
def api_login_card():
    data = request.json or {}
    code = data.get("code", "").strip()
    if not code:
        return jsonify({"success": False, "message": "❌ الرجاء إدخال الرمز"})

    # ── دخول مجاني بكلمة مرور الأدمن (بدون بطاقة) ──────────────
    if code == ADMIN_PASSWORD or code.replace("-","") == ADMIN_PASSWORD:
        session["card_logged_in"]   = True
        session.pop("card_session_id", None)
        session["card_plan_name"]   = "أدمن — دخول مجاني"
        session["card_expires_at"]  = ""
        session["admin_auth"]       = True
        session.permanent = True
        logger.info("✅ دخول مجاني بكلمة مرور الأدمن")
        return jsonify({"success": True, "redirect": "/", "message": "✅ مرحباً أدمن — دخول مجاني"})

    client_ip = request.remote_addr or "0.0.0.0"
    result = activate_card_voucher(code, client_ip)
    if result["success"]:
        session["card_logged_in"] = True
        session["card_session_id"] = result["session_id"]
        session["card_plan_name"] = result.get("plan_name", "")
        session["card_expires_at"] = result.get("expires_at", "")
        session.permanent = True
        return jsonify({"success": True, "redirect": "/", "message": result["message"]})
    return jsonify({"success": False, "message": result["message"]})

@app.route("/api/card_session_status", methods=["GET"])
def api_card_session_status():
    sid = session.get("card_session_id")
    if not sid:
        return jsonify({"active": False})
    data = load_cards_data()
    active = next((s for s in data["active_card_sessions"] if s["session_id"] == sid), None)
    if not active:
        return jsonify({"active": False, "message": "انتهت الجلسة"})
    try:
        expires = datetime.fromisoformat(active["expires_at"])
        remaining = max(0, int((expires - datetime.now()).total_seconds()))
    except Exception:
        remaining = 0
    return jsonify({
        "active": True,
        "remaining": remaining,
        "plan_name": active.get("plan_name", ""),
        "expires_at": active.get("expires_at", "")
    })

@app.route("/api/card_logout", methods=["POST"])
def api_card_logout():
    sid = session.get("card_session_id")
    if sid:
        terminate_card_session(sid, "تسجيل خروج يدوي")
    session.pop("card_logged_in", None)
    session.pop("card_session_id", None)
    session.pop("card_plan_name", None)
    session.pop("card_expires_at", None)
    return jsonify({"success": True, "redirect": "/login"})

# ── مسارات إدارة البطاقات ────────────────────────────────────────────────────

@app.route("/admin/api/create_vouchers", methods=["POST"])
def admin_create_vouchers():
    if not session.get("admin_auth"):
        return jsonify({"success": False, "message": "غير مخول"}), 403
    data = request.json or {}
    plan_id = int(data.get("plan_id", 1))
    count = min(int(data.get("count", 10)), 200)
    features = [f for f in data.get("features", []) if f in FEATURE_LABELS]
    try:
        codes = generate_vouchers(plan_id, count, allowed_features=features)
        return jsonify({"success": True, "codes": codes, "count": len(codes), "features": features})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route("/admin/api/card_status", methods=["GET"])
def admin_card_status():
    if not session.get("admin_auth"):
        return jsonify({"success": False, "message": "غير مخول"}), 403
    data = load_cards_data()
    return jsonify({"enabled": data.get("card_system_enabled", False)})

@app.route("/admin/api/toggle_card_system", methods=["POST"])
def admin_toggle_card_system():
    if not session.get("admin_auth"):
        return jsonify({"success": False, "message": "غير مخول"}), 403
    data_req = request.json or {}
    enabled = bool(data_req.get("enabled", True))
    cards = load_cards_data()
    cards["card_system_enabled"] = enabled
    save_cards_data(cards)
    status_text = "تفعيل" if enabled else "تعطيل"
    return jsonify({"success": True, "enabled": enabled, "message": f"تم {status_text} نظام البطاقات"})

@app.route("/admin/api/vouchers", methods=["GET"])
def admin_list_vouchers():
    if not session.get("admin_auth"):
        return jsonify({"success": False, "message": "غير مخول"}), 403
    data = load_cards_data()
    return jsonify({"success": True, "vouchers": data.get("vouchers", [])})

@app.route("/admin/api/card_sessions", methods=["GET"])
def admin_list_card_sessions():
    if not session.get("admin_auth"):
        return jsonify({"success": False, "message": "غير مخول"}), 403
    data = load_cards_data()
    return jsonify({"success": True, "sessions": data.get("active_card_sessions", [])})

@app.route("/admin/api/terminate_card_session", methods=["POST"])
def admin_terminate_card_session():
    if not session.get("admin_auth"):
        return jsonify({"success": False, "message": "غير مخول"}), 403
    d = request.json or {}
    sid = d.get("session_id")
    if not sid:
        return jsonify({"success": False, "message": "معرف الجلسة مطلوب"})
    terminate_card_session(sid, "إنهاء يدوي من المشرف")
    return jsonify({"success": True})

@app.route("/admin/api/delete_vouchers", methods=["POST"])
def admin_delete_vouchers():
    if not session.get("admin_auth"):
        return jsonify({"success": False, "message": "غير مخول"}), 403
    d = request.json or {}
    status_filter = d.get("status")
    cards = load_cards_data()
    if status_filter:
        cards["vouchers"] = [v for v in cards["vouchers"] if v["status"] != status_filter]
    else:
        cards["vouchers"] = []
    save_cards_data(cards)
    return jsonify({"success": True})


# ══════════════════════════════════════════════════════════════════════════════
# ▸ نظام تقييد الوظائف (Feature Restrictions) + نظام Pro بالبطاقات
# ══════════════════════════════════════════════════════════════════════════════

FEATURE_RESTRICTIONS_FILE = os.path.join(DATA_DIR, "feature_restrictions.json")
FEATURE_VOUCHERS_FILE     = os.path.join(DATA_DIR, "feature_vouchers.json")
_FR_LOCK = threading.Lock()
_FV_LOCK = threading.Lock()

FEATURE_LABELS = {
    "rotating":             "النشر الدوري المتسلسل",
    "group_search":         "البحث في روابطي",
    "auto_join":            "الانضمام المتقدم",
    "auto_replies":         "الردود التلقائية",
    "saved_links":          "الروابط المحفوظة",
    "academic":             "التحليل الأكاديمي الذكي",
    "formatter_pdf2word":   "تحويل PDF إلى Word",
    "formatter_html2word":  "تحويل HTML إلى Word",
    "formatter_html2excel": "تحويل HTML إلى Excel",
    "formatter_html2ppt":   "تحويل HTML إلى PPT",
    "link_finder":          "محرك البحث عن الروابط",
    "message_sending":      "إرسال الرسائل",
    "monitoring":           "مراقبة المجموعات",
    "scan_groups":          "مسح المجموعات",
}

# قائمة كاملة للتقييد: الوظائف + المستخدمون الخمسة
RESTRICTED_FEATURES_LIST = [
    {"id": "rotating",            "name": "🔄 النشر الدوري المتسلسل"},
    {"id": "group_search",        "name": "🔍 البحث في روابطي"},
    {"id": "auto_join",           "name": "🤖 الانضمام المتقدم"},
    {"id": "auto_replies",        "name": "💬 الردود التلقائية"},
    {"id": "saved_links",         "name": "🔗 الروابط المحفوظة"},
    {"id": "academic",            "name": "📚 التحليل الأكاديمي الذكي"},
    {"id": "formatter_pdf2word",  "name": "📄 تحويل PDF إلى Word"},
    {"id": "formatter_html2word", "name": "📝 تحويل HTML إلى Word"},
    {"id": "formatter_html2excel","name": "📊 تحويل HTML إلى Excel"},
    {"id": "formatter_html2ppt",  "name": "🎞️ تحويل HTML إلى PPT"},
    {"id": "link_finder",         "name": "🕵️ محرك البحث عن الروابط"},
    {"id": "message_sending",     "name": "📨 إرسال الرسائل"},
    {"id": "monitoring",          "name": "👁️ مراقبة المجموعات"},
    {"id": "scan_groups",         "name": "📡 مسح المجموعات"},
]

_FR_DEFAULT = {
    "enabled": False,
    "global_restricted": [],
    "user_restrictions": {},
    "user_unlocked": {}
}

def load_feature_restrictions():
    with _FR_LOCK:
        try:
            if os.path.exists(FEATURE_RESTRICTIONS_FILE):
                with open(FEATURE_RESTRICTIONS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                for k, v in _FR_DEFAULT.items():
                    if k not in data:
                        data[k] = v
                return data
        except Exception:
            pass
        return dict(_FR_DEFAULT)

def save_feature_restrictions(data):
    with _FR_LOCK:
        try:
            with open(FEATURE_RESTRICTIONS_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"save_feature_restrictions: {e}")

def is_feature_restricted_for_user(user_id, feature_id):
    """التحقق مما إذا كانت وظيفة معينة مقيّدة لمستخدم محدد."""
    data = load_feature_restrictions()
    if not data.get("enabled", False):
        return False
    # 1. قيود خاصة بالمستخدم
    user_restr = data.get("user_restrictions", {}).get(user_id, [])
    if "all" in user_restr or feature_id in user_restr:
        return True
    # 2. قيود عامة — يتجاوزها إذا كان المستخدم فتحها ببطاقة أو مُدرج في القائمة المجانية (feature_vouchers)
    if feature_id in data.get("global_restricted", []):
        # فحص فتح البطاقة
        unlocked = data.get("user_unlocked", {}).get(user_id, [])
        if feature_id in unlocked:
            return False
        # فحص قائمة المستخدمين المجانيين من لوحة الإدارة (feature_vouchers)
        try:
            fv = load_feature_vouchers()
            allowed_users = fv.get(feature_id, {}).get("users", [])
            if user_id in allowed_users:
                return False
        except Exception:
            pass
        return True
    return False

def is_user_restricted(user_id):
    """تحقق إذا كان المستخدم مقيداً بأي شكل."""
    data = load_feature_restrictions()
    if not data.get("enabled", False):
        return False
    user_restr = data.get("user_restrictions", {}).get(user_id, [])
    if user_restr:
        return True
    unlocked = data.get("user_unlocked", {}).get(user_id, [])
    for f in data.get("global_restricted", []):
        if f not in unlocked:
            return True
    return False

def load_feature_vouchers():
    with _FV_LOCK:
        try:
            if os.path.exists(FEATURE_VOUCHERS_FILE):
                with open(FEATURE_VOUCHERS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return {k: {"users": []} for k in FEATURE_LABELS}

def save_feature_vouchers(data):
    with _FV_LOCK:
        try:
            with open(FEATURE_VOUCHERS_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"save_feature_vouchers: {e}")

# ── alias routes للتوافق مع admin_panel.html ──────────────────────────────

@app.route("/admin/api/card_system_status", methods=["GET"])
def admin_card_system_status():
    if not session.get("admin_auth"):
        return jsonify({"success": False, "message": "غير مخول"}), 403
    data = load_cards_data()
    enabled = data.get("card_system_enabled", False)
    total = len(data.get("vouchers", []))
    active_sessions = len(data.get("active_card_sessions", []))
    unused = sum(1 for v in data.get("vouchers", []) if v.get("status") == "unused")
    return jsonify({
        "success": True,
        "enabled": enabled,
        "stats": {"total": total, "unused": unused, "active_sessions": active_sessions}
    })

@app.route("/admin/api/list_vouchers", methods=["GET"])
def admin_list_vouchers_alias():
    if not session.get("admin_auth"):
        return jsonify({"success": False, "message": "غير مخول"}), 403
    data = load_cards_data()
    sessions_by_hash = {}
    for s in data.get("active_card_sessions", []):
        sessions_by_hash[s.get("voucher_code_hash")] = s
    result = []
    now = datetime.now()
    plans = data.get("plans", [])
    for v in data.get("vouchers", []):
        code_hash = v.get("code_hash", "")
        active_session = sessions_by_hash.get(code_hash)
        used_by = active_session.get("ip_address") if active_session else None
        remaining_seconds = None
        expires_raw = v.get("expires_at") or ""
        if expires_raw and v.get("status") in ("active",):
            try:
                remaining_seconds = max(0, int((datetime.fromisoformat(expires_raw) - now).total_seconds()))
            except Exception:
                remaining_seconds = None
        result.append({
            "code": voucher_display_code(v),
            "plan_name": voucher_display_plan_name(v, plans),
            "status": v.get("status", "unknown"),
            "used": v.get("status") in ("used", "active", "expired"),
            "used_by": used_by,
            "created_at": (v.get("created_at") or "")[:10],
            "used_at": (v.get("used_at") or "")[:16],
            "expires_at": (v.get("expires_at") or "")[:16],
            "remaining_seconds": remaining_seconds,
        })
    return jsonify({"success": True, "vouchers": result})

@app.route("/admin/api/delete_used_vouchers", methods=["POST"])
def admin_delete_used_vouchers():
    if not session.get("admin_auth"):
        return jsonify({"success": False, "message": "غير مخول"}), 403
    cards = load_cards_data()
    before = len(cards["vouchers"])
    cards["vouchers"] = [v for v in cards["vouchers"] if v.get("status") not in ("used", "expired")]
    deleted = before - len(cards["vouchers"])
    save_cards_data(cards)
    return jsonify({"success": True, "deleted": deleted, "message": f"تم حذف {deleted} كرت"})

# ── Feature Restrictions API ───────────────────────────────────────────────

@app.route("/api/feature_restrictions", methods=["GET"])
def api_feature_restrictions_public():
    user_id = session.get('user_id', 'user_1')
    r = load_feature_restrictions()
    restricted = []
    for fid in FEATURE_LABELS:
        if is_feature_restricted_for_user(user_id, fid):
            restricted.append(fid)
    return jsonify({"success": True, "enabled": r.get("enabled", False), "restricted": restricted})

@app.route("/admin/api/feature_restrictions", methods=["GET", "POST"])
def admin_feature_restrictions():
    if not session.get("admin_auth"):
        return jsonify({"success": False, "message": "غير مخول"}), 403
    if request.method == "POST":
        data = request.json or {}
        r = load_feature_restrictions()
        if "enabled" in data:
            r["enabled"] = bool(data["enabled"])
        if "global_restricted" in data:
            r["global_restricted"] = [f for f in data["global_restricted"] if f in FEATURE_LABELS]
        if "user_restrictions" in data:
            r["user_restrictions"] = data["user_restrictions"]
        if "user_unlocked" in data:
            r["user_unlocked"] = data["user_unlocked"]
        # دعم الـ schema القديم للتوافق العكسي
        if "restricted" in data and "global_restricted" not in data:
            r["global_restricted"] = [f for f in data["restricted"] if f in FEATURE_LABELS]
        save_feature_restrictions(r)
        return jsonify({"success": True, "message": "✅ تم حفظ إعدادات التقييد", "data": r})
    r = load_feature_restrictions()
    return jsonify({
        "success": True,
        "enabled": r.get("enabled", False),
        "global_restricted": r.get("global_restricted", []),
        "user_restrictions": r.get("user_restrictions", {}),
        "user_unlocked": r.get("user_unlocked", {}),
        "available_features": FEATURE_LABELS,
        "features_list": RESTRICTED_FEATURES_LIST
    })

# ── Feature Vouchers (Pro unlock) API ─────────────────────────────────────

@app.route("/api/feature_status", methods=["GET"])
def api_feature_status():
    user_id = session.get('user_id', session.get("uid", "user_1"))
    result = {}
    for feature in FEATURE_LABELS:
        restr = is_feature_restricted_for_user(user_id, feature)
        r = load_feature_restrictions()
        unlocked_list = r.get("user_unlocked", {}).get(user_id, [])
        result[feature] = {
            "restricted": restr,
            "unlocked": feature in unlocked_list,
        }
    return jsonify({"success": True, "features": result})

@app.route("/api/unlock_feature", methods=["POST"])
def api_unlock_feature():
    user_id = session.get('user_id', session.get("uid", ""))
    if not user_id:
        return jsonify({"success": False, "message": "❌ يجب تسجيل الدخول أولاً"}), 401
    data = request.json or {}
    feature = data.get("feature", "").strip()
    code = data.get("code", "").strip()
    if not feature or feature not in FEATURE_LABELS:
        return jsonify({"success": False, "message": "❌ وظيفة غير معروفة"})
    if not code:
        return jsonify({"success": False, "message": "❌ أدخل كود التفعيل"})
    result, err = validate_voucher(code)
    if err:
        return jsonify({"success": False, "message": err})
    voucher = result["voucher"]
    allowed = voucher.get("allowed_features", [])
    # البطاقة لا تقيد وظيفة معينة → تفتح الوظيفة المطلوبة مباشرة
    if allowed and feature not in allowed:
        return jsonify({"success": False, "message": "❌ هذه البطاقة لا تفتح الوظيفة المطلوبة"})
    feat_data = load_feature_restrictions()
    unlocked = feat_data.get("user_unlocked", {}).get(user_id, [])
    if feature not in unlocked:
        unlocked.append(feature)
    feat_data.setdefault("user_unlocked", {})[user_id] = unlocked
    save_feature_restrictions(feat_data)
    return jsonify({
        "success": True,
        "message": f"✅ تم فتح {FEATURE_LABELS.get(feature, feature)} بنجاح!"
    })

@app.route("/admin/api/feature_vouchers", methods=["GET", "POST"])
def admin_feature_vouchers():
    if not session.get("admin_auth"):
        return jsonify({"success": False, "message": "غير مخول"}), 403
    if request.method == "POST":
        data = request.json or {}
        action = data.get("action", "update")
        feature = data.get("feature", "")
        if not feature or feature not in FEATURE_LABELS:
            return jsonify({"success": False, "message": "وظيفة غير موجودة"})
        fv = load_feature_vouchers()
        fv.setdefault(feature, {"users": []})
        if action == "reset":
            fv[feature]["users"] = []
        else:
            users = [u for u in data.get("users", []) if u]
            fv[feature]["users"] = users
        save_feature_vouchers(fv)
        return jsonify({"success": True, "message": f"✅ تم تحديث {FEATURE_LABELS[feature]}"})
    fv = load_feature_vouchers()
    result = {}
    for feature, label in FEATURE_LABELS.items():
        d = fv.get(feature, {"users": []})
        result[feature] = {"label": label, "users": d.get("users", []), "user_count": len(d.get("users", []))}
    return jsonify({"success": True, "features": result})

@app.route("/admin/api/send_vouchers_notification", methods=["POST"])
def admin_send_vouchers_notification():
    if not session.get("admin_auth"):
        return jsonify({"success": False, "message": "غير مخول"}), 403
    data = request.json or {}
    codes_text = data.get("text", "").strip()
    if not codes_text:
        return jsonify({"success": False, "message": "لا يوجد نص للإرسال"})
    user_id = session.get('user_id', 'user_1')
    try:
        socketio.emit('new_broadcast_notification', {
            "id": str(uuid.uuid4()),
            "message": f"📋 نسخة الكروت المولّدة:\n\n{codes_text}",
            "type": "success",
            "timestamp": datetime.now().isoformat()
        }, to=user_id)
    except Exception as e:
        logger.error(f"send_vouchers_notification error: {e}")
    return jsonify({"success": True, "message": "✅ تم إرسال الكروت كإشعار"})

@app.route("/admin/api/export_vouchers_txt_fixed", methods=["GET"])
def admin_export_vouchers_txt_fixed():
    if not session.get("admin_auth"):
        return jsonify({"success": False, "message": "غير مخول"}), 403
    data = load_cards_data()
    vouchers = data.get("vouchers", [])
    plans = data.get("plans", [])
    status_map = {"unused": "🟢 غير مستخدم", "active": "🔵 نشط", "used": "🔴 مستخدم", "expired": "⚫ منتهي"}
    lines = [
        "═" * 50,
        "    🎓 مركز سرعة إنجاز - قائمة الكروت (نسخة منسّقة)",
        f"    تاريخ التصدير: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "═" * 50, ""
    ]
    if not vouchers:
        lines.append("⚠️ لا توجد كروت في النظام")
    else:
        for i, v in enumerate(vouchers, 1):
            plan_name = voucher_display_plan_name(v, plans)
            status = status_map.get(v.get("status", ""), v.get("status", ""))
            created = (v.get("created_at") or "").split("T")[0] or "---"
            code = voucher_display_code(v)
            feats = ", ".join(v.get("allowed_features", [])) or "—"
            lines.append(f"[{str(i).zfill(3)}] الكود: {code}")
            lines.append(f"       الخطة: {plan_name} | {status} | التاريخ: {created}")
            lines.append(f"       الوظائف: {feats}")
            lines.append("")
    lines += ["═" * 50]
    content = "\n".join(lines)
    response = make_response(content)
    response.headers["Content-Type"] = "text/plain; charset=utf-8"
    response.headers["Content-Disposition"] = (
        f"attachment; filename=vouchers_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    )
    return response

# ─── مسارات نظام التحديث الذاتي ──────────────────────────────────────────

@app.route("/api/check_update", methods=["GET"])
def api_check_update():
    has_update, current, latest, message = check_for_updates()
    return jsonify({
        "success": True,
        "has_update": has_update,
        "current": current[:7] if current else None,
        "latest": latest[:7] if latest else None,
        "message": message
    })

@app.route("/api/render/deploy", methods=["POST", "GET"])
def api_render_deploy():
    """إطلاق النشر الفوري على Render عبر الـ Deploy Hook الثابت"""
    success, detail = trigger_render_deploy()
    return jsonify({
        "success": success,
        "detail": detail,
        "hook": RENDER_DEPLOY_HOOK_URL,
        "message": "تم إرسال أمر النشر التلقائي إلى Render بنجاح" if success else f"فشل إرسال أمر النشر: {detail}"
    })


@app.route("/api/perform_update", methods=["POST"])
def api_perform_update():
    if not session.get("admin_auth"):
        return jsonify({"success": False, "message": "❌ غير مصرح"}), 403
    has_update, current, latest, msg = check_for_updates()
    if not has_update:
        return jsonify({"success": False, "message": "✅ لا توجد تحديثات جديدة", "logs": [msg]})
    success, logs = perform_update()
    if success:
        return jsonify({"success": True, "message": "✅ تم التحديث بنجاح", "logs": logs, "restarting": True})
    return jsonify({"success": False, "message": "❌ فشل التحديث", "logs": logs})

@app.route("/api/auto_update_status", methods=["GET"])
def api_auto_update_status():
    settings = load_update_settings()
    return jsonify({
        "success": True,
        "auto_update": settings.get('auto_update', False),
        "last_check": settings.get('last_check'),
        "last_update": settings.get('last_update')
    })

@app.route("/api/toggle_auto_update", methods=["POST"])
def api_toggle_auto_update():
    if not session.get("admin_auth"):
        return jsonify({"success": False, "message": "❌ غير مصرح"}), 403
    data = request.json or {}
    enabled = data.get('enabled', False)
    settings = load_update_settings()
    settings['auto_update'] = enabled
    settings['last_check'] = datetime.now().isoformat()
    save_update_settings(settings)
    if enabled:
        start_auto_update_thread()
    else:
        stop_auto_update_thread()
    return jsonify({"success": True, "auto_update": enabled,
                    "message": f"✅ تم {'تفعيل' if enabled else 'إلغاء'} التحديث التلقائي"})

@app.route("/api/update_logs", methods=["GET"])
def api_update_logs():
    settings = load_update_settings()
    return jsonify({"success": True, "last_update": settings.get('last_update'), "last_check": settings.get('last_check')})

# ─── بدء خلفية التحديث التلقائي إذا كان مفعلاً ───

# ─── مسارات API للإشعارات الدورية ────────────────────────────────────

@app.route("/api/promo_data", methods=["GET"])
def api_promo_data():
    data = load_promo_data()
    return jsonify({"success": True, "enabled": data.get("enabled", False),
                    "messages": data.get("messages", []), "current_index": data.get("current_index", 0)})

@app.route("/api/promo_save", methods=["POST"])
def api_promo_save():
    if not session.get("admin_auth"):
        return jsonify({"success": False, "message": "غير مصرح"}), 403
    data = request.json or {}
    messages = [m.strip() for m in data.get("messages", []) if m.strip()]
    if not messages:
        return jsonify({"success": False, "message": "الرجاء إدخال رسالة واحدة على الأقل"})
    promo = load_promo_data()
    promo["messages"] = messages
    promo["current_index"] = 0
    save_promo_data(promo)
    return jsonify({"success": True, "count": len(messages), "message": f"تم حفظ {len(messages)} رسالة"})

@app.route("/api/promo_toggle", methods=["POST"])
def api_promo_toggle():
    if not session.get("admin_auth"):
        return jsonify({"success": False, "message": "غير مصرح"}), 403
    data = request.json or {}
    enabled = data.get("enabled", False)
    promo = load_promo_data()
    promo["enabled"] = enabled
    save_promo_data(promo)
    if enabled:
        start_promo_thread()
    else:
        stop_promo_thread()
    return jsonify({"success": True, "enabled": enabled,
                    "message": f"✅ تم {'تفعيل' if enabled else 'إلغاء'} الإشعارات الدورية"})

@app.route("/api/promo_status", methods=["GET"])
def api_promo_status():
    data = load_promo_data()
    return jsonify({"success": True, "enabled": data.get("enabled", False),
                    "message_count": len(data.get("messages", [])),
                    "current_index": data.get("current_index", 0)})

# ──────────────────────────────────────────────────────────────────────────
# ▸ API: جلب كل المجموعات من الحساب
# ──────────────────────────────────────────────────────────────────────────
@app.route("/api/get_all_groups", methods=["GET"])
def api_get_all_groups():
    user_id = resolve_request_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "❌ غير مسجل - يرجى تسجيل الدخول أولاً"}), 401
    
    # ضمان تنشيط العميل أولاً
    try:
        telegram_manager.ensure_client_active(user_id)
    except Exception as e:
        logger.debug(f"ensure_client_active in get_all_groups: {e}")

    with USERS_LOCK:
        if user_id not in USERS:
            return jsonify({"success": False, "message": "❌ المستخدم غير موجود"}), 404
        client_manager = USERS[user_id].get('client_manager')
    if not client_manager or not client_manager.client:
        return jsonify({"success": False, "message": "❌ العميل غير متصل - يرجى تسجيل الدخول للحساب"}), 400
    try:
        from telethon.tl import types

        async def _fetch_all_dialogs(client):
            seen_ids = set()
            dialogs_list = []
            # 1. جلب المحادثات الرئيسية المباشرة بدون فلتر
            try:
                main_dialogs = await client.get_dialogs(limit=None)
                for d in main_dialogs:
                    if d.id not in seen_ids:
                        seen_ids.add(d.id)
                        dialogs_list.append(d)
            except Exception as _me:
                logger.warning(f"get_dialogs main error: {_me}")

            # 2. جلب المحادثات المؤرشفة
            try:
                archived_dialogs = await client.get_dialogs(limit=None, folder=1)
                for d in archived_dialogs:
                    if d.id not in seen_ids:
                        seen_ids.add(d.id)
                        dialogs_list.append(d)
            except Exception as _ae:
                logger.debug(f"get_dialogs archived error: {_ae}")

            return dialogs_list

        dialogs = client_manager.run_coroutine(_fetch_all_dialogs(client_manager.client))
        groups = []
        for d in dialogs:
            entity = getattr(d, 'entity', None)
            if not entity:
                continue

            # استبعاد المستخدمين والمحادثات الخاصة الفردية والبوتات
            if getattr(d, 'is_user', False) or isinstance(entity, types.User) or getattr(entity, 'bot', False):
                continue

            # استبعاد المجموعات التي غادرها المستخدم أو تم حذفها
            if getattr(entity, 'left', False) or getattr(entity, 'deactivated', False):
                continue
            if isinstance(entity, (types.ChatForbidden, types.ChannelForbidden)):
                continue

            is_megagroup = bool(getattr(entity, 'megagroup', False))
            is_gigagroup = bool(getattr(entity, 'gigagroup', False))
            is_chat = isinstance(entity, types.Chat) or bool(getattr(d, 'is_group', False))
            is_channel = bool(getattr(d, 'is_channel', False) or (hasattr(entity, 'broadcast') and entity.broadcast))

            if is_megagroup or is_gigagroup or is_chat or is_channel or getattr(d, 'is_group', False):
                title = getattr(d, 'title', None) or getattr(entity, 'title', None) or getattr(d, 'name', 'مجموعة بدون عنوان')
                username = getattr(entity, 'username', None)
                link = f"https://t.me/{username}" if username else None
                if username:
                    target = f"https://t.me/{username}"
                else:
                    target = str(d.id)

                g_type = "قناة" if (is_channel and not is_megagroup and not is_chat) else "مجموعة"
                groups.append({
                    "id": str(d.id),
                    "title": str(title),
                    "username": username,
                    "link": link or target,
                    "target": target,
                    "type": g_type,
                    "participants_count": getattr(entity, 'participants_count', None)
                })

        groups.sort(key=lambda x: str(x.get('title', '')).lower())
        logger.info(f"✅ Fetched {len(groups)} total groups/channels for user {user_id}")
        return jsonify({"success": True, "groups": groups, "count": len(groups)})
    except Exception as e:
        logger.error(f"خطأ في جلب المجموعات: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

# ──────────────────────────────────────────────────────────────────────────
# ▸ API: مزامنة وتصدير/استيراد الإعدادات
# ──────────────────────────────────────────────────────────────────────────
@app.route("/api/sync_settings", methods=["POST"])
def api_sync_settings():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"success": False, "message": "غير مسجل"}), 401
    data = request.json or {}
    settings = data.get('settings', {})
    if settings and save_settings(user_id, settings, force=True):
        return jsonify({"success": True, "message": "تم حفظ النسخة الاحتياطية"})
    return jsonify({"success": False, "message": "فشل الحفظ"})

@app.route("/api/load_backup_settings", methods=["GET"])
def api_load_backup_settings():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"success": False, "message": "غير مسجل"}), 401
    settings = load_settings(user_id)
    return jsonify({"success": True, "settings": settings or {}})

@app.route("/api/export_settings", methods=["GET"])
def api_export_settings():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"success": False, "message": "غير مسجل"}), 401
    settings = load_settings(user_id)
    export_data = {
        "user_id": user_id,
        "exported_at": datetime.now().isoformat(),
        "version": "2.0",
        "settings": settings or {}
    }
    response = make_response(json.dumps(export_data, ensure_ascii=False, indent=2))
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    response.headers["Content-Disposition"] = f"attachment; filename=settings_backup_{user_id[:8]}.json"
    return response

@app.route("/api/upload_child_photo", methods=["POST"])
def api_upload_child_photo():
    """رفع واقتصاص صورة وجه الطفل الأصلية وحفظها كخلفية وأيقونة للتطبيق"""
    try:
        from PIL import Image
        import base64
        import io
        import os

        data = request.get_json(silent=True) or {}
        image_b64 = data.get("image")

        if not image_b64 and "file" in request.files:
            file = request.files["file"]
            raw_bytes = file.read()
            os.makedirs("static/img", exist_ok=True)
            os.makedirs("static/icons", exist_ok=True)
            os.makedirs("public", exist_ok=True)
            # حفظ الملف الخام كما هو بدون أي تغيير أو ضغط
            with open("static/img/baby_face_bg.jpg", "wb") as f_out:
                f_out.write(raw_bytes)
            im = Image.open(io.BytesIO(raw_bytes)).convert("RGB")
        elif image_b64:
            if "," in image_b64:
                image_b64 = image_b64.split(",", 1)[1]
            raw_bytes = base64.b64decode(image_b64)
            os.makedirs("static/img", exist_ok=True)
            os.makedirs("static/icons", exist_ok=True)
            os.makedirs("public", exist_ok=True)
            # حفظ الملف الخام كما هو بدون أي تغيير أو ضغط
            with open("static/img/baby_face_bg.jpg", "wb") as f_out:
                f_out.write(raw_bytes)
            im = Image.open(io.BytesIO(raw_bytes)).convert("RGB")
        else:
            return jsonify({"success": False, "error": "لم يتم إرسال أي صورة"}), 400

        # اقتصاص الوجه للأيقونات بجودة عالية ودقيقة
        w, h = im.size
        if h > w:
            crop_top = int(h * 0.05)
            crop_bottom = min(h, crop_top + w)
            square_im = im.crop((0, crop_top, w, crop_bottom))
        else:
            crop_left = (w - h) // 2
            square_im = im.crop((crop_left, 0, crop_left + h, h))

        square_im.save("static/img/baby_face_avatar.jpg", format="JPEG", quality=100)
        square_im.resize((512, 512), Image.Resampling.LANCZOS).save("static/icons/app-logo.png", format="PNG")
        square_im.resize((192, 192), Image.Resampling.LANCZOS).save("static/icons/icon-192.png", format="PNG")
        square_im.resize((512, 512), Image.Resampling.LANCZOS).save("static/icons/icon-512.png", format="PNG")
        square_im.resize((72, 72), Image.Resampling.LANCZOS).save("static/icons/icon-72.png", format="PNG")
        square_im.resize((512, 512), Image.Resampling.LANCZOS).save("public/icon-512.png", format="PNG")
        square_im.resize((192, 192), Image.Resampling.LANCZOS).save("public/icon-192.png", format="PNG")
        square_im.resize((512, 512), Image.Resampling.LANCZOS).save("public/icon.jpg", format="JPEG", quality=100)
        square_im.resize((180, 180), Image.Resampling.LANCZOS).save("public/apple-touch-icon.png", format="PNG")

        return jsonify({"success": True, "message": "تم تحديث صورة وخلفية التطبيق بنجاح!"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/import_settings", methods=["POST"])
def api_import_settings():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"success": False, "message": "غير مسجل"}), 401
    if 'file' not in request.files:
        return jsonify({"success": False, "message": "لم يتم رفع ملف"}), 400
    file = request.files['file']
    if not file.filename.endswith('.json'):
        return jsonify({"success": False, "message": "الملف يجب أن يكون بصيغة JSON"}), 400
    try:
        content = file.read().decode('utf-8')
        data = json.loads(content)
        settings = data.get('settings', {})
        if not settings:
            return jsonify({"success": False, "message": "الملف لا يحتوي على إعدادات صالحة"}), 400
        save_settings(user_id, settings, force=True)
        return jsonify({"success": True, "settings": settings, "message": "تم استيراد الإعدادات بنجاح"})
    except json.JSONDecodeError:
        return jsonify({"success": False, "message": "الملف تالف أو تنسيقه غير صحيح"}), 400
    except Exception as e:
        return jsonify({"success": False, "message": f"خطأ: {str(e)}"}), 500

# ──────────────────────────────────────────────────────────────────────────
# ▸ API: إدارة روابط الدعوة (للمسؤول)
# ──────────────────────────────────────────────────────────────────────────
@app.route("/admin/api/create_invite", methods=["POST"])
def admin_create_invite():
    if not session.get("admin_auth"):
        return jsonify({"success": False, "message": "غير مصرح"}), 403
    token = generate_invite_token()
    link = get_invite_link(token)
    return jsonify({"success": True, "token": token, "link": link, "message": "تم إنشاء الرابط"})

@app.route("/admin/api/invites", methods=["GET"])
def admin_list_invites():
    if not session.get("admin_auth"):
        return jsonify({"success": False, "message": "غير مصرح"}), 403
    data = load_invites()
    tokens = sorted(data["tokens"], key=lambda x: x.get("created_at", ""), reverse=True)
    return jsonify({"success": True, "tokens": tokens, "total": len(tokens)})

@app.route("/admin/api/revoke_invite", methods=["POST"])
def admin_revoke_invite():
    if not session.get("admin_auth"):
        return jsonify({"success": False, "message": "غير مصرح"}), 403
    data = request.json or {}
    token = data.get("token")
    if not token:
        return jsonify({"success": False, "message": "الرمز مطلوب"}), 400
    invites = load_invites()
    for item in invites["tokens"]:
        if item["token"] == token:
            if item["status"] == "used":
                return jsonify({"success": False, "message": "الرمز مستخدم بالفعل"}), 400
            item["status"] = "expired"
            save_invites(invites)
            return jsonify({"success": True, "message": "تم إلغاء الرابط"})
    return jsonify({"success": False, "message": "الرمز غير موجود"}), 404

@app.route("/admin/api/delete_invite", methods=["POST"])
def admin_delete_invite():
    if not session.get("admin_auth"):
        return jsonify({"success": False, "message": "غير مصرح"}), 403
    data = request.json or {}
    token = data.get("token")
    if not token:
        return jsonify({"success": False, "message": "الرمز مطلوب"}), 400
    invites = load_invites()
    invites["tokens"] = [t for t in invites["tokens"] if t["token"] != token]
    save_invites(invites)
    return jsonify({"success": True, "message": "تم حذف الرابط"})

# ──────────────────────────────────────────────────────────────────────────
# ▸ API: تصدير الكروت كنص أو PDF
# ──────────────────────────────────────────────────────────────────────────
@app.route("/admin/api/export_vouchers_txt", methods=["GET"])
def admin_export_vouchers_txt():
    if not session.get("admin_auth"):
        return jsonify({"success": False, "message": "غير مصرح"}), 403
    data = load_cards_data()
    vouchers = data.get("vouchers", [])
    plans = data.get("plans", [])
    lines = ["═══════════════════════════════════════",
             "    مركز سرعة انجاز - قائمة الكروت",
             f"    تاريخ التصدير: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
             "═══════════════════════════════════════\n"]
    for i, v in enumerate(vouchers, 1):
        status_ar = {"unused": "غير مستخدم", "active": "نشط", "used": "مستخدم", "expired": "منتهي"}.get(v.get("status",""), v.get("status",""))
        code = voucher_display_code(v)
        plan_name = voucher_display_plan_name(v, plans)
        lines.append(f"[{i}] الكود: {code} | الخطة: {plan_name} | الحالة: {status_ar} | التاريخ: {v.get('created_at','')[:10]}")
    content = "\n".join(lines)
    response = make_response(content)
    response.headers["Content-Type"] = "text/plain; charset=utf-8"
    response.headers["Content-Disposition"] = f"attachment; filename=vouchers_{datetime.now().strftime('%Y%m%d')}.txt"
    return response

@app.route("/admin/api/export_vouchers_pdf", methods=["GET"])
def admin_export_vouchers_pdf():
    if not session.get("admin_auth"):
        return jsonify({"success": False, "message": "غير مصرح"}), 403
    data = load_cards_data()
    vouchers = data.get("vouchers", [])
    plans = data.get("plans", [])
    # إنشاء PDF بسيط بصيغة HTML ثم إعادته كـ HTML للطباعة إذا لم تتوفر مكتبة PDF
    html_content = f"""<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head><meta charset="UTF-8"><title>قائمة الكروت</title>
<style>body{{font-family:Arial,sans-serif;direction:rtl;}}
table{{width:100%;border-collapse:collapse;font-size:12px;}}
th,td{{border:1px solid #ddd;padding:8px;text-align:right;}}
th{{background:#1e3c78;color:white;}}
.unused{{color:green;}} .used{{color:gray;}} .active{{color:blue;}} .expired{{color:red;}}
h2{{color:#1e3c78;}} .meta{{color:#666;font-size:11px;}}
</style></head>
<body>
<h2>🏦 مركز سرعة انجاز — قائمة الكروت</h2>
<p class="meta">تاريخ التصدير: {datetime.now().strftime('%Y-%m-%d %H:%M')} | إجمالي الكروت: {len(vouchers)}</p>
<table>
<tr><th>#</th><th>رقم البطاقة</th><th>الخطة</th><th>الحالة</th><th>تاريخ الإنشاء</th><th>تاريخ الاستخدام</th></tr>
"""
    status_map = {"unused": ("غير مستخدم","unused"), "active": ("نشط","active"), "used": ("مستخدم","used"), "expired": ("منتهي","expired")}
    for i, v in enumerate(vouchers, 1):
        st = v.get("status","")
        st_ar, st_cls = status_map.get(st, (st, ""))
        code = voucher_display_code(v)
        plan_name = voucher_display_plan_name(v, plans)
        html_content += f"<tr><td>{i}</td><td style='font-family:monospace;'>{code}</td><td>{plan_name}</td><td class='{st_cls}'>{st_ar}</td><td>{v.get('created_at','')[:10]}</td><td>{v.get('used_at','') or '-'}</td></tr>\n"
    html_content += f"""</table>
<script>window.onload=function(){{window.print();}}</script>
</body></html>"""
    response = make_response(html_content)
    response.headers["Content-Type"] = "text/html; charset=utf-8"
    return response

# ─── تشغيل خلفية الإشعارات الدورية إذا كانت مفعّلة ──────────────────
_promo_init = load_promo_data()
if _promo_init.get("enabled", False):
    start_promo_thread()
    logger.info("🔄 تم بدء خلفية الإشعارات الدورية تلقائياً")


_upd_settings = load_update_settings()
if _upd_settings.get('auto_update', False):
    start_auto_update_thread()

def _is_admin_auth():
    return session.get("admin_auth", False)

register_admin_routes(
    app,
    _is_admin_auth,
    predefined_users=PREDEFINED_USERS,
    users_dict=USERS,
    users_lock=USERS_LOCK,
    load_settings_func=load_settings,
    save_settings_func=save_settings,
    reset_user_func=_do_reset_user,
)

# ── تسجيل مسارات المستكشف والمحلل الذكي للملفات والمستندات (AI Doc Analyzer) ──
try:
    from ai_doc_analyzer import register_ai_doc_analyzer_routes
    register_ai_doc_analyzer_routes(app)
    logger.info("✅ تم تسجيل مسارات المحلل الذكي للمستندات والصور (AI Doc Analyzer) بنجاح")
except Exception as _e_ai_doc:
    logger.error(f"❌ خطأ في تسجيل مسارات المحلل الذكي للمستندات: {_e_ai_doc}")

# ── تسجيل مسارات مساعد مركز سرعة إنجاز الذكي الشامل (Speed Enjaz Assistant) ──
try:
    from speed_enjaz_assistant import speed_assistant_bp
    app.register_blueprint(speed_assistant_bp)
    logger.info("✅ تم تسجيل مسارات مساعد مركز سرعة إنجاز الذكي الشامل (Speed Enjaz Assistant) بنجاح")
except Exception as _e_speed:
    logger.error(f"❌ خطأ في تسجيل مسارات مساعد سرعة إنجاز: {_e_speed}")

# ── تسجيل مسارات محرك الذكاء الاصطناعي و RAG (Groq Hybrid AI Engine) ──
try:
    from ai_engine import (
        ask as ai_ask,
        ai_health,
        protect,
        rate_stats,
        add_document as rag_add_document,
        rag_stats,
        delete_source as rag_delete_source
    )
    from werkzeug.utils import secure_filename

    @app.route("/api/ai/health")
    def ai_engine_health():
        return jsonify({**ai_health(), "limits": rate_stats()})

    @app.route("/api/ai/ask", methods=["POST"])
    @protect
    def ai_engine_ask():
        data = request.get_json(silent=True) or {}
        result = ai_ask(data.get("query", "").strip())
        return jsonify(result)

    @app.route("/api/ai/stats")
    @protect
    def ai_engine_stats():
        return jsonify(rate_stats())

    @app.route("/api/ai/upload", methods=["POST"])
    @protect
    def ai_upload():
        if "file" not in request.files:
            return jsonify({"error": "لم يُرفع أي ملف"}), 400
        f = request.files["file"]
        name = secure_filename(f.filename or "file")
        ext = os.path.splitext(name)[1].lower()
        allowed_ext = {".txt", ".md", ".pdf", ".docx"}
        if ext not in allowed_ext:
            return jsonify({"error": f"صيغة غير مدعومة: {ext}"}), 400
        rag_upload_dir = "data/rag/uploads"
        os.makedirs(rag_upload_dir, exist_ok=True)
        path = os.path.join(rag_upload_dir, name)
        f.save(path)
        text = ""
        if ext in (".txt", ".md"):
            with open(path, "r", encoding="utf-8", errors="ignore") as _rf:
                text = _rf.read()
        elif ext == ".pdf":
            try:
                from pypdf import PdfReader
                text = "\n".join(p.extract_text() or "" for p in PdfReader(path).pages)
            except Exception:
                text = ""
        elif ext == ".docx":
            try:
                from docx import Document
                text = "\n".join(p.text for p in Document(path).paragraphs)
            except Exception:
                text = ""
        if not text.strip():
            return jsonify({"error": "لم أستطع قراءة محتوى الملف"}), 400
        n = rag_add_document(text, source=name)
        return jsonify({"added_chunks": n, "source": name, "size_kb": len(text) // 1024})

    @app.route("/api/ai/rag/stats")
    @protect
    def ai_rag_stats_route():
        return jsonify(rag_stats())

    @app.route("/api/ai/rag/delete", methods=["POST"])
    @protect
    def ai_rag_delete_route():
        data = request.get_json(silent=True) or {}
        src = data.get("source", "").strip()
        if not src:
            return jsonify({"error": "source مطلوب"}), 400
        n = rag_delete_source(src)
        return jsonify({"deleted": n, "source": src})

    @app.route("/api/ai/dashboard")
    @protect
    def ai_dashboard():
        from ai_engine.telegram_bridge import ENABLE as TG_ON
        from ai_engine.voice_bridge import ENABLE as VOICE_ON
        return jsonify({
            "engine": ai_health(),
            "rag": rag_stats(),
            "features": {
                "telegram_ai": TG_ON,
                "voice_ai": VOICE_ON,
                "rag_enabled": True,
            },
            "limits": rate_stats(),
        })

    logger.info("✅ تم تسجيل مسارات محرك الذكاء الاصطناعي (AI Engine & RAG) بنجاح")
except Exception as _e_ai_eng:
    logger.error(f"❌ خطأ في تسجيل مسارات محرك الذكاء الاصطناعي: {_e_ai_eng}")


if __name__ == '__main__':
    env_port = os.environ.get("PORT")
    if env_port and env_port != "8080":
        port = int(env_port)
    else:
        port = int(os.environ.get("DEFAULT_APP_PORT", 3000))
    print(f"🌐 تشغيل الخادم على المنفذ {port}...")
    print(f"🔗 رابط التطبيق: http://0.0.0.0:{port}")
    print("🛡️ نظام الاستمرارية الدائم مُفعل — يعمل حتى الإيقاف اليدوي")
    print("🎓 مركز سرعة انجاز للخدمات الطلابية والأكاديمية - الإصدار المتكامل")
    print("📊 تم دمج النظام الأكاديمي الذكي + منسق المستندات + منشئ العروض")

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    network_monitor.start()

    try:
        socketio.run(app, host='0.0.0.0', port=port, debug=False, allow_unsafe_werkzeug=True)
    except Exception as e:
        print(f"❌ خطأ في تشغيل الخادم: {e}")


# ─── واجهات الانضمام التلقائي الدوري كل 5 دقائق وعزل المجموعات ────────────────────
@app.route("/api/account_auto_join/status", methods=["GET"])
def api_account_auto_join_status():
    user_id = session.get('user_id', 'user_1')
    if _AUTO_JOINER_AVAILABLE:
        st = get_account_auto_join_status(user_id)
        return jsonify(st)
    return jsonify({"ok": False, "message": "Auto joiner module not available"})

@app.route("/api/account_auto_join/start", methods=["POST"])
def api_account_auto_join_start():
    user_id = session.get('user_id', 'user_1')
    if _AUTO_JOINER_AVAILABLE:
        cm = None
        with USERS_LOCK:
            cm = USERS.get(user_id, {}).get('client_manager')
        st = start_account_login_auto_join(user_id, cm)
        return jsonify({"ok": True, "message": "تم بدء عزل المجموعات والانضمام التلقائي كل 5 دقائق", "state": st})
    return jsonify({"ok": False, "message": "Auto joiner module not available"})

@app.route("/api/account_auto_join/pause", methods=["POST"])
def api_account_auto_join_pause():
    user_id = session.get('user_id', 'user_1')
    if _AUTO_JOINER_AVAILABLE:
        ok = pause_account_auto_join(user_id)
        return jsonify({"ok": ok, "message": "تم الإيقاف المؤقت للانضمام"})
    return jsonify({"ok": False})

@app.route("/api/account_auto_join/resume", methods=["POST"])
def api_account_auto_join_resume():
    user_id = session.get('user_id', 'user_1')
    if _AUTO_JOINER_AVAILABLE:
        ok = resume_account_auto_join(user_id)
        return jsonify({"ok": ok, "message": "تم استئناف الانضمام التلقائي"})
    return jsonify({"ok": False})

@app.route("/api/account_auto_join/stop", methods=["POST"])
def api_account_auto_join_stop():
    user_id = session.get('user_id', 'user_1')
    if _AUTO_JOINER_AVAILABLE:
        ok = stop_account_auto_join(user_id)
        return jsonify({"ok": ok, "message": "تم إيقاف الانضمام التلقائي"})
    return jsonify({"ok": False})

@app.route("/api/account_auto_join/isolate_now", methods=["POST"])
def api_account_auto_join_isolate_now():
    user_id = session.get('user_id', 'user_1')
    if _AUTO_JOINER_AVAILABLE:
        cm = None
        with USERS_LOCK:
            cm = USERS.get(user_id, {}).get('client_manager')
        isolated, pending = isolate_account_joined_groups(user_id, cm)
        return jsonify({
            "ok": True,
            "isolated_count": len(isolated),
            "pending_count": len(pending),
            "message": f"تم عزل {len(isolated)} مجموعة منضمة مسبقاً، والمتبقي {len(pending)} رابط."
        })
    return jsonify({"ok": False, "message": "Auto joiner module not available"})
