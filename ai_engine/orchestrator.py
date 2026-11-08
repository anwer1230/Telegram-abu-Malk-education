"""منسق المهام وتوجيه الأسئلة إلى الخبير المناسب"""
import re
from loguru import logger
from ai_engine.ollama_client import chat
from ai_engine.config import MODEL_FAST

RAG_KEYWORDS = {
    "ملف", "ملفاتي", "مستند", "مستنداتي", "قاعدتي", "ما سجلته", "سجلته", "المرفق", "المرفقات", "pdf", "word", "وثيقة"
}
CODE_KEYWORDS = {
    "كود", "برمج", "دالة", "function", "code", "python", "javascript", "html", "css", "sql", "خطأ برمج", "bug"
}
LOGIC_KEYWORDS = {
    "احسب", "حساب", "كم يساوي", "معادلة", "نسبة", "تكلفة", "رياضيات", "مجموع", "متوسط"
}


def route(task: str) -> str:
    """تحديد الخبير المناسب بناءً على فحص سريع للكلمات أو استدلال سريع"""
    if not task:
        return "TEXT"

    low = task.lower()

    # 1) فحص الكلمات المفتاحية المباشرة (فائق السرعة)
    if any(k in low for k in RAG_KEYWORDS):
        return "RAG"
    if any(k in low for k in CODE_KEYWORDS):
        return "CODE"
    if any(k in low for k in LOGIC_KEYWORDS):
        return "LOGIC"

    # 2) التوجيه الافتراضي للنصوص العامة
    return "TEXT"
