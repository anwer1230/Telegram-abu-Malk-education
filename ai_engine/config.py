"""إعدادات محرك الذكاء الاصطناعي — Groq ومحركات RAG"""
import os

# ═══ مفاتيح ومزودات الخدمة ═══
# يتم قراءة المفتاح من متغير البيئة GROQ_API_KEY أو ملف .env أو ملف التكوين المحلي
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()

if not GROQ_API_KEY:
    try:
        from dotenv import load_dotenv
        load_dotenv()
        GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
    except Exception:
        pass

if not GROQ_API_KEY:
    _key_file = os.path.join(os.path.dirname(__file__), ".groq_key")
    if os.path.exists(_key_file):
        try:
            with open(_key_file, "r", encoding="utf-8") as _kf:
                GROQ_API_KEY = _kf.read().strip()
        except Exception:
            pass

OLLAMA_URL = os.getenv("OLLAMA_URL", "")

# ═══ النماذج المعتمدة ═══
MODEL_TEXT = os.getenv("AI_MODEL_TEXT", "allam-2-7b")
MODEL_LOGIC = os.getenv("AI_MODEL_LOGIC", "qwen/qwen3.8-27b")
MODEL_CODE = os.getenv("AI_MODEL_CODE", "qwen/qwen3.8-27b")
MODEL_FAST = os.getenv("AI_MODEL_FAST", "allam-2-7b")

FALLBACK_MODELS = [
    "allam-2-7b",
    "qwen/qwen3.8-27b",
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b"
]

# ═══ إعدادات الـ RAG ═══
RAG_DB_PATH = os.getenv("RAG_DB_PATH", "data/rag/embeddings.db")
RAG_UPLOAD_DIR = os.getenv("RAG_UPLOAD_DIR", "data/rag/uploads")
EMBED_PROVIDER = os.getenv("EMBED_PROVIDER", "local")
JINA_API_KEY = os.getenv("JINA_API_KEY", "")

# ═══ إعدادات الربط ═══
AI_TELEGRAM_ENABLED = os.getenv("AI_TELEGRAM_ENABLED", "true").lower() == "true"
AI_VOICE_ENABLED = os.getenv("AI_VOICE_ENABLED", "true").lower() == "true"
