"""PostgreSQL persistence for the Telegram automation application.

The application keeps a JSON mirror for backwards compatibility, but PostgreSQL
becomes the primary store whenever DATABASE_URL is configured.
"""
from __future__ import annotations

import json
import logging
import os
import time
from contextlib import contextmanager
from typing import Any, Iterator, Optional

logger = logging.getLogger(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
def _env_int(name: str, default: int, minimum: int) -> int:
    try:
        return max(minimum, int(os.environ.get(name, str(default)) or default))
    except (TypeError, ValueError):
        return default


DB_CONNECT_TIMEOUT = _env_int("DB_CONNECT_TIMEOUT", 10, 1)
DB_RETRIES = _env_int("DB_RETRIES", 2, 0)
SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema.sql")


def is_enabled() -> bool:
    """Return whether a PostgreSQL connection has been configured."""
    return bool(DATABASE_URL)


def _driver():
    try:
        import psycopg
        return psycopg
    except ImportError as exc:
        raise RuntimeError("DATABASE_URL is set but psycopg is not installed") from exc


@contextmanager
def _connection() -> Iterator[Any]:
    if not is_enabled():
        raise RuntimeError("DATABASE_URL is not configured")
    psycopg = _driver()
    conn = psycopg.connect(DATABASE_URL, connect_timeout=DB_CONNECT_TIMEOUT)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _run(operation, default=None):
    if not is_enabled():
        return default
    last_error = None
    for attempt in range(DB_RETRIES + 1):
        try:
            with _connection() as conn:
                return operation(conn)
        except Exception as exc:
            last_error = exc
            if attempt < DB_RETRIES:
                time.sleep(0.25 * (attempt + 1))
    logger.error("Database operation failed: %s", last_error)
    return default


def init_db() -> bool:
    """Create the schema idempotently. Returns False when DB is not configured."""
    if not is_enabled():
        return False
    try:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as schema_file:
            statements = [part.strip() for part in schema_file.read().split(";") if part.strip()]
        with _connection() as conn:
            with conn.cursor() as cursor:
                for statement in statements:
                    cursor.execute(statement)
        logger.info("PostgreSQL schema is ready")
        return True
    except Exception as exc:
        logger.error("PostgreSQL schema initialization failed: %s", exc)
        return False


def status() -> dict[str, Any]:
    if not is_enabled():
        return {"configured": False, "connected": False}
    result = _run(lambda conn: _ping(conn), default=False)
    return {"configured": True, "connected": bool(result)}


def _ping(conn) -> bool:
    with conn.cursor() as cursor:
        cursor.execute("SELECT 1")
        return cursor.fetchone()[0] == 1


def load_settings(user_id: str) -> Optional[dict]:
    def operation(conn):
        with conn.cursor() as cursor:
            cursor.execute("SELECT settings FROM user_settings WHERE user_id = %s", (str(user_id),))
            row = cursor.fetchone()
            if not row:
                return None
            value = row[0]
            if isinstance(value, dict):
                return value
            return json.loads(value or "{}")
    return _run(operation, default=None)


def save_settings(user_id: str, settings: dict) -> bool:
    def operation(conn):
        from psycopg.types.json import Jsonb
        uid = str(user_id)
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO app_users (user_id, phone, authenticated, connected)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (user_id) DO UPDATE SET
                    phone = COALESCE(EXCLUDED.phone, app_users.phone),
                    authenticated = EXCLUDED.authenticated,
                    connected = EXCLUDED.connected,
                    updated_at = CURRENT_TIMESTAMP
            """, (
                uid,
                settings.get("phone"),
                bool(settings.get("authenticated", False)),
                bool(settings.get("connected", False)),
            ))
            cursor.execute("""
                INSERT INTO user_settings (user_id, settings, updated_at)
                VALUES (%s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (user_id) DO UPDATE SET
                    settings = EXCLUDED.settings,
                    updated_at = CURRENT_TIMESTAMP
            """, (uid, Jsonb(settings)))
        return True
    return bool(_run(operation, default=False))


def record_sent_batch(user_id: str, batch_id: str, payload: dict) -> bool:
    def operation(conn):
        from psycopg.types.json import Jsonb
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO app_users (user_id)
                VALUES (%s)
                ON CONFLICT (user_id) DO UPDATE SET updated_at = CURRENT_TIMESTAMP
            """, (str(user_id),))
            cursor.execute("""
                INSERT INTO sent_batches (user_id, batch_id, payload, sent_at)
                VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (user_id, batch_id) DO UPDATE SET
                    payload = EXCLUDED.payload,
                    sent_at = EXCLUDED.sent_at
            """, (str(user_id), str(batch_id), Jsonb(payload)))
        return True
    return bool(_run(operation, default=False))


def record_schedule_event(user_id: str, phase: str, payload: Optional[dict] = None) -> bool:
    def operation(conn):
        from psycopg.types.json import Jsonb
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO app_users (user_id)
                VALUES (%s)
                ON CONFLICT (user_id) DO UPDATE SET updated_at = CURRENT_TIMESTAMP
            """, (str(user_id),))
            cursor.execute("""
                INSERT INTO schedule_events (user_id, phase, payload, recorded_at)
                VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
            """, (str(user_id), str(phase), Jsonb(payload or {})))
        return True
    return bool(_run(operation, default=False))


def upsert_push_subscription(user_id: str, endpoint: str, payload: dict) -> bool:
    def operation(conn):
        from psycopg.types.json import Jsonb
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO app_users (user_id)
                VALUES (%s)
                ON CONFLICT (user_id) DO UPDATE SET updated_at = CURRENT_TIMESTAMP
            """, (str(user_id),))
            cursor.execute("""
                INSERT INTO push_subscriptions (user_id, endpoint, payload, updated_at)
                VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (user_id, endpoint) DO UPDATE SET
                    payload = EXCLUDED.payload,
                    updated_at = CURRENT_TIMESTAMP
            """, (str(user_id), endpoint, Jsonb(payload)))
        return True
    return bool(_run(operation, default=False))


