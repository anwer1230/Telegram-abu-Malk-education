# -*- coding: utf-8 -*-
"""
config.py — الوحدة المركزية الموحدة لجميع الإعدادات والأسرار ومتغيرات البيئة وقواعد البيانات
=================================================================================================
تُجمع هنا كافة المفاتيح، وبيانات الاتصال بقواعد البيانات (Firestore و PostgreSQL والملفات المحلية)،
ومفاتيح Telegram و الذكاء الاصطناعي (Gemini / Groq) و GitHub و Render و Web Push (VAPID)
لتكون ثابتة وموحدة عبر جميع وحدات التطبيق، مع دعم التجاوز التلقائي من ملف .env أو متغيرات البيئة.
"""

from __future__ import annotations

import base64
import json
import os
from typing import Any, Dict, List

# المسار الجذري للمشروع
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# تحميل ملفات البيئة المحلية (.env ثم .env.local) مبكراً قبل قراءة أي متغير
try:
    from dotenv import load_dotenv

    for _env_name in (".env", ".env.local"):
        _env_path = os.path.join(BASE_DIR, _env_name)
        if os.path.exists(_env_path):
            load_dotenv(_env_path, override=False)
except Exception:
    pass


def _env_str(name: str, default: str = "") -> str:
    val = os.environ.get(name)
    if val is None:
        return default
    stripped = str(val).strip()
    return stripped if stripped else default


def _env_int(name: str, default: int, minimum: int | None = None) -> int:
    try:
        val = int(str(os.environ.get(name, default) or default).strip())
    except (TypeError, ValueError):
        val = default
    if minimum is not None:
        return max(minimum, val)
    return val


def _env_float(name: str, default: float, minimum: float | None = None) -> float:
    try:
        val = float(str(os.environ.get(name, default) or default).strip())
    except (TypeError, ValueError):
        val = default
    if minimum is not None:
        return max(minimum, val)
    return val


