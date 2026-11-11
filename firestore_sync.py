# -*- coding: utf-8 -*-
"""
وحدة المزامنة السريعة مع قاعدة البيانات الخارجية Firestore + PostgreSQL + الكاش المحلي
====================================================================================
تدعم حفظ واسترجاع:
1. أرقام الهواتف المحفوظة
2. الروابط المكتشفة والمحفوظة (واتساب وتيليجرام) مع كاش ذاكري فوري ودمج آمن للمصادر
3. تقارير فحص ومستوى أمان المجموعات (Group Safety Reports)
مع الاتصال المباشر عبر Firestore REST API (بدون تأخير عمليات Node الفرعية)
والمزامنة الخلفية غير الحاجزة (Non-blocking background sync).
"""

import hashlib
import json
import logging
import os
import re
import subprocess
import threading
import time
from concurrent.futures import ThreadPoolExecutor

try:
    import requests
except Exception:
    requests = None

try:
    from ai_engine.telegram_bridge import generate_reply
except Exception:
    generate_reply = None

logger = logging.getLogger('firestore_sync')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
BRIDGE_SCRIPT = os.path.join(BASE_DIR, 'firestore_bridge.js')
FIREBASE_CONFIG_FILE = os.path.join(BASE_DIR, 'firebase-applet-config.json')
NODE_FIREBASE_INSTALLED = os.path.isdir(os.path.join(BASE_DIR, 'node_modules', 'firebase'))

LOCAL_SAFETY_CACHE_FILE = os.path.join(DATA_DIR, 'group_safety_cache.json')
LOCAL_LINKS_CACHE_FILE = os.path.join(DATA_DIR, 'saved_links.json')
LOCAL_PHONES_CACHE_FILE = os.path.join(DATA_DIR, 'saved_phones.json')

_SAFETY_CACHE_LOCK = threading.Lock()
_LINKS_CACHE_LOCK = threading.Lock()
_PHONES_CACHE_LOCK = threading.Lock()
_LINKS_MEM_LOCK = threading.Lock()

# مجمع خيوط للمزامنة الخلفية غير الحاجزة
_SYNC_EXECUTOR = ThreadPoolExecutor(max_workers=4, thread_name_prefix="FirestoreSyncWorker")

_FIREBASE_CFG_CACHE = None

_LINKS_MEM_CACHE = {
    "links": None,
    "ts": 0.0,
    "ttl": 25.0,
}

_LINKS_STATUS = {
    "firestore_live": False,
    "firestore_error": None,
    "last_probe_ts": 0.0,
    "last_sync_time": None,
    "cloud_count": 0,
    "pg_count": 0,
    "local_count": 0,
}

_SYNC_STATS = {
    "total_synced_reports": 0,
    "total_synced_links": 0,
    "last_sync_time": None,
    "last_error": None,
    "is_online": True,
}


def _load_json_file(file_path, default_val):
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.debug(f"خطأ في قراءة الكاش {file_path}: {e}")
    return default_val


def _save_json_file(file_path, data):
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"خطأ في حفظ الكاش {file_path}: {e}")
        return False


# ==========================================
# 🌐 Firestore REST API المباشر والسريع
# ==========================================
def _get_firebase_config():
    global _FIREBASE_CFG_CACHE
    if _FIREBASE_CFG_CACHE is None:
        _FIREBASE_CFG_CACHE = _load_json_file(FIREBASE_CONFIG_FILE, {}) or {}
    return _FIREBASE_CFG_CACHE


def _get_firestore_base_url():
    cfg = _get_firebase_config()
    project_id = cfg.get("projectId") or ""
    db_id = cfg.get("firestoreDatabaseId") or "(default)"
    if not project_id:
        return None, None
    url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/{db_id}/documents"
    return url, cfg.get("apiKey") or ""


def _fs_val_to_py(val):
    if not isinstance(val, dict):
        return val
    if "stringValue" in val:
        return val["stringValue"]
    if "integerValue" in val:
        try:
            return int(val["integerValue"])
        except Exception:
            return val["integerValue"]
    if "doubleValue" in val:
        try:
            return float(val["doubleValue"])
        except Exception:
            return val["doubleValue"]
    if "booleanValue" in val:
        return bool(val["booleanValue"])
    if "nullValue" in val:
        return None
    if "timestampValue" in val:
        return val["timestampValue"]
    if "arrayValue" in val:
        vals = val["arrayValue"].get("values", [])
        return [_fs_val_to_py(x) for x in vals]
    if "mapValue" in val:
        fields = val["mapValue"].get("fields", {})
        return {k: _fs_val_to_py(v) for k, v in fields.items()}
    return None


def _py_val_to_fs(val):
    if val is None:
        return {"nullValue": None}
    if isinstance(val, bool):
        return {"booleanValue": val}
    if isinstance(val, int):
        return {"integerValue": str(val)}
    if isinstance(val, float):
        return {"doubleValue": val}
    if isinstance(val, list):
        return {"arrayValue": {"values": [_py_val_to_fs(x) for x in val]}}
    if isinstance(val, dict):
        return {"mapValue": {"fields": {str(k): _py_val_to_fs(v) for k, v in val.items()}}}
    return {"stringValue": str(val)}