def migrate_json_settings(sessions_dir: str) -> int:
    """Import existing settings only when a user has no DB row yet."""
    if not is_enabled():
        return 0
    imported = 0
    candidates = []
    try:
        for name in os.listdir(sessions_dir):
            if name.endswith(".json") and name not in {"push_subscriptions.json"}:
                candidates.append((name[:-5], os.path.join(sessions_dir, name)))
            user_path = os.path.join(sessions_dir, name, "settings.json")
            if os.path.isfile(user_path):
                candidates.append((name, user_path))
    except OSError as exc:
        logger.warning("Could not scan JSON settings for migration: %s", exc)
        return 0

    seen = set()
    for user_id, path in candidates:
        if user_id in seen:
            continue
        seen.add(user_id)
        try:
            if load_settings(user_id) is not None:
                continue
            with open(path, "r", encoding="utf-8") as settings_file:
                settings = json.load(settings_file)
            if isinstance(settings, dict) and save_settings(user_id, settings):
                imported += 1
        except Exception as exc:
            logger.warning("Could not migrate settings for %s: %s", user_id, exc)
    if imported:
        logger.info("Imported %s JSON user settings into PostgreSQL", imported)
    return imported


def get_saved_links() -> Optional[list[dict]]:
    if not is_enabled():
        return None

    def operation(conn):
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id, url, title, category, date_saved, source, notes "
                "FROM saved_links ORDER BY date_saved DESC"
            )
            rows = cursor.fetchall()
            return [
                {
                    "id": r[0],
                    "url": r[1],
                    "title": r[2] or r[1],
                    "category": r[3] or "عام",
                    "date_saved": r[4] or "",
                    "source": r[5] or "يدوي",
                    "notes": r[6] or "",
                }
                for r in rows
            ]

    return _run(operation, default=None)