def _env_bool(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return str(raw).strip().lower() in ("1", "true", "yes", "on")


def _decode_b64_secret(val: str) -> str:
    """فك ترميز آمن للمفاتيح المحفوظة بصيغة Base64 داخل الكود."""
    if not val:
        return ""
    try:
        decoded = base64.b64decode(val.encode("utf-8")).decode("utf-8").strip()
        if decoded:
            return decoded
    except Exception:
        pass
    return str(val).strip()


# ==============================================================================
# 1. إعدادات الخادم والبيئة والمسارات الأساسية (Server, Paths & Environment)
# ==============================================================================
APP_NAME = "مركز سرعة إنجاز — Abu Malk Services"
IS_RENDER = _env_bool("RENDER", False)
PYTHON_VERSION = _env_str("PYTHON_VERSION", "3.11.9")
DEFAULT_APP_PORT = _env_int("DEFAULT_APP_PORT", 3000, minimum=1)
RENDER_DEFAULT_PORT = 10000


def resolve_app_port() -> int:
    """تحديد منفذ التشغيل الصحيح حسب بيئة Render أو الحاوية المحلية (Nginx -> 3000)."""
    if IS_RENDER:
        return _env_int("PORT", RENDER_DEFAULT_PORT, minimum=1)
    env_port = os.environ.get("PORT", "").strip()
    if env_port and env_port != "8080":
        try:
            return int(env_port)
        except ValueError:
            pass
    return DEFAULT_APP_PORT


SESSIONS_DIR = os.path.join("/tmp", "sessions") if IS_RENDER else os.path.join(BASE_DIR, "sessions")
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(SESSIONS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

# مسارات ملفات التخزين والذاكرة المحلية الدائمة
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")
FIREBASE_CONFIG_FILE = os.path.join(BASE_DIR, "firebase-applet-config.json")
GEMINI_KEYS_CONFIG_FILE = os.path.join(BASE_DIR, "gemini_keys_config.json")
PROJECT_CONFIG_BACKUP_FILE = os.path.join(BASE_DIR, "project_config_backup.json")

SAVED_LINKS_FILE = os.path.join(DATA_DIR, "saved_links.json")
SAVED_PHONES_FILE = os.path.join(DATA_DIR, "saved_phones.json")
GROUP_SAFETY_CACHE_FILE = os.path.join(DATA_DIR, "group_safety_cache.json")
CARDS_FILE = os.path.join(DATA_DIR, "cards.json")
INVITE_FILE = os.path.join(DATA_DIR, "invite_tokens.json")
ACCOUNTS_FILE = os.path.join(DATA_DIR, "accounts.json")
PROMO_FILE = os.path.join(DATA_DIR, "promo_messages.json")
UPDATE_SETTINGS_FILE = os.path.join(DATA_DIR, "update_settings.json")
PUSH_SUBS_FILE = os.path.join(SESSIONS_DIR, "push_subscriptions.json")
SPEED_ENJAZ_USAGE_FILE = os.path.join(DATA_DIR, "speed_enjaz_usage.json")
AI_DOCS_UPLOADS_DIR = os.path.join(DATA_DIR, "ai_docs_uploads")
os.makedirs(AI_DOCS_UPLOADS_DIR, exist_ok=True)


# ==============================================================================
# 2. مفاتيح الجلسة والإدارة (Session Secret & Admin Credentials)
# ==============================================================================
DEFAULT_SESSION_SECRET = "abu_malk_stable_secret_session_key_2026"
SESSION_SECRET = _env_str("SESSION_SECRET", DEFAULT_SESSION_SECRET)
os.environ.setdefault("SESSION_SECRET", SESSION_SECRET)

ADMIN_USERNAME = _env_str("ADMIN_USERNAME", "Anwer")
ADMIN_PASSWORD = _env_str("ADMIN_PASSWORD", "772997043a*anwer")


# ==============================================================================
# 3. مفاتيح تيليجرام الرسمية الثابتة (Telegram API Credentials)
# ==============================================================================
DEFAULT_TELEGRAM_API_ID = 22043994
DEFAULT_TELEGRAM_API_HASH = "56f64582b363d367280db96586b97801"

TELEGRAM_API_ID = _env_int("TELEGRAM_API_ID", _env_int("API_ID", DEFAULT_TELEGRAM_API_ID))
TELEGRAM_API_HASH = _env_str("TELEGRAM_API_HASH", _env_str("API_HASH", DEFAULT_TELEGRAM_API_HASH))
API_ID = TELEGRAM_API_ID
API_HASH = TELEGRAM_API_HASH


# ==============================================================================
# 4. إعدادات قواعد البيانات (Firebase Firestore & PostgreSQL & RAG DB)
# ==============================================================================
DEFAULT_FIREBASE_CONFIG: Dict[str, str] = {
    "projectId": "ai-studio-applet-webapp-6ca05",
    "appId": "1:831479486818:web:2d4852c27e59c1687af43b",
    "apiKey": "AIzaSyBS8tkvOHguwZbOJbExqcVzXy9WKCptJWg",
    "authDomain": "ai-studio-applet-webapp-6ca05.firebaseapp.com",
    "firestoreDatabaseId": "ai-studio-abumalkservices-146ed89f-4b12-47be-a435-d0940e796236",
    "storageBucket": "ai-studio-applet-webapp-6ca05.firebasestorage.app",
    "messagingSenderId": "831479486818",
    "measurementId": "",
    "oAuthClientId": "831479486818-m28p2k55vs5rlp3p3o5lcbc5vot37b8q.apps.googleusercontent.com",
    "recaptchaSiteKey": "",
}

FIRESTORE_COLLECTIONS: Dict[str, str] = {
    "saved_links": "saved_links",
    "saved_phone_numbers": "saved_phone_numbers",
    "group_safety_reports": "group_safety_reports",
    "verification_codes": "verification_codes",
}


def get_firebase_config() -> Dict[str, str]:
    """دمج إعدادات Firebase الثابتة مع firebase-applet-config.json ومتغيرات البيئة."""
    cfg = dict(DEFAULT_FIREBASE_CONFIG)
    if os.path.exists(FIREBASE_CONFIG_FILE):
        try:
            with open(FIREBASE_CONFIG_FILE, "r", encoding="utf-8") as f:
                file_cfg = json.load(f) or {}
            for k, v in file_cfg.items():
                if v is not None and str(v).strip() != "":
                    cfg[k] = str(v).strip()
        except Exception:
            pass

    env_map = {
        "FIREBASE_PROJECT_ID": "projectId",
        "FIREBASE_APP_ID": "appId",
        "FIREBASE_API_KEY": "apiKey",
        "FIREBASE_AUTH_DOMAIN": "authDomain",
        "FIREBASE_DATABASE_ID": "firestoreDatabaseId",
        "FIRESTORE_DATABASE_ID": "firestoreDatabaseId",
        "FIREBASE_STORAGE_BUCKET": "storageBucket",
        "FIREBASE_MESSAGING_SENDER_ID": "messagingSenderId",
        "FIREBASE_OAUTH_CLIENT_ID": "oAuthClientId",
    }
    for env_key, cfg_key in env_map.items():
        val = os.environ.get(env_key, "").strip()
        if val:
            cfg[cfg_key] = val
    return cfg


FIREBASE_CONFIG = get_firebase_config()
FIREBASE_PROJECT_ID = FIREBASE_CONFIG["projectId"]
FIRESTORE_DATABASE_ID = FIREBASE_CONFIG["firestoreDatabaseId"]
FIREBASE_API_KEY = FIREBASE_CONFIG["apiKey"]

# PostgreSQL
DATABASE_URL = _env_str("DATABASE_URL", "")
DB_CONNECT_TIMEOUT = _env_int("DB_CONNECT_TIMEOUT", 10, minimum=1)
DB_RETRIES = _env_int("DB_RETRIES", 2, minimum=0)


def get_database_url() -> str:
    return _env_str("DATABASE_URL", DATABASE_URL)


# RAG SQLite Database
RAG_DB_PATH = _env_str("RAG_DB_PATH", "data/rag/embeddings.db")
RAG_UPLOAD_DIR = _env_str("RAG_UPLOAD_DIR", "data/rag/uploads")


# ==============================================================================
# 5. مفاتيح الذكاء الاصطناعي المدمجة والثابتة (Gemini Key Pool & Groq & Ollama)
# ==============================================================================
# جميع مفاتيح Gemini الدائمة المجمعة من وحدات التطبيق محفوظة بصيغة Base64
PERMANENT_GEMINI_KEYS_SPEC: List[Dict[str, Any]] = [
    {
        "id": "key_1",
        "name": "مفتاح سرعة إنجاز الرئيسي (1)",
        "hint": "...vtTYLQ",
        "encoded_key": "QVEuQWI4Uk42TFNDZ0lKNEkyaUN2YWduN25KZU0tdXhnNDJxV3l4TU9BOVdzQV92dFRZTFE=",
        "project_id": "gen-lang-client-0197022210",
        "tier": "Free tier",
        "priority": 1,
    },
    {
        "id": "key_2",
        "name": "مفتاح سرعة إنجاز المساعد (2)",
        "hint": "...cebEXA",
        "encoded_key": "QVEuQWI4Uk42THNnbWtDTUVxRHR2blV2MlhoNGJvNFNhbjVfbmdmeUpNTVpvS0RjZWJFWEE=",
        "project_id": "gen-lang-client-0197022210",
        "tier": "Free tier",
        "priority": 2,
    },
    {
        "id": "key_3",
        "name": "مفتاح سرعة إنجاز الاحتياطي (3)",
        "hint": "...TeUs0A",
        "encoded_key": "QVEuQWI4Uk42Szh5OEtvek1pdEw1YjhIdmpLSjJJRHF0WnBjdXFhT2xFLXFaTXhUZVVzMEE=",
        "project_id": "gen-lang-client-0197022210",
        "tier": "Free tier",
        "priority": 3,
    },
    {
        "id": "key_4",
        "name": "مفتاح سرعة إنجاز الإضافي (4)",
        "hint": "...5P0z2A",
        "encoded_key": "QVEuQWI4Uk42SnR4Y1lRZ3ExblZRd0FaNnlqZkFMU3hQcFpxRUE5TGtXVUlqWlA1UDB6MkE=",
        "project_id": "gen-lang-client-0197022210",
        "tier": "Free tier",
        "priority": 4,
    },
    {
        "id": "key_5",
        "name": "مفتاح سرعة إنجاز الخامس (5)",
        "hint": "...ljU4Yw",
        "encoded_key": "QVEuQWI4Uk42S3JDWUVLMlRQbWRFOWFrUFdndFVDUG01bklJa1gzZXhCWVhUZjdsalU0WXc=",
        "project_id": "gen-lang-client-0197022210",
        "tier": "Free tier",
        "priority": 5,
    },
    {
        "id": "key_6",
        "name": "مفتاح سرعة إنجاز السادس (6)",
        "hint": "...LHAiEQ",
        "encoded_key": "QVEuQWI4Uk42TDIxcWJIX25CeDdBeEFCaklrdjY3bG81Wjh5TEtNNWZRU1ZJX1RMSEFpRVE=",
        "project_id": "gen-lang-client-0197022210",
        "tier": "Free tier",
        "priority": 6,
    },
    {
        "id": "key_7",
        "name": "مفتاح سرعة إنجاز الاحتياطي (7)",
        "hint": "...3cebvA",
        "encoded_key": "QVEuQWI4Uk42S2dSakRWXzhsVUpLMHNBYUFGVVhNeFQ5b2JiSzRMV19xVWhPd0czY2VidkE=",
        "project_id": "gen-lang-client-0197022210",
        "tier": "Free tier",
        "priority": 7,
    },
    {
        "id": "key_8",
        "name": "مفتاح سرعة إنجاز الاحتياطي (8)",
        "hint": "...O-dj6w",
        "encoded_key": "QVEuQWI4Uk42S2hST0Q0VFQxYWpjWHFlWnpyRzVRMmc5aUJVRjNGcFNudUkwVkFPLWRqNnc=",
        "project_id": "gen-lang-client-0197022210",
        "tier": "Free tier",
        "priority": 8,
    },
    {
        "id": "key_9",
        "name": "Gemini Flash Key (Doc Analyzer)",
        "hint": "...ojVg",
        "encoded_key": "QVEuQWI4Uk42TGV6MW9TVk03dFRPM1UydHc3b2I0UUNGV2pPU2VzdmNydmJsbjV0Zm9qVmc=",
        "project_id": "gen-lang-client-0197022210",
        "tier": "Free tier",
        "priority": 9,
    },
]


def get_permanent_gemini_keys_records(include_env: bool = True) -> List[Dict[str, Any]]:
    """إرجاع قائمة مفاتيح Gemini الدائمة مفكوكة الترميز + مفاتيح متغيرات البيئة دون تكرار."""
    records: List[Dict[str, Any]] = []
    seen_keys = set()

    if include_env:
        env_primary = _env_str("GEMINI_API_KEY", _env_str("GOOGLE_API_KEY", ""))
        if env_primary and env_primary not in seen_keys:
            seen_keys.add(env_primary)
            records.append(
                {
                    "id": "env_key",
                    "name": "مفتاح بيئة النظام التلقائي",
                    "hint": f"...{env_primary[-6:]}",
                    "key": env_primary,
                    "encoded_key": base64.b64encode(env_primary.encode("utf-8")).decode("utf-8"),
                    "project_id": "System Environment",
                    "tier": "Environment",
                    "active": True,
                    "priority": 0,
                }
            )

        env_csv = _env_str("GEMINI_API_KEYS", "")
        for idx, raw_k in enumerate(env_csv.replace(";", ",").split(","), start=1):
            k_clean = raw_k.strip()
            if k_clean and k_clean not in seen_keys:
                seen_keys.add(k_clean)
                records.append(
                    {
                        "id": f"env_list_{idx}",
                        "name": f"Gemini Env Key {idx}",
                        "hint": f"...{k_clean[-4:]}",
                        "key": k_clean,
                        "encoded_key": base64.b64encode(k_clean.encode("utf-8")).decode("utf-8"),
                        "project_id": "System Environment",
                        "tier": "Environment",
                        "active": True,
                        "priority": idx,
                    }
                )

    for spec in PERMANENT_GEMINI_KEYS_SPEC:
        decoded = _decode_b64_secret(spec["encoded_key"])
        if decoded and decoded not in seen_keys:
            seen_keys.add(decoded)
            records.append(
                {
                    "id": spec["id"],
                    "name": spec["name"],
                    "hint": spec["hint"],
                    "key": decoded,
                    "encoded_key": spec["encoded_key"],
                    "project_id": spec.get("project_id", "gen-lang-client-0197022210"),
                    "tier": spec.get("tier", "Free tier"),
                    "active": True,
                    "priority": spec["priority"],
                }
            )
    return records


def get_all_gemini_keys() -> List[str]:
    return [item["key"] for item in get_permanent_gemini_keys_records(include_env=True) if item.get("key")]


def get_gemini_api_key() -> str:
    keys = get_all_gemini_keys()
    return keys[0] if keys else ""


GEMINI_API_KEY = get_gemini_api_key()
if GEMINI_API_KEY and not os.environ.get("GEMINI_API_KEY", "").strip():
    os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY


def get_groq_api_key() -> str:
    key = _env_str("GROQ_API_KEY", "")
    if key:
        return key
    groq_file = os.path.join(BASE_DIR, "ai_engine", ".groq_key")
    if os.path.exists(groq_file):
        try:
            with open(groq_file, "r", encoding="utf-8") as f:
                val = f.read().strip()
            if val:
                return val
        except Exception:
            pass
    return ""


GROQ_API_KEY = get_groq_api_key()
if GROQ_API_KEY:
    os.environ.setdefault("GROQ_API_KEY", GROQ_API_KEY)

OLLAMA_URL = _env_str("OLLAMA_URL", "")
MODEL_TEXT = _env_str("AI_MODEL_TEXT", "allam-2-7b")
MODEL_LOGIC = _env_str("AI_MODEL_LOGIC", "qwen/qwen3.8-27b")
MODEL_CODE = _env_str("AI_MODEL_CODE", "qwen/qwen3.8-27b")
MODEL_FAST = _env_str("AI_MODEL_FAST", "allam-2-7b")
FALLBACK_MODELS = [
    "allam-2-7b",
    "qwen/qwen3.8-27b",
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
]
EMBED_PROVIDER = _env_str("EMBED_PROVIDER", "local")
JINA_API_KEY = _env_str("JINA_API_KEY", "")
AI_TELEGRAM_ENABLED = _env_bool("AI_TELEGRAM_ENABLED", True)
AI_VOICE_ENABLED = _env_bool("AI_VOICE_ENABLED", True)
AI_API_SECRET = _env_str("AI_API_SECRET", "")
AI_RATE_PER_MIN = _env_int("AI_RATE_PER_MIN", 30, minimum=1)
AI_RATE_PER_DAY = _env_int("AI_RATE_PER_DAY", 1000, minimum=1)
AI_TELEGRAM_MIN_LEN = _env_int("AI_TELEGRAM_MIN_LEN", 5, minimum=1)
AI_TELEGRAM_MAX_LEN = _env_int("AI_TELEGRAM_MAX_LEN", 800, minimum=10)
AI_VOICE_MIN_LEN = _env_int("AI_VOICE_MIN_LEN", 3, minimum=1)
AI_VOICE_MAX_LEN = _env_int("AI_VOICE_MAX_LEN", 400, minimum=10)


# ==============================================================================
# 6. مزامنة GitHub وخطاف النشر Render (GitHub Sync & Render Deploy)
# ==============================================================================
GITHUB_REPO_OWNER = _env_str("GITHUB_REPO_OWNER", "anwer1230")
GITHUB_REPO_NAME = _env_str("GITHUB_REPO_NAME", "Telegram-abu-Malk-education")
GITHUB_REPO = _env_str("GITHUB_REPO", f"{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}")
GITHUB_BRANCH = _env_str("GITHUB_BRANCH", "main")
GITHUB_TOKEN = _env_str("GITHUB_TOKEN", "")

DEFAULT_RENDER_DEPLOY_HOOK = "https://api.render.com/deploy/srv-davr5su7bikc73f5978g?key=hZAEDlsJijM"
RENDER_DEPLOY_HOOK_URL = _env_str(
    "RENDER_DEPLOY_HOOK_URL",
    _env_str("RENDER_DEPLOY_HOOK", DEFAULT_RENDER_DEPLOY_HOOK),
)
RENDER_DEPLOY_HOOK = _env_str("RENDER_DEPLOY_HOOK", RENDER_DEPLOY_HOOK_URL)


# ==============================================================================
# 7. مفاتيح إشعارات الويب (Web Push / VAPID Keys)
# ==============================================================================
DEFAULT_VAPID_PUBLIC_KEY = "BIkbfhrnC0MgiZk3KJ8fPTUX300SviFxsJguvQjx6q-TNMxK23yhqhyr5Q5vqad8-k3aD1J7NPWg3GbKHuJdpOc"
DEFAULT_VAPID_PRIVATE_B64 = (
    "LS0tLS1CRUdJTiBFQyBQUklWQVRFIEtFWS0tLS0tCk1IY0NBUUVFSURmeGQ0SUZkSHNrQlFNVjd0RD"
    "VodXVZZlIyOXhtU1ZOMzk5clhhNXYrTTFvQW9HQ0NxR1NNNDkKQXdFSG9VUURRZ0FFaVJ0K0d1Y0xR"
    "eUNKbVRjb254ODlOUmZmVFJLK0lYR3dtQzY5Q1BIcXI1TTB6RXJiZktHcQpIS3ZsRG0rcHAzejZUZG"
    "9QVW5zMDlhRGNac29lNGwyazV3PT0KLS0tLS1FTkQgRUMgUFJJVkFURSBLRVktLS0tLQo"
)

VAPID_PUBLIC_KEY = _env_str("VAPID_PUBLIC_KEY", DEFAULT_VAPID_PUBLIC_KEY)
VAPID_PRIVATE_B64 = _env_str("VAPID_PRIVATE_B64", DEFAULT_VAPID_PRIVATE_B64)
try:
    _vapid_padded = VAPID_PRIVATE_B64 + ("=" * ((4 - len(VAPID_PRIVATE_B64) % 4) % 4))
    VAPID_PRIVATE_PEM = base64.b64decode(_vapid_padded).decode("utf-8")
except Exception:
    VAPID_PRIVATE_PEM = ""
VAPID_CLAIMS = {"sub": _env_str("VAPID_CLAIMS_SUB", "mailto:admin@abumalik.app")}


# ==============================================================================
# 8. معاملات الأتمتة والتحكم الآلي (Automation Rate Limits & Intervals)
# ==============================================================================
SMART_SALAM_WAIT_SECONDS = _env_int("SMART_SALAM_WAIT_SECONDS", 60, minimum=1)
BATCH_SEND_INTERVAL_SECONDS = _env_int("BATCH_SEND_INTERVAL_SECONDS", 5, minimum=1)
JOIN_MIN_DELAY_SECONDS = _env_float("JOIN_MIN_DELAY_SECONDS", 3.0, minimum=0.5)
JOIN_MAX_DELAY_SECONDS = _env_float("JOIN_MAX_DELAY_SECONDS", 10.0, minimum=1.0)
JOIN_MAX_PER_MINUTE = _env_int("JOIN_MAX_PER_MINUTE", 15, minimum=1)
JOIN_MAX_PER_HOUR = _env_int("JOIN_MAX_PER_HOUR", 150, minimum=1)


# ==============================================================================
# 9. ملخص آمن للحالة التشخيصية (بدون كشف الأسرار الخام)
# ==============================================================================
def get_config_summary() -> Dict[str, Any]:
    """إرجاع ملخص موحد وآمن لجميع إعدادات المشروع وقواعد البيانات دون كشف الأسرار الحساسة."""
    gemini_records = get_permanent_gemini_keys_records(include_env=True)
    return {
        "app_name": APP_NAME,
        "is_render": IS_RENDER,
        "port": resolve_app_port(),
        "telegram": {
            "api_id": TELEGRAM_API_ID,
            "api_hash_configured": bool(TELEGRAM_API_HASH),
        },
        "databases": {
            "firebase_project_id": FIREBASE_PROJECT_ID,
            "firestore_database_id": FIRESTORE_DATABASE_ID,
            "firestore_collections": list(FIRESTORE_COLLECTIONS.values()),
            "postgres_configured": bool(get_database_url()),
            "db_connect_timeout": DB_CONNECT_TIMEOUT,
            "db_retries": DB_RETRIES,
            "rag_db_path": RAG_DB_PATH,
        },
        "ai": {
            "gemini_keys_count": len(gemini_records),
            "gemini_primary_hint": gemini_records[0]["hint"] if gemini_records else "",
            "groq_configured": bool(get_groq_api_key()),
            "model_text": MODEL_TEXT,
            "model_logic": MODEL_LOGIC,
        },
        "github": {
            "repo": GITHUB_REPO,
            "branch": GITHUB_BRANCH,
            "token_configured": bool(_env_str("GITHUB_TOKEN", GITHUB_TOKEN)),
        },
        "render": {
            "deploy_hook_configured": bool(RENDER_DEPLOY_HOOK_URL),
        },
        "web_push": {
            "vapid_public_key": VAPID_PUBLIC_KEY,
            "vapid_private_configured": bool(VAPID_PRIVATE_PEM),
        },
        "tunables": {
            "smart_salam_wait_seconds": SMART_SALAM_WAIT_SECONDS,
            "batch_send_interval_seconds": BATCH_SEND_INTERVAL_SECONDS,
            "join_min_delay_seconds": JOIN_MIN_DELAY_SECONDS,
            "join_max_delay_seconds": JOIN_MAX_DELAY_SECONDS,
            "join_max_per_minute": JOIN_MAX_PER_MINUTE,
            "join_max_per_hour": JOIN_MAX_PER_HOUR,
        },
    }
