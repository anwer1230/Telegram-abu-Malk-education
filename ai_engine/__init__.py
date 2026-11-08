"""حزمة محرك الذكاء الاصطناعي الشامل — Abu Malk Services AI Engine"""
from ai_engine.pipeline import ask, health as ai_health
from ai_engine.ratelimit import protect, get_stats as rate_stats
from ai_engine.rag import add_document, search as rag_search, stats as rag_stats, delete_source
from ai_engine.telegram_bridge import generate_reply as telegram_ai_reply
from ai_engine.voice_bridge import generate_reply as voice_ai_reply

__all__ = [
    "ask",
    "ai_health",
    "protect",
    "rate_stats",
    "add_document",
    "rag_search",
    "rag_stats",
    "delete_source",
    "telegram_ai_reply",
    "voice_ai_reply",
]