def _doc_to_dict(doc_obj):
    if not isinstance(doc_obj, dict):
        return None
    name = doc_obj.get("name", "")
    doc_id = name.rsplit("/", 1)[-1] if "/" in name else ""
    fields = doc_obj.get("fields", {})
    out = {k: _fs_val_to_py(v) for k, v in fields.items()}
    if doc_id and not out.get("id"):
        out["id"] = doc_id
    return out


def _firestore_rest_list(collection_name, timeout=3.0):
    """جلب كافة وثائق مجموعة من Firestore REST API مع التصفح السريع."""
    if not requests:
        return None, "requests module unavailable"
    base_url, api_key = _get_firestore_base_url()
    if not base_url:
        return None, "missing firebase projectId"

    docs = []
    page_token = None
    try:
        while True:
            params = {"pageSize": 300}
            if api_key:
                params["key"] = api_key
            if page_token:
                params["pageToken"] = page_token
            resp = requests.get(f"{base_url}/{collection_name}", params=params, timeout=timeout)
            if resp.status_code != 200:
                err_msg = f"HTTP {resp.status_code}"
                try:
                    err_json = resp.json().get("error", {})
                    status = err_json.get("status") or resp.status_code
                    msg = err_json.get("message") or resp.text[:160]
                    err_msg = f"{status} ({resp.status_code}): {msg}"
                except Exception:
                    pass
                return None, err_msg
            payload = resp.json() or {}
            for d in payload.get("documents", []):
                parsed = _doc_to_dict(d)
                if parsed is not None:
                    docs.append(parsed)
            page_token = payload.get("nextPageToken")
            if not page_token or len(docs) >= 3000:
                break
        return docs, None
    except Exception as exc:
        return None, str(exc)


def _firestore_rest_get(collection_name, doc_id, timeout=2.5):
    if not requests or not doc_id:
        return None, "unavailable"
    base_url, api_key = _get_firestore_base_url()
    if not base_url:
        return None, "missing firebase projectId"
    try:
        params = {"key": api_key} if api_key else {}
        resp = requests.get(f"{base_url}/{collection_name}/{doc_id}", params=params, timeout=timeout)
        if resp.status_code == 200:
            return _doc_to_dict(resp.json()), None
        if resp.status_code == 404:
            return None, None
        return None, f"HTTP {resp.status_code}"
    except Exception as exc:
        return None, str(exc)


def _firestore_rest_patch(collection_name, doc_id, data_dict, timeout=3.0):
    if not requests or not doc_id or not isinstance(data_dict, dict):
        return False, "invalid args"
    base_url, api_key = _get_firestore_base_url()
    if not base_url:
        return False, "missing firebase projectId"
    try:
        params = {"key": api_key} if api_key else {}
        body = {"fields": {str(k): _py_val_to_fs(v) for k, v in data_dict.items()}}
        resp = requests.patch(f"{base_url}/{collection_name}/{doc_id}", params=params, json=body, timeout=timeout)
        if resp.status_code in (200, 201):
            return True, None
        err_msg = f"HTTP {resp.status_code}"
        try:
            err_json = resp.json().get("error", {})
            err_msg = f"{err_json.get('status', resp.status_code)}: {err_json.get('message', '')[:120]}"
        except Exception:
            pass
        return False, err_msg
    except Exception as exc:
        return False, str(exc)


def _firestore_rest_delete(collection_name, doc_id, timeout=3.0):
    if not requests or not doc_id:
        return False, "invalid args"
    base_url, api_key = _get_firestore_base_url()
    if not base_url:
        return False, "missing firebase projectId"
    try:
        params = {"key": api_key} if api_key else {}
        resp = requests.delete(f"{base_url}/{collection_name}/{doc_id}", params=params, timeout=timeout)
        if resp.status_code in (200, 204, 404):
            return True, None
        return False, f"HTTP {resp.status_code}"
    except Exception as exc:
        return False, str(exc)


def _run_node_bridge(args, timeout=8):
    if not NODE_FIREBASE_INSTALLED or not os.path.exists(BRIDGE_SCRIPT):
        return None
    try:
        proc = subprocess.run(
            ['node', BRIDGE_SCRIPT] + list(args),
            capture_output=True, text=True, timeout=timeout, cwd=BASE_DIR
        )
        if proc.returncode == 0 and proc.stdout.strip():
            return json.loads(proc.stdout.strip())
    except Exception as e:
        logger.debug(f"Node bridge fallback skipped/failed: {e}")
    return None