def upsert_saved_link(link: dict) -> bool:
    if not is_enabled() or not isinstance(link, dict) or not link.get("url"):
        return False

    import hashlib
    url = str(link.get("url") or "").strip()
    link_id = str(link.get("id") or "").strip() or hashlib.sha1(url.encode("utf-8")).hexdigest()[:8]

    def operation(conn):
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO saved_links (id, url, title, category, date_saved, source, notes, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (url) DO UPDATE SET
                    title = EXCLUDED.title,
                    category = EXCLUDED.category,
                    notes = EXCLUDED.notes,
                    updated_at = CURRENT_TIMESTAMP
            """, (
                link_id,
                url,
                str(link.get("title") or url),
                str(link.get("category") or "عام"),
                str(link.get("date_saved") or ""),
                str(link.get("source") or "يدوي"),
                str(link.get("notes") or ""),
            ))
        return True

    return bool(_run(operation, default=False))


def upsert_saved_links_batch(links: list[dict]) -> int:
    if not is_enabled() or not links:
        return 0

    import hashlib
    rows = []
    seen_urls = set()
    seen_ids = set()
    for link in links:
        if not isinstance(link, dict) or not link.get("url"):
            continue
        url = str(link.get("url") or "").strip()
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)
        link_id = str(link.get("id") or "").strip()
        if not link_id or link_id in seen_ids:
            link_id = hashlib.sha1(url.encode("utf-8")).hexdigest()[:10]
        seen_ids.add(link_id)
        rows.append((
            link_id,
            url,
            str(link.get("title") or url),
            str(link.get("category") or "عام"),
            str(link.get("date_saved") or ""),
            str(link.get("source") or "يدوي"),
            str(link.get("notes") or ""),
        ))

    if not rows:
        return 0

    def operation(conn):
        with conn.cursor() as cursor:
            cursor.executemany("""
                INSERT INTO saved_links (id, url, title, category, date_saved, source, notes, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (url) DO NOTHING
            """, rows)
        return len(rows)

    return int(_run(operation, default=0) or 0)


def delete_saved_link(link_id: str) -> bool:
    if not is_enabled() or not link_id:
        return False

    def operation(conn):
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM saved_links WHERE id = %s", (str(link_id),))
        return True

    return bool(_run(operation, default=False))


def delete_saved_links_batch(link_ids: list[str]) -> bool:
    if not is_enabled() or not link_ids:
        return False

    def operation(conn):
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM saved_links WHERE id = ANY(%s)", ([str(x) for x in link_ids],))
        return True

    return bool(_run(operation, default=False))


def get_saved_phone_numbers() -> Optional[list[dict]]:
    if not is_enabled():
        return None

    def operation(conn):
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT phone_digits, phone_number, account_name, label, is_default, added_at, "
                "COALESCE(to_char(updated_at AT TIME ZONE 'UTC', 'YYYY-MM-DD\"T\"HH24:MI:SS\"Z\"'), '') "
                "FROM saved_phone_numbers ORDER BY is_default DESC, updated_at DESC"
            )
            rows = cursor.fetchall()
            return [
                {
                    "phone_number": r[1],
                    "account_name": r[2] or r[3] or "",
                    "label": r[3] or r[2] or "",
                    "is_default": bool(r[4]),
                    "added_at": r[5] or "",
                    "updated_at": r[6] or "",
                }
                for r in rows
                if r[1]
            ]

    return _run(operation, default=None)


def upsert_saved_phone_number(entry: dict) -> bool:
    if not is_enabled() or not isinstance(entry, dict):
        return False
    import re
    raw_phone = str(entry.get("phone_number") or "").strip()
    digits = re.sub(r"[^0-9]", "", raw_phone)
    if not digits:
        return False
    acc_name = str(entry.get("account_name") or entry.get("label") or "").strip()
    label = str(entry.get("label") or acc_name or "").strip()
    is_def = bool(entry.get("is_default", False))
    added_at = str(entry.get("added_at") or "")

    def operation(conn):
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO saved_phone_numbers (phone_digits, phone_number, account_name, label, is_default, added_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (phone_digits) DO UPDATE SET
                    phone_number = EXCLUDED.phone_number,
                    account_name = EXCLUDED.account_name,
                    label = EXCLUDED.label,
                    is_default = saved_phone_numbers.is_default OR EXCLUDED.is_default,
                    updated_at = CURRENT_TIMESTAMP
            """, (digits, raw_phone, acc_name, label, is_def, added_at))
        return True

    return bool(_run(operation, default=False))


def upsert_saved_phone_numbers_batch(entries: list[dict]) -> int:
    if not is_enabled() or not entries:
        return 0
    import re
    rows = []
    seen = set()
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        raw_phone = str(entry.get("phone_number") or "").strip()
        digits = re.sub(r"[^0-9]", "", raw_phone)
        if not digits or digits in seen:
            continue
        seen.add(digits)
        acc_name = str(entry.get("account_name") or entry.get("label") or "").strip()
        label = str(entry.get("label") or acc_name or "").strip()
        is_def = bool(entry.get("is_default", False))
        added_at = str(entry.get("added_at") or "")
        rows.append((digits, raw_phone, acc_name, label, is_def, added_at))

    if not rows:
        return 0

    def operation(conn):
        with conn.cursor() as cursor:
            cursor.executemany("""
                INSERT INTO saved_phone_numbers (phone_digits, phone_number, account_name, label, is_default, added_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (phone_digits) DO UPDATE SET
                    phone_number = EXCLUDED.phone_number,
                    account_name = EXCLUDED.account_name,
                    label = EXCLUDED.label,
                    is_default = saved_phone_numbers.is_default OR EXCLUDED.is_default,
                    updated_at = CURRENT_TIMESTAMP
            """, rows)
        return len(rows)

    return int(_run(operation, default=0) or 0)


