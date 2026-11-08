"""RAG خفيف — SQLite + Embeddings بعيدة أو محلية"""
import os
import sqlite3
import math
import hashlib
from pathlib import Path
from typing import Optional
from loguru import logger
import httpx
from ai_engine.config import RAG_DB_PATH, EMBED_PROVIDER, JINA_API_KEY, OLLAMA_URL

RAG_DB = RAG_DB_PATH
EMBED_DIM = 384
CHUNK_SIZE = 700
CHUNK_OVERLAP = 100

Path(RAG_DB).parent.mkdir(parents=True, exist_ok=True)


# ═══════════════════════════════════════════════════════════
# Embedding providers
# ═══════════════════════════════════════════════════════════
def _hash_embed(text: str) -> list[float]:
    """Embedding محلي سريع (بدون API) — يعتمد على hashing"""
    vec = [0.0] * EMBED_DIM
    tokens = text.lower().split()
    for tok in tokens:
        h = int(hashlib.md5(tok.encode()).hexdigest(), 16)
        idx = h % EMBED_DIM
        vec[idx] += 1.0
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


def _jina_embed(text: str) -> list[float]:
    """Embeddings عالية الجودة من Jina AI"""
    if not JINA_API_KEY:
        raise RuntimeError("JINA_API_KEY غير مُعد")
    with httpx.Client(timeout=20) as c:
        r = c.post(
            "https://api.jina.ai/v1/embeddings",
            headers={"Authorization": f"Bearer {JINA_API_KEY}"},
            json={"model": "jina-embeddings-v3", "input": [text]},
        )
        r.raise_for_status()
        return r.json()["data"][0]["embedding"]


def _ollama_embed(text: str) -> list[float]:
    """عبر Ollama (إن مُتاح)"""
    if not OLLAMA_URL:
        raise RuntimeError("OLLAMA_URL غير مُعد")
    with httpx.Client(timeout=30) as c:
        r = c.post(f"{OLLAMA_URL}/api/embeddings",
                   json={"model": "bge-m3", "prompt": text})
        r.raise_for_status()
        return r.json()["embedding"]


def embed(text: str) -> list[float]:
    """التضمين مع Fallback تلقائي"""
    try:
        if EMBED_PROVIDER == "jina" and JINA_API_KEY:
            return _jina_embed(text)
        if EMBED_PROVIDER == "ollama" and OLLAMA_URL:
            return _ollama_embed(text)
    except Exception as e:
        logger.warning(f"Embedding فشل: {e} — استخدام hash")
    return _hash_embed(text)


# ═══════════════════════════════════════════════════════════
# Vector store على SQLite
# ═══════════════════════════════════════════════════════════
def _conn() -> sqlite3.Connection:
    c = sqlite3.connect(RAG_DB)
    c.execute("""
        CREATE TABLE IF NOT EXISTS chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            chunk_index INTEGER NOT NULL,
            text TEXT NOT NULL,
            embedding BLOB NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    c.execute("CREATE INDEX IF NOT EXISTS idx_source ON chunks(source)")
    return c


def _pack(vec: list[float]) -> bytes:
    import struct
    return struct.pack(f"{len(vec)}f", *vec)


def _unpack(blob: bytes) -> list[float]:
    import struct
    n = len(blob) // 4
    return list(struct.unpack(f"{n}f", blob))


def _cosine(a: list[float], b: list[float]) -> float:
    if len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)) or 1.0
    nb = math.sqrt(sum(y * y for y in b)) or 1.0
    return dot / (na * nb)


def chunk_text(text: str, size: int = CHUNK_SIZE,
               overlap: int = CHUNK_OVERLAP) -> list[str]:
    text = text.strip()
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        chunks.append(text[start:end].strip())
        if end >= len(text):
            break
        start = end - overlap
    return [c for c in chunks if c]


# ═══════════════════════════════════════════════════════════
# API العامة
# ═══════════════════════════════════════════════════════════
def add_document(text: str, source: str) -> int:
    """إضافة مستند إلى قاعدة بيانات RAG"""
    chunks = chunk_text(text)
    if not chunks:
        return 0
    conn = _conn()
    try:
        for i, chunk in enumerate(chunks):
            vec = embed(chunk)
            conn.execute(
                "INSERT INTO chunks (source, chunk_index, text, embedding) VALUES (?,?,?,?)",
                (source, i, chunk, _pack(vec)),
            )
        conn.commit()
        logger.info(f"✅ RAG: {len(chunks)} chunk من {source}")
        return len(chunks)
    finally:
        conn.close()


def search(query: str, limit: int = 4, min_score: float = 0.10) -> list[dict]:
    """البحث الدلالي في المستندات"""
    conn = _conn()
    try:
        cur = conn.execute("SELECT source, chunk_index, text, embedding FROM chunks")
        qv = embed(query)
        scored = []
        for row in cur:
            score = _cosine(qv, _unpack(row[3]))
            if score >= min_score:
                scored.append({
                    "source": row[0],
                    "chunk_index": row[1],
                    "text": row[2],
                    "score": round(score, 4),
                })
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:limit]
    finally:
        conn.close()


def stats() -> dict:
    conn = _conn()
    try:
        total = conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
        sources = conn.execute(
            "SELECT source, COUNT(*) FROM chunks GROUP BY source"
        ).fetchall()
        return {
            "total_chunks": total,
            "sources": [{"name": s[0], "chunks": s[1]} for s in sources],
        }
    finally:
        conn.close()


def delete_source(source: str) -> int:
    conn = _conn()
    try:
        cur = conn.execute("DELETE FROM chunks WHERE source = ?", (source,))
        conn.commit()
        return cur.rowcount
    finally:
        conn.close()