# ==========================================
# 📱 أرقام الهواتف (Phone Numbers)
# ==========================================
DEFAULT_PHONE_NUMBERS = [
    {"phone_number": "+201120945094", "is_default": True, "label": "Lamis", "account_name": "Lamis"},
    {"phone_number": "+573244867204", "is_default": True, "label": "الحساب الأول", "account_name": "الحساب الأول"},
    {"phone_number": "+201221349790", "is_default": True, "label": "الحساب الثاني", "account_name": "الحساب الثاني"},
    {"phone_number": "+201148863243", "is_default": True, "label": "الحساب الثالث", "account_name": "الحساب الثالث"},
    {"phone_number": "+213797500921", "is_default": True, "label": "الحساب الرابع", "account_name": "الحساب الرابع"},
    {"phone_number": "+201274386864", "is_default": True, "label": "الحساب الخامس", "account_name": "الحساب الخامس"},
    {"phone_number": "+966539709737", "is_default": True, "label": "الحساب السادس", "account_name": "الحساب السادس"}
]


def _clean_phone_digits(p):
    return re.sub(r'[^0-9]', '', str(p or ''))


def _init_default_phones_from_cache():
    """تحديث الأسماء الافتراضية بالأسماء الحقيقية المحفوظة في الكاش المحلي فور بدء التشغيل"""
    try:
        cached = _load_json_file(LOCAL_PHONES_CACHE_FILE, [])
        for c in cached:
            c_digits = _clean_phone_digits(c.get('phone_number'))
            c_name = c.get('account_name') or c.get('label')
            if c_name and not c_name.startswith('الحساب ') and c_name not in ['رقم أساسي', 'رقم محفوظ', 'حساب تليجرام']:
                for d in DEFAULT_PHONE_NUMBERS:
                    if _clean_phone_digits(d.get('phone_number')) == c_digits:
                        d['label'] = c_name
                        d['account_name'] = c_name
    except Exception as e:
        logger.debug(f"Init defaults error: {e}")


_init_default_phones_from_cache()


def _sanitize_phone_list(phones):
    """تنقية وتحديث أسماء الحسابات للأرقام وتثبيت الأسماء الحقيقية ومنع ظهور كلمة 'أساسي'"""
    if not isinstance(phones, list):
        return [dict(x) for x in DEFAULT_PHONE_NUMBERS]

    result = []
    defaults_map = {_clean_phone_digits(d['phone_number']): d for d in DEFAULT_PHONE_NUMBERS}

    for item in phones:
        if not isinstance(item, dict):
            continue
        entry = dict(item)
        raw_phone = entry.get('phone_number', '')
        digits = _clean_phone_digits(raw_phone)
        cur_label = (entry.get('label') or entry.get('account_name') or '').strip()

        if digits == '201120945094' and (not cur_label or cur_label in ['رقم أساسي', 'رقم محفوظ', 'حساب تليجرام']):
            entry['label'] = 'Lamis'
            entry['account_name'] = 'Lamis'
        elif cur_label and not cur_label.startswith('الحساب ') and cur_label not in ['رقم أساسي', 'رقم محفوظ', 'حساب تليجرام']:
            entry['label'] = cur_label
            entry['account_name'] = cur_label
        elif digits in defaults_map:
            def_lbl = defaults_map[digits].get('label', f"حساب {raw_phone}")
            entry['label'] = def_lbl
            entry['account_name'] = defaults_map[digits].get('account_name', def_lbl)
        else:
            entry['label'] = entry.get('account_name') or f"حساب {raw_phone}"
            entry['account_name'] = entry['label']

        result.append(entry)

    existing_digits = {_clean_phone_digits(r.get('phone_number')) for r in result}
    for def_entry in DEFAULT_PHONE_NUMBERS:
        def_digits = _clean_phone_digits(def_entry['phone_number'])
        if def_digits not in existing_digits:
            result.append(dict(def_entry))

    return result


def get_saved_phone_numbers():
    """استرجاع أرقام الهواتف المحفوظة مع أسماء الحسابات الثابتة والـ Fallback للكاش المحلي"""
    with _PHONES_CACHE_LOCK:
        cached = _load_json_file(LOCAL_PHONES_CACHE_FILE, [])

    phones = None
    docs, _ = _firestore_rest_list('saved_phone_numbers', timeout=2.5)
    if docs:
        phones = docs
    elif NODE_FIREBASE_INSTALLED:
        res = _run_node_bridge(['get_phones'], timeout=6)
        if res and res.get('success') and res.get('phones'):
            phones = res.get('phones')

    if not phones:
        phones = cached if cached else [dict(x) for x in DEFAULT_PHONE_NUMBERS]

    sanitized = _sanitize_phone_list(phones)

    with _PHONES_CACHE_LOCK:
        _save_json_file(LOCAL_PHONES_CACHE_FILE, sanitized)

    return sanitized


