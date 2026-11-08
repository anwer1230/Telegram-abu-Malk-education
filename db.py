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
