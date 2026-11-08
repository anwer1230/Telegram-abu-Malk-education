"""حماية و Rate Limiting — بسيط وفعّال بدون مكتبات ثقيلة"""
import os
import time
from collections import defaultdict, deque
from functools import wraps
from flask import request, jsonify

# ═══ الإعدادات ═══
API_SECRET = os.getenv("AI_API_SECRET", "")           # مفتاح سري اختياري
RATE_PER_MINUTE = int(os.getenv("AI_RATE_PER_MIN", "30"))
RATE_PER_DAY = int(os.getenv("AI_RATE_PER_DAY", "1000"))

# ═══ سجلات في الذاكرة ═══
_minute_bucket: dict = defaultdict(deque)
_day_bucket: dict = defaultdict(deque)
_MAX_QUERY_LEN = 4000


def _client_id() -> str:
    """هوية الطالب — IP أو رمز المستخدم"""
    user = getattr(request, "user_id", None)
    if user:
        return f"user:{user}"
    ip = request.headers.get("X-Forwarded-For", request.remote_addr or "unknown")
    return f"ip:{ip.split(',')[0].strip()}"


def _check_window(bucket: deque, limit: int, window_sec: int) -> bool:
    """فحص نافذة زمنية"""
    now = time.time()
    cutoff = now - window_sec
    while bucket and bucket[0] < cutoff:
        bucket.popleft()
    if len(bucket) >= limit:
        return False
    bucket.append(now)
    return True


def protect(fn):
    """ديكوراتور الحماية الكاملة"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # 1. التحقق من المفتاح السري (إذا مُفعّل)
        if API_SECRET:
            token = request.headers.get("X-AI-Token", "")
            if token != API_SECRET:
                return jsonify({"error": "unauthorized", "code": "AUTH"}), 401

        # 2. Rate limit دقيق
        cid = _client_id()
        if not _check_window(_minute_bucket[cid], RATE_PER_MINUTE, 60):
            return jsonify({
                "error": "تجاوزت الحد المسموح بالدقيقة",
                "code": "RATE_MINUTE",
                "retry_after": 60,
            }), 429

        # 3. Rate limit يومي
        if not _check_window(_day_bucket[cid], RATE_PER_DAY, 86400):
            return jsonify({
                "error": "تجاوزت الحد اليومي",
                "code": "RATE_DAY",
                "retry_after": 3600,
            }), 429

        # 4. التحقق من حجم الطلب
        data = request.get_json(silent=True) or {}
        query = (data.get("query") or "").strip()
        if len(query) > _MAX_QUERY_LEN:
            return jsonify({
                "error": f"النص طويل جدًا (الحد {_MAX_QUERY_LEN})",
                "code": "TOO_LONG",
            }), 413

        return fn(*args, **kwargs)
    return wrapper


def get_stats() -> dict:
    """إحصاءات الاستخدام الحالية"""
    return {
        "active_clients_minute": len(_minute_bucket),
        "active_clients_day": len(_day_bucket),
        "rate_per_minute": RATE_PER_MINUTE,
        "rate_per_day": RATE_PER_DAY,
        "auth_enabled": bool(API_SECRET),
    }