def update_phone_account_name(phone, account_name):
    """تحديث اسم الحساب الفعلي للرقم وتثبيته بشكل دائم في الكاش المحلي و Firestore"""
    if not phone or not account_name:
        return None
    clean_phone = str(phone).strip()
    clean_name = str(account_name).strip()
    if not clean_name:
        return None

    target_digits = _clean_phone_digits(clean_phone)
    updated_entry = None

    with _PHONES_CACHE_LOCK:
        phones = _load_json_file(LOCAL_PHONES_CACHE_FILE, [dict(x) for x in DEFAULT_PHONE_NUMBERS])
        phones = _sanitize_phone_list(phones)
        found = False
        for p in phones:
            if _clean_phone_digits(p.get('phone_number')) == target_digits:
                p['label'] = clean_name
                p['account_name'] = clean_name
                p['updated_at'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
                updated_entry = p
                found = True
                break
        if not found:
            updated_entry = {
                "phone_number": clean_phone,
                "is_default": False,
                "label": clean_name,
                "account_name": clean_name,
                "added_at": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            }
            phones.append(updated_entry)

        _save_json_file(LOCAL_PHONES_CACHE_FILE, phones)

        for d in DEFAULT_PHONE_NUMBERS:
            if _clean_phone_digits(d.get('phone_number')) == target_digits:
                d['label'] = clean_name
                d['account_name'] = clean_name

        try:
            acc_file = os.path.join(DATA_DIR, 'accounts.json')
            if os.path.exists(acc_file):
                with open(acc_file, 'r', encoding='utf-8') as af:
                    accs = json.load(af)
                changed = False
                for uid, udata in accs.items():
                    if isinstance(udata, dict) and _clean_phone_digits(udata.get('phone')) == target_digits:
                        udata['name'] = clean_name
                        changed = True
                if changed:
                    with open(acc_file, 'w', encoding='utf-8') as af:
                        json.dump(accs, af, ensure_ascii=False, indent=2)
        except Exception as _ae:
            logger.debug(f"accounts.json sync error: {_ae}")

    def _bg_update():
        if target_digits and updated_entry:
            ok, err = _firestore_rest_patch('saved_phone_numbers', target_digits, updated_entry, timeout=3.0)
            if not ok and NODE_FIREBASE_INSTALLED:
                _run_node_bridge(['update_phone_name', clean_phone, clean_name], timeout=8)

    _SYNC_EXECUTOR.submit(_bg_update)
    return updated_entry


def save_phone_number(phone, label='حساب محفوظ'):
    """حفظ رقم هاتف جديد في الكاش المحلي وخلفياً في Firestore"""
    if not phone:
        return None
    clean_phone = str(phone).strip()
    clean_label = str(label or 'حساب محفوظ').strip()
    if 'أساسي' in clean_label:
        clean_label = 'حساب معتمد'

    new_entry = {
        "phone_number": clean_phone,
        "is_default": False,
        "label": clean_label,
        "account_name": clean_label,
        "added_at": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    }

    target_digits = _clean_phone_digits(clean_phone)
    with _PHONES_CACHE_LOCK:
        phones = _load_json_file(LOCAL_PHONES_CACHE_FILE, [dict(x) for x in DEFAULT_PHONE_NUMBERS])
        phones = _sanitize_phone_list(phones)
        if not any(_clean_phone_digits(p.get('phone_number')) == target_digits for p in phones):
            phones.append(new_entry)
            _save_json_file(LOCAL_PHONES_CACHE_FILE, phones)

    def _bg_save():
        if target_digits:
            ok, _ = _firestore_rest_patch('saved_phone_numbers', target_digits, new_entry, timeout=3.0)
            if not ok and NODE_FIREBASE_INSTALLED:
                _run_node_bridge(['add_phone', clean_phone, clean_label], timeout=8)

    _SYNC_EXECUTOR.submit(_bg_save)
    return new_entry


# ==========================================
# 🔗 الروابط المحفوظة (Saved Links)
# ==========================================
def _is_saved_link_record(item):
    """التحقق من أن السجل رابط محفوظ فعلي وليس تقرير فحص مجموعة مدمج بالخطأ"""
    if not isinstance(item, dict):
        return False
    url = str(item.get("url") or "").strip()
    if not url:
        return False
    item_id = str(item.get("id") or "").strip()
    if item_id.startswith("report_"):
        return False
    if item.get("category") == "safety_report" or item.get("type") == "safety_report":
        return False
    return True


def _normalize_link_record(item):
    url = str(item.get("url") or "").strip()
    link_id = str(item.get("id") or "").strip()
    if not link_id:
        link_id = hashlib.sha1(url.encode("utf-8")).hexdigest()[:8]
    title = str(item.get("title") or "").strip() or url
    category = str(item.get("category") or "").strip() or "عام"
    date_saved = str(item.get("date_saved") or "").strip()
    source = str(item.get("source") or "").strip() or "يدوي"
    notes = str(item.get("notes") or "")
    return {
        "id": link_id,
        "url": url,
        "title": title,
        "category": category,
        "date_saved": date_saved,
        "source": source,
        "notes": notes,
    }


def _read_local_links_file():
    raw = _load_json_file(LOCAL_LINKS_CACHE_FILE, {"links": []})
    if isinstance(raw, dict):
        val = raw.get("links", [])
        while isinstance(val, dict):
            val = val.get("links", [])
        items = val if isinstance(val, list) else []
    elif isinstance(raw, list):
        items = raw
    else:
        items = []
    return [_normalize_link_record(x) for x in items if _is_saved_link_record(x)]


def _merge_link_lists(*lists):
    """دمج عدة قوائم روابط دون تكرار وبأفضل بيانات متوفرة، مع استبعاد تقارير الأمان."""
    by_url = {}
    for lst in lists:
        if not lst:
            continue
        for item in lst:
            if not _is_saved_link_record(item):
                continue
            rec = _normalize_link_record(item)
            key = rec["url"].lower()
            existing = by_url.get(key)
            if not existing:
                by_url[key] = rec
            else:
                # نحتفظ بالنسخة الأحدث أو الأكثر تفصيلاً
                if (not existing["notes"] and rec["notes"]) or (existing["title"] == existing["url"] and rec["title"] != rec["url"]):
                    merged_rec = dict(existing)
                    if rec["title"] and rec["title"] != rec["url"]:
                        merged_rec["title"] = rec["title"]
                    if rec["notes"]:
                        merged_rec["notes"] = rec["notes"]
                    if rec["category"] and rec["category"] != "عام":
                        merged_rec["category"] = rec["category"]
                    if rec["date_saved"] > merged_rec["date_saved"]:
                        merged_rec["date_saved"] = rec["date_saved"]
                    by_url[key] = merged_rec
    merged = list(by_url.values())
    merged.sort(key=lambda x: x.get("date_saved") or "", reverse=True)
    return merged


def invalidate_links_cache():
    with _LINKS_MEM_LOCK:
        _LINKS_MEM_CACHE["links"] = None
        _LINKS_MEM_CACHE["ts"] = 0.0


def _try_get_pg_links():
    try:
        import db as _pg_db
        if _pg_db.is_enabled():
            rows = _pg_db.get_saved_links()
            if isinstance(rows, list):
                return [_normalize_link_record(x) for x in rows if _is_saved_link_record(x)]
    except Exception as exc:
        logger.debug(f"PG saved_links read notice: {exc}")
    return None


def _bg_sync_links_to_pg(links_list):
    if not links_list:
        return
    def _task():
        try:
            import db as _pg_db
            if _pg_db.is_enabled():
                _pg_db.upsert_saved_links_batch(links_list)
        except Exception as exc:
            logger.debug(f"PG saved_links background sync notice: {exc}")
    _SYNC_EXECUTOR.submit(_task)


def get_firestore_links(force_refresh=True):
    """
    جلب الروابط من Firestore REST API مباشرة.
    تُرجع قائمة (list) عند نجاح الاتصال الفعلي بـ Firestore، أو None عند تعذر الاتصال/الصلاحيات.
    """
    now = time.time()
    # إذا فحصنا منذ أقل من 20 ثانية ولم يكن الفحص إجبارياً، نعيد احترام النتيجة لتسريع الأداء
    if not force_refresh and (now - _LINKS_STATUS["last_probe_ts"]) < 20.0 and not _LINKS_STATUS["firestore_live"]:
        return None

    docs, err = _firestore_rest_list('saved_links', timeout=3.0)
    _LINKS_STATUS["last_probe_ts"] = time.time()

    if err is None and isinstance(docs, list):
        clean_cloud = [_normalize_link_record(d) for d in docs if _is_saved_link_record(d)]
        _LINKS_STATUS["firestore_live"] = True
        _LINKS_STATUS["firestore_error"] = None
        _LINKS_STATUS["cloud_count"] = len(clean_cloud)
        _LINKS_STATUS["last_sync_time"] = time.strftime('%Y-%m-%d %H:%M:%S')
        _SYNC_STATS["is_online"] = True
        _SYNC_STATS["last_error"] = None
        return clean_cloud

    # محاولة ثانية عبر Node bridge فقط إذا كانت مكتبة firebase مثبتة فعلياً
    if NODE_FIREBASE_INSTALLED:
        res = _run_node_bridge(['get_links'], timeout=6)
        if res and res.get('success'):
            clean_cloud = [_normalize_link_record(d) for d in res.get('links', []) if _is_saved_link_record(d)]
            _LINKS_STATUS["firestore_live"] = True
            _LINKS_STATUS["firestore_error"] = None
            _LINKS_STATUS["cloud_count"] = len(clean_cloud)
            _LINKS_STATUS["last_sync_time"] = time.strftime('%Y-%m-%d %H:%M:%S')
            return clean_cloud

    _LINKS_STATUS["firestore_live"] = False
    _LINKS_STATUS["firestore_error"] = err or "Firestore unavailable"
    _SYNC_STATS["last_error"] = _LINKS_STATUS["firestore_error"]
    logger.debug(f"Firestore links probe notice: {_LINKS_STATUS['firestore_error']}")
    return None


def get_merged_saved_links(force_refresh=False):
    """
    استرجاع كافة الروابط المحفوظة بسرعة فائقة مع الدمج الآمن عبر:
    - الذاكرة المؤقتة الفورية (<1ms)
    - قاعدة بيانات PostgreSQL الدائمة
    - الملف المحلي data/saved_links.json
    - سحابة Firebase Firestore REST API (دون حذف الروابط المحلية عند فشل/نقص السحابة)
    """
    now = time.time()
    if not force_refresh:
        with _LINKS_MEM_LOCK:
            cached_mem = _LINKS_MEM_CACHE["links"]
            if cached_mem is not None and (now - _LINKS_MEM_CACHE["ts"]) < _LINKS_MEM_CACHE["ttl"]:
                return [dict(x) for x in cached_mem]

    # 1. القراءة السريعة من الملف المحلي و PostgreSQL
    with _LINKS_CACHE_LOCK:
        local_links = _read_local_links_file()
    _LINKS_STATUS["local_count"] = len(local_links)

    pg_links = _try_get_pg_links()
    _LINKS_STATUS["pg_count"] = len(pg_links) if pg_links is not None else 0

    # 2. استعلام السحابة (فقط عند التحديث الإجباري أو أول تحميل أو إذا انقضت مهلة الفحص)
    cloud_links = get_firestore_links(force_refresh=force_refresh)

    # 3. الدمج الآمن بدون فقدان أي رابط
    merged = _merge_link_lists(cloud_links or [], pg_links or [], local_links or [])

    # 4. تحديث الكاش المحلي و PG في الخلفية إذا ظهر دمج جديد
    if merged:
        if len(merged) != len(local_links):
            with _LINKS_CACHE_LOCK:
                _save_json_file(LOCAL_LINKS_CACHE_FILE, {"links": merged})
            _LINKS_STATUS["local_count"] = len(merged)
        if pg_links is None or len(pg_links) < len(merged):
            _bg_sync_links_to_pg(merged)

    with _LINKS_MEM_LOCK:
        _LINKS_MEM_CACHE["links"] = [dict(x) for x in merged]
        _LINKS_MEM_CACHE["ts"] = time.time()

    return merged


def get_links_sync_status():
    """إرجاع الحالة الحقيقية الفعلية لمصادر تخزين الروابط."""
    return {
        "firestore_live": bool(_LINKS_STATUS["firestore_live"]),
        "firestore_error": _LINKS_STATUS["firestore_error"],
        "cloud_count": int(_LINKS_STATUS["cloud_count"]),
        "pg_count": int(_LINKS_STATUS["pg_count"]),
        "local_count": int(_LINKS_STATUS["local_count"]),
        "last_sync_time": _LINKS_STATUS["last_sync_time"],
    }


def add_firestore_link(link_dict):
    """
    حفظ رابط فورياً في الكاش الذاكري والمحلي وPostgreSQL ومزامنته خلفياً مع Firestore.
    """
    if not _is_saved_link_record(link_dict):
        return None

    rec = _normalize_link_record(link_dict)
    url_lower = rec["url"].lower()

    # 1. تحديث الكاش المحلي والذاكرة فوراً
    with _LINKS_CACHE_LOCK:
        links = _read_local_links_file()
        existing = next((l for l in links if l.get('url', '').lower() == url_lower), None)
        if not existing:
            links.insert(0, rec)
            if len(links) > 3000:
                links = links[:3000]
            _save_json_file(LOCAL_LINKS_CACHE_FILE, {"links": links})

    with _LINKS_MEM_LOCK:
        if _LINKS_MEM_CACHE["links"] is not None:
            if not any(l.get('url', '').lower() == url_lower for l in _LINKS_MEM_CACHE["links"]):
                _LINKS_MEM_CACHE["links"].insert(0, dict(rec))
            _LINKS_MEM_CACHE["ts"] = time.time()

    # 2. حفظ غير حاجز في PG و Firestore REST
    def _bg_add_link():
        try:
            import db as _pg_db
            if _pg_db.is_enabled():
                _pg_db.upsert_saved_link(rec)
        except Exception:
            pass
        ok, err = _firestore_rest_patch('saved_links', rec['id'], rec, timeout=3.5)
        if ok:
            _SYNC_STATS["total_synced_links"] += 1
            _SYNC_STATS["last_sync_time"] = time.strftime('%Y-%m-%d %H:%M:%S')
            _LINKS_STATUS["firestore_live"] = True
            _LINKS_STATUS["firestore_error"] = None
        else:
            if err:
                _SYNC_STATS["last_error"] = err
            if NODE_FIREBASE_INSTALLED:
                _run_node_bridge(['add_link', json.dumps(rec, ensure_ascii=False)], timeout=8)

    _SYNC_EXECUTOR.submit(_bg_add_link)
    return rec


def update_firestore_link(link_dict):
    """تحديث بيانات رابط محفوظ في الكاش المحلي وPostgreSQL وFirestore."""
    if not _is_saved_link_record(link_dict):
        return None
    rec = _normalize_link_record(link_dict)

    with _LINKS_MEM_LOCK:
        if _LINKS_MEM_CACHE["links"] is not None:
            for idx, item in enumerate(_LINKS_MEM_CACHE["links"]):
                if item.get("id") == rec["id"] or item.get("url", "").lower() == rec["url"].lower():
                    _LINKS_MEM_CACHE["links"][idx] = dict(rec)
                    break
            _LINKS_MEM_CACHE["ts"] = time.time()

    def _bg_upd():
        try:
            import db as _pg_db
            if _pg_db.is_enabled():
                _pg_db.upsert_saved_link(rec)
        except Exception:
            pass
        ok, err = _firestore_rest_patch('saved_links', rec['id'], rec, timeout=3.5)
        if ok:
            _LINKS_STATUS["firestore_live"] = True
            _LINKS_STATUS["firestore_error"] = None
        elif err:
            _SYNC_STATS["last_error"] = err

    _SYNC_EXECUTOR.submit(_bg_upd)
    return rec


def delete_firestore_link(link_id):
    """حذف رابط من الكاش المحلي والذاكري وPostgreSQL وFirestore."""
    if not link_id:
        return False
    str_id = str(link_id)

    with _LINKS_CACHE_LOCK:
        links = _read_local_links_file()
        new_links = [l for l in links if str(l.get('id', '')) != str_id]
        _save_json_file(LOCAL_LINKS_CACHE_FILE, {"links": new_links})

    with _LINKS_MEM_LOCK:
        if _LINKS_MEM_CACHE["links"] is not None:
            _LINKS_MEM_CACHE["links"] = [l for l in _LINKS_MEM_CACHE["links"] if str(l.get('id', '')) != str_id]
            _LINKS_MEM_CACHE["ts"] = time.time()

    def _bg_del():
        try:
            import db as _pg_db
            if _pg_db.is_enabled():
                _pg_db.delete_saved_link(str_id)
        except Exception:
            pass
        ok, _ = _firestore_rest_delete('saved_links', str_id, timeout=3.0)
        if not ok and NODE_FIREBASE_INSTALLED:
            _run_node_bridge(['delete_link', str_id], timeout=8)

    _SYNC_EXECUTOR.submit(_bg_del)
    return True


def delete_firestore_links_batch(link_ids):
    """حذف مجموعة روابط دفعة واحدة."""
    if not link_ids:
        return False
    id_set = {str(x) for x in link_ids if x}
    if not id_set:
        return False

    with _LINKS_CACHE_LOCK:
        links = _read_local_links_file()
        new_links = [l for l in links if str(l.get('id', '')) not in id_set]
        _save_json_file(LOCAL_LINKS_CACHE_FILE, {"links": new_links})

    with _LINKS_MEM_LOCK:
        if _LINKS_MEM_CACHE["links"] is not None:
            _LINKS_MEM_CACHE["links"] = [l for l in _LINKS_MEM_CACHE["links"] if str(l.get('id', '')) not in id_set]
            _LINKS_MEM_CACHE["ts"] = time.time()

    def _bg_del_batch():
        try:
            import db as _pg_db
            if _pg_db.is_enabled():
                _pg_db.delete_saved_links_batch(list(id_set))
        except Exception:
            pass
        for lid in id_set:
            _firestore_rest_delete('saved_links', lid, timeout=2.5)

    _SYNC_EXECUTOR.submit(_bg_del_batch)
    return True


# ==========================================
# 🛡️ تقارير فحص وأمان المجموعات (Group Safety Reports)
# ==========================================
def _normalize_group_key(k):
    if not k:
        return ""
    clean = str(k).strip().lower()
    return re.sub(r'^(?:https?://)?(?:t\.me|telegram\.me)/', '', clean).lstrip('@')


def _normalize_report_doc_id(raw):
    if not raw:
        return ""
    s = str(raw).strip().lower()
    s = re.sub(r'^https?://', '', s)
    s = re.sub(r'^(?:t\.me|telegram\.me)/', '', s)
    s = s.lstrip('@')
    s = re.sub(r'[^a-zA-Z0-9_\-]', '_', s)
    return s[:120]


def get_group_safety_report_from_db(group_key, alt_key=None):
    """
    استرجاع تقرير فحص المجموعة من الكاش المحلي أولاً (بسرعة فائقة)
    وإذا لم يتوفر، استرجاعه من Firestore REST وحفظه محلياً.
    """
    if not group_key and not alt_key:
        return None

    keys_to_check = [k for k in [group_key, alt_key] if k]

    with _SAFETY_CACHE_LOCK:
        local_cache = _load_json_file(LOCAL_SAFETY_CACHE_FILE, {})
        for k in keys_to_check:
            clean_k = str(k).strip().lower()
            if clean_k in local_cache:
                return local_cache[clean_k]
            norm_k = _normalize_group_key(clean_k)
            if norm_k in local_cache:
                return local_cache[norm_k]

    for k in keys_to_check:
        doc_id = _normalize_report_doc_id(k)
        if not doc_id:
            continue
        report = None
        doc_data, _ = _firestore_rest_get('saved_links', f'report_{doc_id}', timeout=2.5)
        if doc_data:
            report = doc_data.get('report_data') or doc_data
        else:
            doc_data2, _ = _firestore_rest_get('group_safety_reports', doc_id, timeout=2.5)
            if doc_data2:
                report = doc_data2

        if report:
            with _SAFETY_CACHE_LOCK:
                local_cache = _load_json_file(LOCAL_SAFETY_CACHE_FILE, {})
                local_cache[str(k).strip().lower()] = report
                norm = _normalize_group_key(k)
                if norm:
                    local_cache[norm] = report
                if alt_key:
                    local_cache[str(alt_key).strip().lower()] = report
                _save_json_file(LOCAL_SAFETY_CACHE_FILE, local_cache)
            return report

    return None


def save_group_safety_report_to_db(report_dict):
    """حفظ دائم وثابت لتقرير المجموعة في الكاش المحلي وخلفياً في Firestore."""
    if not report_dict:
        return None

    key = report_dict.get('group_key') or report_dict.get('group_id') or report_dict.get('group_title')
    if not key:
        return None

    with _SAFETY_CACHE_LOCK:
        local_cache = _load_json_file(LOCAL_SAFETY_CACHE_FILE, {})
        str_key = str(key).strip().lower()
        local_cache[str_key] = report_dict
        norm = _normalize_group_key(str_key)
        if norm:
            local_cache[norm] = report_dict
        if report_dict.get('group_id'):
            local_cache[str(report_dict['group_id']).strip().lower()] = report_dict
        if report_dict.get('username'):
            local_cache[str(report_dict['username']).strip().lower()] = report_dict
        _save_json_file(LOCAL_SAFETY_CACHE_FILE, local_cache)

    def _bg_save_report():
        doc_id = _normalize_report_doc_id(key)
        if not doc_id:
            return
        now_iso = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        clean_data = dict(report_dict)
        clean_data['doc_id'] = doc_id
        clean_data['group_key'] = str(key)
        clean_data['updated_at'] = now_iso
        payload = {
            'id': f'report_{doc_id}',
            'url': str(key),
            'title': report_dict.get('group_title') or str(key),
            'category': 'safety_report',
            'type': 'safety_report',
            'date_saved': now_iso,
            'source': 'group_ai_analyzer',
            'report_data': clean_data
        }
        ok, err = _firestore_rest_patch('saved_links', f'report_{doc_id}', payload, timeout=3.0)
        if ok:
            _SYNC_STATS["total_synced_reports"] += 1
            _SYNC_STATS["last_sync_time"] = time.strftime('%Y-%m-%d %H:%M:%S')
        elif err:
            _SYNC_STATS["last_error"] = err

    _SYNC_EXECUTOR.submit(_bg_save_report)
    return report_dict


def get_sync_status():
    """معلومات حالة المزامنة والكاش لخدمة الفحص والمراقبة"""
    with _SAFETY_CACHE_LOCK:
        cached_reports_count = len(_load_json_file(LOCAL_SAFETY_CACHE_FILE, {}))
    with _LINKS_CACHE_LOCK:
        cached_links_count = len(_read_local_links_file())

    return {
        "success": True,
        "online": _SYNC_STATS["is_online"],
        "firestore_live": _LINKS_STATUS["firestore_live"],
        "firestore_error": _LINKS_STATUS["firestore_error"],
        "cached_reports": cached_reports_count,
        "cached_links": cached_links_count,
        "pg_links": _LINKS_STATUS["pg_count"],
        "synced_reports": _SYNC_STATS["total_synced_reports"],
        "synced_links": _SYNC_STATS["total_synced_links"],
        "last_sync_time": _SYNC_STATS["last_sync_time"],
        "last_error": _SYNC_STATS["last_error"]
    }


def save_verification_code_to_firestore(phone, code, raw_text=""):
    """حفظ كود التحقق في Firestore لمزامنته سحابياً ولحظياً عبر الأجهزة"""
    if not code:
        return
    def _bg_save():
        clean_phone = re.sub(r'[^0-9]', '', str(phone or 'latest')) or 'latest'
        payload = {
            "phone": str(phone or 'latest'),
            "code": str(code or '').strip(),
            "raw_text": str(raw_text or '')[:300],
            "updated_at": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        }
        ok, _ = _firestore_rest_patch('telegram_verification_codes', clean_phone, payload, timeout=3.0)
        if not ok and NODE_FIREBASE_INSTALLED:
            _run_node_bridge(['save_verification_code', str(phone or ''), str(code or '').strip(), str(raw_text or '')], timeout=8)

    _SYNC_EXECUTOR.submit(_bg_save)
